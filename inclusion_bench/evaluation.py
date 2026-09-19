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
import time
from datetime import datetime, timezone
from pathlib import Path

from .benchmark import Benchmark, canonical_hash, read_json
from .engine import Atom, InvalidEvidence


def execute_adapter(adapter: list[str], request_file: Path, response_file: Path, error_file: Path,
                    directory: Path, deadline: float) -> tuple[int, dict]:
    """Run a trusted POSIX adapter; bound wall time and captured output, including descendants."""
    if os.name != 'posix':
        raise InvalidEvidence('The adapter runner currently requires Linux or macOS')
    with request_file.open('rb') as stdin, response_file.open('wb') as stdout, error_file.open('wb') as stderr:
        process = subprocess.Popen(adapter, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=directory, start_new_session=True,
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
            'eligibility': 'open_at_cutoff' if certified else 'unreviewed',
            'allowed_resolutions': ['inclusion', 'separation', 'independence'],
            'prompt': f'Resolve whether {labels[left]} is contained in {labels[right]} under the attached exact class conventions. Supply a rigorous proof of inclusion, a rigorous proof of non-inclusion, or a precise ZFC-independence metatheorem. If you cannot resolve it, return unsolved. A conjecture, oracle separation, or conditional result with a new unproved assumption is not a solution. Identify every additional ordered-pair consequence your proof establishes. Return proof artifacts and exact claim objects; the evaluator, not the model, decides verification and points.'
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
    if run.get('schema_version') != 1 or not isinstance(run['attempts'], list):
        raise InvalidEvidence('Expected schema_version 1 and a list of attempts')
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
    attempt_ids = set()
    for attempt in run['attempts']:
        if not isinstance(attempt, dict):
            raise InvalidEvidence('Each attempt must be a JSON object')
        if attempt.get('attempt_id') in attempt_ids or not attempt.get('attempt_id'):
            raise InvalidEvidence('Attempt IDs must be present and unique within a run')
        attempt_ids.add(attempt['attempt_id'])
        if attempt.get('task_id') not in tasks:
            raise InvalidEvidence('Attempt references an unknown or baseline-resolved task')
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


def evaluate_run(benchmark: Benchmark, manifest: Path) -> dict:
    run = read_json(manifest)
    validate_run(benchmark, run, manifest.parent)
    run_hash = canonical_hash(run)
    registry_file = benchmark.root / 'data/ai_reviews.json'
    registry = read_json(registry_file) if registry_file.exists() else []
    accepted = []
    provenance = {}
    verified_attempts = []
    for attempt in run['attempts']:
        exact = next((r for r in registry if r.get('run_sha256') == run_hash
            and r.get('dataset_sha256') == benchmark.digest and r.get('attempt_id') == attempt['attempt_id']
            and r.get('attempt_sha256') == canonical_hash(attempt) and r.get('status') == 'accepted'), None)
        if exact is not None:
            # Registry is a maintainer-controlled trust input, never model response metadata.
            if exact.get('verified_claims') != attempt.get('claims') or exact.get('artifact_hashes') != [a['sha256'] for a in attempt.get('artifacts', [])]:
                raise InvalidEvidence('Accepted review does not match the exact artifact set and claims')
            if not exact.get('verification_record'):
                raise InvalidEvidence('An accepted review needs a proof-verification record')
            accepted.extend(exact['verified_claims'])
            for claim in exact['verified_claims']:
                provenance.setdefault(Atom.read(claim).key, []).append({'attempt_id': attempt['attempt_id'], 'artifact_hashes': exact['artifact_hashes'], 'verification_record': exact['verification_record']})
            verified_attempts.append(attempt['attempt_id'])
    accepted = [a.json() for a in dict.fromkeys(Atom.read(c) for c in accepted)]
    consequences = benchmark.score({'claims': accepted})
    direct = {(a['left'], a['right']) for a in accepted} & benchmark.unresolved
    suite_count = len(taskset(benchmark)['tasks'])
    unique_tasks = len({a['task_id'] for a in run['attempts']})
    full_suite = unique_tasks == suite_count
    run_registry_file = benchmark.root / 'data/ai_run_reviews.json'
    run_reviews = read_json(run_registry_file) if run_registry_file.exists() else []
    run_review = next((r for r in run_reviews if r.get('run_sha256') == run_hash and r.get('dataset_sha256') == benchmark.digest
                       and r.get('taskset_sha256') == run['taskset_sha256'] and r.get('status') == 'accepted'
                       and r.get('verification_record')), None)
    official_ready = benchmark.policy['release_stage'] == 'certified' and run['track'] != 'smoke-test' and full_suite and run_review is not None
    official_score = None
    if official_ready:
        # Artifact reviews admit mathematics; a separate run review admits provenance,
        # configuration and budget compliance. Legacy standalone reviews are irrelevant.
        eligible = benchmark.certified_eligibility()
        official_score = sum((r['left'], r['right']) in eligible for r in consequences['resolutions'])
    return {
        'run_id': run['run_id'], 'model': run['model'], 'track': run['track'],
        'run_sha256': run_hash, 'dataset_sha256': benchmark.digest,
        'attempt_count': len(run['attempts']),
        'recorded_invocation_count': sum(bool(a.get('request_path')) for a in run['attempts']),
        'unique_task_count': unique_tasks, 'task_count': suite_count, 'full_suite': full_suite,
        'scope': 'full-suite' if full_suite else 'partial-suite',
        'run_integrity_reviewed': run_review is not None,
        'proof_candidate_count': sum(a['status'] == 'proof_candidate' for a in run['attempts']),
        'verified_attempt_count': len(verified_attempts), 'verified_attempt_ids': verified_attempts,
        'provisional_verified_points': consequences['score'],
        'direct_verified_pairs': len(direct), 'consequence_verified_pairs': consequences['score'] - len(direct),
        'official_score': official_score,
        'verified_claim_provenance': provenance, 'provisional_resolutions': consequences['resolutions'],
        'status': 'official' if official_ready else 'not-rankable',
        'verification_note': 'Model assertions earn no points. Only exact artifacts admitted by the trusted review registry contribute. Official scores remain unavailable until the dataset and proof pipeline are certified.',
    }


def leaderboard(benchmark: Benchmark, manifests: list[str]) -> list[dict]:
    """Publish only reviewed full-suite runs; ranks are within identical evaluation cohorts."""
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
        cohort = canonical_hash({'taskset_sha256': run['taskset_sha256'], 'track': run['track'], 'budget': run['budget']})
        records.append({'model': run['model'], 'run_id': run['run_id'], 'run_sha256': result['run_sha256'],
                        'score': result['official_score'], 'verified_points': result['official_score'],
                        'track': run['track'], 'budget': run['budget'], 'cohort_sha256': cohort,
                        'date': run['finished_at'], 'verification_status': 'Verified evaluation',
                        'kind': 'official-model-run',
                        'report_url': 'https://github.com/tkwa/inclusion-bench/blob/main/' + relative})
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
                    attempt.update(status=response['status'], claims=response.get('claims', []))
                    attempt['artifacts'] = [{'path': p, 'sha256':sha256_file(artifact_path(output,p))} for p in response.get('artifacts', [])]
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
