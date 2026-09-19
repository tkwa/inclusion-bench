# Counting and quantum rules: independent cross-review

All 21 proposed rules survive review. The two held rules can also be admitted with the explicit arguments below. The [JSON dossier](audit-round2-cross-counting.json) gives a separate verdict, precise source locator, oracle-scope check and normalized conclusion for every rule. Its preferred integration list has 22 rules and 36 conclusions: it combines the two CeqP-to-parity consequences and removes a reflexive conclusion.

This review binds the round-one dossier and the inspected file hashes. The working dataset at replay was `03a20575c82bab512158a0bb0bb7766c4066b5c8ecc645c012d16053ad1714e2`. Adding the recommended rules to structural/Horn closure caused no contradiction and no new unconditional labels: the matrix remained **709 inclusions, 413 noninclusions and 1,378 candidates**. The parent’s complete SAT audit is a separate check.

## Rule decisions

Every row is accepted. “Expanded” means the original conclusion is valid and the review supplies more consequences. CeqP denotes C₌P; arrows inside the right column denote implications between containment statements.

| Premise | Accepted consequence | Review note |
| --- | --- | --- |
| PP ⊆ QMA | PH ⊆ PP | Vyalyi Corollary 1; baseline QMA ⊆ PP supplies equality. |
| PP ⊆ CeqP | PH ⊆ PP | Equality with PP also identifies coCeqP with PP. |
| CeqP ⊆ AWPP | PH, PP, parityP ⊆ AWPP | Expanded by exact-count simulation D1. |
| CeqP ⊆ WPP | PH, PP, parityP ⊆ WPP | Expanded by D1 and the stated UP-oracle closure. |
| CeqP ⊆ UP | PH, PP, parityP ⊆ UP | OH Theorem 3.2 explicitly includes these equalities. |
| CeqP ⊆ LWPP | PH, PP, parityP ⊆ LWPP | Exact-counting lowness and ordinary Turing closure suffice. |
| CeqP ⊆ parityP | PP ⊆ parityP | Previously held; D1 discharges it. |
| CeqP ⊆ coNP | PH ⊆ Σ₂P | Replace only the oracle in UP^CeqP. |
| NP ⊆ SPP | Δ₂P ⊆ SPP | Ordinary polynomial-time oracle closure. |
| NP ⊆ LWPP | Δ₂P ⊆ LWPP | Same; original FFK passage verified. |
| NP ⊆ AWPP | Δ₂P ⊆ AWPP | Follows from UP^AWPP ⊆ AWPP. |
| NP ⊆ BQP | Δ₂P ⊆ BQP | Amplify each classical adaptive subroutine call. |
| NP ⊆ parityP | Δ₂P ⊆ parityP | Parity oracle closure. |
| NP ⊆ WPP | Θ₂P ⊆ WPP | Truth-table closure, without a Turing-closure claim. |
| parityP ⊆ BPP | PH ⊆ BPP | Compose Toda’s randomized reduction with amplified BPP. |
| parityP ⊆ BQP | PH ⊆ BQP | Same composition with a quantum subroutine. |
| PP ⊆ AWPP | PH, parityP ⊆ AWPP | Transport P^PP through the oracle inclusion. |
| PP ⊆ BQP | PH, parityP ⊆ BQP | Same, with error amplification. |
| PP ⊆ parityP | PH ⊆ parityP | Delete the redundant parityP ⊆ parityP conclusion. |
| PP ⊆ SPP | PH, parityP ⊆ SPP | Ordinary polynomial-time oracle closure. |
| PP ⊆ LWPP | PH, parityP ⊆ LWPP | Ordinary polynomial-time oracle closure. |
| CeqP ⊆ QMA | PH, parityP ⊆ PP | Previously held; D2 discharges it and adds the parity endpoint. |
| CeqP ⊆ parityP | PH ⊆ parityP | Valid; combine with the seventh row for integration. |

The central primary passages were checked directly. STT’s printed manuscript pp. 22–24 give PH ⊆ UP^CeqP, UP^AWPP ⊆ AWPP, WPP truth-table closure, and UP^WPP ⊆ coCeqP. The PDF’s text mapping is corrupted, so the formulas were read from rendered pages. Its journal publication date is July 2005. [Spakowski–Thakur–Tripathi manuscript](https://urresearch.rochester.edu/fileDownloadForInstitutionalItem.action?itemFileId=464&itemId=374), [publisher metadata](https://www.sciencedirect.com/science/article/pii/S0890540105000210)

## The LWPP and WPP distinctions

The LWPP collapse uses this chain:

`PP ⊆ C=·CeqP ⊆ CeqP^CeqP ⊆ CeqP^LWPP = CeqP ⊆ LWPP`.

The first two steps are unconditional operator facts; the premise changes only the oracle in the third step. LWPP lowness for CeqP supplies the equality. Then PH and parityP belong to P^PP ⊆ P^LWPP = LWPP. OH Proposition 2.6(6) and 2.7(2) give the operator steps. [Ogiwara–Hemachandra, printed pp. 7–8](https://urresearch.rochester.edu/fileDownloadForInstitutionalItem.action?itemFileId=7017&itemId=4661)

The original FFK manuscript explicitly gives SPP Turing closure in Corollary 5.8, p. 17. Its discussion after Definition 5.13, p. 19, gives both LWPP lowness for CeqP and SPP^LWPP = LWPP, hence ordinary Turing closure. The same passage carefully distinguishes these from LWPP^LWPP, because an oracle-dependent FP normalizer changes the relativized definition. This review preserves that distinction. [Fenner–Fortnow–Kurtz](https://cse.sc.edu/~fenner/papers/gaps.pdf)

For WPP, only the published truth-table closure is used for NP ⊆ WPP. The CeqP ⊆ WPP rule uses the separate UP^WPP ⊆ coCeqP theorem. Under its premise, WPP = CeqP, and WPP complement closure then gives coCeqP = WPP. Neither argument assumes unrestricted WPP Turing closure.

## D1: an exact-count certificate

The construction proving PH ⊆ UP^CeqP works for every language in P^#P[1]. It therefore covers PP and parityP as well.

Write the computation as a #P function F(x), followed by a polynomial-time acceptance test b(x,j) on the returned count. Choose a polynomial w with **F(x) < 2^w(|x|)**. Guess exactly w bits for j, ask whether F(x) = j, and accept iff equality holds and b(x,j) = 1. The equality language is in CeqP. Invalid pair encodings can be rejected using a constant nonzero gap. Every integer has one fixed-width representation, so at most one branch survives. Choosing a strict count bound includes the largest possible count without an off-by-one error.

The machine need only be unambiguous with its actual oracle. That is precisely STT Definition 5.2; unambiguity under every possible replacement oracle is unnecessary. A containment CeqP ⊆ C means the same equality language belongs to C, so its answers stay unchanged.

For C = parityP, use the unconditional, relativizing inclusion UP ⊆ parityP and parityP^parityP = parityP. This discharges the held PP consequence without relativizing the hypothetical premise. For C = AWPP, use UP^AWPP ⊆ AWPP. For C = WPP, use the equality argument in the preceding section. These establish the expanded PH, PP and parityP conclusions.

The PP and parityP endpoints are derived here; STT Theorem 5.1 states the PH endpoint. The strong one-#P-query Toda form is used explicitly in that proof. Parity self-lowness is also recorded in OH Proposition 2.7(3). Ordinary Toda containment and the randomized parity operator appear directly in the [publisher abstract](https://epubs.siam.org/doi/10.1137/0220053).

## D2: CeqP inside QMA is enough

Vyalyi proves QMA ⊆ A0PP and gives a power-of-two, length-dependent threshold characterization of A0PP. Corollary 1 states the PH collapse under QMA = PP. The proof of Theorem 2 uses its stronger hypothesis only for an exact-count test, which permits the following weaker premise. [Vyalyi, Theorem 1, Lemma 3 and Theorem 2 proof, printed pp. 4–8](https://eccc.weizmann.ac.il/report/2003/021/download/)

Assume CeqP ⊆ QMA and take L ∈ PH. Use D1’s F, w, b and exact-count language A. Encode each query (x,j) so that its length ℓ depends only on |x| and w(|x|), with ℓ ≥ w. Thus all guessed counts on one input share the same threshold.

Since A ∈ QMA ⊆ A0PP, obtain a GapP function h₀ and a polynomial p such that a yes query z satisfies h₀(z) > 2^p(|z|), while a no query satisfies 0 ≤ h₀(z) < 2^(p(|z|)−1). Raise h₀ to the polynomial power k(|z|) = |z| + 2. Set h = h₀^k and S = 2^(pk). Then yes queries have h > S; no queries have 0 ≤ h < 2^−k S.

Now form the GapP sum

`H(x) = Σ[j has w(|x|) bits] b(x,j) · h(encode(x,j))`.

If x ∈ L, its correct count contributes more than S, and every other contribution is nonnegative. If x ∉ L, the correct count is omitted and every included term is a wrong guess. Their total is less than `2^w · 2^−(ℓ+2) S ≤ S/4`. Therefore H−S is positive exactly on L, placing L in PP. The common encoding length, nonnegativity and fixed-width guesses are all necessary parts of the argument.

The same construction applies to a parityP language, whose answer is obtained by taking the parity of one #P value. Therefore the premise also gives parityP ⊆ PP.

This is an explicit adaptation, not a claim that Vyalyi’s corollary states CeqP ⊆ QMA. Marriott–Watrous supplies independent primary support for QMA ⊆ A0PP in Remark 3.5. [Quantum Arthur–Merlin Games, printed p. 14](https://arxiv.org/pdf/cs/0506068)

## Semantic and cutoff checks

The audit also checked 23 relevant existing inclusion seeds and the concrete counting, transducer and quantum definitions. No class-changing discrepancy was found. Counts retain path multiplicity; UP is globally unambiguous; CeqP tests zero; PP tests positivity. The AWPP quantifiers and global numerator bounds agree with the power-of-two definition. WPP/LWPP use genuine total FP transducers. Signed nonzero normalizers agree with the original definition and can be made positive by multiplying both gap and normalizer by the normalizer. [FFKL, Definitions 2.2–2.3 and 6.1, Lemma 6.3](https://lance.fortnow.com/papers/files/obt.pdf)

Quantum families have a concrete polynomial-time generator, standard finite gates, disjoint registers and normalized witnesses. Pure QMA witnesses suffice because mixed-state acceptance is a convex combination. Dephasing a QCMA witness can be implemented by copying its basis bits to unused ancillas. The total-language gap holds on every input, as required by the oracle substitutions. General model-equivalence and amplification theorems remain trusted mathematical inputs, not new Lean proofs produced by this audit.

All inputs precede the cutoff. Ivanashev’s corroborating version 5 is explicitly dated August 2, 2026; none of these rules relies on that preprint alone. Its recalled CeqP = coNP collapse agrees with the older oracle derivation. [Version 5, Theorem 2.4 proof](https://arxiv.org/html/2507.04110v5)

The most useful remaining check is a second independent reconstruction of D1 and D2, followed by the full SAT replay. The dossier supplies conservative subjective risk ranges for prioritization, not a calibrated expected pair-error bound. This bounded cross-review does not establish the global “fewer than two incorrect classifications” stopping criterion. Future flaws in currently accepted proofs are excluded from its risk accounting.
