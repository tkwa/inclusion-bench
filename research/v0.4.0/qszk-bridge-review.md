# QSZK: operational definition to the standard class

**The reviewed definition has the intended total-language QSZK meaning, subject to the standard literature and model-simulation steps listed below.** No concrete defect requiring a change to the Lean definition was found. This is a formula-level mathematical review, not a Lean proof of the complete equivalence.

The review binds `Statistical.lean` SHA-256 `ef8a9015fcc8a9faabbd0f132e58ee13bd055b241d8c5b8c8672d84891ab491f` and dataset `e929704944eba030d541cf2a12a6aa012cb7a0f10c003ca308a1dda65cd85ef5`. The [companion JSON](qszk-bridge-review.json) records every source file, source locator, formula, and remaining trusted step. It concerns the existing 61 context definitions and selected 50 endpoints; it changes neither roster nor historical classifications.

## 1. The reduced state computed by the code

Fix an input `x`. Write `m` for its output-register length and `e` for one sampler's environment length, including the extra environment qubit. Let

$$
\psi_{a,z}=\texttt{sampler.state x}(\texttt{joinBasis}(a,z)),
\qquad a\in\{0,1\}^{m},\ z\in\{0,1\}^{e}.
$$

`joinBasis` and `splitBasis` are inverse bijections, proved in [Unentangled.lean, lines 28–61](../../quantum/InclusionQuantum/Unentangled.lean#L28). Thus this is precisely a tensor-register indexing of the complete state, without missing or duplicated basis vectors. The relevant output density matrix is

$$
\boxed{\rho_{a,b}=\sum_z\psi_{a,z}\overline{\psi_{b,z}}.}\tag{1}
$$

In matrix notation, put the amplitudes in a rectangular matrix $A_{a,z}=\psi_{a,z}$. Then $\rho=AA^\dagger$: it is Hermitian and positive semidefinite, and

$$
\operatorname{Tr}\rho=\sum_{a,z}|\psi_{a,z}|^2=1.
$$

The last equality follows from `sampler_state_normalized` at [Statistical.lean, lines 158–161](../../quantum/InclusionQuantum/Statistical.lean#L158). Equation (1) is the finite partial trace of $|\psi\rangle\langle\psi|$. Each sampler may have a different environment dimension; their output dimensions must agree, which is exactly what the common `outputLength` parameter requires. The standard partial-trace entry formula is also given in [Watrous, *The Theory of Quantum Information*, §2.1.3, equation (2.34)](https://cs.uwaterloo.ca/~watrous/TQI/TQI.pdf).

The component calculations in this review are derived directly from the code. No density matrix, spectral theorem, or trace-norm identity is asserted to have been formalized merely because the sampler-normalization theorem exists.

## 2. `OutputMeasurement.probability` is the Born probability

Let $U$ be `measurement.matrix`, and let $S$ be the subset of output basis labels for which `measurement.accepts` is true. Write $D_S$ for its diagonal zero-one projector. The code's `matrixAction` is complex-linear, since

$$
(Uv)_r=\sum_a U_{r,a}v_a.
$$

The `preservesNorm` field requires $\|Uv\|^2=\|v\|^2$ for **every** complex vector $v$. Equivalently $v^\dagger(U^\dagger U-I)v=0$ for all $v$. Testing basis vectors and their sums with coefficients 1 and $i$, or using complex polarization, gives $U^\dagger U=I$. Domain and codomain are the same finite-dimensional space; hence $U$ is invertible and $UU^\dagger=I$ as well. This is a unitary matrix, not an arbitrary norm-changing map or a predicate on states.

Set $P=U^\dagger D_SU$. It is Hermitian and idempotent, so $\{P,I-P\}$ is a binary projective measurement on the output register. Expanding [Statistical.lean, lines 50–56](../../quantum/InclusionQuantum/Statistical.lean#L50) gives

$$
\begin{aligned}
p(U,S;\psi)
 &=\sum_z\sum_{r\in S}\left|\sum_a U_{r,a}\psi_{a,z}\right|^2\\
 &=\sum_{r\in S}\sum_{a,b}U_{r,a}\overline{U_{r,b}}\rho_{a,b}\\
 &=\operatorname{Tr}(D_SU\rho U^\dagger)
  =\boxed{\operatorname{Tr}(P\rho).}\tag{2}
\end{aligned}
$$

All sums are finite. The trace in (2) is real and nonnegative, despite being written with complex matrices. It therefore equals the real-valued probability returned by Lean. Equivalently it is $\langle\psi|(P\otimes I_E)|\psi\rangle$.

There are no coherent cross-terms between different environment labels: the absolute square is taken **before** summing over `rest`. Consequently the sampler exposes its reduced output state, not its purification. This also explains the already compiled `environment_sign_invisible` regression theorem in [SemanticChecks.lean, lines 63–82](../../quantum/InclusionQuantum/SemanticChecks.lean#L63).

Conversely, every orthogonal projector on this output space occurs in this representation. Choose an orthonormal basis for its image and kernel, use the adjoint basis matrix for $U$, and let `accepts` select exactly the image basis labels. Finite output labels admit this Boolean characteristic function. Rank-zero and full-rank projectors are allowed. Thus the code neither omits the optimal binary projector nor enlarges the measurement family beyond projective measurements.

## 3. The optimum is exactly half the trace norm, and is attained

Let $\rho_0,\rho_1$ be the two reduced density matrices and $\Delta=\rho_0-\rho_1$. This is Hermitian with trace zero. By the finite-dimensional spectral theorem, write

$$
\Delta=\sum_j\lambda_j|v_j\rangle\langle v_j|,
\quad \lambda_j\in\mathbb R,
\quad \sum_j\lambda_j=0.
$$

Put

$$
t=\sum_{\lambda_j>0}\lambda_j
 =-\sum_{\lambda_j<0}\lambda_j
 =\tfrac12\sum_j|\lambda_j|
 =\tfrac12\|\Delta\|_1.
$$

For every projector $P$, let $p_j=\langle v_j|P|v_j\rangle$. Since $0\le p_j\le1$,

$$
-t\le\operatorname{Tr}(P\Delta)=\sum_j\lambda_jp_j\le t.
$$

The projector $P_+$ onto the span of eigenvectors with positive eigenvalues achieves $\operatorname{Tr}(P_+\Delta)=t$. Section 2 constructs a valid `OutputMeasurement` for this projector. Therefore

$$
\boxed{
\max_{M:\,\texttt{OutputMeasurement}(m)}
 |p(M;\psi_0)-p(M;\psi_1)|
 =\tfrac12\|\rho_0-\rho_1\|_1.
}\tag{3}
$$

This is a maximum, not merely a supremum. It uses only the output register; no extra measurement ancilla is needed. The same value is optimal over arbitrary binary POVMs, but that stronger observation is unnecessary for the code. The standard state-discrimination theorem explicitly guarantees attainment by a projective measurement: [Watrous, *The Theory of Quantum Information*, Theorem 3.4, pp. 128–129](https://cs.uwaterloo.ca/~watrous/TQI/TQI.pdf).

Let $d=\tfrac12\|\rho_0-\rho_1\|_1$. With the exact order and factors in [Statistical.lean, lines 163–183](../../quantum/InclusionQuantum/Statistical.lean#L163), equation (3) implies

$$
\begin{aligned}
\texttt{quantumFar(first,second,x)}&\iff d\ge2/3,\\
\texttt{quantumClose(first,second,x)}&\iff d\le1/3.
\end{aligned}\tag{4}
$$

In particular, **if $d=2/3$, the maximizing measurement witnesses `quantumFar` exactly**. Replacing attainment by approximate gate synthesis would not suffice for this existential boundary. The definition correctly allows arbitrary complex measurement matrices, including the spectral basis, because the measurement describes the mathematical distance; it is not an efficient operation available to a sampler. At $d=1/3$, all measurements meet the non-strict close bound. When `outputLength` is zero, the output space has dimension one, both reduced states equal 1, and $d=0$, as expected.

The normalization convention matters: in the 2002 paper the notation $\|\cdot\|_{tr}$ already includes the factor $1/2$; in modern Schatten notation $\|\cdot\|_1$ does not. See [Watrous 2002, Appendix A, p. 21](https://arxiv.org/pdf/quant-ph/0202111).

## 4. The actual generator is a polynomial-time reduction

`polynomialInputUniform` requires a single concrete transducer and a finite coefficient list giving its runtime. On every binary input `x`, that machine halts by the stated polynomial and emits the **entire** serialization of `family x`. The transducer has finite control and cannot read its append-only output. It is not an arbitrary polynomially bounded function used as advice. See [Statistical.lean, lines 134–150](../../quantum/InclusionQuantum/Statistical.lean#L134) and [Transducers.lean, lines 23–59](../../lean/InclusionBench/Transducers.lean#L23).

The serialization records width, the otherwise unused `Circuit.output` field, gate count, gate tags, and every wire index. Natural-number fields have an injective unary-delimited encoding, with a proved decoder round trip. See [Quantum.lean, lines 76–90](../../quantum/InclusionQuantum/Quantum.lean#L76) and [UniformCircuits.lean, lines 18–47](../../lean/InclusionBench/UniformCircuits.lean#L18). For width $w(n)$ and $g(n)$ gates, the encoding has length $O(w(n)+g(n)w(n)+g(n))$, which remains polynomial. Unary indices therefore cause polynomial overhead, not a different polynomial-time class. `output_length_le_time` supplies an additional formal output-length bound.

The only circuit gates are H, T, X, and CNOT; T has the fixed algebraic phase $(1+i)/\sqrt2$, and CNOT's two wires must be distinct. `Circuit.run` folds just these gates. It never reads `Circuit.output` and never performs an implicit final measurement. The sampler starts every qubit at zero and discards its environment after the circuit. Thus two sampler generators, run sequentially and packaged together, compute a deterministic polynomial-time map from `x` to a conventional QSD circuit pair.

The noncomputable Lean declarations express exact mathematical states and real probabilities. They do not allow the circuit generator to use arbitrary real constants, distinguishers, or density matrices as instructions.

## 5. Both directions of the total-language characterization

The external complexity facts used here are these:

- Watrous's 2002 Theorem 6 makes far-yes $(\alpha,\beta)$-QSD complete for honest-verifier QSZK whenever $0<\alpha<\beta^2<1$. The definition in §2.4 uses mixed output states, non-strict promise bounds, and all-zero circuit initialization. Appendix A gives input-dependent polynomial-time uniformity. [Author preprint](https://arxiv.org/pdf/quant-ph/0202111).
- Watrous's general-verifier result gives $\mathrm{QSZK}=\mathrm{QSZK}_{HV}$, with quantum auxiliary-input security: **Theorem 13**, not an assertion supplied by the earlier paper. [Corrected April 2009 author version, §5.2](https://cs.uwaterloo.ca/~watrous/Papers/ZeroKnowledgeAgainstQuantum.pdf).
- Efficient synthesis over a fixed universal finite gate set has polynomial overhead at inverse-polynomial accuracy. H, T, and CNOT suffice; inverses needed by synthesis are available because $T^{-1}=T^7$, while H and CNOT are self-inverse. Global phase has no effect on output states. [Dawson–Nielsen, Theorem 1 and the algorithmic statement immediately following it](https://arxiv.org/pdf/quant-ph/0505030).

**Operational definition to ordinary QSZK.** For each total input, equation (4) puts the generated pair into the promise of $(1/3,2/3)$-QSD with the correct polarity. Its constants obey $1/3<(2/3)^2$. Completeness/membership and closure under deterministic polynomial-time precomputation yield an honest-verifier protocol; the full-versus-honest-verifier theorem yields ordinary QSZK. A simulator for the composed protocol runs the classical preprocessing and the QSD simulator. Pad the generated description to length at least $|x|$, for example by adding $|x|$ unused zero environment wires. Its length is then between $|x|$ and a polynomial in $|x|$: simulation still takes polynomial time, and negligible target-instance error remains negligible in the original input length. This avoids silently assuming that a reduction never shortens its input. There are no unspecified inputs: every string belongs to the language or its complement, and the Lean definition imposes the corresponding gap condition.

One may choose the QSD circuit basis to include these standard gates. If a fixed different reference basis is demanded, avoid exact-boundary trouble as follows. Approximate each output state to trace distance at most $1/96$. The pair distance changes by at most $1/48$, hence close inputs have distance at most $17/48<3/8$, and far inputs at least $31/48>5/8$. The outer constants remain eligible because $3/8=24/64<25/64=(5/8)^2$. These same interior bounds address a strict-inequality formulation of polarization. They do not assume that an approximate circuit realizes a boundary value exactly.

**Ordinary QSZK to the operational definition.** Regard a total QSZK language as a promise problem with no excluded inputs. Its honest-verifier characterization and QSD completeness provide polynomial-time generated circuit pairs with close distance at most $1/8$ and far distance at least $7/8$. These constants are eligible because $1/8<(7/8)^2$. Using this stronger gap before any compilation leaves explicit room for error.

Compile each circuit into H/T/X/CNOT so that each reduced output changes by trace distance at most $1/24$. Then

$$
d_{\mathrm{no}}\le\tfrac18+\tfrac1{12}=\tfrac5{24}<\tfrac13,
\qquad
d_{\mathrm{yes}}\ge\tfrac78-\tfrac1{12}=\tfrac{19}{24}>\tfrac23.
$$

For an original circuit with at most $M(n)$ constant-arity gates, synthesize each gate to operator-norm error at most $1/(24\max(1,M(n)))$, up to irrelevant global phase. A telescoping product bound gives whole-circuit error at most $1/24$. For pure outputs, trace distance is at most the Euclidean distance of their suitably phased state vectors: expand the difference of rank-one matrices as $(\psi-\phi)\psi^\dagger+\phi(\psi-\phi)^\dagger$ and use the triangle inequality. Partial trace cannot increase this distance, since every output projector lifts to the full-space projector $P\otimes I_E$, to which equation (3) also applies. Thus the preceding error budget applies. Synthesis time and gate count are polynomial. This uses universality for constant-arity gates in a polynomial-size circuit, not a false claim that an arbitrary many-qubit unitary has a polynomial-size synthesis.

The remaining layout and machine-model conversions are explicit polynomial constructions:

1. **Output layout:** map the designated output wires to the first block by index relabeling or SWAPs (three CNOTs per swap). Keep their order consistent between the two circuits.
2. **Output padding:** choose an integer-coefficient polynomial $p(n)$ dominating the number of output qubits. Append identical zero qubits to both outputs. Their matrices change by the same isometry, so all nonzero singular values of the difference, and therefore trace distance, are unchanged.
3. **Environment padding:** choose polynomial environment bounds for each sampler and add unused zero qubits, including the extra qubit required by `Circuit.output`. Tracing these qubits out changes no output state. If a source requires both circuits to have the same full width, pad to a common bound. The output-wire field can point to the extra wire because `run` ignores it.
4. **Polynomial descriptions:** ordinary polynomial bounds are dominated by $C(n+1)^k$, whose expansion is a finite list of nonnegative integer coefficients of the kind used by `polynomialValue`. The output length can therefore be an exact polynomial of input length even when the source circuits use varying widths.
5. **Concrete generators:** the fixed polynomial-time reduction, compiler, wire relabeler, padder, and serializer compose into one deterministic algorithm for each circuit. Standard deterministic-machine simulation realizes each algorithm by the finite-control transducer here with polynomial overhead. No density-matrix calculation or optimal distinguishing measurement is performed by this generator. Asymptotic bounds can be enlarged to cover all input lengths; any finitely many exceptional inputs can be handled by a fixed finite lookup in the machine, without length advice.

The resulting families satisfy `QuantumSampler` and the all-input conditions of `QSZK`. This proves the reverse identification at the mathematical-model level, subject to the cited completeness and compilation facts and the routine machine-simulation bridge. General mixed-state circuit conventions also cause no problem: retain discarded qubits, coherently record measurement results and controls, and move the final discard to the environment. Polynomial-size unitary purifications and padding are explicitly used in [Vidick–Watrous, *Quantum Proofs*, §5.3.3, Figure 5.7](https://arxiv.org/pdf/1610.01664).

## 6. What is proved in Lean and what remains trusted

The code already proves sampler normalization, the probability interval $[0,1]$, the difference bound $[0,1]$, closeness of identical samplers, and disjointness of far and close. The independent environment-sign test and serialization-width test are also compiled checks. They support the correspondence but do not prove all of it.

The following steps remain mathematical bridges outside the Lean theorem inventory:

| Step | Status in this review |
|---|---|
| Partial-trace matrix formula and equality of the code probability to $\operatorname{Tr}(P\rho)$ | Derived explicitly in equations (1)–(2); not a Lean theorem here |
| Norm-preserving square matrix is unitary; representation of every projector | Finite linear-algebra argument supplied above; not formally encoded here |
| Maximum probability difference equals half trace norm, with attainment | Spectral proof supplied in equation (3); standard source theorem cross-checked |
| Standard QSD completeness and full/honest-verifier QSZK equivalence | Trusted pre-cutoff literature theorems with separate source anchors |
| Gate compilation, purification, trace-distance stability, and padding | Explicit error and resource accounting supplied; standard simulation facts remain trusted |
| Every polynomial-time generator has a polynomial-time implementation by this transducer | Standard deterministic machine-model equivalence; not established by compiling `Statistical.lean` |

No new axiom, admission rule, baseline inclusion, or canonical definition was added. The review found no factor-of-two error, wrong yes/no orientation, missing boundary attainment, access to discarded information, or hidden nonuniform sampler. Its conclusion is an independently worked mathematical correspondence under the stated trusted bridges, not a claim that the complete QSZK equivalence has passed the Lean kernel.
