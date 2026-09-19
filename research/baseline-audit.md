# September 2026 historical audit

The audit corrects **eight classifications** and adds **106 implication rules**. Version 0.3.0 has 50 classes and 2,500 ordered pairs: **709 known inclusions, 413 known noninclusions and 1,378 remaining questions**. The cutoff includes results publicly available before September 2, 2026, 00:00 UTC.

The audit is AI-assisted. Domain reviewers searched primary literature, then exchanged scopes for independent checks. It does not represent a human expert endorsement. Existing accepted mathematical results remain trusted inputs; their proofs were not reconstructed in Lean.

## Corrections

Both **NE and NEXP are not contained in Θ₂P, coNP, coRP or coUP**. These eight directions were candidates in version 0.2.0 and now earn zero.

[Buhrman–Fortnow–Santhanam, Theorem 6](https://eccc.weizmann.ac.il/report/2009/064/download/) excludes NEXP from polynomial time with a fixed polynomial bound on NP queries and advice. Its c=1 case covers logarithmically many queries without advice. The [regular-padding argument](audit-padding.md) transfers this exclusion to NE. Complement and hierarchy reasoning independently establish the six coNP/coRP/coUP consequences. The fixed query exponent matters: the theorem does not establish NEXP ⊄ Δ₂P.

The additional rules comprise 81 regular-padding instances, three classical consequences and 22 counting/quantum consequences. They include stronger propagation from hypothetical exact-counting collapses. The latter constructions received a [separate third review](audit-round3-exact-count.md). These are implications used to score future answers; adding them does not assert their open premises.

## What was checked

| Check | Coverage and result |
| --- | --- |
| Domain literature review | All 50 class entries and all 2,500 ordered pairs indexed through overlapping domain and theorem-family reviews |
| Independent cross-review | Classical/circuit/space seeds, counting/quantum seeds, model conventions and proposed implications |
| External inclusion census | 582 existing inclusions confirmed; no missing inclusion found in the matched portion of the cited census |
| Independent SAT encoding | Both polarities tested for all 1,378 candidates; no additional forced resolution in the finite cited theory |
| Lean inference replay | All 1,122 known-label derivations checked with literature facts and rules as explicit hypotheses |
| Recent title screening | 1,488 conference entries and 580 ECCC submission-window records, with 32 closer primary-source scope checks |
| Additional quantum literature | 984 cutoff-eligible Quantum journal entries inventoried, 94 selected by the recorded title filter; TQC/QIC indexes and 27 closer primary-source checks |
| Quantum semantics | Exact gates, complete circuits and register embedding preserve normalization; acceptance probabilities are proved between zero and one |
| Operational verification | All 50 Lean definitions compile; isolated proof admission accepts valid proofs and rejects the tested forged evidence |

The title counts overlap across venues and repositories; they are not a count of distinct papers or full-paper reviews. ECCC submission dates are not publication dates. Relevant reports and revisions were checked for actual public availability. FOCS 2026 titles require individually dated preprints because the conference occurs after the cutoff.

A SAT model is not a model of complexity theory or ZFC. The SAT check establishes completeness only for literal consequences of its finite encoding. Likewise, a Lean trace proves the deduction from its stated hypotheses, not the literature theorem supplied as a hypothesis. No-result literature searches supply revisable historical judgments, not proofs that a problem was open.

## Residual-error assessment

The final working expectation is **1.98 incorrectly classified pairs** (unrounded ledger sum 1.9822), slightly below the requested threshold of two. The research pass stopped after **4,584,652 tracked goal tokens**, before release assembly and publication. This is a subjective judgment with little margin to the threshold; it is not a calibrated bound.

| Cause group | Working expected wrong pairs |
| --- | ---: |
| Definition and theorem-application errors | 0.602 |
| Missed older results | 1.0302 |
| Missed recent results | 0.30 |
| Software and final assembly | 0.05 |
| **Total** | **1.9822** |

The recorded sensitivity endpoints sum to **0.31–12.33 expected errors**. They illustrate how different probability and consequence assumptions change the answer; they are not a confidence interval. More than two actual errors remains plausible.

The final assessment is recorded in `audit-assessment.json` and bound to the pair index. Its unit is an incorrectly classified ordered pair. A shared mistake can affect many pairs, so the ledger counts the distinct affected pairs conditional on each error event, rather than assigning an independent probability to every matrix cell. It excludes future discoveries of flaws in currently accepted proofs, as requested.

The estimate is subjective. Its sensitivity scenarios are not confidence intervals, and a broad upper scenario can exceed two even when the working expectation is below two. Reviewer agreement is not treated as independent statistical evidence. Missing conditional implications that change no current classification do not contribute to the current-label error count, though they can affect future scores.

## Historical decisions and corrections

The [historical registry](../data/history_reviews.json) records each admitted question's decision, reviewer identity, evidence and rationale against the exact dataset hash. Model runs reuse those decisions. New ordinary results still require proof verification, mathematical review and sealed run provenance; independence follows the separate metatheory-review protocol.

If an earlier accepted result was missed, record the evidence, mark the pair known at the cutoff and revise any affected score. Preserve the original run and review history. Changes to the mathematical baseline create a new benchmark version. Version 0.2.0 remains available in Git history and its release tag.

## Evidence

The [machine-readable index](baseline-audit.json) links all 2,500 pairs to their domain dossiers, known-result sources and final checks. It hashes the supporting reports and the structured assessment.

- Domain reviews: [classical](audit-round1-classical.md), [circuits and space](audit-round1-circuits-space.md), [counting and quantum](audit-round1-counting-quantum.md).
- Cross-reviews: [classical/circuit/space](audit-round2-cross-classical.md), [counting consequences](audit-round2-cross-counting.md), [exact-count constructions](audit-round3-exact-count.md).
- Later literature checks: [recent publications](audit-round2-recent.md), [counting interfaces](audit-round4-interfaces.md), [older classical results](audit-round4-classical-risk.md), [recent quantum and zero knowledge](audit-round5-recent-quantum.md), [internal counting classes](audit-round6-internal-counting.md).
- Risk and method checks: [counting/quantum risk](audit-round3-counting-risk.md), [independent audit-method review](audit-round4-audit-method.md).
- Reproduction evidence: [final SAT report](audit-final-sat.json), [all known-label Lean traces](audit-final-lean-traces.json), [external census](audit-round1-external-census.json), and the [development instructions](../docs/DEVELOPMENT.md#reproduce-the-historical-audit-checks).

One plausible pre-cutoff NL-versus-LogCFL manuscript was withheld because the reviewers found a concrete counterexample to a closure lemma and separate gaps in its entropy argument. The [cross-review](audit-round2-cross-classical.md#independent-review-of-the-may-2026-separation-claim) states those objections. This decision concerns an error visible now; it is not a charge for a hypothetical future flaw in an accepted proof.
