"""Isolated Lean elaboration followed by data-only, fresh kernel replay.

The report is verifier evidence, not a benchmark admission or history review.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import selectors
import shlex
import subprocess
import tempfile
import time
from pathlib import Path

from .benchmark import canonical_hash
from .engine import Atom, InvalidEvidence
from .proofbundle import MAX_SOURCE_BYTES, load_proof_bundle

STANDARD_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
MAX_VERIFIER_RESPONSE_BYTES = 40 * 1024 * 1024
MAX_VERIFIER_DIAGNOSTIC_BYTES = 1024 * 1024
VERIFIER_SHUTDOWN_GRACE_SECONDS = 25


def _run_verifier(command, *, input: str, timeout: float):
    """Bound the trusted driver response before parsing it on the caller.

    A file-backed request avoids blocking pipe writes while the driver emits
    diagnostics. Neither a noisy SSH connection nor a large citation report
    can cause unbounded output buffering here.
    """
    with tempfile.TemporaryFile() as request:
        request.write(input.encode("utf-8"))
        request.seek(0)
        with subprocess.Popen(command, stdin=request, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as process:
            deadline = time.monotonic() + timeout
            chunks = {process.stdout: bytearray(), process.stderr: bytearray()}
            limits = {process.stdout: MAX_VERIFIER_RESPONSE_BYTES,
                      process.stderr: MAX_VERIFIER_DIAGNOSTIC_BYTES}
            with selectors.DefaultSelector() as selector:
                for pipe in chunks:
                    os.set_blocking(pipe.fileno(), False)
                    selector.register(pipe, selectors.EVENT_READ)
                try:
                    while selector.get_map():
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise ValueError("Verifier response timed out")
                        for key, _ in selector.select(min(remaining, 0.1)):
                            pipe = key.fileobj
                            data = os.read(pipe.fileno(), 65536)
                            if not data:
                                selector.unregister(pipe)
                            else:
                                if len(chunks[pipe]) + len(data) > limits[pipe]:
                                    channel = "response" if pipe is process.stdout else "diagnostics"
                                    raise ValueError(f"Verifier {channel} exceeded its byte limit")
                                chunks[pipe].extend(data)
                    try:
                        code = process.wait(timeout=max(0, deadline - time.monotonic()))
                    except subprocess.TimeoutExpired:
                        raise ValueError("Verifier response timed out") from None
                except BaseException:
                    # A local driver handles SIGTERM by removing its active
                    # container (up to 20 seconds). Force-kill only if that
                    # cleanup stalls. A disconnected remote driver retains
                    # its independent stage deadlines and container cleanup.
                    process.terminate()
                    try:
                        process.wait(timeout=VERIFIER_SHUTDOWN_GRACE_SECONDS)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    raise
            return subprocess.CompletedProcess(command, code,
                chunks[process.stdout].decode("utf-8"),
                chunks[process.stderr].decode("utf-8", "replace"))


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def baseline_name(identifier: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_]", "_", identifier)
    return "InclusionBench.TrustedBaseline.b_" + stem + "_" + sha256(identifier.encode())[:12]


def known_name(identifier: str) -> str:
    return "InclusionBench.Known." + re.sub(r"[^A-Za-z0-9_]", "_", identifier)


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
    from .literature import trusted_axiom_names
    has_support = (benchmark.root / "support/InclusionSupport.lean").is_file()
    lines = ["import InclusionSupport" if has_support else "import InclusionQuantum", "", "namespace InclusionBench", "",
             f"-- Dataset SHA-256: {benchmark.digest}",
             "-- Existing literature is explicitly trusted; submitted results are not."]
    entries = []

    def add(identifier, statement, sources):
        name = baseline_name(identifier)
        lines.append(f"axiom {name.removeprefix('InclusionBench.')} : {statement}")
        alias = known_name(identifier)
        lines.append(f"theorem {alias.removeprefix('InclusionBench.')} : {statement} := {name}")
        entries.append({"name": name, "alias": alias, "id": identifier, "statement": statement,
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
    if len({e["alias"] for e in entries}) != len(entries):
        raise InvalidEvidence("Friendly baseline theorem names collide")
    allowed = STANDARD_AXIOMS + [e["name"] for e in entries] + trusted_axiom_names(benchmark)
    lines += ["", "def TrustedBaseline.allowedAxiomNames : List String := [",
              ",\n".join("  " + json.dumps(name) for name in allowed), "]"]
    targets = []
    for i, raw in enumerate(claims):
        expected = f"InclusionBench.TrustedBaseline.expected_{i}"
        lines.append(f"def TrustedBaseline.expected_{i} : Prop := {proposition(Atom.read(raw))}")
        targets.append({"theorem": raw["theorem"], "expected": expected})
    lines += ["", "end InclusionBench", ""]
    return "\n".join(lines), entries, targets


def semantic_inputs(benchmark):
    """Version support separately from the frozen mathematical taskset."""
    trusted_hashes, semantic_sources = {}, {}
    for subdir in ("lean", "quantum", "support"):
        for p in sorted((benchmark.root / subdir).rglob("*.lean")):
            if ".lake" not in p.parts:
                relative = str(p.relative_to(benchmark.root))
                trusted_hashes[relative] = sha256(p.read_bytes())
                semantic_sources[relative] = p.read_text()
    lock = benchmark.root / "quantum/lake-manifest.json"
    trusted_hashes[str(lock.relative_to(benchmark.root))] = sha256(lock.read_bytes())
    # Metadata changes invalidate literature decisions, but mutable decisions
    # must not invalidate themselves. The runner only needs Lean and the lock.
    registries = {str(p.relative_to(benchmark.root)): sha256(p.read_bytes())
                  for p in sorted((benchmark.root / "support").glob("registry-*.json"))}
    return trusted_hashes, semantic_sources, canonical_hash({**trusted_hashes, **registries})


def trusted_verification_inputs(benchmark, claims):
    """Reconstruct the exact trusted inputs used by verification and admission.

    The baseline includes the report's entire ordered target list. A review
    may accept a subset of those claims, but cannot reuse their verification
    under different definitions, trusted axioms, or checker code.
    """
    claims = validate_claims(benchmark, claims)
    baseline, entries, targets = trusted_baseline(benchmark, claims)
    support = benchmark.root / "scripts" / "proofcheck"
    files = {p.name: p.read_text() for p in support.glob("*.lean")}
    if not {"ProofCodec.lean", "ProofExport.lean", "ProofAudit.lean"} <= files.keys():
        raise InvalidEvidence("Trusted proof-checker sources are missing")
    runner = (support / "remote_runner.py").read_text()
    trusted_hashes, semantic_sources, semantics = semantic_inputs(benchmark)
    bindings = {
        "baseline_sha256": sha256(baseline.encode()),
        "checker_sha256": canonical_hash({**files, "remote_runner.py": runner,
                                           "proofcheck.py": Path(__file__).read_text(),
                                           "proofbundle.py": Path(__file__).with_name("proofbundle.py").read_text(),
                                           "literature.py": Path(__file__).with_name("literature.py").read_text()}),
        "semantics_sha256": semantics,
    }
    return {"claims": claims, "baseline": baseline, "entries": entries,
            "targets": targets, "files": files, "runner": runner,
            "trusted_hashes": trusted_hashes, "semantic_sources": semantic_sources,
            "bindings": bindings}


def verification_bindings(benchmark, claims):
    """Current identity required of a report for this exact ordered claim list."""
    return trusted_verification_inputs(benchmark, claims)["bindings"]


def verify_proof(benchmark, proof_path, claims, *, report_path=None,
                 host="tkwa-ubuntu-box-wan",
                 remote_root="/home/tkwa/code/inclusion-quantum-build",
                 timeout_seconds=120,
                 image="nvidia/cuda:12.4.1-devel-ubuntu22.04",
                 toolchain_path=None, literature_requests=None) -> dict:
    """Return verification or pending literature review; never award points.

    `host=None` runs the same Docker driver on the local Linux host. A file is
    a legacy Lean body. A directory is a bounded submission.json project with
    ordinary modules. Only its immutable source snapshot enters the sandbox.
    """
    from .literature import validate_requests, bind_dependencies, dependency_decisions, curated_catalog
    requests = validate_requests(benchmark, literature_requests)
    claims = validate_claims(benchmark, claims)
    if not isinstance(image, str) or not image.strip() or image.startswith("-"):
        raise InvalidEvidence("Provide an installed Docker image name or digest")
    if not isinstance(timeout_seconds, int) or not 5 <= timeout_seconds <= 3600:
        raise InvalidEvidence("Proof timeout must be between 5 and 3,600 seconds")
    bundle = load_proof_bundle(proof_path)
    trusted = trusted_verification_inputs(benchmark, claims)
    baseline, entries, targets = (trusted[key] for key in ("baseline", "entries", "targets"))
    files = dict(trusted["files"])
    files["TrustedBaseline.lean"] = baseline
    # These comments are not security checks. The kernel replays the exported
    # declarations in a clean environment, with no candidate module imported.
    names = json.dumps([c["theorem"] for c in claims])
    if bundle.metadata is None:
        body = next(iter(bundle.sources.values()))
        files["Candidate.lean"] = "import ProofExport\nimport TrustedBaseline\n\n" + body + "\n\n#proofcheck_export_targets " + names + "\n"
    else:
        files["AuditImports.lean"] = "import TrustedBaseline\n" + "".join(
            "import " + module + "\n" for module in bundle.external_imports)
        # Load trusted library initializers into the auditor process as well
        # as importing their declarations into its separate fresh environment.
        files["ProofAudit.lean"] = "import AuditImports\n" + files["ProofAudit.lean"]
        files["Candidate.lean"] = ("import ProofExport\nimport AuditImports\nimport " + bundle.entrypoint +
            "\n\n#proofcheck_export_project " + json.dumps(bundle.module_order) + " " + names + "\n")
    files["targets.json"] = json.dumps(targets)
    files["literature.json"] = json.dumps({"requests": requests})
    packet = {"files": files, "trusted_hashes": trusted["trusted_hashes"], "semantic_sources": trusted["semantic_sources"],
              "remote_root": str(remote_root), "timeout_seconds": timeout_seconds,
              "image": image, "toolchain_path": str(toolchain_path) if toolchain_path is not None else None}
    if bundle.metadata is not None:
        packet["candidate_project"] = {"sources": bundle.sources, "entrypoint": bundle.entrypoint,
                                       "manifest": bundle.files["submission.json"].decode("utf-8"),
                                       "module_order": bundle.module_order,
                                       "external_imports": bundle.external_imports,
                                       "metadata": bundle.metadata}
    runner = trusted["runner"]
    command = (["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host,
                "python3 -c " + shlex.quote(runner)] if host else ["python3", "-c", runner])
    report = {"schema_version": 1, "dataset_sha256": benchmark.digest,
              "proof_sha256": bundle.proof_sha256, "claims": claims,
              **trusted["bindings"], "baseline_axioms": entries,
              "method": "lean4-data-only-fresh-kernel-replay", "official_points": 0,
              "literature_requests": requests,
              "support_axioms": [entry for entry in curated_catalog(benchmark) if entry.get("kind") == "axiom"]}
    if bundle.metadata is not None:
        report["proof_project"] = bundle.metadata
    try:
        # Only the trusted driver writes this pipe. The proof export stays in
        # its bounded file and is parsed only by the isolated Lean auditor.
        completed = _run_verifier(command, input=json.dumps(packet),
                                  timeout=3 * timeout_seconds + 120)
        response = json.loads(completed.stdout)
        if not isinstance(response, dict) or response.get("status") not in {"verified", "needs_literature_review", "rejected", "unavailable"}:
            raise ValueError("Invalid verifier response")
        if completed.returncode and response["status"] in {"verified", "needs_literature_review"}:
            raise ValueError("Verifier failed while reporting success")
        if response["status"] in {"verified", "needs_literature_review"}:
            dependencies = bind_dependencies(benchmark, response.get("literature_dependencies", []),
                                             requests, **trusted["bindings"])
            if bool(dependencies) != (response["status"] == "needs_literature_review"):
                raise InvalidEvidence("Auditor status does not match its literature dependencies")
            if dependencies and response.get("kernel_status") != "verified":
                raise InvalidEvidence("Literature dependencies lack successful kernel verification")
            decisions = dependency_decisions(benchmark, dependencies, trusted["bindings"]["semantics_sha256"])
            response["literature_dependencies"] = dependencies
            response["literature_reviews"] = decisions
            if dependencies:
                response["status"] = "verified" if all(d["status"] == "accepted" for d in decisions) else "needs_literature_review"
        # Immutable input bindings cannot be replaced by diagnostic output.
        for key in report:
            if key in response and response[key] != report[key]:
                raise InvalidEvidence("Verifier attempted to replace input binding: " + key)
        report.update(response)
    except (OSError, subprocess.TimeoutExpired, ValueError, RecursionError, InvalidEvidence) as error:
        report.update(status="unavailable", reason=f"Verifier did not return valid evidence: {error}")
    if report_path is not None:
        Path(report_path).write_text(json.dumps(report, indent=2) + "\n")
    return report
