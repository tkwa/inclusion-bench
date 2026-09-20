"""Fail if rebuilding changes any checked-in generated artifact."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = [ROOT / p for p in ("data/classes.json", "data/knowledge.json", "data/formalization.json", "data/eligibility.json", "evaluation/tasks.json", "web/benchmark.json", "lean/InclusionBench/Catalog.lean", "lean/ExampleConsequence.lean", "lean/ComplementExample.lean", "lean/ComplementSwapExample.lean", "lean/ContrapositiveExample.lean", "lean/CollapseExample.lean")]
paths += [ROOT / 'schemas' / name for name in (
    'ai-run.schema.json', 'adapter-response.schema.json', 'submission.schema.json')]
before = {p: p.read_bytes() if p.exists() else None for p in paths}
runpy.run_path(str(ROOT / "scripts/build_release.py"), run_name="__main__")
changed = [str(p.relative_to(ROOT)) for p in paths if before[p] != p.read_bytes()]
if changed:
    raise SystemExit("Stale generated artifacts: " + ", ".join(changed))
print("Generated artifacts are reproducible.")
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark, canonical_hash, read_json
from inclusion_bench.evaluation import sha256_file
from inclusion_bench.runner import frozen_release
benchmark = Benchmark(ROOT)
freeze = frozen_release(benchmark)
audit_path = ROOT / 'research/baseline-audit.json'
audit = read_json(audit_path)
binding = audit['binding']
if binding['classes_sha256'] != canonical_hash(benchmark.catalog) or binding['knowledge_sha256'] != canonical_hash(benchmark.knowledge):
    raise SystemExit('Baseline audit does not match the frozen mathematical data')
if freeze['baseline_audit_sha256'] != sha256_file(audit_path):
    raise SystemExit('Frozen baseline audit hash mismatch')
if audit.get('schema_version') == 2:
    if binding['dataset_sha256'] != benchmark.digest or audit['cutoff'] != benchmark.policy['cutoff']:
        raise SystemExit('Audit policy/dataset binding is stale')
    audited = {(p['left'], p['right']): p['status'] for p in audit['pair_index']}
    actual = {(p['left'], p['right']): p['status'] for p in benchmark.matrix()['pairs']}
    if len(audit['pair_index']) != len(actual) or audited != actual:
        raise SystemExit('Audit pair index differs from the current mathematical classifications')
    for relative, digest in audit['supporting_report_sha256'].items():
        if sha256_file(ROOT / relative) != digest:
            raise SystemExit('Audit evidence changed after indexing: ' + relative)
    if sha256_file(ROOT / 'research/audit-assessment.json') != binding['assessment_sha256']:
        raise SystemExit('Audit assessment changed after indexing')
    adoption = audit.get('policy_adoption')
    if adoption:
        original = ROOT / adoption['previous_assessment_file']
        if sha256_file(original) != adoption['previous_assessment_sha256']:
            raise SystemExit('Original audit assessment changed during policy adoption')
        if read_json(original)['dataset_sha256'] != adoption['previous_dataset_sha256']:
            raise SystemExit('Policy adoption does not identify the original audited dataset')
        for key in ('classes_sha256', 'knowledge_sha256'):
            if adoption['unchanged'][key] != binding[key]:
                raise SystemExit('Policy adoption cannot carry history across changed mathematical data')
        if (adoption['unchanged']['cutoff'] != benchmark.policy['cutoff'] or
                adoption['unchanged']['candidate_questions'] != len(benchmark.unresolved)):
            raise SystemExit('Policy adoption changed the historical scope')
    migration = audit.get('roster_migration')
    if migration:
        report_path = ROOT / migration['comparison_report']
        report = read_json(report_path)
        if sha256_file(report_path) != migration['comparison_report_sha256']:
            raise SystemExit('Roster migration report changed after review')
        comparison = runpy.run_path(str(ROOT / 'scripts/audit_roster_migration.py'))['compare']()
        if report != comparison or report['dataset_sha256'] != benchmark.digest:
            raise SystemExit('Roster migration does not match the current and preserved parent datasets')
        parent_path = ROOT / migration['previous_assessment_file']
        if (sha256_file(parent_path) != migration['previous_assessment_sha256'] or
                read_json(parent_path)['dataset_sha256'] != report['parent_dataset_sha256']):
            raise SystemExit('Roster migration does not bind the preserved parent assessment')
        if migration['inherited_context_classifications_unchanged'] and report['changed_parent_context_pairs']:
            raise SystemExit('Roster migration falsely claims unchanged parent classifications')
    history_records = read_json(ROOT / 'data/history_reviews.json')
    for record in history_records:
        recorded_hash = record.get('review_sha256')
        if recorded_hash != canonical_hash({k: v for k, v in record.items() if k != 'review_sha256'}):
            raise SystemExit('Historical review record hash mismatch')
    initial = [r for r in history_records if r.get('audit_id') == audit['audit_id'] and
               r.get('dataset_sha256') == benchmark.digest and r.get('status') == 'accepted' and
               r.get('baseline_audit_sha256') == freeze['baseline_audit_sha256']]
    intended = {(p['left'], p['right']): p['historical_assessment']
                for p in audit['pair_index'] if p['status'] == 'unreviewed'}
    if not any(len(r['pairs']) == len(intended) and
               {(p['left'], p['right']): p['status'] for p in r['pairs']} == intended for r in initial):
        raise SystemExit('Release-wide historical decisions are missing or do not match their audit')
    from inclusion_bench.reviews import history_status
    opened, known, _ = history_status(benchmark)
    if opened | known != benchmark.unresolved:
        raise SystemExit('Historical registry does not cover the full current question suite')
    # Later documented known-at-cutoff corrections may override the initial
    # audit without rewriting its frozen evidence or an earlier model run.
print('Release freeze and baseline audit match the generated data.')
