# Release status and remaining obligations

Version 0.1.0 is a research preview of an **AI evaluation benchmark**. Task export, adapter execution, run manifests, review-aware consequence scoring, and the website work. All 50 operational class definitions compile through the core and optional quantum projects. Official rankings remain disabled: the historical task suite and proof-admission pipeline are not yet certified, and no model evaluation score is implied by the working smoke tests.

| Obligation | Current evidence | Remaining work |
| --- | --- | --- |
| Fixed class roster | 50 identifiers with explicit language and uniformity conventions | Review convention choices; no guarantee of covering every major advance is claimed |
| Historical baseline | Primary-source literature records, locators, elementary derivations and conditional rules | Independent theorem-by-theorem mathematical review and historical-version verification |
| Open-status certification | Complete pair matrix with known versus unreviewed status | Certify every unresolved pair as open or add its known resolution; freeze the manifest |
| Inference scoring | Tested signed closure, contradiction rejection, proof DAGs, deduplication | Extend rules when sound implications are missing |
| AI-run evaluation | Runnable task exporter, adapter protocol, immutable manifests, distinct access tracks, and pooled verified consequences | Complete provider adapters and audit model identity, resource enforcement, transcripts, and full-suite execution |
| Lean scoring foundations | Checked semantic reasoning, proof certificates and finite scoring properties | Connect eligibility and official ingestion to the formal scorer |
| Lean operational semantics | 46 core definitions plus four optional quantum definitions; complete 50-class interpretation and agreement with the core proved | Prove textbook-model equivalences and remaining semantic invariants, including general quantum unitarity and normalization preservation |
| Lean historical results | Generic soundness under explicit hypotheses | Formalize the baseline and each substantive cited conditional theorem |
| ZFC independence | Abstract proof-relation interface, isolated from ordinary inference | Actual ZFC syntax/proof encoding, interpretation of class sentences and metatheory policy |
| Proof and run verification | Separate exact-artifact and exact-run review gates; draft fails closed | End-to-end sandboxed proof checking, semantic/axiom audit, and independent run-integrity review |
| Scope | Documented example advances and explicit exclusions | Optional future promise/search/algebraic/fine-grained tracks; examples are not a coverage guarantee |
| Website | AI leaderboard presentation, scenario explorer, interactive pair matrix | Add only genuine reviewed model runs; keep hypothetical scenarios and smoke fixtures unranked |

Do not remove the draft label or enable official scoring by changing one flag. The missing mathematical artifacts are substantive prerequisites.

The optional quantum project was compiled on the authorized Ubuntu host using Lean and Mathlib v4.19.0 under a one-CPU restriction. Its complete interpretation has no default or opaque substitute for a class. The checked theorems include agreement with the 46 core definitions and coverage of all 50, normalized basis states, injective gate records, and X applied twice. General gate unitarity, arbitrary-circuit normalization, amplification, deep baseline results, and ZFC formalization remain unproved. See [formalization status](formalization.md) and [quantum build details](../quantum/README.md).

For AI rankings, `data/ai_reviews.json` admits exact proof artifacts and claims; `data/ai_run_reviews.json` separately admits the exact run's model identity, access policy, resource use, and integrity. Both gates are required. The AI path does not require a duplicate aggregate record in the legacy `data/reviews.json` submission registry. A standard full-suite run must cover exactly the task set bound to the certified eligibility manifest. Partial runs and `smoke-test` runs remain unranked. See [the evaluation protocol](EVALUATION.md).

Known names that describe the same class should be aliases, not extra scored targets. Examples for later alias support include IP and QIP for PSPACE, and PostBQP for PP. Adding a duplicate class column would inflate scores without adding a research question.

An independent audit should test whether inferred point counts overweight densely represented parts of the class lattice. The one-point-per-pair score is the primary metric requested here; family-normalized or implication-minimal auxiliary metrics could be reported later without silently changing that metric.
