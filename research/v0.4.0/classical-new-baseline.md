# Classical baseline additions for provisional v0.4.0

This AI-assisted review proposes **13 primitive facts, eight padding rules and three complement identities** for BPL, UL, PL, ∃ℝ and UniformNC1. The accompanying [JSON](classical-new-baseline.json) contains importable records and all **585 ordered pairs** incident to these five endpoints in the proposed 61-class context. The literature cutoff remains **September 1, 2026**.

The current overlay resolves 234 of these pairs by inclusion and 60 by noninclusion; 291 remain candidates. These are consequences of the listed sources and the existing baseline, with explicitly listed quantum/counting inputs from the other reviewers. They are not 585 independently certified historical decisions. Recompute the overlay after the complete baseline is merged. The JSON binds the exact files used here and identifies the older v0.3.1 dataset separately.

## Models that the facts require

**BPL** uses fresh fair coins, a read-only binary input, logarithmic work space on every computation prefix, and one worst-case polynomial time bound for every input and coin sequence. The acceptance gap is at least 2/3 versus at most 1/3. Re-reading an uncounted random tape, or replacing the clock with almost-sure termination, changes the model. [Le Gall, Nishimura and Yakaryılmaz, §2.1](https://arxiv.org/pdf/2105.02681) distinguish polynomial-time BPL from its unrestricted-time counterpart.

**UL** has at most one accepting computation path on every input. It uses logarithmic space and a polynomial clock on every branch; membership means that the one accepting path exists. Distinct choices leading to the same configuration still give distinct paths. “Exactly one on yes inputs” is insufficient if no inputs may have several accepting paths. Nor is ordinary UL the stronger restriction imposing uniqueness between every pair of configurations. [Reinhardt and Allender](https://people.cs.rutgers.edu/~allender/papers/nlul.pdf) also prove an advice simulation of NL; removing that advice would change the theorem.

**PL** is polynomial-time logarithmic-space computation with acceptance probability greater than 1/2 exactly on members. Equality at 1/2 belongs on the no side. An equivalent definition uses a positive integer GapL function, where GapL is a difference of two polynomial-clocked #L path counts. [Allender and Ogihara, Propositions 2–3 and Theorem 6](https://www.numdam.org/item/ITA_1996__30_1_1_0.pdf) supply the bridge and the equivalence with the classical unrestricted-time definition. Bounded error is a different requirement.

**∃ℝ** is the downward closure, under polynomial-time binary many-one reductions, of finite real feasibility. A suitable concrete complete problem is a finite system of quadratic equations with rational coefficients encoded in binary. Variables range over the mathematical reals; the input remains a finite binary string. [Meer and Wurm, Definition 1](https://arxiv.org/html/2502.00680v1) give this formulation. A witness need not have polynomially many rational bits. Arbitrary real machine constants and succinct descriptions of exponentially many constraints are excluded.

**UniformNC1** means standard **U_E** uniformity, equivalently ALOGTIME on a random-access-input alternating machine. The finite machine, address tape, branch rules and logarithmic clock must be explicit. DLOGTIME recognition of the **direct** connection language defines U_D, for which the equivalence with ALOGTIME is not established by the standard theorem. [Behle, Krebs, Lange and McKenzie, Remark 1](https://eccc.weizmann.ac.il/report/2011/095/revision/1/download/) make this distinction explicit. This endpoint is separate from the benchmark’s existing nonuniform NC1.

## Primitive facts and their transfers

| Proposed fact | Evidence and exact scope |
|---|---|
| L ⊆ BPL | Ignore the random coins; also displayed in Le Gall–Nishimura–Yakaryılmaz §2.3. |
| BPL ⊆ BPP | Forget the space bound while preserving polynomial time and the all-input error gap. |
| BPL ⊆ SC | [Nisan’s 1994 abstract](https://cris.huji.ac.il/en/publications/rl-sc-2/) explicitly covers two-sided bounded error and gives simultaneous polynomial time and O(log² n) space. |
| BPL ⊆ PL | A bounded-error machine satisfies the weaker strict-majority condition. |
| L ⊆ UL ⊆ NL | Deterministic computations have at most one accepting path; forgetting uniqueness gives NL. |
| NL ⊆ PL | For a clocked NL machine, its #L accepting count minus zero is a GapL function positive exactly on members. |
| PL ⊆ uniform NC | [Borodin–Cook–Pippenger, Corollary 6.3](https://www.cs.toronto.edu/~bor/Papers/parallel-computation-well-endowed-rings.pdf) gives NC²; §2 specifies logspace uniformity. |
| NP ⊆ ∃ℝ | Boolean circuit satisfiability becomes a quadratic real system: constrain each wire by z(z−1)=0, use z=xy for AND and z=1−x for NOT, and force output 1. |
| ∃ℝ ⊆ PSPACE | [Canny’s original report abstract](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1988/6041.html) states the real existential decision upper bound. Polynomial binary reductions preserve PSPACE. |
| UniformNC1 ⊆ L | The uniform inclusion is recorded in [Greenlaw–Hoover–Ruzzo, Appendix D](https://homes.cs.washington.edu/~ruzzo/papers/limits.pdf). A logarithmic-depth alternating tree can be traversed using a logarithmic path description and recomputation. |
| UniformNC1 ⊆ NC1 | Forget U_E uniformity. |
| UniformNC1 ⊄ AC0 | Uniform balanced XOR trees compute PARITY; the existing Furst–Saxe–Sipser lower bound excludes even nonuniform AC0. |

The L ⊆ UL ⊆ NL row represents two primitive facts; the total is 13. PARITY’s XOR gates can be replaced by constant-size AND/OR/NOT gadgets without changing logarithmic depth or standard uniformity. That seed is necessary: the older L ⊄ AC0 fact alone would not establish a lower bound for a subclass of L.

BPL, PL and UniformNC1 are self-complementary. For BPL, exchange the halting answers. For PL, if integer GapL gap g defines membership by g>0, use 1−g for the complement; this handles the tie correctly. For ALOGTIME, dualize existential and universal states and exchange terminal answers. **No self-complement identity is proposed for UL or ∃ℝ.**

## Conditional rules

The eight added rules extend the existing length-regular padding scheme to C∈{BPL, UL, PL, ∃ℝ}:

- E ⊆ C implies EXP ⊆ C.
- NE ⊆ C implies NEXP ⊆ C.

For each language in EXP or NEXP, pad to a suitable fixed polynomial length so that the padded language lies in E or NE. The inverse simulation accesses the padded input virtually. For BPL it retains fresh coins; for UL it introduces no nondeterministic choices; for PL it preserves path counts; for ∃ℝ it is ordinary composition of polynomial-time reductions. Polynomial clocks remain polynomial and logarithmic workspace changes by a constant factor.

The first six premises are already false through the P upper bounds, so these rules mainly preserve the uniform treatment of background nodes. The ∃ℝ rules can have substantive consequences. **UniformNC1 is excluded from this generic extension:** the precise U_E behavior of the chosen padding map deserves a separate proof. Its E/NE premises are already false, so excluding the redundant rule loses no current classification.

Other useful implications require no new rule. For example, P ⊆ PL entails P ⊆ NC, which activates the existing EXP ⊆ PSPACE padding consequence. The analogous NP premise gives NEXP ⊆ PSPACE. Similarly, a collapse of PL to BPL gives PL ⊆ SC by transitivity.

[Ogihara’s PL hierarchy theorem](https://eccc.weizmann.ac.il/report/1996/013/download/) was checked, but no oracle endpoint was introduced. It uses Ruzzo–Simon–Tompa relativization, including restrictions on query formation. It is not permission to replace arbitrary oracle computation or to identify all determinant-output bits with PL.

## Incident-pair coverage

Every direction is listed individually in JSON. The groups partition the 585 pairs; a pair with two focus endpoints is counted in the final row.

| Other endpoint family | Pairs | Inclusion | Noninclusion | Candidate |
|---|---:|---:|---:|---:|
| Nonuniform circuits and advice | 60 | 9 | 35 | 16 |
| Other space and parallel classes | 60 | 24 | 0 | 36 |
| Counting | 120 | 50 | 0 | 70 |
| Polynomial time, randomness and proofs | 190 | 81 | 0 | 109 |
| Quantum | 70 | 28 | 0 | 42 |
| Larger time and space | 60 | 28 | 25 | 7 |
| The five new endpoints internally | 25 | 14 | 0 | 11 |
| **Total** | **585** | **234** | **60** | **291** |

The nonuniform checks are consequential. All five new endpoints lie in PSPACE and contain only recursive languages. Each of AC0, ACC0, TC0, NC1, P/poly and NP/poly contains arbitrary unary languages. The existing AC0 ⊄ PSPACE seed therefore excludes all 30 incoming nonuniform directions. This is why nonuniform NC1 ⊆ UniformNC1 is already false, whereas L ⊆ UniformNC1 remains a substantial question.

The four small-resource additions lie in P. Their outward inclusions into the polynomial-time counting, probabilistic and proof classes mostly follow from that fact. Their placement in uniform NC also lets the existing PSPACE separation propagate. These arguments do **not** put ∃ℝ into a counting class or settle EXP/NEXP versus ∃ℝ. The seven surviving larger-resource directions are E, EXP, NE, NEXP or PSPACE ⊆ ∃ℝ, and ∃ℝ ⊆ E or NE.

The quantum/counting overlay is listed explicitly in JSON and remains owned by the corresponding reviewers. In particular, it uses BPL ⊆ BQL ⊆ PL, QMA ⊆ QMA(2) ⊆ NEXP, the StoqMA and QSZK bounds, and PP/PH ⊆ PSharpP ⊆ CH ⊆ PSPACE. The full merged conditional theory may resolve additional pairs; these counts must not be frozen before that recomputation.

## Difficult interfaces and recent-paper triage

Several unresolved interfaces deserve independent review because a mistaken transfer would resolve many pairs at once:

- **PL, LogCFL and SC.** The NC² simulation does not supply SC’s simultaneous time and space bounds. [Datta and Gupta, p.6](https://eccc.weizmann.ac.il/report/2022/147/revision/2/download) explicitly distinguish LogDCFL from LogCFL and record that UL and LogCFL are not known to lie in SC.
- **BPL and nondeterministic/semibounded space.** [Cheng and Wang’s 2024 theorem](https://eccc.weizmann.ac.il/report/2024/048/download) puts BPL in logspace-uniform AC¹. Both gate types have unbounded fan-in; this is not LogCFL’s SAC¹ characterization. Their introduction also warns that L=NL is not known to imply L=BPL.
- **Real feasibility and counting.** PosSLP and sum-of-square-roots membership in CH concerns particular problems. It does not give ∃ℝ ⊆ CH or ∃ℝ ⊆ PSharpP. [The 2024 compendium](https://arxiv.org/html/2407.18006v1) treats ∃ℝ’s placement relative to the polynomial hierarchy as unresolved. Complex Hilbert Nullstellensatz bounds are not interchangeable with real feasibility.
- **Real and quantum witnesses.** A polynomial-qubit witness has exponentially many amplitudes; writing them as real variables is not a polynomial-size ∃ℝ reduction. A real solution likewise does not automatically give a bounded-error quantum verification procedure.

Recent primary publications were screened for changes to these statements. [Stade’s May 2026 result, Theorem 2](https://arxiv.org/html/2605.23517v1), proves ∃ℝ-hardness of approximating a real constraint problem. Its real-alphabet assignment tests do not provide ordinary binary NP/MA verifiers. [Meer and Wurm’s 2025 structural results](https://arxiv.org/html/2502.00680v1) concern relativization and conditional intermediate problems, not an ordinary NP/∃ℝ separation.

[Apers and Edenhofer, CCC 2025](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.18), provide a total-language quantum-space candidate and a StrongFewL simulation. Their stronger path condition does not prove UL ⊆ BQL. [Arvind, Chakraborty and Datta’s February 2026 revision](https://arxiv.org/abs/2512.09374v3) uses catalytic memory and a UL oracle for its NL simulation; it does not prove NL ⊆ UL.

[Pyne and Tell’s April 2026 survey](https://eccc.weizmann.ac.il/report/2026/045/download/) checks the current hardness-versus-randomness context. Its quantitative, catalytic and infinitely-often results do not establish BPL=L or NL=UL for the selected endpoints. In particular, replacing a specified exponential circuit-hardness hypothesis by a bare E ⊄ P/poly statement would strengthen the theorem without justification.

## What this review does not certify

The searches and primary statements support the proposed seeds and identify the main transfer hazards. They do not prove that an unlisted result is absent from the entire pre-cutoff literature. Live Complexity Zoo pages often failed; BPL/PL discovery mirrors were checked, and primary papers supplied the actual evidence. Missing mirror entries are not evidence of openness.

The next review should check the canonical machine encodings against these conventions and independently inspect PL/LogCFL/SC, U_E uniformity and ∃ℝ/counting interfaces. No calibrated expected-error estimate or blanket historical certificate is attached to this extension. Existing proofs may remain trusted under the user’s source waiver; their statements and model hypotheses still have to match the admitted propositions.
