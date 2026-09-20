# Independent review of the counting extension

**Conclusion:** the five primitive facts, nine conditional rules, and two complement declarations in `counting-new-baseline.json` are sound for the stated standard classes. Two additional rules are supported: **PP ⊆ MA ⇒ CH ⊆ MA** and **PP ⊆ ⊕P ⇒ CH ⊆ ⊕P**. No additional unconditional primitive relation was identified. This is an AI-assisted review, recorded September20,2026, against the September1,2026 cutoff; it is not human expert certification or a proof that every remaining comparison was historically open.

The [machine-readable report](counting-cross-review.json) binds the reviewed input files by SHA-256, supplies importable sources and rules, and enumerates all **240 ordered pairs** incident to PSharpP or CH in the61-node context. Its explicit overlay produces99 known inclusions,16 known noninclusions, and125 unresolved candidates. Those counts must be regenerated after the full quantum dossier is imported.

## Definitions and unconditional relations

PSharpP denotes the total decision class **P^PP**, equivalently decision P^#P. It is neither the function class #P nor the total search class PPP. CH is the union of a **fixed finite number of counting levels per language**; it does not permit the number of levels to grow with the input.

The admitted chain PP ⊆ PSharpP ⊆ CH ⊆ PSPACE is correct. A single PP oracle query gives the first inclusion. Deterministic polynomial time with a PP oracle is a special case of the second counting level. Polynomial space can evaluate each fixed-level computation by recursively enumerating its branches and oracle computations. PH ⊆ PSharpP is Toda’s theorem. For ⊕P ⊆ PSharpP, recover the polynomial-bit accepting-path count using PP threshold queries, then inspect its parity.

Both classes are closed under complement. Deterministic oracle machines swap their answers; each fixed PP-oracle level admits the usual relativized PP complement argument. These are trusted literature bridges to the intended models, not claims that their machine transformations have already been proved in Lean.

## Conditional checks and additional rules

**Small circuits.** [Bürgisser2006, Definition2.3, equation(3), and Lemma2.5](https://eccc.weizmann.ac.il/report/2006/113/download/) give the fixed-level hierarchy and explicitly establish PP ⊆ P/poly ⇒ CH ⊆ P/poly. The premise is not relativized to an arbitrary oracle.

The stronger conclusion CH ⊆ MA is also justified. PP circuits permit reconstruction of every #P output bit using polynomially many threshold queries. Advice for all query lengths up to a polynomial bound can be combined into one polynomial-size circuit family. [Fournier–Perifel–deVerclos, author version dated April11,2014, Lemma3, printed p.12](https://webusers.imj-prg.fr/~herve.fournier/publications/vnp.pdf), then gives CH=MA. Its proof uses the permanent protocol and strengthened Toda theorem. This lemma does **not** assume GRH, even though other results in that paper do.

**AWPP.** The unconditional lowness theorem PP^AWPP=PP makes PP ⊆ AWPP ⇒ CH ⊆ PP valid. If a fixed level lies in PP, the premise puts its oracle languages in AWPP, and the lowness theorem collapses the next level. This replaces the oracle class only; it does not assert that an unrelativized inclusion can be applied to the outer oracle machine. The root source, Fortnow–Rogers Theorem3.3, is corroborated by [Fenner’s primary treatment of PP-lowness](https://eccc.weizmann.ac.il/report/2002/036/download/).

**PH.** PP ⊆ PH ⇒ CH ⊆ PH needs the strengthened theorem **PP^PH ⊆ P^PP**, not just PH ⊆ P^PP. [Allender–Wagner, §1, final theorem and proof, PDF p.5](https://people.cs.rutgers.edu/~allender/papers/column40.pdf), states the needed version. Under the premise, P^PP ⊆ P^PH ⊆ PH: each oracle language occupies one fixed PH level. An induction now keeps every counting level inside PH.

**MA — additional rule.** MA ⊆ PP is unconditional, so PP ⊆ MA implies equality. [Vinkhuijzen–Deutz2019, §7, Theorem20, printed p.9](https://eccc.weizmann.ac.il/report/2019/131/download/), explicitly states that MA=PP implies MA=CH. One way to unpack the argument is to use amplified MA certificates for a deterministic query transcript, giving P^(MA∩coMA) ⊆ MA. The hypothesis makes PP=MA=coMA, hence P^PP ⊆ MA. Since MA ⊆ PH, strengthened Toda then keeps each next counting level inside MA. The publication metadata is September30,2019; the report was submitted September11.

**Parity — additional rule.** The last proof in the Allender–Wagner source also uses **PP^⊕P ⊆ P^PP**. Together with P^⊕P=⊕P, established in the Ogiwara–Hemachandra closure source already in the baseline, this yields the stronger rule. Under PP ⊆ ⊕P, first P^PP ⊆ ⊕P. If the kth counting level lies in ⊕P, the next lies in PP^⊕P ⊆ P^PP ⊆ ⊕P. This is a fixed-level induction; it never replaces PP by ⊕P in the outer machine of a relativized premise.

For T in {P,BPP,BQP,SPP,LWPP,AWPP,⊕P}, the suggested PP ⊆ T ⇒ PSharpP ⊆ T transfer is safe. For the first six targets, the new AWPP rule already supplies the stronger CH ⊆ PP ⊆ T. Parity uses the separate argument above. **WPP must remain excluded** from the generic adaptive-Turing-closure template: its known truth-table closure is insufficient.

The old coNP ⊆ AM ⇒ PH ⊆ AM rule, together with PP ⊆ PH ⇒ CH ⊆ PH, already handles PP ⊆ AM ⇒ CH ⊆ AM. No duplicate special case is needed. The quantum reviewer is separately documenting PP ⊆ QMA or QCMA ⇒ PSharpP ⊆ PP using classical query transcripts; that argument does not collapse all of CH.

## The quantum-advice correction and its repair

[Aaronson’s May24,2017 erratum](https://scottaaronson.blog/?p=3256) withdrew the original proof of PP ⊆ BQP/qpoly ⇒ CH=QMA. Its invalid step attempted to place a general quantum advice state inside a classical oracle query. The classical-advice result survived.

The cutoff record must also include [Yirka2025, Theorem3.3](https://theoryofcomputing.org/articles/v021a007/v021a007.pdf), published October2,2025. It repairs the statement using a PP-low class of verifiable input-oblivious proofs: under PP ⊆ BQP/qpoly, CH=QMA=YQP*. This is a new valid proof, not rehabilitation of the old oracle-hardcoding step. The same paper restores the associated fixed-degree quantum circuit lower bound.

Thus neither “the2006 proof was valid” nor “the theorem was still unsupported at cutoff” is an accurate admission rationale. The selected context has no qpoly endpoint, so this repaired theorem does not directly add a matrix fact. The v0.4.0 landscape files mentioning quantum advice were searched; none asserts the invalid proof or relies on an unrepaired collapse. The JSON records the exact scanned files and hashes.

## All-incident family screen

| Other endpoints | Pairs | Review result |
|---|---:|---|
| Six nonuniform circuit/advice classes |24|14 noninclusions;10 remaining directions require actual circuit bounds. Arbitrary unary languages defeat every incoming nonuniform inclusion. |
| Ten logspace/parallel classes |40|All20 incoming inclusions follow through P; reverse directions remain candidates. |
| Ten existing counting classes |40|All20 incoming inclusions follow through PP or parity; closure hypotheses were checked separately. |
| Nineteen basic/proof/randomness/PH classes |76|All38 incoming inclusions follow through PH or PP; reverse directions remain candidates. |
| Seven quantum/proof classes |28|10 inclusions,18 candidates. QSZK and QMA(2) are not presumed to lie in CH. |
| ∃R |4|All four directions remain candidates. Individual numerical problems in CH do not classify all ∃R. |
| Six larger resource classes |24|8 inclusions,2 noninclusions,14 candidates. No time-versus-space gap is silently resolved. |
| PSharpP and CH internally |4|Three inclusions, one remaining CH ⊆ PSharpP question. |

The family count includes ordered directions and diagonal entries. All statuses are enumerated in the JSON, including the unscored background nodes. This is a reproducible coverage screen, not240 independent literature searches.

## Transfers deliberately rejected

- **PSharpP=PP does not itself license CH=PP.** Deterministic PP-oracle closure does not imply PP^PP=PP.
- **PP ⊆ QMA does not inherit the classical MA collapse.** The2019 source explicitly distinguishes that stronger quantum conjecture. Yirka’s repair assumes an advice containment, which is an additional hypothesis.
- **Fixed-degree circuit lower bounds do not prove PP ⊄ P/poly.** The hard language may depend on the chosen degree.
- **GapL and determinant simulations do not simulate unrestricted GapP.** The new PL endpoint gives no reverse containment of either counting endpoint in NC or SC.
- **PosSLP or square-root-sum in CH does not imply ∃R ⊆ CH.** Their relationship to real feasibility supplies no such complete reduction.
- **A trusted cited statement still needs the matching machine model.** This review establishes the standard-class implications; independent operational-definition review remains necessary.
