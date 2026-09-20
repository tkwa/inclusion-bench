# Independent review of the quantum and randomness roster proposal

Reviewed September 20, 2026, using sources available by September 1, 2026. This review concerns `quantum-randomness-landscape.md`, snapshot SHA-256 `0cd978d7c8b7f5e88598c6ca00351e1b3f974af3580a0d91091f3e4c55e1b9a7`. It does not edit that proposal or certify new baseline labels.

The proposal's main scientific cases are sound. It correctly distinguishes promise classes from their total-language restrictions, treats gate-dependent perfect completeness separately, and avoids presenting all the candidate additions as mandatory. I support QMA(2), StoqMA, and a space-randomness extension as serious additions to a language roster. QSZK is also a strong choice. QPCP and QMA₁ have especially compelling canonical questions, but the total-language matrix does not fully represent those questions.

The principal new finding is a concrete StoqMA threshold trap: **soundness exactly 1/2 gives an NP variant, not a harmless normal form for general StoqMA**. This should be resolved in the definition specification before implementation. The proposal already warns that amplification is open; the result below makes that warning actionable.

## Candidate judgments and the strongest objections

| Candidate | Independent judgment | Strongest scientific reason against allocating a slot |
|---|---|---|
| QMA(2) | Strong addition; keep two product witnesses, with ordinary constant-gap semantics. | A total-only row incompletely covers QMA(2) versus QMA. Many important short-witness or restricted-measurement results do not resolve the broad class. |
| StoqMA | Strong addition if its threshold family is explicit. | Hamiltonian algorithms often concern a restricted interaction graph or gap regime. The whole-class question gives only partial coverage of that physics program. |
| QSZK | Strong alternative or addition; simulation and state distinguishability are distinct from witness restrictions. | Its canonical complete problems and cryptographic motivations are promise problems; a total restriction loses some of that coverage. |
| BPL | Strong cross-field addition. | RL and other error conventions compete for the same space-randomness program; do not count all of them as unrelated missing fields. |
| BQL | Strong addition, particularly under a language-only constraint. | Choosing it uses a slot that could represent a different resource family; individual numerical algorithms need not settle BQL versus BPL. |
| QPCP[O(1)] | Strong in a promise track; more conditional in a total-only portfolio. | A total inclusion is weaker than the canonical quantum PCP conjecture, and a negative Hamiltonian result may address a reduction notion different from the selected endpoint. |
| QMA₁ | Foundational and defensible; gate identity must be part of the target. | A perfect-completeness result for a different exact gate model or only a promise subclass is not automatically the selected inclusion. |
| NISZK | Defensible interaction-focused choice. | Adding it while removing several unrelated fields can overweight protocol variants; the setup and promise convention are substantial. |
| QIP(2) | Defensible if interaction is a deliberate emphasis. | QMA, QSZK, and PSPACE already capture some nearby questions; a fixed-message refinement must justify its slot against omitted algebraic or search directions. |

These are opportunity costs, not difficulty estimates. I would not reject any candidate because its Lean definition is lengthy. Under a strict language-only scope, I give BQL more weight than the proposal's smallest compromise does: it provides a genuine space axis and now has a primary total-language example. Choosing QSZK instead is reasonable if the final portfolio emphasizes zero knowledge. I would not claim that this is an objectively measured ordering.

The seven-face survey distinguishes the verification models and explains why they are not interchangeable. Its discussion also shows why a single upper bound or promise-complete example is insufficient to advertise complete coverage of a research program. [Gharibian, *The 7 Faces of Quantum NP*, §§4–7](https://arxiv.org/pdf/2310.18010v1).

## Promise-to-total transfer: accepted, with its assumptions stated

For a promise class C, define `Tot(C)` to contain the languages L whose total promise problem `(L, complement L)` lies in C. Then:

- `C⊆D` implies `Tot(C)⊆Tot(D)`.
- A witness to `Tot(C)⊄Tot(D)` is also a promise witness to `C⊄D`.
- Neither converse follows merely from these definitions.

The obstacle is real: outside its promise, a bounded-error verifier can have an intermediate acceptance probability. Merely assigning that input a yes/no label does not repair the gap. The proposal correctly does not transfer a promise separation to a total-language separation. Watrous explicitly sets his principal quantum classes in the universe of promise problems. [*Quantum Computational Complexity*, §II.1](https://arxiv.org/pdf/0804.3401).

The proposed NEXP exception is valid under the ordinary global resource convention. Given a promise NEXP machine M with an exponential running-time bound, its acceptance language `L(M)` is a total NEXP completion of the promised yes/no sets. If every total NEXP language has a total QMA(2) verifier, apply that assertion to `L(M)` and restrict the resulting verifier to the original promise. Consequently,

`Tot(NEXP)⊆Tot(QMA(2))  ⇒  prNEXP⊆prQMA(2)`.

The same completion argument works for deterministic P/PSPACE and existential NP with their standard all-input resource bounds. This does not grant a completion property to QMA, QCMA, QMA(2), or QPCP. It also does not assert that every verifier is a recognizer outside its promise. These distinctions should be encoded as explicit bridge theorems, not a general rule that erases the promise type.

## StoqMA: specify a union, and preserve the boundary distinction

Aharonov–Grilo–Liu's Definition 2.3 uses NOT, CNOT, and Toffoli gates; zero and plus ancillas; and a single final Hadamard-basis measurement. Its thresholds satisfy an inverse-polynomial separation. The text explains why ordinary majority amplification does not preserve this verifier model. Thus selecting fixed 2/3-versus-1/3 thresholds would fail even at the level of the intended acceptance range. [*StoqMA vs. MA: The Power of Error Reduction*, Definition 2.3 and Remarks 2.4–2.5](https://arxiv.org/pdf/2010.02835v4).

There is a sharper boundary theorem. Liu proves

`union over a>1/2 of StoqMA(a,1/2) = NP`.

The theorem holds even when the positive gap is very small. It is therefore unsafe to simplify a general StoqMA endpoint to perfect soundness 1/2, or to copy an informal statement of parameter equivalence over a closed threshold range. [*StoqMA Meets Distribution Testing*, Corollary 24, Proposition 23, and Appendix A.3](https://drops.dagstuhl.de/storage/00lipics/lipics-vol197-tqc2021/LIPIcs.TQC.2021.4/LIPIcs.TQC.2021.4.pdf).

A direct way to understand the issue is that the acceptance operator of the prescribed nonnegative verifier is `I/2+K`, where K has nonnegative entries. A strictly positive contribution can be witnessed by compatible basis and coin strings; no-instances at threshold 1/2 have no such contribution. This explanation is an independent reconstruction of the certificate mechanism, not an additional baseline theorem.

For the new node, use an explicit union over efficiently specified rational threshold functions a(n), b(n), with `1/2≤b(n)<a(n)≤1` and `a(n)−b(n)≥1/p(n)` for a fixed polynomial p. State the representation and uniform computation of those thresholds. Including the NP boundary cases inside that union is harmless; **identifying the union with the boundary slice is not**. If a different fixed-threshold definition is chosen, it needs a source proving equivalence to the intended union. Neither this recommendation nor the known NP boundary is an argument against StoqMA's scientific value.

## QMA(2): accepted model and amplification scope

For the usual endpoint, completeness supplies two independently prepared registers and soundness quantifies over every product witness across their designated bipartition. Arbitrary entanglement within each register is allowed. Allowing convex mixtures of product states does not change the optimum for a fixed linear acceptance functional; allowing entanglement across the two registers changes the problem.

Harrow–Montanaro's Theorem 9 supports amplification and collapse of polynomially many unentangled proofs to two in the stated inverse-polynomial-gap regimes. The surrounding analysis also gives the NEXP upper bound. This supports the proposal's use of QMA(2), and its decision not to spend extra slots on QMA(3) and QMA(poly). It does not justify importing a logarithmic-witness or exponentially small gap result into ordinary constant-gap QMA(2). [*Testing Product States, Quantum Merlin–Arthur Games and Tensor Optimisation*, Theorem 9 and §3.1](https://arxiv.org/pdf/1001.0017).

A future implementation may choose pure product witnesses as the operational definition and separately prove the convex-mixture equivalence. The important scientific condition is the bipartition constraint, not the internal density-matrix representation chosen for the verifier.

## QPCP: the canonical question is accurately identified

The proposal's QPCP endpoint is supported by Buhrman–Helsen–Weggemans' Definition 5: one polynomial-size quantum proof, polynomial-time uniform verification, a constant number of accessed proof qubits, and fixed bounded error. Their adaptive model measures the next index after acting on workspace and previously accessed proof qubits. It is not unrestricted coherent access to the entire proof through an unspecified random-access oracle. Their constant-query adaptivity theorem permits a nonadaptive equivalent with its own proof. [*Quantum PCPs*, Definitions 4–5 and Theorem 3](https://arxiv.org/pdf/2403.04841v3).

The union over constant query bounds should be explicit. Local-Hamiltonian formulations require the reduction and normalization convention stated in the source; this review accepts the proposal's warning that classical deterministic reductions are not silently interchangeable with its quantum reduction. A bound on the number of qubits actually touched is central. Merely placing a constant number of gates labeled “query” in a model that gives each such gate global proof access would not formalize this endpoint.

The strongest selection objection is scope: under a total-only matrix, the natural missing inclusion becomes `Tot(QMA)⊆Tot(QPCP)`, which need not resolve the full promise conjecture. It remains a legitimate question, but its headline should say exactly that. A known restricted-Hamiltonian approximation algorithm need not refute the selected whole-class inclusion either.

## QMA₁: exactness is part of the scientific identity

Gosset–Nagaj explicitly fix `{H,T,CNOT}` and require probability exactly one on yes instances. They state that QMA₁'s gate-set independence is not known in that framework. They also distinguish exact projector measurement from approximation. This independently confirms the proposal's gate warning. [*Quantum 3-SAT is QMA₁-Complete*, §2, Definition 2, and the projector-encoding discussion](https://arxiv.org/pdf/1302.0290).

Approximate universality cannot be used alone to transfer exact completeness. Fix the gate set, allowed intermediate measurements, classical controls, and input representation before the historical audit. The pre-cutoff case for studying perfect completeness is ample; post-cutoff claims should neither change its eligibility nor make it attractive because a new answer may have entered model training. This review does not adjudicate those later claims.

## BQL: a particularly good language-only bridge

Fefferman–Remscrim establish equivalence of unitary and general bounded-error quantum space using a space-efficient argument. Their circuit families have space-bounded uniformity and the associated `2^O(s)` time scale, which is polynomial at logarithmic space. This supports equivalence of the intended models, not permission for a polynomial-space classical controller around a logarithmic quantum register. [*Eliminating Intermediate Measurements in Space-Bounded Quantum Computation*, Theorem 1 and definitions in §2](https://arxiv.org/pdf/2006.03530).

Apers–Edenhofer's Theorem 4 is indeed a total language: its input includes a unary bound k, and the language requires both the path-bound condition and s–t connectivity. Their algorithm checks the relevant structural condition rather than assuming it as a promise. This independently confirms the proposal's most useful evidence for BQL under a total-only scope. [*Directed st-Connectivity with Few Paths Is in Quantum Logspace*, Theorem 4 and §3.2](https://drops.dagstuhl.de/storage/00lipics/lipics-vol339-ccc2025/LIPIcs.CCC.2025.18/LIPIcs.CCC.2025.18.pdf).

That example must not become a claimed ordinary separation: it is not known to lie in BPL, which is different from a proof that it does not. As with the other additions, the full all-pairs historical audit remains future work after the endpoint is selected.

## Independent check of the counting-hierarchy algebra

The counting review proposed two collapse equivalences. Both survive a direct oracle simulation check.

Let `D=P^PP` and `C₂=PP^PP`. If a fixed language A belongs to D, choose a fixed B∈PP and a deterministic polynomial-time B-oracle machine deciding A. An outer PP machine querying A can simulate that deterministic subroutine at each oracle call. Query lengths are polynomial in the original input length, the number of calls is polynomial, and the inner time bound is a fixed polynomial. Composition therefore remains polynomial-time.

Crucially, the inner subroutine creates no additional random or nondeterministic choices. Every outer random tape has exactly the same acceptance outcome after replacement, so the acceptance probability and strict majority condition are preserved. The same fixed B is used throughout the computation. This proves `PP^(P^PP)⊆PP^PP`; the reverse inclusion follows from `PP⊆P^PP`.

Now:

1. If C₂=PP, induction makes every counting level equal PP; conversely CH=PP contains C₂. Thus `C₂=PP iff CH=PP`.
2. If C₂=D, then `C₃=PP^D=C₂`. Induction stabilizes every higher level there, so CH=D. Conversely, `D⊆C₂⊆CH` gives C₂=D when CH=D. Thus `C₂=D iff CH=D`.

This reasoning **does not** prove that D=PP implies C₂=PP. Flattening replaces a deterministic oracle subcomputation; it does not replace an inner PP majority computation with a deterministic one. That distinction is the reason to keep adaptive PP closure separate from collapse of the counting hierarchy. These are reviewed mathematical derivations, not yet Lean-checked rules or canonical data changes.

## Review boundary

The cross-review inspected the stated primary definitions and central transfer arguments. It did not repeat the other agent's full literature search, validate every 2026 research claim, or rerun a new all-pairs baseline. The new StoqMA boundary source and the precise query/gate/space conditions should be incorporated into the selected-class specification. The broader recommendations remain editorial alternatives for the final 40–50-endpoint portfolio.
