"""Fail if rebuilding changes any checked-in generated artifact."""
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = [ROOT / p for p in ("data/classes.json", "data/knowledge.json", "data/eligibility.json", "web/benchmark.json", "lean/ExampleConsequence.lean", "lean/ComplementExample.lean", "lean/ComplementSwapExample.lean", "lean/ContrapositiveExample.lean", "lean/CollapseExample.lean")]
before = {p: p.read_bytes() if p.exists() else None for p in paths}
runpy.run_path(str(ROOT / "scripts/build_release.py"), run_name="__main__")
changed = [str(p.relative_to(ROOT)) for p in paths if before[p] != p.read_bytes()]
if changed:
    raise SystemExit("Stale generated artifacts: " + ", ".join(changed))
print("Generated artifacts are reproducible.")
