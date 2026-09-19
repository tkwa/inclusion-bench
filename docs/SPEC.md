# AI benchmark scoring specification

## Target universe

The evaluated system is one fixed AI model and configuration in one budgeted run. See [the evaluation protocol](EVALUATION.md) for prompts, adapters, evidence and run admission. An instance is an ordered pair from the frozen class catalog. The current 50-class roster has 2,500 pairs, including 50 reflexive pairs that are known and ineligible. A language is a subset of finite binary strings; a class is a set of languages. Inclusion means ordinary set inclusion, not a reduction.

The cutoff is September 1, 2026, inclusive: a result publicly available before September 2, 2026 at 00:00 UTC is pre-cutoff. Original versions, acceptance claims, corrections and publication dates require evidence. A later exposition can explain an older theorem but cannot establish its historical availability by itself. Month-only dates near the cutoff require explicit review.

A certified release freezes the catalog, the cited rule set and per-pair eligibility. A SHA-256 digest binds the class definitions, knowledge base and policy; the manifest and admission records name that digest. Changes produce a new version and a documented rescore. Historical omissions are corrected, never treated as achievements.

## Resolutions and scoring

A normal atom is `inclusion(A,B)` or `separation(A,B)`. The latter is ¬(A ⊆ B), equivalent in classical logic to a witness language in A outside B. Incomparability is two separation atoms. Equality is two inclusion atoms. Strict containment A ⊊ B is inclusion(A,B) together with separation(B,A).

For an accepted submission S and certified eligibility set E:

```
score(S) = | { (A,B) in E : an accepted resolution of (A,B)
                          follows from the baseline and S } |
```

Each ordered pair contributes at most one point, regardless of the number of proofs or the direction of the answer. A run score uses the union of the pairs resolved by its accepted proof artifacts. Answers to different tasks in the same run may combine through implications. Different runs are never pooled. Exact run, attempt and artifact hashes bind every admitted proof to its originating run. The standalone `score` command assumes mathematical claims for diagnosis; `evaluate-run` requires trusted proof reviews before counting them.

A contradiction with the baseline, with another submitted claim, or between derived resolutions rejects the submission. Logical explosion earns no points. Existing facts and consequences earn zero. A stronger result earns at least as many points when it entails all the weaker submission's accepted consequences under the same dataset; the engine need not discover every implication in mathematics.

## Supported inference

The scorer maintains a finite, signed relation graph and an acyclic explanation record. It repeatedly applies:

1. Reflexivity and inclusion transitivity.
2. Separation propagation: A ⊄ B, A ⊆ C and D ⊆ B imply C ⊄ D.
3. Complement transport when the catalog supplies both complement identities. Direction is preserved: A ⊆ B implies coA ⊆ coB.
4. Cited Horn implications with any finite list of signed premises.
5. Classical contraposition of each Horn implication: its other premises and the negation of its conclusion imply the negation of the missing premise.

The rule set includes hierarchy collapses, Karp–Lipton, consequences of Toda's theorem, circuit/advice collapses, padding and intersection introduction. A rule is a mathematical assertion with a source, not executable code. Every generated conclusion records its premises and rule/source IDs. The first found derivation is deterministic for a fixed input order; it need not be the shortest proof.

The graph is deliberately incomplete. For example, the known containment PH ⊆ P^PP cannot be replaced by PH ⊆ PP. Exponential circuit hardness needed for Impagliazzo–Wigderson cannot be replaced by the weaker claim E ⊄ P/poly. Quantitative, disjunctive and auxiliary propositions will need an extended rule language or separately proved consequences. A submitter can supply additional proved pair conclusions for review.

## Independence from ZFC

Independence is a metatheorem about **provability**, not an additional truth value for a language-class relation. The intended certificate establishes both:

- there is no ZFC derivation of the encoded inclusion sentence;
- there is no ZFC derivation of its negation.

It must state its metatheory, the exact arithmetical/set-theoretic encodings, and any consistency assumptions. A theorem conditional on Con(ZFC) must be displayed as conditional and reviewed under an explicit acceptance policy. Lean's type theory is not automatically ZFC.

The Lean library currently expresses independence relative to an explicit abstract proof relation. It does not implement ZFC syntax or its proof system. The Python scenario tool stores an independence claim at its exact pair and never uses it as an inclusion, a separation, or a Horn-rule premise. Even propagation across equivalences is withheld until a corresponding metatheorem is implemented. An independence resolution conflicts with an ordinary accepted resolution at that same pair under the benchmark's single-resolution policy.

## Admission and the draft boundary

The present dataset has no certified-open pairs. `unreviewed` means “not resolved by this dataset's conservative closure,” which is weaker than “open in the literature.” Scenario mode calculates impact on that provisional complement and labels the result hypothetical. Official mode refuses all submissions while the release stage is draft.

A future certified mode additionally requires a complete eligibility manifest for the exact dataset and a repository-maintained acceptance record matching the exact submission digest. The code checks neither author identity nor proof correctness merely from JSON. Those must come from the proof/review pipeline. Setting local metadata to `certified` is not a way to obtain a valid public score.

The model leaderboard currently has no evaluated runs. A separate historical reference displays zero points. Partial suites, smoke fixtures, unverified candidates and draft runs cannot become ranked model entries. A zero reference follows from the scoring definition; it is not a literature search conclusion about every result published after the cutoff.
