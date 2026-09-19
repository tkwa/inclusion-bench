# AI evaluation protocol

InclusionBench evaluates an AI model's ability to resolve complexity-theory questions. One entry identifies a model configuration, an assigned set of questions, a declared budget and a single recorded run. Its accepted proofs and their consequences determine its score.

Version 0.3.0 is open for runs. Existing cited mathematics is trusted; re-formalizing those proofs is not required. The suite contains 1,378 frozen questions with recorded open-at-cutoff decisions from the [release audit](../research/baseline-audit.md). Runs reuse these revisable historical judgments; they still need proof and run-integrity review.

## 1. Freeze the benchmark

The release fixes the 50 class identifiers, their canonical operational definitions, uniformity conventions, baseline facts, implication rules, cutoff and candidate task list. A candidate is an ordered pair absent from the baseline's resolution closure. Its absence does not by itself establish historical openness.

A task asks whether A ⊆ B, A ⊄ B, or the encoded inclusion is independent of ZFC. Reversing the classes creates a different task. Equalities and strict containments can resolve several directions. The targets are classes of total binary decision languages; a promise problem or relativized question does not silently replace them.

The dataset and taskset have canonical JSON hashes. The taskset binds the formalization bundle, and `data/freeze.json` identifies the released snapshot. Use the checked-in frozen version for runs. A maintainer changing mathematical data or task conventions must create a new version and freeze it:

```sh
python3 -m inclusion_bench freeze
```

The canonical definitions are the target statements. Proving equivalence with every textbook presentation, adding aliases, or formalizing every historical theorem is useful further work, not a prerequisite to this protocol.

## 2. Declare the run

Record the model's exact API identifier, provider, reasoning/sampling settings, assigned task IDs, access track, tool policy, time limits and token budget before generation. Preserve the configuration and its hash. If the provider returns a different model identifier or only offers a mutable alias, retain both the requested and returned IDs; do not describe an alias as an immutable snapshot.

An assignment may be one question, a chosen subset, or the whole suite. Subsets are valid runs. Rankings compare matching **assignment, access track and budget** cohorts; a one-question run and a full-suite run are not ranked against each other as if their conditions matched. Preserve assignment order or its recorded shuffle seed.

The supplied adapters perform one attempt per assigned task, with a fresh context and no model tools or retrieval. Each receives the frozen baseline, all canonical Lean source files, and generated `TrustedBaseline` declarations. The provider prompt asks for one Lean body without imports, with `Submission.result_N` theorems mapped to the ordered claims; the verifier supplies fixed imports. A persistent agent sharing notes across tasks requires a separately declared configuration. Pool accepted statements at scoring time, rather than secretly feeding one attempt's answer into another independent-task attempt.

Do not discard unsuccessful attempts or publish the best of undisclosed retries. Provider failures, interrupted requests and partial outputs remain part of the run. Human theorem suggestions, proof repairs or extra prompting count as generation assistance and must be disclosed; reviewing an already sealed artifact is verification.

## 3. Run with explicit limits

Set the provider's normal credential environment variable, choose an exact model ID, and inspect the configuration's declared budgets. Replace `MODEL` below with that identifier:

```sh
python3 -m inclusion_bench preflight --config configs/openai.json --model MODEL
python3 -m inclusion_bench run --config configs/openai.json --model MODEL --output runs/first
python3 -m inclusion_bench evaluate-run runs/first/run.json
```

Preflight sends no provider requests. Use `--no-credentials` to check a configuration without requiring a key. The OpenAI starter configuration assigns `inclusion.NP.P`; override the assignment with repeated `--task` flags or `--all-tasks`. For Anthropic, select `configs/anthropic.json` and set `ANTHROPIC_API_KEY`.

The runner limits each attempt's wall time and the run's cumulative budget, preserves checkpoints, and seals the final manifest. An interrupted run may resume only with the original configuration and frozen taskset. An in-flight request with unknown remote usage does not receive a fresh token allowance on resume. Sealed runs are immutable.

The adapters call provider input-token counting before generation and reduce the output cap to fit the remaining total-token allowance. The Anthropic counter is an estimate; a configurable reserve provides headroom, and actual usage is checked afterward. Returned reasoning usage is already included in output tokens. Unknown usage stays unknown: the runner charges the remaining allowance conservatively and stops after an uncertain generation request. This is a spending control, not a claim that the provider billed exactly that amount. [Provider adapter details](../evaluation/adapters/README.md).

The built-in adapters run serially and perform little local computation. On Linux, the runner uses CPU affinity and a per-process memory limit; that is not an aggregate memory cap on arbitrary child processes. macOS has no hard CPU/RAM cap in this runner. Custom tool adapters need aggregate container isolation when their process-tree budget must be enforced. Keep concurrent local work within four CPU cores and 16 GiB, and record which limits were actually enforced. These limits describe local tools, not the remote provider's inference hardware. Record observed token usage, duration, tool activity and any overrun. Provider costs are not silently inferred from stale prices or missing usage.

## 4. Preserve evidence

The version 2 run manifest includes the frozen hashes, model identity, full configuration, assignment, budgets, timing, checkpoint history, attempts and an evidence index. Each attempt records its task and prompt digest, status, exact claims, artifact hashes, provider identity and usage.

| Attempt status | Meaning |
| --- | --- |
| `unsolved` | A completed answer asserts no resolved pair |
| `proof_candidate` | The model supplied exact claims and proof artifacts; acceptance is pending |
| `error` | A provider, transport, parsing or execution failure; available evidence is preserved |
| `budget_exhausted` | Time or token limits prevented completion; available partial work is preserved |

Preserve the final answer, full provider request and response, returned proof text, Lean source, notes, usage, provider response ID and diagnostics. Adapters save paths relative to isolated attempt directories; the runner seals the corresponding files with hashes. Credentials are never part of the published evidence. The provider adapters redact known key strings and omit authorization headers from logs.

A model's `accepted: true` or `verified: true` field grants nothing. Acceptance lives in a separate maintainer-controlled registry and binds the exact run, attempt, claims and artifact hashes. Later revisions are new evidence with explicit provenance, not silent replacements of sealed model output.

## 5. Review the run and its proofs

Generate a packet containing the sealed hashes and pending review records:

```sh
python3 -m inclusion_bench review-packet runs/first/run.json --output review.json
```

The run reviewer checks model identity, configuration and tools, budgets and usage, transcripts and artifacts, and undisclosed human assistance. Fill the packet's `run_review` section with the reviewer, rationale, evidence and explicit decision. The command accepts the packet directly and extracts that section:

```sh
python3 -m inclusion_bench review-run runs/first/run.json review.json
```

Run-integrity acceptance is separate from proof acceptance. A standalone run-review object is also accepted.

Every proof candidate must be accepted or rejected before publishing the final score. A reviewer may accept a verified subset of the model's claims, but cannot add an unsubmitted claim. Acceptance requires both statement matching and substantive proof review: the exact classes, uniformity, language conventions and inclusion direction must agree with the frozen catalog.

### Ordinary inclusions and non-inclusions

Use the submitted Lean body and its claims-to-theorem mapping to obtain a verification report. The adapter saves `adapter-artifacts/<provider-uuid>/claims-map.json` inside the attempt directory. Each ordinary claim includes a `theorem` field: `Submission.result_1` for the first original claim, `Submission.result_2` for the second, and so on. Independence entries are excluded from the automatic map without renumbering later claims.

Replace `SOURCE` and `CLAIMS_MAP` in the command with their sealed paths from the manifest, resolving relative paths beneath the run directory. Do not add imports to the sealed source: it runs under the verifier's fixed imports. The supplied canonical sources and generated baseline let the model refer to the exact target definitions and historical assumptions. See [proof format and verifier setup](PROOF_REVIEW.md).

```sh
python3 -m inclusion_bench verify-proof SOURCE --claims CLAIMS_MAP --report proof-report.json
```

The proof checker executes in a sandbox and checks the actual target with a fresh Lean kernel. The release's approved cited baseline and implication premises may be used. Arbitrary new axioms, an assumed version of the claimed result, or a proof of a different proposition do not establish a solution. Existing cited proofs do not need to be re-formalized as part of admission.

Review the mathematical argument and source alongside the report. The admitted source hash must match a sealed artifact from this attempt; a reviewer must not repair the proof and attribute the repair to the original model. Fill the matching entry in `review.json` under `proof_reviews`. For an accepted ordinary proof, set `proof_report` to its report path; relative paths are resolved from the review JSON's directory. Select the entry by its actual attempt ID:

```sh
python3 -m inclusion_bench review-proof runs/first/run.json review.json --attempt-id attempt-0001
```

Repeat for every proof candidate. Standalone proof-review objects remain supported; the packet form avoids copying hashes between files.

A consequence trace only establishes a deduction from its listed premises. It cannot verify a new premise by treating that premise as an assumption.

### Independence metatheorems

Independence has a separate expert-review lane. Its record must identify the exact encoded inclusion sentence, ZFC axioms and proof relation, metatheory, consistency assumptions, and evidence establishing unprovability of both the sentence and its negation. State conditional metatheorems as conditional; do not silently remove their assumptions.

The ordinary Lean checker is not an automatic ZFC-independence verifier. The absence of such a general verifier does not block ordinary inclusion evaluations. Independence resolves only its exact ordered pair and never becomes a negative edge in ordinary inclusion closure.

## 6. Review the history of positive points

Pool the accepted claims and compute their consequences on the frozen baseline. Before awarding any positive point, require a recorded decision about that pair's status at the cutoff, including the release's exact UTC convention. Reuse the release-wide decision when available; a run does not require a duplicate literature review. The history record names the dataset, reviewer, evidence, rationale and one of:

- `open_at_cutoff`: the direction is eligible for a point.
- `known_at_cutoff`: the direction earns no point, even if the baseline omitted its earlier resolution.

The release audit normally leaves no historical decisions pending. After accepting proofs, regenerate a packet to identify any remaining decisions:

```sh
python3 -m inclusion_bench review-packet runs/first/run.json --output history-review.json
```

If pairs are listed, inspect each one and fill that section's reviewer, decision, evidence and rationale. Then pass the whole packet; `review-history` extracts `history_review`:

```sh
python3 -m inclusion_bench review-history history-review.json
python3 -m inclusion_bench evaluate-run runs/first/run.json
```

A standalone history-review object also works. Skip `review-history` when the section is empty; the release decisions already satisfy the history gate. If the run has no resolved candidate pairs, no historical review is needed; an empty pending template is not an acceptance record.

History review applies to implied points as well as direct claims, including consequences outside the assignment. A source list alone does not certify openness. Consult the actual statements, versions and public availability dates. The cutoff is September 1, 2026, with its precise boundary specified in the release policy.

Retrospective omissions are expected to be possible. Keep the candidate set and inference rules frozen for the run; exclude the known pair through its historical decision and record any correction. Changing the frozen baseline itself creates a new version. Published rescoring must identify the review revision and preserve an audit trail rather than quietly replacing an old score.

## 7. Score and publish

For run `r`, let `S_r` be its accepted ordinary claims, `I_r` its accepted independence pairs, `B` the frozen baseline and `E` the positively reviewed eligible pairs. The score is:

```text
| E ∩ (pairs resolved by closure(B ∪ S_r) ∪ I_r) |
```

Count each ordered pair once. Do not add direct and implied resolutions twice or pool accepted proofs from different runs. Contradictory statements cannot earn points; a conflict blocks scoring until review resolves it. Preserve the derivation graph and its links back to accepted attempts, artifact hashes and cited rules.

An official result requires a sealed genuine model run, accepted run-integrity review, disposition of its proof candidates, and historical decisions for all candidate pairs the accepted claims resolve. Pairs already settled by the baseline need no additional history record and earn zero. A run with no accepted resolutions can receive a reviewed **zero** without certifying every unattempted question's history. A pending review produces an unavailable official score, not zero.

Once `evaluate-run` reports an official result, prepare its public evidence and register the leaderboard entry:

```sh
python3 -m inclusion_bench publish-run runs/first/run.json
python3 scripts/build_release.py
```

`publish-run` copies the manifest and only files in its sealed evidence index into `evaluation/published-runs/<run_id>`, then registers that manifest in `data/leaderboard_runs.json`. Unindexed files in a working run directory are not copied. Commit the published evidence, review registries and generated leaderboard together; pushing to GitHub and deploying are separate actions.

Publish the reviewed evidence, credited pair IDs, resource usage, cohort, verification decisions and replayable traces. Report assigned questions and actual attempted questions separately. A budget-stopped run must not claim that unattempted questions received model answers.

The public leaderboard contains only genuine reviewed runs. A fixture or mock API response is infrastructure validation and cannot enter it. The historical pre-cutoff reference has zero by definition; it is not a model evaluation.

The suite and rules are public. Training exposure and retrieval of post-cutoff solutions are possible. A score therefore does not establish blind generalization, independent discovery or priority. Report known exposure and the declared access policy; discovery claims require a separate literature and priority review.
