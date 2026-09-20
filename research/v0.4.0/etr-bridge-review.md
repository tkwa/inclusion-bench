# Independent ETR encoding bridge review

**Disposition:** no blocking defect found; no model or baseline change proposed. This review identifies the binary language `RealFeasibility.ETR` with conventional finite ETR under deterministic polynomial-time many-one reductions in both directions. It supplies the encoding argument and its complexity bounds; it does not claim that these reductions have been proved in Lean.

The review covers `lean/InclusionBench/RealSyntax.lean` and `quantum/InclusionQuantum/RealFeasibility.lean`, at the hashes recorded in the accompanying JSON. The historical cutoff is September 1, 2026. The endpoint remains a class of total binary decision languages.

## What the definition accepts

An input word must decode exactly to an instance containing a variable count and a typed postfix program. Its instructions construct arithmetic terms from variables, binary natural-number magnitudes, negation, addition and multiplication; then construct formulas using equality, strict inequality and Boolean operations. Assembly must leave exactly one formula. Every referenced variable index must be below the declared count.

`Satisfiable` quantifies one tuple `Fin variableCount → ℝ` of actual real numbers. Its zero extension outside this tuple makes evaluation total but cannot admit an out-of-range reference: validity is a separate required conjunct. `ExistsR` is the downward closure of this binary language under the concrete polynomial-time output transducers in `RealSyntax`.

The native decoder's reserialization check rejects truncated unary fields and trailing garbage. It does not require a unique spelling for each mathematical integer: leading coefficient zeros and the empty magnitude both have their specified arithmetic meaning. Distinct spellings do not affect the reduction.

The primary reference encoding is an existential prefix followed by a finite quantifier-free Boolean formula over real arithmetic. Schaefer–Štefankovič specify this in §2, including the elimination of integer and rational abbreviations; their Lemma 3.2 and Corollary 4.2 provide the quadratic-system bridge. The locators here refer to the final 22-page author manuscript, not the older preprint's different numbering. [Primary paper](https://www.cs.rochester.edu/u/stefanko/Publications-new/J35.pdf)

## Exact native size accounting

Let `d` be the variable count. Each natural metadata field `k` is encoded as `k` false bits followed by one true bit. The length of a serialized instance is therefore exactly

```text
N = d + 1
    + Σ_variable-records (j + 4)
    + Σ_natural-records (3 + 2L + popcount(bits))
    + Σ_other-records (tag + 2).
```

Here `j` is a variable index, `L` is the length of that coefficient's magnitude bit string, and an ordinary opcode has tag between 2 and 11. The coefficient record encodes the individual binary digits; it never writes the integer magnitude in unary. For example, the coefficient `2^k` costs `2k+6` bits in its natural record.

For a valid instance with `V` variable records, `C` constant records, total magnitude length `B`, and `O` other records,

```text
N ≤ d + 1 + (d + 3)V + 3C + 3B + 13O.
```

All metadata values in an `N`-bit native word are at most `N`; both the number of instructions and total coefficient-bit length are at most `N`. Postfix assembly consumes operands without a duplication instruction. Consequently, it builds a syntax tree of linear node count, even if a simple implementation copies intermediate lists.

## Native words to conventional ETR

Given an arbitrary native word of length `N`:

1. Decode its fields, validate tags and payloads, check every index, and check the typed stack. If any check fails, output the fixed false sentence `0=1`.
2. For a valid program, emit its assembled formula with the prefix `∃x₀ … ∃x_{d−1}`. Give indices ordinary binary names; preserve arithmetic operations and every Boolean negation.
3. If the target uses only constants `0,1`, compile each coefficient by Horner's rule, `a ↦ (1+1)a+b`. The previous term occurs once, so this takes linear size in the coefficient's bit length. If unary minus is absent from the exact target signature, introduce a fresh variable `y` for each negated subterm `u`, conjoin `y+u=0`, and replace that subterm by `y`.

These added arithmetic equations determine their fresh variables uniquely for each original real assignment. Conjoining them outside the original formula is therefore valid even when the replaced term lies under Boolean negation. No coefficient is evaluated into an exponentially long unary numeral.

There are `O(N)` nodes and variables, and their binary names have `O(log(N+2))` bits. Output length is `O(N log(N+2))`. A straightforward parser, stack reconstruction and serializer run within `O((N+1)^3)` multitape bit operations. The fixed false output also handles the empty input. The resulting total reduction preserves membership on every word, not just on well-formed instances.

## Conventional ETR to native words

Let the source have bit length `m`, with an explicitly encoded existential prefix and finite quantifier-free formula.

First validate the source syntax and binding. Map a malformed encoding to the native serialization of `{variableCount := 0, program := [falsum]}`. Remove unused quantified variables and rename the used ones densely. At most `m` distinct variables occur.

This renaming is essential. A label such as `x_{2^k}` uses only `O(k)` source bits and must not become a unary native index of length `2^k`. Compare source identifiers and declared bounds in binary, then replace labels by dictionary indices `0,…,d−1`. If an encoding declares a huge tuple count in binary, unused coordinates can still be dropped: existential quantification over unused real coordinates has no effect. This does not permit a succinct circuit describing exponentially many constraints.

Normalize the finitely many source operators and emit typed postfix code:

- Preserve `¬`, `∧` and `∨` directly. Express `a≤b` as `¬(b<a)`, `a≥b` as `¬(a<b)`, and disequality as negated equality.
- Encode signed binary integers by their magnitude bits and, when needed, `negateTerm`. Express subtraction by addition and term negation.
- For a rational literal `p/q`, check `q≠0`; replace it by a fresh variable `r` and conjoin `qr=p` outside the Boolean formula. This uniquely defines `r`, including occurrences under negation. A zero denominator is a malformed literal.

After normalization there are `O(m)` instructions and variables and `O(m)` coefficient bits. The exact native size formula gives an `O((m+1)^2)` output bound. Even naive identifier comparisons, syntax processing and writing unary indices fit within `O((m+1)^3)` multitape time. These algorithms are fixed, finite procedures; they do not ask whether a formula has a real solution.

The same argument handles an explicitly listed sparse polynomial with binary exponents, or an ordinary explicitly listed arithmetic DAG, after adding gate variables. Compute `x^e` by repeated squaring and multiplication using `O(log(e+1))` gates, then impose each gate equation. Keep sharing through variables rather than unfolding the DAG. Total gate count is linear in the explicitly listed syntax and exponent-bit lengths. A circuit that succinctly generates exponentially many equations is outside this bridge.

For both directions, the repository transducer has one binary work tape, not an assumed unit-cost multitape instruction. Encoding the fixed number of simulated tapes and scanning their used intervals gives the usual quadratic simulation overhead. Thus `O((n+1)^6)` is a conservative bound in the concrete transducer model for the algorithms above. A finite nonnegative-coefficient polynomial clock can dominate this bound, including at length zero. This simulation and its bound are mathematical arguments here, not newly checked Lean theorems.

## Boolean formulas to quadratic systems, without a negation error

Here is an independent explicit construction. It also explains why the richer native Boolean syntax does not define a larger class than real quadratic-system feasibility.

Give each arithmetic subterm a value variable and impose its arithmetic gate equation: `v=c`, `v+u=0`, `v=u+w`, or `v=uw`. Give each Boolean subformula a variable `b` with `b(b−1)=0`, using `b=1` for true.

For an equality atom `p=0`, use a fresh real `t` and impose

```text
bp = 0,
(1−b)(pt−1) = 0.
```

For `b=1` these require `p=0`; for `b=0` they require `p≠0`. For a strict-positive atom `p>0`, use fresh `s,t` and impose

```text
b(ps²−1) = 0,
(1−b)(p+t²) = 0.
```

The true case holds exactly when `p>0`; the false case holds exactly when `p≤0`. Existence of the requisite real square roots supplies the converse directions. For native `u<v`, take `p=v−u` through an arithmetic gate.

Use the Boolean gate equations

```text
b_verum = 1,
b_falsum = 0,
b_not = 1−b,
b_and = b₁b₂,
b_or = b₁+b₂−b₁b₂,
```

and force the root variable to be 1. The constant equations also cover zero-variable `verum` and `falsum`, including when either is the entire formula. Every atom now has its correct truth value in **both** polarities. This avoids the invalid shortcut of replacing a positive atom by an existential slack condition inside a negation and then moving that quantifier outside.

The displayed atom gadgets contain degree-three or degree-four products. Split each product into fresh arithmetic gate variables before emitting the system. Each gadget has constant size, so all resulting equations have degree at most two with only a constant number of monomials per equation. There are `O(m)` auxiliary variables and equations, total coefficient-bit length `O(m)`, and an `O(m log(m+2))` sparse binary description. Its native serialization is `O((m+1)^2)`.

For each assignment to the original variables, the source formula is true iff some assignment to these auxiliaries satisfies the system. In the reverse direction, write a finite quadratic system as a conjunction of its equations and apply the source-to-native compiler. Summing the squares of the quadratic equations gives a single quartic equation over the reals if that alternative encoding is wanted; this does not establish completeness of a single quadratic equation. The construction is consistent with the primary quadratic and quartic completeness statements cited above, but no exact constant from that paper is asserted for these different gadgets.

## What the counting-hierarchy theorems do—and do not—say

Three distinctions prevent an incorrect `ExistsR ⊆ CH` seed.

**The nondeterministic real Boolean part is the ETR endpoint.** The relevant identity is `∃R = BP(NP_R^0)`, with binary inputs, real nondeterministic guesses, and only the fixed constants `0,1`. It is not `BP(P_R^0)`. Schaefer–Štefankovič state the nondeterministic identification in Remark 2.1 and footnote 2. Arbitrary built-in real constants are excluded. [Primary identification](https://www.cs.rochester.edu/u/stefanko/Publications-new/J35.pdf)

**The PosSLP upper bound concerns deterministic computation.** Allender–Bürgisser–Kjeldgaard-Pedersen–Miltersen, Proposition 1.1 and Theorem 1.4, give `BP(P_R^0)=P^PosSLP ⊆ CH`. Their §4 discussion after Theorem 4.1 separately permits digital nondeterminism, meaning guessed bits rather than arbitrary real numbers. Thus a polynomial-bit guess followed by PosSLP queries stays in CH; this does not simulate an unrestricted real witness. No equality between full ETR and `NP^PosSLP` is used here. [Primary paper](https://people.cs.rutgers.edu/~allender/papers/slp.pdf)

**Complex feasibility is not real feasibility.** Andrews–Garg–Schost, ECCC TR26-024, February 20, 2026, Theorem 1.1, put Hilbert's Nullstellensatz over their listed fields in CH; the question is existence in the **algebraic closure**. In particular the rational-coefficient case allows complex roots. Their Theorem 1.4 counting result concerns the corresponding algebraic variety. Neither theorem supplies a real-feasibility or real-solution-counting upper bound. [Primary theorem and scope](https://eccc.weizmann.ac.il/report/2026/024/download)

The polynomial `x²+1` has a complex root and no real root. The existing Lean theorem `negativeSquare_not_in_etr` certifies precisely this obstruction for the native equation `x²=−1`. Splitting a complex variable into real and imaginary parts yields a polynomial reduction from complex feasibility to real feasibility, using paired arithmetic gate variables to preserve sharing. That direction cannot transfer an upper bound to the larger real-feasibility problem.

## Evidence and remaining boundary

Existing kernel-checked results cover serialization round trips and injectivity, postfix compilation, finite-assignment lookup, malformed-input rejection, a genuine irrational witness for `x²=2`, and rejection of `x²=−1`. The earlier independent semantic checks also cover invalid indices, malformed coefficient digits, stack typing, unused stack entries and leading coefficient zeros.

This review adds a mathematical reduction audit, not another compilation run. The explicit reductions, their standard machine simulations and the textbook BSS identification remain trusted, reviewable bridges rather than Lean theorems. No automatic derivation of `ExistsR⊆CH`, `ExistsR⊆PSharpP`, `ExistsR⊆PP`, or `ExistsR⊆NP` is justified by the papers reviewed here. No current class label needs correction on the evidence found.
