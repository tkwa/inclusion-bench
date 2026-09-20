# Provisional roster decision for v0.4.0

**Select 50 scored classes from the current 61-class candidate pool.** The resulting roster replaces eleven endpoints from v0.3.1. The proposed roster gives direct targets to logspace randomness, unambiguity, counting and quantum computation; real feasibility; adaptive and iterated counting; and three additional quantum proof models. It also distinguishes uniform NC¹ from the existing nonuniform formula-size class. Every removed endpoint remains an unscored class available in definitions, cited facts, accepted claims and implication proofs.

This is the proposal selected for implementation and audit, dated September 20, 2026. It awaits the user's PR review. The cutoff stays September 1, 2026, the metric stays one point per eligible ordered pair, and the v0.3.1 independence policy stays intact. The benchmark continues to evaluate an AI's mathematical discoveries in a recorded run. The selection experiments below are checks of benchmark coverage, not a new result-impact scoring product.

## Changelist and reasons

| Add to the scored roster | Missing question or resource |
| --- | --- |
| Standard uniform NC¹ | The uniform NC¹ versus L boundary; the old nonuniform NC¹ row remains for formula lower bounds. |
| UL | Whether logarithmic-space nondeterminism can be made unambiguous. |
| BPL | Whether randomness can be removed in logarithmic space. |
| PL | Unbounded-error counting in small space and its relation to nondeterministic and parallel computation. |
| BQL | Quantum computation in logarithmic space, compared with L, BPL and PL. |
| ∃R | The NP, PH and PSPACE boundaries of finite real-feasibility problems. |
| P^#P = P^PP | Adaptive exact-counting access, including its comparison with PP and PSPACE. |
| CH | The fixed finite counting hierarchy and its possible collapse. |
| QMA(2) | Verification using unentangled proofs, including the NEXP boundary. |
| StoqMA | Stoquastic verification, connecting quantum Hamiltonians and classical probabilistic proofs. |
| QSZK | Quantum statistical zero knowledge and state distinguishability. |

| Move to unscored background | Reason and material loss |
| --- | --- |
| AC⁰ | All of its incident pairs were known in v0.3.1. It remains useful historical and inference vocabulary. |
| coRP, coUP, coMA, coAM, coQMA, Π₂P | Reallocate some complement-related weight to new resources. These classes are not aliases; asymmetric comparisons and independence questions can lose their only scored endpoint. |
| FewP | Reallocate a fine ambiguity slot. A positive FewP=UP result need not receive a remaining point. |
| LWPP, WPP | Reallocate two exact-normalization slots to adaptive and iterated counting. Positive normalization collapses can lose all direct credit. |
| E | Reallocate a linear-exponential-time slot to small-space breadth. Its quantitative hardness role remains important, but that role was only partly represented by ordinary class-pair questions. |

The comparison is between the **current 61-class catalog** and the **selected 50**, as Thomas clarified. It is not a comparison that keeps the original 50 fixed. The inference catalog contains all 61 classes, while the matrix has **50 × 50 = 2,500** potential scored pairs. A theorem about a background class can earn points for consequences whose two endpoints are scored. A background pair itself earns none. Old snapshots keep their own roster and scores; results are not compared across these changed denominators.

## The fifty endpoints

These groups help readers find classes. They are not disjoint scientific fields or numerical estimates of research importance: BPL, PL and BQL are also randomness, counting and quantum classes respectively.

| Group | Endpoints | Count |
| --- | --- | ---: |
| Circuits and advice | ACC⁰, TC⁰, nonuniform NC¹, uniform NC¹, P/poly, NP/poly | 6 |
| Space and parallelism | L, UL, NL, BPL, PL, BQL, LogCFL, NC, SC, PSPACE, EXPSPACE | 11 |
| Time, nondeterminism and real feasibility | P, NP, coNP, NP∩coNP, ∃R, NE, EXP, NEXP | 8 |
| Randomness and classical proofs | RP, ZPP, BPP, MA, AM, SBP, SZK | 7 |
| Polynomial-time counting and ambiguity | UP, SPP, C=P, PP, ⊕P, AWPP, P^#P, CH | 8 |
| Quantum computation and verification | BQP, QCMA, QMA, QMA(2), StoqMA, QSZK | 6 |
| Higher polynomial hierarchy | Σ₂P, Δ₂P, Θ₂P, PH | 4 |

NP∩coNP and NP/poly remain because they expose positive containment questions not replaced by NP and P/poly. EXPSPACE remains despite having only two old open incident pairs: the time–space gaps are real scientific questions. Θ₂P remains for the distinction between parallel and adaptive NP queries. These decisions illustrate why maximizing unknown-pair counts or equalizing group sizes would be poor selection rules.

## Evidence and alternatives

The decision combines three primary-source landscape reviews and two independent cross-reviews: [classical](classical-landscape.md), [counting and scope](counting-and-scope-landscape.md), [quantum and randomness](quantum-randomness-landscape.md), [cross-domain review](cross-domain-review.md), and [quantum definition review](quantum-cross-review.md). They give the sources, exact conventions, strongest objections and alternative portfolios. This is AI-assisted editorial judgment, not a human expert endorsement or an empirical distribution of the field's important problems.

The selected portfolio is `B-uniform` in the [comparison data](portfolio-comparison.json). The less disruptive alternative A makes eight replacements and retains E, coRP and Π₂P. B adds PL and BQL while retaining Π₂P. B-uniform replaces that final complement slot with uniform NC¹. Other defensible choices are S₂P, a gate-specified QMA₁, quantum PCP, FewP, a concrete second counting level, or an odd-prime modular class. None was rejected because its proofs or formalization would be harder.

The uniform-NC¹ margin is a judgment about breadth: it adds a basic parallelism/space boundary, while Σ₂P and PH retain the headline second-level complement-collapse question. This does not make Π₂P mathematically redundant. S₂P would instead emphasize symmetric verification; QMA₁ or QPCP would emphasize a particular foundational quantum question. Under the retained total-language scope, the chosen space and verification additions provide broader direct coverage without claiming to represent every promise formulation.

## What the old-theory experiment does and does not show

The simultaneous demotions remove **585** of the old **1,378** candidate pairs from the active matrix. That is a change in pair weighting, not a loss of 585 independent scientific conjectures. The new pairs have not been counted as open merely because they were absent from the old database.

For each of those 585 old pairs, the comparison separately assumed inclusion and noninclusion and ran the old cited implication engine: **1,170 ordinary hypotheses**. Every tested noninclusion still had a consequence on at least one retained old candidate. **22 inclusion hypotheses** had none, including FewP⊆UP, WPP⊆LWPP and several asymmetric complementary-proof comparisons. The complete list is in the comparison data. Some may acquire new consequences after adding the new classes; that must be checked on the audited graph.

This result supports making the weighting change visible. It does not justify ranking the lost positive results as unimportant, prove that the old implication library is complete, or say anything about independence. Independence is not propagated through ordinary inclusion rules. Adding uniform NC¹ after B caused no additional last-consequence loss in this particular experiment, but still removes direct Π₂P points.

## Semantic commitments and scope limits

All endpoints still contain total binary decision languages. Standard quantum promise-class inclusions imply their total restrictions, while promise separations need not. The review records this asymmetry; the website and tasks must not advertise complete coverage of canonical promise questions. Thomas explicitly selected total decision-language classes for this revision; separate promise, search/function and algebraic tracks are outside its scope.

Several conventions are essential to the proposed names:

- Uniform NC¹ means the standard extended-connection/U_E notion, operationally ALOGTIME with random access; direct-connection-only U_D uniformity is not silently substituted.
- BPL and BQL require polynomial worst-case time as well as logarithmic workspace. BQL's classical control is also space-bounded.
- StoqMA uses an explicit efficiently specified inverse-polynomial-gap threshold union. Soundness exactly 1/2 is a known NP boundary, not a normalization of general StoqMA.
- QMA(2) requires product witnesses across the two proof registers. QSZK uses a cited quantum state-distinguishability characterization with explicit preparation and threshold conventions.
- ∃R uses finite coefficient/formula encodings and genuine real semantics. P^#P is a decision class with a counting oracle; it is not #P itself. CH quantifies over a fixed finite level before the input.

Decision pairs still miss many important advances in sampling, search, algebraic circuit families, fine-grained complexity, communication, proof complexity and individual algorithms. The user relaxed the requirement that every top candidate advance score. Separate typed or quantitative tracks remain a possible later revision, with their own definitions and audits.

The provisional implementation and classification audit are recorded in the [release assessment](../baseline-audit.md). The frozen snapshot binds its definitions, evidence and historical decisions. This roster remains a proposal for PR review; the audit is revisable and does not certify that every literature judgment is correct.
