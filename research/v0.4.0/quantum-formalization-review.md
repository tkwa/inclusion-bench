# Independent review of the new quantum definitions

**No blocking semantic defect was found** in the reviewed QMA(2), BQL, StoqMA, or QSZK definitions. The review checked the actual state transformations, generator constraints, resource accounting, and quantifier order. It also produced five Lean regression checks aimed at definitions that could accidentally denote a different class.

This is an AI-assisted review by a different author role, recorded September 20, 2026. It is not human expert certification or a proof of every textbook equivalence. The [JSON report](quantum-formalization-review.json) records16 individual checks, exact file hashes and line references, the checked theorem names, and the remaining trusted bridges. No authored model definition was changed during this review.

## Shared circuit and generator boundary

[Quantum.lean](../../quantum/InclusionQuantum/Quantum.lean#L44) gives the verifier exactly H, T, X, and CNOT gates. Every wire is a `Fin` index; CNOT requires different control and target wires. The H formula has the correct sign on the one output, and T has the fixed algebraic phase `(1+i)/sqrt(2)`. These are explicit linear transformations, rather than arbitrary matrices supplied by a verifier. The existing normalization module proves norm preservation for these exact formulas and the input/witness/ancilla embedding.

The circuit description contains its width, output wire, gate count, and every gate tag and index. A concrete transducer must emit the complete description. Natural-number encoding is injective, records have fixed arity, and gate fields distinguish the constructors. A family cannot choose an unrecorded gate or width using uncomputable advice.

[Transducers.lean](../../lean/InclusionBench/Transducers.lean#L26) was included in the review because circuit uniformity depends on its boundary. A transition sees only finite control, one input symbol, and one work symbol. The append-only output is unreadable; neither its length nor the externally supplied evaluation horizon is available to the transition function. Each step emits at most one bit, so polynomial runtime bounds serialized output length. A machine is selected before the universal quantifier over inputs.

## QMA(2): the product restriction is real

[Unentangled.lean:63](../../quantum/InclusionQuantum/Unentangled.lean#L63) multiplies the amplitudes of two separately indexed states. The split/join maps are inverse bijections, so the two registers neither overlap nor omit basis coordinates. The proof of norm factorization establishes that separately normalized witnesses yield a normalized joint state.

The [class definition](../../quantum/InclusionQuantum/Unentangled.lean#L104) chooses polynomial witness and ancilla lengths, then one uniform verifier. On a yes input, some normalized pair must achieve completeness; on a no input, **every** normalized pair must obey soundness. There is no arbitrary joint-state parameter and no selected-witness restriction on the no side. Each binary input has an obligation.

The independent checks go beyond recognizing the tensor-product notation. `product_minor_vanishes` proves that every two-by-two coefficient minor of a product state is zero. `correlated_state_not_product` then proves that the diagonal Bell pattern with any nonzero amplitude cannot be supplied through that interface. Choosing amplitude `1/sqrt(2)` gives the familiar normalized example; the obstruction itself is stronger because it does not assume normalization of the proposed factors.

The remaining bridge is the usual equivalence between pure-product witnesses and separable mixtures, together with QMA(2) amplification and universal-gate normalization. A separable mixture cannot outperform its best pure-product component for a linear acceptance test. These mathematical facts are not silently introduced as Lean axioms. [Harrow–Montanaro](https://arxiv.org/abs/1001.0017) is the cited source for the broader verifier conventions.

## BQL: both parts of the computer have bounds

[Logspace.lean:30](../../quantum/InclusionQuantum/Logspace.lean#L30) requires the classical generator to halt in polynomial time and to obey its logarithmic workspace bound on **every prefix** through that horizon. It operates on the actual read-only input. The quantum circuit starts on zero qubits rather than an uncharged copy of the entire input, and its width is logarithmic. Its gate count has a polynomial bound.

The existential `width : Nat → Nat` initially looks like a possible advice channel. It is constrained by the first field of the exact serialized output. The independent theorem `serialized_width_determined` proves that two equal serializations, even at different type-level widths, force those widths to be equal. Together with the concrete generator, this removes that channel. Allowing only a length-dependent width is harmless: standard circuits whose widths depend on the input can pad to a computable logarithmic upper bound.

The source match is particularly direct. [Fefferman–Remscrim, Definitions4–5](https://arxiv.org/pdf/2006.03530), explicitly uses input-dependent DSPACE(s)-uniform circuits, names H/CNOT/T as a universal gate set, and starts the quantum register at zero. Its Theorem1 connects unitary and general-measurement space-bounded computation. At logarithmic space the stated time bound is polynomial. The benchmark therefore does not rely only on an informal analogy between a circuit model and a quantum Turing machine.

The stored gate list is a mathematical description, not a readable extra work tape granted to the controller. It can be generated and executed as a stream using a logarithmic-size gate parser. Exact tape-model and serialization simulations are still trusted equivalence bridges. Removing the polynomial clock or replacing the generator with unrestricted polynomial-time preprocessing would change the definition; neither change is present.

## StoqMA: restricted gates and an explicit threshold union

[Stoquastic.lean:31](../../quantum/InclusionQuantum/Stoquastic.lean#L31) allows only NOT, CNOT, and Toffoli in the verifier. The Toffoli indices are pairwise distinct. H gates appear only when preparing plus ancillas and when implementing the final X-basis measurement. `plusAcceptance` accepts computational zero after that H, which is the plus outcome. No internal H/T circuit is hidden inside the reversible gate type.

The [threshold structure](../../quantum/InclusionQuantum/Stoquastic.lean#L172) contains actual FP integer functions, evaluated on unary input length. If their values are `a,b,d`, validity gives

`d > 0`, `d ≤ 2b`, `b < a ≤ d`, and `d ≤ p(n)(a-b)`.

Consequently the rational thresholds satisfy `1/2 ≤ b/d < a/d ≤ 1`, with reciprocal-polynomial gap. The independent `stoq_threshold_integer_sanity` theorem checks positive denominator, positive soundness numerator, correct ordering, and a nonzero gap polynomial. The denominator may be large, but its bit string must be emitted by a polynomial-time transducer; it cannot encode arbitrary length advice.

The endpoint is expressly a **union over efficiently computable rational threshold pairs**. It does not identify all individual parameter settings. This matters because general StoqMA amplification is open and the exact soundness-one-half boundary is special. The verifier and witness conventions match [Aharonov–Grilo–Liu, Definition2.3 and Remarks2.4–2.5](https://arxiv.org/html/2010.02835v4). The selected union, rather than a silently chosen fixed gap, must remain visible in the class catalog and source bindings.

## QSZK: compare mixed outputs, not their purifications

[Statistical.lean:38](../../quantum/InclusionQuantum/Statistical.lean#L38) defines a measurement by finite matrix multiplication, norm preservation on every vector, and a subset of output outcomes. In equal finite dimensions this is a unitary basis change followed by a binary projective measurement. Such measurements attain the optimal distinguishing probability for two density matrices. Their unrestricted complexity is appropriate for the mathematical trace distance; no sampler can invoke this measurement as a computational oracle.

The crucial implementation is [the probability formula at line50](../../quantum/InclusionQuantum/Statistical.lean#L50). For each fixed environment basis label, the matrix acts only on the retained output slice. Squared magnitudes are then summed over environment labels. This is precisely the probability after discarding that register, with output coherence retained and environment sectors summed incoherently. Different sampler environments are allowed, while their output dimensions agree.

The independent `environment_sign_invisible` theorem proves that an arbitrary sign change depending only on the discarded environment label leaves **every** permitted output measurement probability unchanged. This excludes a serious alternative definition: Bell states of opposite phase are distinguishable on the whole purification, yet have identical one-register outputs. A measurement of the full state would fail this check.

Both samplers start at zero and run circuits emitted by concrete polynomial-time transducers. Their output and environment lengths are polynomials. They cannot supply arbitrary mixed states, witnesses, or amplitude tables. The stored `Circuit.output` field is unused during state generation; it does not trigger an extra measurement.

The far and close predicates use absolute acceptance-probability differences, hence the **half trace norm** convention. Every member must have distance at least2/3 and every nonmember at most1/3. These constants satisfy the QSD polarization condition. For strict inequalities in a source statement, use the interior thresholds3/8 and5/8. [Watrous, the QSD definition and Theorems1,4–6](https://arxiv.org/pdf/quant-ph/0202111), supplies the relevant complete-problem framework. The variational trace-distance identity, polarization, and full-versus-honest-verifier equivalence remain trusted mathematical bridges, not results established merely by compiling this file.

## Preserved checks and validation

The new [SemanticChecks.lean](../../quantum/InclusionQuantum/SemanticChecks.lean) contains these checked declarations in `InclusionBench.Quantum.Review`:

- `product_minor_vanishes`
- `correlated_state_not_product`
- `environment_sign_invisible`
- `serialized_width_determined`
- `stoq_threshold_integer_sanity`

Their proof bodies passed Lean4.19.0 on the authorized Ubuntu host with one CPU, one Lean worker, and an8GiB process address-space limit. Only the standard foundational axioms appeared. The exact tracked module, including its documentation, subsequently passed the full combined core and quantum build with exit code0. All five required axiom audits passed, without warnings or errors. Its source SHA-256 is `e08ab15bb8f9368058ee7d1b158bd154cdd9516fcb089381388bec007e1ee142`; the JSON records the build-log hash.

The two new quantum conditional rules were also checked against [Vinkhuijzen–Deutz, Theorems4 and11](https://eccc.weizmann.ac.il/report/2019/131/download/). PP ⊆ QMA yields PSharpP ⊆ PP by closure of QMA∩coQMA under deterministic Turing reductions. QMA ⊆ coQMA yields equality after complementing, and therefore PH ⊆ QMA. Neither argument supplies a general counting-hierarchy collapse.

These checks address particular failure modes; they do not replace the listed model-equivalence theorems. The baseline policy may trust those cited existing theorems. A future fully internalized development could prove Helstrom equivalence, all generator-model translations, amplification, and the complete-problem bridges, but no such unfinished proof was used to justify a false operational-definition claim here.
