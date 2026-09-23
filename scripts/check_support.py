"""Compile textbook support, fixture proofs, and catalog signatures with pinned Lean."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
compiler = os.environ.get("LEAN_BIN") or shutil.which("lean")
if not compiler or "version 4.19.0" not in subprocess.check_output([compiler, "--version"], text=True):
    raise SystemExit("Set LEAN_BIN to the pinned Lean 4.19.0 compiler; build the core first.")

with tempfile.TemporaryDirectory(prefix="inclusion-support-") as directory:
    build = Path(directory)
    environment = {**os.environ, "LEAN_NUM_THREADS": "1", "LEAN_PATH": f"{build}:{ROOT / 'lean'}"}
    sources = {"InclusionSupport." + p.stem: p for p in (ROOT / "support/InclusionSupport").glob("*.lean")
               if p.stem != "Classes"}
    done = set()

    def compile_module(module):
        if module in done:
            return
        source = sources[module]
        for imported in re.findall(r"^import (\S+)", source.read_text(), re.M):
            if imported in sources:
                compile_module(imported)
        target = build / (module.replace(".", "/") + ".olean")
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([compiler, "-j1", "-DwarningAsError=true", "-o", str(target), str(source)], cwd=ROOT, env=environment, check=True)
        done.add(module)

    for module in sorted(sources):
        compile_module(module)
    for path in sorted((ROOT / "tests/lean").glob("Support*Tests.lean")):
        subprocess.run([compiler, "-j1", str(path)], cwd=ROOT, env=environment, check=True)
    entries = []
    for path in (ROOT / "support").glob("registry-*.json"):
        entries.extend(e for e in json.loads(path.read_text())["theorems"] if e["module"] in sources)
    signatures = "import Lean\n" + "\n".join("import " + m for m in sorted(sources)) + "\nset_option warningAsError true\n"
    signatures += "\n".join(f'example : {e["statement"]} := @{e["name"]}' for e in entries) + "\n"
    approved = ["propext", "Classical.choice", "Quot.sound"] + [e["name"] for e in entries if e.get("kind") == "axiom"]
    signatures += "\nopen Lean Elab Command\nrun_cmd do\n  let env ← getEnv\n"
    signatures += "  let allowed : List String := " + json.dumps(approved) + "\n"
    # Lean emits unsafe compiler-only stages for safe definitions. Inspect
    # kernel declarations and reject any public unsafe support declaration.
    signatures += "  for (name, info) in env.constants.toList do\n"
    signatures += '    if name.toString.startsWith "InclusionBench.Support." && !(info.isUnsafe && name.isInternal) then\n'
    signatures += '      if info.isUnsafe then throwError "Unsafe support declaration: {name}"\n'
    signatures += '      for dependency in (((CollectAxioms.collect name).run env).run {}).2.axioms do\n'
    signatures += '        unless allowed.contains dependency.toString do\n'
    signatures += '          throwError "Unregistered axiom {dependency} used by {name}"\n'
    for entry in entries:
        signatures += "\nrun_cmd do\n  let env ← getEnv\n"
        signatures += f'  let some info := env.find? `{entry["name"]} | throwError "Missing catalog declaration"\n'
        expected = "true" if entry.get("kind") == "axiom" else "false"
        signatures += f'  unless (match info with | .axiomInfo _ => true | _ => false) == {expected} do\n'
        signatures += f'    throwError "Wrong catalog declaration kind: {entry["name"]}"\n'
    # Keep the temporary Lean source under the project root accepted by Lean.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", prefix=".support-signatures-", dir=ROOT) as handle:
        handle.write(signatures)
        handle.flush()
        subprocess.run([compiler, "-j1", handle.name], cwd=ROOT, env=environment, check=True)
    print(f"Checked {len(sources)} support modules, {len(entries)} catalog signatures, and textbook proof fixtures.")
