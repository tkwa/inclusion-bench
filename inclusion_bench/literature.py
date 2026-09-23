"""Cited mathematical dependencies and maintainer decisions about their exact meaning.

A citation is a request, never permission to assume a proposition. The fresh
Lean auditor supplies the declaration and its local defining context. Reviews
bind those data, citations, the dataset, and every trusted semantic source.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import calendar
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .benchmark import canonical_hash, read_json
from .engine import InvalidEvidence

REQUEST_FIELDS = {"name", "statement", "sources", "rationale"}
DEPENDENCY_FIELDS = {"name", "statement", "declaration", "context", "request",
                     "dataset_sha256", "semantics_sha256", "baseline_sha256", "checker_sha256"}
CHECKS = ("published_before_cutoff", "exact_statement", "model_alignment", "no_new_result_assumed")
MAX_REQUESTS = 128
MAX_METADATA_BYTES = 1024 * 1024
NAME = re.compile(r"Literature\.[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")


def _text(value, label, limit=20000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise InvalidEvidence(f"Literature {label} must be nonempty text (at most {limit} characters)")
    return value


def _source(source, cutoff):
    if not isinstance(source, dict):
        raise InvalidEvidence("Each literature source must be an object")
    for field in ("title", "url", "locator", "publication_date"):
        _text(source.get(field), "source " + field, 4000)
    try:
        url = urlsplit(source["url"])
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
            raise ValueError()
        published = source["publication_date"]
        if re.fullmatch(r"\d{4}", published):
            latest = date(int(published), 12, 31)
        elif re.fullmatch(r"\d{4}-\d{2}", published):
            year, month = map(int, published.split("-"))
            latest = date(year, month, calendar.monthrange(year, month)[1])
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", published):
            latest = date.fromisoformat(published)
        else:
            raise ValueError()
        if latest > date.fromisoformat(cutoff):
            raise InvalidEvidence("Literature must be published by the cutoff; supply a precise date if needed")
    except InvalidEvidence:
        raise
    except (ValueError, TypeError) as error:
        raise InvalidEvidence("Literature source needs an HTTP(S) URL and an ISO publication date") from error
    return {k: source[k] for k in ("title", "url", "locator", "publication_date")}


def validate_requests(benchmark, requests=None):
    if requests is None:
        return []
    if not isinstance(requests, list) or len(requests) > MAX_REQUESTS:
        raise InvalidEvidence(f"Literature requests must be a list of at most {MAX_REQUESTS} items")
    try:
        if len(json.dumps(requests, ensure_ascii=False).encode()) > MAX_METADATA_BYTES:
            raise InvalidEvidence("Literature metadata exceeds 1 MiB")
    except (TypeError, ValueError) as error:
        raise InvalidEvidence("Literature metadata must be JSON data") from error
    result, seen = [], set()
    for request in requests:
        if not isinstance(request, dict) or set(request) != REQUEST_FIELDS:
            raise InvalidEvidence("Literature request requires exactly name, statement, sources, and rationale")
        name = request["name"]
        if not isinstance(name, str) or len(name) > 240 or not NAME.fullmatch(name) or name in seen:
            raise InvalidEvidence("Literature requests need distinct qualified names under Literature")
        seen.add(name)
        if not isinstance(request["sources"], list) or not 1 <= len(request["sources"]) <= 16:
            raise InvalidEvidence("Each literature request needs between 1 and 16 sources")
        result.append({"name": name, "statement": _text(request["statement"], "statement"),
                       "rationale": _text(request["rationale"], "rationale"),
                       "sources": [_source(s, benchmark.policy["cutoff"]) for s in request["sources"]]})
    return result


def curated_catalog(benchmark):
    """Read versioned support metadata; mutable submission reviews live separately."""
    result, names = [], set()
    for path in sorted((benchmark.root / "support").glob("registry-*.json")):
        registry = read_json(path)
        sources = {s["id"]: s for s in registry["sources"]}
        for entry in registry["theorems"]:
            name = entry["name"]
            if name in names or not name.startswith("InclusionBench.Support."):
                raise InvalidEvidence("Invalid or repeated support theorem: " + name)
            names.add(name)
            cited = []
            for identifier in entry["source_ids"]:
                source = sources[identifier]
                cited.append(_source({**source, "locator": entry["locator"]}, benchmark.policy["cutoff"]))
            if not cited:
                raise InvalidEvidence("Support entries require literature provenance")
            result.append({**entry, "sources": cited})
    return result


def trusted_axiom_names(benchmark):
    return [e["name"] for e in curated_catalog(benchmark) if e.get("kind") == "axiom"]


def theorem_catalog(benchmark):
    from .proofcheck import trusted_baseline
    # No targets are generated for this catalog-only call.
    _, entries, _ = trusted_baseline(benchmark, [])
    existing = [{**e, "name": e["alias"], "axiom_name": e["name"], "module": "TrustedBaseline", "kind": "baseline",
                 "sources": [benchmark.sources[s] for s in e["source_ids"]]} for e in entries]
    return existing + curated_catalog(benchmark)


def dependency_identity(dependency):
    if not isinstance(dependency, dict) or not DEPENDENCY_FIELDS <= dependency.keys():
        raise InvalidEvidence("Literature dependency is missing its exact declaration, context, or bindings")
    return canonical_hash({k: dependency[k] for k in sorted(DEPENDENCY_FIELDS)})


def _validate_dependency(benchmark, dependency, semantics_sha256):
    digest = dependency_identity(dependency)
    request = validate_requests(benchmark, [dependency["request"]])[0]
    if dependency["name"] != request["name"]:
        raise InvalidEvidence("Literature dependency name does not match its citation")
    if dependency.get("dependency_sha256") != digest:
        raise InvalidEvidence("Literature dependency hash mismatch")
    if dependency["dataset_sha256"] != benchmark.digest or dependency["semantics_sha256"] != semantics_sha256:
        raise InvalidEvidence("Literature dependency has stale dataset or semantic bindings")
    if not isinstance(dependency["baseline_sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", dependency["baseline_sha256"]):
        raise InvalidEvidence("Literature dependency requires its exact trusted baseline binding")
    if not isinstance(dependency["checker_sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", dependency["checker_sha256"]):
        raise InvalidEvidence("Literature dependency requires its checker binding")
    declaration = dependency["declaration"]
    if not isinstance(declaration, dict) or declaration.get("kind") != "axiom" or "value" in declaration:
        raise InvalidEvidence("Literature review must bind a reconstructed axiom declaration")
    if not isinstance(dependency["context"], list) or not all(isinstance(d, dict) for d in dependency["context"]):
        raise InvalidEvidence("Literature review must include the reconstructed local context")
    _text(dependency["statement"], "reconstructed statement", 1000000)
    return digest


def literature_reviews(benchmark):
    path = benchmark.root / "support/literature-reviews.json"
    records = read_json(path) if path.exists() else []
    if not isinstance(records, list):
        raise InvalidEvidence("Literature review registry must be a list")
    return records


def _decisions(benchmark):
    latest = {}
    for record in literature_reviews(benchmark):
        if not isinstance(record, dict):
            raise InvalidEvidence("Invalid literature review registry record")
        if record.get("review_sha256") != canonical_hash({k: v for k, v in record.items() if k != "review_sha256"}):
            raise InvalidEvidence("Literature review registry hash mismatch")
        digest = dependency_identity(record.get("dependency"))
        if digest != record["dependency"].get("dependency_sha256"):
            raise InvalidEvidence("Literature review registry dependency hash mismatch")
        if record.get("status") not in {"accepted", "rejected"}:
            raise InvalidEvidence("Invalid literature review decision")
        if record["status"] == "accepted" and not all(record.get("checks", {}).get(c) is True for c in CHECKS):
            raise InvalidEvidence("Accepted literature decision lacks statement and source checks")
        latest[digest] = record
    return latest


def bind_dependencies(benchmark, raw_dependencies, requests, semantics_sha256, baseline_sha256, checker_sha256):
    if not isinstance(raw_dependencies, list) or len(raw_dependencies) > MAX_REQUESTS:
        raise InvalidEvidence("Auditor returned an invalid literature dependency list")
    requested = {r["name"]: r for r in validate_requests(benchmark, requests)}
    result, seen = [], set()
    for raw in raw_dependencies:
        if not isinstance(raw, dict) or set(raw) != {"name", "statement", "declaration", "context"}:
            raise InvalidEvidence("Auditor returned an incomplete literature declaration")
        name = raw["name"]
        if name not in requested or name in seen:
            raise InvalidEvidence("Auditor returned an unrequested or duplicate literature dependency")
        seen.add(name)
        item = {**raw, "request": requested[name], "dataset_sha256": benchmark.digest,
                "semantics_sha256": semantics_sha256, "baseline_sha256": baseline_sha256, "checker_sha256": checker_sha256}
        item["dependency_sha256"] = dependency_identity(item)
        _validate_dependency(benchmark, item, semantics_sha256)
        result.append(item)
    return result


def dependency_decisions(benchmark, dependencies, semantics_sha256):
    if not isinstance(dependencies, list) or len(dependencies) > MAX_REQUESTS:
        raise InvalidEvidence("Invalid literature dependencies")
    latest, result, seen = _decisions(benchmark), [], set()
    for dependency in dependencies:
        digest = _validate_dependency(benchmark, dependency, semantics_sha256)
        if dependency["name"] in seen:
            raise InvalidEvidence("Duplicate literature dependency")
        seen.add(dependency["name"])
        review = latest.get(digest)
        result.append({"name": dependency["name"], "dependency_sha256": digest,
                       "status": review["status"] if review else "pending",
                       "review_sha256": review["review_sha256"] if review else None})
    return result


def require_approved_dependencies(benchmark, report):
    dependencies = report.get("literature_dependencies", [])
    if not isinstance(dependencies, list):
        raise InvalidEvidence("Literature dependencies must be a list")
    used = {name for target in report.get("targets", []) for name in target.get("axioms", [])
            if isinstance(name, str) and name.startswith("Literature.")}
    declared = {dependency.get("name") for dependency in dependencies if isinstance(dependency, dict)}
    if not used <= declared:
        raise InvalidEvidence("Proof report omits a used literature dependency")
    if not dependencies:
        if report.get("literature_reviews"):
            raise InvalidEvidence("Literature approvals without dependencies")
        return []
    from .proofcheck import verification_bindings
    bindings = verification_bindings(benchmark, report.get("claims", []))
    if any(report.get(k) != v for k, v in bindings.items()):
        raise InvalidEvidence("Proof report has stale trusted verification inputs")
    semantics = bindings["semantics_sha256"]
    if any(d.get(k) != report.get(k) for d in dependencies for k in ("baseline_sha256", "checker_sha256")):
        raise InvalidEvidence("Literature dependency has a mismatched target baseline")
    decisions = dependency_decisions(benchmark, dependencies, semantics)
    if any(d["status"] != "accepted" for d in decisions):
        raise InvalidEvidence("Proof uses literature without a current accepted review")
    if decisions != report.get("literature_reviews"):
        raise InvalidEvidence("Proof report has stale literature decisions; recheck the submission")
    return decisions


def record_literature_review(benchmark, review):
    if not isinstance(review, dict) or review.get("schema_version") != 1:
        raise InvalidEvidence("Literature review requires schema_version 1")
    for key in ("reviewer", "rationale"):
        _text(review.get(key), "review " + key)
    if review.get("status") not in {"accepted", "rejected"}:
        raise InvalidEvidence("Literature review status must be accepted or rejected")
    if review["status"] == "accepted" and not all(review.get("checks", {}).get(c) is True for c in CHECKS):
        raise InvalidEvidence("Acceptance requires publication, exact statement, model, and no-new-result checks")
    from .proofcheck import semantic_inputs
    _, _, semantics = semantic_inputs(benchmark)
    _validate_dependency(benchmark, review.get("dependency"), semantics)
    records = literature_reviews(benchmark)
    _decisions(benchmark)  # Refuse to extend a corrupted registry.
    record = {k: review[k] for k in ("schema_version", "reviewer", "rationale", "status", "dependency")}
    record["checks"] = {c: review.get("checks", {}).get(c) is True for c in CHECKS}
    record["recorded_at"] = datetime.now(timezone.utc).isoformat()
    record["review_sha256"] = canonical_hash(record)
    records.append(record)
    path = benchmark.root / "support/literature-reviews.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)
    return record
