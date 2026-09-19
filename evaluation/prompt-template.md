# InclusionBench task {{task_id}}

You are being evaluated on your ability to solve a complexity-theory research problem. Resolve the following ordered-pair question by proving it, disproving it, or proving the specified independence statement. Reporting that you have not solved it is an acceptable outcome. An `unreviewed` eligibility status denotes a provisional task; do not infer historical openness from that status.

**Question:** Is **{{left_display}} ⊆ {{right_display}}**?

- Left class ID: `{{left_id}}`
- Right class ID: `{{right_id}}`
- Exact statement: {{statement}}
- Class definitions and conventions: {{definition_material}}
- Historical cutoff and convention: {{cutoff_material}}
- Eligibility status: {{eligibility_status}}
- Benchmark release: `{{benchmark_version}}`
- Dataset digest: `{{dataset_sha256}}`
- Supplied baseline and permitted references: {{baseline_material}}

Inclusion means inclusion of sets of languages over finite binary strings. It does not mean a reduction. Preserve the supplied uniformity, advice, promise, and machine conventions. Do not replace an unrelativized problem with an oracle-relative one.

## Access and budget

- Evaluation track: `{{track}}`
- Allowed tools and retrieval policy: {{tool_policy}}
- Per-task limits: {{task_budget}}
- Remaining run-wide limits: {{run_budget}}
- Output/artifact location, if available: {{artifact_location}}

Use only these permitted resources. The runner records all attempts and tool use. In a closed-book attempt, you have no tool or retrieval access; formal source can be returned as text for later verification. In a tool-assisted attempt, include retrieved sources and use the declared proof environment when available.

## What to submit

If you find a proof, provide the exact theorem statement, a complete argument, all assumptions and dependencies, and any formal proof source and build instructions. State which of the following you establish:

- `inclusion`: {{left_display}} ⊆ {{right_display}}.
- `separation`: {{left_display}} ⊄ {{right_display}}. Merely proving that two classes are unequal does not identify this direction.
- `independence`: neither the exact encoded inclusion sentence nor its negation has a proof from ZFC, in an explicitly stated metatheory.

For independence, supply the sentence encoding, proof relation, both unprovability arguments, and all consistency assumptions. Do not identify independence with a contradiction or with failure to find a proof.

You may submit a stronger theorem and additional pair consequences. Separate established claims from conjectures and partial observations. A conditional result must retain its hypothesis. Do not introduce an axiom equivalent to the desired result, leave a proof hole, or treat a cited theorem as checked without explaining its applicability. Definitions alone do not prove a new class relation.

Finish with a machine-readable record followed by your proof or an explanation of what remains unresolved:

```json
{
  "task_id": "{{task_id}}",
  "status": "unsolved",
  "claims": [],
  "artifacts": [],
  "assumptions": [],
  "references": [],
  "summary": "State what you established, or why this attempt remains unsolved."
}
```

Set `status` to `proof_candidate` only when you submit a complete argument. Each claim must have `relation`, `left`, and `right` fields using the catalog IDs. `artifacts` lists relative paths inside the assigned run directory. When you cannot create files, place their exact proposed contents in labeled code blocks after the record; the provider adapter must archive them as files before submitting its runner response. Do not assign yourself a verified status or a score.

Only independently accepted proofs can earn points. The evaluator pools accepted consequences from this run and counts each eligible ordered pair once. A result already known before the cutoff, an unsupported claim, or partial progress alone earns no point.
