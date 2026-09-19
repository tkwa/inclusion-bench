**Coverage audit — draft for the 2026-09-01 cutoff**

The roster can measure broad progress on relationships between complexity classes. It cannot guarantee a point for every major complexity-theory advance. The accompanying [50-scenario stress test](coverage.json) maps 35 scenarios directly to an ordered pair and one through a short reduction. Fourteen have no guaranteed scoring implication. These are design examples, not a ranking of the 50 most likely discoveries. Their order carries no forecast probability.

| Classification | Scenarios | Meaning |
| --- | ---: | --- |
| Direct | 35 | The proposed theorem is an inclusion or noninclusion between roster classes. |
| Consequence | 1 | A short argument turns the proposed theorem into a roster inclusion. |
| Unsupported | 14 | No scored implication is established in this release. |
| Certified eligible | 0 | Historical eligibility still requires a cutoff audit. |

The distinction between a mapped pair and an eligible point matters. A traversal that cannot derive an inclusion does not establish that the inclusion was open on September 1, 2026. The source records in [quantum.json](quantum.json) support particular baseline facts; they do not certify the absence of other results. Freeze an eligibility manifest only after review of both directions, relevant class conventions and pre-cutoff literature versions.

The four small circuit classes are nonuniform. That choice represents questions such as whether NEXP has polynomial-size threshold circuits and whether NC¹ exceeds TC⁰. It also means these classes contain undecidable languages determined solely by input length. Edges from nonuniform NC¹ to L, or from nonuniform AC⁰ to P, would therefore be false. NC is a separate, logspace-uniform class. Arbitrary advice in P/poly and NP/poly must remain arbitrary throughout the definitions and scorer.

The main coverage gaps are mathematical, rather than a matter of adding a few more class names:

- **Individual algorithms.** A polynomial-time graph-isomorphism algorithm could be a major result without deciding every SPP or NP language. [Babai's quasipolynomial algorithm](https://arxiv.org/abs/1512.03547) illustrates how much progress is possible within existing class bounds. Factoring and explicit combinatorial constructions have the same issue.
- **Quantitative bounds.** A better polynomial exponent does not separate classes defined by a union over all polynomial bounds. This is already visible before the cutoff: [Chen, Tal and Wang's 2026 depth-two threshold lower bound](https://eccc.weizmann.ac.il/report/2026/039/) is a substantial advance, but it does not establish NEXP outside TC⁰. The hard language, fixed depth and fixed exponent must all be tracked.
- **Promise problems.** A promise-class inclusion implies the corresponding total-language inclusion. A promise-only separation need not imply a total-language separation. The scenario file distinguishes these cases explicitly for QMA and QCMA. A new promise track would need its own definitions and baseline, rather than reusing language labels silently.
- **Search, functions and algebra.** PPAD, function-valued #P and algebraic VP/VNP do not belong in the same untyped inclusion matrix as languages. There can be consequences across these settings: if every TFNP problem has a polynomial-time solver, then NP ∩ coNP is contained in P. The scenario file supplies that reduction. No analogous consequence is assumed for PPAD alone.
- **Relativization and proof systems.** The [2025 classical-oracle QMA/QCMA separation](https://arxiv.org/abs/2511.09551) does not resolve the unrelativized pair. A lower bound against one propositional proof system likewise need not separate NP and coNP.

Two tempting implication rules are deliberately absent. Total-language BPP=P does not automatically derandomize the promise problem faced by an MA verifier. Also, [Kabanets–Impagliazzo](https://www.cs.sfu.ca/~kabanets/Research/poly.html) derive a disjunction of Boolean and arithmetic circuit lower bounds from PIT derandomization; the arithmetic branch need not settle a Boolean roster pair. The scorer should preserve such disjunctions if a future version supports them, and must not select a convenient branch.

The accepted 50-class roster omits NISZK. That trades away a recognized zero-knowledge question, although restoring its name alone would not fix the promise-language gap. Future expansions should use separate typed tracks for promise problems, algorithms and explicit constructions, quantitative bounds, total search, and algebraic complexity. Those tracks need independently defined points; mixing them into this matrix would change what an inclusion means.
