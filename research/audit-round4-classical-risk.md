# Older classical separations and basic-class risk: round 4

This pass found **no additional pair to relabel**. It followed older reference
chains for exponential time, bounded queries, advice and semantic hierarchies,
and checked the remaining block of basic classical classes. The review is
AI-assisted, not human expert certification. It does not certify the historical
openness of every candidate.

The [JSON dossier](audit-round4-classical-risk.json) binds the review to dataset
`e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3`:
709 inclusions, 413 noninclusions and 1,378 candidates. It records sources,
review depth, the 32 principal time-class comparisons, all 361 basic-class
comparisons, and the residual estimates below. No canonical data was changed.

## What the additional primary reading resolved

Three author manuscripts were recovered and read beyond the abstracts or
citations available in previous rounds:

- **Homer and Mocas (1995)** prove lower bounds with fixed advice and circuit
  exponents. The witness language can depend on that exponent. Their results
  therefore do not establish EXP ⊄ P/poly or NEXP ⊄ NP/poly.
  [Author manuscript, Theorems 2.1–2.2 and Corollaries 2.1–2.5](https://web.cecs.pdx.edu/~sarah/homer.ps).
- **Mocas (1996)** separates NEXP from polynomial-time NP queries with a fixed
  query exponent, and from parallel NP queries. The latter confirms the
  already-corrected Θ₂P comparison. The concluding section expressly retains
  the unrestricted Pᴺᴾ-versus-NEXP question.
  [Corollaries 3.1 and 3.3, printed pp. 9 and 11](https://web.cecs.pdx.edu/~sarah/bounded-query.ps).
- **Mocas (2002)** separates BPP from an exponential-time zero-error class
  with an RP oracle. Removing that oracle or replacing the larger class by
  EXP is conditional. In particular, her EXP-versus-BPP consequence assumes
  P = RP. That hypothesis cannot be discarded.
  [Corollaries 3.3–3.5, printed pp. 3–4](https://web.cecs.pdx.edu/~sarah/tr-02.ps).

The complete theorem statements in Buhrman, Fortnow and Santhanam (2009) retain
the same qualifications: fixed advice degree, fixed query or time exponent,
or an exponential randomized/proof-system class on the left. Theorem 6 already
supports the Θ₂P correction; it does not separate NEXP from Δ₂P. The proof of
Theorem 3 contains a disjunction and does not prove its NP/poly branch alone.
[Theorems 3, 6, 9, 13 and 15](https://lance.fortnow.com/papers/files/advice.pdf).

Two semantic-hierarchy papers keep advice even on the harder side. A hierarchy
with one advice bit does not establish a hierarchy for the corresponding
uniform total-language class.
[Fortnow–Santhanam–Trevisan, Theorems 1–3](https://lance.fortnow.com/papers/files/promise.pdf);
[van Melkebeek–Pervyshev, Theorems 1–4](https://drops.dagstuhl.de/storage/16dagstuhl-seminar-proceedings/dsp-vol06111/DagSemProc.06111.3/DagSemProc.06111.3.pdf).

The later sublinear-advice hierarchy likewise retains fixed exponents and,
for its circuit application, an NP-uniformity requirement. Its one-sided
exponential randomized lower bound gives no missing BPP comparison.
[Fortnow–Santhanam 2016, Theorems 1.1–1.4](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2016.19).

Finally, MAEXP circuit lower bounds cannot be transferred to NEXP by deleting
the exponential verifier's randomness. The original 1998 paper also defines
PEXP as exponential-time majority computation, not deterministic EXP. Later
robust-simulation results preserve their promise-class or fixed-degree
qualifications.
[Buhrman–Fortnow–Thierauf, Theorem 3.4 and Corollaries 3.5–3.6](https://ir.cwi.nl/pub/1270/1270D.pdf);
[Fortnow–Santhanam, Theorems 28 and 30](https://lance.fortnow.com/papers/files/robust.pdf).

The 2024 constructive-separations theorem is conditional on a separation; it
does not supply every separation appearing in its parameter list. Its stated
open examples include ZPP versus EXP and BPP versus NEXP.
[Chen–Jin–Santhanam–Williams, abstract and Theorem 1.2](https://theoretics.episciences.org/12881/pdf).

## Checked pair groups

The principal 32-pair slice has eight known noninclusions and 24 candidates:

| Left class | NP, coNP, Θ₂P, ZPP | P/poly, NP/poly, Δ₂P, BPP |
| --- | --- | --- |
| E | All four remain candidates | All four remain candidates |
| EXP | All four remain candidates | All four remain candidates |
| NE | All four known noninclusions | All four remain candidates |
| NEXP | All four known noninclusions | All four remain candidates |

These are current baseline statuses, not 24 new openness certificates. The
review also checked adjacent advice, proof-system and hierarchy theorems;
it was not confined to searching those 32 exact strings.

The separate **basic block** consists of AM, BPP, Δ₂P, MA, NP, NP∩coNP, P, PH,
Π₂P, RP, SBP, SZK, Σ₂P, Θ₂P, ZPP, coAM, coMA, coNP and coRP. Its 361 ordered
pairs have 146 known inclusions and 215 candidates. Neither endpoint belongs
to the counting, quantum, circuit, space or exponential-time families covered
by the other risk ledgers.

Every class in this block lies between P and PH in the baseline. A fresh
closure with NP ⊆ P identifies all 19 classes and yields all 361 inclusions.
Consequently, any noninclusion within this block would imply P ≠ NP. This
reduces the plausibility of a quietly overlooked accepted separation; it does
not rule out a missing known inclusion. Round one's entry-by-entry census and
the later interface reviews remain the principal evidence for those inclusions.

I also reread the finite-coin probabilities, MA/AM witness order, polynomial
length descriptions, advice indexing and oracle-query bounds in the selected
Lean definitions. No mismatch was found in that selection. This was not a
new proof that the machine models equal every textbook convention, nor a
complete review of the low-level machine implementation.

## Revised residual judgment

The **older exponential/query/advice omission** contribution is revised from
0.60 to **0.36 expected wrong labels**: a 6% chance of at least one remaining
omission, with a conditional mean of six distinct affected pairs. The earlier
values were 10% and six. Recovering the old author manuscripts and following
the hierarchy/advice chains warrants a modest reduction; their overlapping
references are not independent negative experiments. Obscure older corollaries
and less visible journal publications remain plausible sources of error.

For the previously uncovered **basic 19×19 block**, I add **0.22**:

| Remaining cause | Judgmental probability | Mean distinct wrong pairs if it occurs | Expected contribution |
| --- | ---: | ---: | ---: |
| At least one older omitted theorem in the basic block | 2% | 8 | 0.16 |
| A definition or application mismatch within that block | 0.2% | 30 | 0.06 |

These probabilities describe family-level events. The conditional counts are
unions of affected pairs, allowing one mistake to change many labels; they
are not per-paper or per-pair rates. The model allowance concerns an incorrect
translation or application of a result, and excludes future-discovered flaws
in currently accepted proofs. Errors affecting other endpoint families belong
to those families' allowances, not again to these 361 pairs.

This dossier contributes **0.58** to the aggregate: **replace** the previous
0.60 by 0.36, then **add** 0.22 for the basic block. The separate recent-publication
estimate of 0.15 is unchanged and retains its stated classical/time/counting
scope. It does not silently cover every recent quantum or zero-knowledge result.

The JSON's sensitivity scenarios span 0.055–4.40 expected labels for the three
components here. Those endpoint products are not confidence intervals or
rigorous bounds. This pass alone makes no all-50-class stopping claim.

A primary accepted theorem giving another omitted ordinary pair would raise
the estimate, especially if it escaped multiple searches through an indirect
corollary. Independent expert review of the 215 basic candidates, original
journal-only reference chains, and machine-model equivalences would lower it.
Any concrete error must be corrected before reconsidering these numbers.
