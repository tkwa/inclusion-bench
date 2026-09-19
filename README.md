# InclusionBench

**An AI mathematics benchmark built from open questions in complexity theory.**

Give a model a frozen set of complexity-class inclusion questions and a declared budget. Verify its answers, then award one point for each eligible ordered pair they resolve. Proven consequences count; duplicate resolutions count once within the run. The leaderboard entry identifies a model version and a single run.

[Leaderboard and task explorer](https://tkwa.github.io/inclusion-bench/) · [Evaluation protocol](docs/EVALUATION.md) · [Scoring specification](docs/SPEC.md) · [Formalization status](docs/formalization.md)

**Version 0.2.0 is open for model runs.** The release includes 50 canonical operational class definitions, a cited baseline and implication scorer, OpenAI and Anthropic adapters, token and time budgets, sealed run records, proof checking, review commands, and a static leaderboard. Existing cited mathematical results are trusted premises; formalizing their proofs is not a prerequisite to running or scoring.

The frozen suite contains **candidate questions**, meaning pairs unresolved in its baseline. A baseline omission can make a candidate already known, so every positive point requires a historical review confirming openness at the September 1, 2026 cutoff. A real run that resolves nothing can receive an official zero after run-integrity review and disposition of all proof candidates. No paid model run or model score was invented for this release.

## Run a model

Python 3.11 or later; no Python runtime dependencies. From the repository root, replace `MODEL` with the exact API model ID you intend to evaluate. Set `OPENAI_API_KEY` in your environment through your usual credential setup; never put credentials in a run configuration.

```sh
python3 -m inclusion_bench preflight --config configs/openai.json --model MODEL
python3 -m inclusion_bench run --config configs/openai.json --model MODEL --output runs/first
python3 -m inclusion_bench evaluate-run runs/first/run.json
```

Preflight sends no API requests. Inspect the configuration's token and wall-time limits before running. The starter configuration assigns only `inclusion.NP.P`; use repeated `--task` selections or `--all-tasks` to choose a different assignment. Subsets are valid evaluations, with separate comparison cohorts for each assignment, access track and budget. For Anthropic, use `configs/anthropic.json` and `ANTHROPIC_API_KEY`.

The adapters count input tokens before allocating the remaining generation budget. They preserve provider usage, partial answers and errors, and make no automatic retries. If a request may have been charged but its usage is unknown, the runner conservatively exhausts the remaining allowance and stops. [Provider setup, settings and accounting](evaluation/adapters/README.md).

The built-in adapters run serially and do little local computation. On Linux, the runner applies CPU affinity and a per-process memory limit; macOS has no hard CPU/RAM cap in this runner. Custom tool adapters need aggregate container isolation to enforce a process-tree budget. Keep concurrent local work within four CPU cores and 16 GiB; remote provider inference is outside those limits.

For checks that need no API key:

```sh
python3 -m inclusion_bench preflight --config configs/openai.json --model MODEL --no-credentials
python3 -m inclusion_bench run --config configs/fixture.json --output runs/fixture
```

The first command checks configuration only. The second uses an always-unsolved infrastructure fixture, labeled `smoke-test`; it cannot enter the AI leaderboard. Use a new output directory for each run. The runner checkpoints progress and supports resuming an interrupted run with the original configuration; sealed runs remain immutable.

## Review a result

Model assertions never approve themselves. Generate a review packet from the sealed run:

```sh
python3 -m inclusion_bench review-packet runs/first/run.json --output review.json
```

A reviewer checks the model identity, declared configuration, budgets, transcripts and artifact hashes. Each proof candidate is accepted or rejected separately.

Provider requests include the canonical Lean sources and generated `TrustedBaseline` declarations. Models are instructed to return one Lean body with `Submission.result_N` theorems mapped to their claims, without `import` commands: the verifier supplies fixed imports.

For an ordinary new inclusion or non-inclusion, replace `SOURCE` and `CLAIMS_MAP` below with the sealed paths from the run manifest, resolving relative paths beneath `runs/first`. The adapter saves the mapping as `adapter-artifacts/<provider-uuid>/claims-map.json` inside the attempt directory. It maps claim 1 to `Submission.result_1`, and so on, omitting independence claims from automatic verification:

```sh
python3 -m inclusion_bench verify-proof SOURCE --claims CLAIMS_MAP --report proof-report.json
```

Prepare a Linux verifier using the [setup instructions](docs/PROOF_REVIEW.md); `--local`, `--remote-root`, `--image` and `--toolchain-path` select your installation. The verifier uses a sandbox and a fresh Lean kernel, checking the actual class statement and limiting trusted assumptions to the release's allowed cited premises. A source that assumes its own conclusion is not a verified solution. The natural-language argument and class conventions also receive mathematical review. Independence uses a separate expert-review lane that identifies the encoded sentence, ZFC proof system, metatheory, assumptions and unprovability of both polarities.

Fill `run_review` and the relevant `proof_reviews` entry in `review.json` with the decision and evidence. For an accepted ordinary proof, set that entry's `proof_report` to the verifier report path, resolved relative to the review JSON. Record the completed sections directly:

```sh
python3 -m inclusion_bench review-run runs/first/run.json review.json
python3 -m inclusion_bench review-proof runs/first/run.json review.json --attempt-id attempt-0001
```

Repeat proof review for each candidate. After accepted proofs are recorded, generate a fresh packet to obtain their pending historical decisions:

```sh
python3 -m inclusion_bench review-packet runs/first/run.json --output history-review.json
```

Fill its `history_review` section for each listed pair, then record and evaluate it. Skip `review-history` if the section has no pairs:

```sh
python3 -m inclusion_bench review-history history-review.json
python3 -m inclusion_bench evaluate-run runs/first/run.json
```

No proof or history review is needed for an ordinary unsolved attempt. Before a positive score is published, every pair its accepted proofs resolve must be classified as open or known at the cutoff. Known pairs earn zero. Pending proof candidates or required history decisions keep the official score unavailable; unavailable is different from zero. [Full review protocol](docs/EVALUATION.md) · [Verifier setup and proof format](docs/PROOF_REVIEW.md).

Once evaluation reports an official score, register the run for the leaderboard:

```sh
python3 -m inclusion_bench publish-run runs/first/run.json
```

This copies the manifest and only its sealed, indexed evidence to `evaluation/published-runs/<run_id>` and registers it in `data/leaderboard_runs.json`. Rebuild the release to update the site. Committing and pushing the reviewed evidence and generated files to GitHub is a separate publication step.

## What earns a point

The target for `(A, B)` is **A ⊆ B**, inclusion between classes of total binary decision languages. Proving inclusion, proving its negation, or establishing an admissible ZFC-independence metatheorem resolves that ordered pair. Only directions open at the cutoff earn points.

Strict inclusion `A ⊊ B` means `A ⊆ B` and `B ⊄ A`. Accepted proofs from one run are pooled before closure, so implications can combine answers to different tasks and resolve questions outside the assigned subset. Results from different runs are never combined into an individual model score.

For example, a proof of `BPP ⊊ NP` would also establish `P ⊊ PSPACE`. Inspect the computed consequences on the frozen snapshot:

```sh
python3 -m inclusion_bench score examples/bpp-strictly-below-np.json
python3 -m inclusion_bench explain separation PSPACE P --assuming examples/bpp-strictly-below-np.json
```

These are scoring examples, not AI achievements. Pre-cutoff public knowledge scores zero by definition and appears separately from the model leaderboard. The suite is public: training exposure and retrieval of later solutions are possible. A valid score measures resolved questions under the declared access conditions; it does not establish independent discovery.

## The 50 classes

| Area | Classes |
| --- | --- |
| Nonuniform circuits and advice | AC⁰, ACC⁰, TC⁰, NC¹, P/poly, NP/poly |
| Space and parallel computation | L, NL, LogCFL, **uniform NC**, SC |
| Polynomial computation | P, NP, coNP, NP ∩ coNP |
| Randomness | RP, coRP, ZPP, BPP, SBP |
| Counting | UP, coUP, FewP, SPP, C₌P, PP, ⊕P, AWPP, LWPP, WPP |
| Proof systems | MA, coMA, AM, coAM, SZK |
| Quantum | BQP, QCMA, QMA, coQMA |
| Polynomial hierarchy | Θ₂P, Δ₂P, Σ₂P, Π₂P, PH |
| Exponential resources | E, NE, EXP, NEXP, PSPACE, EXPSPACE |

The [catalog](data/classes.json) fixes every convention. Nonuniform classes can contain undecidable languages and must not be silently included in EXP. Promise-only, fixed-exponent, search or algebraic advances need not resolve these total-language targets. The [coverage audit](research/coverage.json) documents examples and gaps; exhaustive coverage of every plausible breakthrough is not required.

## Frozen data and Lean

- [`data/classes.json`](data/classes.json): stable IDs, class specifications, uniformity and complement identities.
- [`data/knowledge.json`](data/knowledge.json): cited baseline facts and conditional implications.
- [`data/freeze.json`](data/freeze.json): the release's dataset and taskset hashes.
- [`evaluation/tasks.json`](evaluation/tasks.json): the fixed public candidate questions.
- [`research/`](research/): primary-source records, theorem locators and historical audit notes.
- [`lean/`](lean/) and [`quantum/`](quantum/): all 50 operational definitions and Lean inference/scoring foundations.

The definitions are the benchmark's canonical targets. The core covers 46 classes; the pinned Mathlib extension supplies the four quantum classes and agrees with the core interpretation. Alternative textbook characterizations, aliases such as IP for PSPACE, and further invariants can be added with documented equivalences. They are useful future work rather than launch requirements.

Existing cited theorems and substantive implication rules are explicitly trusted. New ordinary claims must pass the proof-admission checks. A generated consequence trace verifies a deduction from its stated premises; it does not verify a new premise merely by assuming it.

A maintainer changing the roster, baseline, definitions or rule set creates a new version and runs `freeze` to bind that snapshot. Historical reviews may identify a pre-cutoff omission without changing the questions mid-run: the affected pair earns no point, the review is recorded, and published scores are versioned when corrected. [Release policy](docs/RELEASE.md).

## Website and development

```sh
python3 scripts/build_release.py
python3 -m unittest discover -s tests -v
python3 scripts/check_generated.py
python3 scripts/check_lean.py
python3 -m http.server 8000 --directory web
```

Open `http://localhost:8000`. The static site has a model leaderboard, evaluation protocol, pair matrix, proof traces and secondary scoring examples. Copy `web/` into your website or embed the [deployed page](https://tkwa.github.io/inclusion-bench/). It has no analytics, external fonts, model API calls or backend. Provider adapter tests use a local mock server and fake credentials. [Development and embedding](docs/DEVELOPMENT.md).

The chosen name is **InclusionBench**. Alternatives: **ClassFrontier**, **ComplexityFrontier**, **SeparationBench**.

Original code and benchmark text are MIT-licensed. Linked papers retain their authors' copyrights.
