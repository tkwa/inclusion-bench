# Provisional v0.4.0 integration review

The review found six concrete integration defects or binding gaps. All have fixes on disk. No unresolved blocking code defect remains in the boundaries exercised here. Final isolated Lean replay and the release-wide audit/freeze are still parent-task work; this report does not treat those pending steps as completed.

The reviewed dataset has 50 scored classes, 61 inference classes and 1,324 candidate questions. The accompanying JSON records exact dataset, taskset and source hashes. Neither test fixtures nor hypothetical scoring examples are model evaluations.

## Findings and fixes

| Finding | Consequence before correction | Correction |
|---|---|---|
| Old verifier build list | Fresh sandbox compilation omitted new imported models and could not verify submitted proofs. | Build a deterministic import graph from hash-checked trusted sources. Reject missing imports, cycles, unsafe paths and source/hash discrepancies. |
| Scored-only census map | Retained background complements caused a `KeyError`. | Use all context identifiers in the external discovery census. |
| Unchecked proof-report identities | A report for identical proof bytes under older definitions or checker code could pass the dataset/source checks. | Recompute and require exact semantic, checker and target-bearing baseline digests, plus the verification method. |
| Unfrozen root imports | Changing a root Lean import did not invalidate the declared source bundle. | Include both root entry points in the formalization manifest. |
| Evidence links fixed to `main` | A provisional model row could point to evidence absent from `main`. | Honor the release's repository reference. |
| Old schema enums | The three public JSONSchemas rejected all eleven new class identifiers. | Generate their endpoint enums from the entire context catalog during the release build. |

The proof-report issue is an automatic binding failure within an explicitly trusted review boundary. The regression fixture deliberately supplied synthetic maintainer evidence; it did not produce a mathematical proof or show that model output can edit the trusted registry. Exact hashes prevent accidental reuse of stale evidence. They do not authenticate JSON fabricated by a malicious maintainer.

## Scoring and inference boundary

`Benchmark.ids` selects scored endpoints; `context_ids` supplies the complete inference vocabulary. Baseline saturation, complements, cited rules and submitted claim validation use all 61 entries. Eligibility, candidate task assignment and positive credit use only the scored matrix. Demoting a class therefore preserves its role inside a proof, even when its own ordered pairs receive no direct point.

A temporary V2 run submitted the background claim coRP ⊆ P. The adapter received all 61 class specifications and every new formalization module. The claim remained a valid proof target. With synthetic trusted evidence, the evaluator counted **zero direct pairs and fourteen scored consequences**, including RP ⊆ P. Every credited endpoint belonged to the scored roster. Background WPP-versus-LWPP independence scored zero and produced no ordinary closure consequences. The fixture used a local adapter, made no provider request and was deleted afterward.

Old dataset and taskset hashes were rejected. Reordering the scored roster changed the dataset identity and invalidated the old run. Resume still requires the exact normalized configuration and task suite. Cohorts retain assignment, budget, track and access-policy distinctions. Historical review accepts only scored candidate pairs; a background result can earn its surviving consequences only after those individual scored pairs receive history review.

The Lean catalog retains all 61 constructors and separately defines `scoredClasses` with 50 entries. Its ordered matrix and score bound use the latter. Conditional trace export continues to accept background constructors and emits the cited hypotheses actually used. The SAT encoding retains all context variables, while its ordinary report can restrict the tested candidate endpoints. The explicit all-context mode also checks background candidates. The pruning audit compares full-context deductions with surviving scored resolutions instead of assuming all demotions are free.

## Verification and generated artifacts

The new sandbox dependency discovery never inspects candidate imports. It accepts only safe first-party source paths already supplied with matching trusted hashes, checks the complete first-party graph for missing imports and cycles, then builds the dependencies of the two root imports. Checker support and the generated trusted baseline remain explicit later stages. Actual repository sources produce 33 first-party compilation units, including every new model and both independently authored semantic-check modules.

Proof generation and proof review now share one reconstruction of trusted inputs. A review checks the report's complete ordered claim list when rebuilding the target-bearing baseline. Accepting only a subset of a verified report does not permit changing that report's targets. Missing digests, all three mismatched digests, changed semantic source bytes and changed checker source bytes fail closed. An old-format report is retained only when it contains the required method and exact current identities.

A wheel was built from a temporary copy without downloading dependencies. All 35 files in the current formalization manifest were present with exact hashes. The wheel contained 41 Lean source files, and its packaged source graph reproduced the same 33 required first-party compilation units. No new model was silently omitted by the packaging globs. Schema regeneration now includes all context endpoints and is part of the generated-artifact reproducibility check.

The website payload exposes 50 matrix classes and 11 background definitions. Its label lookup merges both groups, and its shared proof graph retains background nodes. Generated-data tests check every proof node's display metadata and every scenario resolution's scored eligibility. The public leaderboard still contains no invented evaluation.

## Validation and remaining limits

The focused checks passed: 15 runner tests, nine integration-boundary tests, seven proofchecker unit tests, twenty benchmark tests and four release-data tests. Eight actual isolated Lean tests were explicitly skipped in this audit because the parent coordinates remote compilation and final replay. The review also repeated the complete temporary adapter/admission fixture and an actual wheel build. No paid or unpaid provider API request was made.

These checks address high-fanout failure modes directly, but they do not justify a calibrated numerical probability of zero software defects. Existing literature and model-equivalence claims remain trusted inputs; their mathematical validity is a separate review. Final Docker/Lean replay must still confirm that the new source order works in the real sandbox. A future trusted Lean import-header syntax outside the documented parser subset will fail closed and require a parser/test update. Browser behavior was inspected through its source and generated proof-graph tests rather than a repeated whole-application interaction session.
