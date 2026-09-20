# Provisional release 0.4.0

This branch proposes a revised InclusionBench roster for review. It keeps 50
scored total decision-language classes, adds 11 endpoints and retains the 11
demoted endpoints as unscored proof vocabulary. The published v0.3.1 release and
[tkwa.me](https://tkwa.me) are separate; this branch does not deploy either site.

The [roster decision](../research/v0.4.0/roster-decision.md) explains the scientific
choices. The [pruning audit](../research/v0.4.0/pruning-audit.json) measures losses
against the full 61-class context, including cases that keep some consequence
credit and cases that lose all credit. These are explicit tradeoffs, not an
objective ranking of the field's most important classes. Expected tractability
and implementation difficulty are not selection criteria.

## Changelist

| Change | Purpose |
| --- | --- |
| Add BPL, UL, PL, BQL | Represent space-bounded randomness, ambiguity, counting and quantum computation |
| Add uniform NC¹ | Represent the uniform NC¹-versus-L boundary separately from nonuniform formula lower bounds |
| Add ∃R | Represent real feasibility within the existing binary decision-language universe |
| Add P^#P and CH | Represent deterministic counting-oracle computation and the counting hierarchy |
| Add QMA(2), StoqMA, QSZK | Represent unentangled proofs, restricted quantum verification and quantum zero knowledge |
| Demote AC⁰, coUP, coMA, coAM, coQMA, FewP, LWPP, WPP, coRP, E, Π₂P | Keep the scored roster at 50 while preserving their definitions and implication paths |
| Separate context and scored classes | Prevent background pairs from earning direct points without deleting supporting mathematics |
| Extend definitions, baseline and audits | Bind the new targets, cited implications, historical review and proof checker to a distinct snapshot |
| Add independent semantic checks | Test specific model risks beyond successful compilation |
| Mark the explorer provisional | Make the review status and cross-version score limits visible |

The provisional matrix has 845 known inclusions and 331 known noninclusions,
leaving 1,324 candidate questions. The [migration audit](../research/v0.4.0/roster-migration.json)
checks that every parent fact, rule, source and complement identity remains
present and that all 2,500 parent context classifications are unchanged.
Historical admission is recorded separately in the [release audit](../research/baseline-audit.md).
A missing pre-cutoff result earns no point and requires a recorded correction.

The arithmetic-soundness policy introduced in v0.3.1 is preserved. Independence
metatheorems may be unconditional or conditional on Con(ZFC) or arithmetic
soundness of ZFC. Every accepted pair needs its exact encoded sentence and
both nonderivability arguments under the recorded premise. The full ZFC
encoding and metatheorem remain expert-reviewed; independence supplies no
ordinary implication premise.

## Running and comparing evaluations

The runner, provider adapters, sealed evidence, review commands, isolated Lean
proof checker and leaderboard remain available. Existing cited mathematical
results are trusted inputs; recreating their proofs in Lean is not a condition
for running the benchmark.

Scores belong to the exact frozen taskset. A v0.3.1 score cannot be copied into
the v0.4.0 leaderboard: the candidate universe and implication library differ.
Subset runs are allowed, but ranks compare the same assignment, access track
and resource budget. A reviewed real run with no accepted solutions can score
zero. Infrastructure fixtures and mock-provider tests do not enter the AI
leaderboard, and no paid run was performed for this revision.

Accepted supporting claims may mention any of the 61 context classes. Only
newly resolved, historically eligible pairs with two scored endpoints count.
An inactive pair never earns a direct point, even for independence. Preserving
its definition therefore does not preserve all of its former scoring weight.

## Trust boundary

The core defines 52 classes. The pinned Mathlib extension supplies eight quantum
classes and ∃R, and proves agreement with every core interpretation. The new
models use finite operational machines, circuits or encodings; no new class is
an unconstrained axiom. Independent reviews inspect the literature bridges and
retain adversarial checks. Compilation alone does not prove equivalence with
every textbook convention or certify historical openness.

New ordinary claims must pass mathematical review and the isolated Lean proof
checker. A consequence trace with an assumed submission is not a proof of that
submission. The verifier permits only the exact release's cited baseline
assumptions and standard Lean foundations. Source, statement, dataset and
artifact hashes remain part of admission.

The historical audit is AI-assisted, with domain reviews and independent
cross-reviews. It is not human expert endorsement. Lean replay checks inference
from explicit cited premises; SAT checks the finite encoded theory. Neither
proves that no paper was missed. The release-wide assessment records its
residual uncertainty without treating a subjective estimate as a guarantee.

## Promotion and future changes

This is a review branch, not a published v0.4.0 release. Before promotion, review
the changelist, scientific losses, exact class conventions and remaining trust
boundaries. Publication and the separately developed tkwa.me integration are
outside this PR's deployment scope.

Changes to the roster, definitions, baseline or rules require a new versioned
freeze. Preserve previous history records and their dataset hashes. Later
historical corrections can disqualify a question without silently changing a
sealed run's mathematical taskset; any published rescore must identify its
review state.

Promise, search/function and algebraic tracks are outside this revision at
Thomas's explicit request. They remain possible future work with their own
objects and scoring rules. The primary metric remains one point per eligible
ordered pair. See the [evaluation protocol](EVALUATION.md),
[formalization notes](formalization.md) and [proof-review format](PROOF_REVIEW.md).
