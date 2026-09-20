# Independent review of the v0.4.0 classical baseline

**Decision:** accept the 13 primitive facts, eight regular-padding rules and three complement identities in [classical-new-baseline.json](classical-new-baseline.json). Add the two conditional circuit rules below. This review found no additional unconditional classification among the 585 incident pairs. It is an AI-assisted statement-and-model review, not human certification or a proof that the literature contains no omitted result.

The reviewed JSON has SHA-256 `0da4aadde59b2d89153c65078c453d313eb260c83388aabff93859244546d2c8`. Its own overlay, including its listed counting/quantum inputs, reproduces **234 inclusions, 60 noninclusions and 291 candidates**, with zero mismatches across all 585 distinct pairs. Adding the two rules below changes zero unconditional labels in that overlay. The accompanying [supplement](classical-baseline-cross-review.json) has `facts: []`, two importable `rules`, and new source records; it does not replace or modify the original dossier.

The five focus endpoints are BPL, UL, PL, ∃ℝ and UniformNC1. The context has 61 nodes, including background nodes; the scored roster is a separate selection. The literature cutoff remains September 1, 2026. A paper’s later indexing date is not its discovery date, and post-cutoff revisions are not evidence for an earlier classification.

## Primitive statements

| Original seed | Verdict and independent check |
|---|---|
| L ⊆ BPL | Accept. A halting deterministic logspace machine ignores its fair coins. The containment is also displayed in Le Gall–Nishimura–Yakaryılmaz §2.3. |
| BPL ⊆ BPP | Accept. Dropping the space restriction preserves the same polynomial clock and bounded-error guarantee. |
| BPL ⊆ SC | Accept. Nisan’s original institutional abstract explicitly gives polynomial time and O(log² n) workspace simultaneously, for two-sided error. The historical title “RL” is not a reason to weaken this to one-sided error. |
| BPL ⊆ PL | Accept. The 2/3-versus-1/3 gap meets the strict-majority predicate with the same resources. This inclusion also has a direct proof in the new core library. |
| L ⊆ UL | Accept. Deterministic computation supplies one accepting path on members and none otherwise; unique paths refer to computation choices, not just reached configurations. |
| UL ⊆ NL | Accept. Forgetting the at-most-one condition leaves a nondeterministic logspace decision procedure. |
| NL ⊆ PL | Accept. A clocked NL accepting-path count is a #L function; its difference from zero is a GapL function whose positivity decides the language. Allender–Ogihara Proposition 3 supplies the fair-coin PL bridge. |
| PL ⊆ NC | Accept. Borodin–Cook–Pippenger Corollary 6.3 gives NC², and their §2 explicitly specifies logspace uniformity. This matches the benchmark’s NC endpoint. |
| NP ⊆ ∃ℝ | Accept. The Boolean circuit satisfiability encoding uses real variables constrained to {0,1}, quadratic AND equations, linear NOT equations and an output constraint. Its finite description is polynomial in the Boolean circuit size. |
| ∃ℝ ⊆ PSPACE | Accept. Canny’s institution-hosted original report states the real existential upper bound. Composition with the benchmark’s polynomial-time binary reductions preserves polynomial space. |
| UniformNC1 ⊆ L | Accept. Use U_E/ALOGTIME, then enumerate the bounded alternating computation tree while keeping an O(log n)-bit branch description and recomputing its configuration. No nonuniform circuit description must be computed in logspace. |
| UniformNC1 ⊆ NC1 | Accept. Forget the standard circuit uniformity condition. The right endpoint remains nonuniform. |
| UniformNC1 ⊄ AC0 | Accept. PARITY has standard-uniform logarithmic-depth bounded-fan-in circuits, and the existing nonuniform AC0 lower bound applies to that language. A lower bound for L alone would not justify this smaller left endpoint. |

The principal primary anchors checked were [Nisan, abstract](https://cris.huji.ac.il/en/publications/rl-sc-2/), [Allender–Ogihara, Propositions 2–3 and Theorem 6](https://www.numdam.org/item/ITA_1996__30_1_1_0.pdf), [Borodin–Cook–Pippenger, §2 and Corollary 6.3](https://www.cs.toronto.edu/~bor/Papers/parallel-computation-well-endowed-rings.pdf), [Reinhardt–Allender, §2](https://people.cs.rutgers.edu/~allender/papers/nlul.pdf), [Canny’s report abstract](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1988/6041.html), and [Meer–Wurm, Definition 1](https://arxiv.org/html/2502.00680v1). Nisan and Canny were checked at the original abstract level; this review does not claim to have reconstructed those deep proofs.

## Clock, complement and padding checks

BPL needs a polynomial worst-case clock on every coin sequence. An almost-surely halting process can define a different class. Likewise, a space-only simulation does not establish SC: its time and space bounds must hold for the same algorithm. [Le Gall–Nishimura–Yakaryılmaz, §§2.1–2.3](https://arxiv.org/pdf/2105.02681) distinguish the polynomial-time and unrestricted-time versions and explicitly display BPL ⊆ BQL ⊆ PL. Their postselection theorem does not give PL ⊆ BQL.

The three proposed complement identities are valid. BPL swaps binary terminal answers. PL requires the integer-gap transformation g ↦ 1−g; simply negating g mishandles inputs with gap zero. ALOGTIME dualizes universal/existential choices and terminal answers. There is no proposed complement identity for UL or ∃ℝ.

All eight padding rules are valid for C ∈ {BPL, UL, PL, ∃ℝ}:

- E ⊆ C implies EXP ⊆ C.
- NE ⊆ C implies NEXP ⊆ C.

Fix a language’s exponent and pad an n-bit input to a fixed polynomial length m(n), using a delimiter and zero suffix. The padded language belongs to E or NE. To simulate its C machine on the unpadded input, compute each requested padding bit using logarithmic workspace; log m(n)=O(log n), and any fixed polynomial clock in m(n) remains polynomial in n.

For BPL, deterministic work between simulated random transitions leaves the probability distribution unchanged. Extra ignored coin positions in the explicit fair-machine implementation do not create extra statistical power. For UL, each auxiliary step is deterministic, so accepting-path multiplicity is preserved. For PL, either use the same probability-preserving simulation or compose both #L functions defining a GapL function. This refines the original dossier’s shorthand “preserves path counts”: a padded fair-coin execution may duplicate equally weighted coin strings; raw fair-coin counts need not stay numerically equal. ∃ℝ uses composition of ordinary polynomial-time reductions.

No extra UniformNC1 padding rule is required here. Its E/NE premises are already refuted through the existing P upper bound; extending arbitrary low-level uniformity templates without a proof would add risk without changing those baseline decisions.

## Two additional circuit consequences

For each **C ∈ {ACC0, TC0}**, where C is nonuniform, add:

> **UniformNC1 ⊆ C ⇒ NC1 ⊆ C.**

This is a derived implication, not a claim that a source states the exact benchmark identifiers. The derivation uses the variable-free Boolean formula value language BFV and the closure of the two target circuit models under restrictions.

1. Fix an ordinary parenthesized formula syntax over seven symbols and an equal-width three-bit code, with `0` and `1` differing in one bit. BFV accepts exactly the well-formed formulas evaluating to true. [Buss’s original paper, Main Theorem 1 and §2, pp.3–5](https://mathweb.ucsd.edu/~sbuss/ResearchWeb/Boolean/paper.pdf), places this finite-alphabet problem in ALOGTIME and explicitly discusses fixed-width binary coding. Its random-access multitape convention agrees with the intended UniformNC1 model.
2. Take any language A in the existing **nonuniform** NC1. Unfold each depth-O(log n), bounded-fan-in circuit into a formula F_n of polynomial size. There is no requirement that a uniform algorithm print F_n.
3. Substitute each leaf variable of F_n with its input value. The resulting variable-free formula has length m(n)=poly(n), independent of the values of the input bits. Its encoded string is a projection: every bit is a fixed syntax bit or one input bit. The truth value is A(x).
4. Under the premise, BFV has a C circuit at each binary input length. Choose its m(n)-bit circuit and hardwire the syntax bits, identifying repeated variable positions. The result decides A on n-bit inputs. Its size remains polynomial in n; its depth remains constant. For ACC0, no new modulus is introduced. TC0 permits the same constant restrictions and wire identifications.

Thus A belongs to C. Hardwiring a nonuniform formula is legitimate because the conclusion is nonuniform. This argument does not convert a direct-connection U_D condition into extended-connection U_E uniformity. [Behle–Krebs–Lange–McKenzie, Remark 1](https://eccc.weizmann.ac.il/report/2011/095/revision/1/download/) explicitly distinguishes the two. Buss also warns on p.18 that a pointer-table representation of formulas changes the evaluation problem; that representation is not used here.

The reverse implications follow from UniformNC1 ⊆ NC1. Consequently the two respective containments are equivalent, even though nonuniform NC1 ⊆ UniformNC1 is false in this catalog. The closure engine’s valid contraposition then also transfers NC1 ⊄ C to UniformNC1 ⊄ C if a future proof establishes it.

## Adversarial interface review

The pair groups reproduce the original partition. They are family-level reviews of all listed directions, not 585 separate literature searches.

| Family outside the five focus nodes | Pairs | Inclusion | Noninclusion | Candidate |
|---|---:|---:|---:|---:|
| Nonuniform circuits/advice | 60 | 9 | 35 | 16 |
| Other space/parallel classes | 60 | 24 | 0 | 36 |
| Counting | 120 | 50 | 0 | 70 |
| Polynomial-time/randomness/proofs | 190 | 81 | 0 | 109 |
| Quantum | 70 | 28 | 0 | 42 |
| Larger resources | 60 | 28 | 25 | 7 |
| Internal to the five nodes | 25 | 14 | 0 | 11 |
| **Total** | **585** | **234** | **60** | **291** |

**PL, SC and LogCFL.** The NC² upper bound gives a parallel algorithm, not simultaneous polynomial time and polylogarithmic sequential space. Determinant’s full output-bit class is not identified with PL. The PL oracle-hierarchy result uses the Ruzzo–Simon–Tompa query convention; arbitrary oracle substitutions are invalid. [Datta–Gupta, p.6](https://eccc.weizmann.ac.il/report/2022/147/revision/2/download) separates LogDCFL from LogCFL and records the SC uncertainties. [Cheng–Wang’s BPL ⊆ L-AC¹ theorem](https://eccc.weizmann.ac.il/report/2024/048/download) does not give LogCFL: AC¹ allows both kinds of unbounded-fan-in gate, unlike SAC¹. These checks support retaining the relevant candidates; they do not prove historical openness.

**UL, BPL and BQL.** The new quantum simulation of strong fewness cannot be applied to ordinary UL solely from uniqueness of accepting paths. Reinhardt–Allender’s NL/poly result retains its advice. Polynomial-time BQL must also be distinguished from its unrestricted-time or postselected variants. No source checked justifies UL ⊆ BPL/BQL or BPL ⊆ UL.

**∃ℝ versus counting and proof systems.** The [2024 compendium, §1.2](https://arxiv.org/html/2407.18006v1) concerns finite-bit inputs and genuine real witnesses. Its counting-hierarchy bounds for PosSLP and sum of square roots apply to particular problems, not all of ∃ℝ. The relation NP^PosSLP=∃ℝ is a conjecture there. A complex-feasibility AM theorem does not establish the corresponding real-feasibility theorem. A polynomial-qubit witness likewise cannot be expanded into exponentially many amplitude variables inside a polynomial-size reduction. No such transfer is imported.

**Nonuniform and large-resource directions.** All five focus classes are contained in PSPACE. Arbitrary unary languages already occur in nonuniform AC0, so none of the six nonuniform/advice nodes is contained in a focus class. Conversely, PARITY gives the five outgoing AC0 exclusions. The four small-resource additions lie in P; their inclusions in UP/coUP and other polynomial-time supersets are therefore already known. The seven larger-resource candidates all involve ∃ℝ. None is removed merely by its PSPACE upper bound.

## Additional pre-cutoff checks

These checks extend the original recent-paper triage. “No new label” means that the stated result does not yield one under the reviewed transfer; it is not a statistical bound on omissions.

| Source, pinned version | What was checked | Outcome for this baseline |
|---|---|---|
| [Applebaum, TR26-131 revision 1, August 10, 2026](https://eccc.weizmann.ac.il/report/2026/131/revision/1/download/) | Theorem 1 and §§2.1–2.5: uniform NL ⊆ Mod_pL, including parity logspace. | Genuine new progress outside the context vocabulary. NL ⊆ parityP is already implied through P. Modular counts do not supply unique accepting paths or a BQL/SC simulation. |
| [Hoza, TR26-124, July 2026](https://eccc.weizmann.ac.il/report/2026/124/) | Author abstract: lower bound for deterministic **oblivious** min-isolating weights. | Excludes a method of obtaining NL=UL; does not prove NL≠UL. Full PDF retrieval failed, so this is abstract-level triage. |
| [Cohen–Doron–Goldgraber, TR26-123, July 2026](https://eccc.weizmann.ac.il/report/2026/123/) | Author abstract: PRG for permutation read-once branching programs. | Restricted test family and seed bound; no general BPL=L conclusion. Full PDF retrieval failed. |
| [Asadi–Cleve, TR26-044 revision 1, April 7, 2026](https://eccc.weizmann.ac.il/report/2026/044/) | Authors’ withdrawal notice. | The claimed polynomial-time TreeEval bound was withdrawn before the cutoff. It supplies no SC result. |
| [Chakraborty et al., TR26-080 revision 1, June 1, 2026](https://eccc.weizmann.ac.il/report/2026/080/revision/1/download/) | Introduction and Theorems 1.1–1.4: matching/rank algorithms with catalytic memory. | The extra catalytic tape is essential to the stated model; no ordinary L/UL/BPL containment follows. |
| [Bläser–Dutta–Okyay, arXiv:2606.16744v1, June 15, 2026](https://arxiv.org/html/2606.16744v1) | Theorem 4.2 and §8/Corollary 8.5. | Invertible-matrix constraints have an RP algorithm; determinant-one constraints give a different ∃ℝ-complete problem. These statements do not combine into ∃ℝ ⊆ RP. |
| [Stade, arXiv:2605.23517v1, May 22, 2026](https://arxiv.org/html/2605.23517v1) | Theorem 2 and the explicit real-RAM interpretation. | The proof symbols and verifier operations are over reals. This is not an ordinary binary MA/NP/QMA upper bound. |
| [Pyne–Tell, TR26-045, March/April 2026](https://eccc.weizmann.ac.il/report/2026/045/download/) | Theorems 1.2, 3.5–3.6 and 3.9–3.11. | Simultaneous bounds, quantitative hardness, infinitely-often guarantees and input-dependent alternatives are retained. None is replaced by a bare catalog separation or unconditional collapse. |

The live 2026 ECCC index was used to find the July/August papers and the withdrawal, with source versions checked individually against the cutoff. This was a targeted title/abstract sweep, not a complete conference census. Search failures were not converted to “known open” evidence.

## Remaining obligations

The integrated baseline must be recomputed after all independent dossiers are imported. This report binds the original overlay, not a later merged dataset. The conditional hardwiring results are mathematical derivations supported by pre-cutoff ingredients; they are not new kernel-checked circuit-simulation theorems.

The canonical operational definitions need the separate semantic review already assigned to another agent. I authored the new classical models, so this report does not count as an independent review of my own implementation. Textbook equivalences for fair coins/GapL, U_E/ALOGTIME and real encodings remain trusted bridges under the user’s waiver, with their exact hypotheses still subject to review.

The largest residual omission families remain PL/SC/LogCFL, ordinary unambiguity versus bounded-error space, and ∃ℝ versus counting/proof systems. The source checks above reduce specific transfer risks without turning a finite search into an exhaustive historical theorem. No independence-from-ZFC conclusion is inferred from any unresolved entry.
