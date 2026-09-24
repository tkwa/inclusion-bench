# InclusionBench v0.4.3

Agents can submit ordinary multi-file Lean projects and use uniform integer-array interfaces with explicit complexity and size guarantees.

- **Multi-file proofs.** A small `submission.json` names the entry module and source files. Normal imports connect helper modules; installed pinned Lean and Mathlib libraries are available. The verifier builds the module graph in its isolated container and exports all declarations needed by the target proofs. Legacy `proof.lean` bodies remain supported.
- **Complete submission evidence.** Provider adapters retain the module tree, claim mapping, and literature requests. The runner seals every file. Proof review and scoring bind the report to the exact manifest and sources under one project directory, so a checked entrypoint cannot stand in for unchecked helpers.
- **Uniform signed-integer arrays.** The support library supplies binary encodings, explicit length and bit-size bounds, bounded tabulation, indexed reads and updates, maps, arithmetic, sums, dot products, and rectangular matrices. The same algorithm must work across all inputs. Generic operations need a uniform bit-time computation guarantee.
- **Separate contracts for large implicit arrays.** Efficient indexed access is distinguished from constructing an entire array. Materialization requires an additional polynomial bound on the number of entries; efficient access alone does not justify fast whole-array sums or dot products.
- **Setup and examples.** The starter project, submission guide, theorem catalog, and packaged two-file example support the new workflow. The Linux setup command can provision additional modules from the pinned Mathlib cache with `--mathlib-module`.

The support catalog now contains 189 kernel-proved helpers and 31 explicitly cited premises. This release adds 77 helpers and 12 premises for standard binary arithmetic and array computation; the succinct-array layer adds no new premises.

Projects allow up to 128 Lean files and 16 MiB including the manifest; the manifest is capped at 64 KiB. Legacy source bodies keep their 2 MiB limit. The original tagged release caps exported proof JSON at 32 MiB; the build 1 follow-up below raises that limit. The isolated time and memory limits still apply. Candidate object files never enter fresh kernel replay. Newly submitted inductive types and structures remain outside the codec; imported library types are supported.

This release preserves the frozen v0.4.0 benchmark definitions, dataset, questions, historical judgments, and scoring rules. No new mathematical result or model score is claimed. See the [submission guide](https://github.com/tkwa/inclusion-bench/blob/v0.4.3/docs/AGENT_SUBMISSIONS.md) for project and array examples.

## Follow-up: 256 MiB proof exports

Build 1 keeps software version 0.4.3 and raises the proof-export cap from 32 MiB to 256 MiB (268,435,456 serialized UTF-8 bytes). The auditor now parses proof exports inside its isolated container. Each isolated stage retains its 8 GiB memory limit, and audit reports have a separate 32 MiB cap. Source limits, declaration limits, proof checks, and the frozen benchmark are unchanged.

The `v0.4.3` tag and original wheel remain pinned to the initial release. The current follow-up wheel is `inclusion_bench-0.4.3-1-py3-none-any.whl`; the added build number distinguishes its bytes while preserving package version 0.4.3. The published release notes identify the follow-up's exact source commit, wheel SHA-256, and download. Use that build or its pinned source revision for the larger export limit.
