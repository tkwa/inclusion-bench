# Counting baseline extension for provisional v0.4.0

This dossier covers the new total decision-language endpoints **PSharpP** and
**CH**. It is a working literature audit, pending independent cross-review and
integration with the classical and quantum extensions. The historical cutoff
remains September 1, 2026. It does not classify function-valued #P as a language
class.

## Definitions and primitive inclusions

PSharpP means deterministic polynomial time with a total PP language oracle.
This is the usual decision class P^PP = P^#P. A #P function has a
polynomial-length binary output; polynomially many threshold queries recover
that output, and an exact count answers a PP query. Neither direction identifies
the decision class with the function class #P or the search class PPP.

CH is the union of **fixed finite** levels C₀P = P and Cₖ₊₁P = PP^(CₖP).
The level is fixed for each language, not allowed to increase with input length.
The oracle characterization agrees with the standard counting-quantifier
definition. The relevant primary references are Bürgisser's
[2006 manuscript, Definition 2.3](https://eccc.weizmann.ac.il/report/2006/113/download/)
and Allender–Wagner's
[counting-hierarchy survey, §1](https://people.cs.rutgers.edu/~allender/papers/column40.pdf).

The six primitive inclusions are PP ⊆ PSharpP, PH ⊆ PSharpP,
parityP ⊆ PSharpP, PSharpP ⊆ CH, CH ⊆ PSPACE, and P ⊆ CH (the last is
redundant and need not be stored). Toda supplies the PH containment. For parity,
recover the accepting-path count and test its low bit. A deterministic PP-oracle
computation is a special case of a PP-oracle majority computation, putting
PSharpP in the second standard counting level. Each fixed level can be evaluated
in polynomial space, with its particular polynomial bound depending on the
level and machines. Both new classes are closed under complement.

These seeds do **not** give PH ⊆ PP, PSharpP ⊆ PP, or CH ⊆ PSharpP.
They also do not settle whether ∃R, QSZK, or QMA(2) lie in either new class.
Each of those interfaces needs its own theorem; an upper bound by PSPACE or
NEXP is insufficient.

## Conditional consequences

**Small circuits for PP.** PP ⊆ P/poly implies CH ⊆ P/poly by
Bürgisser's Lemma 2.5. It also implies CH ⊆ MA. The latter follows from
[Fournier–Perifel–de Verclos, Lemma 3](https://webusers.imj-prg.fr/~herve.fournier/publications/vnp.pdf):
polynomial-size Boolean circuits for #P imply CH = MA. Threshold queries and
polynomial composition of nonuniform circuits convert PP ⊆ P/poly to the
lemma's #P hypothesis. This particular conditional lemma is unconditional;
the paper's separate uses of GRH do not qualify it.

An independent derivation uses the LFKN consequence P^#P ⊆ MA, stated in
[Aaronson–Wigderson, Theorem 3.5](https://www.scottaaronson.com/papers/alg.pdf),
and the strengthened Toda containment PP^PH ⊆ P^PP. The latter appears
explicitly near the end of §1 of Allender–Wagner. As MA ⊆ PH, induction over
the counting levels gives the claimed collapse. This argument requires the
strengthened Toda theorem; it does not infer collapse merely from P^PP = PP.

**A PP-low upper class.** PP ⊆ AWPP implies CH ⊆ PP. The unconditional
identity PP^AWPP = PP is
[Fortnow–Rogers, Theorem 3.3](https://lance.fortnow.com/papers/files/quantum.pdf).
Starting from C₁P = PP, replace only the *oracle class* by AWPP and induct on
the fixed level. Transitivity then gives CH ⊆ AWPP. The same stored rule
automatically handles a hypothesis PP ⊆ T whenever the baseline already
contains T ⊆ AWPP, including P, BPP, BQP, SPP, LWPP and WPP. It does not
require generic Turing closure of WPP.

**PP in the polynomial hierarchy.** PP ⊆ PH implies CH ⊆ PH.
First P^PP ⊆ P^PH ⊆ PH: a particular PH oracle language has a fixed finite
level, and polynomially many adaptive queries add at most a fixed number of
levels. Then induction uses PP^PH ⊆ P^PP ⊆ PH. This is a union-of-fixed-levels
argument, not a uniform bound on the whole hierarchy.

**Parity simulation.** PP ⊆ parityP implies PSharpP ⊆ parityP, using
the established identity P^parityP = parityP. A stronger CH consequence may
also follow from PP^parityP ⊆ P^PP; it is deliberately left for independent
cross-review before import.

**Padding.** For T equal to either PSharpP or CH, E ⊆ T implies EXP ⊆ T,
and NE ⊆ T implies NEXP ⊆ T. Use the existing regular-padding construction
and polynomial-time many-one closure. For CH, a polynomial-time reduction
to a particular fixed-level language stays within some fixed level. No level
is selected as a function of the input length.

## Rules deliberately not inferred

- PSharpP ⊆ PP alone is not used to collapse CH. Deterministic adaptive
  oracle closure is a different assertion from PP^PP = PP.
- An unrelativized inclusion PP ⊆ T is never applied to the outer PP machine
  under an arbitrary oracle. Only a proved relativizing simulation, an oracle
  replacement, or the cited lowness theorem permits that step.
- Generic P^WPP = WPP or WPP^WPP = WPP is not assumed.
- A fixed-polynomial circuit lower bound is not converted into a separation
  from the union P/poly.
- Nothing about finite-field or real algebraic counting replaces the ordinary
  binary decision models here.
- No independence-from-ZFC result follows from a missing ordinary inclusion.

## Audit status

The companion JSON records importable primitive facts, complements, and
candidate rules with explicit provenance. An independent reviewer is checking
the conditional arguments and all incident endpoint families. The final merged
matrix, complete incident-pair index, SAT audit, Lean inference traces, and
residual-error assessment must be generated after all three domain extensions
have been integrated. This document by itself does not certify historical
openness or the final Lean-to-literature model correspondence.
