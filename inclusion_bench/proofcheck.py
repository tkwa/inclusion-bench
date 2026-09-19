"""Isolated Lean elaboration followed by data-only, fresh kernel replay.

The report is verifier evidence, not a benchmark admission or history review.
"""
from __future__ import annotations

import hashlib
import json
import re
import shlex
import subprocess
from pathlib import Path

from .benchmark import canonical_hash
from .engine import Atom, InvalidEvidence

STANDARD_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
MAX_SOURCE_BYTES = 2 * 1024 * 1024


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def baseline_name(identifier: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_]", "_", identifier)
    return "InclusionBench.TrustedBaseline.b_" + stem + "_" + sha256(identifier.encode())[:12]


def proposition(atom: Atom) -> str:
    if atom.relation == "independence":
        raise InvalidEvidence("Independence uses the expert metatheorem review lane")
    relation = "Includes" if atom.relation == "inclusion" else "NonIncludes"
    return f"{relation} (Quantum.completeInterpretation .{atom.left}) (Quantum.completeInterpretation .{atom.right})"


def validate_claims(benchmark, claims: list[dict]) -> list[dict]:
    if not isinstance(claims, list) or not 1 <= len(claims) <= 2500:
        raise InvalidEvidence("Provide between 1 and 2,500 ordinary claims")
    result = []
    seen = set()
    for raw in claims:
        atom = Atom.read(raw)
        benchmark.baseline.validate_atom(atom)
        proposition(atom)
        name = raw.get("theorem", "")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*", name):
            raise InvalidEvidence("Every claim needs a qualified ASCII theorem name")
        if atom.key in seen:
            raise InvalidEvidence("Duplicate proof claim")
        seen.add(atom.key)
        result.append({**atom.json(), "theorem": name})
    return result


def trusted_baseline(benchmark, claims: list[dict]) -> tuple[str, list[dict], list[dict]]:
    """Generate *only* cited existing facts/rules and class complement identities.

    This is the intentional trust boundary authorized by the existing-proof
    waiver. Nothing from the submitted source becomes a baseline assumption.
    """
    lines = ["import InclusionQuantum", "", "namespace InclusionBench", "",
             f"-- Dataset SHA-256: {benchmark.digest}",
             "-- Existing literature is explicitly trusted; submitted results are not."]
    entries = []

    def add(identifier, statement, sources):
        name = baseline_name(identifier)
        lines.append(f"axiom {name.removeprefix('InclusionBench.')} : {statement}")
        entries.append({"name": name, "id": identifier, "statement": statement,
                        "source_ids": list(sources),
                        "sources_sha256": canonical_hash([benchmark.sources[s] for s in sources])})

    for raw in benchmark.knowledge["facts"]:
        add("fact:" + raw["id"], proposition(Atom.read(raw)), raw["source_ids"])
    for rule in benchmark.rules:
        chain = " → ".join("(" + proposition(a) + ")" for a in (*rule.premises, rule.conclusion))
        add("rule:" + rule.id, chain, rule.source_ids)
    for item in benchmark.catalog["complements"]:
        a, b = item["left"], item["right"]
        add(f"complement:{a}:{b}",
            f"Quantum.completeInterpretation .{b} = coClass (Quantum.completeInterpretation .{a})",
            item["source_ids"])
    allowed = STANDARD_AXIOMS + [e["name"] for e in entries]
    lines += ["", "def TrustedBaseline.allowedAxiomNames : List String := [",
              ",\n".join("  " + json.dumps(name) for name in allowed), "]"]
    targets = []
    for i, raw in enumerate(claims):
        expected = f"InclusionBench.TrustedBaseline.expected_{i}"
        lines.append(f"def TrustedBaseline.expected_{i} : Prop := {proposition(Atom.read(raw))}")
        targets.append({"theorem": raw["theorem"], "expected": expected})
    lines += ["", "end InclusionBench", ""]
    return "\n".join(lines), entries, targets


def verify_proof(benchmark, proof_path, claims, *, report_path=None,
                 host="tkwa-ubuntu-box-wan",
                 remote_root="/home/tkwa/code/inclusion-quantum-build",
                 timeout_seconds=120,
                 image="nvidia/cuda:12.4.1-devel-ubuntu22.04",
                 toolchain_path=None) -> dict:
    """Return verified/rejected/unavailable; never award benchmark points.

    `host=None` runs the same Docker driver on the local Linux host. The source
    is a Lean body under fixed trusted imports; arbitrary new imports are not
    part of the v1 format. The submitted file's exact bytes are hash-bound.
    """
    claims = validate_claims(benchmark, claims)
    if not isinstance(image, str) or not image.strip() or image.startswith("-"):
        raise InvalidEvidence("Provide an installed Docker image name or digest")
    if not isinstance(timeout_seconds, int) or not 5 <= timeout_seconds <= 3600:
        raise InvalidEvidence("Proof timeout must be between 5 and 3,600 seconds")
    path = Path(proof_path)
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise InvalidEvidence("Proof source exceeds the 2 MiB limit")
    with path.open("rb") as handle:
        source = handle.read(MAX_SOURCE_BYTES + 1)
    if len(source) > MAX_SOURCE_BYTES:
        raise InvalidEvidence("Proof source exceeds the 2 MiB limit")
    try:
        body = source.decode("utf-8")
    except UnicodeError as error:
        raise InvalidEvidence("Proof source must be UTF-8") from error
    baseline, entries, targets = trusted_baseline(benchmark, claims)
    support = benchmark.root / "scripts" / "proofcheck"
    files = {p.name: p.read_text() for p in support.glob("*.lean")}
    files["TrustedBaseline.lean"] = baseline
    # These comments are not security checks. The kernel replays the exported
    # declarations in a clean environment, with no candidate module imported.
    files["Candidate.lean"] = "import ProofExport\nimport TrustedBaseline\n\n" + body + "\n\n#proofcheck_export\n"
    files["targets.json"] = json.dumps(targets)
    trusted_hashes = {}
    semantic_sources = {}
    for subdir in ("lean", "quantum"):
        for p in sorted((benchmark.root / subdir).rglob("*.lean")):
            if ".lake" not in p.parts:
                trusted_hashes[str(p.relative_to(benchmark.root))] = sha256(p.read_bytes())
                semantic_sources[str(p.relative_to(benchmark.root))] = p.read_text()
    lock = benchmark.root / "quantum" / "lake-manifest.json"
    trusted_hashes[str(lock.relative_to(benchmark.root))] = sha256(lock.read_bytes())
    packet = {"files": files, "trusted_hashes": trusted_hashes, "semantic_sources": semantic_sources,
              "remote_root": str(remote_root), "timeout_seconds": timeout_seconds,
              "image": image, "toolchain_path": str(toolchain_path) if toolchain_path is not None else None}
    runner = (support / "remote_runner.py").read_text()
    command = (["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host,
                "python3 -c " + shlex.quote(runner)] if host else ["python3", "-c", runner])
    report = {"schema_version": 1, "dataset_sha256": benchmark.digest,
              "proof_sha256": sha256(source), "claims": claims,
              "baseline_sha256": sha256(baseline.encode()), "baseline_axioms": entries,
              "checker_sha256": canonical_hash({**{k: v for k, v in files.items()
                    if k not in {"Candidate.lean", "TrustedBaseline.lean", "targets.json"}},
                    "remote_runner.py": runner, "proofcheck.py": Path(__file__).read_text()}),
              "semantics_sha256": canonical_hash(trusted_hashes),
              "method": "lean4-data-only-fresh-kernel-replay", "official_points": 0}
    try:
        # Only the trusted remote runner writes this pipe; candidate stdout is
        # captured and size-limited inside its Docker container.
        completed = subprocess.run(command, input=json.dumps(packet), text=True,
                                   capture_output=True, timeout=3 * timeout_seconds + 120)
        response = json.loads(completed.stdout)
        if response.get("status") not in {"verified", "rejected", "unavailable"}:
            raise ValueError("Invalid verifier response")
        report.update(response)
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        report.update(status="unavailable", reason=f"Verifier did not return valid evidence: {error}")
    if report_path is not None:
        Path(report_path).write_text(json.dumps(report, indent=2) + "\n")
    return report
