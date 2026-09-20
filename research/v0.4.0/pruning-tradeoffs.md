# What the 50-class roster leaves out

**The main loss is precision, with a smaller but real set of results losing all credit.** The proposal buys space derandomization, quantum logspace, real feasibility, adaptive and iterated counting, uniform parallelism, and new quantum-proof models by dropping some exact-counting distinctions, complement endpoints, and a finer exponential-time scale. That is a defensible breadth preference, not an objective “top50.”

The 61 definitions remain available as mathematical background. Only 50 endpoints are scored. A theorem about a background class can still earn points through consequences between scored classes, but its own pair earns none.

The current [pruning experiment](pruning-audit.json), using all 11 cuts simultaneously, found the following. Its final dataset binding is `e929704944eba030d541cf2a12a6aa012cb7a0f10c003ca308a1dda65cd85ef5`, including the two added uniform-circuit rules. This is a comparison within the 61 chosen context classes, not a claim that the best 50 classes worldwide must come from those 61.

- **2,049** candidate ordered pairs in the 61-class context; **1,324** remain directly scored and **725** do not.
- Testing both ordinary answers for those 725 removed questions gives **1,450 hypotheses**. **26 inclusions** have no new scored consequence; every tested noninclusion retains at least one.
- All 725 removed questions lose their **direct independence point**. Independence is not propagated by ordinary closure.

These are counts of encoded consequences, not probabilities of breakthroughs, scientific importance, or a claim that 98% of future advances are covered. Compound results can behave differently. The [companion review JSON](pruning-tradeoffs.json) binds the exact graph output and records every zero-credit inclusion.

## Losses from each cut

“Still scores” below means at least one retained consequence, often a weaker statement with fewer points. It does not mean unchanged recognition.

| Demoted class | Meaningful result or distinction losing direct credit | What survives, and what does not |
|---|---|---|
| **AC0** | No currently unresolved incident pair in this context. | The easiest cut. Its definitions and lower bounds still support inference. Quantitative AC0 results were not automatically rewarded by this matrix in the first place. |
| **coUP** | Complement-unambiguous computation and its quantum/proof interfaces; for example **coUP ⊆ QMA**. | UP=coUP still implies the scored UP ⊆ coNP. But coUP ⊆ QMA produces **zero** retained points. Its exact mirror UP ⊆ coQMA disappears too because coQMA is also cut. This is substantially more than removing a duplicate name. |
| **coMA** | MA complement closure and asymmetric coMA comparisons. | MA=coMA still gives coNP ⊆ MA. Some cross-class results lose all credit: **UP ⊆ coMA** is one of the 26 zero-credit cases. |
| **coAM** | AM complement closure and asymmetric public-coin proof comparisons. | AM=coAM still gives coNP ⊆ AM and PH ⊆ AM. **UP ⊆ coAM** loses all current credit. |
| **coQMA** | Quantum-witness complement closure and the opposite polarity of classical/quantum verification. | QMA=coQMA still gives PH ⊆ QMA; QMA ⊄ coQMA gives QMA ⊄ BQP. But **UP ⊆ coQMA**, equivalently coUP ⊆ QMA, loses all current credit. |
| **FewP** | Whether polynomially many accepting paths add power beyond a unique path. | **FewP=UP loses all credit.** FewP ⊄ UP would still imply NP ⊄ UP. Broader collapses can still score, so the loss particularly affects a positive intermediate collapse. |
| **LWPP** | Exact gap normalization depending only on input length. | **LWPP=SPP loses all credit**, as do some parity interfaces. A separation LWPP ⊄ SPP still gives AWPP ⊄ SPP. |
| **WPP** | Input-dependent exact normalization and its distinction from length-dependent normalization. | **WPP=LWPP loses all credit.** WPP ⊄ LWPP still gives AWPP ⊄ SPP. Keeping SPP and AWPP does not preserve the intervening normalization questions. |
| **coRP** | The other one-sided error convention as a direct algorithmic target. | RP=coRP remains expressible as RP=ZPP, and coRP=P as RP=P. But **coRP ⊆ NE** and **coRP ⊆ ∃R** each lose all current credit. |
| **E** | Deterministic time 2^O(n), rather than arbitrary polynomial exponents inside an exponential. | Every tested E outcome retains some credit. For example, NP ⊆ E implies EXP ⊄ NP; NE ⊄ E implies P≠NP. Outgoing circuit questions largely survive via EXP and padding. The finer statement and its extra points still disappear. |
| **Π₂P** | The universal second level as an explicit endpoint, particularly against classes whose complements are also cut. | Σ₂P=Π₂P still collapses PH to Σ₂P, and their inequality still gives a retained hierarchy separation. Every tested ordinary outcome retains some credit, but direct polarity-specific comparisons lose their own points. |

The counting distinctions are supported by the primary closure and model evidence in the [counting landscape](counting-and-scope-landscape.md). They are not aliases. Likewise, the E/EXP distinction and the PH allocation are discussed with sources in the [classical landscape](classical-landscape.md). The QMA complement consequence uses [Vinkhuijzen–Deutz, Theorem 11](https://eccc.weizmann.ac.il/report/2019/131/download/).

Some representative point totals make the asymmetry concrete:

| Hypothetical result | Points with all 61 endpoints | Points with the selected 50 |
|---|---:|---:|
| FewP=UP |1|0|
| WPP=LWPP |1|0|
| LWPP=SPP |2|0|
| coUP ⊆ QMA |3|0|
| coUP ⊄ QMA |841|508|
| coRP=P |44|14|
| E ⊆ P/poly |707|445|
| E ⊄ P/poly |26|17|
| PH collapses to its second level |8|4|

Those large totals measure implications of one assumed theorem in the current graph. They are not a prediction that any such theorem is true, easy, or likely. Per-class loss counts overlap when both endpoints are demoted and must not be added.

## Which cuts are most debatable?

**FewP is my first restoration candidate** if the aim is to preserve one more recognizable structural question. Its comparison with UP expresses a clean change in computational ambiguity, and the positive collapse otherwise receives nothing. Restoring it at the expense of Θ₂P, for example, would cost the dedicated parallel-versus-adaptive NP-query target. That is a substantive exchange.

**LWPP/WPP and coUP are the next preference-sensitive losses.** The former remove exact-normalizer distinctions; coUP loses several asymmetric connections to quantum and probabilistic proof systems. Which is more important depends on the research coverage desired. The graph has ten zero-credit inclusions incident to coUP, but that count alone is not an importance ranking. Restoring coQMA instead would rescue some complement mirrors, illustrating why cuts should be assessed jointly.

**E, coRP, and Π₂P are easier to defend under breadth, though each has a constituency.** Their headline collapses retain substantial consequences. Restoring E instead of NE would exchange two different finer resource emphases. Restoring Π₂P instead of uniform NC¹ would give up the distinct uniform-NC¹-versus-L question; nonuniform NC¹ cannot substitute for it. Restoring coRP instead of BQL would trade an asymmetric randomness endpoint for the quantum-space frontier.

Dropping coMA, coAM, and coQMA reduces repeated polarity weighting, but the UP/FewP examples show why “they are just complements” is not a sufficient justification. AC0 is the clearest background-only choice because it presently contributes no open pair at all.

## Equal treatment of all 61 candidates

The relevant choice is **50 out of the current 61**, not a return to the original 50. I would keep the selected 50 under a preference for broad scientific coverage. This judgment gives no advantage to old roster membership, recent implementation work, or an anticipated easier proof.

The closest tradeoffs are substantive. P^PP and CH cover adaptive and iterated counting, which I prefer to retaining both exact-normalizer endpoints LWPP and WPP. Θ₂P covers parallel versus adaptive NP queries; I narrowly prefer that distinct resource question to FewP, while recognizing that FewP=UP is the clearest wholly lost result. PL and BQL introduce majority and quantum computation under a space bound; I prefer that expansion to retaining both coRP and coUP as scored endpoints. Uniform NC¹ versus L is a stronger breadth addition than a second PH polarity.

The new quantum endpoints receive the same scrutiny. QMA(2), StoqMA, and QSZK represent unentangled witnesses, constrained verification, and statistical zero knowledge, respectively. They should be kept for those distinctions, under the agreed total-language convention. Their scientific value is not established by their being quantum or recently implemented. Conversely, complement endpoints should not be discarded merely for having a “co” prefix: the zero-credit interfaces above are real counterexamples to that argument.

NE and EXPSPACE remain preference-sensitive retained slots. They preserve nondeterministic linear-exponential interfaces and explicit exponential time-space questions, while E's finer deterministic questions remain available only through background inference. A structural-complexity emphasis could reasonably restore FewP or exact-normalizer classes by changing these or other marginal allocations. The proposal publishes that disagreement rather than calling its selection uniquely optimal.

## An optional 55–56-class compromise

If the review favors fewer blind spots over the original approximately 40–50 target, a concrete **55-class** version would restore **FewP, LWPP, WPP, coUP, and coRP**. Those are the classes behind the clearest zero-credit losses. Restoring coUP also recovers retained complement mirrors for several UP-to-co-proof results. AC0, coMA, coAM, coQMA, E, and Π₂P would remain background.

A concrete **56-class** version would additionally restore **coQMA**, giving quantum complement closure and related independence questions their direct endpoints again. That leaves AC0, coMA, coAM, E, and Π₂P as background. A reviewer more concerned with exponential resources could reasonably prefer E for that 56th slot, but that is a different scientific weighting.

These are optional comparisons, not an unannounced change to the recommended 50. Restoring a class does two things: it makes its eligible incident pairs direct questions again, and it increases the score of results whose consequences reach those pairs. It does not add a new mathematical implication. Conversely, restoring some ordinary consequence does not restore the original statement’s direct point or its independence certificate. The [targeted alternative comparison](pruning-alternatives.json) tests the 26 zero-credit hypotheses and nine illustrative results, using 31 distinct closure runs. It is not a second exhaustive experiment.

| Scored roster | Direct candidate questions | Restored relative to 50 | Context candidates still unscored | Former zero-credit hypotheses now scoring |
|---|---:|---:|---:|---:|
| Selected 50 | 1,324 | 0 | 725 | 0 of 26 |
| Optional 55 | 1,655 | 331 | 394 | 26 of 26 |
| Optional 56 | 1,733 | 409 | 316 | 26 of 26 |

The 55-class version restores the original direct endpoint point for 20 of those 26 hypotheses; the other six receive credit through different consequences. The 56-class version restores 22 direct points. Their remaining 394 and 316 unscored candidate pairs also remain without direct independence credit.

| Hypothetical result | Selected 50 | Optional 55 | Optional 56 | All 61 |
|---|---:|---:|---:|---:|
| FewP=UP | 0 | 1 | 1 | 1 |
| WPP=LWPP | 0 | 1 | 1 | 1 |
| LWPP=SPP | 0 | 2 | 2 | 2 |
| coUP ⊆ QMA | 0 | 2 | 3 | 3 |
| coUP ⊄ QMA | 508 | 664 | 716 | 841 |
| coRP=P | 14 | 38 | 38 | 44 |
| E ⊆ P/poly | 445 | 477 | 526 | 707 |
| E ⊄ P/poly | 17 | 18 | 18 | 26 |
| PH collapses to its second level | 4 | 4 | 4 | 8 |

## Independence loses more than ordinary implication scoring suggests

An inclusion theorem can pass through the remaining implication graph. An independence certificate is a metatheorem about a particular encoded sentence; it does not become an inclusion or a noninclusion. A certificate concerning a removed pair therefore earns no direct point, even if either ordinary resolution would have many consequences.

Sometimes a provable equivalence, such as a simultaneous complement transformation, can support an independence theorem for a retained pair too. That requires an explicit, separately reviewed certificate. The scorer does not infer it automatically, and a one-way ordinary implication is insufficient. The 725 removed candidate slots are therefore a real loss of direct independence coverage, not an estimate that 725 independent statements exist.

## Important directions beyond the 61 candidates

The 61-node comparison is itself selective. Plausible alternatives still outside it include:

- **NISZK:** whether statistical zero knowledge needs interaction. [Goldreich–Sahai–Vadhan, Theorems 1.3 and 1.5–1.6](https://www.wisdom.weizmann.ac.il/~/oded/PSX/gsv2.pdf).
- **S₂P and the Boolean hierarchy:** symmetric alternation, refined collapse targets, and exact optimization. DP is different from NP∩coNP. [Russell–Sundaram](https://doi.org/10.1007/s000370050007); [Kadin](https://epubs.siam.org/doi/10.1137/0217080).
- **QAM and QIP(2):** public randomness before a quantum proof, and genuine two-message quantum interaction. QIP=PSPACE is already represented; QIP(2) is a different question. [Jain–Upadhyay–Watrous, §3](https://arxiv.org/abs/0905.1300); [Quantum Proofs](https://arxiv.org/abs/1610.01664v1).
- **RL and randomized parallel classes:** L=RL need not settle L=BPL. A major one-sided or problem-specific derandomization advance can therefore remain unscored. [Vadhan, Open Problem 2.47](https://people.seas.harvard.edu/~salil/pseudorandomness/).
- **PP^PP and Mod₃P:** a concrete intermediate counting level and odd-prime modular counting. P^PP, CH, and parity do not cover every such comparison. [Fournier–Malod–Mengel, Theorem 4.3](https://arxiv.org/pdf/1110.6271).
- **CC, catalytic space, and refined exponential/oracle classes:** other parallelism, memory and lower-bound questions. Known equal names should not consume separate slots; for example, CL=CNL is already established. [Cook–Filmus–Lê](https://www.cs.utoronto.ca/~sacook/homepage/lfmmToct.pdf); [Koucký–Mertz–Pyne–Sami](https://eccc.weizmann.ac.il/report/2025/019/download).

All alternatives here must remain **classes of total binary decision languages**. Total-restricted QMA₁ or QPCP endpoints are possible, but they would not automatically cover the canonical promise versions of perfect completeness or quantum PCP. No promise track, function/search class, sampling class, or algebraic polynomial-family class is being smuggled into the roster.

There is also a limit no fifty-name selection fixes: a major algorithm for one problem need not resolve an entire class inclusion. Quantitative lower bounds and disjunctive results can likewise miss every pair. The proposed pruning should be judged as a transparent weighting of important class-comparison questions, with these concrete losses published alongside its gains.
