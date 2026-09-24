# InclusionBench

**Software v0.4.3** accepts multi-file Lean projects and supplies uniform integer-array interfaces with length, bit-size, and computation guarantees. Agents can reuse trusted textbook results and cite additional published dependencies for statement and model-alignment review without formalizing their original proofs. [Agent submission guide](docs/AGENT_SUBMISSIONS.md) · [Release notes](docs/RELEASE-0.4.3.md). The frozen v0.4.0 questions and scores are unchanged.

The current same-version build 1 accepts proof exports up to 256 MiB. Its wheel is `inclusion_bench-0.4.3-1-py3-none-any.whl`; the original tag and unnumbered wheel retain their 32 MiB limit. [Download and exact source revision](https://github.com/tkwa/inclusion-bench/releases/tag/v0.4.3).

> **v0.4.0 publication:** approved through [PR #1](https://github.com/tkwa/inclusion-bench/pull/1). Use the immutable [v0.4.0 tag](https://github.com/tkwa/inclusion-bench/tree/v0.4.0) to reproduce this release. Current publication state comes from [`data/publication.json`](data/publication.json).

**An AI mathematics benchmark built from open questions in complexity theory.**

Give a model a frozen set of complexity-class inclusion questions and a declared budget. Verify its answers, then award one point for each eligible ordered pair they resolve. Proven consequences count; duplicate resolutions count once within the run. The leaderboard entry identifies a model version and a single run.

[Public site](https://tkwa.me) · [Leaderboard and task explorer mirror](https://tkwa.github.io/inclusion-bench/) · [Evaluation protocol](docs/EVALUATION.md) · [Scoring specification](docs/SPEC.md) · [Formalization status](docs/formalization.md)

**v0.4.0 scores 50 classes, backed by 61 canonical operational definitions.** It supplies a cited baseline and implication scorer, OpenAI and Anthropic adapters, token and time budgets, sealed run records, proof checking, review commands, and a static leaderboard. Existing cited mathematical results are trusted premises; formalizing their proofs is not a prerequisite to running or scoring.

The suite contains **1,324 questions at the September 1, 2026 cutoff**. The [release audit](research/baseline-audit.md) records historical eligibility for every question, so model runs reuse those decisions. The [roster decision](research/v0.4.0/roster-decision.md) explains eleven additions, eleven demotions, alternatives and lost coverage. Scores are not directly comparable with v0.3.1. These are revisable literature judgments: a missed pre-cutoff result earns no point and triggers a recorded correction. A real run that resolves nothing can receive an official zero after run-integrity review and disposition of all proof candidates. No paid model run or model score was invented for this release.

Some frozen policy and audit fields still say “provisional”: they describe the snapshot reviewed in PR #1 and remain unchanged to preserve its audited identities. The separate, hash-bound [publication record](data/publication.json) records the current publication state without changing the frozen questions, definitions or historical decisions. The tkwa.me frontend is maintained separately.

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

Provider requests include the canonical Lean sources and generated `TrustedBaseline` declarations. Models can return named Lean modules and an entrypoint, with `Submission.result_N` theorems mapped to their claims. Project modules use ordinary imports; a legacy single source body under fixed imports remains supported.

For an ordinary new inclusion or non-inclusion, replace `SOURCE` and `CLAIMS_MAP` below with the sealed paths from the run manifest, resolving relative paths beneath `runs/first`. The adapter saves the mapping as `adapter-artifacts/<provider-uuid>/claims-map.json` inside the attempt directory. It maps claim 1 to `Submission.result_1`, and so on, omitting independence claims from automatic verification:

```sh
python3 -m inclusion_bench verify-proof SOURCE --claims CLAIMS_MAP --report proof-report.json
```

Prepare a Linux verifier using the [setup instructions](docs/PROOF_REVIEW.md); `--local`, `--remote-root`, `--image` and `--toolchain-path` select your installation. The verifier uses a sandbox and a fresh Lean kernel, checking the actual class statement and limiting trusted assumptions to the release's allowed cited premises. A source that assumes its own conclusion is not a verified solution. The natural-language argument and class conventions also receive mathematical review.

Independence uses a separate [expert-review lane](docs/PROOF_REVIEW.md#independence-review). It accepts unconditional metatheorems or ones conditional on Con(ZFC) or arithmetic soundness of ZFC: every first-order arithmetic sentence with a provable ZFC translation is true in standard N. Soundness is a stronger premise than consistency, so it permits a weaker conditional theorem. Both nonderivability polarities must hold for the exact sentence under the recorded premise. The target theory remains ZFC itself; conditions stay visible in review and public results. A full ZFC encoding and its correspondence to the claimed pair remain expert-reviewed, and independence receives no ordinary implication credit.

Fill `run_review` and the relevant `proof_reviews` entry in `review.json` with the decision and evidence. For an accepted ordinary proof, set that entry's `proof_report` to the verifier report path, resolved relative to the review JSON. Record the completed sections directly:

```sh
python3 -m inclusion_bench review-run runs/first/run.json review.json
python3 -m inclusion_bench review-proof runs/first/run.json review.json --attempt-id attempt-0001
```

Repeat proof review for each candidate. This release already records historical decisions for the full suite. If a later version or correction leaves decisions pending, generate a fresh packet:

```sh
python3 -m inclusion_bench review-packet runs/first/run.json --output history-review.json
```

Fill its `history_review` section for each listed pair, then record and evaluate it. Skip `review-history` if the section has no pairs:

```sh
python3 -m inclusion_bench review-history history-review.json
python3 -m inclusion_bench evaluate-run runs/first/run.json
```

No proof or history review is needed for an ordinary unsolved attempt. Every positively scored pair needs an open-at-cutoff decision; the release audit supplies these for the current suite. Known pairs earn zero. Pending proof candidates or required history decisions keep the official score unavailable; unavailable is different from zero. [Full review protocol](docs/EVALUATION.md) · [Verifier setup and proof format](docs/PROOF_REVIEW.md).

Once evaluation reports an official score, register the run for the leaderboard:

```sh
python3 -m inclusion_bench publish-run runs/first/run.json
```

This copies the manifest and only its sealed, indexed evidence to `evaluation/published-runs/<run_id>` and registers it in `data/leaderboard_runs.json`. Rebuild the release to update the site. Committing and pushing the reviewed evidence and generated files to GitHub is a separate publication step.

## What earns a point

The target for `(A, B)` is **A ⊆ B**, inclusion between classes of total binary decision languages. Proving inclusion, proving its negation, or establishing an admissible ZFC-independence metatheorem resolves that ordered pair. Only directions open at the cutoff earn points. A qualifying conditional independence metatheorem already public before the cutoff also earns zero.

Strict inclusion `A ⊊ B` means `A ⊆ B` and `B ⊄ A`. Accepted proofs from one run are pooled before closure, so implications can combine answers to different tasks and resolve questions outside the assigned subset. Results from different runs are never combined into an individual model score.

For example, a proof of `BPP ⊊ NP` would also establish `P ⊊ PSPACE`. Inspect the computed consequences on the frozen snapshot:

```sh
python3 -m inclusion_bench score examples/bpp-strictly-below-np.json
python3 -m inclusion_bench explain separation PSPACE P --assuming examples/bpp-strictly-below-np.json
```

These are scoring examples, not AI achievements. Pre-cutoff public knowledge scores zero by definition and appears separately from the model leaderboard. The suite is public: training exposure and retrieval of later solutions are possible. A valid score measures resolved questions under the declared access conditions; it does not establish independent discovery.

## The 50 scored classes

| Area | Classes |
| --- | --- |
| Circuits and advice | ACC⁰, TC⁰, NC¹, **uniform NC¹**, P/poly, NP/poly |
| Space and parallel computation | L, UL, NL, BPL, PL, BQL, LogCFL, uniform NC, SC, PSPACE, EXPSPACE |
| Time, nondeterminism and real feasibility | P, NP, coNP, NP ∩ coNP, ∃R, NE, EXP, NEXP |
| Randomness and classical proof systems | RP, ZPP, BPP, MA, AM, SBP, SZK |
| Polynomial-time counting | UP, SPP, C₌P, PP, ⊕P, AWPP, P^#P, CH |
| Quantum computation and proof systems | BQP, QCMA, QMA, QMA(2), StoqMA, QSZK |
| Polynomial hierarchy | Θ₂P, Δ₂P, Σ₂P, PH |

These display groups overlap scientifically: BQL is both quantum and space-bounded, PL is a counting class, and unambiguity connects space and counting. They are not separate weighted scores. Selection considers important research questions and model diversity, without predicting which questions an AI will solve first.

The eleven demoted endpoints remain **unscored background classes**: AC⁰, coUP, coMA, coAM, coQMA, FewP, LWPP, WPP, coRP, E and Π₂P. Their definitions, facts and implication rules remain available. A proof about a background pair can score through an eligible consequence on two scored endpoints; that background pair itself earns no point. An independence result earns credit only for its exact scored pair.

The [catalog](data/classes.json) fixes every convention. ACC⁰, TC⁰, NC¹, P/poly and NP/poly are nonuniform; background AC⁰ is too. These classes may contain undecidable languages and must not be silently included in EXP. UniformNC1 uses standard extended-connection uniformity, equivalently ALOGTIME; it is distinct from nonuniform NC¹. PSharpP is the **decision** class P^PP = P^#P, not the function class #P or the search class PPP.

The [original coverage stress test](research/coverage.json) and [twenty examples for the additions](research/v0.4.0/representative-questions.json) document coverage without claiming a forecast distribution. Promise-only, fixed-exponent, search and algebraic advances need not resolve these total-language targets. Exhaustive coverage of every plausible breakthrough is not required.

## Frozen data and Lean

- [`data/classes.json`](data/classes.json): stable IDs, class specifications, uniformity and complement identities.
- [`data/knowledge.json`](data/knowledge.json): cited baseline facts and conditional implications.
- [`data/freeze.json`](data/freeze.json): the release's dataset and taskset hashes.
- [`data/publication.json`](data/publication.json): current publication state bound to the frozen snapshot; historical provisional fields are not rewritten.
- [`evaluation/tasks.json`](evaluation/tasks.json): the fixed public candidate questions.
- [`research/baseline-audit.md`](research/baseline-audit.md): audit findings, coverage, residual-error estimate and versioned corrections.
- [`data/history_reviews.json`](data/history_reviews.json): dated historical decisions for the frozen questions.
- [`research/`](research/): primary-source records, theorem locators and independent review dossiers.
- [`lean/`](lean/) and [`quantum/`](quantum/): all 61 operational definitions and Lean inference/scoring foundations.

The definitions are the benchmark's canonical targets. The core covers 52 classes; the pinned Mathlib extension supplies eight quantum classes and ∃R, and agrees with every core definition. Alternative textbook characterizations, aliases such as IP for PSPACE, and further invariants can be added with documented equivalences. They are useful future work rather than launch requirements.

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

Open `http://localhost:8000`. The standalone site has a model leaderboard, evaluation protocol, pair matrix, proof traces and secondary scoring examples. The public site is [tkwa.me](https://tkwa.me), managed separately; this repository also deploys a [GitHub Pages mirror](https://tkwa.github.io/inclusion-bench/). Copy `web/` into another site or embed that mirror. The standalone site has no analytics, external fonts, model API calls or backend. Provider adapter tests use a local mock server and fake credentials. [Development and embedding](docs/DEVELOPMENT.md).

The chosen name is **InclusionBench**. Alternatives: **ClassFrontier**, **ComplexityFrontier**, **SeparationBench**.

Original code and benchmark text are MIT-licensed. Linked papers retain their authors' copyrights.
