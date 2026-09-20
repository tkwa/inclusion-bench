# Provisional v0.4.0 historical audit

The proposed 50-class roster has **845 known inclusions, 331 known noninclusions and 1,324 questions assessed as open at the cutoff**. The cutoff includes results publicly available before September 2, 2026, 00:00 UTC. The full proof vocabulary contains 61 classes; eleven background classes retain their definitions and implications but supply no scored pairs.

This is an AI-assisted, revisable literature assessment prepared for the v0.4.0 review branch. It is not human expert certification. Existing accepted theorems remain trusted inputs, as requested; their proofs were not all reconstructed in Lean. A missed accepted pre-cutoff result earns no point and requires a recorded correction.

## What changed

The [roster decision](v0.4.0/roster-decision.md) selects 50 endpoints from the current pool of 61. Eleven endpoints replace eleven from v0.3.1. The [migration report](v0.4.0/roster-migration.json) checks that all parent facts, rules, sources and complement identities remain intact and that **all 2,500 classifications among the old classes are unchanged**.

The new library has 163 cited facts and 302 conditional rules, adding 28 facts and 53 rules to the parent theory. The rules include new resource-padding and counting/proof-system consequences, standard intersection instances for the new classes, and two uniform-circuit hardwiring implications. A conditional rule does not assert its open premise.

| Scored pair block | Pairs | Known inclusion | Known noninclusion | Open candidates |
| --- | ---: | ---: | ---: | ---: |
| Both endpoints retained from v0.3.1 | 1,521 | 482 | 246 | 793 |
| At least one newly added endpoint | 979 | 363 | 85 | 531 |
| **Total** | **2,500** | **845** | **331** | **1,324** |

The earlier eight corrections involving NE/NEXP and Θ₂P, coNP, coRP and coUP remain in the context theory. Their original evidence and judgment are preserved in the [v0.3.1 assessment](audit-assessment-v0.3.1.json) and [archived audit](baseline-audit-v0.3.1.md). Historical snapshots should be read at their corresponding release tag; shared filenames such as `audit-final-sat.json` now describe this revision.

The arithmetic-soundness policy from v0.3.1 is unchanged. An independence certificate may be unconditional or conditional on Con(ZFC) or arithmetic soundness of ZFC. Its premise and both unprovability arguments must remain explicit. Independence supplies no ordinary inclusion or noninclusion premise and receives no automatic propagation.

## Evidence and verification

| Check | Scope and result |
| --- | --- |
| Literature review | The inherited three domain reviews and three new endpoint dossiers cover all 61 context classes; the current pair index links all 2,500 scored pairs to their dossiers |
| Independent source checks | Classical, counting and quantum statements were checked against exact models, oracle conventions, uniformity, promise restrictions and public versions |
| Operational definitions | All 61 classes have concrete Lean interpretations; the core supplies 52 and the pinned Mathlib extension supplies nine |
| Independent semantic checks | Twenty retained checks address branch weighting, ambiguity, tape space, random access, real encodings, product witnesses, discarded environments and threshold conventions |
| Complete propositional check | Both polarities of all 1,324 scored candidates and all 2,049 full-context candidates were tested; no further classification follows from the encoded finite theory |
| Conditional Lean replay | All 1,672 known context-label derivations were kernel checked with cited facts, rules and complements as explicit premises |
| Roster pruning | All 1,450 ordinary hypotheses on the 725 inactive candidate pairs were tested for surviving scored consequences |
| Integration review | Six identified defects were fixed, including omitted verifier modules, stale semantic-report admission, source-manifest coverage and outdated claim schemas |

The [classical dossier](v0.4.0/classical-new-baseline.md), [counting dossier](v0.4.0/counting-new-baseline.md) and [quantum dossier](v0.4.0/quantum-new-baseline.md) record the new evidence. The [classical cross-review](v0.4.0/classical-baseline-cross-review.md) and [counting cross-review](v0.4.0/counting-cross-review.md) inspect the supporting arguments. The [classical model review](v0.4.0/classical-formalization-review.md), [quantum model review](v0.4.0/quantum-formalization-review.md) and [integration review](v0.4.0/integration-review.md) distinguish what was checked from what remains trusted.

Three bounded follow-ups inspect the [full QSZK operational bridge](v0.4.0/qszk-bridge-review.md), [finite ETR encoding in both directions](v0.4.0/etr-bridge-review.md), and [quantum/counting upper-bound chains](v0.4.0/quantum-counting-interface-review.md). A cross-review corrected omitted truth-constant constraints in the written ETR reduction; no canonical definition or baseline label changed. These are explicit mathematical arguments and source checks, not new Lean proofs of all model equivalences. The [source and verifier validation record](v0.4.0/validation-pre-freeze.json) binds the completed Python, core/extension and eight isolated proof-admission checks.

Some domain reports retain counts and hashes for the partial overlays they actually reviewed. They are not mislabeled as final merged runs. The [final SAT report](audit-final-sat.json), [full-context SAT report](v0.4.0/all-context-sat.json), [Lean trace report](audit-final-lean-traces.json), and [migration report](v0.4.0/roster-migration.json) bind the complete current theory.

A SAT assignment is not a model of complexity theory or ZFC. SAT establishes completeness only for literal consequences of the finite registered theory. A Lean consequence trace proves a deduction from its stated hypotheses, not the cited theorem supplied as a hypothesis. Neither check proves historical openness, textbook equivalence of every operational model, or correctness of a new model submission.

## Residual uncertainty

The independent review's broad working estimate is **about three incorrectly classified scored pairs**: approximately 1.8 from mathematical application or historical omissions, 1.0 from operational interpretation, and 0.1 from assembly or publication. The unrounded ledger is 2.9375. It does **not** meet the earlier audit's below-two criterion, and the old 1.98 estimate is not carried over to the enlarged set of class definitions.

The [risk review](v0.4.0/residual-risk-review.md) and [structured ledger](v0.4.0/residual-risk-review.json) make the assumptions visible. Their sensitivity endpoints sum to approximately 0.47–14.1 expected wrong pairs. These are subjective stress scenarios, not a confidence interval, calibrated posterior or rigorous bound. Future discoveries of flaws in currently accepted proofs are excluded, as requested. Present misquotations, wrong model transfers, missed results and pipeline mistakes remain included.

Shared causes can affect many pairs. The ledger allocates distinct affected pairs by cause and scope rather than pretending that each cell or each review is an independent trial. Reviewer agreement and repeated negative searches do not supply an empirical omission-detection rate. Missing conditional rules that affect only future scores are separate from errors in current classifications.

No concrete remaining incorrect label has been identified. The decision is to present a bounded, revisable provisional benchmark for human review, with these limits exposed. The roster's scientific value is an editorial judgment, not a consequence of the numerical risk estimate.

## Coverage lost by selecting 50

The full 61-class context has 2,049 candidate pairs. Selecting 50 leaves 725 without direct points. Of the 1,450 tested inclusion/noninclusion hypotheses on those pairs, **26 inclusions have no scored consequence**; every tested noninclusion retains at least one. These counts describe the encoded implication engine, not the proportion of important breakthroughs covered.

Examples losing all ordinary credit include FewP=UP, WPP=LWPP, LWPP=SPP and coUP ⊆ QMA. The cuts also remove direct independence credit for all 725 inactive candidate pairs. Preserving the background definitions does not preserve that scoring coverage. The [pruning review](v0.4.0/pruning-tradeoffs.md) lists every cut's scientific cost and compares optional 55- and 56-class alternatives.

## Historical admission and later corrections

The [machine-readable index](baseline-audit.json) binds the assessment and supporting reports to every scored pair. The [history registry](../data/history_reviews.json) preserves previous release records and records the current candidates' decisions against their exact dataset and audit hashes. These decisions are reusable by model runs; they do not accept a model's proposed proof.

New ordinary claims still require mathematical review, isolated fresh-kernel verification, a matching sealed artifact and accepted run provenance. Independence follows its separate metatheory-review route. Infrastructure fixtures and hypothetical consequence experiments are never AI achievements.

When an overlooked accepted pre-cutoff result is found, record its evidence, mark the direction known at cutoff, and identify any affected rescore. Preserve sealed runs and prior review history. Changing the mathematical taskset requires a new versioned snapshot. The published v0.3.1 release and tkwa.me are not changed by this provisional PR.
