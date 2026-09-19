# Classical, randomized and proof-system audit: round 1

This pass found **eight ordered pairs incorrectly left as candidates** in the
0.2.0 baseline. One additional seed, `NE ⊄ Theta2P`, removes all eight. It found
no incorrect seed theorem and proposes two conditional rules that affect future
implication scoring. The review is AI-assisted, not human expert certification.

The accompanying [machine-readable dossier](audit-round1-classical.json) binds
the results to dataset
`8f69436c927248a9b7615fa97543f83764fef4afdc7b6a61b2ae9de1b4665d1d`.
It was generated from the frozen 0.2.0 commit while the working baseline was being
corrected. The historical cutoff is September 1, 2026. Current discovery pages
are not evidence that a result predates that cutoff.

## Eight known noninclusions

| Left class | Right classes newly ruled out |
| --- | --- |
| NE | Theta2P, coNP, coRP, coUP |
| NEXP | Theta2P, coNP, coRP, coUP |

Buhrman, Fortnow and Santhanam's Theorem 6 separates NEXP from polynomial time
with at most `n^c` NP queries and `n^c` advice bits, for every fixed `c`. In
particular, NEXP is not contained in Theta2P, whose NP-query budget is
`O(log n)`. Advice can be ignored for this consequence.
[Original paper, printed p. 5](https://eccc.weizmann.ac.il/report/2009/064/download/).

To obtain the NE statement, suppose NE were contained in Theta2P. For each
NEXP language, choose a polynomial padding length large enough that its padded
language belongs to NE. A Theta2P algorithm on strings of padded length
`(n+2)^k` still takes polynomial time in the original length and makes only
`O(log n)` NP queries. This would put every NEXP language in Theta2P, a
contradiction. Padding does **not** generally preserve a specified bound `n^c`
with the same exponent; logarithmic queries are the feature needed here.

The other six labels follow from `coRP, coUP ⊆ coNP ⊆ Theta2P` and
`NE ⊆ NEXP`. They also have an independent check: `NP ⊆ NE ⊆ coNP` would imply
`NP = coNP` by complementation, and hence `NE ⊆ NP`, contradicting the
nondeterministic time hierarchy.
[Seiferas, Fischer and Meyer, 1978](https://citeseerx.ist.psu.edu/document?doi=5a5339f901785db63330bc653ea76ea02b51d3fd&repid=rep1&type=pdf).

The author manuscript by **Bin Fu, Angsheng Li and Liyu Zhang** independently
records the older NE separation against subpolynomial NP-query bounds. It is
corroboration; the derivation above uses the directly inspected 2009 theorem.
[Fu–Li–Zhang, introduction](https://faculty.utrgv.edu/liyu.zhang/blz10-sepNE-joco.pdf).

A temporary closure computation against the frozen dataset produced exactly
these eight new noninclusions and no contradiction. The global counts change
from 709 inclusions, 405 noninclusions and 1,386 candidates to 709, 413 and 1,378.
Six of the eight corrections touch this agent's assigned classes; the two
coUP targets fall outside its assigned scope.

## Two conditional rules

- **`NP ⊆ FewP ⇒ AM ⊆ SBP`.** Volkovich's Theorem 1 explicitly includes the
  case where 3-SAT belongs to FewP and concludes `AM = SBP`. The hypothesis
  `NP ⊆ FewP` supplies this case. An UP hypothesis is already subsumed because
  `UP ⊆ FewP`.
  [The Untold Story of SBP, printed p. 2](https://eccc.weizmann.ac.il/report/2018/088/revision/1/download).
- **`NP ⊆ Ppoly ⇒ PH ⊆ Ppoly`.** Chakaravarthy and Roy prove that the circuit
  hypothesis collapses PH to oblivious symmetric alternation, which itself has
  polynomial-size circuits. The 2024 primary treatment states both ingredients.
  Equivalently, hardwire the polynomial-size oracle circuits at each fixed PH
  level and use `NP/poly = P/poly` under the hypothesis. Polynomial degrees may
  depend on the language and level.
  [Oblivious Classes Revisited, §§1.1.2 and 1.2](https://eccc.weizmann.ac.il/report/2024/049/download/).

Neither conclusion was already obtained by the frozen rule engine under its
respective premise. These rules settle no additional baseline pair by
themselves. The original 2006 manuscript's indexed theorem was available, but
direct PDF retrieval failed; the dossier records that access limit.

## Coverage and interpretation

The scope contains the 1,539 ordered pairs with at least one endpoint among
P, NP, coNP, RP, coRP, ZPP, BPP, SBP, MA, coMA, AM, coAM, SZK, NPcapcoNP,
Sigma2P, Pi2P, Delta2P, Theta2P and PH. Initially 952 were candidates; the six
in-scope corrections reduce that to 946.

For each of these 19 classes, the complete main Complexity Zoo entry was read
through the boundary before its backlinks. The primary site returned HTTP 403,
so a public per-entry mirror supplied discovery text. The Delta2P and Theta2P
oracle aliases, plus the neighboring S2P and O2P entries, were also read. The
JSON records every entry, URL, interpretation, unresolved row and unresolved
incoming pair from outside the scope. No additional unconditional roster
inclusion emerged from that census.

The dossier partitions the scope into 39 family groups, covering every scoped
pair exactly once. This records a semantic and literature screen, not 1,539
independent proofs of historical openness. Absence from the sources leaves a
pair a candidate.

The full randomized-machine, proof-system, oracle and statistical-distance Lean
modules were read. The checks covered fair coins, halting and terminal padding,
finite-polynomial witness lengths, quantifier order, intentional advice,
logarithmic NP-query counts, fixed PH levels and sampler multiplicities. No
concrete definition error was found. General equivalence to textbook machine
models remains unproved; the definitions are not proofs of the literature
containments.

Several plausible transfers were rejected:

- Oracle separations involving SZK, SBP, QMA or PP do not establish ordinary
  noninclusions. Perfect and noninteractive zero knowledge also differ from SZK.
- Fixed-degree circuit lower bounds do not separate a class from the union
  P/poly. Advice and arithmetic-circuit lower bounds require their own transfer.
- A two-query `ZPP^NP` simulation retains outer randomness. It does not put BPP
  or MA in Theta2P.
- Total-language `BPP = P` alone does not justify replacing every promised
  verifier slice in an MA protocol with a deterministic algorithm.

Primary sources and exact locators for these decisions are in the JSON.
Selective searches included 2024–2026 work and a September 7, 2026 preprint
excluded for appearing after the cutoff. A publication census remains work for
the next pass.

## Remaining uncertainty

The user stopping rule is an expected number of fewer than two misclassified
ordered pairs, excluding future flaws discovered in currently accepted proofs.
This pass does not establish that bound. Discovering eight correlated omissions
from one older theorem is direct evidence that counting checked entries or
successful searches overstates confidence.

The JSON therefore gives explicit **judgmental sensitivity ranges**, not a
statistically calibrated posterior. Four possible remaining error families
cover missed older query separations, randomized/proof/counting adjacency,
misinterpretation of existing statements, and recent pre-cutoff omissions.
Their probability and conditional expected propagation ranges give summed
endpoints of **0.23 to 5.80 affected pairs**. The clusters overlap, so those
endpoints are not a confidence interval or a rigorous upper bound. They are
inputs for a second reviewer to challenge. Estimates from overlapping agent
scopes must not be added as though they described disjoint events.

The next pass should reproduce the query-padding argument independently,
review promise-sensitive conditional rules, and inspect recent primary
publication lists. A second reviewer should also challenge the operational
definitions and the source-to-class translations before using the low end of
any estimate to decide whether to stop.
