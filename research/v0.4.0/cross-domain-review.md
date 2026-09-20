# Independent cross-review of the total-language roster

Review date: September 20, 2026. Mathematical cutoff: September 1, 2026. Inputs: [classical landscape](classical-landscape.md), [counting and scope landscape](counting-and-scope-landscape.md), and the separate [quantum landscape](quantum-randomness-landscape.md). This review proposes a fifty-endpoint comparison, with no canonical data changes or expansion of the problem universe.

**I favor the classical review's broader space comparison B: add BPL, UL, PL, BQL, ∃R, P^PP, CH, QMA(2), StoqMA, and QSZK; demote AC0, coUP, coMA, coAM, coQMA, FewP, LWPP, WPP, coRP, and E to background.** Every scored endpoint remains a class of total binary languages. The quantum proof classes therefore mean their total restrictions, not an unannounced promise track.

This is a defensible allocation, not an optimum. Its strongest losses are positive fine-counting collapses, exact linear-exponential deterministic comparisons, direct complement interfaces, and the continued lack of a uniform NC¹ endpoint. Its strongest gain is a set of distinct questions about small-space randomness, unambiguity, quantum computation, real feasibility, adaptive counting, iterated counting, and quantum verification. I did not use implementation effort or expected proof tractability to choose these slots.

## Findings that affect mathematical meaning

**State polynomial runtime explicitly for BPL and BQL.** The classical dossier's requirement that every random tape halt can imply a polynomial bound in a standard fresh-coin machine with polynomially many configurations: a reachable directed cycle would permit an infinite sequence of coin choices. That is not the same as halting with probability one, and it depends on the random-tape access model. The implementation should require one polynomial worst-case bound directly, with logarithmic workspace and read-only input. Le Gall–Nishimura–Yakaryılmaz distinguish BPL from unrestricted-time BPL(∞), and give `L ⊆ BPL ⊆ BQL ⊆ PL`. Their unrestricted-time bounded-error quantum class equals PL. Omitting BQL's time bound would therefore identify a different endpoint. [*Quantum Logarithmic Space and Post-selection*, 2021, §§2.1–2.3 and §3.4](https://arxiv.org/abs/2105.02681).

**An added uniform NC¹ must use its declared small-circuit uniformity.** The recommendation for DLOGTIME-uniform NC¹ is sound. A logspace machine that prints circuits is not automatically a DLOGTIME direct-connection procedure. Specify gate indexing, random access, and the local circuit questions answered within the time bound; do not silently weaken the convention to reuse a transducer library. The current nonuniform NC¹ should remain separately named because its formula lower-bound questions are different. [Barrington–Immerman–Straubing, *On uniformity within NC¹*, 1990](https://doi.org/10.1016/0022-0000(90)90022-D). The full theorem was not re-proved in this review; this is an agreement with the dossier's model distinction, not a new equivalence claim.

**P^PP, PP^PP, and CH should remain distinct.** The counting review correctly distinguishes deterministic adaptive counting queries from a majority machine with a counting oracle. P^PP = P^#P is a decision-class identity; neither is the function class #P. Fortnow's survey explicitly highlights the PSPACE comparison and separates truth-table closure from the adaptive oracle question. [*My Favorite Ten Complexity Theorems*, §§2.8–2.9](https://lance.fortnow.com/papers/files/topten.pdf). This is substantial importance evidence for the extra endpoint, independent of a desire to include the familiar string “#P.”

I independently checked the two proposed collapse equivalences. Let `D=P^PP`. Flattening a deterministic D-oracle computation inside a probabilistic machine gives `PP^D=PP^PP`, using a fixed oracle and polynomial overhead. Thus `PP^PP=D` makes the next counting level equal to D and induction collapses CH to D. Conversely, `CH=D` immediately contains the second level in D. The analogous induction proves `PP^PP=PP` iff `CH=PP`. These arguments do **not** prove that `D=PP` implies `PP^PP=PP`: determinism in D is the missing resource. The counting dossier's refusal to insert that converse is correct.

CH means a union over **fixed finite** levels. Allowing the level to grow with input length would change the class. It also should not be advertised as having a standard complete language like a fixed level unless a suitable collapse or another convention is supplied. The definition in the counting dossier is adequate; implementation should preserve the quantifier order.

**∃R is a high-value total-language addition.** It gains comparisons with NP, PH, and PSPACE, and connects many natural finite geometric descriptions through completeness. Those comparisons are not reproduced by P versus NP: an NP algorithm for all real feasibility, a PH upper bound, and PSPACE-hardness are different conclusions. The primary compendium explicitly discusses these interfaces and the obstacle of witnesses requiring large precision. [Schaefer–Cardinal–Miltzow, 2024, §§1.1–1.3](https://arxiv.org/html/2407.18006v1#S1.SS1).

The definition must retain binary encodings and integer or rational coefficients. Real-valued BSS input, arbitrary built-in real constants, or a polynomial-bit rational certificate substitute would change the problem. Likewise, a quantum witness's real amplitudes do not establish ∃R ⊆ QMA: efficient verification must still have the required gap. No such extra containment is proposed here. The strongest objection to this addition is that a particular geometric breakthrough may only improve one member problem, not the entire class. That objection also applies to familiar classes such as SPP and SZK; it does not erase ∃R's well-developed complete-problem family.

**StoqMA needs the threshold union proposed in the quantum review.** There is now a concrete warning beyond “amplification is open”: Liu proves that the perfect-soundness boundary, the union of StoqMA(a,1/2) over a>1/2, equals NP. Choosing that boundary as a convenient canonical fixed soundness would miss the intended class. [*StoqMA Meets Distribution Testing*, TQC 2021, Corollary 24](https://drops.dagstuhl.de/storage/00lipics/lipics-vol197-tqc2021/LIPIcs.TQC.2021.4/LIPIcs.TQC.2021.4.pdf). Use explicit efficiently describable thresholds with inverse-polynomial separation; do not assert every allowed parameter choice is equivalent.

## Why the counting changes are defensible—and what they lose

Moving from ten current counting/ambiguity classes to the eight `UP, SPP, C=P, PP, ⊕P, AWPP, P^PP, CH` exchanges several fine distinctions for adaptive and iterated counting. That is a scientific tradeoff, not a removal of aliases. I agree with the proposed eight as the starting point for a broad total-language roster.

FewP remains the strongest candidate to restore if an extra counting slot is available. An equality FewP=UP need not collapse any retained pair, while its inequality separates NP from UP. The asymmetry matters: keeping only the coarse upper endpoint preferentially preserves negative results. The same issue affects LWPP=WPP. A serious benchmark should publish these lost positive targets, rather than describe all lost points as duplicate complement weighting.

The best case for retaining LWPP is its exact-normalization structure and algorithmic applications; the best case for WPP is that input-dependent normalization and closure questions are genuinely different. Their demotion is justified here by the unrepresented oracle and cross-field questions, not by a judgment that exact counting is unimportant. The counting dossier documents enough primary evidence for this tradeoff to be reviewable.

P^PP and CH are not both mandatory. A seven-class counting block with CH but no P^PP creates another slot, but loses direct adaptive-closure and deterministic-counting-versus-PSPACE questions. A fixed `PP^PP` node has natural complete problems and finer middle-level comparisons, but loses the full-hierarchy endpoint if substituted for CH. Both alternatives are sensible; the preferred pair covers a broader range of named structural questions.

## Fifty total-language endpoints

The names below are provisional identifiers, not permission to replace existing definitions. `PSharpP` denotes P^PP = P^#P with deterministic adaptive access; `ExistsR` denotes binary-encoded existential real feasibility under polynomial-time many-one reductions. All quantum rows impose their gap conditions on every binary input.

| Group for reading convenience | Endpoints | Count |
|---|---|---:|
| Circuits and advice | ACC0, TC0, NC1 (nonuniform), Ppoly, NPpoly | 5 |
| Space and parallelism | L, UL, NL, BPL, PL, LogCFL, NC, SC, BQL, PSPACE, EXPSPACE | 11 |
| Time, nondeterminism, real feasibility | P, NP, coNP, NPcapcoNP, ExistsR, NE, EXP, NEXP | 8 |
| Randomness and classical proof systems | RP, ZPP, BPP, MA, AM, SBP, SZK | 7 |
| Counting and unambiguity | UP, SPP, CeqP, PP, parityP, AWPP, PSharpP, CH | 8 |
| Quantum computation and verification | BQP, QCMA, QMA, QMA2, StoqMA, QSZK | 6 |
| Higher polynomial hierarchy | Sigma2P, Pi2P, Delta2P, Theta2P, PH | 5 |

These groups overlap scientifically; eleven entries under “space” is not evidence that exactly 22% of the science is space complexity. PL is also counting, BQL is quantum, and PSPACE connects every other group. The reasons for the three nearby additions BPL, PL, and BQL are their different randomness, counting, and quantum resources. The BQL case is especially suitable for this scope because the 2025 connectivity work includes a natural total-language example. [Apers–Edenhofer, Theorem 4](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.18).

I prefer demoting **E rather than NE** for these two extra space slots. Both have substantial outgoing overlap with their padded exponential counterparts, while the classical dossier's single-demotion experiment found more ordinary outcomes with no retained consequence for NE. That calculation is only supporting evidence: simultaneous demotions can behave differently, and independence does not propagate. E's importance in quantitative circuit hardness is real, but those quantitative hypotheses are not faithfully represented by the existing one-point polynomial-class matrix anyway. Retaining E as a background node preserves the exact hypothesis vocabulary.

Keep NPcapcoNP and NPpoly in this conservative comparison. The former is a whole certificate-on-both-sides class, not an alias for a few attractive member problems. The latter distinguishes positive nondeterministic-circuit upper bounds and the coNP-in-NP/poly hypothesis used in compression lower bounds. Keep EXPSPACE as well: its small number of remaining comparisons includes genuine time–space questions, which cannot be dismissed solely by degree.

## Alternatives that survive cross-review

- **Uniform parallelism emphasis:** replace Pi2P with DLOGTIME-uniform NC1, retaining Pi2P as background. This adds the exact uniform NC¹/L frontier. It changes complement weighting and can lose asymmetric higher-hierarchy questions.
- **Symmetric verification emphasis:** replace Pi2P with S2P. This gains a different collapse target, but still leaves uniform NC¹ absent.
- **Fine ambiguity emphasis:** restore FewP in place of CH. This restores a positive ambiguity collapse while losing the full counting-hierarchy frontier. It is a real preference, not a simplification.
- **Foundational quantum emphasis:** replace QSZK with gate-specified QMA1. This exposes perfect completeness, but loses state-distinguishability/zero-knowledge interfaces; its total-language target still does not cover every promise statement.
- **More conservative migration:** keep the classical A roster, with E and coRP instead of PL and BQL. This protects more old endpoint wording but misses two substantial resource comparisons.

For the constrained total roster I would not add QPCP ahead of these choices. Its importance is exceptionally strong, but the canonical quantum PCP conjecture quantifies over promise QMA problems and the reduction model is delicate. A total-restricted QPCP node is legitimate; presenting its inclusion as complete coverage of the canonical conjecture would be misleading. This is a representation argument, not an argument that quantum PCPs are less important or harder to formalize.

Before freezing a roster, rerun loss scenarios for the complete simultaneous cut, separately for inclusion, noninclusion, and independence. The existing single-node results are not additive. Audit all selected new endpoints against the exact conventions above, and retain a public list of named major questions that still have no guaranteed scoring route. This review establishes a defensible candidate set; it does not claim that fifty total-language classes exhaust complexity theory.
