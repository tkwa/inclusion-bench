#!/usr/bin/env bash
set -euo pipefail

repository="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repository"

# CPU affinity applies to dependency downloads, cache extraction, and every
# compiler child. The memory limit is 8 GiB of address space per process.
command -v taskset >/dev/null || {
  echo "The resource-limited quantum checker requires Linux taskset." >&2
  exit 2
}
if [[ "${INCLUSION_QUANTUM_CPU_PINNED:-}" != 1 ]]; then
  selected_cpu="$(python3 -c 'import os; print(min(os.sched_getaffinity(0)))')"
  export INCLUSION_QUANTUM_CPU_PINNED=1
  exec taskset -c "$selected_cpu" bash "$repository/scripts/check_quantum.sh" "$@"
fi
ulimit -v 8388608
export LEAN_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 - <<'PY'
import os
if len(os.sched_getaffinity(0)) != 1:
    raise SystemExit("Quantum verification must run on exactly one CPU.")
PY

LEAN_BIN="${LEAN_BIN:-$(command -v lean || true)}"
[[ -n "$LEAN_BIN" && -x "$LEAN_BIN" ]] || {
  echo "Install Lean 4.19.0 or set LEAN_BIN to its compiler." >&2
  exit 2
}
export LEAN_BIN
export PATH="$(dirname "$LEAN_BIN"):$PATH"
case "$("$LEAN_BIN" --version)" in
  *"version 4.19.0"*) ;;
  *) echo "Quantum verification requires Lean 4.19.0." >&2; exit 2 ;;
esac

# The source scan supplements kernel checking and the axiom audit. It is not
# a sandbox for arbitrary Lean metaprograms supplied by benchmark entrants.
python3 - <<'PY'
import json
import re
from pathlib import Path

expected_revision = "c44e0c8ee63ca166450922a373c7409c5d26b00b"
manifest = json.loads(Path("quantum/lake-manifest.json").read_text())
mathlib = next(p for p in manifest["packages"] if p["name"] == "mathlib")
if mathlib["rev"] != expected_revision or mathlib["url"] != "https://github.com/leanprover-community/mathlib4.git":
    raise SystemExit("Quantum dependency lock must use the pinned official Mathlib source.")

def without_comments(text):
    result = []
    depth = 0
    index = 0
    while index < len(text):
        if text.startswith("/-", index):
            depth += 1
            index += 2
        elif depth and text.startswith("-/", index):
            depth -= 1
            index += 2
        elif depth:
            index += 1
        elif text.startswith("--", index):
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
        else:
            result.append(text[index])
            index += 1
    if depth:
        raise SystemExit("Unterminated Lean block comment in source audit.")
    return "".join(result)

for root in (Path("lean"), Path("quantum")):
    for path in root.rglob("*.lean"):
        if ".lake" in path.parts:
            continue
        source = without_comments(path.read_text())
        forbidden = re.search(r"\b(sorry|sorryAx|admit|axiom|unsafe|implemented_by|native_decide)\b", source)
        forbidden = forbidden or re.search(
            r"(?m)^\s*(?:(?:private|protected|noncomputable)\s+)*(?:constant|opaque)\s", source)
        if forbidden:
            raise SystemExit(f"Forbidden proof marker {forbidden[0]!r} in {path}")
PY

bash quantum/setup.sh
actual_revision="$(git -C quantum/.lake/packages/mathlib rev-parse HEAD)"
[[ "$actual_revision" == c44e0c8ee63ca166450922a373c7409c5d26b00b ]] || {
  echo "Installed Mathlib revision does not match the audited pin." >&2
  exit 1
}
git -C quantum/.lake/packages/mathlib diff --quiet
git -C quantum/.lake/packages/mathlib diff --cached --quiet

audit_log="$(mktemp "${TMPDIR:-/tmp}/inclusion-quantum-audit.XXXXXX")"
trap 'rm -f "$audit_log"' EXIT
bash quantum/build.sh 2>&1 | tee "$audit_log"
python3 - "$audit_log" <<'PY'
import re
import sys
from pathlib import Path

output = Path(sys.argv[1]).read_text()
if re.search(r"\b(sorryAx|sorry|admit)\b", output):
    raise SystemExit("Quantum build contains an unproved declaration.")
allowed = {"propext", "Classical.choice", "Quot.sound"}
for match in re.finditer(r"depends on axioms:\s*\[([^\]]*)\]", output):
    dependencies = {item.strip() for item in match[1].split(",") if item.strip()}
    unexpected = dependencies - allowed
    if unexpected:
        raise SystemExit("Unexpected axiom dependencies: " + ", ".join(sorted(unexpected)))
for qualified in (
    'InclusionBench.Quantum.complete_agrees_with_core',
    'InclusionBench.Quantum.every_class_defined',
    'InclusionBench.Quantum.all_catalog_classes_defined',
    'InclusionBench.Quantum.gateFields_injective',
    'InclusionBench.Quantum.basisState_normalized',
    'InclusionBench.Quantum.pauliX_twice',
    'InclusionBench.Quantum.gate_preserves_normSquared',
    'InclusionBench.Quantum.circuit_preserves_normSquared',
    'InclusionBench.Quantum.initialState_preserves_normSquared',
    'InclusionBench.Quantum.acceptance_bounded',
    'InclusionBench.Quantum.empty_witness_normalized',
    'InclusionBench.Quantum.productState_normSquared',
    'InclusionBench.Quantum.productState_normalized',
    'InclusionBench.Quantum.twoWitnessAcceptance_bounded',
    'InclusionBench.Quantum.zeroState_normalized',
    'InclusionBench.Quantum.logspaceAcceptance_bounded',
    'InclusionBench.Quantum.toffoliBasis_twice',
    'InclusionBench.Quantum.reversibleGate_preserves_normSquared',
    'InclusionBench.Quantum.reversibleGateFields_injective',
    'InclusionBench.Quantum.stoquasticCircuit_preserves_normSquared',
    'InclusionBench.Quantum.stoquasticInitialState_preserves_normSquared',
    'InclusionBench.Quantum.stoquasticAcceptance_bounded',
    'InclusionBench.Quantum.measurement_probability_bounded',
    'InclusionBench.Quantum.sampler_state_normalized',
    'InclusionBench.Quantum.identical_quantum_samplers_close',
    'InclusionBench.Quantum.quantum_far_close_disjoint',
    'InclusionBench.Quantum.measurementDifference_bounded',
    'InclusionBench.RealFeasibility.encoded_etr_iff',
    'InclusionBench.RealFeasibility.malformed_input_rejected',
    'InclusionBench.RealFeasibility.finiteAssignment_at',
    'InclusionBench.RealFeasibility.squareTwo_satisfiable',
    'InclusionBench.RealFeasibility.squareTwo_in_etr',
    'InclusionBench.RealFeasibility.negativeSquare_not_satisfiable',
    'InclusionBench.RealFeasibility.negativeSquare_not_in_etr',
    'InclusionBench.IndependentClassicalReview.footprint_never_decreases',
    'InclusionBench.IndependentClassicalReview.footprint_step_upper',
    'InclusionBench.IndependentClassicalReview.unequal_depth_fair_count',
    'InclusionBench.IndependentClassicalReview.unequal_depth_total_mass',
    'InclusionBench.IndependentClassicalReview.majority_tie_rejected',
    'InclusionBench.IndependentClassicalReview.nondeterministic_halted_multiplicity',
    'InclusionBench.IndependentClassicalReview.address_after_head_movement',
    'InclusionBench.IndependentClassicalReview.high_address_bit_is_binary',
    'InclusionBench.IndependentClassicalReview.nonterminal_flag_does_not_accept',
    'InclusionBench.IndependentClassicalReview.query_encoding_holes',
    'InclusionBench.IndependentClassicalReview.variable_count_enforced',
    'InclusionBench.IndependentClassicalReview.malformed_coefficient_digit',
    'InclusionBench.IndependentClassicalReview.malformed_typed_stack',
    'InclusionBench.IndependentClassicalReview.unused_stack_rejected',
    'InclusionBench.IndependentClassicalReview.leading_coefficient_zero_preserves_value',
    'InclusionBench.Quantum.Review.product_minor_vanishes',
    'InclusionBench.Quantum.Review.correlated_state_not_product',
    'InclusionBench.Quantum.Review.environment_sign_invisible',
    'InclusionBench.Quantum.Review.serialized_width_determined',
    'InclusionBench.Quantum.Review.stoq_threshold_integer_sanity',
):
    pattern = re.escape("'" + qualified + "'") + r" (?:depends on axioms:|does not depend on any axioms)"
    if not re.search(pattern, output):
        raise SystemExit("Missing required quantum axiom audit: " + qualified)
print("All catalog class mappings, quantum definitions and real-feasibility semantics checked without proof holes or custom axioms.")
PY
