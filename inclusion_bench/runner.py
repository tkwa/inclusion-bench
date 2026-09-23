"""Serial, checkpointed model runs with sealed evidence and explicit token budgets."""
from __future__ import annotations

import copy
import json
import os
import random
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .benchmark import Benchmark, canonical_hash, read_json
from .engine import Atom, InvalidEvidence
from .evaluation import artifact_path, execute_adapter, sha256_file, taskset, validate_run


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def submission_support(benchmark: Benchmark) -> dict:
    """Snapshot agent-facing mathematical support separately from frozen tasks."""
    from .literature import theorem_catalog
    sources = {str(path.relative_to(benchmark.root)): path.read_text()
               for path in sorted((benchmark.root / 'support').rglob('*.lean'))
               if '.lake' not in path.parts}
    # A paper can justify many declarations. Send each citation once rather
    # than repeating the full bibliography in every theorem record.
    citations, theorems = {}, []
    for entry in theorem_catalog(benchmark):
        refs = []
        for citation in entry.get('sources', []):
            key = canonical_hash(citation)
            citations[key] = citation
            refs.append(key)
        theorems.append({k: v for k, v in entry.items() if k != 'sources'} | {'source_refs': refs})
    return {'cutoff': benchmark.policy['cutoff'], 'theorems': theorems, 'sources': citations,
            'lean_sources': sources,
            'instructions': 'Formalize the novel argument using standard textbook abstractions and the supplied trusted results. '
                'For an additional published result, declare its exact Lean type as an axiom named Literature.your_name '
                'and supply literature_requests with the matching name, statement, source title/URL/theorem or page/publication date, '
                'and the reason its conventions match these models. A maintainer reviews the existing result and model alignment; '
                'its published proof does not need to be formalized again. A new benchmark claim must be proved. '
                'Lean submissions may use a normal module tree: return named lean_sources plus lean_entrypoint. '
                'Import TrustedBaseline for the supplied definitions and results, and import local helper modules normally. '
                'The project manifest and every named source must be retained as sealed artifacts.'}


def write_json(path: Path, value) -> None:
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def frozen_release(benchmark: Benchmark) -> dict:
    path = benchmark.root / 'data/freeze.json'
    if not path.exists():
        raise InvalidEvidence('Freeze this release before a real run: inclusion-bench freeze')
    freeze = read_json(path)
    suite = taskset(benchmark)
    if freeze.get('dataset_sha256') != benchmark.digest or freeze.get('taskset_sha256') != suite['taskset_sha256']:
        raise InvalidEvidence('The release changed after freezing; freeze a new version before running')
    if freeze.get('benchmark_version') != benchmark.policy['version']:
        raise InvalidEvidence('Frozen release version does not match policy')
    for relative, digest in suite['formalization_bundle']['files'].items():
        path = benchmark.root / relative
        if not path.is_file() or sha256_file(path) != digest:
            raise InvalidEvidence(f'Frozen formalization source is missing or changed: {relative}')
    if benchmark.policy['release_stage'] not in {'operational', 'certified'}:
        raise InvalidEvidence('This release is not open for model runs')
    return freeze


def freeze_release(benchmark: Benchmark) -> dict:
    if benchmark.policy['release_stage'] not in {'operational', 'certified'}:
        raise InvalidEvidence('Set a versioned operational policy before freezing the release')
    suite = taskset(benchmark)
    audit = benchmark.root / 'research/baseline-audit.json'
    path = benchmark.root / 'data/freeze.json'
    if path.exists():
        previous = read_json(path)
        same = (previous.get('dataset_sha256') == benchmark.digest and
                previous.get('taskset_sha256') == suite['taskset_sha256'])
        if same and previous.get('benchmark_version') == benchmark.policy['version']:
            frozen_release(benchmark)
            return previous
        if previous.get('benchmark_version') == benchmark.policy['version']:
            raise InvalidEvidence('A changed frozen suite requires a new policy.version')
    freeze = {'schema_version': 1, 'benchmark_version': benchmark.policy['version'],
              'frozen_at': now(), 'dataset_sha256': benchmark.digest, 'taskset_sha256': suite['taskset_sha256'],
              'formalization_bundle_sha256': suite['formalization_bundle']['bundle_sha256'],
              'candidate_question_count': len(suite['tasks']), 'ordered_pair_count': len(benchmark.ids)**2,
              'baseline_audit_sha256': sha256_file(audit) if audit.exists() else None,
              'trust_policy': 'Cited existing results and canonical model conventions are trusted inputs. New ordinary proofs are checked; every awarded pair receives historical review.',
              'eligibility_policy': 'Freezing fixes candidate questions; it does not certify them all open.'}
    write_json(benchmark.root / 'data/freeze.json', freeze)
    return freeze


def normalize_config(benchmark: Benchmark, config: dict, model_override: str | None = None) -> dict:
    config = copy.deepcopy(config)
    def reject_secrets(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if str(key).lower() in {'api_key', 'apikey', 'authorization', 'password', 'access_token', 'secret'}:
                    raise InvalidEvidence('Keep credentials in environment variables, never in saved run configuration')
                reject_secrets(item)
        elif isinstance(value, list):
            for item in value:
                reject_secrets(item)
    reject_secrets(config)
    if model_override:
        config['model'] = {'name': model_override, 'version': model_override}
        config.setdefault('configuration', {})['model_id'] = model_override
    model = config.get('model', {})
    if not all(isinstance(model.get(k), str) and model[k].strip() and '<' not in model[k] for k in ('name', 'version')):
        raise InvalidEvidence('Supply an explicit model snapshot with --model or config.model.name/version')
    if config.get('track', 'closed-book') not in {'closed-book', 'tool-assisted', 'smoke-test'}:
        raise InvalidEvidence('Unknown evaluation track')
    config.setdefault('track', 'closed-book')
    provider = config.get('provider', 'custom')
    if provider in {'openai', 'anthropic'}:
        explicit = config.get('configuration', {}).get('model_id')
        if explicit and explicit != model['version']:
            raise InvalidEvidence('configuration.model_id must match the recorded model.version')
        config['adapter'] = [sys.executable, str(benchmark.root / 'evaluation/adapters' / {'openai': 'openai_responses.py', 'anthropic': 'anthropic_messages.py'}[provider])]
        config.setdefault('configuration', {})['model_id'] = config.get('configuration', {}).get('model_id', model['version'])
        if config['track'] == 'tool-assisted':
            raise InvalidEvidence('The built-in provider adapters are closed-book; use a custom adapter for tools')
    elif provider == 'fixture':
        if config['track'] != 'smoke-test':
            raise InvalidEvidence('Infrastructure fixtures must use the smoke-test track')
        config['adapter'] = [sys.executable, str(benchmark.root / 'evaluation/unsolved_adapter.py')]
    elif provider != 'custom':
        raise InvalidEvidence('Provider must be openai, anthropic, custom, or fixture')
    command = config.get('adapter')
    if not isinstance(command, list) or not command or any(not isinstance(p, str) or not p for p in command):
        raise InvalidEvidence('A custom adapter requires a nonempty argument list; shell strings are not accepted')
    config['adapter'] = [p.replace('{repository}', str(benchmark.root)).replace('{python}', sys.executable) for p in command]
    adapter_sources = []
    for argument in config['adapter'][1:]:
        try:
            if Path(argument).is_file():
                adapter_sources.append(Path(argument))
        except OSError:
            pass  # An inline program or long option is not a file path.
    if provider in {'openai', 'anthropic'}:
        adapter_sources.append(benchmark.root / 'evaluation/adapters/provider.py')
    config['adapter_source_sha256'] = {str(p): sha256_file(p) for p in adapter_sources}
    config['harness_source_sha256'] = {name: sha256_file(Path(__file__).parent / name)
                                     for name in ('runner.py', 'evaluation.py', 'proofcheck.py', 'proofbundle.py', 'proofevidence.py', 'literature.py', 'submissions.py')}
    config['submission_support_sha256'] = canonical_hash(submission_support(benchmark))
    budget = config.setdefault('budget', {})
    defaults = {'wall_time_seconds': 3600, 'per_task_wall_time_seconds': 600, 'max_total_tokens': 100000,
                'max_output_tokens_per_task': 8192, 'max_cpu_cores': 1, 'memory_limit_mib': 4096}
    for key, default in defaults.items():
        budget.setdefault(key, default)
        if type(budget[key]) is not int or budget[key] < 1:
            raise InvalidEvidence(f'Budget {key} must be a positive integer')
    if budget['max_cpu_cores'] > 4 or budget['memory_limit_mib'] > 16384:
        raise InvalidEvidence('Local adapter limits may not exceed four CPUs or 16 GiB')
    budget['per_task_wall_time_seconds'] = min(budget['per_task_wall_time_seconds'], budget['wall_time_seconds'])
    suite = taskset(benchmark)
    tasks = [t['task_id'] for t in suite['tasks']]
    selection = config.setdefault('selection', {'task_ids': ['inclusion.NP.P']})
    if selection.get('all_tasks') is True:
        assigned = tasks[:]
        seed = selection.setdefault('seed', 0)
        if type(seed) is not int:
            raise InvalidEvidence('Task-order seed must be an integer')
        random.Random(seed).shuffle(assigned)
    else:
        assigned = selection.get('task_ids')
    if not isinstance(assigned, list) or not assigned or len(assigned) != len(set(assigned)) or not set(assigned) <= set(tasks):
        raise InvalidEvidence('Select distinct task IDs from the frozen suite or set all_tasks=true')
    config['assigned_task_ids'] = assigned
    config['schema_version'] = 2
    return config


def preflight(benchmark: Benchmark, config: dict, model_override: str | None = None, *, require_credentials=True) -> dict:
    freeze = frozen_release(benchmark)
    normalized = normalize_config(benchmark, config, model_override)
    executable = normalized['adapter'][0]
    if not (Path(executable).is_file() or shutil.which(executable)):
        raise InvalidEvidence(f'Adapter executable is unavailable: {executable}')
    provider = normalized.get('provider', 'custom')
    credential = {'openai': 'OPENAI_API_KEY', 'anthropic': 'ANTHROPIC_API_KEY'}.get(provider)
    available = bool(os.environ.get(credential)) if credential else None
    if require_credentials and credential and not available:
        raise InvalidEvidence(f'Set {credential} in the environment before running; never put secrets in the config')
    return {'ready': True, 'network_requests_made': False, 'provider': provider, 'model': normalized['model'],
            'credential_configured': available, 'dataset_sha256': benchmark.digest,
            'taskset_sha256': freeze['taskset_sha256'], 'assigned_task_count': len(normalized['assigned_task_ids']),
            'total_task_count': len(taskset(benchmark)['tasks']), 'budget': normalized['budget'],
            'configuration_sha256': canonical_hash(normalized),
            'note': 'No model request is sent by preflight. Token limits are enforced conservatively; provider billing cannot be reversed after an uncertain network outcome.'}


def _validate_response(benchmark: Benchmark, response: dict, attempt_dir: Path, run_dir: Path,
                       remaining: int, provider: str) -> dict:
    if not isinstance(response, dict) or response.get('status') not in {'unsolved', 'proof_candidate', 'error', 'budget_exhausted'}:
        raise InvalidEvidence('Adapter must return a recognized attempt status')
    claims, artifacts = response.get('claims', []), response.get('artifacts', [])
    if not isinstance(claims, list) or not isinstance(artifacts, list):
        raise InvalidEvidence('Adapter claims and artifact paths must be arrays')
    if response['status'] == 'proof_candidate' and (not claims or not artifacts):
        raise InvalidEvidence('A proof candidate needs exact claims and proof artifacts')
    if response['status'] != 'proof_candidate' and claims:
        raise InvalidEvidence('Only a proof candidate may assert claims')
    for c in claims:
        benchmark.baseline.validate_atom(Atom.read(c))
    from .literature import validate_requests
    literature = validate_requests(benchmark, response.get('literature_requests', []))
    if literature and response['status'] != 'proof_candidate':
        raise InvalidEvidence('Only a proof candidate may request literature dependencies')
    sealed = []
    for relative in artifacts:
        path = artifact_path(attempt_dir, relative)
        sealed.append({'path': str(path.relative_to(run_dir)), 'sha256': sha256_file(path)})
    submission_manifest = None
    if response.get('submission_manifest') is not None:
        from .proofevidence import validate_submission_artifacts
        relative = response['submission_manifest']
        # Validate the original relative name before normalizing it into the
        # run. The shared helper checks the complete co-located artifact set.
        artifact_path(attempt_dir, relative)
        submission_manifest = str(attempt_dir.relative_to(run_dir) / relative)
        submission_manifest = validate_submission_artifacts(benchmark, {
            'status': response['status'], 'claims': claims, 'artifacts': sealed,
            'literature_requests': literature, 'submission_manifest': submission_manifest,
        }, run_dir)
    usage = response.get('usage', {})
    if not isinstance(usage, dict):
        raise InvalidEvidence('Usage must be a JSON object')
    fixture = provider == 'fixture'
    complete = response.get('usage_complete', usage.get('usage_complete', fixture))
    if type(complete) is not bool or type(response.get('request_made', not fixture)) is not bool:
        raise InvalidEvidence('usage_complete and request_made must be booleans')
    for key in ('input_tokens', 'output_tokens', 'total_tokens'):
        if usage.get(key) is not None and (type(usage[key]) is not int or usage[key] < 0):
            raise InvalidEvidence('Reported token counts must be nonnegative integers')
    measured = max(usage.get('total_tokens') or 0, (usage.get('input_tokens') or 0) + (usage.get('output_tokens') or 0))
    charge = response.get('budget_charge_tokens', usage.get('total_tokens') if usage.get('total_tokens') is not None else (0 if fixture else remaining))
    if type(charge) is not int or charge < 0:
        raise InvalidEvidence('Adapter budget_charge_tokens must be a nonnegative integer')
    if charge < measured:
        raise InvalidEvidence('Adapter token charge is below its reported usage')
    if not complete and response.get('request_made', not fixture):
        charge = max(charge, remaining)
    overrun = charge > remaining
    return {'status': 'error' if overrun else response['status'], 'claims': [] if overrun else claims, 'artifacts': sealed,
            'literature_requests': [] if overrun else literature,
            **({'submission_manifest': submission_manifest} if submission_manifest is not None and not overrun else {}),
            'usage': usage, 'usage_complete': bool(complete), 'budget_charge_tokens': charge,
            'request_made': bool(response.get('request_made', not fixture)),
            'provider_model': response.get('provider_model') or response.get('model_returned'),
            'error': 'Observed token budget overrun' if overrun else response.get('error'), 'budget_overrun': overrun,
            'finish_reason': response.get('finish_reason')}


def run_config(benchmark: Benchmark, raw_config: dict, output: Path, *, model_override=None, resume=False) -> Path:
    preflight(benchmark, raw_config, model_override)
    config = normalize_config(benchmark, raw_config, model_override)
    output = output.resolve()
    manifest = output / 'run.json'
    suite = taskset(benchmark)
    by_id = {t['task_id']: t for t in suite['tasks']}
    from .proofcheck import trusted_baseline
    baseline_source, _, _ = trusted_baseline(benchmark, [])
    formalizations = {p: (benchmark.root / p).read_text() for p in suite['formalization_bundle']['files'] if p.endswith('.lean')}
    formalizations['TrustedBaseline.lean'] = baseline_source
    support = submission_support(benchmark)
    if canonical_hash(support) != config['submission_support_sha256']:
        raise InvalidEvidence('Submission support changed while preparing the run')
    if resume:
        run = read_json(manifest)
        if run.get('configuration_sha256') != canonical_hash(config) or run.get('taskset_sha256') != suite['taskset_sha256']:
            raise InvalidEvidence('Resume requires the exact original config and frozen task suite')
        if run.get('state') == 'sealed':
            raise InvalidEvidence('Sealed runs are immutable; start a new run')
        validate_run(benchmark, run, output)
        if run.get('in_flight'):
            # A killed client may already have incurred remote charges. Do not retry or
            # grant a fresh quota after losing the response.
            lost = run.pop('in_flight')
            lost.update(status='error', claims=[], artifacts=[], error='Interrupted request; remote usage is unknown',
                        finished_at=now(), usage={}, request_made=True, recovered_interruption=True,
                        usage_complete=False, budget_charge_tokens=max(0, config['budget']['max_total_tokens']-run['usage']['charged_tokens']))
            write_json(output / Path(lost['request_path']).parent / 'recovery.json',
                       {'reason': lost['error'], 'recovered_at': lost['finished_at'], 'remote_usage_unknown': True})
            run['attempts'].append(lost)
            run['usage']['charged_tokens'] += lost['budget_charge_tokens']
    else:
        if output.exists():
            raise InvalidEvidence('Output directory already exists; use --resume for an interrupted run')
        output.mkdir(parents=True)
        started = now()
        run = {'schema_version': 2, 'run_id': output.name, 'state': 'running', 'model': config['model'],
               'track': config['track'], 'provider': config.get('provider', 'custom'),
               'dataset_sha256': benchmark.digest, 'taskset_sha256': suite['taskset_sha256'],
               'configuration': config, 'configuration_sha256': canonical_hash(config),
               'budget': config['budget'], 'assigned_task_ids': config['assigned_task_ids'],
               'assignment_sha256': canonical_hash(config['assigned_task_ids']),
               'tools': {'adapter_command': config['adapter'], 'access_policy': config.get('tools', {'model_tools': [], 'network': 'provider-api-only'})},
               'resource_enforcement': {'serial_adapters': True, 'wall_time': 'process-group deadline',
                   'cpu_affinity': sys.platform.startswith('linux'), 'memory_limit_per_process': sys.platform.startswith('linux'),
                   'aggregate_process_tree_limit': False,
                   'note': 'Custom adapters must supply container or equivalent aggregate isolation. macOS has no hard CPU/RAM cap in this runner.'},
               'started_at': started, 'finished_at': started, 'attempts': [],
               'usage': {'charged_tokens': 0, 'measured_input_tokens': 0, 'measured_output_tokens': 0},
               'resume_events': [], 'evidence_index': {}}
        write_json(output / 'config.json', config)
        write_json(output / 'taskset.json', suite)
    if resume:
        run['resume_events'].append(now())
    deadline = datetime.fromisoformat(run['started_at']).timestamp() + config['budget']['wall_time_seconds']
    completed = {a['task_id'] for a in run['attempts']}
    write_json(manifest, run)
    for task_id in config['assigned_task_ids']:
        if task_id in completed:
            continue
        remaining = config['budget']['max_total_tokens'] - run['usage']['charged_tokens']
        seconds = min(deadline - time.time(), config['budget']['per_task_wall_time_seconds'])
        if remaining <= 0 or seconds <= 0:
            break
        number = len(run['attempts']) + 1
        relative_dir = Path('attempts') / f'{number:04d}'
        attempt_dir = output / relative_dir
        if attempt_dir.exists():
            # Preserve files from a crash before its in-flight checkpoint. No API
            # invocation can occur before that checkpoint has been committed.
            orphan = output / 'orphaned' / f'{number:04d}-{time.time_ns()}'
            orphan.parent.mkdir(parents=True, exist_ok=True)
            attempt_dir.rename(orphan)
        attempt_dir.mkdir(parents=True, exist_ok=False)
        request = {'schema_version': 2, 'task': by_id[task_id], 'classes': benchmark.catalog,
                   'knowledge': benchmark.knowledge, 'dataset_sha256': benchmark.digest,
                   'formalizations': formalizations, 'formalization_bundle': suite['formalization_bundle'],
                   'submission_support': support,
                   'model': config['model'], 'configuration': config.get('configuration', {}),
                   'limits': {'max_output_tokens': min(config['budget']['max_output_tokens_per_task'], remaining),
                              'max_total_tokens_remaining': remaining}, 'time_remaining_seconds': seconds,
                   'response_schema': {'status': 'unsolved|proof_candidate|error|budget_exhausted',
                                       'claims': 'relation/left/right objects', 'artifacts': 'relative paths within this attempt directory',
                                       'literature_requests': 'optional cited dependencies matching Literature.* declarations in the proof',
                                       'submission_manifest': 'optional relative path to submission.json; seal its named Lean files, claims.json, and literature.json together'}}
        write_json(attempt_dir / 'request.json', request)
        attempt = {'attempt_id': f'attempt-{number:04d}', 'task_id': task_id, 'started_at': now(),
                   'request_path': str(relative_dir / 'request.json'), 'prompt_sha256': canonical_hash(request)}
        run['in_flight'] = attempt
        run['finished_at'] = now()
        write_json(manifest, run)
        interrupted = False
        try:
            code, response = execute_adapter(config['adapter'], attempt_dir / 'request.json', attempt_dir / 'response.json',
                                             attempt_dir / 'stderr.txt', attempt_dir, time.monotonic()+seconds,
                                             memory_limit_mib=config['budget']['memory_limit_mib'], cpu_limit=config['budget']['max_cpu_cores'])
            if code:
                raise InvalidEvidence(f'Adapter exited with code {code}; usage is unknown')
            attempt.update(_validate_response(benchmark, response, attempt_dir, output, remaining, run['provider']))
        except (Exception, KeyboardInterrupt) as exc:
            interrupted = isinstance(exc, KeyboardInterrupt)
            attempt.update(status='budget_exhausted' if isinstance(exc, TimeoutError) or type(exc).__name__ == 'TimeoutExpired' else 'error',
                           claims=[], artifacts=[], error=str(exc) or 'Interrupted', usage_complete=False,
                           budget_charge_tokens=remaining, request_made=True, usage={})
        # Keep an explicit capture record even when execution fails before opening
        # its streams. Empty files are evidence of missing output, never an answer.
        for filename in ('response.json', 'stderr.txt'):
            (attempt_dir / filename).touch(exist_ok=True)
        attempt['finished_at'] = now()
        run['attempts'].append(attempt)
        run.pop('in_flight', None)
        run['usage']['charged_tokens'] += attempt['budget_charge_tokens']
        run['usage']['measured_input_tokens'] += attempt.get('usage', {}).get('input_tokens', 0) or 0
        run['usage']['measured_output_tokens'] += attempt.get('usage', {}).get('output_tokens', 0) or 0
        run['finished_at'] = now()
        write_json(manifest, run)
        if interrupted or attempt['status'] in {'error', 'budget_exhausted'}:
            break
    completed = {a['task_id'] for a in run['attempts']}
    run['unattempted_task_ids'] = [t for t in config['assigned_task_ids'] if t not in completed]
    run['state'] = 'sealed'
    run['finished_at'] = now()
    # The index covers the unedited model output and diagnostics as well as proof
    # files. Sealed hashes make subsequent artifact or transcript edits detectable.
    run['evidence_index'] = {str(p.relative_to(output)): sha256_file(artifact_path(output, str(p.relative_to(output)))) for p in sorted(output.rglob('*'))
                             if p.is_file() and p != manifest and p.suffix != '.tmp'}
    validate_run(benchmark, run, output)
    write_json(manifest, run)
    return manifest
