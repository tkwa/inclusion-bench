# Development, evaluation and embedding

Version 0.2.0 is operational. The Python runner and consequence scorer use the standard library. The complete Lean proof target includes all 50 canonical definitions. Historical results are trusted, cited inputs; new ordinary model claims use the isolated proof verifier. See [the evaluation protocol](EVALUATION.md) for run policy and [formalization status](formalization.md) for the trust boundary.

Run commands from the repository root. An editable installation (`python3 -m pip install -e .`) also exposes the `inclusion-bench` command.

## Check a development change

```sh
python3 scripts/build_release.py
python3 -m unittest discover -s tests -v
python3 scripts/check_generated.py
python3 scripts/check_lean.py
```

Install the version in `lean/lean-toolchain`, or set `LEAN_BIN` to that compiler's absolute path. The core check builds modules serially and checks exported inference traces without Mathlib. For the complete interpretation, including quantum classes:

```sh
bash scripts/check_quantum.sh
```

This script uses the pinned official Lean release and selective Mathlib cache, constrains the Linux work to one CPU and 8 GiB, and audits the permanent library for incomplete proofs and unexpected axioms. See [the quantum build instructions](../quantum/README.md) for setup details. CI requires both core and quantum jobs before deployment.

Local adapters default to one CPU and 4 GiB, and configuration rejects limits above four CPUs or 16 GiB. The built-in provider adapters run serially and perform little local computation. Linux enforces CPU affinity and a per-process memory bound; macOS has no hard CPU/RAM cap in this runner. Per-process limits do not cap an arbitrary child-process tree, so custom tool adapters need aggregate container isolation. Keep concurrent local work within the four-core/16-GiB development budget. The isolated proof checker runs on Linux with one CPU and 8 GiB. These resource limits do not describe the remote model provider's inference hardware.

## Change mathematical data and freeze a release

`research/classical.json` and `research/quantum.json` are the literature inputs. The importer assembles them into `data/knowledge.json`; editing generated data alone fails the reproducibility check. Edit class specifications in `data/classes.json`, then rerun the importer and release build. `scripts/catalog_seed.py` is an authoring utility, not a routine build step.

Keep exact source locators, historical dates, model conventions and uncertainties with each change. The [baseline audit](../research/baseline-audit.md) distinguishes family-level screening from per-pair historical decisions. The current baseline has 709 inclusions, 405 noninclusions and 1,386 candidate questions.

After intentionally changing the versioned dataset, rebuild and freeze it:

```sh
python3 scripts/build_release.py
python3 -m inclusion_bench.cli freeze
```

`data/freeze.json` binds the dataset, taskset, formalization bundle and audit. Freezing does not certify all candidates open. A normal evaluation uses the existing freeze; it must not silently replace the dataset underneath an earlier run. Historical decisions about that version's candidates go in `data/history_reviews.json`, preserving the original frozen question set.

## Start a model run

Choose an exact model identifier and inspect the starter configuration's assignment and budgets. In these examples, replace `MODEL` with the intended identifier and set the provider credential through its environment variable:

```sh
python3 -m inclusion_bench.cli preflight --config configs/openai.json --model MODEL
python3 -m inclusion_bench.cli run --config configs/openai.json --model MODEL --output runs/first
python3 -m inclusion_bench.cli evaluate-run runs/first/run.json
```

Preflight sends no model requests. `--no-credentials` checks the configuration without requiring a credential. Use `configs/anthropic.json` for the supplied Anthropic adapter. The built-in provider adapters are closed-book; a tool-assisted run needs a custom adapter and a declared access policy. Never put credentials in a saved configuration. Provider requests contain all canonical Lean sources and generated `TrustedBaseline` declarations. The response format asks for one Lean body, no imports, and `Submission.result_N` declarations mapped to exact claim objects. The verifier supplies the trusted imports; each verification claim's `theorem` field names its declaration.

Use repeated `--task` options for a selected assignment or `--all-tasks` for the full suite. Subsets are valid, labeled evaluations. Preserve the exact assignment, order or shuffle seed, model settings, tools and budget so the cohort can be reproduced. The schema-v2 `run` command records checkpoints and seals requests, responses and proof artifacts with hashes. An interrupted run can use `--resume` with its original configuration. A sealed run cannot be resumed.

The `run-adapter` command remains available for the older adapter interface. Use schema-v2 `run` for operational official admission. Fixtures must use the smoke-test track and cannot appear as model results.

## Review and verify the sealed evidence

Create pending review records for a run:

```sh
python3 -m inclusion_bench.cli review-packet runs/first/run.json --output review.json
```

The packet contains run and attempt hashes, artifact hashes, and pending `run_review`, `proof_reviews` and `history_review` sections. A maintainer completes these sections from inspected evidence. The review commands accept the packet directly; standalone review objects also remain supported. A packet is not an approval, and a model-provided verification claim is not a trusted review.

| Command | Required decision or evidence |
| --- | --- |
| `review-run MANIFEST REVIEW` | Reviewer, rationale, exact run hash, and checks of model identity, setup, budget, transcripts/artifacts and unreported human assistance. |
| `verify-proof SOURCE --claims CLAIMS --report REPORT` | Sealed Lean source plus exact ordinary claim objects and theorem names; produces verifier evidence without awarding points. |
| `review-proof MANIFEST REVIEW --attempt-id ID` | Exact run/attempt hashes, accepted or rejected claims, and the verified report for accepted ordinary claims. |
| `review-history REVIEW` | Dataset hash, reviewer, evidence and rationale for each pair classified `open_at_cutoff` or `known_at_cutoff`. |

For an ordinary candidate, replace `SOURCE` with its sealed Lean body and `CLAIMS_MAP` with the sealed `adapter-artifacts/<provider-uuid>/claims-map.json` inside its attempt directory, resolving manifest-relative paths beneath the run directory. Provider-generated output maps the original claim positions to `Submission.result_1`, `Submission.result_2`, and so on; independence claims are omitted without renumbering the others. Use the declaration names actually present in the source. Fill `run_review` and the matching `proof_reviews` entry in `review.json`. An accepted ordinary proof entry needs `proof_report`, resolved relative to the review JSON, for example `proof-report.json` when both files are in the same directory:

```sh
python3 -m inclusion_bench.cli verify-proof SOURCE --claims CLAIMS_MAP --report proof-report.json
python3 -m inclusion_bench.cli review-run runs/first/run.json review.json
python3 -m inclusion_bench.cli review-proof runs/first/run.json review.json --attempt-id attempt-0001
```

After recording every proof decision, regenerate a packet to list the historical reviews needed for accepted consequences:

```sh
python3 -m inclusion_bench.cli review-packet runs/first/run.json --output history-review.json
```

Fill its `history_review` section, then record the section and evaluate the run. If no pairs are listed, skip `review-history`; an empty pending section is not a review decision:

```sh
python3 -m inclusion_bench.cli review-history history-review.json
python3 -m inclusion_bench.cli evaluate-run runs/first/run.json
```

Use [the public Linux setup instructions](PROOF_REVIEW.md) to prepare the pinned Lean/Mathlib environment and Docker image. `--local` selects Docker on the current Linux host; `--remote-root` identifies the prepared clone, and `--image` and `--toolchain-path` select the installed image and compiler. `--host` selects an authorized SSH host, and `--timeout-seconds` controls each verifier stage. The initial deployment defaults to `tkwa-ubuntu-box-wan` and `/home/tkwa/code/inclusion-quantum-build`; that private host is not a prerequisite for other installations. Verification has no unsandboxed fallback and does not pull an image. The Python API uses `host=None` for the local Docker route.

The verifier rebuilds the trusted source bundle and generates an explicit historical-baseline axiom allowlist. Candidate elaboration has no network or writable host mount. A fresh process reconstructs exported declaration data and kernel-checks every declaration and exact target. Candidate compiled modules are never imported into replay. The current proof format does not support new inductive declarations. See [proof format and verifier installation](PROOF_REVIEW.md) and [formalization status](formalization.md) for the complete limits.

The registries are `data/ai_run_reviews.json`, `data/ai_reviews.json` and `data/history_reviews.json`. They are maintainer-controlled evidence. The review code binds ordinary proof reports to sealed source hashes and cannot turn an unsubmitted claim into a model result. Review every proof candidate, including rejected ones, before final scoring. A source repaired after sealing is new evidence; it must not be attributed to the original model output.

Historical review covers all candidate consequences of accepted proofs, including implications outside the assigned subset. Pairs already known at the cutoff earn zero. With no accepted resolutions, a genuine run can receive an official zero after provenance review and complete candidate adjudication; unclaimed pairs need no blanket openness certificate. At least one genuine request must have a completed model answer. Empty/error-only runs and smoke tests are not scored model results.

Independence uses the separate expert metatheory review lane. Its record must identify the encoded sentence, ZFC proof system, metatheory, assumptions and both unprovability arguments. The absence of automatic ZFC syntax and proof encoding does not block ordinary evaluations.

## Export a conditional consequence to Lean

```sh
python3 -m inclusion_bench.cli export-lean separation PSPACE P \
  --assuming examples/bpp-strictly-below-np.json \
  --output lean/ExampleConsequence.lean
python3 scripts/check_lean.py
```

This exporter proves the selected inference trace from visible baseline, rule, complement and submission hypotheses. Compiling it establishes the conditional deduction; it does not verify an assumed breakthrough. The `verify-proof` route instead checks a submitted theorem against its exact target while permitting only the approved historical assumptions. Independence is excluded from ordinary trace export.

The checked examples exercise transitivity, both separation directions, complement transport, forward rules and contraposition. Python tests additionally check generic closure soundness over interpretations of three class symbols as subsets of a two-element universe.

## Publish and embed the leaderboard

After the run has an official score:

```sh
python3 -m inclusion_bench.cli publish-run runs/first/run.json
python3 scripts/build_release.py
```

`publish-run` validates the result, copies the manifest and only sealed evidence-index files into `evaluation/published-runs/<run_id>`, and registers its repository-relative manifest in `data/leaderboard_runs.json`. Unindexed working files are not copied. Repository commit/push and website deployment are separate actions; registration does not send anything to GitHub. Include the published evidence, review registries and generated leaderboard in the publication commit.

The release generator re-evaluates every registered run and refuses a non-official result. Keep the proof artifacts and all three review registries available with the manifest. Rank cohorts bind the taskset, exact assignment, access track, budget and access policy. Equal scores within a cohort share a rank. Full-suite and declared-subset results show their scope and assignment count; their ranks are not interchangeable.

Serve `index.html`, `styles.css`, `app.js` and `benchmark.json` from `web/` over HTTP. They use relative URLs and no external dependencies. Copy the directory into an existing site or embed the hosted leaderboard:

```html
<iframe
  src="https://tkwa.github.io/inclusion-bench/"
  title="InclusionBench leaderboard and complexity-class explorer"
  style="width:100%;height:1200px;border:0"
  loading="lazy">
</iframe>
```

GitHub Actions publishes to GitHub Pages after both verification jobs pass. The site shows the version and hash, operational review policy, actual reviewed model runs, the historical zero reference and separately labeled hypothetical examples. Deployment changes this repository's site, not another website.
