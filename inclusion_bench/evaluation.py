"""AI-run task export, adapter execution and proof-review-aware aggregation.

This module never treats a model's claim as a verified mathematical result.
Proof compilation/admission remains a separate trusted review boundary.
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import selectors
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .benchmark import Benchmark, canonical_hash, read_json
from .engine import Atom, InvalidEvidence


def execute_adapter(adapter: list[str], request_file: Path, response_file: Path, error_file: Path,
                    directory: Path, deadline: float, *, memory_limit_mib=None, cpu_limit=1) -> tuple[int, dict]:
    """Run a trusted POSIX adapter; bound wall time and captured output, including descendants."""
    if os.name != 'posix':
        raise InvalidEvidence('The adapter runner currently requires Linux or macOS')
    def child_limits():
        import resource
        if hasattr(os, 'sched_setaffinity'):
            os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:cpu_limit]))
        if memory_limit_mib and sys.platform.startswith('linux'):
            cap = memory_limit_mib * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        # A 16 MiB project can exceed 64 MiB once source JSON is nested inside
        # the provider transcript. Keep archive files bounded with headroom
        # for the 128 MiB HTTP body plus its request; pipe limits stay separate.
        resource.setrlimit(resource.RLIMIT_FSIZE, (256 * 1024 * 1024, 256 * 1024 * 1024))
    with request_file.open('rb') as stdin, response_file.open('wb') as stdout, error_file.open('wb') as stderr:
        process = subprocess.Popen(adapter, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=directory, start_new_session=True, preexec_fn=child_limits,
                                   env={**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'LEAN_NUM_THREADS': '1'})
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ, [stdout, 0, 8_000_000])
                selector.register(process.stderr, selectors.EVENT_READ, [stderr, 0, 1_000_000])
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(adapter, 0)
                    for key, _ in selector.select(min(remaining, 0.2)):
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        sink, size, cap = key.data
                        sink.write(chunk[:max(0, cap - size)])
                        key.data[1] += len(chunk)
                        if key.data[1] > cap:
                            raise InvalidEvidence('Adapter exceeded the captured output limit (8 MB response / 1 MB diagnostics)')
            process.wait(timeout=max(0.001, deadline - time.monotonic()))
        finally:
            # A successful adapter must also stop child tools before its attempt ends.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            process.stdout.close()
            process.stderr.close()
    return process.returncode, read_json(response_file) if process.returncode == 0 else {}


def taskset(benchmark: Benchmark) -> dict:
    tasks = []
    certified = benchmark.policy['release_stage'] == 'certified'
    eligibility = benchmark.certified_eligibility() if certified else benchmark.unresolved
    labels = {c['id']: c['label'] for c in benchmark.classes}
    for left, right in sorted(eligibility):
        tasks.append({
            'task_id': f'inclusion.{left}.{right}', 'left': left, 'right': right,
            'statement': f'{labels[left]} ⊆ {labels[right]}',
            'eligibility': 'open_at_cutoff' if certified else 'candidate_open_at_cutoff' if benchmark.policy['release_stage'] == 'operational' else 'unreviewed',
            'allowed_resolutions': ['inclusion', 'separation', 'independence'],
            'independence_premises': benchmark.policy['independence_premises'],
            'lean': {'import': 'InclusionQuantum', 'inclusion_target': f'InclusionBench.Includes (InclusionBench.Quantum.completeInterpretation .{left}) (InclusionBench.Quantum.completeInterpretation .{right})',
                     'separation_target': f'InclusionBench.NonIncludes (InclusionBench.Quantum.completeInterpretation .{left}) (InclusionBench.Quantum.completeInterpretation .{right})',
                     'independence_target': None, 'independence_note': 'An expert metatheory review must fix each exact ZFC sentence, proof relation and permitted premise. Arithmetic soundness uses truth in standard N, not truth in an arbitrary model.'},
            'prompt': f'Resolve whether {labels[left]} is contained in {labels[right]} under the attached exact class conventions. Supply a rigorous proof of inclusion, a rigorous proof of non-inclusion, or a precise ZFC-independence metatheorem. If you cannot resolve it, return unsolved. Conjectures and oracle separations are not solutions. Ordinary inclusion or non-inclusion proofs may not add unproved assumptions. Independence may be unconditional or conditional on Con(ZFC) or arithmetic soundness of ZFC, with both unprovability directions under the same stated premise. Arithmetic soundness means all first-order arithmetic sentences whose standard translations ZFC proves are true in standard N. Retain the premise explicitly; stronger unproved assumptions are not permitted. Identify every additional ordered-pair consequence your proof establishes. Return proof artifacts and exact claim objects; the evaluator, not the model, decides verification and points.'
        })
    core = {'schema_version': 1, 'benchmark': 'InclusionBench', 'dataset_sha256': benchmark.digest,
            'stage': benchmark.policy['release_stage'], 'cutoff': benchmark.policy['cutoff'],
            'access': 'public-white-box', 'unit_of_evaluation': 'one fixed AI model and configuration in one run',
            'formalization_bundle': read_json(benchmark.root / 'data/formalization.json'),
            'eligibility_manifest_sha256': canonical_hash(read_json(benchmark.root / 'data/eligibility.json')) if certified else None,
            'tasks': tasks}
    return {**core, 'taskset_sha256': canonical_hash(core)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_path(run_directory: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise InvalidEvidence('Artifact path must be a nonempty string')
    value = Path(relative)
    if value.is_absolute() or '..' in value.parts:
        raise InvalidEvidence('Proof artifacts must use relative paths inside the run directory')
    path = (run_directory / value).resolve()
    if not path.is_relative_to(run_directory.resolve()) or not path.is_file():
        raise InvalidEvidence(f'Artifact is missing or escapes run directory: {relative}')
    return path


def validate_run(benchmark: Benchmark, run: dict, directory: Path) -> None:
    if not isinstance(run, dict):
        raise InvalidEvidence('AI run must be a JSON object')
    for field in ('run_id', 'model', 'track', 'dataset_sha256', 'taskset_sha256', 'budget', 'attempts', 'started_at', 'finished_at'):
        if field not in run:
            raise InvalidEvidence(f'Missing AI run field: {field}')
    if not isinstance(run['model'], dict) or not run['model'].get('name') or not run['model'].get('version'):
        raise InvalidEvidence('An exact model name and version are required')
    if run.get('schema_version') not in {1, 2} or not isinstance(run['attempts'], list):
        raise InvalidEvidence('Expected run schema_version 1 or 2 and a list of attempts')
    if not run['run_id'] or not isinstance(run['budget'], dict) or not run['budget']:
        raise InvalidEvidence('A run identity and explicit budget are required')
    try:
        started, finished = [datetime.fromisoformat(run[k]) for k in ('started_at', 'finished_at')]
        if started.tzinfo is None or finished.tzinfo is None or finished < started:
            raise ValueError('Invalid timestamp order or absent timezone')
    except (ValueError, TypeError) as exc:
        raise InvalidEvidence('Run timestamps must be ordered ISO-8601 values with timezones') from exc
    if run['track'] not in {'closed-book', 'tool-assisted', 'smoke-test'}:
        raise InvalidEvidence('Unknown evaluation track')
    suite = taskset(benchmark)
    if run['dataset_sha256'] != benchmark.digest or run['taskset_sha256'] != suite['taskset_sha256']:
        raise InvalidEvidence('Run does not target this exact dataset/taskset')
    tasks = {t['task_id']: t for t in suite['tasks']}
    if run.get('schema_version') == 2:
        assigned = run.get('assigned_task_ids')
        if not isinstance(assigned, list) or not assigned or len(assigned) != len(set(assigned)) or not set(assigned) <= tasks.keys():
            raise InvalidEvidence('V2 runs require a distinct, declared task assignment')
        if run.get('assignment_sha256') != canonical_hash(assigned):
            raise InvalidEvidence('Task assignment hash mismatch')
        if run.get('configuration_sha256') != canonical_hash(run.get('configuration')):
            raise InvalidEvidence('Run configuration hash mismatch')
        config = run['configuration']
        if any(run.get(k) != config.get(k) for k in ('model', 'budget', 'track', 'assigned_task_ids')):
            raise InvalidEvidence('Run identity, budget, and assignment must match the frozen configuration')
        if run.get('tools', {}).get('adapter_command') != config.get('adapter'):
            raise InvalidEvidence('Run adapter does not match its frozen configuration')
        if run.get('tools', {}).get('access_policy') != config.get('tools', {'model_tools': [], 'network': 'provider-api-only'}):
            raise InvalidEvidence('Run tool access does not match its frozen configuration')
        if run.get('state') not in {'running', 'sealed'}:
            raise InvalidEvidence('Run state must be running or sealed')
        for relative, digest in run.get('evidence_index', {}).items():
            if sha256_file(artifact_path(directory, relative)) != digest:
                raise InvalidEvidence(f'Sealed evidence hash mismatch: {relative}')
    attempt_ids = set()
    attempted_tasks = set()
    for attempt in run['attempts']:
        if not isinstance(attempt, dict):
            raise InvalidEvidence('Each attempt must be a JSON object')
        if attempt.get('attempt_id') in attempt_ids or not attempt.get('attempt_id'):
            raise InvalidEvidence('Attempt IDs must be present and unique within a run')
        attempt_ids.add(attempt['attempt_id'])
        if attempt.get('task_id') not in tasks:
            raise InvalidEvidence('Attempt references an unknown or baseline-resolved task')
        if run.get('schema_version') == 2 and attempt['task_id'] not in run['assigned_task_ids']:
            raise InvalidEvidence('Attempt falls outside the declared task assignment')
        if run.get('schema_version') == 2 and attempt['task_id'] in attempted_tasks:
            raise InvalidEvidence('V2 suite runs allow one attempt per assigned task')
        attempted_tasks.add(attempt['task_id'])
        if attempt.get('status') not in {'unsolved', 'proof_candidate', 'error', 'budget_exhausted'}:
            raise InvalidEvidence('Unknown attempt status')
        artifacts = attempt.get('artifacts', [])
        claims = attempt.get('claims', [])
        if not isinstance(claims, list) or not isinstance(artifacts, list):
            raise InvalidEvidence('Attempt claims and artifacts must be lists')
        if attempt['status'] == 'proof_candidate' and (not claims or not artifacts):
            raise InvalidEvidence('A proof candidate needs exact claims and at least one proof artifact')
        if attempt['status'] != 'proof_candidate' and claims:
            raise InvalidEvidence('Only proof candidates may assert claims')
        for claim in claims:
            benchmark.baseline.validate_atom(Atom.read(claim))
        for artifact in artifacts:
            if not isinstance(artifact, dict) or not isinstance(artifact.get('path'), str):
                raise InvalidEvidence('Each artifact needs a path and SHA-256 hash')
            path = artifact_path(directory, artifact['path'])
            if sha256_file(path) != artifact.get('sha256'):
                raise InvalidEvidence(f'Artifact hash mismatch: {artifact["path"]}')
        if attempt.get('request_path'):
            request = read_json(artifact_path(directory, attempt['request_path']))
            if canonical_hash(request) != attempt.get('prompt_sha256') or request.get('task', {}).get('task_id') != attempt['task_id']:
                raise InvalidEvidence('Stored prompt does not match the attempt')
    if run.get('schema_version') == 2:
        charged = 0
        measured_input = measured_output = 0
        required = {'config.json', 'taskset.json'}
        for attempt in run['attempts']:
            value = attempt.get('budget_charge_tokens')
            if type(value) is not int or value < 0:
                raise InvalidEvidence('Every V2 attempt requires a nonnegative token charge')
            usage = attempt.get('usage', {})
            if not isinstance(usage, dict) or any(type(usage[k]) is not int or usage[k] < 0 for k in ('input_tokens', 'output_tokens', 'total_tokens') if usage.get(k) is not None):
                raise InvalidEvidence('Attempt usage requires nonnegative integer token counts')
            if value < max(usage.get('total_tokens') or 0, (usage.get('input_tokens') or 0) + (usage.get('output_tokens') or 0)):
                raise InvalidEvidence('Token charge may not be below measured usage')
            if type(attempt.get('request_made')) is not bool or type(attempt.get('usage_complete')) is not bool:
                raise InvalidEvidence('Every V2 attempt must record request and usage status')
            charged += value
            measured_input += attempt.get('usage', {}).get('input_tokens', 0) or 0
            measured_output += attempt.get('usage', {}).get('output_tokens', 0) or 0
            if not attempt.get('request_path'):
                raise InvalidEvidence('Every V2 attempt requires its captured request')
            if attempt.get('request_path'):
                required.add(attempt['request_path'])
                parent = Path(attempt['request_path']).parent
                captures = ('recovery.json',) if attempt.get('recovered_interruption') is True else ('response.json', 'stderr.txt')
                required.update(str(parent / p) for p in captures)
            required.update(a['path'] for a in attempt.get('artifacts', []))
        if run.get('usage') != {'charged_tokens': charged, 'measured_input_tokens': measured_input, 'measured_output_tokens': measured_output}:
            raise InvalidEvidence('Run usage totals must equal the recorded attempts')
        if run.get('state') == 'sealed':
            if run.get('in_flight') or run.get('unattempted_task_ids') != [t for t in run['assigned_task_ids'] if t not in attempted_tasks]:
                raise InvalidEvidence('Sealed runs must account for every assigned task and have no in-flight request')
            index = run.get('evidence_index', {})
            if not required <= index.keys():
                raise InvalidEvidence('Sealed evidence index must cover config, taskset, requests, transcripts, and proof artifacts')
            saved_config = read_json(artifact_path(directory, 'config.json'))
            saved_suite = read_json(artifact_path(directory, 'taskset.json'))
            if canonical_hash(saved_config) != run['configuration_sha256'] or saved_suite != suite:
                raise InvalidEvidence('Sealed config or taskset does not match the run')


def evaluate_run(benchmark: Benchmark, manifest: Path) -> dict:
    from .reviews import history_status, registry, validate_independence_review
    run = read_json(manifest)
    validate_run(benchmark, run, manifest.parent)
    run_hash = canonical_hash(run)
    reviews = registry(benchmark, 'ai_reviews')
    accepted = []
    provenance = {}
    verified_attempts, rejected_attempts, pending_attempts = [], [], []
    for attempt in run['attempts']:
        if attempt['status'] != 'proof_candidate':
            continue
        matches = [r for r in reviews if r.get('run_sha256') == run_hash
                   and r.get('dataset_sha256') == benchmark.digest and r.get('attempt_id') == attempt['attempt_id']
                   and r.get('attempt_sha256') == canonical_hash(attempt)]
        exact = matches[-1] if matches else None
        if exact is None or exact.get('status') not in {'accepted', 'rejected'}:
            pending_attempts.append(attempt['attempt_id'])
            continue
        if exact['status'] == 'rejected':
            rejected_attempts.append(attempt['attempt_id'])
            continue
        verified = exact.get('verified_claims', [])
        if not {Atom.read(c) for c in verified} <= {Atom.read(c) for c in attempt.get('claims', [])}:
            raise InvalidEvidence('Accepted review includes a claim not made by this model attempt')
        if exact.get('artifact_hashes') != [a['sha256'] for a in attempt.get('artifacts', [])] or not exact.get('verification_record'):
            raise InvalidEvidence('Accepted review must match the exact sealed artifact set and verification record')
        proof_report = exact.get('proof_verification') or {}
        source_evidence = {}
        if any(c['relation'] != 'independence' for c in verified) and (proof_report or attempt.get('submission_manifest') is not None):
            from .proofevidence import validate_proof_evidence
            source_evidence = validate_proof_evidence(benchmark, proof_report, attempt, manifest.parent)
        if 'literature_dependencies' in proof_report or any(
                any(isinstance(name, str) and name.startswith('Literature.') for name in target.get('axioms', []))
                for target in proof_report.get('targets', [])):
            from .literature import require_approved_dependencies
            require_approved_dependencies(benchmark, proof_report)
        independence = validate_independence_review(benchmark, exact, verified)
        accepted.extend(verified)
        for claim in verified:
            condition = {}
            if claim['relation'] == 'independence':
                certificate = next(c for c in independence['claim_certificates']
                                   if (c['left'], c['right']) == (claim['left'], claim['right']))
                condition = {'independence_review': {k: v for k, v in independence.items()
                                                     if k != 'claim_certificates'} | {'claim_certificate': certificate}}
            provenance.setdefault(Atom.read(claim).key, []).append({'attempt_id': attempt['attempt_id'],
                'artifact_hashes': exact['artifact_hashes'], 'verification_record': exact['verification_record'],
                **({'proof_source': source_evidence} if source_evidence else {}), **condition})
        verified_attempts.append(attempt['attempt_id'])
    accepted = [a.json() for a in dict.fromkeys(Atom.read(c) for c in accepted)]
    consequences = benchmark.score({'claims': accepted})
    direct = {(a['left'], a['right']) for a in accepted} & benchmark.unresolved
    suite = taskset(benchmark)
    suite_count = len(suite['tasks'])
    unique_tasks = len({a['task_id'] for a in run['attempts']})
    assigned = run.get('assigned_task_ids', [a['task_id'] for a in run['attempts']])
    full_suite = len(set(assigned)) == suite_count
    run_reviews = [r for r in registry(benchmark, 'ai_run_reviews') if r.get('run_sha256') == run_hash
                   and r.get('dataset_sha256') == benchmark.digest and r.get('taskset_sha256') == run['taskset_sha256']]
    run_review = run_reviews[-1] if run_reviews else None
    integrity_ok = bool(run_review and run_review.get('status') == 'accepted' and run_review.get('verification_record'))
    completed_answers = sum(a['status'] in {'unsolved', 'proof_candidate'} and a.get('request_made', run.get('schema_version') == 1)
                            for a in run['attempts'])
    opened, known, history = history_status(benchmark)
    resolved = {(r['left'], r['right']) for r in consequences['resolutions']}
    if benchmark.policy['release_stage'] == 'certified':
        opened = benchmark.certified_eligibility()
        known = benchmark.unresolved - opened
    history_pending = resolved - opened - known
    launch_ready = False
    if benchmark.policy['release_stage'] == 'operational' and run.get('schema_version') == 2:
        from .runner import frozen_release
        frozen_release(benchmark)
        launch_ready = True
    elif benchmark.policy['release_stage'] == 'certified':
        launch_ready = full_suite
    official_ready = (launch_ready and run['track'] != 'smoke-test' and integrity_ok and
                      run.get('state', 'sealed') == 'sealed' and not pending_attempts and not history_pending
                      and completed_answers > 0 and run.get('usage', {}).get('charged_tokens', 0) <= run['budget'].get('max_total_tokens', 10**100))
    credited = [r for r in consequences['resolutions'] if (r['left'], r['right']) in opened]
    return {
        'run_id': run['run_id'], 'model': run['model'], 'track': run['track'],
        'run_sha256': run_hash, 'dataset_sha256': benchmark.digest,
        'attempt_count': len(run['attempts']), 'recorded_invocation_count': sum(bool(a.get('request_path')) for a in run['attempts']),
        'unique_task_count': unique_tasks, 'assigned_task_count': len(assigned), 'task_count': suite_count,
        'completed_model_answer_count': completed_answers,
        'full_suite': full_suite, 'scope': 'full-suite' if full_suite else 'declared-subset',
        'run_integrity_reviewed': integrity_ok, 'proof_candidate_count': sum(a['status'] == 'proof_candidate' for a in run['attempts']),
        'verified_attempt_count': len(verified_attempts), 'verified_attempt_ids': verified_attempts,
        'pending_attempt_ids': pending_attempts, 'rejected_attempt_ids': rejected_attempts,
        'provisional_verified_points': consequences['score'], 'direct_verified_pairs': len(direct),
        'consequence_verified_pairs': consequences['score'] - len(direct),
        'history_pending_pairs': [{'left': a, 'right': b} for a, b in sorted(history_pending)],
        'excluded_known_at_cutoff_pairs': [{'left': a, 'right': b} for a, b in sorted(resolved & known)],
        'history_review_sha256': canonical_hash(registry(benchmark, 'history_reviews')),
        'official_score': len(credited) if official_ready else None, 'credited_resolutions': credited if official_ready else [],
        'verified_claim_provenance': provenance, 'provisional_resolutions': consequences['resolutions'],
        'status': 'official' if official_ready else 'awaiting-review' if launch_ready and run['track'] != 'smoke-test' else 'not-rankable',
        'verification_note': 'Existing literature is an explicit trusted baseline. Positive points require accepted model proofs and historical review of every credited pair. Run provenance and all candidate answers must be reviewed before publishing a score.',
    }


def leaderboard(benchmark: Benchmark, manifests: list[str]) -> list[dict]:
    """Publish reviewed runs; ranks are within identical declared evaluation cohorts."""
    records = []
    seen = set()
    for relative in manifests:
        path = artifact_path(benchmark.root, relative)
        result = evaluate_run(benchmark, path)
        if result['status'] != 'official' or result['official_score'] is None:
            raise InvalidEvidence(f'Leaderboard run is not officially admissible: {relative}')
        if result['run_sha256'] in seen:
            raise InvalidEvidence('A run may appear only once on the leaderboard')
        seen.add(result['run_sha256'])
        run = read_json(path)
        cohort = canonical_hash({'taskset_sha256': run['taskset_sha256'], 'track': run['track'], 'budget': run['budget'], 'assignment_sha256': run.get('assignment_sha256'), 'access_policy': run.get('tools', {}).get('access_policy')})
        records.append({'model': run['model'], 'run_id': run['run_id'], 'run_sha256': result['run_sha256'],
                        'score': result['official_score'], 'verified_points': result['official_score'],
                        'track': run['track'], 'budget': run['budget'], 'scope': result['scope'], 'assigned_task_count': result['assigned_task_count'], 'cohort_sha256': cohort,
                        'date': run['finished_at'], 'verification_status': 'Verified evaluation',
                        'kind': 'official-model-run',
                        'independence_results': {key: evidence for key, evidence in result['verified_claim_provenance'].items()
                                                 if any('independence_review' in item for item in evidence)},
                        'report_url': 'https://github.com/tkwa/inclusion-bench/blob/' +
                                      benchmark.policy.get('repository_ref', 'main') + '/' + relative})
    records.sort(key=lambda r: (r['cohort_sha256'], -r['score'], r['run_id']))
    cohorts = {}
    for record in records:
        previous = cohorts.setdefault(record['cohort_sha256'], [])
        record['rank'] = previous[-1]['rank'] if previous and previous[-1]['score'] == record['score'] else len(previous) + 1
        previous.append(record)
    return records


def run_adapter(benchmark: Benchmark, adapter: list[str], model: str, model_version: str,
                selected_tasks: list[str], output: Path, wall_seconds: int = 60,
                track: str = 'tool-assisted') -> Path:
    if wall_seconds < 1 or wall_seconds > 86400:
        raise InvalidEvidence('Wall-time budget must be between 1 and 86,400 seconds')
    if not adapter or not model.strip() or not model_version.strip():
        raise InvalidEvidence('Adapter command, model name, and exact version are required')
    if track not in {'closed-book', 'tool-assisted', 'smoke-test'}:
        raise InvalidEvidence('Unknown evaluation track')
    output = output.resolve()
    suite = taskset(benchmark)
    by_id = {t['task_id']: t for t in suite['tasks']}
    if not selected_tasks or len(selected_tasks) != len(set(selected_tasks)) or any(t not in by_id for t in selected_tasks):
        raise InvalidEvidence('Choose a nonempty list of distinct valid task IDs')
    if output.exists():
        raise InvalidEvidence('Run output directory already exists; runs are immutable')
    output.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    deadline = time.monotonic() + wall_seconds
    attempts = []
    for i, task_id in enumerate(selected_tasks):
        attempt = {'attempt_id': f'attempt-{i+1:04d}', 'task_id': task_id, 'status': 'budget_exhausted', 'claims': [], 'artifacts': []}
        remaining = deadline - time.monotonic()
        if remaining > 0:
            request = {'task': by_id[task_id], 'classes': benchmark.catalog, 'knowledge': benchmark.knowledge,
                       'dataset_sha256': benchmark.digest, 'time_remaining_seconds': remaining,
                       'response_schema': {'status': 'unsolved|proof_candidate', 'claims': 'list of relation/left/right objects', 'artifacts': 'list of relative paths to files written in this run directory'}}
            request_name = f'request-{i+1:04d}.json'
            (output / request_name).write_text(json.dumps(request, indent=2, ensure_ascii=False)+'\n')
            attempt['prompt_sha256'] = canonical_hash(request)
            attempt['request_path'] = request_name
            try:
                # The adapter is trusted executable configuration chosen by the evaluator.
                # This is not a sandbox for untrusted Lean proof compilation.
                returncode, response = execute_adapter(adapter, output / request_name,
                    output / f'response-{i+1:04d}.json', output / f'stderr-{i+1:04d}.txt', output, deadline)
                if returncode:
                    attempt['status'] = 'error'
                    attempt['error'] = f'Adapter exited with code {returncode}'
                else:
                    if not isinstance(response, dict) or not isinstance(response.get('claims', []), list) or not isinstance(response.get('artifacts', []), list):
                        raise InvalidEvidence('Adapter response must be an object with claims and artifacts lists')
                    if response.get('status') not in {'unsolved','proof_candidate'}:
                        raise InvalidEvidence('Adapter response status must be unsolved or proof_candidate')
                    if response['status'] == 'proof_candidate' and (not response.get('claims') or not response.get('artifacts')):
                        raise InvalidEvidence('A proof candidate requires claims and proof artifacts')
                    if response['status'] == 'unsolved' and response.get('claims'):
                        raise InvalidEvidence('Unsolved attempts cannot assert claims')
                    for claim in response.get('claims', []):
                        benchmark.baseline.validate_atom(Atom.read(claim))
                    from .literature import validate_requests
                    literature = validate_requests(benchmark, response.get('literature_requests', []))
                    if literature and response['status'] != 'proof_candidate':
                        raise InvalidEvidence('Only a proof candidate may request literature dependencies')
                    candidate = {**attempt, 'status': response['status'], 'claims': response.get('claims', []),
                                 'literature_requests': literature,
                                 'artifacts': [{'path': str(artifact_path(output, p).relative_to(output)),
                                                'sha256': sha256_file(artifact_path(output, p))}
                                               for p in response.get('artifacts', [])]}
                    if response.get('submission_manifest') is not None:
                        from .proofevidence import validate_submission_artifacts
                        candidate['submission_manifest'] = response['submission_manifest']
                        candidate['submission_manifest'] = validate_submission_artifacts(benchmark, candidate, output)
                    attempt.update(candidate)
            except subprocess.TimeoutExpired:
                attempt['status'] = 'budget_exhausted'
            except (ValueError, OSError, InvalidEvidence, TypeError, KeyError, AttributeError) as exc:
                attempt.update(status='error', claims=[], artifacts=[], error=str(exc))
        attempts.append(attempt)
    run = {'schema_version':1, 'run_id':output.name, 'model':{'name':model,'version':model_version},
           'track':track, 'dataset_sha256':benchmark.digest,'taskset_sha256':suite['taskset_sha256'],
           'budget':{'wall_time_seconds':wall_seconds,'max_cpu_cores':4,'memory_limit_mib':16384,
                     'enforcement':'Adapter wall time enforced; CPU/RAM isolation must be supplied by adapter/container and reported separately.'},
           'tools':{'adapter_command':adapter,'external_tool_policy':'Evaluator must record and enforce tool access; track labels alone do not enforce it.'},
           'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'attempts':attempts}
    validate_run(benchmark,run,output)
    manifest=output/'run.json'
    manifest.write_text(json.dumps(run,indent=2,ensure_ascii=False)+'\n')
    return manifest
