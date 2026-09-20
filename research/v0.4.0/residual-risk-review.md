# Independent residual-risk review for provisional v0.4.0

My working judgment is **about three incorrectly classified scored ordered pairs**, under the broad interpretation that includes mismatches between the intended classes and the benchmark's operational definitions. About **1.8 pairs** comes from mathematical statement/application or historical omission risk; about **1.0** from class conventions and operational interpretation; about **0.1** from baseline assembly and publication. These are subjective planning estimates, not a calibrated posterior, a confidence bound, or a claim that the error count is below two.

There is no concrete remaining incorrect label identified by this review. That supports presenting a provisional release for review. It does not make the residual expectation zero, and it does not justify reusing the parent release's 1.98 estimate without adjustment.

This report is an independent input to the root reviewer's release-wide assessment. It does not authorize a historical registry or freeze a release. The [JSON](residual-risk-review.json) records the working ledger, exact input hashes, sensitivity choices and attribution rules. Mathematical judgments are current through the **September 1, 2026** cutoff. Future discoveries of flaws in proofs currently accepted by the literature are excluded, as the user requested. Present misquotations, wrong theorem applications, overlooked accepted results, incorrect model translations, and release-binding mistakes are included.

## Unit and scope

The unit is one distinct **scored ordered pair**, not a paper, rule, endpoint or failed proof attempt. For historical eligibility, I assess the proposed treatment of the 1,324 remaining questions as open at cutoff. A record currently marked merely `unreviewed` does not itself assert openness; the estimate applies if it is adopted into the eligibility registry.

The current closure has 845 inclusions, 331 noninclusions and 1,324 candidates. The 39 retained scored endpoints give 1,521 retained pairs; the eleven additions touch 979 other scored pairs. I also rebuilt the parent facts, rules and complements in a fresh closure and compared all 2,500 old context pairs: their classifications are unchanged. This is a useful migration check, not a repeated independent audit of every retained claim.

| Disjoint pair block | Pairs | Inclusion | Noninclusion | Candidate |
|---|---:|---:|---:|---:|
| Both endpoints retained from v0.3.1 | 1,521 | 482 | 246 | 793 |
| At least one new quantum endpoint: BQL, QMA2, StoqMA, QSZK | 384 | 117 | 27 | 240 |
| Otherwise, a new BPL, UL, PL or UniformNC1 endpoint | 352 | 161 | 40 | 151 |
| Otherwise, a new PSharpP or CH endpoint | 164 | 69 | 12 | 83 |
| Remaining ExistsR pairs | 79 | 16 | 6 | 57 |
| **Total** | **2,500** | **845** | **331** | **1,324** |

The priority in this table assigns a mixed new-class pair exactly once. It is a bookkeeping convention, not a statement that, for example, BQL has no classical-space risks. The ledger keeps common model causes separate from these omission blocks.

## What carries forward

The [v0.3.1 assessment](../audit-assessment-v0.3.1.json) reported 1.9822 expected wrong pairs over its 2,500-pair roster. That number was already judgmental. It cannot be treated as a measured error rate and multiplied by 1,521/2,500. The removed endpoints were concentrated in complement and exact-counting families, and their background facts still participate in inference.

For the retained pairs, the old omission partition becomes:

| Old review family, after restricting to retained endpoints | Pairs | Candidates |
|---|---:|---:|
| Resource/circuit/advice endpoint first | 945 | 387 |
| Internal counting | 36 | 19 |
| Other counting/quantum interfaces | 315 | 256 |
| Basic classical block | 225 | 131 |

I retain approximately 0.61 expected historical omissions in those four blocks: 0.25, 0.06, 0.20 and 0.10 respectively. These are lower than the corresponding parent allowances because fewer distinct labels remain scored, particularly the former LWPP/WPP/FewP/coUP comparisons. They are not zero: retained questions still depend on auxiliary classes and nonuniform conventions. No new source check discovered a reason to reset their likelihoods to zero.

I also retain about 0.20 for overlooked recent results affecting retained pairs, 0.04 for statement/application error, and 0.25 for operational-model application. The new primary-source checks and semantic reviews revisit some old machinery, but they are not independent repetitions of the entire old audit. Their overlapping source ancestry should not be counted as repeated independent evidence.

The inherited nonuniform contract is a separate common cause. Five currently scored nonuniform classes each have 45 recursive target classes, giving **225** directed noninclusions from nonuniform endpoints justified by arbitrary unary languages. Of these, 170 are retained pairs and 55 involve new endpoints. Applying the parent's very small subjective common-contract probability, 0.0005, to that explicit fanout gives about 0.11 expected pairs. The convention is clear and repeatedly checked; this residual allowance concerns a shared interpretation conflict, not the chance that a standard accepted proof will later fail.

## What the new review changes

The [classical source cross-review](classical-baseline-cross-review.md) accepts all thirteen seeds, eight padding rules and three complements. It reproduced every one of its 585 context-incident statuses. It checked U_E rather than U_D uniformity, strict-majority ties, fresh coins, unique accepting paths, simultaneous SC bounds, and finite real encodings. The new BFV hardwiring consequences are explicit derivations, and they add no unconditional label.

The [counting cross-review](counting-cross-review.md) reconstructed the P^PP/CH oracle arguments, distinguished the function class #P from the decision endpoint, and rejected unjustified outer-oracle substitutions. It also tracked the quantum-advice correction and its later repair. This is strong evidence against the particular tempting errors; it is not a census of every old CH corollary.

The [classical model review](classical-formalization-review.md) and [quantum model review](quantum-formalization-review.md) independently read the new definitions. Their retained Lean checks address real failure modes: fair-coin branch weighting, duplicate nondeterministic paths, visited-space accounting, fixed binary addresses, malformed real syntax, separable witness structure, discarded quantum environments, encoded width, and StoqMA threshold arithmetic. All 22 source-file bindings in their two hash maps match the present files.

Those checks support smaller model-risk estimates than would be reasonable for unreviewed definitions. They do not prove every required equivalence. The remaining boundary is principally the match between the exact implementation and cited machine, generator, QSD, amplification and real-encoding conventions. The waiver for re-formalizing existing proofs does not erase that matching obligation.

My new-model allowances are approximately 0.12 for the classical resource/uniformity block, 0.07 for PSharpP/CH, 0.09 for real feasibility and 0.30 for the four quantum additions, plus 0.10 for a shared generator/encoding defect affecting new-endpoint pairs. The quantum allocation is larger because several distinct bridges remain: pure-product witnesses, threshold-union semantics, logspace-controlled unitary computation and mixed-state distinguishability. It does not assert that any one of those definitions is wrong.

For missed older results on new-endpoint pairs, I allocate approximately 0.16 to resource/uniformity interfaces, 0.15 to counting, 0.11 to real feasibility and 0.25 to quantum interfaces. A further 0.20 covers recent omissions in the new blocks, and 0.08 covers a present theorem-application error. The 2025–2026 checks found genuine progress outside the selected endpoints and several invalid transfer opportunities, including the withdrawn TreeEval claim, modular logspace versus ordinary unambiguity, catalytic memory, real-alphabet PCPs and StoqMA(2) versus QMA(2). These concrete exclusions help; negative search results alone do not certify openness.

## Working ledger

| Cause group | Working expected distinct wrong pairs |
|---|---:|
| Retained-pair operational interpretation | 0.25 |
| Retained-pair theorem application | 0.04 |
| Retained-pair older omissions | 0.61 |
| Retained-pair recent omissions | 0.20 |
| Shared nonuniform contract, all scored pairs | 0.11 |
| New-endpoint operational interpretation, including shared infrastructure | 0.68 |
| New-endpoint theorem application | 0.08 |
| New-endpoint older omissions | 0.67 |
| New-endpoint recent omissions | 0.20 |
| Additional baseline assembly/publication error | 0.10 |
| **Rounded working total** | **about 3.0** |

The underlying arithmetic is preserved in JSON for review, not because four decimal places are meaningful. The component sensitivity endpoints span roughly **0.5 to 14.1** when added. That is an illustrative stress range, not a confidence interval or a mathematical upper bound. There is no empirical omission-detection rate with which to calibrate these judgments.

For rows expressed as probability times impact, the event means **at least one error somewhere in that family**. The conditional impact is the mean number of distinct affected scored pairs across that event, including multiple related omissions. It is not a per-paper mean to be multiplied again by an unknown number of papers. A reviewer could reasonably choose different probabilities or impacts; those changes should be visible rather than selected to meet a threshold.

## Correlation and fanout

Assign a wrong pair first to an operational/convention mismatch, then to a mistaken theorem application, then to an older omission, then to a recent omission, and finally to an additional assembly error. Later rows count additional distinct pairs only. Within omission rows, retained and new pair blocks are disjoint; the priority table resolves overlaps between new families. This is an intended attribution rule, not proof that the numerical judgments form an exact joint probability model.

The same overlooked theorem can affect both retained and new pairs. Those counts may be added because they are different pairs; their probabilities must not be treated as independent. Likewise, a common serialization or uniformity mistake must not be charged afresh to every class that imports the same module. The residual common-infrastructure row covers that situation.

As a scale check, twelve **hypothetical** inclusions were propagated through the current engine. These are not proposed facts. QSZK ⊆ PP would resolve four current candidates, including one retained pair. StoqMA ⊆ BQP would resolve 34, including twenty retained pairs. UL ⊆ BQL would resolve one; CH ⊆ PP would resolve nine. Thus a family impact of a few pairs can coexist with a much larger tail. These counterfactual consequences inform scale only; they supply no probability that an old theorem was missed or that a hypothesis is true.

Missing conditional rules that change only future hypothetical scores are outside this error count. So are the importance of a question, a model's likelihood of solving it, and the chance that a submitted new proof will fool an adjudicator. The latter deserves separate evaluation of the proof-admission system; it is not a current cutoff-classification error.

## Pipeline and binding limits

Twenty benchmark tests passed in this review, including background-node and scored-roster behavior. The 2,500 scored pairs and the 1,521/979 migration split were independently recomputed. The initially stale SAT snapshot has now been corrected by the root reviewer: I checked that both final reports bind the current dataset and the independently reconstructed 221,345-clause theory. The scored report tests 2,648 hypotheses and the all-context report tests 4,098, with no additional consequence in either. I also matched the 1,672 targets in the successful conditional Lean replay report to the entire current baseline. SAT completeness concerns the registered finite theory; it is not completeness of the literature. The Lean replay checks inference conditional on trusted historical results; it does not re-prove all those results.

The provisional data digest at this review is `e929704944eba030d541cf2a12a6aa012cb7a0f10c003ca308a1dda65cd85ef5`; the JSON also records a mathematical pair-matrix hash and source hashes. Final adoption must bind the final assessment, dataset, complete pair index, history decisions and published payload. The 0.10 pipeline allowance is conditional on those checks passing. A failed binding check is a concrete repair obligation, not something to absorb into a probability allowance.

## Pruning and next useful checks

The roster remains total binary languages. Demoting an endpoint changes coverage, not the truth of its claims. The parent had 585 open pairs that are no longer directly scored; background implications can preserve some ordinary consequences. Direct independence credit on an inactive pair is lost because independence does not propagate. Neither that loss nor a narrower question portfolio should be disguised as reduced mathematical error. The separate pruning report must retain these losses even if the residual estimate improves.

Three bounded follow-ups have the highest expected information value:

1. **Quantum/counting upper-bound chains.** Assign an independent reviewer the exact candidates QSZK versus PP/PSharpP/CH, QMA(2) versus PSPACE/CH, and StoqMA versus BQP. Follow full primary theorem chains through intermediate classes, including the pre-cutoff 2025–2026 updates, and write the missing premise whenever a transfer fails. These families account for much of the new omission allowance; an obscure intermediate-class theorem can affect several labels even when its title never names a roster class. The review must distinguish ordinary total languages from promises, restricted nonnegative witnesses, postselection and advice.
2. **The QSZK operational bridge, end to end.** Starting from the actual `Statistical.lean` formulas, derive the reduced density matrix, identify `measurementProbability` with its projective measurement probability, and show that the defined far/close predicates equal the half-trace-norm conditions, including attained boundaries. Then check the total-language QSD reduction in both directions against the exact cited theorem. The environment-sign invariant is useful but does not prove this entire correspondence. A mistake here could invalidate a whole family of model-bound labels without contradicting any accepted source theorem.
3. **Real-feasibility encoding and counting boundary.** Have a reviewer who did not design `RealSyntax` give explicit polynomial reductions between its accepted words and a primary-source finite ETR encoding, including unary metadata, binary coefficients, Boolean negation, malformed words and quadratic auxiliary variables. In parallel with that mathematical mapping, check the precise Boolean-part distinction between P_R^0 and NP_R^0: a PosSLP or complex-feasibility upper bound must not become an ∃ℝ upper bound. The current parser checks prove several local properties; the complete polynomial-equivalence argument remains external.

These tasks may confirm the current judgments rather than uncover errors. Their value is that each targets a named residual mechanism, not that spending another token budget automatically lowers the estimate. Final exact-input pipeline checks remain mandatory before freezing any historical decisions.

I would not present this independent assessment as evidence that the broad expected error is below two. The narrower mathematical/historical subtotal is around 1.8, but substituting it for the broad total would silently discard model and assembly risks that remain relevant to a Lean-based benchmark.
