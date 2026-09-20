# Formalization status

**Version 0.3.1 is operational: all 50 canonical class definitions compile, the inference kernel is checked, and new ordinary proofs have an isolated Lean verification route.** The Mathlib-free core supplies 46 definitions; the quantum project supplies four more and the complete interpretation. Existing cited theorems and model conventions are explicit trusted baseline inputs. Their proofs do not need to be recreated in Lean before running the benchmark.

Textbook-model equivalences, quantum amplification and an automatic formal ZFC implementation remain future work. These limitations are documented rather than used as a launch gate for ordinary runs. A model still has to prove its exact new claim against the frozen class interpretation; merely compiling definitions or a conditional consequence does not establish a breakthrough. Historical review separately determines whether each resolved pair earns a point.

## What has been proved

The library defines a language as `List Bool → Prop` and a complexity class as a predicate on languages. It proves:

- Inclusion reflexivity and transitivity; separation propagation in both directions; complement transport; intersection introduction and elimination; and strict inclusion implying distinct classes.
- Soundness of Horn derivations, including contraposition, under explicit hypotheses for the baseline, submissions, and cited rules.
- Soundness of an executable, JSON-serializable certificate checker. Each step must name an existing baseline fact, an existing submitted fact, or a registered rule whose premises were already checked. Missing leaves and premature rule applications are rejected.
- A score bound by the number of distinct eligible ordered pairs and monotonicity when additional pairs become resolved. A general numerical theorem proves that duplicating an eligible pair leaves its score unchanged. The full 50 × 50 matrix has a proved upper bound of 2,500 points; historical eligibility makes the actual bound smaller. The two orientations of a pair remain distinct. Multiple evidence types share one resolution bit.
- A separate independence interface requiring that neither a sentence nor its negation has a proof in an explicitly supplied theory, with conditional certificates for the admitted metatheoretic premises. Independence never enters the ordinary inclusion closure.

`lean/Examples.lean` checks accepted and rejected certificates and verifies that duplicate eligibility entries cannot create extra points. `lean/AxiomAudit.lean` prints the kernel dependencies of the principal theorems. The permanent core and quantum library audits contain only standard Lean foundations (`propext`, `Classical.choice`, and `Quot.sound`) where needed, with no project-specific axioms or incomplete proofs. The submission verifier separately generates explicit axioms for the cited historical baseline, as described below. Those intentional trusted inputs are not disguised as proved library theorems.

## Concrete definitions: all 50

`Machines.lean` defines finite-control deterministic and nondeterministic machines with a read-only input tape, endmarkers, a two-way work tape, finite transition tables, and explicit time and work-space bounds. Initialization cannot inspect an arbitrary language, and no oracle is hidden in the model.

`Circuits.lean` defines acyclic Boolean gate programs. An index can refer only to an earlier gate. Evaluation, size, output depth, allowed gate bases, and nonuniform families are explicit. The size measure counts gates and wires; bit-level serialization conventions remain an equivalence obligation. The ACC⁰ definition fixes one modulus across the family; the threshold basis uses majority gates.

`Randomized.lean` uses finite fair-coin transitions and proves that a budget of *t* steps has exactly 2^t equally likely random strings. Halting states remain fixed under padding. Probabilities use these random strings, rather than a fraction of variable-length nondeterministic branches. ZPP uses polynomial-time Las Vegas trials with no wrong answers and success probability at least one half; equivalence with the expected-time convention remains unproved.

`Counting.lean` counts accepting computation paths with transition multiplicities preserved, even when two branches reach the same configuration. It defines #P and GapP over the concrete machines and uses those functions to define the counting classes. AWPP quantifies over inverse-exponential polynomial error bounds with explicit finite polynomial descriptions.

`ProofSystems.lean` supplies finite deterministic verifiers, a proved injective input/randomness/witness encoding, and explicit finite polynomial witness and random lengths. MA fixes a witness before randomness; AM counts random strings after which some witness succeeds. Only NP/poly permits arbitrary advice by input length.

`Oracles.lean` supplies finite deterministic and nondeterministic oracle machines with a separate writable query tape. A query instruction asks membership of the explicitly written word in one fixed language from the specified oracle class. Θ₂P also bounds the number of queries. The polynomial hierarchy is the union of explicitly defined levels.

`Transducers.lean` supplies polynomial-time integer-output machines with a write-only output tape. WPP uses a nonzero computed integer normalizer on the input; LWPP gives the normalizer only the input length. `UniformCircuits.lean` requires a logspace transducer to emit the complete circuit description, using explicit tagged records and a proved injective natural-field encoding. `LogCFL.lean` supplies finite context-free grammars, derivations, and actual logspace transducers for the reduction.

`Statistical.lean` uses two concrete polynomial-time samplers and exact finite statistical distance. Repeated outputs retain their probability mass; only the support is deduplicated. Its SZK definition uses the Statistical Difference characterization on total languages. Equivalence to interactive statistical zero knowledge remains unproved.

The `quantum/` project, optional for core-only development and required by the complete proof-verification target, adds BQP, QCMA, QMA, and coQMA using Mathlib's exact real and complex arithmetic. States are complex amplitudes on finite computational basis strings. H, T, X, and CNOT have explicit actions; T uses the exact phase `(1 + i) / sqrt(2)`. Concrete polynomial-time output transducers generate complete circuit descriptions on unary input length. Witness and ancilla lengths are explicit polynomials. QCMA uses classical basis witnesses; QMA quantifies over normalized complex witness states. Acceptance is a finite sum of squared amplitudes, with the total-language 2/3 and 1/3 completeness/soundness gaps.

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

The quantum project proves normalization of computational basis states, injectivity of gate records, and that applying X twice restores the state. `InclusionQuantum/Normalization.lean` proves that every H, T, X and CNOT gate preserves squared norm; any circuit and the input/witness/ancilla embedding preserve normalization; and acceptance lies between zero and one for normalized witnesses. It also checks the empty witness used by BQP. These theorems use the actual class definitions. Amplification and equivalence with conventional quantum models remain separate trusted mathematics.

## What the Python-to-Lean bridge certifies

The Python exporter turns a selected closure trace into a Lean theorem with visible hypotheses. Structural steps call proved Lean lemmas; submitted statements, cited baseline facts, cited conditional rules, and complement identities are explicit assumptions. The generated file includes the dataset digest and an axiom audit.

A successful Lean check establishes that the selected consequence follows from those assumptions. It does **not** establish that a submitted theorem is true, that a citation proves its encoded statement, that the full Python implementation is verified, or that the pair was open on September 1, 2026. Existing cited leaves and rules are trusted literature inputs under the operational policy; they do not need separate Lean proofs. The model's new claims still need verification. The current bridge takes an explicit `Interpretation ClassId`. The complete quantum interpretation can supply that argument, but doing so does not discharge the theorem's baseline or submission hypotheses.

## Checking a new model proof

`verify-proof` checks ordinary claims against `InclusionBench.Quantum.completeInterpretation`. The caller supplies a Lean source artifact and exact claim objects, each naming a closed theorem. The source is a body under fixed trusted imports. Expected propositions are generated from validated class identifiers, rather than parsed from model-provided notation.

The verifier generates `TrustedBaseline.lean` from the frozen cited facts, implications and complement identities. Each becomes a named axiom with source provenance. The allowlist contains exactly those names plus `propext`, `Classical.choice` and `Quot.sound`. This is the explicit trust boundary authorized for existing results; a model cannot contribute a new baseline assumption.

The Linux driver runs candidate elaboration in a container with one CPU, 8 GiB memory, no network, a read-only root, read-only trusted imports, and bounded temporary storage and output. It exports declaration data as JSON. A separate fresh process reconstructs and kernel-checks every exported declaration, checks the exact target theorem types, and audits all reconstructed declarations for forbidden axiom dependencies. Candidate `.olean` files and native libraries are never imported into this replay environment.

The current format accepts checked theorem, definition and opaque bodies. It rejects new axioms, unsafe/partial declarations, unresolved expressions and new inductive/constructor/recursor declarations. Supporting additional declaration forms is an extension of the proof format, not permission to bypass kernel checking. The trusted Lean compiler, dependency objects, checker code and maintainer review process remain part of the trust boundary.

A verified report binds the dataset, source bytes, claims, checker and semantic-source hashes, and records the trusted baseline assumptions and runtime. It establishes the submitted ordinary theorem relative to those explicit historical inputs. It does not establish model authorship, budget compliance, historical novelty or ZFC independence. `review-proof` binds that evidence to a sealed model artifact; run review and recorded per-pair historical decisions are still required before scoring. The release-wide audit supplies the latter for this suite.

All proof candidates in a run must be adjudicated. A genuine completed run may receive an official zero once its provenance and candidates are reviewed; the 1,378 frozen questions already have revisable historical decisions. See [the specification](SPEC.md) for subset cohorts and scoring gates.

## Independence and ZFC

`Independent theory sentence` means both `¬ theory.proves sentence` and `¬ theory.proves (theory.negation sentence)`. It is a statement about a proof relation, not the inconsistent conjunction `¬p ∧ ¬¬p`.

The admitted premise may be unconditional, Con(ZFC), or arithmetic soundness of ZFC. Arithmetic soundness means that every first-order arithmetic sentence with a provable ZFC translation is true in the standard natural numbers. For the standard proof system, soundness implies consistency; using that stronger premise yields a weaker conditional independence theorem. A certificate must retain the premise and establish both nonderivability polarities under it.

The premise is outside the target proof relation: nonderivability is from ZFC, not from ZFC plus consistency or soundness. The expert metatheory review must reject stronger unapproved assumptions concealed in the chosen ambient theory.

The interface in [`Independence.lean`](../lean/InclusionBench/Independence.lean) supplies the following objects, all under `InclusionBench`:

| Lean object | Meaning |
| --- | --- |
| `Arithmetic.Term n`, `Arithmetic.Formula n`, `Arithmetic.Sentence` | Typed first-order arithmetic syntax; a sentence has no free variables |
| `Arithmetic.TrueInN` | Recursive truth semantics with quantifiers over Lean's natural numbers |
| `ArithmeticTranslation theory` | An explicit translation into the supplied theory, with checked negation compatibility |
| `ArithmeticSound theory translation` | Every provable translated arithmetic sentence is true in standard N |
| `Consistent theory`, `ArithmeticExplosion theory translation` | Syntactic consistency and the explicit rule turning contradictory proofs into a proof of translated 0 = 1 |
| `ConditionalIndependenceCertificate theory premise` | An exact target sentence and both nonderivability obligations conditional on the premise |
| `IndependencePremise`, `AdmittedIndependenceCertificate` | The three admitted premise categories and certificates restricted to them |

`arithmeticSound_implies_consistent` requires `ArithmeticExplosion`; this logical property cannot be silently assumed for an arbitrary supplied proof relation. `admitSoundnessFromConsistency` transports a consistency-conditional certificate to a soundness-conditional one, retaining the exact target sentence. `ArithmeticSoundnessIndependenceCertificate` also names the soundness specialization of the general conditional interface. None of these definitions asserts that ZFC is consistent or sound.

The soundness premise concerns arithmetic sentences. The independence target may be any exact sentence of the supplied theory; the interface does not require a complexity-class inclusion itself to be arithmetical.

The repository does not yet encode the full ZFC syntax, axioms or derivations, or validate the translation of each complexity inclusion into that syntax. Supplying an arbitrary proof relation does not make a certificate a ZFC result. Expert review checks the exact sentence, its connection to the benchmark pair, the ZFC proof system, arithmetic translation where relevant, metatheory, assumptions and both nonderivability arguments. The ordinary Lean verifier does not automatically supply this review. Accepted conditions remain in provenance and public reporting. An independence result resolves only its exact ordered pair and supplies no premise to ordinary inclusion, separation or Horn-rule closure. This separate lane does not block ordinary proof runs.

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

For all 50 definitions and the interpretation used by the proof verifier, install the quantum dependencies and run its checks:

```sh
cd quantum
sh setup.sh
sh build.sh
```

The quantum project pins Mathlib v4.19.0 at commit `c44e0c8ee63ca166450922a373c7409c5d26b00b` and locks its dependencies. Its build also checks the core serially. See [the quantum README](../quantum/README.md) for cache setup and a Linux CPU-affinity command that constrains setup as well as compilation. Generated `.olean` files and downloaded dependency caches are build products and must not be committed.

The core was checked with the official macOS arm64 Lean 4.19.0 release. The complete core-plus-quantum build and `quantum/AxiomAudit.lean` were checked on the authorized Ubuntu host with one CPU. Both builds succeeded; their permanent library theorems use only standard Lean foundations, with no custom axioms or incomplete proofs. The generated proof-verification helper intentionally adds the separately audited historical baseline axioms. Mathlib setup and quantum compilation did not run on the local Mac. See [Lean's account of kernel validation](https://lean-lang.org/doc/reference/latest/) for the distinction between checking a proof term and just executing a program.
