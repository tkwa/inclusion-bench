# Checking submitted proofs

Ordinary inclusion and noninclusion submissions have an executable Lean verifier. It checks closed theorems over all 61 operational class definitions in `InclusionBench.Quantum.completeInterpretation`. A successful report establishes the submitted statement relative to the explicitly trusted literature baseline. Only pairs with two of the 50 scored endpoints earn direct points; background claims can support scored consequences. Benchmark points also require the separate proof, run-integrity, and cutoff-history reviews described in [EVALUATION.md](EVALUATION.md).

Existing published proofs may be trusted under the benchmark's existing-proof waiver. Each cited fact, conditional implication, and complement identity becomes a named axiom generated from the current dataset. Submitted results never become axioms. The generated file exists only in the verifier's temporary job directory; it does not weaken the core library's no-custom-axioms build.

## Submit a proof

Write a UTF-8 Lean file containing declarations under the verifier's fixed imports. This infrastructure example is already known and earns zero points:

```lean
open InclusionBench

theorem submitted :
    Includes (Quantum.completeInterpretation .P)
             (Quantum.completeInterpretation .P) :=
  includes_refl _
```

Specify the exact declaration for each ordinary claim:

```json
[
  {"relation": "inclusion", "left": "P", "right": "P", "theorem": "submitted"}
]
```

Use `separation` for `NonIncludes`. Qualified theorem names such as `MyProof.result` are supported. Targets must be closed and monomorphic: a theorem with an unproved hypothesis does not match an unconditional benchmark claim.

The Python entry point is:

```python
import json
from pathlib import Path
from inclusion_bench.benchmark import Benchmark
from inclusion_bench.proofcheck import verify_proof

runtime = json.loads(Path(".tools/proofcheck-runtime.json").read_text())
report = verify_proof(
    Benchmark(), "proof.lean",
    [{"relation": "inclusion", "left": "P", "right": "P",
      "theorem": "submitted"}],
    report_path="proof-report.json",
    timeout_seconds=180,
    **runtime,
)
```

The setup command below writes this runtime configuration. `host=None` uses Docker on the local Linux machine. To use another Linux host, set `host` to its SSH alias and set `remote_root` and `toolchain_path` to paths on that host. There is no fallback that executes submitted Lean directly on the host.

To inspect the available trusted facts and their exact declaration names, call `trusted_baseline(Benchmark(), claims)`. It returns the generated Lean source, the source-linked axiom manifest, and the expected-target map. `baseline_name("fact:" + fact_id)` gives a stable name. Every axiom has its fact/rule identifier, source identifiers, and source metadata hash in the report. Baseline assumptions are reviewable mathematical inputs; the verifier does not prove their consistency or their agreement with every textbook presentation of the classes.

## What the verifier checks

1. It hashes the proof bytes, dataset, semantic sources, checker sources, and generated baseline. It checks the remote Mathlib lock file and records manifests of the actual Mathlib objects, Lean executable/objects/shared libraries, and Docker image ID. These fingerprints identify the trusted installation; they do not independently attest to its provenance.
2. A trusted build reconstructs the repository's core and quantum libraries from the submitted verifier package's **trusted repository sources**, then compiles the generated baseline and export helper. Candidate source is not executed during this stage.
3. A separate container elaborates the candidate and exports declaration types and proof terms as bounded JSON. Shared names, universe levels, and subexpressions are stored once per declaration and referenced by index. The candidate cannot write host files or change the trusted imports. Its compiled objects are discarded.
4. A fresh container reads only the JSON. The trusted decoder constructs Lean names, universes, expressions, and declarations, then calls the synchronous kernel declaration checker with checking enabled. It imports no candidate module and executes no candidate initializer or native library.
5. For each requested theorem, the kernel checks its use at a server-generated exact target type. Changing notation, reporting a different claim, or printing a successful diagnostic cannot change that target.
6. The verifier collects actual axiom dependencies of every reconstructed declaration. The allowlist contains only `propext`, `Classical.choice`, `Quot.sound`, and the generated cited baseline axioms. `sorryAx`, new axioms, and native-compiler trust axioms are rejected.

This design follows Lean's distinction between elaborating untrusted source and validating its proof objects. Lean's [proof-validation documentation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) explains why an untrusted `.olean` file and an ordinary successful compiler invocation are insufficient. The current checker reuses Lean 4.19's kernel; it is not an independently implemented kernel.

Each container uses one CPU, an 8 GiB memory and swap ceiling, 32 processes, no network, no capabilities, a read-only root filesystem, and bounded temporary storage. Candidate execution has no writable host mount. Output is bounded while the process runs; a timeout or output overflow also removes the container. The timeout applies separately to trusted build, candidate elaboration, and fresh replay. Only one container runs at a time.

## Set up a public Linux verifier

Start with a Linux x86_64 or aarch64 machine with Docker Engine, Python 3.10 or later, Git, and enough disk space for Lean and the requested Mathlib cache. Your user must be able to run Docker. No private repository or private machine is needed:

```sh
git clone https://github.com/tkwa/inclusion-bench.git
cd inclusion-bench
python3 scripts/proofcheck/setup_linux.py \
  --toolchain-path "$HOME/.local/share/inclusion-bench/lean-4.19.0" \
  --image ubuntu:22.04
```

Setup pulls the small public Ubuntu image, downloads the official [Lean 4.19.0 release](https://github.com/leanprover/lean4/releases/tag/v4.19.0) when needed, checks out each dependency at the committed lock's exact revision, and fetches only the four required Mathlib modules and their transitive imports. It preserves the dependency lock and refuses to overwrite a checkout at a different revision. It records the release archive hash and checks the GitHub asset digest when one is provided.

Provisioning runs in a trusted container limited to one CPU and 8 GiB, including cache extraction. This setup container has network access and writable installation directories because its job is to install trusted dependencies. It installs no host packages. Proof-checking containers always disable network access and candidate host writes.

The generated `.tools/proofcheck-runtime.json` contains the exact keyword arguments for `verify_proof`, including the resolved image ID. The toolchain path is optional: setup defaults to `.tools/lean-4.19.0` in the checkout. Existing installations can be reused with `--toolchain-path`; `--skip-pull` reuses an installed image. Check an existing installation without downloading or changing it:

```sh
python3 scripts/proofcheck/setup_linux.py --check-only \
  --toolchain-path "$HOME/.local/share/inclusion-bench/lean-4.19.0"
```

The command-line verifier accepts `--local`, `--image`, `--toolchain-path`, and `--remote-root`. For example, after writing the proof and claims above:

```sh
python3 -m inclusion_bench verify-proof proof.lean --claims claims.json \
  --report proof-report.json --local --image ubuntu:22.04 \
  --toolchain-path "$HOME/.local/share/inclusion-bench/lean-4.19.0" \
  --remote-root "$PWD"
```

Verification requires the chosen image to be installed already; it never pulls an image. Any compatible Linux image with `/bin/sh`, `cat`, and glibc can be supplied by name or digest, and the actual image ID is recorded. The API's original defaults still target Thomas's existing SSH host and cached NVIDIA Ubuntu image. Public users should supply the generated configuration or the explicit options above. A GPU is never used.

## Current proof-format limits

Software v0.4.1 exports proof format version 2. Each declaration has tables of names, universe levels, and expressions, shared by its type and value. Repeated subexpressions use integer references into those tables. References within a table must point backward, so the decoder rejects cycles, forward references, and out-of-range indices. The JSON stays a tree of objects and arrays; the indices preserve sharing when Lean reconstructs the proof. The decoder also accepts legacy version 1 tree exports.

Both formats accept ordinary theorem declarations, safe definitions, and opaque declarations with bodies, using types already present in the trusted imports. Every reconstructed declaration still passes the Lean kernel, exact target check, and axiom allowlist described above. Sharing changes only the serialization and reconstruction of proof objects.

Newly declared inductive types, structures, constructors, recursors, unsafe declarations, and partial definitions remain unsupported. Such a proof requires extending and reviewing the data-only codec before it can be admitted. This limitation is a verifier-format limitation, not evidence that the mathematics is false. Imported trusted libraries remain available through the fixed `ProofExport` and `TrustedBaseline` imports; arbitrary additional imports are outside the submission format.

Proof source is limited to 2 MiB, exported JSON to 32 MiB, and reconstructed declarations to 100,000. Reports have one of three statuses: `verified`, `rejected`, or `unavailable`. Only `verified` is positive proof evidence. A report always contains `official_points: 0`: the verifier itself cannot award points or certify that a statement was open at the cutoff.

The Lean kernel, its runtime, the trusted repository sources, pinned dependency objects, Docker/Linux isolation, and the reviewer's verifier installation form the trust boundary. Do not accept a model-authored report or a report copied without rerunning the verifier. A maintainer binds the resulting report to the exact artifact hash in `data/ai_reviews.json`; run integrity is recorded separately in `data/ai_run_reviews.json`.

## Independence review

ZFC independence has a separate expert-review lane. For the exact encoded inclusion sentence, the metatheorem must establish that ZFC derives neither that sentence nor its negation. The admitted premise is `unconditional`, `zfc_consistency`, or `zfc_arithmetic_soundness`. Arithmetic soundness means that every first-order arithmetic sentence whose ZFC translation is provable is true in the standard natural numbers. It is stronger than consistency, so a theorem conditional on it is weaker than the corresponding consistency-conditional theorem.

Consistency and soundness are external premises of the metatheorem. The target proof relation remains ZFC itself, not ZFC augmented by either premise. The reviewer must check the arithmetic translation and standard interpretation, the actual proof system and ambient metatheory, and reject stronger unapproved assumptions hidden in that metatheory. Both nonderivability polarities must be proved under the recorded premise.

The proof-review record contains an `independence_review` object. The following fragment illustrates its shape; the placeholder text must be replaced by checked evidence and does not constitute acceptance:

```json
{
  "independence_review": {
    "premise": "zfc_arithmetic_soundness",
    "zfc_proof_system": "<Exact ZFC axioms, syntax, inference rules and encoding reference>",
    "metatheory": "<Ambient formal system and its role in the metatheorem>",
    "assumptions": "External premise: arithmetic soundness of ZFC. No additional unproved assumptions.",
    "arithmetic_interpretation": "<Translation of first-order arithmetic into ZFC and truth in standard N>",
    "expert_report": "<Reviewed report and proof-artifact references, with hashes>",
    "claim_certificates": [
      {
        "left": "NP",
        "right": "P",
        "encoded_sentence": "<Exact ZFC sentence encoding NP being contained in P>",
        "unprovability_both_polarities": "<Arguments that ZFC derives neither this sentence nor its negation, under the recorded premise>"
      }
    ]
  }
}
```

The common fields are nonempty strings. `arithmetic_interpretation` is additionally required for `zfc_arithmetic_soundness`. The `claim_certificates` list must contain exactly one entry for each verified independence pair and no entries for other pairs. Each entry has its own nonempty `encoded_sentence` and `unprovability_both_polarities` strings. The surrounding proof review still binds the sealed run, attempt, claims, artifacts, reviewer and decision. A shared freeform sentence cannot certify several distinct ordered pairs. Automatic validation checks this structure and these bindings; expert review establishes the mathematical content and checks for hidden assumptions.

The core `InclusionBench.Independent` interface represents both nonderivability obligations relative to an explicit proof relation. `InclusionBench.AdmittedIndependenceCertificate` restricts the premise category to the three allowed values; it does not certify that the supplied theory and translation represent ZFC. The automated ordinary-proof verifier does not implement a full ZFC encoding and rejects `independence` claims. Expert acceptance must verify the precise ZFC correspondence and metatheorem.

Evaluation provenance retains the selected premise, common review fields and relevant singular `claim_certificate` for each accepted pair. The public leaderboard exposes these records in `independence_results`. Public descriptions must keep the condition visible.

Independence resolves only the certified ordered pair and never supplies an inclusion, separation or Horn-rule premise. A qualifying conditional metatheorem already public before the cutoff earns zero. The existing-proof waiver does not turn an unverified new independence assertion into an axiom.

## Verification tests

Run the local input-validation tests with:

```sh
python -m unittest tests.test_proofcheck -v
```

Run codec round-trip and malformed-reference checks with the pinned Lean 4.19.0 compiler:

```sh
LEAN_BIN=/path/to/lean-4.19.0/bin/lean \
  python3 -m unittest tests.test_proofcodec -v
```

Run the actual isolated positive and adversarial tests using the generated local runtime configuration:

```sh
INCLUSION_PROOFCHECK_INTEGRATION=1 \
  INCLUSION_PROOFCHECK_CONFIG=.tools/proofcheck-runtime.json \
  python -m unittest tests.test_proofcheck.IsolatedProofcheckTests -v
```

The integration suite checks a real reflexivity proof, a cited baseline proof, an incorrect target, `sorry`, a fabricated axiom, a fake successful diagnostic, and a malicious candidate that writes a forged proof export and exits successfully before the exporter runs. The last test exercises the fresh kernel directly. These are infrastructure tests and contribute no benchmark score.
