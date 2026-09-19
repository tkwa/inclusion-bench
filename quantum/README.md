# Quantum definitions

This optional Lean project completes the benchmark's operational definitions
for BQP, QCMA, QMA, and coQMA. It imports the 46 definitions in `../lean` and
uses Mathlib for exact real and complex arithmetic. The core library remains
independent of Mathlib.

The full interpretation is `InclusionBench.Quantum.completeInterpretation`.
The theorem `complete_agrees_with_core` proves agreement with every supplied
core definition; `all_fifty_defined` checks coverage of the entire roster.
Import `InclusionQuantum` to use both.

## Model

A state is a complex amplitude for each finite computational basis string.
Normalization is a finite sum of squared complex magnitudes equal to one.
The available gates are H, T, X, and CNOT. CNOT requires distinct control and
target wires. The T phase is exactly `(1 + i) / sqrt(2)`.

A concrete finite-control transducer, running in polynomial time, outputs
each complete circuit on unary input length. The serialization contains the
width, measured output wire, gate count, and fixed-width records holding every
gate tag and wire index. Witness and ancilla lengths are explicit polynomials.

Input bits occupy a computational basis register. Witnesses occupy a separate
register, and ancillary bits start at zero. QCMA quantifies over classical
basis witnesses; QMA quantifies over normalized complex witness states. BQP
has an empty witness register. Acceptance is the finite sum of squared
amplitudes whose output bit is one. Each class imposes the usual total-language
completeness and soundness gaps of 2/3 and 1/3 on every input.

## Build

Install Lean `leanprover/lean4:v4.19.0`. Mathlib is pinned to `v4.19.0`, commit
`c44e0c8ee63ca166450922a373c7409c5d26b00b`; `lake-manifest.json` locks its
dependencies.

Run from this directory:

```sh
sh setup.sh
sh build.sh
```

The compiler checks modules serially with one Lean worker. Cache downloads
request only four modules and their transitive dependencies, rather than all
of Mathlib. The cache decompressor may create workers independently of Lean.
On Linux, restrict the entire setup and build to one available CPU when
resource limits matter:

```sh
taskset -c 0 sh setup.sh
taskset -c 0 sh build.sh
```

The project was checked on the authorized Ubuntu host with this one-CPU
configuration. No Mathlib dependency download or compilation ran locally.

## What the proofs establish

The checked theorems include coverage of all 50 classes, compatibility with
the core interpretation, normalized computational basis states, injectivity
of gate records, and the fact that applying X twice restores the state.
The audit file prints their Lean axiom dependencies.

General gate unitarity, normalization preservation, amplification, textbook
model equivalence, and the literature's inclusion and separation theorems
remain unproved here. Having all definitions available does not certify the
historical baseline or prove any open complexity-class relation.
