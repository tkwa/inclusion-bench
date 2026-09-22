# InclusionBench v0.4.1

Proof exports now preserve shared subexpressions instead of duplicating them in nested JSON trees. Format version 2 stores names, universe levels, and expressions in indexed tables shared by each declaration's type and value. Repeated references reuse the reconstructed Lean object. This reduces export size for proofs with repeated terms and avoids exponential expansion caused by nested sharing.

A synthetic sharing regression shrank from 7,340,123 bytes to 358 bytes. An 80-level doubling expression uses 81 nodes and 1,102 bytes; these are codec fixtures, not measurements of typical proof files.

The decoder accepts legacy version 1 exports. Version 2 rejects malformed, forward, cyclic, and out-of-range references. Reconstructed declarations still undergo the same fresh Lean kernel checks, exact theorem-target checks, and axiom allowlist checks. The accepted declaration kinds and proof-size limits are unchanged.

This is a software patch to the frozen v0.4.0 benchmark. The 50 scored classes, 61 class definitions, 1,324 questions, scoring rules, historical decisions, dataset hash, taskset hash, and publication record are unchanged. Software packages and the Git tag use v0.4.1; benchmark metadata continues to identify v0.4.0. Proof-verifier reports record the new checker hash.

See the [proof-format documentation](https://github.com/tkwa/inclusion-bench/blob/v0.4.1/docs/PROOF_REVIEW.md#current-proof-format-limits) for compatibility and limits, and the [v0.4.0 release notes](https://github.com/tkwa/inclusion-bench/blob/v0.4.0/docs/RELEASE.md) for the benchmark snapshot.
