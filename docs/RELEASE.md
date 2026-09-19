# Release 0.2.0

InclusionBench is open for AI model runs. The release freezes the class definitions, cited mathematical baseline, implication rules and candidate questions. Existing cited proofs are trusted premises; formalizing them is not a condition of running the benchmark or admitting a new result.

The official leaderboard is evidence-driven. A real sealed run can receive zero after run-integrity review and disposition of its proof candidates. Every positive point additionally requires an accepted proof and a historical decision that its ordered pair was open at the cutoff. The repository's empty model leaderboard is intentional: infrastructure fixtures and mock provider tests are not AI evaluations, and no paid model run was performed to manufacture a result.

## What is ready

| Component | Operational contract |
| --- | --- |
| Class roster | 50 canonical operational definitions with explicit total-language and uniformity conventions |
| Frozen release | Dataset, taskset and formalization hashes; changed mathematics requires a new release |
| Candidate suite | Every direction unresolved in the frozen baseline is runnable; candidate does not mean historically certified open |
| Mathematical baseline | Cited facts and substantive implication rules are explicit trusted premises |
| Model execution | OpenAI Responses and Anthropic Messages adapters, explicit model IDs, input counting, output caps, cumulative token budgets and wall-time limits |
| Evidence | Isolated attempts, checkpoints, sealed manifests, artifact hashes, provider records, partial answers and usage accounting |
| Proof admission | Exact artifact and statement review; sandboxed Lean checking for new ordinary claims; a separate expert lane for independence |
| Run admission | Model/configuration provenance, declared tools, budgets, transcripts and human-assistance review |
| Historical admission | An evidence-backed open/known decision for every pair that would receive a positive point |
| Scoring | Union of a run's resolved pairs, implications included, contradictions rejected, no duplicate credit |
| Comparisons | Subsets are allowed; ranks compare matching assignment, track and budget cohorts |
| Website | Reviewed model leaderboard, separate historical zero, interactive matrix, citations and hypothetical scoring examples |

## Trust boundary

The release's cited existing mathematics is trusted. The Lean operational definitions are the benchmark targets. The dependency-free core covers 46 classes; the pinned quantum extension supplies the other four and agrees with the core interpretation. Further textbook-equivalence theorems, aliases and mathematical invariants can improve the library without being prerequisites for model runs.

New model assertions receive no trust merely because they are syntactically valid. Ordinary new claims must pass the proof checker and mathematical review; accepted source hashes must identify sealed model artifacts. The verifier's approved cited premises are distinct from arbitrary user-supplied axioms. An inference trace that assumes the submitted statement does not prove it.

An independence result requires an expert report about both unprovability directions, its exact sentence, proof system, metatheory and assumptions. The ordinary checker does not claim to formalize all of ZFC. This separate lane does not delay evaluation of ordinary inclusions and separations.

## Historical corrections and versioning

A frozen candidate suite can contain omissions from the literature database. Review each positively resolved direction at the release cutoff. If it was already known, it earns no point. Record that decision and any versioned rescore. Do not silently alter an in-progress run's questions or implication rules.

Changes to the roster, definitions, baseline or inference rules require a new version and `freeze`. Review registries retain the frozen dataset hashes and their own recorded revisions. Published results must identify the snapshot and review state used for scoring.

## Further work

These improvements can proceed alongside real evaluations:

- More historical research, additional cited implications and independent audit of the baseline.
- Formal proofs of existing literature results and equivalences with alternative class definitions.
- Aliases for equivalent names, such as IP and QIP for PSPACE, without adding duplicate scored columns.
- Broader promise, search, algebraic or fixed-exponent tracks, each with its own explicit targets.
- A fuller formal treatment of ZFC independence and automated metatheorem checking.
- Additional provider and agent configurations, with declared tools and comparable resource budgets.
- Auxiliary family-level analyses of the score's sensitivity to the chosen roster.

The primary metric remains one point per eligible ordered pair. Improvements must not silently change that metric or turn a hypothetical scenario into a measured model result. See the [evaluation protocol](EVALUATION.md), [provider adapters](../evaluation/adapters/README.md), and [formalization notes](formalization.md).
