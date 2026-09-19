# AI evaluation protocol

InclusionBench evaluates an AI system's attempts to solve open complexity-theory problems. One run assigns the frozen problem suite to a specified model configuration under a declared budget. Verified consequences of that run's proofs determine its score.

This document specifies the evaluation contract. The current release is a draft: candidate tasks can be generated and attempts can be recorded, but official scores remain unavailable until eligibility and semantic proof admission are certified. A hypothetical set of claims is not an AI evaluation.

## 1. Freeze the problems

A certified release contains one task for **every ordered pair certified open at the cutoff**, using the exact class definitions and uniformity conventions in that release. A task asks whether A ⊆ B, A ⊄ B, or the encoded inclusion is independent of ZFC. Reversed pairs are separate tasks. Equalities, strict containments, or stronger theorems can resolve several tasks through proved consequences.

The task manifest must contain:

| Field | Required content |
| --- | --- |
| `schema_version`, `benchmark_version` | Format and release identifiers |
| `dataset_sha256`, `taskset_sha256` | Digests of the frozen mathematical data and canonical task manifest |
| `cutoff`, `cutoff_convention` | The release's exact historical boundary; no runner-local date interpretation |
| `task_id`, `left`, `right` | A stable ID and two catalog IDs; one entry per ordered pair |
| `eligibility_status`, `eligibility_record` | Certified historical openness and the review record supporting it |
| `statement`, `definition_refs` | The actual inclusion question and exact operational conventions |
| `baseline_refs`, `prompt_sha256` | Permitted baseline material and the fully rendered prompt digest |

Sort tasks by `(left, right)` before hashing. The versioned schema must specify canonical JSON serialization and exclude the digest's own field from its hashed payload. Reject duplicate pairs, unknown IDs, missing definitions, and an eligibility manifest from another dataset. Freeze the rule set as well as the pair list; otherwise the same proof could receive different scores during an evaluation.

The draft may generate an analogous suite from pairs absent from its conservative baseline closure. Every such task must be marked `unreviewed`; absence from a database does not certify an open problem. These tasks support dry runs only. Once a certified eligibility manifest exists, both task membership and the full-suite completeness check must use that exact manifest, rather than the draft complement of known closure or a comparison of task counts alone.

## 2. Define a run before starting it

A leaderboard row identifies a **run**, not just a product name. Record the following before dispatch:

| Section | Required fields |
| --- | --- |
| Identity | `run_id`, `benchmark_version`, `dataset_sha256`, `taskset_sha256` |
| Model | Provider, exact model/snapshot ID, version date if known, API endpoint/version, reasoning configuration, sampling settings, and seed if the provider supports one |
| Harness | Repository commit, runner version, system/developer prompts, rendered task prompts, and their digests |
| Track | `closed-book` or `tool-assisted`; any human assistance and cross-task state policy |
| Planned budget | Per-task and total token limits, wall-clock limits, attempt limit, tool-call limits, and declared spending/resource caps |
| Tools | Exact allowlist, tool versions, network/retrieval policy, available proof libraries, and initial filesystem contents |
| Scheduling | Complete task list, deterministic order or recorded shuffle seed, concurrency limit, retry policy |
| Timing | UTC start/end timestamps and the measurement source |

If a provider does not expose an immutable snapshot, record the returned model ID and evaluation time, and label the snapshot as unpinned. Unknown usage fields stay `null` with a reason; they must not silently become zero. Record observed token usage, cost, tool calls, duration, and budget overruns after execution.

For a standard suite run, each task starts in a fresh context with identical shared baseline material. Do not feed one task's generated proof into another task during the run. Pool accepted mathematical consequences only at scoring time. A persistent agent that shares notes across tasks belongs in a separately labeled research-campaign configuration and is not directly comparable to independent-task runs.

The default attempt count is one per task. A run with multiple attempts must declare the count in advance, retain every attempt, and charge all of them to its budget. Do not publish the best of several undisclosed runs. Provider failures and retries must remain in the record even when a retry policy excludes a transport failure from mathematical attempt counts.

For local tools on the development host, retain the user's limits of four CPU cores and 16 GiB RAM in aggregate. A published evaluation must declare its own enforced limits; limits on local tools do not describe a remote model provider's inference hardware.

## 3. Keep access tracks separate

**Closed book:** the model receives the frozen prompt and supplied baseline material, with no external retrieval, tool calls, or computation during the attempt. A verifier may run afterward; its feedback is not returned to the model. The model may emit formal source as text.

**Tool assisted:** the model may use only the declared tools, within the declared budget. Record calls, outputs, retrieved URLs, retrieval times, and the content or immutable digest needed to reconstruct the evidence. Proof checking and model-directed revisions may occur inside the attempt. If network access is disabled, say so; if it is enabled, do not describe the run as closed book.

Human prompting beyond the frozen protocol, theorem suggestions, or proof repairs create a human-assisted configuration. Human review of an already sealed proof is verification, not generation assistance. Reviewers must not silently repair the submitted artifact and credit the repaired proof to the model.

## 4. Preserve attempts and proofs

Every assigned task gets an attempt record, including unsuccessful tasks. Record:

```json
{
  "attempt_id": "run-id/task-id/0",
  "task_id": "release-specific-task-id",
  "attempt_index": 0,
  "status": "proof_candidate",
  "started_at": "UTC timestamp",
  "finished_at": "UTC timestamp",
  "claims": [
    {"relation": "inclusion", "left": "A", "right": "B"}
  ],
  "artifacts": [
    {"path": "artifacts/proof.lean", "sha256": "content digest", "kind": "lean_source"}
  ],
  "transcript_sha256": "content digest",
  "usage": {}
}
```

The sample is a record shape, not a scored result. Catalog IDs, timestamps, and digests must be real values in an actual run. The implementation's versioned schema is authoritative for exact field names.

Use attempt statuses `unsolved`, `proof_candidate`, `budget_exhausted`, or `error`. Report tasks outside an executed subset as not attempted when summarizing suite coverage; do not invent model attempts for them. A proof candidate may later be accepted or rejected; the model cannot assign its own review status. A timeout with useful partial work remains `budget_exhausted`, with its partial artifacts preserved. Partial progress earns no point unless it contains a separately verified resolution.

Preserve the unedited final answer, complete conversation and tool trace, formal source, human-readable argument, exact theorem statement, imported dependencies, build command, environment/container identity, and verifier stdout/stderr. Hash artifacts when the attempt closes. Later revisions are new artifacts with explicit provenance; never overwrite the original.

## 5. Verify before awarding points

Admission has separate checks:

1. **Run integrity:** the attempt belongs to this run, uses the pinned task/dataset, and obeys the declared access and budget policy.
2. **Statement match:** the proof concerns the exact catalog classes, uniformity, inclusion direction, and unrelativized question. A relativized result, a promise problem, an added assumption, or a weaker circuit model does not silently replace the task.
3. **Proof verification:** replay the artifact in a clean environment. Audit all assumptions and imports. Reject incomplete proofs, unchecked axioms that assert the result, and a proof of a different proposition. A conditional theorem whose hypothesis is the submitted claim does not verify that claim.
4. **Semantic and historical review:** verify the connection between the formal statement and the catalog, the source/rule assumptions, and the pair's eligibility at the cutoff. Preserve reviewer identity, decision, reasons, artifact digests, and verification logs in a separate acceptance record.

The AI path uses two independent registries. `data/ai_reviews.json` records acceptance of exact attempts, artifacts, and claims. `data/ai_run_reviews.json` records a separate integrity review of the exact run, including its model snapshot, access policy, budget compliance, transcripts, and suite binding. A mathematically valid proof does not establish that a model produced it under the declared conditions, and a compliant run does not make its claims true. Official AI scoring requires both reviews; it does not require an additional aggregate entry in the legacy `data/reviews.json` submission registry.

The prototype's generated Lean traces certify that consequences follow **if the submitted statements and cited hypotheses hold**. They cannot by themselves satisfy step 3 for a new mathematical result. Current admission therefore remains blocked even if a local reviewer marks a claim promising. Distinguish `pending`, `accepted`, and `rejected` proof reviews from a release-level `official_score_available` flag.

An independence submission must identify the exact encoded sentence, ZFC axioms and proof relation, its negation, the metatheory, and every consistency assumption. It must establish unprovability of both polarities. A result conditional on Con(ZFC) stays conditional unless the frozen admission policy explicitly accepts that form. Lean's foundation is not automatically a formal implementation of ZFC. Independence resolves only its exact ordered pair and never enters ordinary inclusion closure.

## 6. Score the model's run

Let `E` be the certified eligible pairs, `B` the frozen baseline, `S_r` the ordinary claims accepted from run `r`, and `I_r` its accepted independence pairs. The official score is:

```text
score(r) = cardinality of
  E ∩ (pairs resolved by sound closure(B ∪ S_r) ∪ I_r)
```

Pool proofs across attempts **within that run** before computing closure. This gives stronger results their full consequence credit and allows two independently proved premises to imply a third result. Count each ordered pair once, even if several tasks, attempts, proofs, or inference paths resolve it. Do not pool proofs from different models or runs into an individual run's score.

The pooled accepted statements must be mutually compatible with the baseline and the independence policy. If they conflict, block official scoring until review resolves the conflict; logical explosion earns nothing. Preserve the explanation graph from every credited pair back to accepted artifact IDs and baseline/rule IDs. If a new theorem has consequences beyond the frozen inference engine, submit proofs of the additional pair statements; a model-written rule is not automatically trusted or inserted into the baseline.

Report the resolved-pair score alongside assigned/attempted tasks, accepted proofs, directly resolved tasks, consequence-resolved tasks, pending/rejected candidates, and measured resource usage. These secondary counts must not be added to the score. A partially executed suite is labeled partial; it is not a standard full-suite ranking entry. Registry corrections require a versioned rescore and a public change record.

## 7. Publish results without overstating them

Publish the run manifest, proof artifacts, verification decisions, credited pair IDs, and replayable consequence traces. Use `null` or “not available” for an uncertified score and “not run” for a model with no recorded evaluation. Zero is appropriate for a completed, admissible run that resolved no eligible pair. The historical pre-cutoff reference receives zero by definition; it is not a measured AI result or evidence that a particular model was evaluated.

The suite is public. Both closed-book training contamination and tool-assisted retrieval of post-cutoff solutions are possible. It cannot establish blind generalization, prove that a model discovered a result independently, or establish a discovery date from a transcript alone. Record known exposure and retrieval evidence. A valid post-cutoff proof may solve the fixed benchmark task, but a retrieval-assisted run must be labeled accordingly. Claims of original discovery require a separate priority and literature review.

Solved toy tasks, parser fixtures, and the Lean smoke tests validate the harness. They are not members of the open-problem suite and cannot contribute official points. No model scores should be generated from those fixtures or invented as illustrative leaderboard entries.

## Current adapter contract

`inclusion_bench.evaluation.taskset` exports the draft tasks. `run_adapter` sends one JSON request on the adapter's standard input for each selected task. The request contains the task, catalog, knowledge base, dataset digest, remaining wall time, and response schema. The trusted adapter runs its configured model and returns one JSON object on standard output:

```json
{"status": "unsolved", "claims": [], "artifacts": []}
```

For a proof candidate, `artifacts` is a list of relative file paths written inside the run directory. The runner validates the paths and computes their hashes before creating the manifest. An adapter for a text-only model must save the emitted proof text/source to a file and return its path. Standard output must contain only the response JSON; diagnostic output goes to standard error. The adapter must preserve the full model/tool transcript in artifact files.

`evaluate_run` validates the manifest and consults `data/ai_reviews.json` for proof acceptance. These records bind the run digest, attempt digest, exact claims, artifact hashes, and verification record. Official admission separately consults `data/ai_run_reviews.json` for the exact run's integrity review and checks full membership of the certified task suite. Model-authored metadata cannot create either acceptance record. The old aggregate submission registry, `data/reviews.json`, is not an extra requirement for the AI-run path.

The Linux/macOS draft runner enforces its wall-time deadline, terminates the adapter process group at attempt end, and caps captured output at 8 MB for the response and 1 MB for diagnostics. Artifact hashes are computed in streaming chunks. The adapter/container must enforce and document tool access, token budgets, CPU/RAM limits, and other declared restrictions. The minimal generated manifest does not itself establish compliance with the full certified-run protocol above. Fill the required audit fields and independently verify enforcement before publishing a comparable model result.

`evaluation/unsolved_adapter.py` is an infrastructure fixture that always reports unsolved. It must use the `smoke-test` track, which is excluded from official scoring. It is not an AI model evaluation.

From the repository root, export the task suite and exercise that fixture with:

```sh
python -m inclusion_bench tasks --output evaluation/tasks.json
python -m inclusion_bench run-adapter \
  --model not-a-model --model-version infrastructure-fixture \
  --output runs/protocol-smoke --task inclusion.NP.P \
  --wall-seconds 60 --track smoke-test \
  -- python "$PWD/evaluation/unsolved_adapter.py"
python -m inclusion_bench evaluate-run runs/protocol-smoke/run.json
```

Choose an unused output directory; the runner refuses to overwrite an existing run. The task asks whether NP ⊆ P; the opposite orientation is a known baseline inclusion and is not an open task. This command sequence exercises one task and produces an unranked partial smoke run. It does not evaluate a model or create a proof-verification record.

For a real run, replace the fixture with a provider adapter, declare the model snapshot and access track, assign the intended full task suite, and preserve the required audit evidence. There is currently **no end-to-end automatic checker for submitted research proofs and no certified official release**. The adapter and manifest evaluator are runnable; acceptance of new mathematics remains a separate proof-verification and maintainer-review obligation.
