"""Serial Lean build, exported Python traces and forbidden-proof audit."""
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
compiler = os.environ.get("LEAN_BIN") or shutil.which("lean")
if not compiler:
    raise SystemExit("Install lean/lean-toolchain or set LEAN_BIN to its compiler.")
version = subprocess.check_output([compiler, "--version"], text=True)
if "version 4.19.0" not in version:
    raise SystemExit("The reproducible build requires Lean 4.19.0: " + version)
environment = {**os.environ, "LEAN_BIN": compiler, "LEAN_NUM_THREADS": "1", "LEAN_PATH": str(ROOT / "lean")}
subprocess.run(["sh", "build.sh"], cwd=ROOT / "lean", env=environment, check=True)
for name in ("ExampleConsequence", "ComplementExample", "ComplementSwapExample", "ContrapositiveExample", "CollapseExample"):
    result = subprocess.run([compiler, "-j1", name + ".lean"], cwd=ROOT / "lean", env=environment, check=True, capture_output=True, text=True)
    if "sorryAx" in result.stdout + result.stderr:
        raise SystemExit("Unproved dependency in " + name)
    print(result.stdout.strip())
for path in (ROOT / "lean").rglob("*.lean"):
    if ".lake" in path.parts:
        continue
    # Source scan supplements compilation and #print axioms; it is not a proof verifier.
    text = re.sub(r"/-.*?-/", "", path.read_text(), flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    if re.search(r"\b(sorry|admit|axiom|unsafe|implemented_by|native_decide)\b", text):
        raise SystemExit("Forbidden proof declaration in " + str(path))
print("Lean library and exported inference traces checked without proof holes.")
