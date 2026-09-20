# Quantum and real-number definitions

This Mathlib project completes the provisional v 0.4.0 interpretation: eight
quantum classes and ∃R supplement the 52 definitions in `../lean`. The full
catalog has 61 concrete definitions, of which 50 supply scored endpoints. The
core remains independent of Mathlib.

Import `InclusionQuantum` for
`InclusionBench.Quantum.completeInterpretation`.
`complete_agrees_with_core` proves agreement with every core definition;
`all_catalog_classes_defined` checks complete context coverage. Background
classes remain valid proof targets without earning points for their own pairs.

## Models

`Quantum.lean` and `Normalization.lean` define BQP, QCMA, QMA and coQMA.
States are complex amplitudes on finite computational basis strings. H, T,
X and CNOT have explicit actions; the T phase is `(1 + i) / sqrt(2)`.
Finite-control polynomial-time transducers generate complete circuits on unary
input length. Input, witness and zero-ancilla registers have explicit bounds.
Acceptance is a finite sum of squared amplitudes, with a gap on every input.

The new modules supply these targets:

| Module | Target and convention |
| --- | --- |
| `Unentangled.lean` | QMA(2), with an explicit tensor product of two separately normalized witnesses |
| `Logspace.lean` | BQL, with a logspace polynomial-time generator reading the actual input, logarithmic quantum workspace and a polynomial gate bound |
| `Stoquastic.lean` | StoqMA, with reversible classical gates, zero/plus ancillas, X measurement and the standard union over efficiently computed inverse-polynomial-gap thresholds |
| `Statistical.lean` | QSZK through Quantum State Distinguishability on retained outputs, after discarding environment registers |
| `RealFeasibility.lean` | ∃R over finitely encoded integer-coefficient formulas and finite real assignments, closed under concrete polynomial-time many-one reductions |

QSZK's distance uses the finite-dimensional variational characterization of
trace distance. Its optimizing measurement defines a mathematical quantity;
it is not a free efficient subroutine. StoqMA does not normalize its thresholds
to the exact soundness-1/2 slice, which would describe NP instead. BQL does not
permit polynomial-time classical preprocessing with unrestricted workspace.

The [design and literature dossiers](../research/v 0.4.0/quantum-new-baseline.md)
and [formalization notes](../docs/formalization.md) document these choices and
the trusted textbook-equivalence bridges. All endpoints are total binary
languages; promise-only conclusions require a separate valid transfer.

## Build

Both projects pin Lean 4.19.0. Mathlib is pinned to commit
`c44e0c8ee63ca166450922a373c7409c5d26b00b`, with its dependencies locked in
`lake-manifest.json`. From this directory:

```sh
sh setup.sh
sh build.sh
```

Compilation is serial with one Lean worker. Setup requests four Mathlib
modules and their transitive dependencies; the cache decompressor may create
its own workers. On Linux, `bash ../scripts/check_quantum.sh` constrains the
whole setup and build to one available CPU and 8GiB of address space. It checks
the core, the complete interpretation and the required axiom-audit output.
Mathlib setup and compilation for this revision ran on the authorized Ubuntu
host, not the local Mac.

## What is proved

The library checks normalization, gate and circuit norm preservation,
acceptance bounds, product-witness normalization, state preparation and
measurement bounds, serialization injectivity, and the full interpretation's
coverage and agreement. Real-feasibility checks include an executable encoding
round trip, malformed-input rejection, and satisfiable and unsatisfiable
real equations.

`SemanticChecks.lean` preserves independent adversarial checks, including a
Bell-pattern state that cannot be a product witness and invariance of retained
output measurements under phase changes confined to the discarded environment.
The complementary core semantic checks cover clocks, branch weights, work
space, index tapes, counting multiplicities and formula decoding.

The audits permit only standard Lean foundations: `propext`,
`Classical.choice` and `Quot.sound`. They do not prove every textbook-model
equivalence, reconstruct the cited literature, establish historical openness,
or solve any open class inclusion. Existing results remain explicit trusted
inputs; new model claims use the separate isolated proof checker.
