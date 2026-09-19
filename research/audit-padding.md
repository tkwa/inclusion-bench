# Length-regular padding review

This is a derivation from standard pre-cutoff definitions, recorded during the
September 2026 audit. The recording date does not claim a new historical result.
The padding method and time classes are described in Arora and Barak,
[Computational Complexity](https://theory.cs.princeton.edu/complexity/book.pdf),
Chapters 2–3. The class-specific closure checks below are part of this derivation.

For each roster class C other than E and NE, add these implications:

- E ⊆ C implies EXP ⊆ C.
- NE ⊆ C implies NEXP ⊆ C.

These are conditional rules, not unconditional containments. Several circuit
instances were already present in release 0.2.0.

## Derivation

Let L be decided in deterministic (respectively nondeterministic) time
2^(n^d + O(1)). Choose a fixed integer k large enough and put p(n) = (n+2)^k.
Encode x as pad(x) = x 1 0^(p(|x|)-|x|-1). The length p(n) is strictly increasing
and at least n+1. A decider checks the length and padding format, recovers x,
and simulates L. Invalid encodings are rejected. The padded language is in E
(respectively NE), because its simulation takes time 2^O(p(n)).

Under the premise, the padded language belongs to C. Each C listed below is
closed under the inverse of this particular padding map. Applying its decider
or circuit to pad(x) recovers L in C. The argument is language by language;
the polynomial degree, machine and size bound may depend on L, as the
definitions of EXP, NEXP and C permit.

This argument does not assert closure of every C under arbitrary polynomial-time
reductions. In particular, logspace and small circuit classes only need the
simple input projection and fixed bits used by pad.

## Checks for all 48 target classes

| Targets | Why inverse padding preserves the class |
| --- | --- |
| AC0, ACC0, TC0, NC1 | In the circuit for length p(n), wire the first n inputs to x and fix the delimiter and remaining inputs. Polynomial size remains polynomial in n, constant or logarithmic depth remains valid, and the fixed ACC modulus is unchanged. No uniformity is assumed for these four classes. |
| L, NL | Simulate the input head on the virtual padded string. Its position and p(n) require O(log n) bits. Nondeterministic choices are unchanged. |
| LogCFL | The padding map is computable in logspace; compose it with the logspace reduction to a context-free language. |
| NC | Generate the circuit of length p(n) and hardwire its fixed inputs. A logspace generator can compute p(n) and the new input wiring; polylogarithmic depth and polynomial size are preserved. |
| SC | The virtual-input simulation takes polynomial time and polylogarithmic space simultaneously. |
| P, RP, coRP, ZPP, BPP | Polynomial-time preprocessing and simulation preserve the respective deterministic, one-sided, zero-error and bounded-error conditions. Expected running time for ZPP also composes with p. |
| UP, coUP, FewP | The deterministic input transformation leaves accepting path multiplicities unchanged; polynomial bounds compose with p. Complementation gives the coUP case. |
| NP, coNP, NPcapcoNP | Polynomial witnesses remain polynomial after substituting p(n). Complementation and intersection commute with inverse images. |
| SPP, CeqP, PP, parityP, WPP | GapP or accepting-path functions compose with a deterministic polynomial-time map. The required zero, unit, sign, parity or FP normalization conditions are preserved. |
| LWPP | The normalization becomes h(0^p(n)), which is still an FP function of input length alone. Exact length regularity matters here. |
| AWPP | Compose the GapP numerator and polynomial normalization bound. For an error exponent r(n), choose a polynomial error exponent r'(m) at least r(n) whenever m=p(n)≥n. The required approximation then holds. |
| MA, coMA, AM, coAM | Run the same verifier on the padded input, with polynomially longer messages and randomness. Completeness and soundness hold for each original input and every prover. Complements commute with inverse images. |
| BQP, QCMA, QMA, coQMA | Compose the uniform circuit generator with n↦p(n), and initialize padding wires to fixed basis states. Certificate lengths remain polynomial, and acceptance probabilities are unchanged. Extra witness bits, if required by the chosen length convention, are ignored. Complementation gives coQMA. |
| SBP | Compose the #P count and threshold exponent with p. The fixed multiplicative acceptance gap is unchanged. |
| SZK | Run the original protocol on pad(x); the simulator computes the same padding first. Polynomial running time and statistical distance bounds are preserved. For general malicious verifiers, compose the verifier with the efficient padding map. |
| Sigma2P, Pi2P, Delta2P, Theta2P, PH | Fixed quantifier levels and polynomial oracle computations compose. O(log p(n))=O(log n), so Theta2P's logarithmic query bound is preserved. A language in PH keeps its fixed finite level. |
| Ppoly, NPpoly | Advice for length p(n) depends only on n and has polynomial length in n. The advised simulation is polynomial time and preserves nondeterministic acceptance. |
| PSPACE, EXP, NEXP, EXPSPACE | Substitution of a fixed polynomial preserves the union over polynomial resource exponents. |

E and NE are deliberately excluded as targets: the inverse simulation may take
2^poly(n) time, rather than 2^O(n). They require separate implications, such as
the existing rule NE ⊆ E implies NEXP ⊆ EXP.

## Review record

The circuits/space reviewer independently checked circuits, advice, low-space and
exponential targets. The counting/quantum reviewer independently checked path
counts, length-dependent LWPP normalization, AWPP accuracy and quantum witness
and uniformity conditions. The classical reviewer independently checked the
randomized, interactive-proof and hierarchy cases. No existing literature proof is being
represented as a new Lean proof.
