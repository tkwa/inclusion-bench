# InclusionBench

**One point for resolving one open complexity-class inclusion. Consequences count.**

InclusionBench turns a complexity breakthrough into a set of resolved ordered pairs. A proof that `NP ⊄ BPP`, for example, also establishes `PSPACE ⊄ P`. The scorer follows those implications and counts each eligible pair once.

**This is a working research preview, not a certified competition release.** It has 50 classes, a cited knowledge base, a tested scorer, a Lean proof library and an interactive leaderboard. The September 1, 2026 open-problem audit and the full operational Lean formalization are unfinished. Official scoring therefore refuses submissions. Scenario scores assume their claims and show provisional impact; they never award public points.

[Explore the leaderboard](https://tkwa.github.io/inclusion-bench/) · [Scoring specification](docs/SPEC.md) · [Formalization status](docs/formalization.md) · [Coverage audit](research/coverage-notes.md)

## Try it

Python 3.11 or later; the scorer has no runtime dependencies. Run from the repository root:

```sh
python3 -m inclusion_bench.cli validate
python3 -m inclusion_bench.cli score examples/bpp-strictly-below-np.json
python3 -m inclusion_bench.cli explain separation PSPACE P \
  --assuming examples/bpp-strictly-below-np.json
python3 -m unittest discover -s tests -v
```

The score response contains every resolved pair and its derivation, including the source IDs and submitted premises. A contradictory claim, unknown class, or attempt to turn an independence result into a normal negative edge is rejected. `--official` fails closed in this release.

To view the website locally:

```sh
python3 -m http.server 8000 --directory web
```

Open `http://localhost:8000`. The entire site is static. Copy `web/` to an existing website or embed its deployed URL in an iframe. It makes no requests to analytics, fonts, model APIs, or a backend.

## What earns a point

The target for ordered pair `(A, B)` is **A ⊆ B**, where both are classes of total binary decision languages. Resolving it means proving the inclusion, proving its negation, or proving independence from ZFC in an explicitly specified metatheory. Only pairs certified open at the cutoff are eligible.

Strict inclusion `A ⊊ B` consists of two claims: `A ⊆ B` and `B ⊄ A`. Known directions earn nothing. Proven consequences may resolve many other eligible pairs; duplicate proofs do not multiply credit.

Pre-cutoff results score zero by definition. The baseline's zero is a reference row, not evidence that no public research has advanced since the cutoff. No model runs or accepted post-cutoff results have been entered in this preview.

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

The exact conventions are in [the catalog](data/classes.json). Nonuniform classes can contain undecidable languages, so they must not be silently included in EXP. Quantum and interactive classes here contain **total languages**; a promise-only separation need not resolve a target.

This roster covers many central structural questions. It cannot guarantee coverage of the “50 most likely advances”: that population has no established ranking, and important advances concern fixed exponents, individual problems, search, promise problems, or arithmetic circuits. The [50-scenario stress test](research/coverage.json) records 36 mappings and 14 uncovered cases instead of claiming complete coverage.

## Data and verification

- [`data/classes.json`](data/classes.json): stable IDs, mathematical specifications, uniformity and complement identities.
- [`data/knowledge.json`](data/knowledge.json): cited inclusion/separation seeds and conditional Horn rules.
- [`data/eligibility.json`](data/eligibility.json): all 2,500 ordered pairs; unresolved entries are explicitly **unreviewed**, not automatically open.
- [`data/policy.json`](data/policy.json): cutoff, credit and admission policy.
- [`research/`](research/): literature records, locators, derivations and audit gaps.
- [`lean/`](lean/): compiled semantic and scoring theorems, machine/circuit foundations and a partial class interpretation. Citations are not disguised as proved theorems.

Regenerate derived data with `python3 scripts/build_release.py`. CI checks the Python tests, reproducible data and Lean library using one worker for each build. [Development instructions](docs/DEVELOPMENT.md) explain proof export and website deployment.

The Python closure can export a target's actual inference trace to a Lean theorem. Baseline results, submitted claims, cited conditional rules and complement identities appear as explicit hypotheses; transitivity, separation propagation and contraposition are then checked by Lean. This verifies the inference **conditional on those hypotheses**. It does not verify a claimed solution to P versus NP.

## Before official scoring opens

[The release checklist](docs/RELEASE.md) tracks the remaining work: complete semantic definitions, prove or independently review the historical results, certify every pair's cutoff status, implement actual ZFC syntax and proof semantics, and admit proof artifacts through review. The current implementation does not substitute a hash or an `accepted: true` field for mathematical verification.

The chosen name is **InclusionBench**. Other names considered: ClassFrontier, ComplexityAtlas and SeparationBench.

Original code and benchmark text are MIT-licensed. Linked papers retain their authors' copyrights.
