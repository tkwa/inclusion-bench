# Provisional v0.4.0 roster review

User request: revise the class list to reflect important open problems and a sensible balance across complexity areas, without favoring tractable problems. Work for approximately one million tokens, implement justified changes to the established quality standard, and open a PR with a changelist for human review.

Base: v0.3.1, commit 5e4addcddd40f1a75a02b83dc26aaee2ac54b1cd. Worktree: inclusion-bench-v040. Branch: provisional-v0.4.0. No merge, release publication or tkwa.me deployment is authorized by this request; the user will review the PR.

Working assumptions: preserve the September 1, 2026 cutoff, approximately 40–50 scored classes, one point per open ordered pair, implication credit, and v0.3.1's independence-premise policy. Class selection is driven by scientific importance and coverage, not expected ease of proving results or formalizing definitions. Quantitative metrics inform expert judgment and must not be presented as an objective distribution over the field.

## Work phases

1. Independently assess the present roster and important omitted problem families, using primary surveys, open-problem collections, conference material and research reference chains.
2. Build an explicit comparison of candidate rosters: scientific coverage, family balance, duplication and complement effects, missing important questions, and sensitivity to reasonable expert preferences. Keep implementation cost separate from scientific value.
3. Decide the provisional roster and document retained, added and removed classes. Resolve representation questions before changing semantics.
4. Implement definitions, literature-backed baseline and implication rules, Lean interfaces, scorer/export/UI data and migration records. Preserve previous releases and audit provenance.
5. Independently audit all changed classifications and supporting theorem/model transfers; rerun finite-theory, Lean and proof-admission checks. Carry forward unchanged evidence only with exact scope and binding checks.
6. Freeze the provisional snapshot, prepare a concrete changelist and limitations in the PR description, push the branch, open and attach the PR. Do not deploy the provisional release.

## Resource limits

At most four local CPU cores and 16 GiB RAM. Compile serially; heavy Lean work may use the authorized Ubuntu host with explicit limits. Up to three independent research/review subagents accompany root work.

## Current state

The proposal is 50 scored endpoints in a 61-class context catalog. Add BPL, UL, PL, BQL, ExistsR, PSharpP, CH, QMA2, StoqMA, QSZK and UniformNC1. Demote AC0, coUP, coMA, coAM, coQMA, FewP, LWPP, WPP, coRP, E and Pi2P while preserving their definitions and inference paths. Thomas confirmed total decision-language classes only. The scientific selection remains provisional for PR review.

Three landscape reviews, two roster cross-reviews, three new-baseline dossiers, counting and classical baseline cross-reviews, and independent reviews of both sets of formal definitions are complete. The merged theory has 163 facts and 302 conditional rules. Its scored matrix has 845 known inclusions, 331 noninclusions and 1,324 candidates. All 2,500 old context classifications are unchanged. No accepted pre-cutoff proof has been disqualified because of a merely hypothetical future flaw.

All 61 definitions, 20 independent semantic invariants, and the combined core/quantum axiom audits passed a serial Ubuntu build. The core supplies 52 models and the Mathlib extension supplies nine. Existing literature proofs and textbook-model equivalences remain explicit trusted inputs. New ordinary proofs are checked in isolation against the exact release semantics; independence keeps its separate arithmetic-soundness-aware metatheory review.

Integration review found and fixed the proof checker's obsolete hardcoded module list, the external census's scored/context mismatch, and missing semantic/checker/baseline binding in admission of verification reports. Root is adding the two root Lean import modules to the frozen formalization manifest and correcting provisional branch links. Fresh isolated verifier tests, full generated/audit/history checks and final packaging/UI validation remain pending.

The full-context SAT pass checks 4,098 ordinary hypotheses with no additional forced classification. The final pruning experiment is being rerun after the two uniform-circuit conditional rules. Its preceding result found 725 inactive candidates and 26 positive hypotheses with no scored consequence; no tested negative hypothesis lost all credit. The tradeoff report also considers optional 55/56-class alternatives. These are scoring-scope experiments, not importance or tractability estimates.

Root owns canonical data, release generation, scorer/UI, migration/history, final audit assembly, packaging and the PR. classical_literature owns pruning tradeoffs; lean_kernel owns an independent residual-risk assessment; quantum_coverage owns the integration review and its admission regression fixes. The old freeze and history still identify v0.3.1, so this development checkout is not yet ready for model runs. Do not freeze v0.4.0 until mathematical data, semantics and the final audit are stable.

The isolated remote mirror is /home/tkwa/code/inclusion-bench-provisional-v040-01a0b850 on tkwa-ubuntu-box-wan, with an independent pinned dependency cache. Compiler: /home/tkwa/.elan/toolchains/leanprover--lean4---v4.19.0/bin/lean. Coordinate full synchronization; do not mutate the old inclusion-quantum-build. Local compiler: /private/tmp/lean-4.19.0-darwin_aarch64/bin/lean. Use serial builds and an 8 GiB limit for heavy Linux work.

The latest observed goal usage was 759,227 tokens, with 240,773 remaining in the original allowance. Thomas authorized another million if needed. No v0.4.0 commit, push, PR, release or deployment has occurred yet. Continue through a reviewable, tested PR and attach it to this task.

## Additional user steering

Thomas explicitly requested a loss analysis for pruning to the proposed most-important50. Root is computing every inactive pair under both ordinary polarities in the final61-class graph, and classical_literature is writing the scientific tradeoffs. Do not call the selection an objective ranking. Thomas also authorized another one million tokens if needed; use additional work only when it materially improves the audit, not as a requirement to spend all of it.

## Global selection clarification

Thomas clarified that the target is the best50 across the full field under his stated criteria, not the old50 or a subset restricted to the current61-node catalog. Before freezing, the three reviewers are challenging the roster against a broader total-language candidate pool. Existing implementation is not a selection constraint. The61-to50 computation remains a limited scoring-scope comparison; the final loss analysis must also cover important excluded classes never introduced into that catalog.

Thomas immediately clarified the candidate universe: **select the best50 from the current61**, not a fresh expansion beyond61. The earlier broader-review direction is superseded. The current proposal already differs from the original50; the completed61-to-selected50 pruning experiment is the relevant loss analysis. Agents have been redirected to finish the bounded61-class comparison and remaining audit work. No new outside class will be introduced for this clarification.

## Budget-limited checkpoint — September 20

The app marked the original goal budget-limited at 1,018,635 tokens; a subsequent read reported 1,020,929. Thomas had already authorized another million if needed, but it was not applied to the active goal's limit. The goal is not complete. No commit, push or PR exists yet. Resume the existing work rather than restarting the research or changing the selected roster.

Final selection is the best proposed50 from the current61, as clarified by Thomas. All agents stopped edits after completing their reports. classical_literature's bounded61-class sanity check retained the selected50; FewP is the closest restoration candidate. Optional55 restores FewP/LWPP/WPP/coUP/coRP and has1,655 candidates; optional56 also restores coQMA and has1,733. These are alternatives for review, not the implemented roster.

Current dataset: e929704944eba030d541cf2a12a6aa012cb7a0f10c003ca308a1dda65cd85ef5. Facts163, rules302, sources119; active845/331/1324; fullcontext1672 known and2049 candidates. All2,500 parent classifications unchanged. Final pruning is complete:725 inactive candidates,1,450 hypotheses,26 zero-credit inclusions and no zero-credit noninclusions. Every inactive pair loses direct independence credit. Final migration and pruning reports bind this dataset.

Validation now complete: core Lean build; all1,672 conditional baseline traces; SAT2,648 scored hypotheses and4,098 fullcontext hypotheses with no findings (221,345 clauses);98 Python tests passed with8 isolated tests skipped in that suite; JavaScript syntax and git whitespace checks passed. The initial Python run failed only because sandbox denied loopback mock-server sockets; the authorized rerun passed. Combined61-definition quantum/core build and20 independent invariants had already passed on Ubuntu with standard axioms only. No semantic Lean source changed afterward.

Actual isolated proof tests are still running in PTY session21049. Log: /private/tmp/inclusion-v040-proofcheck-final.log. At checkpoint, new11-target replay, extra-axiom rejection, fake-diagnostic rejection and forged-export kernel rejection passed; positive cited baseline was running. Poll this existing session/log before deciding whether any rerun is necessary. Runtime config: /private/tmp/inclusion-v040-proofcheck-runtime.json, pointing to the dedicated Ubuntu mirror. Python suite session31779 has finished successfully; log /private/tmp/inclusion-v040-python-final.log. Core log /private/tmp/inclusion-v040-core-final.log. Reviewed combined-build log /private/tmp/inclusion-v040-reviewed-build.log.

The local preview server remains in session94572 at127.0.0.1:8766. The in-app browser tab4 showed a well-laid-out provisional banner, correct50/2500/1176/1324 summary and empty genuine-model leaderboard. Searching BQL correctly filtered to one class; a follow-up checkbox locator did not match, so matrix interaction verification is unfinished. Reacquire the actual DOM button role before retrying, not the AX checkbox description. Browser documentation must be refreshed after compaction. The preview still shows pending history because freeze/registry assembly is not done.

Independent residual-risk review is now on disk. Its broad working expectation is2.9375 (publish as about3), with wide subjective sensitivity; do not claim below2 or reuse the old1.98 without adjustment. It excludes future-discovered flaws in currently accepted proofs, as requested. No concrete unresolved incorrect label was identified. Remaining model-equivalence and literature-completeness limits are explicit. Root has not yet adopted this in the release-wide assessment.

### Required completion sequence

1. Read final residual-risk-review.json and integration-review.json. All agents are done; do not alter their historical evidence casually. Mathematical data and semantic sources are stable. Existing isolated tests should finish before release acceptance.
2. Finish current audit assembly: write research/audit-assessment.json for v0.4.0, preserving archived v0.3.1 assessment; set literature_scope_reports to old3 domain reviews plus new3 baseline dossiers so all61 are covered. Include final SAT/Lean, migration/pruning, cross-reviews, semantic reviews and integration/risk reports as supporting evidence. Do not claim all old evidence was newly repeated. New roster_migration object must carry comparison_report, comparison_report_sha256, previous_assessment_file, previous_assessment_sha256, inherited_context_classifications_unchanged. check_generated validates those against a freshly recomputed compare().
3. Rewrite research/baseline-audit.md for current results/risks; the exact parent MD/JSON are now archived as baseline-audit-v0.3.1.*. Update stale research/AUDIT_STATE.md, final paragraphs of roster-decision.md and any release docs that still describe work in progress. Keep current user clarification clear:61→selected50.
4. Build the audit index with scripts/build_audit_index.py. Build release artifacts. Only then freeze provisional0.4.0 once all mathematical/semantic/audit inputs are stable; freeze refuses later same-version changes. Record fresh release-wide history decisions for1324 candidates with current audit ID/hash, preserving all old registry records. Rebuild web payload afterward and run check_generated.py. Do not weaken freeze checks or silently overwrite an existing0.4.0 freeze.
5. Finish actual isolated proof tests, credential-free preflight and a fixture run in a new temporary folder; fixtures remain unrankable. Full Python suite already passed; repeat only if new changes warrant it. Agent verified packaged wheel includes all35 formalization-manifest files with exact hashes and41 Lean sources. Final installed-package preflight and website interaction/history display checks remain useful.
6. Prepare a PR body with the concrete11 additions/11 demotions, scientific rationale,61→50 losses, optional55/56 comparisons, all61 definitions,163 facts/302 rules,1324 questions, preservedoldlabels, total-only scope, unchanged arithmetic-soundness policy, tests and candid≈3 subjective residual estimate. Explicitly state no model score, merge, release publication or tkwa.me deployment.
7. Commit and push provisional-v0.4.0 to tkwa/inclusion-bench; open the review PR and attach it with mcp__codex_app__attach_artifact. The workflow does not deploy PRs. Check CI and fix any actual failures. Do not merge or tag/publishv0.4.0. Update goal complete only when everything required is done, and report its final usage.
