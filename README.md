# InclusionBench

**An AI mathematics benchmark built from open questions in complexity theory.**

Give an AI the frozen task suite, a fixed configuration and a recorded budget. For each ordered pair of complexity classes, ask it to prove inclusion, prove non-inclusion, or prove independence from ZFC. Verify its proof artifacts, then award one point for each eligible question its answers resolve. Proven consequences count; duplicate resolutions count once within the run.

The leaderboard entry is a **model run**. A breakthrough with broad consequences can earn many points because that run has solved many benchmark questions.

[Leaderboard and task explorer](https://tkwa.github.io/inclusion-bench/) · [Evaluation protocol](docs/EVALUATION.md) · [Scoring specification](docs/SPEC.md) · [Formalization status](docs/formalization.md)

**This is a research preview. Official evaluation is not open yet.** The repository supplies 50 class definitions, 1,387 provisional tasks, a cited baseline, an AI adapter harness, a tested consequence scorer, compiled Lean foundations and a website. Certifying the September 1, 2026 open-problem set, proving the remaining semantic and literature obligations, and completing proof admission remain substantive work. Unknown to this dataset does not mean certified open. No evaluated AI runs or invented model scores appear on the leaderboard.

## Run an evaluation

Python 3.11 or later; no Python runtime dependencies. From the repository root:

```sh
python3 -m inclusion_bench validate
python3 -m inclusion_bench tasks --output evaluation/tasks.json
python3 -m inclusion_bench run-adapter \
  --model 'Infrastructure fixture' --model-version 'not-an-AI' \
  --task inclusion.NP.P --wall-seconds 60 --track smoke-test \
  --output /tmp/inclusion-fixture \
  -- python3 "$PWD/evaluation/unsolved_adapter.py"
python3 -m inclusion_bench evaluate-run /tmp/inclusion-fixture/run.json
```

The included adapter always returns `unsolved`. It tests the infrastructure and is never a model result. The output directory must be new. Replace the command after `--` with a trusted model adapter; use `--all-tasks` for the full suite. Each invocation receives a JSON task, the class catalog and the known implication rules on standard input. It returns `unsolved` or a `proof_candidate` with exact claims and relative proof-artifact paths. [Adapter schema](schemas/adapter-response.schema.json) · [Run schema](schemas/ai-run.schema.json) · [Prompt template](evaluation/prompt-template.md).

The Linux/macOS harness enforces a shared wall-time deadline and records prompts, responses, evidence hashes and run identity. CPU, memory, model-token and tool-access enforcement belong to the adapter's execution environment and must be independently recorded and reviewed. Tool-assisted and closed-book runs are separate tracks; partial runs are not ranked as full-suite runs.

A model's `accepted: true` field earns nothing. Only exact proof artifacts admitted through the maintainer review registry contribute to provisional verified points. Official scores additionally require a certified dataset and a review of the run's provenance, configuration and budget. The draft returns an unavailable official score, distinct from a verified zero.

## What earns a point

The target for `(A, B)` is **A ⊆ B**, ordinary inclusion between classes of total binary decision languages. Only pairs certified open at the cutoff are eligible. A proof of its negation or an admissible ZFC-independence metatheorem also resolves the target.

Strict inclusion `A ⊊ B` means `A ⊆ B` and `B ⊄ A`. Known directions earn nothing. Accepted proofs from one run are pooled before closure, so implications can combine answers to different tasks. Results from different runs are never combined into a fictional model score.

For example, a proof of `BPP ⊊ NP` would also establish `P ⊊ PSPACE`. On the provisional dataset its closure resolves 196 previously unresolved ordered pairs. This is a scoring example, not an AI achievement. Inspect it with:

```sh
python3 -m inclusion_bench score examples/bpp-strictly-below-np.json
python3 -m inclusion_bench explain separation PSPACE P \
  --assuming examples/bpp-strictly-below-np.json
```

Pre-cutoff knowledge scores zero by definition. The historical zero appears separately from the model leaderboard; it makes no claim about developments after the cutoff. The questions and rules are public, so this is a white-box benchmark with possible training contamination, unlike a hidden test set. New answers still need valid proofs.

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

The [catalog](data/classes.json) fixes every convention. Nonuniform classes can contain undecidable languages and must not be silently included in EXP. Promise-only, fixed-exponent, search or algebraic advances need not resolve these total-language targets. The [coverage stress test](research/coverage.json) maps 36 of 50 illustrative advances; broad coverage is the aim, not exhaustive coverage of a speculative top 50.

## Data and Lean

- [`data/classes.json`](data/classes.json): stable IDs, mathematical specifications, uniformity and complement identities.
- [`data/knowledge.json`](data/knowledge.json): 133 cited seeds and 138 conditional rules from 40 source records.
- [`data/eligibility.json`](data/eligibility.json): all 2,500 pairs, with 708 inclusions, 405 non-inclusions and 1,387 unreviewed entries after closure.
- [`evaluation/tasks.json`](evaluation/tasks.json): prompts bound to the dataset and formalization bundle by a taskset hash.
- [`research/`](research/): primary-source literature records, locators, derivations and audit gaps.
- [`lean/`](lean/) and [`quantum/`](quantum/): concrete operational definitions for all 50 classes, with compiled closure, certificate and scoring theorems. Textbook-equivalence proofs and most deep baseline theorems remain unfinished.

The dependency-free Lean core covers 46 classes. The pinned Mathlib extension supplies the four quantum classes and a complete interpretation agreeing with the core. Both builds passed with one compiler worker. The axiom audits contain only standard Lean foundations; no project-specific axioms or `sorry` proofs are used.

The scorer can export a consequence's actual inference trace to Lean. Cited baseline results, submitted claims and substantive conditional rules appear as explicit hypotheses. Lean checks the deduction from them; it does not turn an unverified claim into a proof. ZFC independence has an abstract interface, while an actual ZFC encoding remains unfinished.

## Website and development

```sh
python3 scripts/build_release.py
python3 -m unittest discover -s tests -v
python3 scripts/check_generated.py
python3 scripts/check_lean.py
python3 -m http.server 8000 --directory web
```

Open `http://localhost:8000`. The static site has a model leaderboard, evaluation protocol, pair matrix, proof traces and secondary scoring examples. Copy `web/` into your website or embed the [deployed page](https://tkwa.github.io/inclusion-bench/). It has no analytics, external fonts, model API calls or backend. [Development and embedding](docs/DEVELOPMENT.md) · [Release obligations](docs/RELEASE.md).

The chosen name is **InclusionBench**. Alternatives: **ClassFrontier**, **ComplexityFrontier**, **SeparationBench**.

Original code and benchmark text are MIT-licensed. Linked papers retain their authors' copyrights.
