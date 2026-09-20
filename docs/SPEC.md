# AI benchmark scoring specification

**Version 0.4.0 is provisional and prepared for review.** Model runs may start against the frozen suite. Existing cited theorems are explicit trusted baseline inputs; re-formalizing their proofs is not a launch requirement. New ordinary claims require isolated Lean verification, and points require a recorded historical decision for each resolved pair. The release-wide audit supplies those decisions for the current suite.

## Target universe and freeze

The evaluated system is one fixed AI model and configuration in one budgeted run. See [the evaluation protocol](EVALUATION.md) for prompts, adapters, evidence and admission. An instance asks whether one class is included in another. Languages are subsets of finite binary strings, classes are sets of languages, and inclusion means ordinary set inclusion.

The scored roster has 50 classes and 2,500 ordered pairs, including 50 reflexive pairs. Its baseline settles 845 inclusions and 331 noninclusions, leaving **1,324 candidate questions**. The full inference catalog has 61 concretely defined classes: eleven background endpoints remain available in proofs but do not supply scored pairs. Historical decisions are revisable; they do not prove the absence of an overlooked paper. AC0, ACC0, TC0, NC1, P/poly and NP/poly are nonuniform; NC is logspace-uniform, and the separate UniformNC1 endpoint uses standard extended-connection uniformity (ALOGTIME).

The cutoff is September 1, 2026, inclusive: a result publicly available before September 2, 2026 at 00:00 UTC is pre-cutoff. Historical review checks original versions, corrections, the exact statement and publication evidence. A later exposition can explain an older result but does not alone establish its earlier availability.

`freeze` records the dataset, taskset, formalization bundle and baseline-audit hashes. The dataset digest binds the class catalog, cited knowledge base and policy. Freezing fixes candidate questions; it does not certify that every candidate was open. The [AI-assisted baseline audit](../research/baseline-audit.md) records its coverage and limitations. Changes require a versioned freeze and a documented treatment of affected runs.

## Resolutions and scoring

An ordinary atom is `inclusion(A,B)` or `separation(A,B)`. Separation means ¬(A ⊆ B), equivalent in classical logic to a witness language in A outside B. Incomparability requires two separation atoms; equality requires two inclusion atoms. Strict containment A ⊊ B requires inclusion(A,B) and separation(B,A).

For one run, let S be its accepted model claims, R the candidate pairs resolved by the baseline and S, and H the pairs reviewed as open at the cutoff:

```
score(run) = | R ∩ H |
```

An official score is published only after the run-admission requirements below are satisfied. Every pair in R must have a historical decision, including one supplied by the release-wide audit; a pair reviewed as already known earns zero. Each ordered pair contributes at most one point, regardless of how many proofs resolve it. Accepted answers to different tasks in the same run may combine through implications. Different runs are never pooled.

Implication credit ranges over the frozen candidate universe, including consequences outside a run's assigned subset. The universe contains only pairs from `scored_class_ids`. Accepted supporting claims may use any context endpoint. Demoting a class preserves its proof paths but removes direct credit, including direct independence credit, for pairs containing it. Different roster versions define different cohorts and denominators. Exact run, attempt and artifact hashes bind accepted proofs to their originating run. The standalone `score` command assumes mathematical claims for diagnosis and reports hypothetical consequences. Operational official scores use `evaluate-run`; `score --official` is not the operational admission route.

A contradiction with the baseline, another accepted claim, or a derived resolution rejects that inconsistent claim set. Logical explosion earns no points. A stronger accepted result earns at least as many points when it entails all the weaker result's accepted consequences under the same baseline and historical eligibility decisions. The engine need not discover every implication in mathematics.

## Supported inference

The scorer maintains a finite signed relation graph and an acyclic explanation record. It repeatedly applies:

1. Reflexivity and inclusion transitivity.
2. Separation propagation: A ⊄ B, A ⊆ C and D ⊆ B imply C ⊄ D.
3. Complement transport when the catalog supplies both identities. Direction is preserved: A ⊆ B implies coA ⊆ coB.
4. Cited Horn implications with finite lists of signed premises.
5. Classical contraposition: the other premises and the negation of a rule's conclusion imply the negation of its missing premise.

The rule set includes hierarchy collapses, Karp–Lipton, consequences of Toda's theorem, circuit/advice collapses, padding and intersection introduction. Each conclusion records its premises and rule/source IDs. The first derivation found is deterministic for a fixed input order; it need not be the shortest proof.

The graph is incomplete. PH ⊆ P^PP cannot be replaced by PH ⊆ PP. Exponential circuit hardness needed for Impagliazzo–Wigderson cannot be replaced by E ⊄ P/poly. Quantitative, disjunctive and auxiliary propositions need a richer rule language or separately proved pair consequences. A model may submit those additional consequences for verification.

## Admission and review

Operational admission has three separate records:

| Review | What it establishes |
| --- | --- |
| Run review | Exact model identity, configuration and tools, budgets and usage, sealed transcripts/artifacts, and absence of unreported human assistance. |
| Proof review | Which submitted claims are accepted or rejected, bound to the exact run, attempt and artifact hashes. Ordinary accepted claims require a verified isolated Lean report. |
| Historical review | Whether each resolved candidate pair was open or already known at the cutoff, with evidence and rationale. |

The ordinary proof verifier generates a trusted helper containing only cited baseline facts, rules and complement identities. It elaborates the model's Lean source in an isolated container, exports declaration data, and rechecks those declarations in a fresh Lean kernel environment against exact class propositions. Only standard Lean foundations and the named trusted-baseline axioms are allowed. Submitted assumptions, fabricated verification metadata and conditional proofs with new unproved premises are not accepted proofs. See [formalization status](formalization.md) for the precise trust boundary and supported proof format.

Review registries are maintainer-controlled inputs, not model answers. A review packet is a template, not an acceptance decision. The commands `review-run`, `review-proof` and `review-history` record explicit decisions; `verify-proof` supplies proof-checking evidence without awarding points by itself.

An operational official run must use the current frozen version and sealed schema-v2 evidence, have an accepted run review, and have every proof candidate adjudicated. All candidate consequences of accepted proofs need historical decisions; existing release-wide decisions are reused. At least one genuine model request must produce a completed `unsolved` or `proof_candidate` answer, and the recorded charge must fit the token budget. Infrastructure fixtures, smoke tests, empty runs and runs consisting only of errors or exhausted budgets cannot become ranked model results.

**A measured zero is valid.** If a real run meets those requirements and resolves no eligible pairs, it receives zero. Unclaimed candidates need no blanket openness certification for that result. A pending proof candidate prevents a final score until adjudicated, even if the eventual score is zero.

Declared subsets are allowed and labeled. Rankings compare only identical frozen tasksets, exact task assignments, access tracks, resource budgets and access policies. Full-suite and subset results are different cohorts; equal scores within a cohort share a rank.

## Historical corrections

A missed pre-cutoff theorem or consequence earns zero. Record the supporting evidence, correct historical eligibility, and recompute affected scores while retaining the original run and frozen evidence. Changes to the baseline graph or semantics require a new dataset version; a review decision about a frozen candidate can be recorded in the historical registry for that version. Do not silently reclassify a known result as an achievement.

The historical baseline's zero is a scoring convention, not a measured AI result or a claim that no post-cutoff advance exists. The leaderboard publishes only actual reviewed runs. Hypothetical examples and smoke fixtures remain separately labeled.

## Independence from ZFC

Independence is a metatheorem about provability. For the exact encoded inclusion sentence, it must establish both that ZFC has no derivation of the sentence and that ZFC has no derivation of its negation. The accepted premise is one of:

| Review value | Required metatheorem |
| --- | --- |
| `unconditional` | Both nonderivability statements in the declared metatheory, without a consistency or soundness premise |
| `zfc_consistency` | Con(ZFC) implies both nonderivability statements |
| `zfc_arithmetic_soundness` | Arithmetic soundness of ZFC implies both nonderivability statements |

Arithmetic soundness means that **every first-order arithmetic sentence whose translation into ZFC is provable is true in the standard natural numbers**. The translation and standard interpretation must be specified. For the standard ZFC proof system, this premise implies consistency. It is a stronger assumption than Con(ZFC), so accepting it permits a weaker conditional independence theorem. The benchmark does not assert either premise as a proved fact.

These are external premises of the metatheorem. The theory whose derivations are excluded remains exactly ZFC, not ZFC augmented by consistency or soundness. Expert review must reject stronger unapproved assumptions hidden in the declared metatheory. A qualifying independence result already public before the cutoff, including one conditional on arithmetic soundness, earns zero.

The expert review records the selected premise, ZFC proof system, metatheory, assumptions and proof evidence. Each verified independence pair needs its own encoded sentence and evidence for both polarities; a single unspecified sentence cannot stand for several pairs. The premise and any other stated conditions remain attached to the accepted result in evaluation provenance and public reporting. See [the review format](PROOF_REVIEW.md#independence-review).

The repository supplies a proof-relation interface, arithmetic syntax and standard-natural-number semantics, and conditional independence certificates. Identifying the supplied theory with the intended ZFC proof system, validating its translations and proving the submitted metatheorem remain an expert-reviewed boundary. The ordinary proof checker does not implement a complete ZFC verification route. This separate lane does not block ordinary inclusion or noninclusion runs.

Independence resolves only its exact pair and never acts as an inclusion, separation or Horn-rule premise. Propagation across equivalences is withheld until a corresponding metatheorem is supplied. Under the benchmark's single-resolution policy, independence conflicts with an ordinary accepted resolution at the same pair.
