"""Fail if rebuilding changes any checked-in generated artifact."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = [ROOT / p for p in ("data/classes.json", "data/knowledge.json", "data/formalization.json", "data/eligibility.json", "evaluation/tasks.json", "web/benchmark.json", "lean/ExampleConsequence.lean", "lean/ComplementExample.lean", "lean/ComplementSwapExample.lean", "lean/ContrapositiveExample.lean", "lean/CollapseExample.lean")]
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
print('Release freeze and baseline audit match the generated data.')
