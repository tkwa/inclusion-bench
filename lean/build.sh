#!/bin/sh
set -eu
cd "$(dirname "$0")"
LEAN_BIN="${LEAN_BIN:-lean}"
export LEAN_PATH="$(pwd)${LEAN_PATH:+:$LEAN_PATH}"
# One compiler worker; modules are checked sequentially. No mathlib build.
for module in Semantics Derivation Certificate Independence Scoring Catalog Machines Circuits Counting Randomized Oracles ProofSystems Transducers UniformCircuits LogCFL Statistical LogspaceClasses CountingHierarchy AlternatingLogtime RealSyntax ClassicalSemanticChecks Definitions; do
  "$LEAN_BIN" -j1 -o "InclusionBench/$module.olean" "InclusionBench/$module.lean"
done
"$LEAN_BIN" -j1 -o InclusionBench.olean InclusionBench.lean
"$LEAN_BIN" -j1 Examples.lean
"$LEAN_BIN" -j1 AxiomAudit.lean
