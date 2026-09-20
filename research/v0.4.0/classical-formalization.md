# Selected classical definitions for provisional v0.4.0

The six new Mathlib-free endpoints are concrete machine definitions: **BPL, UL, PL, P^#P, CH, and DLOGTIME-uniform NC¹**. The ∃R endpoint adds finite input syntax, real-number truth, and concrete polynomial-time reductions in the Mathlib project. These definitions preserve the selected scientific conventions; the standard equivalences between machine models and the cited presentations remain review obligations. Existing literature theorems may be trusted under the benchmark's baseline policy, but no such theorem is introduced as an axiom in these modules.

This note describes the implementation, not a completed audit of every new baseline classification. The new endpoints remain provisional until independent semantic review and the joint baseline checks finish.

## BPL, UL, and PL

`lean/InclusionBench/LogspaceClasses.lean` supplies `LogspaceClasses.BPL`, `UL`, and `PL`.

BPL and PL use the existing `Randomized.FairMachine`: finite control, read-only binary input, a binary work tape with blank symbols, and one fair bit selecting between two finite actions at each nonterminal step. Random bits are consumed as a stream. They are not a freely revisitable auxiliary input. Halting padding gives exactly 2^t equiprobable random strings for a t-step horizon.

The time bound is explicitly polynomial, and the *same machine* must obey a coefficient times log₂(n+1)+1 work-space bound on **every random prefix** through that horizon. BPL requires acceptance probability at least 2/3 on members and at most 1/3 on nonmembers. PL requires probability strictly greater than 1/2 exactly on members; ties reject. Every full random string halts and returns a Boolean answer.

UL is defined through `SharpL`, the natural functions counting accepting paths of a polynomial-time logarithmic-space nondeterministic machine. Transition-list multiplicities count separately, even when branches reach the same configuration. Every reachable branch obeys the space bound, every branch halts by the polynomial horizon, and the accepting-path count is at most one on every input. `GapL` is also supplied as a reusable function predicate; it does not become an extra scored language endpoint.

The module proves `bpl_in_pl`, `bpl_in_bpp`, `ul_in_up`, `sharpL_in_sharpP`, and `gapL_in_gapP` directly from these definitions. PL's equivalence with positivity of a GapL function is **not** silently asserted by its name. That equivalence, clock normalization, and simulations between the exact tape model and standard logspace models are the remaining bridges.

Source anchors: [Hoza, space derandomization survey, §1](https://eccc.weizmann.ac.il/report/2022/121/download); [Reinhardt–Allender, unambiguous logspace](https://people.cs.rutgers.edu/~allender/papers/nlul.pdf); [Allender–Ogihara, logspace counting, §2–3](https://www.numdam.org/item/ITA_1996__30_1_1_0.pdf). The separate [classical baseline dossier](classical-new-baseline.md) records the endpoint-specific source and oracle-model checks.

## P^#P and CH

`lean/InclusionBench/CountingHierarchy.lean` supplies `CountingHierarchy.PSharpP` and `CH`.

PSharpP is operationally **P^PP**, using the existing concrete deterministic oracle machine and the concrete GapP definition of PP. One oracle language is fixed for all inputs and lengths. A machine writes its queries on a tape; each oracle reply is one Boolean. The catalog's P^#P label uses the standard P^#P=P^PP theorem. The definition does not confuse a polynomial-bit #P function reply with one Boolean PP query, nor does it insert #P itself into the language matrix.

For CH, `SharpPWith` counts paths of a finite nondeterministic oracle machine, `GapPWith` takes integer differences of two such counts with the same oracle, and `PPWith` tests strict positivity. Every branch has an explicit polynomial time bound. `countingLevel 0` is P, level 1 is PP, and level k+2 is PP with one fixed oracle from level k+1. Membership in CH existentially chooses **one finite level for the whole language**, outside the quantification over input lengths.

The module proves P⊆CH, PP⊆CH, inclusion of each level in CH, monotonicity in the oracle class, negation closure of relativized gap functions, and a duplicated-branch counting check. It does not yet formalize P^#P=P^PP, closure of PP under truth-table reductions, general oracle-machine simulations, or counting-hierarchy collapse theorems.

The [counting landscape](counting-and-scope-landscape.md) and [independent cross-review](quantum-cross-review.md) distinguish P^PP from PP^PP and verify the algebra behind CH-collapse rules. Primary anchors include [Fortnow's counting chapter](https://lance.fortnow.com/papers/files/counting.pdf), [Fortnow's P^#P discussion](https://lance.fortnow.com/papers/files/topten.pdf), and [Bürgisser, Definition2.3](https://eccc.weizmann.ac.il/report/2006/113/download/).

## DLOGTIME-uniform NC¹

`lean/InclusionBench/AlternatingLogtime.lean` supplies `AlternatingLogtime.UniformNC1`, defined as its explicit ALOGTIME model.

A machine has finite control, an arbitrary fixed finite number of ordinary work tapes, and a separate semi-infinite binary index tape with a local head. Each transition reads and writes one cell of each work tape and moves each head by at most one position. The address tape has a fixed origin: moving its head never changes the significance of existing bits. Its binary value selects one read-only input bit in constant time; an out-of-range address returns an explicit missing-bit symbol. This address port is the only random-access operation. Ordinary work tapes have no free arithmetic or random addressing.

All tapes initially contain blanks or zeros, and all heads start at their fixed origins. There is no input-dependent initialization, advice function, arbitrary transition predicate, or precomputed circuit family. All transition-table arguments range over finite types. A state is existential or universal, and acceptance is the corresponding Boolean evaluation of its finite computation tree. A terminal configuration uses its explicit answer, including a universal state with no successors. Every branch must halt within c(log₂(n+1)+1) transitions.

The module proves the address-write/read invariant, halting-padding evaluation, and examples distinguishing existential from universal branching. It uses a finite number of tapes rather than presuming that an arbitrary multitape logtime computation can be simulated on one tape without time loss.

The intended circuit convention is **extended connection language U_E**, which has the standard ALOGTIME identification. Direct-connection-only U_D is not substituted. The ALOGTIME↔U_E-uniform NC¹ theorem and detailed model normalizations remain literature bridges. [Barrington–Immerman–Straubing](https://www.sciencedirect.com/science/article/pii/002200009090022D); [ECCC2011/095 revision1, Remark1](https://eccc.weizmann.ac.il/report/2011/095/revision/1/download/). The existing nonuniform NC¹ and logspace-uniform NC endpoints retain their own definitions.

## Existential real feasibility

`lean/InclusionBench/RealSyntax.lean` supplies the finite input syntax and reduction interface. `quantum/InclusionQuantum/RealFeasibility.lean` supplies `RealFeasibility.ETR` and `RealFeasibility.ExistsR`.

An input declares a finite variable count and a typed postfix program. Terms use indexed variables, binary natural coefficients, unary negation, addition, and multiplication. Formulas use equality, strict inequality, negation, conjunction, disjunction, true, and false. The stack interpreter must finish with exactly one formula; incorrect stack types, missing operands, extra results, and out-of-range variables are rejected.

Serialization consists of length-delimited tagged records encoded as bits. Tags, record lengths, and variable indices are unary; coefficient magnitudes are sequences of **binary digits**, never unary integers. Since the variable count is explicit and each valid index is smaller than it, this has at most polynomial overhead relative to the usual finite-variable formula encoding. Each coefficient retains linear bit length. Repeated squaring can be represented by additional existential variables when translating circuit or binary-exponent encodings; that conventional translation remains a bridge rather than an implicit input operation.

The executable decoder has a proved round trip, and serialization is proved injective. A final re-encoding check rejects malformed unary suffixes and noncanonical records. The module also proves that every arithmetic term and Boolean formula in the syntax compiles to the postfix program with the intended parsed result. Thus the language is not restricted to a hand-picked family of satisfiability instances.

Truth uses Mathlib's real numbers. A witness is a tuple `Fin variables → ℝ`; there is no rational-witness restriction, numerical tolerance, floating-point evaluation, or bit-length bound on a real witness. Invalid variables are rejected before the total evaluator's zero extension can matter. The semantic examples use x²=2 and x²=−1 to check positive and negative real feasibility.

A reduction is computed by one concrete total finite-control output transducer with a finite coefficient-list polynomial runtime. Its output tape is write-only, and its emitted binary word must belong to ETR exactly when the original input belongs to the source language. `ExistsR` is the collection of languages admitting such polynomial-time many-one reductions. Arbitrary functions without a machine witness do not qualify. The output-length bound follows from the transducer's time bound.

The standard equivalence between this ordered-field formula language, quadratic-system ETR encodings, and the usual ∃R class is a remaining representation bridge. In particular, this implementation does not replace real feasibility with rational feasibility, nor claim ∃R⊆CH or ∃R⊆P^#P. See the source evidence in the [classical baseline dossier](classical-new-baseline.md).

## Validation and review boundaries

All new definitions are explicit terms; none are opaque axioms or default class predicates. Core modules compile with Lean4.19.0 in one worker. RealFeasibility also compiles on the isolated Ubuntu Mathlib4.19 project, with one CPU and an 8GiB virtual-memory cap; its seven real-semantics lemmas and the encoding lemmas pass the axiom audit. `lean/AxiomAudit.lean` includes the new semantic and encoding lemmas. The only permitted dependencies are Lean's usual foundational axioms, not a project-specific axiom or `sorryAx`.

The final combined Mathlib build, complete61-entry interpretation, independent model review, and dataset-wide baseline audit are separate checks. A successful definition build establishes that these objects and the listed lemmas are formalized; it does not prove all cited textbook equivalences or all imported historical containments.
