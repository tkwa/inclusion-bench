# InclusionBench v0.4.2

Agents can now express proofs through textbook complexity-theory interfaces and reuse published results without formalizing their original proofs. The release addresses the cost of rebuilding standard mathematics after finding a new argument.

- **Familiar targets and reusable theorems.** All 61 class definitions have short aliases, and the existing benchmark facts and rules have readable `Known.*` names. A searchable catalog gives statements and citations.
- **Textbook proof obligations.** The support library supplies 112 proved interfaces over 19 explicitly cited standard premises. It covers polynomial functions and reductions, complete-problem arguments, P predicates, NP witness relations, coNP universal certificates, GapP arithmetic, counting-class characterizations, and oracle/hierarchy reasoning. Standard model bridges are explicit cited premises; the derived interfaces are kernel-checked.
- **Additional literature dependencies.** A submission can name a published theorem and state its exact Lean type. The verifier checks the new argument conditional on that theorem. A maintainer reviews the source, precise statement, and model alignment; re-proving the cited result is unnecessary. Pending or revoked dependencies cannot support an admitted proof.
- **A smaller submission workflow.** `submission-init` creates exact targets and an editable proof; `theorems` searches the catalog; `check-submission` checks the proof and dependencies; `review-literature` records a maintainer decision. Provider adapters preserve citations and the trusted support snapshot alongside run evidence.
- **Target-only proof export.** Proof format 3 exports the declarations actually needed by the requested targets. It retains shared expression tables and accepts formats 1 and 2. Fresh kernel replay still checks every reconstructed declaration and the exact target.

Literature decisions bind the reconstructed declaration, its local defining context, citations, dataset, generated target baseline, and trusted library/checker versions. Changing only the novel proof body can reuse an approval. Changing what an approved statement means cannot. Decisions are append-only and can be revoked.

This is a software and support-library release over the frozen v0.4.0 benchmark. The 50 scored classes, 61 operational definitions, 1,324 questions, dataset, taskset, historical decisions, and scoring rules are unchanged. No new model score or solution to an open problem is claimed.

The support library is a starting collection, not a complete formalization of complexity theory. New results still require precise arguments. Submissions remain one Lean source body under fixed imports; new submitted inductive types and structures remain unsupported. The source/export size limits remain 2 MiB/32 MiB. See the [agent submission guide](https://github.com/tkwa/inclusion-bench/blob/v0.4.2/docs/AGENT_SUBMISSIONS.md) for examples and the literature review workflow.
