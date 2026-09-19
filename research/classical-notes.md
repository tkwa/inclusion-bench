# Classical knowledge-base review

This is a literature-informed draft for a benchmark frozen at **2026-09-01**. Its positive mathematical statements have source anchors or explicit derivations. Its omissions do **not** certify that a problem was open on the cutoff date. The machine-readable companion is [classical.json](classical.json).

The roster contains 50 classes. AC0, ACC0, TC0, NC1, P/poly, and NP/poly are nonuniform; `NC` means **logspace-uniform NC**. Every other entry denotes a class of total decision languages. These conventions matter to the score: a nonuniform TC0 lower bound can remain open when the corresponding uniform separation is already known.

## What the sources establish

- [Williams, Theorem 1.1](https://people.csail.mit.edu/rrw/acc-lbs-journal-final.pdf) gives **NE ⊄ ACC0**, through the stronger statement NTIME(2ⁿ) ⊄ ACC0. Recording only NEXP ⊄ ACC0 would miss known baseline consequences. The paper's stale journal-template footer is not its publication date; the journal publication is 2014.
- [Furst–Saxe–Sipser](https://wiki.epfl.ch/edicpublic/documents/Candidacy%20exam/Furst%20Saxe%20Sipser%20-%201984%20-%20Parity%20circuits%20and%20the%20polynomial-time%20hierarchy.pdf) supplies the parity lower bound. PARITY belongs to L and to ACC0, so both L ⊄ AC0 and ACC0 ⊄ AC0 are seeded.
- [Borodin–Cook–Dymond–Ruzzo–Tompa, §3.1](https://www.cs.toronto.edu/~bor/Papers/two-applications-complementation-via-inductive-counting.pdf) supplies NL ⊆ LOGCFL ⊆ uniform NC and LOGCFL's complement closure. NL's complement closure also has the direct [Immerman source](https://epubs.siam.org/doi/10.1137/0217058).
- [Borodin's space/depth simulation](https://www.cs.toronto.edu/~bor/Papers/relating-time-space-size-depth.pdf) and the space hierarchy give PSPACE ⊄ uniform NC. The same hierarchy gives PSPACE ⊄ SC. These do not resolve P versus PSPACE.
- [Karp–Lipton](https://doi.org/10.1145/800141.804678), with Sipser's improvement as stated in [Arora–Barak, Theorem 6.13](https://theory.cs.princeton.edu/complexity/book.pdf), gives NP ⊆ P/poly ⇒ PH ⊆ Σ₂P.
- [Babai–Fortnow–Nisan–Wigderson, Lemma 4.2](https://lance.fortnow.com/papers/files/bppexp.pdf) gives EXP ⊆ P/poly ⇒ EXP = MA. The related PSPACE consequence uses an efficient circuit for the honest prover in [IP = PSPACE](https://doi.org/10.1145/146585.146609).
- [Toda](https://epubs.siam.org/doi/10.1137/0220053) gives PH ⊆ P^PP. The implemented consequence is PP ⊆ P ⇒ PH ⊆ P. PH ⊆ PP is **not** a baseline fact.

## Elementary derivations needing mathematical review

The JSON labels these as derivations, rather than pretending a historical paper contains the exact benchmark-specific formulation. They are mathematically explicit enough for a reviewer to check and later formalize.

### Undecidable unary languages in AC0

Choose an undecidable language U ⊆ {1}*. For each length n, take the circuit that computes the AND of its n input bits if 1ⁿ ∈ U, and the constant-zero circuit otherwise. Its language over binary strings is exactly U. This family has depth at most two and linear size. No uniform construction of the family is required.

Thus AC0 is not a subset of any of the 44 recursive classes in this roster. The same witness propagates to ACC0, TC0, NC1, P/poly, and NP/poly through known inclusions. An advice class must never be inserted beneath EXP or PSPACE merely because an individual circuit can be evaluated efficiently.

The target classes are recursive under the benchmark's total-language conventions: time/space machines have effective finite simulations; accepting paths can be enumerated for counting classes; bounded-error classical and quantum computations have decidable acceptance gaps; interactive classes have standard recursive upper bounds. For quantum classes this relies on a fixed, computable gate set. Arbitrary uncomputable amplitudes are excluded.

### Uniform NC uses polylogarithmic space

A depth O(logᵏ n), polynomial-size circuit can be evaluated recursively. A stack frame needs O(log n) bits for a gate identifier and a constant amount of control information. Logspace uniformity lets the simulator recover each gate's predecessors. The total working space is O(logᵏ⁺¹ n). The deterministic space hierarchy therefore supplies a polynomial-space language outside every such bound. SC is already restricted to polylogarithmic space by definition.

### Padding

For a language running in time 2^(nᵏ), append a self-delimiting block of zeros to increase the input length to Θ(nᵏ). The padded language runs in linear-exponential time. Consequently NE ⊆ E implies NEXP ⊆ EXP.

For exponential padding, make the padded length Θ(2^(nᵏ)). A nondeterministic exponential-time language then becomes an NP language; an exponential-space language becomes a PSPACE language. This proves the conventional upward consequences of P = NP and P = PSPACE.

If P ⊆ SC or P ⊆ uniform NC, apply its polylogarithmic-space algorithm to an exponentially padded EXP language. Store the virtual padded input's head position in O(nᵏ) bits and generate its symbols when requested. This gives EXP ⊆ PSPACE. The same construction gives NEXP ⊆ PSPACE if NP is contained in either SC or uniform NC. These implications do not assume that the padded string fits in polynomial space; it is simulated virtually.

### Hardwiring advice and padding into circuits

Let C be one of the nonuniform circuit targets in the JSON. If P ⊆ C, the ordinary circuit-evaluation language has polynomial-size C circuits. Fix the circuit-description bits to evaluate any chosen polynomial-size Boolean circuit. Thus P/poly ⊆ C; this is [Williams's Lemma 5.4](https://people.csail.mit.edu/rrw/acc-lbs-journal-final.pdf).

Replacing circuit evaluation by nondeterministic circuit evaluation gives NP ⊆ C ⇒ NP/poly ⊆ C. Similarly, if E ⊆ C, polynomial padding followed by hardwiring its fixed bits gives EXP ⊆ C. NE ⊆ C gives NEXP ⊆ C. Fixing input bits preserves each circuit model and changes size by at most a polynomial.

### Intersection rules

For each roster class A, A ⊆ NP and A ⊆ coNP imply A ⊆ NP ∩ coNP. The JSON contains all 50 instances. It also contains all 50 instances for ZPP = RP ∩ coRP. These rules refer to intersections of **classes of languages**, not to the Boolean hierarchy class DP.

## Exponential-space exclusion from nondeterministic advice

**EXPSPACE ⊄ NP/poly** has the following direct counting argument. It is included as an elementary derivation in the JSON. This research pass did not locate an exact primary-source statement; the argument still warrants the same explicit mathematical review as other benchmark derivations.

At each sufficiently large n, let s = ⌊2^(n/4)⌋. There are at most 2^O(s log(n+s)) nondeterministic Boolean circuits of size at most s, with at most s relevant witness-input bits. This is smaller than the 2^(2ⁿ) truth tables on n input bits. Choose the lexicographically first truth table not represented by any such circuit.

A deterministic machine can find that table in O(2ⁿ) space: store a candidate table; enumerate circuit descriptions; and compare the table with each circuit's accepted language. Test a circuit on an input by enumerating its witness assignments. This uses enormous but finite time and only exponential space. On input x, return the corresponding table bit.

The resulting language has no polynomial-size nondeterministic circuits, since every fixed polynomial eventually falls below 2^(n/4). Every NP/poly language has polynomial-size nondeterministic circuits after its advice is fixed. The constructed language is therefore in EXPSPACE \ NP/poly. It also separates EXPSPACE from P/poly.

## Where the audit stops

The sources cover classical seed relations and selected collapse, padding, and hardwiring rules. They do not exhaust all implications expressible on 50 classes. In particular, lowness, nonuniform collapse refinements, and contrapositives requiring several hypotheses may require additional rules. NP ⊆ BPP ⇒ NP ⊆ RP and PH ⊆ BPP is recorded as an unimported candidate pending a precise primary-source locator.

Several tempting shortcuts are invalid:

- [Impagliazzo–Wigderson](https://www.math.ias.edu/~avi/PUBLICATIONS/MYPAPERS/IW97/proc.pdf) requires exponential circuit hardness with appropriate quantifiers over input lengths. E ⊄ P/poly alone does not supply that premise.
- Kannan's lower bounds against each fixed polynomial circuit size do not exchange the quantifiers to give Σ₂P ⊄ P/poly.
- P = BPP for total languages does not automatically give a deterministic algorithm for a promise-BPP verifier, so it does not by itself justify MA = NP.
- Oracle and communication-complexity separations do not settle the corresponding unrelativized language inclusions. A September 2026 communication result found during search was both outside the cutoff and outside this model.

Historical publication dates establish that the seeded theorems predate the cutoff. They cannot establish that every remaining pair was open then. Before official scoring, a reviewer must audit the residual pairs, record a source and cutoff rationale for each eligible item, review the derivations above, and verify the formal statements. The present dataset supports provisional exploration until that work is complete.
