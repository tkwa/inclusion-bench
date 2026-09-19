#!/bin/sh
set -eu
cd "$(dirname "$0")"
export LEAN_NUM_THREADS=1
export MATHLIB_NO_CACHE_ON_UPDATE=1
lake update
# Only these modules and their transitive imports are requested. The cache
# command can decompress files concurrently; use taskset on a constrained host.
lake exe cache get Mathlib.Data.Complex.Basic Mathlib.Data.Real.Sqrt \
  Mathlib.Data.Fintype.Pi Mathlib.Algebra.BigOperators.Group.Finset.Basic
