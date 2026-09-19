#!/bin/sh
set -eu
cd "$(dirname "$0")"
export LEAN_NUM_THREADS=1
# Compile the dependency with its own serial, Mathlib-free build first.
sh ../lean/build.sh
export LEAN_PATH="../lean:.${LEAN_PATH:+:$LEAN_PATH}"
for module in Quantum Complete; do
  lake env lean -j1 -o "InclusionQuantum/$module.olean" "InclusionQuantum/$module.lean"
done
lake env lean -j1 -o InclusionQuantum.olean InclusionQuantum.lean
lake env lean -j1 AxiomAudit.lean
