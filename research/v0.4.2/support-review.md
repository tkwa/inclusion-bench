# Textbook support review — 2026-09-22

The support library exposes 112 kernel-proved helper theorems over 19 explicit literature premises. It leaves the frozen operational definitions and benchmark dataset unchanged. The premises use the existing-proof waiver; the helper proofs and submitted novel arguments remain subject to Lean checking. Exact statements, source locators, and model-alignment explanations are recorded in `support/registry-*.json`.

All premise names below are under `InclusionBench.Support.Literature`. The public API lives under `InclusionBench.Support` and is imported by `InclusionSupport` together with the 61 class aliases and the existing quantum interpretation.

**Counting: six premises.** Source: Fenner, Fortnow and Kurtz, [Gap-Definable Counting Classes](https://cse.sc.edu/~fenner/papers/gaps.pdf), 1994, Section 3. The author manuscript's printed pages 5–8 were inspected visually because its extracted text is corrupted.

| Premise | Source locator and exact scope |
| --- | --- |
| `sharpP_add` | Page 7, the paragraph extending closure properties to #P, Property 3 and Corollary 3.6; page 8 proof. Add two accepting-path counts. |
| `sharpP_mul` | Page 7, Property 4 and Corollary 3.6; page 8 sequential-path construction. Multiply two counts. |
| `sharpP_precompose` | Pages 7–8, Property 1 and the #P closure paragraph. Apply a total polynomial-time transformation to the input. |
| `gapP_of_fp` | Pages 6–8, Proposition 3.5 and Property 1. Include total signed binary FP functions in GapP. |
| `gapP_sum_bits` | Pages 7–8, Property 3. Sum one uniform GapP function over every binary index of one fixed polynomial length. |
| `gapP_product_range` | Pages 7–8, Property 4. Multiply one uniform GapP function over polynomially many numeric indices. |

Path multiplicities are preserved, including duplicated transitions. Every source machine has a polynomial bound on all branches. Finite branching can be encoded by binary choices while rejecting unused codes. Total preprocessing introduces no extra multiplicity, and its output length is bounded by its polynomial runtime. Signed FP values may have exponential magnitude; the bound concerns their binary length. The sum and product use the core's injective, linear-size tuple encoding. Products use unary indices smaller than a fixed polynomial and have neutral value one on the empty range. They do not multiply exponentially many factors.

**Reductions and verifier formulations: five premises.** Source: Arora and Barak, [Computational Complexity: A Modern Approach, January 2007 author draft](https://theory.cs.princeton.edu/complexity/book.pdf). Locators use this draft's printed pages.

| Premise | Source locator and exact scope |
| --- | --- |
| `polytime_identity` | Chapter 1's input/output machine model and Definition 2.7, p.43. Copy the input. |
| `polytime_compose` | Theorem 2.8(1) and proof, p.44. Compose total polynomial-time word functions. |
| `p_precompose` | Definition 2.7, Figure 2.1 and Theorem 2.8, pp.43–44. Deterministically compute a transformed input, then decide it. |
| `p_iff_decider` | Definitions 1.19–1.20, p.27; polynomial verifier convention in Definition 2.1, p.40. Replace the core existential runtime bound with an explicit total polynomial-clocked verifier. |
| `np_iff_verifier` | Definition 2.1 and Theorem 2.6 with proof, pp.40–43. Characterize NP by a single total verifier and polynomial-length certificates. |

Composition charges for the transformed input's length and the tape simulation. The P bridge uses the same deterministic machine: halting configurations stay fixed when its clock is padded. Natural coefficient lists can majorize the core polynomial bounds. The NP bridge pads choice sequences to an exact polynomial witness length, rejects invalid choices, and uses an empty randomness field. It does not supply advice. Complementing a verifier's answer, transporting predicates, composing reductions, and the coNP universal-certificate introduction are kernel-proved wrappers.

**Elementary computation and NP closure: eight premises.** These are standard elementary consequences of the same Arora–Barak model, with concrete algorithms recorded in `registry-closure.json`; the source does not present them under these Lean names.

| Premise | Source locator and concrete computation |
| --- | --- |
| `polytime_constant` | Sections 1.2 and 1.5, especially Definition 1.20, p.27. Write one fixed finite word. |
| `polytime_pair` | Section 1.2 and Theorem 2.8 proof, p.44. Run two polynomial transducers and encode their outputs as a pair. |
| `polytime_first` | Sections 1.2 and 1.5. Parse the concrete tuple and return its first field; return the empty word on malformed input. |
| `polytime_second` | Sections 1.2 and 1.5. Parse the same tuple and return its third field, the second component of the pair. |
| `polynomialPredicate_and` | Definition 1.20, p.27, and polynomial composition in Theorem 2.8, p.44. Run two total deciders and conjoin their answers. |
| `polynomialRelation_eq` | Sections 1.2 and 1.5. Parse two finite words and compare them. |
| `polynomialPredicate_forall_range` | Example 1.12, p.22; Definition 1.20, p.27; Theorem 2.8 proof, p.44. Run one uniform predicate for each index below a fixed polynomial bound. |
| `np_precompose` | Theorem 2.6 and Definition 2.7/Theorem 2.8, pp.42–44. Deterministically preprocess, then simulate the NP machine. |

The tuple encoding has length `2*(|first|+|second|)+3`. Parsing is total on malformed inputs, and all output lengths and simulation costs are polynomial. The bounded-iteration premise charges an index for its unary length: there are `q(n)` iterations, each on an input of size `O(n+q(n))`, under one uniform polynomial runtime. This supports polynomially many conditions, not universal quantification over all `2^q(n)` binary strings. An independent support review confirmed this distinction.

The 112 proved helpers include GapP arithmetic, SPP characteristic functions and Boolean operations, PP complement, reductions and completeness, P predicates, NP/coNP certificate introductions, predicate/relation Boolean operations, equality, tuple preprocessing, bounded loops, and hierarchy induction. The hierarchy module adds no premises. Its fixed-level conventions follow the frozen core, [Bürgisser's Definition 2.3 and equation (3), pp.4–5](https://eccc.weizmann.ac.il/report/2006/113/download/), and Arora–Barak's Sections 3.5, 5.2 and 5.5. Generic oracle closure remains an explicit hypothesis.

Lean 4.19.0 compiled all four nonquantum support modules and the three `Support*Tests.lean` fixtures with one worker. The fixtures include short P, NP and coNP arguments assembled from computation rules, counting algebra, complete-problem reasoning, preprocessing, and empty bounded iterations. All 131 catalog statement strings independently elaborate to their named declarations. The repository checker also audits declaration kinds and transitive axiom dependencies; isolated full-import and submission checks are separate release gates.

The new library does not formalize all of complexity theory. Its concrete polynomial-reduction closure instances cover P, NP, coNP, SPP, PP and C=P, with a proved generic complement-class transfer. BPP, PSPACE and quantum computation combinators require further reviewed interfaces. No polynomial-reduction closure is supplied for L, NC or E. Agents must still prove the novel mathematical implication and either construct their remaining polynomial computations from available rules or request review of precise existing results through the literature workflow. The unavailable motivating “CH contains something” argument has not been reproduced or assessed.
