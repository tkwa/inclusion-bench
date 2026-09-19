# Counting and quantum residual-risk assessment

Assessment date: 2026-09-19. Historical cutoff: 2026-09-01. Dataset: `e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3`, with 709 inclusions, 413 noninclusions and 1,378 candidate pairs. The accompanying JSON contains the measured dependency exposures, hypothetical fanouts and numerical assumptions.

My subjective expectation is **1.12 wrong current pair labels** within the scope below: 0.435 from counting/quantum definition or theorem-application mistakes, and 0.6802 from missed older results. I found no concrete remaining incorrect label. This estimate is a judgment, not a calibrated statistical bound; it was not chosen to meet the project's stopping threshold. Varying the event probabilities across the stated sensitivity scenarios while keeping conditional impacts fixed gives 0.32–3.15. That range is not a confidence interval and does not limit larger correlated failures.

## Scope and overlap

Definition and application review covers pairs incident to any of UP, coUP, FewP, SPP, CeqP, PP, parityP, AWPP, LWPP, WPP, BQP, QCMA, QMA and coQMA. There are 1,204 such pairs: 279 included, 118 separated and 807 candidates. This component concerns mistakes in our use of published results or our operational definitions. It excludes future discoveries of flaws in accepted published proofs.

For missed older results, I exclude every pair with a circuit, space, exponential-time or advice endpoint assigned to the other audit: AC0, ACC0, TC0, NC1, L, NL, LogCFL, NC, SC, Ppoly, NPpoly, PSPACE, EXP, NEXP, EXPSPACE, E or NE. That leaves 728 pairs, with 149 known inclusions and 579 candidates. The candidates split into 53 internal counting pairs and 526 interfaces involving quantum or other polynomial-time classes. Recent-paper discovery and acceptance review is also excluded; another reviewer owns it.

The 22 newly integrated conditional rules change **zero current labels**. Their omission risk therefore contributes zero to this assessment, even though they matter for scoring future advances.

The parent should charge each incorrect pair to its first applicable cause. In particular, do not add the definition/application component again if another dossier already counts the same counting or quantum model failure. Multiple derivations or missed papers resolving one pair count once.

## Numerical judgment

| Residual cause | Probability of at least one error | Mean distinct wrong labels given that event | Expected labels |
|---|---:|---:|---:|
| Counting definition or textbook-transfer error | 0.6% | 30 | 0.180 |
| Quantum definition or simulation-transfer error | 0.6% | 35 | 0.210 |
| Other seed statement or scope error | 0.3% | 15 | 0.045 |
| Missed older internal counting inclusion | 4% | 5 | 0.200 |
| Missed older cross-interface inclusion | 8% | 6 | 0.480 |
| Missed older ordinary noninclusion or independence result | 0.01% | 2 | 0.0002 |

Each omission row describes **one global event**: at least one result was missed anywhere in the whole family. Its conditional mean counts the union of all distinct wrong labels caused by all omissions in that family, after earlier causes have been excluded. Six is not an impact per paper, and 8% is not a probability per pair. Neither should be multiplied by 526 or by the number of possible omitted results. No independence assumption between rows is needed to add expectations of these disjointly attributed counts.

The model-error probabilities are small because concrete definitions and their transfer conditions were inspected repeatedly, not because the deep published theorems were formalized. The conditional impacts remain substantial because a single shared definition error can invalidate several applications at once. The older-literature probabilities are larger because correlated searches can repeatedly miss the same intermediate class or terminology.

## Evidence and conditional impact

Counting inspection covered transition multiplicities, halting on all branches, the exact SPP characteristic gap, CeqP's zero gap, PP's positive gap, odd path counts, AWPP's nonnegative global bounds, and actual computed signed WPP/LWPP normalizers. Quantum inspection covered the explicit H/T/X/CNOT formulas, distinct control and target wires, input/witness/ancilla indexing, normalized pure witnesses, total-language gaps and a concrete uniform circuit generator. No class-changing mismatch was found. Model equivalences and deep simulations remain trusted mathematics under the user's waiver, rather than newly machine-checked theorems.

Twenty-three relevant inclusion seeds and complement conventions were reread against primary passages. Examples include [Marriott–Watrous, Theorem 3.4](https://arxiv.org/pdf/cs/0506068) for QMA's PP upper bound, [Fortnow–Rogers, Theorem 3.1](https://lance.fortnow.com/papers/files/quantum.pdf) for BQP's AWPP upper bound, and [Fenner–Fortnow–Kurtz–Li, Corollary 6.4](https://lance.fortnow.com/papers/files/obt.pdf) for WPP's AWPP upper bound. The detailed source and operator review is recorded in the round-two dossier.

Withholding selected anchors from the current closure removes 5 encoded labels for BQP⊆AWPP, 6 for WPP⊆AWPP, 18 for QMA⊆PP, 34 for a group of gap/threshold anchors, 39 for the SPP–LWPP–WPP chain and 45 for either FewP⊆SPP or the two MA–QCMA–QMA simulation anchors. These are lost encoded derivations, **not counts of false mathematical statements**: some statements still have independent elementary arguments. They justify allowing substantial conditional fanout without assuming that every unsupported path is wrong.

Hypothetical old inclusions range from one newly classified in-scope pair for SZK⊆PP or SBP⊆QMA to nine for SBP⊆AWPP or NPcapcoNP⊆SPP. Strong counting collapses have larger fanouts, such as 28 for CeqP⊆AWPP and 33 for SPP⊆NP, but an unnoticed older theorem of that strength seems less likely than a local inclusion. These are stress tests, not proposed facts or statement-specific probabilities.

All classes remaining in the older-omission scope contain P and lie within PSPACE. An ordinary noninclusion between them would imply P≠PSPACE. This makes an unnoticed established older noninclusion much less plausible than a misread oracle result. The primary [SZK/PP paper](https://eccc.weizmann.ac.il/report/2016/140/) and [SBP/QMA approximate-counting paper](https://eccc.weizmann.ac.il/report/2019/015/) explicitly supply oracle separations; neither supplies a corresponding ordinary label.

## Most useful next check

The largest residual component is older cross-interface literature. An independent reviewer is now checking [Morimae–Nishimura, *Quantum interpretations of AWPP and APP* (2016)](https://www.rintonpress.com/xxqic16/qic-16-56/0498-0514.pdf), especially Figure 1 and Theorems 3–8, and the complete taxonomy in [Böhler–Glaßer–Meister (2003)](https://eccc.weizmann.ac.il/report/2003/069/). The bounded task is to compare roster reachability through postBQP_FP, postBPP_FP, WAPP, APP and SBQP, concentrating on WPP, AWPP, BQP, SBP, AM and UP/coUP. This adds a different source family to the already repeated FFK/STT/Vyalyi checks.

UP∩coUP must not be replaced by NPcapcoNP, WAPP must not be replaced by WPP, and exact postselection identities must retain their stated gate model. My preliminary reading found no new roster edge; I have not reduced the estimate before the independent comparison. A separate direct proof that the four explicit quantum gates and initial-state embedding preserve normalization would address the quantum-definition component.

Zero additional SAT-forced literals establishes closure only under the encoded rules. It supplies no likelihood against a theorem absent from those rules. Likewise, the number of subagent reviews is not treated as a multiplier of independent confidence.
