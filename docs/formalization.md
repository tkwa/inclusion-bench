# Formalization status

**All 50 class definitions compile in Lean, and the reasoning kernel is checked. The benchmark is not yet formally certified.** The Mathlib-free core supplies 46 operational definitions; the optional quantum project supplies the other four and a complete interpretation. Textbook-model equivalences, general quantum gate unitarity, most cited complexity theorems, historical eligibility certification, and a formal ZFC implementation remain unfinished. Definitions and conditional inference proofs do not establish a submitted research result.

## What has been proved

The library defines a language as `List Bool → Prop` and a complexity class as a predicate on languages. It proves:

- Inclusion reflexivity and transitivity; separation propagation in both directions; complement transport; intersection introduction and elimination; and strict inclusion implying distinct classes.
- Soundness of Horn derivations, including contraposition, under explicit hypotheses for the baseline, submissions, and cited rules.
- Soundness of an executable, JSON-serializable certificate checker. Each step must name an existing baseline fact, an existing submitted fact, or a registered rule whose premises were already checked. Missing leaves and premature rule applications are rejected.
- A score bound by the number of distinct eligible ordered pairs and monotonicity when additional pairs become resolved. A general numerical theorem proves that duplicating an eligible pair leaves its score unchanged. The full 50 × 50 matrix has a proved upper bound of 2,500 points; historical eligibility makes the actual bound smaller. The two orientations of a pair remain distinct. Multiple evidence types share one resolution bit.
- A separate independence interface requiring that neither a sentence nor its negation has a proof in an explicitly supplied theory. Independence never enters the ordinary inclusion closure.

`lean/Examples.lean` checks accepted and rejected certificates and verifies that duplicate eligibility entries cannot create extra points. `lean/AxiomAudit.lean` prints the kernel dependencies of the principal theorems. The audit contains only standard Lean foundations (`propext`, `Classical.choice`, and `Quot.sound`) where needed; there are no project-specific axioms or incomplete proofs.

## Concrete definitions: all 50

`Machines.lean` defines finite-control deterministic and nondeterministic machines with a read-only input tape, endmarkers, a two-way work tape, finite transition tables, and explicit time and work-space bounds. Initialization cannot inspect an arbitrary language, and no oracle is hidden in the model.

`Circuits.lean` defines acyclic Boolean gate programs. An index can refer only to an earlier gate. Evaluation, size, output depth, allowed gate bases, and nonuniform families are explicit. The size measure counts gates and wires; bit-level serialization conventions remain an equivalence obligation. The ACC⁰ definition fixes one modulus across the family; the threshold basis uses majority gates.

`Randomized.lean` uses finite fair-coin transitions and proves that a budget of *t* steps has exactly 2^t equally likely random strings. Halting states remain fixed under padding. Probabilities use these random strings, rather than a fraction of variable-length nondeterministic branches. ZPP uses polynomial-time Las Vegas trials with no wrong answers and success probability at least one half; equivalence with the expected-time convention remains unproved.

`Counting.lean` counts accepting computation paths with transition multiplicities preserved, even when two branches reach the same configuration. It defines #P and GapP over the concrete machines and uses those functions to define the counting classes. AWPP quantifies over inverse-exponential polynomial error bounds with explicit finite polynomial descriptions.

`ProofSystems.lean` supplies finite deterministic verifiers, a proved injective input/randomness/witness encoding, and explicit finite polynomial witness and random lengths. MA fixes a witness before randomness; AM counts random strings after which some witness succeeds. Only NP/poly permits arbitrary advice by input length.

`Oracles.lean` supplies finite deterministic and nondeterministic oracle machines with a separate writable query tape. A query instruction asks membership of the explicitly written word in one fixed language from the specified oracle class. Θ₂P also bounds the number of queries. The polynomial hierarchy is the union of explicitly defined levels.

`Transducers.lean` supplies polynomial-time integer-output machines with a write-only output tape. WPP uses a nonzero computed integer normalizer on the input; LWPP gives the normalizer only the input length. `UniformCircuits.lean` requires a logspace transducer to emit the complete circuit description, using explicit tagged records and a proved injective natural-field encoding. `LogCFL.lean` supplies finite context-free grammars, derivations, and actual logspace transducers for the reduction.

`Statistical.lean` uses two concrete polynomial-time samplers and exact finite statistical distance. Repeated outputs retain their probability mass; only the support is deduplicated. Its SZK definition uses the Statistical Difference characterization on total languages. Equivalence to interactive statistical zero knowledge remains unproved.

The optional `quantum/` project adds BQP, QCMA, QMA, and coQMA using Mathlib's exact real and complex arithmetic. States are complex amplitudes on finite computational basis strings. H, T, X, and CNOT have explicit actions; T uses the exact phase `(1 + i) / sqrt(2)`. Concrete polynomial-time output transducers generate complete circuit descriptions on unary input length. Witness and ancilla lengths are explicit polynomials. QCMA uses classical basis witnesses; QMA quantifies over normalized complex witness states. Acceptance is a finite sum of squared amplitudes, with the total-language 2/3 and 1/3 completeness/soundness gaps.

| Catalog entries | Definition supplied |
| --- | --- |
| L, P, PSPACE, E, EXP, EXPSPACE | Deterministic tape-machine resource classes |
| NL, NP, NE, NEXP | Nondeterministic tape-machine space and time classes |
| SC | One machine satisfying both polynomial time and polylogarithmic work space |
| coNP, NP ∩ coNP | Complement and intersection of the supplied NP definition |
| AC⁰, ACC⁰, TC⁰, NC¹, P/poly | Nonuniform circuit families with the stated size, depth, and gate restrictions |
| NC | Polynomial-size, polylogarithmic-depth bounded-fan-in circuits generated in logspace |
| LogCFL | Logspace transducer reductions to languages generated by finite context-free grammars |
| RP, coRP, BPP, ZPP, SBP | Fair-coin machines with one-sided, two-sided, Las Vegas, or inverse-exponential threshold conditions |
| UP, coUP, FewP, SPP, C_=P, PP, ⊕P, AWPP | Explicit #P and GapP path-count conditions |
| WPP, LWPP | GapP functions with nonzero normalizers computed by actual integer transducers |
| MA, coMA, AM, coAM, NP/poly | Concrete verifiers, finite witness/randomness bounds, and length advice where specified |
| Σ₂P, Π₂P, Δ₂P, Θ₂P, PH | Concrete oracle machines and the polynomial hierarchy |
| SZK | Concrete uniform samplers with the Statistical Difference gap on every input |
| BQP, QCMA, QMA, coQMA | Uniform finite quantum circuits and explicit classical or complex witness registers; optional Mathlib project |

The core's `Definitions.lean` exposes `operationalDefinition : ClassId → Option ComplexityClass` and proves that it supplies 46 entries. Its four quantum entries remain `none` so the core does not acquire a Mathlib dependency.

Import `InclusionQuantum` to obtain `InclusionBench.Quantum.completeInterpretation : Interpretation ClassId`. It explicitly assigns a concrete definition to every catalog constructor, without a default replacement class. `complete_agrees_with_core` proves agreement with all 46 core entries; `every_class_defined` and `all_fifty_defined` establish complete coverage. These are checked theorems about the supplied definitions, not proofs of textbook equivalence or of the historical class lattice.

These definitions fix concrete conventions; they do not prove equivalence with every textbook machine or encoding convention. Several elementary containments are proved directly: deterministic resource-bound monotonicity, SC ⊆ P, E ⊆ EXP, NE ⊆ NEXP, NC¹ ⊆ P/poly, AC⁰ ⊆ ACC⁰, UP ⊆ FewP, SPP ⊆ PP, SPP ⊆ AWPP, RP ⊆ SBP, Θ₂P ⊆ Δ₂P, and Σ₂P ⊆ PH for the supplied definitions. Deep literature results have not been recreated in Lean.

The quantum project also proves normalization of computational basis states, injectivity of gate records, and that applying X twice restores the state. General gate unitarity, preservation of normalization by arbitrary circuits, amplification, and equivalence with conventional quantum models remain unproved. In particular, the presence of an `acceptanceProbability` definition does not mean the library has proved all probability invariants for it.

## What the Python-to-Lean bridge certifies

The Python exporter turns a selected closure trace into a Lean theorem with visible hypotheses. Structural steps call proved Lean lemmas; submitted statements, cited baseline facts, cited conditional rules, and complement identities are explicit assumptions. The generated file includes the dataset digest and an axiom audit.

A successful Lean check establishes that the selected consequence follows from those assumptions. It does **not** establish that a submitted theorem is true, that a citation proves its encoded statement, that the full Python implementation is verified, or that the pair was open on September 1, 2026. Every cited leaf and every cited rule still needs its own semantic proof. The current bridge takes an explicit `Interpretation ClassId`. The complete quantum interpretation can supply that argument, but doing so does not discharge the theorem's baseline or submission hypotheses.

## Independence and ZFC

`Independent theory sentence` means both `¬ theory.proves sentence` and `¬ theory.proves (theory.negation sentence)`. It is a statement about a proof relation, not the inconsistent conjunction `¬p ∧ ¬¬p`.

The repository does not yet encode ZFC syntax, axioms, or derivations, nor the translation of class inclusions into that syntax. Supplying an arbitrary proof relation does not make a certificate a ZFC result. A future admissible independence entry needs the exact formal sentence, its connection to the benchmark pair, and proofs of unprovability in the specified metatheory. It resolves only that exact ordered pair; no independence propagation rule is supplied.

## Reproduce the checks

Both projects pin [Lean 4.19.0](https://github.com/leanprover/lean4/releases/tag/v4.19.0). The core needs only Lean's bundled libraries. From the repository root:

```sh
sh lean/build.sh
```

If the compiler is not on the search path:

```sh
LEAN_BIN=/absolute/path/to/lean sh lean/build.sh
```

The core script compiles modules sequentially with one Lean worker, runs the examples, and prints the axiom audit. It does not download or build Mathlib.

For all 50 definitions, install the optional dependencies and run the quantum checks:

```sh
cd quantum
sh setup.sh
sh build.sh
```

The quantum project pins Mathlib v4.19.0 at commit `c44e0c8ee63ca166450922a373c7409c5d26b00b` and locks its dependencies. Its build also checks the core serially. See [the quantum README](../quantum/README.md) for cache setup and a Linux CPU-affinity command that constrains setup as well as compilation. Generated `.olean` files and downloaded dependency caches are build products and must not be committed.

The core was checked with the official macOS arm64 Lean 4.19.0 release. The complete core-plus-quantum build and `quantum/AxiomAudit.lean` were checked on the authorized Ubuntu host with one CPU. Both builds succeeded; their audited theorems use only standard Lean foundations, with no custom axioms or incomplete proofs. Mathlib setup and quantum compilation did not run on the local Mac. See [Lean's account of kernel validation](https://lean-lang.org/doc/reference/latest/) for the distinction between checking a proof term and just executing a program.
