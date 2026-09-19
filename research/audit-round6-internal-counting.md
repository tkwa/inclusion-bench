# Internal counting classes: final bounded review

This pass found **no additional ordinary inclusion or noninclusion**. It checked
the 53 unresolved ordered pairs among UP, coUP, FewP, SPP, CeqP, PP, parityP,
AWPP, LWPP and WPP. The other 47 pairs in this block are known inclusions. This
is an AI-assisted literature review, not expert certification of openness.

The [machine-readable dossier](audit-round6-internal-counting.json) binds the
review to dataset
`e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3`, with
709 inclusions, 413 noninclusions and 1,378 candidates. It lists all 100 internal
pairs, precise source locators, prior dossier hashes and hypothetical impacts.
No canonical data was changed.

## New evidence

The previously unavailable **Böhler–Glaßer–Meister technical report** was
recovered from its university archive. Its dated title page is October 7, 2002;
the archive index's August metadata should not override it. Section 4 and the
visually inspected Figure 1 confirm the expected SPP–WPP–AWPP chain. WAPP is
a separate class. Section 5's noninclusions retain their oracle qualifiers.
The final 2006 journal version was not retrieved, so this closes the technical
report retrieval gap only.
[Full report, §§4–5 and Figure 1](https://www1.pub.informatik.uni-wuerzburg.de/pub/TRs/tr299.ps.gz)

Two later primary branches were also checked directly:

- **Hemaspaandra–Hemaspaandra–Spakowski–Watanabe (2018)** prove robustness
  under polynomially many target values for LWPP, WPP and CeqP. Their
  Exp-LWPP notation permits exponentially many target values; it does not
  identify that class with LWPP. Their #P-based LWPP+ also cannot replace
  the GapP class.
  [Definitions 2.3–2.9; Theorems 3.1, 3.7, 5.2 and 7.3](https://arxiv.org/pdf/1711.01250v3)
- **Hemaspaandra–Juvekar–Nadjimzadah–Phillips (2024 revision)** investigate
  ambiguity bounds and restricted counting targets. Zero accepting paths
  on no-inputs is stronger than SPP's zero *gap*. The results do not give
  FewP⊆UP or SPP⊆FewP. Their earlier FewP-to-parity and SPP references agree
  with the current baseline.
  [Definitions, Table 1, §3 and Theorem 4.1](https://arxiv.org/pdf/2109.14764v5)

The original gap-counting and oracle-toolkit taxonomy was cross-checked against
these branches. Ten elementary or cited edges, using reflexivity and
transitivity, reproduce **exactly all 47 current internal inclusions**. The
coUP→SPP edge uses complement closure of SPP. This is an independent projection
check, not a completeness theorem for the literature.
[Fenner–Fortnow–Kurtz–Li, Definitions 2.2–2.3 and Corollary 6.4](https://lance.fortnow.com/papers/files/obt.pdf)

## The 53 remaining candidates

Each cell lists targets for which inclusion from the row's class remains a
candidate in the frozen baseline. These are recorded statuses, not new
historical-openness certificates.

| Left class | Candidate right classes | Count |
| --- | --- | ---: |
| UP | coUP | 1 |
| coUP | UP, FewP | 2 |
| FewP | UP, coUP | 2 |
| SPP | UP, coUP, FewP | 3 |
| CeqP | UP, coUP, FewP, SPP, parityP, AWPP, LWPP, WPP | 8 |
| PP | UP, coUP, FewP, SPP, CeqP, parityP, AWPP, LWPP, WPP | 9 |
| parityP | UP, coUP, FewP, SPP, CeqP, PP, AWPP, LWPP, WPP | 9 |
| AWPP | UP, coUP, FewP, SPP, CeqP, parityP, LWPP, WPP | 8 |
| LWPP | UP, coUP, FewP, SPP, parityP | 5 |
| WPP | UP, coUP, FewP, SPP, parityP, LWPP | 6 |

## Residual judgment

I revise the older internal-counting omission component from **0.20 to 0.15
expected wrong labels**: a 3% probability of at least one remaining omission,
times a conditional mean of five distinct affected pairs. The previous
probability was 4%. This replaces that row of the round-three assessment;
it is not an additional contribution.

The reduction reflects identifiable new evidence: recovery of the missing
primary taxonomy and direct review of two follow-up branches. Shared authors
and reference chains make these correlated checks. They warrant a modest
update, not a claim that all relevant literature has been found. The absent
final journal text and obscure intermediate-class corollaries remain reasons
for uncertainty.

The impact remains five. Examples such as WPP⊆LWPP or AWPP⊆CeqP would resolve
one internal pair, while LWPP⊆SPP would resolve two. Stronger collapses could
resolve many more. The conditional mean concerns the union of labels from
all remaining omissions; it is neither a per-theorem nor a per-pair rate.
Sensitivity choices of 1–8% probability and 3–12 affected pairs give products
from 0.03 to 0.96. These are not confidence bounds. The estimate is subjective
and uncalibrated, and this dossier alone makes no global stopping claim.

An overlooked accepted ordinary edge would raise the estimate, particularly
if found through terminology absent from the reviewed chains. Independent
expert review of these 53 candidates and the final journal reference chains
would lower it. Future-discovered flaws in accepted proofs are excluded as
requested; translation or application errors belong to separate allowances.

## Resource-domain allocation clarification

The round-four **0.36 older-resource omission allowance** applies to every
ordered pair with at least one of these 17 endpoints: AC0, ACC0, TC0, NC1, L,
NL, LogCFL, NC, SC, P/poly, NP/poly, PSPACE, EXP, NEXP, EXPSPACE, E and NE.
That is 1,411 pairs, including 476 resource/counting-or-quantum comparisons
(228 current candidates). The narrower wording in the earlier dossier was
inaccurate; it must not leave those cross-family comparisons unassigned.

I retain 0.36 for this full domain on the combined evidence of the original
17-by-all census, the recovered old time/query/advice manuscripts and the
subsequent interface reviews. This clarification supplies no independent
reason to change the numerical judgment. Fixed-degree circuit bounds,
quantum advice classes and restricted quantum-space results retain their
qualifications; they cannot be substituted for the roster's unrestricted
unions or uniform total-language classes.

For older omissions, the disjoint endpoint blocks contain 1,411 resource pairs,
100 internal-counting pairs, 628 other counting/quantum interface pairs and
361 basic pairs: all 2,500 ordered pairs. Model and theorem-application errors
have separate cause allocations, with each incorrect label counted only once.
