# Baseline audit and launch policy

**Recorded September 19, 2026. Historical cutoff: September 1, 2026.** This is an AI-assisted literature and semantic audit by the collaborating Codex agent `/root/classical_literature`. It is not a human expert certification that every candidate was open at the cutoff.

The corrected baseline contains **709 inclusions and 405 noninclusions**, leaving **1,386 candidate questions** among the 2,500 ordered pairs. The [machine-readable audit](baseline-audit.json) indexes every pair and assigns it to one of 100 ordered family groups. Those groups record the conventions, source families and searches considered. Indexing every pair does not mean conducting 2,500 independent literature searches.

Runs can start against these frozen candidates. Points require historical review of each pair actually claimed, including pairs obtained through implications. Existing theorems are trusted, cited baseline inputs; their proofs do not need to be formalized in Lean.

## Corrections from this pass

| Added fact or implication | Evidence checked |
| --- | --- |
| Θ₂P ⊆ PP | Beigel, Hemachandra and Wechsung, February 1989, Theorem 2.1 and Corollary 2.3 of the [original technical report](https://urresearch.rochester.edu/fileDownloadForInstitutionalItem.action?itemFileId=8631&itemId=5587). The repository's later deposit date is not the theorem's publication date. |
| NP ⊆ BPP ⇒ PH ⊆ BPP | Theorem 3.3 of Fortnow's [A Simple Proof of Toda's Theorem](https://toc.cs.uchicago.edu/articles/v005a007/), published July 3, 2009. |
| coNP ⊆ AM ⇒ PH ⊆ AM | Klapper's [primary author abstract](https://cs.uky.edu/~klapper/abs/lowness.html), Mathematical Systems Theory 22 (1989), recovers this collapse using the notation BP·NP. |
| NP ⊆ P/poly ⇒ AM ⊆ MA | Arvind, Köbler, Schöning and Schuler, [If NP has polynomial-size circuits, then MA = AM](https://www.sciencedirect.com/science/article/pii/030439759591133B), January 23, 1995. Publisher abstract and author publication record checked. |
| NP ⊆ BPP ⇒ NP ⊆ RP | SAT self-reduction, amplification and final assignment verification; derivation below. |
| ⊕P ⊆ P ⇒ NP ⊆ RP | Specialize the isolation reduction in Fortnow's Theorem 3.1 to a deterministic parity-SAT solver; derivation below. |

Only the first correction changes unconditional baseline pair counts. The other five improve the consequences assigned to future proofs. Neither the imported implications nor this audit claim to enumerate every known implication.

## Elementary implications added during this audit

For **NP ⊆ BPP ⇒ NP ⊆ RP**, use an amplified BPP SAT algorithm to fix a satisfying assignment one variable at a time. Bound the error of each query so that their sum is at most one third; this remains valid for adaptive queries. Accept only if the final assignment passes deterministic verification. A satisfiable formula is accepted with probability at least two thirds, and an unsatisfiable formula is never accepted. The historical ingredients are the SAT self-reduction and amplification in the [Arora–Barak author draft](https://theory.cs.princeton.edu/complexity/book.pdf). This paragraph records the elementary consequence, not a new research result dated before the cutoff.

For **⊕P ⊆ P ⇒ NP ⊆ RP**, generate the random list of formulas in the isolation theorem. Unsatisfiability is preserved in every formula; on a satisfiable input, with high probability at least one formula has exactly one solution. A deterministic parity solver accepts the list if any formula has an odd number of solutions. This has no false positives. The proof is a specialization of [Fortnow's Theorem 3.1 and Lemma 3.4](https://toc.cs.uchicago.edu/articles/v005a007/). It does not replace the total parity solver with a solver for the total-language class UP: Unique-SAT has a promise that must be handled separately.

## Semantic checks

The four small circuit classes AC0, ACC0, TC0 and NC1 are nonuniform. P/poly and NP/poly also admit arbitrary advice. Every unary language therefore has an AC0 family: at each length, a circuit tests the unary word and hardwires the appropriate membership bit. Choosing an undecidable unary language witnesses noninclusion of AC0 in each of the 44 recursive classes. All **264 ordered pairs from these six nonuniform classes to the recursive classes** are consequently already settled. These facts must not be mistaken for circuit lower bounds on efficiently decidable languages. See the [classical derivation notes](classical-notes.md) and the [author textbook's advice definitions](https://theory.cs.princeton.edu/complexity/book.pdf).

NC is logspace-uniform; NC1 in this roster is not. Thus the familiar uniform-NC1-to-L simulation cannot be inserted as NC1 ⊆ L. SC requires polynomial time and polylogarithmic space simultaneously. Savitch's simulation does not establish NL ⊆ SC. A simulation with a better fixed exponent also need not separate unions over every polynomial exponent.

Counting definitions remain distinct: C=P tests an exact gap, PP tests its sign, and ⊕P tests path-count parity. Toda's upper bound uses a counting oracle; it does not say PH ⊆ PP. A lower bound saying that for every fixed exponent some language needs larger circuits does not, without further argument, give one language outside P/poly.

Oracle, promise, query and communication results require a valid transfer to the benchmark's unrelativized total languages. The same caution applies to derandomization: a statement about total BPP cannot silently substitute for a PromiseBPP algorithm inside a verifier.

## Recent-result screen

The audit inspected primary abstracts and version histories for several results close to the cutoff. These checks establish what the papers claim and which models they use; they do not validate every proof.

| Public evidence | Effect on this baseline |
| --- | --- |
| Williams, [Simulating Time in Square-Root Space](https://eccc.weizmann.ac.il/report/2025/017/), February 24, 2025 | A finer time/space simulation, not P ≠ PSPACE. |
| Bostanci, Haferkamp, Nirkhe and Zhandry, [Separating QMA from QCMA with a classical oracle](https://arxiv.org/abs/2511.09551), November 12, 2025; revised January 17, 2026 | The oracle qualification prevents an unconditional QMA ⊄ QCMA seed. |
| Volkovich, [Yet Another Proof that BPP ⊆ PH](https://eccc.weizmann.ac.il/report/2026/004/), January 16, 2026 | Reproves known containments. |
| Miloschewsky, Podder and Rudolph, [En Route to a Standard QMA1 vs. QCMA Oracle Separation](https://arxiv.org/abs/2604.26921), April 29, 2026 | Oracle models and verifier restrictions remain part of the statements. |
| Chatterjee and colleagues, [Bipartite Matching is in NC](https://eccc.weizmann.ac.il/report/2026/100/), June 14, 2026; revised June 15 and July 15 | A problem-specific algorithm claim does not establish P = NC. The June revision records a proof correction. |
| Ren and Williams, [Near-Maximum Circuit Lower Bounds for Exponential Time with Merlin-Arthur Queries](https://arxiv.org/abs/2607.09963), July 10, 2026 | The class has a promise-MA oracle and advice; removing those qualifiers would change the theorem. |

The JSON dossier also records checks of the SZK oracle-separation literature and July/August 2026 papers about bit-counting classes outside this roster. No-result searches are recorded as searches, never as proof that a question was open.

## Policy for running and scoring

1. **Freeze candidates and provenance.** A run records the exact model configuration, budget, question set and dataset version. Candidate status means absence from that version's baseline closure.
2. **Review proofs and historical eligibility separately.** Accept an exact mathematical statement and its proof under the benchmark's semantics. Before granting a point, review whether that ordered pair was already settled, directly or implicitly, before September 2, 2026 at 00:00 UTC.
3. **Review every point requested.** Implication-derived pairs count, but each still needs its own historical eligibility decision. A review can cover a family with a common argument if it identifies all covered pairs and the supporting evidence explicitly.
4. **Allow measured zeroes.** A real model run can receive an official zero once the run is reviewed and all its proof candidates are adjudicated. Unclaimed candidate pairs do not need blanket openness certification to record this result.
5. **Correct omissions retrospectively.** An overlooked pre-cutoff result earns zero. Publish the evidence, correct eligibility and recompute affected scores while preserving the original frozen run. Do not silently rewrite history or reward rediscovery of known consequences.

The historical baseline's zero is a scoring convention, not a measured AI result. ZFC-independence submissions need an exact metatheorem and explicit metatheory; independence does not propagate through ordinary relation closure.

## Limits and reproducibility

This was a focused AI-assisted review, not an exhaustive survey of every publication before the cutoff. Some primary rechecks were limited to abstracts. Historical sources with year-only metadata are identified in the knowledge base; crawl and repository dates are not substituted for original publication dates. The audit does not claim Lean proofs of existing theorems or a completed proof that every operational definition is equivalent to every textbook convention.

The JSON binds the complete `classes` and `knowledge` documents using SHA-256 over canonical UTF-8 JSON with sorted keys, compact separators and unescaped Unicode. Policy and audit contents are excluded from that graph hash to avoid a circular dependency. The release can separately hash this audit file and record that hash in its freeze manifest. Every pair has a baseline status, family group, source index, semantic flags and explicit pending-review status where appropriate.
