# Round 1: counting and quantum audit

The first pass found **no incorrect primitive seed and no independently discovered missing unconditional pair status** in the assigned classes. It found missing conditional consequences and two stronger variants that must remain on hold. The classical reviewer separately identified missing NE/NEXP versus coUP negatives; those are acknowledged, not counted again. Canonical benchmark data was not edited.

Snapshot: `8f69436c927248a9b7615fa97543f83764fef4afdc7b6a61b2ae9de1b4665d1d`. The 14 assigned classes touch **1204 distinct ordered pairs**: 279 known inclusions, 116 known noninclusions, and 809 unresolved in this snapshot. Numbers will change when the shared audit findings are integrated.

The companion JSON contains every incident row and column, source locators, exact proposed atoms, semantic file hashes, and every newly derived pair used in the fanout calculations.

## Known labels and discovery coverage

All 14 entries were swept: UP, coUP, FewP, SPP, CeqP, PP, parityP, AWPP, LWPP, WPP, BQP, QCMA, QMA, coQMA. Live Complexity Zoo requests returned HTTP403; indexed named sections and their continuation through the next heading supplied discovery coverage. No distinct coQMA entry was located, so its audit uses QMA and the explicit complement definition. Zoo text was not used as authority for a proposed fact.

| Group | Checks and result |
|---|---|
| Counting inclusions | Checked ambiguity counts, exact GapP predicates, normalizer restrictions, complement closure, and the SPP/LWPP/WPP/AWPP chains. All discovered unconditional roster edges were already derivable. |
| Quantum inclusions | Checked total-language BQP/QCMA/QMA definitions and BQP⊆AWPP, MA⊆QCMA⊆QMA⊆PP. Complementing QMA supplies the coQMA bounds. |
| Known negative labels | Checked parity versus AC0, undecidable length languages in all six nonuniform classes versus each uniform class, EXPSPACE hierarchy, and NE/NEXP versus NP subclasses. No scope mismatch found. |
| Boundary cases | PP fixed-exponent circuit lower bounds do not separate PP from P/poly. BQP/PH and QMA/QCMA oracle separations do not classify ordinary pairs. |

The primary anchors are [Gap-definable Counting Classes](https://cse.sc.edu/~fenner/papers/gaps.pdf), [An Oracle Builder’s Toolkit](https://lance.fortnow.com/papers/files/obt.pdf), [Graph Isomorphism is Low for PP](https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.190/Mitarbeiter/toran/gi-low.pdf), [Complexity Limitations on Quantum Computation](https://lance.fortnow.com/papers/files/quantum.pdf), and [Quantum Arthur–Merlin Games](https://arxiv.org/pdf/cs/0506068).

## Proposed conditional additions

These are mathematical consequences under a hypothetical premise, not new unconditional classifications. Extra pairs count the marginal change relative to the existing rule set with that premise already assumed. They overlap and must not be summed. Source abbreviations resolve to full primary references in the JSON.

| Assumption | Additional consequence | Extra pairs | Anchor |
|---|---|---:|---|
| PP ⊆ QMA | PH ⊆ PP | 21 | Vya03 |
| PP ⊆ CeqP | PH ⊆ PP | 14 | Vya03 |
| CeqP ⊆ AWPP | PH ⊆ AWPP | 18 | STT05 |
| CeqP ⊆ WPP | PH ⊆ WPP | 42 | STT05 |
| CeqP ⊆ UP | PP ⊆ UP, PH ⊆ UP, parityP ⊆ UP | 194 | OH91 |
| CeqP ⊆ LWPP | PP ⊆ LWPP, PH ⊆ LWPP, parityP ⊆ LWPP | 81 | OH91, KST92, STT05, Toda91 |
| CeqP ⊆ coNP | PH ⊆ Sigma2P | 7 | STT05, Ivanashev26 |
| NP ⊆ SPP | Delta2P ⊆ SPP | 13 | SizeSPP03 |
| NP ⊆ LWPP | Delta2P ⊆ LWPP | 9 | STT05 |
| NP ⊆ AWPP | Delta2P ⊆ AWPP | 3 | STT05 |
| NP ⊆ BQP | Delta2P ⊆ BQP | 11 | FR99, BV97 |
| NP ⊆ parityP | Delta2P ⊆ parityP | 2 | OH91 |
| NP ⊆ WPP | Theta2P ⊆ WPP | 3 | STT05 |
| parityP ⊆ BPP | PH ⊆ BPP | 182 | Toda91 |
| parityP ⊆ BQP | PH ⊆ BQP | 68 | Toda91, FR99, BV97 |
| PP ⊆ AWPP | PH ⊆ AWPP, parityP ⊆ AWPP | 16 | Toda91, OH91, STT05 |
| PP ⊆ BQP | PH ⊆ BQP, parityP ⊆ BQP | 48 | Toda91, OH91, FR99, BV97 |
| PP ⊆ parityP | PH ⊆ parityP, parityP ⊆ parityP | 7 | Toda91, OH91, OH91 |
| PP ⊆ SPP | PH ⊆ SPP, parityP ⊆ SPP | 55 | Toda91, OH91, SizeSPP03 |
| PP ⊆ LWPP | PH ⊆ LWPP, parityP ⊆ LWPP | 40 | Toda91, OH91, STT05 |
| CeqP ⊆ parityP | PH ⊆ parityP | 12 | STT05, OH91 |

The potentially stronger **CeqP⊆QMA ⇒ PH⊆PP** is held for an independent check of Vyalyi’s equality-test construction. **CeqP⊆parityP ⇒ PP⊆parityP** is also held: a tempting argument incorrectly relativizes its assumption. Its weaker PH consequence has a valid separate derivation using the unconditional relativizing UP⊆parityP inclusion.

One specific guard matters: **NP⊆SPP does not justify the PH⊆SPP rule by simply relativizing the premise**. The source gives the Delta2P consequence directly and adds a nonzero-measure hypothesis for its stronger PH statement. See [The Size of SPP, before Corollary5.3](https://eccc.weizmann.ac.il/report/2003/063/download).

## Exact-definition inspection

No concrete semantic bug was confirmed. Nondeterministic lists preserve path multiplicity; truncation is excluded by global halting requirements. GapP functions come from actual machines. Signed nonzero WPP normalizers convert to positive normalizers without adding power. AWPP has the correct universal inverse-exponential accuracy quantifier. Quantum gates are explicit, the circuit generator is a uniform polynomial-time transducer, and acceptance bounds cover every input. Quantum witnesses are normalized pure states; mixed states add no power to this linear optimization. These observations are not Lean proofs of textbook equivalence.

The shared regular-padding rules were independently approved for every assigned target. Exact padded length depends only on input length, so LWPP keeps a length-only normalizer. AWPP error polynomials compose, and quantum circuits hardwire the suffix while padding witnesses. Use a padding length such as `(n+2)^k` or treat finitely many short inputs separately.

A minor stale comment in Counting.lean still says WPP/LWPP are omitted; their definitions are now in Transducers.lean. This has no semantic effect.

## Cutoff and residual uncertainty

[Ivanashev v5](https://arxiv.org/abs/2507.04110v5) is dated August2,2026 and was screened. [Bostanci–Haferkamp–Nirkhe–Zhandry](https://arxiv.org/abs/2511.09551v2) and [Bostanci–Huang–Vaikuntanathan](https://arxiv.org/abs/2602.09385v2) are also before the cutoff, but their separations are relativized. [QMA has perfect completeness](https://arxiv.org/abs/2609.13032) was submitted September11,2026 and is excluded.

**This pass does not support an expected remaining error count below two.** The main residual risk is a missed family of implicit negative consequences, followed by less familiar counting collapse theorems and recent literature. Errors can be correlated: one omitted theorem may change many pairs. We have no calibrated omission rate with which to multiply the remaining count.

The JSON gives a conservative logical range from zero to the number of unresolved incident pairs; it is deliberately not a confidence interval. It excludes hypothetical future failures of accepted proofs. It does not exclude theorem-scope errors, definition mistakes, or overlooked pre-cutoff theorems. After integrating cross-team findings, the next pass should recompute all 14 rows and columns and independently challenge every proposed operator/oracle derivation before reducing uncertainty estimates.
