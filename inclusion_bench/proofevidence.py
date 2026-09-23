"""Bind verified source snapshots to one sealed model-submission directory."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from .engine import Atom, InvalidEvidence


def _sealed_files(attempt):
    files = {}
    for artifact in attempt.get("artifacts", []):
        relative = artifact.get("path") if isinstance(artifact, dict) else None
        if not isinstance(relative, str) or relative in files:
            raise InvalidEvidence("Proof evidence requires distinct sealed artifact paths")
        files[relative] = artifact.get("sha256")
    return files


def _sealed_path(directory, relative, files):
    from .evaluation import artifact_path, sha256_file
    path = PurePosixPath(relative)
    if (not relative or path.is_absolute() or path.as_posix() != relative or
            ".." in path.parts or "\\" in relative or relative not in files):
        raise InvalidEvidence("Project file is not a sealed artifact: " + relative)
    current = Path(directory)
    for component in path.parts:
        current = current / component
        if current.is_symlink():
            raise InvalidEvidence("Project evidence may not use symlinks: " + relative)
    resolved = artifact_path(directory, relative)
    if sha256_file(resolved) != files[relative]:
        raise InvalidEvidence("Project artifact hash mismatch: " + relative)
    return resolved


def _metadata_document(directory, relative, files):
    path = _sealed_path(directory, relative, files)
    if path.stat().st_size > 2 * 1024 * 1024:
        raise InvalidEvidence("Project metadata exceeds 2 MiB: " + relative)
    try:
        return json.loads(path.read_bytes().decode("utf-8"))
    except (ValueError, UnicodeError) as error:
        raise InvalidEvidence("Project metadata must be UTF-8 JSON: " + relative) from error


def _load_sealed_project(directory, manifest, files):
    from .proofbundle import load_proof_bundle
    path = _sealed_path(directory, manifest, files)
    if path.name != "submission.json":
        raise InvalidEvidence("Project entry must be a submission.json manifest")
    bundle = load_proof_bundle(path.parent)
    if bundle.metadata is None:
        raise InvalidEvidence("Submission manifest must identify a project")
    root = PurePosixPath(manifest).parent
    for name, source in bundle.files.items():
        relative = (root / name).as_posix()
        _sealed_path(directory, relative, files)
        if files[relative] != hashlib.sha256(source).hexdigest():
            raise InvalidEvidence("Project file is not sealed under the verified root: " + relative)
    return root, bundle


def validate_submission_artifacts(benchmark, attempt, directory):
    """Validate an unverified adapter project without changing token accounting."""
    from .literature import validate_requests
    from .proofcheck import validate_claims
    manifest = attempt.get("submission_manifest")
    if manifest is None:
        return None
    if not isinstance(manifest, str) or attempt.get("status") != "proof_candidate":
        raise InvalidEvidence("Only a proof candidate may identify a submission manifest")
    files = _sealed_files(attempt)
    root, _ = _load_sealed_project(directory, manifest, files)
    document = _metadata_document(directory, (root / "claims.json").as_posix(), files)
    mapped = document.get("claims") if isinstance(document, dict) else document
    if not isinstance(mapped, list):
        raise InvalidEvidence("Project claims.json must contain a claims array")
    mapped = validate_claims(benchmark, mapped) if mapped else []
    ordinary = [Atom.read(c).json() for c in attempt.get("claims", []) if c["relation"] != "independence"]
    if [Atom.read(c).json() for c in mapped] != ordinary:
        raise InvalidEvidence("Project claims.json must match the submitted ordinary claims")
    document = _metadata_document(directory, (root / "literature.json").as_posix(), files)
    if (not isinstance(document, dict) or set(document) != {"requests"} or not isinstance(document["requests"], list) or
            validate_requests(benchmark, document["requests"]) !=
            validate_requests(benchmark, attempt.get("literature_requests", []))):
        raise InvalidEvidence("Project literature.json must match the submitted literature requests")
    return manifest


def _check_metadata(benchmark, report, attempt, directory, root, files):
    from .literature import validate_requests
    from .proofcheck import validate_claims
    reported_claims = validate_claims(benchmark, report.get("claims", []))
    submitted = {Atom.read(claim) for claim in attempt.get("claims", [])}
    if not {Atom.read(claim) for claim in reported_claims} <= submitted:
        raise InvalidEvidence("Project report includes a claim outside this attempt")
    relative = (root / "claims.json").as_posix()
    path = Path(directory) / relative
    if path.exists() or path.is_symlink() or relative in files:
        document = _metadata_document(directory, relative, files)
        claims = document.get("claims") if isinstance(document, dict) else document
        if validate_claims(benchmark, claims) != reported_claims:
            raise InvalidEvidence("Project claims.json does not match the verified theorem mapping")
    requests = validate_requests(benchmark, report.get("literature_requests", []))
    if "literature_requests" in attempt and validate_requests(benchmark, attempt["literature_requests"]) != requests:
        raise InvalidEvidence("Project literature requests do not match this attempt")
    relative = (root / "literature.json").as_posix()
    path = Path(directory) / relative
    if path.exists() or path.is_symlink() or relative in files:
        document = _metadata_document(directory, relative, files)
        if not isinstance(document, dict) or not isinstance(document.get("requests"), list):
            raise InvalidEvidence("Project literature.json must contain a requests array")
        if validate_requests(benchmark, document["requests"]) != requests:
            raise InvalidEvidence("Project literature.json does not match the verified dependencies")


def _project_owns_source(directory, files, sources):
    """Recognize declared project paths without requiring missing helpers to exist."""
    from .proofbundle import MODULE_NAME, SOURCE_PATH
    for relative in files:
        if PurePosixPath(relative).name != "submission.json":
            continue
        try:
            manifest = _metadata_document(directory, relative, files)
        except (InvalidEvidence, OSError, ValueError):
            continue  # An unrelated JSON artifact is not a project declaration.
        if (not isinstance(manifest, dict) or set(manifest) != {"schema_version", "entrypoint", "files"} or
                type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1 or
                not isinstance(manifest["entrypoint"], str) or
                not re.fullmatch(MODULE_NAME, manifest["entrypoint"]) or
                not isinstance(manifest["files"], list) or not manifest["files"] or
                any(not isinstance(name, str) or not re.fullmatch(SOURCE_PATH, name) for name in manifest["files"]) or
                manifest["entrypoint"].replace(".", "/") + ".lean" not in manifest["files"]):
            continue
        root = PurePosixPath(relative).parent
        if sources.intersection((root / name).as_posix() for name in manifest["files"]):
            return True
    return False


def validate_proof_evidence(benchmark, report, attempt, directory):
    """Require the complete verified project under one sealed root.

    Legacy reports retain their raw single-file hash contract. A declared
    project can never fall back to matching only its entrypoint or a helper.
    """
    from .evaluation import artifact_path, sha256_file
    if not isinstance(report, dict):
        raise InvalidEvidence("Proof verification evidence must be an object")
    files = _sealed_files(attempt)
    pointer = attempt.get("submission_manifest")
    if pointer is not None and not isinstance(pointer, str):
        raise InvalidEvidence("Submission manifest must name a sealed relative file")
    metadata = report.get("proof_project")
    if metadata is None:
        if pointer is not None:
            raise InvalidEvidence("A project attempt requires complete project verification evidence")
        source_hash = report.get("proof_sha256") or report.get("source_sha256")
        matches = [name for name, digest in files.items() if digest == source_hash and source_hash]
        if _project_owns_source(directory, files, set(matches)):
            raise InvalidEvidence("A project source requires complete project verification evidence")
        for name in matches:
            path = artifact_path(directory, name)
            if sha256_file(path) == source_hash:
                return {"kind": "single-file", "path": name, "proof_sha256": source_hash}
        raise InvalidEvidence("Verified source is not one of this attempt's sealed artifacts")
    if (not isinstance(metadata, dict) or metadata.get("kind") != "project" or
            not isinstance(metadata.get("files"), dict) or "submission.json" not in metadata["files"]):
        raise InvalidEvidence("Proof report has invalid project source metadata")
    if (report.get("status") != "verified" or report.get("dataset_sha256") != benchmark.digest or
            report.get("method") != "lean4-data-only-fresh-kernel-replay"):
        raise InvalidEvidence("Project proof report is not verified for this dataset and method")
    from .proofcheck import verification_bindings
    for key, expected in verification_bindings(benchmark, report.get("claims", [])).items():
        if report.get(key) != expected:
            raise InvalidEvidence("Project proof report has stale trusted input: " + key)
    if pointer is not None:
        candidates = [pointer]
    else:
        candidates = [name for name, digest in files.items()
                      if PurePosixPath(name).name == "submission.json" and
                      digest == metadata["files"]["submission.json"]]
    failures = []
    for manifest in candidates:
        try:
            root, bundle = _load_sealed_project(directory, manifest, files)
            if bundle.metadata != metadata or bundle.proof_sha256 != report.get("proof_sha256"):
                raise InvalidEvidence("Project digest or source map does not match the verified snapshot")
            if report.get("source_sha256", bundle.proof_sha256) != bundle.proof_sha256:
                raise InvalidEvidence("Project report contains a conflicting single-file digest")
            _check_metadata(benchmark, report, attempt, directory, root, files)
            return {"kind": "project", "manifest": manifest, "proof_sha256": bundle.proof_sha256,
                    "proof_project": metadata}
        except (InvalidEvidence, OSError, ValueError) as error:
            failures.append(str(error))
    detail = "; ".join(failures[:3]) if failures else "no matching sealed submission.json manifest"
    raise InvalidEvidence("Verified project is not one complete sealed submission: " + detail)
