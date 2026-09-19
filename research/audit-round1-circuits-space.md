# Circuits, space and exponential resources: first audit round

The audit found two related omissions: `NE ⊄ coNP` and `NE ⊄ Θ₂P`, together with their consequences for NEXP and smaller target classes. The first is an elementary consequence of the existing hierarchy facts. The second has published primary support. These findings overlap the logical and classical dossiers; they are not additional discoveries to count twice.

The accompanying [JSON dossier](audit-round1-circuits-space.json) records every incoming and outgoing comparison for the 17 assigned classes, all 84 baseline seeds touching them, source locators, model checks, and proposed changes. Its baseline is dataset `8f69436c927248a9b7615fa97543f83764fef4afdc7b6a61b2ae9de1b4665d1d`. The scope contains 1,411 distinct ordered pairs: 414 inclusions, 405 noninclusions, and 592 candidates. This is a systematic first review, not 1,411 independent certifications of openness.

## Corrections and missing implications

If NE were contained in coNP, then NP would be contained in coNP, hence NP = coNP. NE would consequently be contained in NP, contradicting the nondeterministic time hierarchy. Adding this consequence resolves six current candidate pairs, through NE/NEXP and coNP/coUP/coRP. The root logical audit owns its integration.

The logarithmic-query separation has a direct primary anchor in **Buhrman, Fortnow and Santhanam, _Unconditional Lower Bounds against Advice_, Theorem 6**. It excludes NEXP from polynomial-time computation with a fixed polynomial bound on NP queries and advice. This covers Θ₂P. Polynomially padding an NEXP language into NE preserves logarithmically many queries when the padding is removed, giving NE ⊄ Θ₂P. The classical auditor independently read that theorem. [ECCC TR09-064](https://eccc.weizmann.ac.il/report/2009/064/)

Fortnow and Klivans also recount the earlier Fu–Li–Zhong result for parallel NP queries in §5 of [_NP with Small Advice_](https://eccc.weizmann.ac.il/report/2004/103/download/). The original 1994 paper was identified bibliographically but its original full text was not retrieved. That limitation does not block the later direct primary proof. Adding NE ⊄ Θ₂P resolves eight candidates against the starting baseline; six overlap the coNP correction, leaving **two further pairs**.

Two useful conditional implications are absent:

- `PSPACE ⊆ NP/poly ⇒ PSPACE ⊆ PH`. The published unconditional consequence is a collapse to Σ₃P. A stronger collapse to Σ₂P in the same paper has an extra promise-AM derandomization assumption and cannot be imported here. [Aydınlıoğlu–van Melkebeek, introduction, printed p. 4](https://eccc.weizmann.ac.il/report/2012/080/download/)
- `NP ⊆ P/poly ⇒ PH ⊆ P/poly`. Under the premise, NP/poly = P/poly. Closure of P/poly under complement and polynomial-size composition then eliminates any fixed number of alternating quantifiers. The stronger oblivious symmetric collapse is supporting literature; the elementary argument suffices for this endpoint. [Chakaravarthy–Roy, _Oblivious Symmetric Alternation_](https://pages.cs.wisc.edu/~venkat/pubs.html)

Neither conditional changes the baseline without its premise. The classical auditor independently found the latter.

The root audit proposes extending polynomial padding to every roster target except E and NE. For this audit's targets the extension is sound. Padding fixes circuit inputs without changing constant/logarithmic depth or a fixed ACC modulus. A small-space machine computes padded input symbols using a logarithmic counter. The SC simulation preserves polynomial time and polylogarithmic space on the same machine. Advice for the padded length remains polynomial in the original length. This uses a particular easily computable padding map; it does not assert closure of AC0, TC0 or NC1 under arbitrary polynomial-time reductions.

## Baseline provenance and model checks

All 84 relevant seed statements were checked for mathematical meaning and compatibility with the chosen models. The JSON assigns each seed a review group, retaining its existing sources and distinguishing directly inspected primary passages from accepted standard theorems whose full proofs were not reread. Existing deep proofs remain trusted under the user's waiver.

The largest group is 44 seeds asserting that nonuniform AC0 is not contained in a uniform class. These are intentional. A nonrecursive set of input lengths can be encoded by one constant-output circuit at each length, whereas the uniform classes contain only recursive languages. Borodin explicitly discusses this obstruction immediately after his uniform circuit-depth/space simulation theorem. The same paper's Lemma 1 and Theorem 4 support the polylogarithmic-space upper bound for uniform NC. These observations justify both the nonuniform block and the application of the space hierarchy to PSPACE versus NC. [Borodin 1977, printed p. 738](https://www.cs.toronto.edu/~bor/Papers/relating-time-space-size-depth.pdf)

The four LogCFL-related inclusions use the uniform SAC¹ characterization. The primary paper states the uniform inclusion chain on printed p. 560, and establishes complement closure in §3.1/Corollary 15. No nonuniform NC1 inclusion into L was imported from that chain. [Borodin–Cook–Dymond–Ruzzo–Tompa 1989](https://www.cs.toronto.edu/~bor/Papers/two-applications-complementation-via-inductive-counting.pdf)

The ACC lower bound is stronger than merely NEXP ⊄ ACC0: Theorem 1.1 explicitly excludes NTIME[2ⁿ], giving the NE seed. Its separate exponential-size lower bound uses an NP oracle, so it supplies no E ⊄ ACC0 seed. Lemma 5.4 supports the universal circuit-evaluation hardwiring argument. [Williams, _Nonuniform ACC Circuit Lower Bounds_](https://people.csail.mit.edu/rrw/acc-lbs-journal-final.pdf)

The EXPSPACE ⊄ NP/poly seed also survives an independent constructive check. At length n, enumerate nondeterministic circuits of size at most 2^(⌊n/4⌋), and find a truth table outside their range. Their description count is smaller than the number of n-input Boolean functions. Storing a truth table takes 2ⁿ bits; enumerating descriptions and nondeterministic assignments also fits exponential space. The resulting language eventually defeats every fixed polynomial circuit bound. The unrestricted running time is essential: this argument supplies no EXP lower bound.

The concrete Lean definitions were inspected at the machine and encoding level:

- The finite transition tables cannot hide an arbitrary noncomputable oracle. The input head is bounded by endmarkers. Workspace measures the visited work-tape interval.
- NL requires all branches to halt within a finite input-dependent bound and constrains every reachable configuration. SC uses one deterministic machine for both resource bounds.
- E and NE use a linear exponent; EXP, NEXP and EXPSPACE range over polynomial exponents.
- ACC0 chooses one fixed modulus per family. Circuit size counts gates and wires; the difference from literal bit-encoding size is polynomial and does not change the roster's polynomial-size unions.
- Uniform NC emits an actual circuit serialization using a logspace transducer. Its output tape is write-only and is not available as free workspace.
- Circuit depth is measured at the selected output. Unused deep gates cause no enlargement: unrolling all gates for the stated depth gives the same output, with polynomial size and a logspace generator. This avoids assuming a logspace algorithm for trimming all nodes that reach the output.
- LogCFL uses a finite grammar and a concrete logspace reduction. NP/poly intentionally allows arbitrary advice indexed only by input length.

No class-changing discrepancy was found in these modules. The mathematical equivalence with textbook machine models remains a distinct proof obligation; this review did not turn those equivalences into Lean theorems.

## Literature sweep and excluded transfers

Each of AC0, ACC0, TC0, NC1, L, NL, LogCFL, NC, SC, P/poly, NP/poly, PSPACE, EXP, NEXP, EXPSPACE, E and NE has an individual Zoo discovery record in the JSON. Most live Zoo pages returned HTTP 403. Their named sections and available tails were recovered from indexed search responses; the E page was retrieved live. This is not an authoritative fresh snapshot of every page. Zoo supplied leads, while theorem admission relies on primary sources and explicit model arguments.

Several apparently relevant advances do not resolve a new roster pair:

| Primary source | Scope relevant to admission |
| --- | --- |
| [Chen–Ren 2020, revision 1](https://eccc.weizmann.ac.il/report/2020/010/) | Nondeterministic quasipolynomial time versus ACC0 with a bottom layer of threshold gates; this is not all TC0. |
| [Chen–Tal–Wang, March 2026](https://eccc.weizmann.ac.il/report/2026/039/) | A hard E^NP function and a fixed depth-two threshold size bound; neither the oracle nor the depth restriction can be dropped. |
| [Ren–Williams, July 2026](https://eccc.weizmann.ac.il/report/2026/118/) | Near-maximum lower bounds use promise-MA queries and one bit of advice. |
| [ITCS 2026 torus-polynomial paper](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.88) | Does not prove majority outside ACC0; that remains the motivating conjecture. |
| [Pyne–Tell, March 2026 revision, §4.3.1](https://eccc.weizmann.ac.il/report/2025/140/revision/1/download/) | Explicitly treats NC ⊄ SC as a conjecture and discusses unresolved directed-connectivity time-space bounds. |

The full P^NP class must be distinguished from a fixed query bound. A language-dependent polynomial exponent cannot be replaced by one exponent that works for the whole class. The oracle construction in [_Two Oracles that Force a Big Crunch_](https://cse.sc.edu/~fenner/papers/bigcrunch.pdf) is useful as a scope check, not as an unrelativized benchmark fact.

A pre-cutoff manuscript also needed triage. [Montoya, arXiv:2605.08555v1, submitted May 8, 2026](https://arxiv.org/abs/2605.08555v1), claims NL ≠ LogCFL. In Theorem 35's proof, printed pp. 15–17, an arbitrary automaton is assumed to consist of a local subroutine and a global routine without a normalization result. A projected uniform configuration distribution is then asserted to be uniform without establishing equal fiber sizes. These gaps leave the central entropy decomposition unsupported. No acceptance evidence was found. The claim should not be admitted as known; an independent reviewer should check this assessment. This concerns a present gap in an unreviewed claim, not a prediction of a future flaw in an accepted proof.

## Remaining uncertainty

This round does **not** establish an expected error count below two. The JSON gives explicit probability and affected-pair ranges for sensitivity analysis, but they are not calibrated posterior estimates. In particular, this round discovered an old bounded-query separation missing from both the baseline and the relevant Zoo entry. Search absence is therefore weak evidence for completeness.

The remaining risks are an obscure older exponential/oracle separation, a mistaken uniformity or advice transfer with substantial fanout, an overlooked pre-cutoff result or revision, and consequences absent from the inference rules. These overlap; treating repeated agent searches as independent evidence would exaggerate confidence. Future flaws in currently accepted proofs are excluded from this accounting.

The next useful review is to rotate the circuit/space dossier to another auditor, independently check the 44 uniform endpoints of the nonrecursive-length argument, replay the expanded padding and contradiction consequences, and measure actual pair fanout for each surviving uncertainty. The detailed candidate lists in the JSON provide the starting comparison inventory.
