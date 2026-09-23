"""Prepare exact proof targets and inspect an editable submission project."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .benchmark import read_json
from .engine import Atom, InvalidEvidence
from .proofcheck import proposition, validate_claims, verify_proof


RUNTIME_FIELDS = {"host", "remote_root", "toolchain_path", "image", "timeout_seconds"}


def init_submission(benchmark, directory, claims):
    """Create a small proof workspace without replacing any existing file."""
    if not isinstance(claims, list) or not claims:
        raise InvalidEvidence("Choose at least one claim: --claim inclusion NP P")
    mapped = validate_claims(benchmark, [
        {**Atom.read(claim).json(), "theorem": f"Submission.result_{i}"}
        for i, claim in enumerate(claims, 1)
    ])
    directory = Path(directory)
    filenames = ("proof.lean", "claims.json", "literature.json", "AGENTS.md")
    if directory.exists() and not directory.is_dir():
        raise InvalidEvidence("Submission destination must be a directory")
    existing = [name for name in filenames if (directory / name).exists() or (directory / name).is_symlink()]
    if existing:
        raise InvalidEvidence("Submission files already exist; preserving them: " + ", ".join(existing))
    proof = ["-- The verifier supplies the trusted imports.", "open InclusionBench InclusionBench.Support", "open InclusionBench.Support.Classes", "", "namespace Submission", ""]
    for i, claim in enumerate(mapped, 1):
        proof += [f"-- {claim['relation']}: {claim['left']} to {claim['right']}",
                  f"theorem result_{i} : {'Includes' if claim['relation'] == 'inclusion' else 'NonIncludes'} {claim['left']} {claim['right']} := by",
                  "  sorry", ""]
    proof += ["end Submission", ""]
    guide = """# Working on this submission

Edit `proof.lean`. Its theorem statements and `claims.json` already describe the
exact benchmark targets. Replace each `sorry` with a proof; a placeholder cannot
pass verification. Keep the generated theorem names, or update `claims.json` if
you rename them. The verifier supplies imports, so this file is a Lean body.

Use existing textbook and paper results. You do not need to formalize their
original proofs. Search the available declarations with:

```sh
python3 -m inclusion_bench theorems --search "your topic"
python3 -m inclusion_bench theorems --search "your topic" --json
```

Formalize your new argument. If it needs a published result that is missing from
the catalog, declare `axiom Literature.my_dependency : TYPE` in `proof.lean`,
before `namespace Submission`, replacing `TYPE` with its exact Lean proposition.
Use that declaration in your proof and add its citation to `literature.json`:

```json
{
  "requests": [{
    "name": "Literature.my_dependency",
    "statement": "The exact proposition, explained for the reviewer",
    "sources": [{
      "title": "Actual paper or textbook title",
      "url": "https://...",
      "locator": "Theorem number and page",
      "publication_date": "YYYY-MM-DD"
    }],
    "rationale": "Why this result applies to these exact class definitions and conventions"
  }]
}
```

Replace all placeholders with the real source information. The result must have
been public before the benchmark cutoff. A maintainer checks the actual Lean
declaration, cited statement, and agreement with the benchmark's models. You do
not have to formalize the cited proof. A new conjecture or the submission's target
cannot be admitted as an existing theorem. The JSON description does not replace
the declared Lean type.

Check from the benchmark checkout, replacing `PATH` with this directory:

```sh
python3 -m inclusion_bench check-submission PATH --runtime /path/to/proofcheck-runtime.json
```

You can instead save the runtime configuration at
`PATH/.tools/proofcheck-runtime.json`. Without a runtime configuration, checking
uses Docker on this computer with the installed `ubuntu:22.04` image and this
benchmark checkout. It does not select a private SSH host or install software.
The report is saved to `PATH/proof-report.json`.

`needs_literature_review` means the missing dependency needs maintainer review.
The report's `literature_dependencies` identifies the actual checked declarations.
After checking a dependency's exact type, citation, and model alignment, a
maintainer copies its full report entry into a review's `dependency` field and
records the review with:

```sh
python3 -m inclusion_bench review-literature REVIEW.json
```

The review includes `schema_version: 1`, `reviewer`, `status`, `rationale`, and
`checks` for `published_before_cutoff`, `exact_statement`, `model_alignment`, and
`no_new_result_assumed`. All checks must be true for acceptance. Rerun the proof
check after approval. `verified` means the proof passed verification;
run-integrity and historical review still determine benchmark admission and points.
"""
    contents = {
        "proof.lean": "\n".join(proof),
        "claims.json": json.dumps({"claims": mapped}, indent=2) + "\n",
        "literature.json": json.dumps({"requests": []}, indent=2) + "\n",
        "AGENTS.md": guide,
    }
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in contents.items():
        with (directory / name).open("x", encoding="utf-8") as stream:
            stream.write(content)
    return {"directory": str(directory), "written": list(contents),
            "claims": mapped, "dataset_sha256": benchmark.digest}


def _theorem_catalog(benchmark):
    from .literature import theorem_catalog
    return theorem_catalog(benchmark)


def find_theorems(benchmark, search=None):
    """Search names, propositions, and citation metadata without altering them."""
    entries = _theorem_catalog(benchmark)
    terms = (search or "").casefold().split()
    def matches(entry):
        content = json.dumps(entry, ensure_ascii=False, sort_keys=True).casefold()
        # Short class names such as P, NP and RP must not match "input" or
        # "sharpP". Underscores still separate useful theorem-name words.
        return all((re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", content)
                    if len(term) <= 3 else term in content) for term in terms)
    return [entry for entry in entries if matches(entry)]


def format_theorems(entries):
    if not entries:
        return "No matching trusted theorems. Request a cited dependency in literature.json."
    rows = []
    for entry in entries:
        rows.append(f"{entry['name']} : {entry['statement']}")
        sources = entry.get("sources") or entry.get("source_ids")
        if sources:
            rows.append("  Sources: " + json.dumps(sources, ensure_ascii=False))
    return "\n".join(rows)


def submission_runtime(benchmark, directory, runtime_path=None, overrides=None):
    """Use explicit configuration or local Docker, never a personal SSH default."""
    runtime = {"host": None, "remote_root": str(benchmark.root.resolve()),
               "image": "ubuntu:22.04", "timeout_seconds": 120}
    config_path = Path(runtime_path) if runtime_path is not None else Path(directory) / ".tools/proofcheck-runtime.json"
    if runtime_path is not None or config_path.exists():
        config = read_json(config_path)
        if not isinstance(config, dict) or set(config) - RUNTIME_FIELDS:
            raise InvalidEvidence("Runtime configuration must contain only " + ", ".join(sorted(RUNTIME_FIELDS)))
        runtime.update(config)
    if overrides:
        if set(overrides) - RUNTIME_FIELDS:
            raise InvalidEvidence("Unknown proof-checker runtime option")
        runtime.update(overrides)
    if runtime["host"] is not None and (not isinstance(runtime["host"], str) or not runtime["host"].strip()):
        raise InvalidEvidence("Runtime host must be a nonempty SSH host or null for local Docker")
    if not isinstance(runtime["remote_root"], str) or not runtime["remote_root"].strip():
        raise InvalidEvidence("Runtime remote_root must identify the verifier checkout")
    return runtime


def check_submission(benchmark, directory, *, runtime_path=None, report_path=None, runtime_overrides=None):
    directory = Path(directory)
    claim_document = read_json(directory / "claims.json")
    claims = claim_document.get("claims") if isinstance(claim_document, dict) else claim_document
    claims = validate_claims(benchmark, claims)
    literature_path = directory / "literature.json"
    literature = read_json(literature_path) if literature_path.exists() else {"requests": []}
    if not isinstance(literature, dict) or not isinstance(literature.get("requests"), list):
        raise InvalidEvidence("literature.json must contain a requests array")
    runtime = submission_runtime(benchmark, directory, runtime_path, runtime_overrides)
    report = Path(report_path) if report_path is not None else directory / "proof-report.json"
    return verify_proof(benchmark, directory / "proof.lean", claims,
                        literature_requests=literature["requests"], report_path=report, **runtime)
