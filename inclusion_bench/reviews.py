"""Maintainer review records: mathematics, run provenance, and historical eligibility.

These are explicit trusted inputs. They are never taken from model output.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from .benchmark import Benchmark, canonical_hash, read_json
from .engine import Atom, InvalidEvidence


def registry(benchmark: Benchmark, name: str) -> list[dict]:
    path = benchmark.root / 'data' / f'{name}.json'
    return read_json(path) if path.exists() else []


def save_record(benchmark: Benchmark, name: str, record: dict) -> dict:
    records = registry(benchmark, name)
    record = {**record, 'recorded_at': datetime.now(timezone.utc).isoformat()}
    record['review_sha256'] = canonical_hash(record)
    records.append(record)
    path = benchmark.root / 'data' / f'{name}.json'
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(records, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)
    return record


def _reviewer(review: dict) -> None:
    for field in ('reviewer', 'rationale'):
        if not isinstance(review.get(field), str) or not review[field].strip():
            raise InvalidEvidence(f'Review requires {field}')
    if review.get('status') not in {'accepted', 'rejected'}:
        raise InvalidEvidence('Review status must be accepted or rejected')


def history_status(benchmark: Benchmark) -> tuple[set, set, dict]:
    latest = {}
    for record in registry(benchmark, 'history_reviews'):
        if record.get('dataset_sha256') != benchmark.digest:
            continue
        for pair in record.get('pairs', []):
            latest[(pair['left'], pair['right'])] = {**pair, 'review_sha256': record.get('review_sha256')}
    opened = {p for p, r in latest.items() if r['status'] == 'open_at_cutoff'}
    known = {p for p, r in latest.items() if r['status'] == 'known_at_cutoff'}
    return opened, known, latest


def record_history_review(benchmark: Benchmark, review: dict) -> dict:
    _reviewer(review)
    if review.get('status') != 'accepted' or review.get('dataset_sha256') != benchmark.digest:
        raise InvalidEvidence('Historical decisions require accepted review of this exact dataset')
    if not isinstance(review.get('pairs'), list) or not review['pairs']:
        raise InvalidEvidence('Historical review requires at least one ordered pair')
    seen = set()
    for pair in review['pairs']:
        atom = Atom('inclusion', pair['left'], pair['right'])
        benchmark.baseline.validate_atom(atom)
        if atom.pair in seen or atom.pair not in benchmark.unresolved:
            raise InvalidEvidence('Historical review pairs must be distinct candidate questions')
        seen.add(atom.pair)
        if pair.get('status') not in {'open_at_cutoff', 'known_at_cutoff'}:
            raise InvalidEvidence('Historical status must be open_at_cutoff or known_at_cutoff')
        if not pair.get('evidence') or not pair.get('rationale'):
            raise InvalidEvidence('Every historical decision requires evidence and rationale')
    return save_record(benchmark, 'history_reviews', review)


def review_packet(benchmark: Benchmark, manifest: Path) -> dict:
    from .evaluation import evaluate_run, validate_run
    run = read_json(manifest)
    validate_run(benchmark, run, manifest.parent)
    run_hash = canonical_hash(run)
    pending_history = evaluate_run(benchmark, manifest)['history_pending_pairs']
    return {'schema_version': 1, 'run_sha256': run_hash, 'dataset_sha256': benchmark.digest,
            'taskset_sha256': run['taskset_sha256'], 'run_id': run['run_id'],
            'run_review': {'run_sha256': run_hash, 'reviewer': '', 'rationale': '', 'status': 'pending',
                'checks': {'model_identity': False, 'configuration_and_tools': False, 'budgets_and_usage': False,
                           'transcripts_and_artifacts': False, 'no_unreported_human_assistance': False}},
            'proof_reviews': [{'run_sha256': run_hash, 'attempt_id': a['attempt_id'], 'attempt_sha256': canonical_hash(a),
                'claims': a.get('claims', []), 'artifact_hashes': [p['sha256'] for p in a.get('artifacts', [])],
                'reviewer': '', 'rationale': '', 'status': 'pending', 'proof_report': None}
                for a in run['attempts'] if a['status'] == 'proof_candidate'],
            'history_review': {'dataset_sha256': benchmark.digest, 'reviewer': '', 'rationale': '', 'status': 'pending',
                'pairs': [{**p, 'status': 'pending', 'evidence': [], 'rationale': ''} for p in pending_history]},
            'instructions': 'Complete reviews using independent evidence. Pending entries cannot be admitted. Ordinary accepted claims require the sandboxed Lean report; historical eligibility is reviewed separately for every point.'}


def record_run_review(benchmark: Benchmark, manifest: Path, review: dict) -> dict:
    from .evaluation import validate_run
    run = read_json(manifest)
    validate_run(benchmark, run, manifest.parent)
    _reviewer(review)
    if run.get('state', 'sealed') != 'sealed':
        raise InvalidEvidence('Seal the run before reviewing it')
    checks = ('model_identity', 'configuration_and_tools', 'budgets_and_usage', 'transcripts_and_artifacts', 'no_unreported_human_assistance')
    if review['status'] == 'accepted' and not all(review.get('checks', {}).get(c) is True for c in checks):
        raise InvalidEvidence('Run acceptance requires all provenance and budget checks')
    if review.get('run_sha256') != canonical_hash(run):
        raise InvalidEvidence('Review must bind the exact sealed run hash')
    record = {**review, 'dataset_sha256': benchmark.digest, 'taskset_sha256': run['taskset_sha256'],
              'verification_record': review['rationale']}
    return save_record(benchmark, 'ai_run_reviews', record)


def record_proof_review(benchmark: Benchmark, manifest: Path, review: dict) -> dict:
    from .evaluation import artifact_path, sha256_file, validate_run
    run = read_json(manifest)
    validate_run(benchmark, run, manifest.parent)
    _reviewer(review)
    attempt = next((a for a in run['attempts'] if a['attempt_id'] == review.get('attempt_id')), None)
    if not attempt or attempt['status'] != 'proof_candidate':
        raise InvalidEvidence('Review must reference a proof-candidate attempt')
    if review.get('run_sha256') != canonical_hash(run) or review.get('attempt_sha256') != canonical_hash(attempt):
        raise InvalidEvidence('Review must bind the exact run and attempt hashes')
    verified = review.get('verified_claims', attempt['claims']) if review['status'] == 'accepted' else []
    submitted = {Atom.read(c) for c in attempt['claims']}
    if not {Atom.read(c) for c in verified} <= submitted:
        raise InvalidEvidence('A reviewer cannot add claims that the model did not submit')
    report = None
    if review['status'] == 'accepted':
        if not verified:
            raise InvalidEvidence('An accepted proof review requires verified claims')
        if any(c['relation'] == 'independence' for c in verified):
            # No claim of an automatic formal ZFC encoding. This separately identified
            # lane requires a precise metatheorem and an expert review record.
            meta = review.get('independence_review', {})
            if not all(meta.get(k) for k in ('encoded_sentence', 'zfc_proof_system', 'metatheory', 'assumptions', 'unprovability_both_polarities', 'expert_report')):
                raise InvalidEvidence('Independence needs an explicit expert metatheory review for both polarities')
        ordinary = {Atom.read(c) for c in verified if c['relation'] != 'independence'}
        if ordinary:
            report_path = Path(review.get('proof_report', ''))
            if not report_path.is_file():
                raise InvalidEvidence('Ordinary accepted claims require a sandboxed Lean verification report')
            report = read_json(report_path)
            if report.get('status') != 'verified' or report.get('dataset_sha256') != benchmark.digest:
                raise InvalidEvidence('Proof report is not verified for this dataset')
            reported = {Atom.read(c) for c in report.get('claims', [])}
            if not ordinary <= reported:
                raise InvalidEvidence('Proof report does not verify every accepted ordinary claim')
            source_hash = report.get('proof_sha256') or report.get('source_sha256')
            if source_hash not in {a['sha256'] for a in attempt.get('artifacts', [])}:
                raise InvalidEvidence('Verified source is not one of this attempt\'s sealed artifacts')
            report = {**report, 'report_sha256': sha256_file(report_path)}
    record = {**review, 'dataset_sha256': benchmark.digest, 'verified_claims': verified,
              'artifact_hashes': [a['sha256'] for a in attempt.get('artifacts', [])],
              'verification_record': review['rationale'], 'proof_verification': report}
    return save_record(benchmark, 'ai_reviews', record)


def publish_run(benchmark: Benchmark, manifest: Path) -> dict:
    """Package reviewed evidence locally; network publication remains explicit."""
    import re
    import shutil
    from .evaluation import artifact_path, evaluate_run, sha256_file
    from .runner import write_json
    manifest = manifest.resolve()
    result = evaluate_run(benchmark, manifest)
    if result['status'] != 'official' or result['official_score'] is None:
        raise InvalidEvidence('Only an officially admissible, reviewed model run can be published')
    run = read_json(manifest)
    if run.get('schema_version') != 2:
        raise InvalidEvidence('Publication packaging requires a sealed V2 run')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,119}', run['run_id']):
        raise InvalidEvidence('Public run IDs must use letters, digits, underscores or hyphens')
    relative = Path('evaluation/published-runs') / run['run_id']
    destination = benchmark.root / relative
    target = destination / 'run.json'
    if destination.exists():
        if not target.is_file() or read_json(target) != run:
            raise InvalidEvidence('A different run already uses this public run ID')
        evaluate_run(benchmark, target)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        import tempfile
        staging = Path(tempfile.mkdtemp(prefix='.publish-', dir=destination.parent))
        try:
            for path, digest in run['evidence_index'].items():
                source = artifact_path(manifest.parent, path)
                copied = staging / path
                copied.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, copied)
                if sha256_file(copied) != digest:
                    raise InvalidEvidence('Evidence changed while preparing publication')
            write_json(staging / 'run.json', run)
            evaluate_run(benchmark, staging / 'run.json')
            staging.rename(destination)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    write_json(destination / 'evaluation.json', result)
    path = str(relative / 'run.json')
    registry_path = benchmark.root / 'data/leaderboard_runs.json'
    records = read_json(registry_path) if registry_path.exists() else []
    if path not in records:
        records.append(path)
        write_json(registry_path, records)
    return {'packaged': path, 'official_score': result['official_score'], 'run_sha256': result['run_sha256'],
            'network_publication_performed': False,
            'next_step': 'Rebuild the website, inspect the packaged evidence and review records, then commit and push to publish.'}
