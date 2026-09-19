# Recent-publication audit: round 2

This pass found **no additional known ordered-pair classification missing from
the corrected baseline**. It screened the complete title lists for CCC, STOC,
FOCS and ITCS in 2024–2026, plus ECCC's 2024–2026 submission lists, then checked
32 plausible papers against primary abstracts or theorem statements. This is
an AI-assisted literature review, not human expert certification or a proof
that every remaining candidate was open.

The [machine-readable dossier](audit-round2-recent.json) records the title
metadata, official index URLs, selected sources, review depth, cutoff checks,
and a binding to the working dataset. That snapshot has 709 inclusions,
413 noninclusions and 1,378 candidates. It includes the eight NE/NEXP corrections
from [round 1](audit-round1-classical.md). The parent audit separately checked
all propositional consequences of the encoded baseline; this pass looked for
literature that the encoded theory might still omit.

## What was screened

| Primary index | 2024 | 2025 | 2026 | Total screened |
| --- | ---: | ---: | ---: | ---: |
| CCC accepted papers | 36 | 36 | 42 | 114 |
| STOC accepted papers | 188 | 219 | 212 | 619 |
| FOCS accepted papers | 127 | 137 | 174 | 438 |
| ITCS accepted papers/program | 103 | 96 | 118 | 317 |
| ECCC records submitted by September 1, 2026 | 202 | 215 | 163 | 580 |

The conference total is **1,488 title entries**. A paper may appear both at a
conference and on ECCC, so these numbers must not be added into a count of
distinct papers. They also do not count full-paper reviews. The dossier retains
all 611 ECCC listing records retrieved, including 31 outside the submission
window, and identifies the selected deeper reviews.

The focus was exponential-time classes against randomness, counting,
polynomial-hierarchy and proof-system classes. Titles involving lower bounds,
hierarchies, derandomization, independence, sampling, advice and oracle
separations received particular attention. Recent circuit/space and quantum
claims also informed the parallel reviewers; this report does not duplicate
their full domain audits.

## Results that looked close but do not change the matrix

Ren and Williams obtain near-maximum circuit lower bounds in **E with a
promise-MA oracle and one advice bit**. Their Theorem 1.1 preserves those
resources; it does not place the hard language in ordinary E, NE or NEXP.
[Primary theorem, July 2026 revision, printed p. 2](https://eccc.weizmann.ac.il/report/2026/118/revision/1/download/).

Chen, Li and Liang prove a near-maximum lower bound for **exponential-time
Arthur–Merlin computation with subexponential advice**, including a symmetric
intersection. AMEXP and its advice cannot be replaced by the roster's AM or
NEXP. The June 2026 revision was checked, including its correction notes.
[Theorem 1.1](https://eccc.weizmann.ac.il/report/2024/182/revision/2/download/).

The symmetric-exponential-time lower bounds likewise retain symmetric
alternation. Zeyong Li removes the earlier advice requirement, but that does
not turn S2E into E or NE.
[Primary preprint](https://arxiv.org/abs/2310.17762).

Other scope checks included:

- A **promise-BPTIME hierarchy** does not give a hierarchy for total-language
  BPP. [He, 2025](https://eccc.weizmann.ac.il/report/2025/004/).
- Putting **Hilbert's Nullstellensatz in the counting hierarchy** improves a
  particular problem's upper bound. Neither its PSPACE-completeness nor
  equality of CH and PP is supplied.
  [Andrews, Garg and Schost, 2026](https://eccc.weizmann.ac.il/report/2026/024/).
- A title saying that Alexandrov–Fenchel equality cases are outside PH is
  qualified in the theorem: membership would collapse PH. It is not an
  unconditional CeqP-versus-PH separation.
  [Chan and Pak, Theorem 1.1](https://www.math.ucla.edu/~pak/papers/AFequality32.pdf).
- Recent **bounded-arithmetic unprovability** results concern theories weaker
  than ZFC. They do not establish ZFC independence of an ordinary class pair.
  [Chen, Li and Oliveira, 2024](https://eccc.weizmann.ac.il/report/2024/060/).
- **Effective zero knowledge** uses a different requirement from statistical
  zero knowledge. Its claimed constructions do not put NP in SZK.
  [Ilango, 2025](https://eccc.weizmann.ac.il/report/2025/095/).
- A recent **MA-versus-NP-with-BPP separation** is explicitly about
  communication complexity. The analogous language-class statement does
  not follow. [Watson, August 2026](https://eccc.weizmann.ac.il/report/2026/155/).

The JSON also records search and sampling separations, fixed-degree lower
bounds, conditional hitting-set consequences, and proof-system results.
No proposed new seed or rule is imported from this pass. That does not assert
that every possible conditional consequence of the selected papers has been
extracted.

## Cutoff checks

**ECCC's year-list dates are submission dates.** For example, TR26-170 was
submitted on August 14 but published on September 7. Its ECCC version therefore
cannot establish a result's public availability by September 1. Its black-box
lattice lower bound also falls outside ordinary class-pair scope.
[Report metadata](https://eccc.weizmann.ac.il/report/2026/170/).

Conversely, TR26-163 was submitted and published on September 1; the displayed
publication time is 21:56. The screen includes that boundary record, which
concerns super-Ramanujan graphs.
[Report metadata](https://eccc.weizmann.ac.il/report/2026/163/).

FOCS 2026 takes place after the cutoff. Its accepted-paper list was useful for
discovery, but acceptance on that list is not evidence of a pre-cutoff public
theorem. Selected papers require a separately dated preprint or other public
version. Most screened ECCC titles did not receive an individual release-date
audit; they supply no new baseline fact.

## Remaining expected errors

My judgmental estimate for **remaining pair errors attributable to recent
publication omissions in this pass's scope** is **0.15**. This is not the
all-era, all-50-class total and must not be added to another estimate that
already includes the same omissions. It excludes future-discovered flaws in
currently accepted proofs, as requested.

The estimate has two explicit components:

| Remaining event | Judgmental probability | Mean affected pairs if it occurs | Expected contribution |
| --- | ---: | ---: | ---: |
| A missed specialized recent theorem or corollary | 2% | 5 | 0.10 |
| A recent result missed through a shared interpretation or discovery gap, with broad consequences | 0.2% | 25 | 0.05 |

The low event probabilities reflect the complete main-venue title screen,
overlapping ECCC coverage, and primary checks of plausible results. The
conditional pair counts explicitly allow correlated propagation: one missed
theorem can affect many matrix entries. These are reasoned judgments, not
frequencies estimated from independent samples. The original eight-pair
omission is a reason to retain this propagation risk.

The JSON gives sensitivity ranges whose endpoint products sum to **0.015–1.08
pairs**. That range is a scenario calculation, not a confidence interval or a
rigorous upper bound. Older omitted theorems, errors in translating class
definitions, and domains handled by other reviewers remain separate issues.
This dossier alone does not establish the user's global stopping threshold.

An independent check of these scope translations, a journal-only and
arXiv-only census, or recent primary surveys explicitly identifying the
high-impact comparisons as open would lower the estimate. One additional
accepted theorem that settles an omitted ordinary pair—especially through an
unobvious corollary—would raise it. So would a failed check of advice,
uniformity, promise or fixed-exponent qualifications. No numerical estimate
here substitutes for correcting a concrete error when one is found.
