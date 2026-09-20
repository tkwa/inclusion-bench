"""Regenerate the draft matrix, website payload and checked Lean examples."""
import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark, read_json
from inclusion_bench.engine import Atom, InvalidEvidence
from inclusion_bench.lean_export import export_theorem
from inclusion_bench.evaluation import taskset, leaderboard, sha256_file
from inclusion_bench.reviews import history_status
from inclusion_bench.runner import frozen_release


def write(path, value, compact=False):
    (ROOT / path).write_text(json.dumps(value, indent=None if compact else 2, ensure_ascii=False, separators=(",", ":") if compact else None) + "\n")


def proof_steps(closure, exclude=()):
    return [{"id": atom.key, **atom.json(), **record} for atom, record in closure.proofs.items() if atom not in exclude]


def publication_metadata(benchmark, suite):
    """Promote display metadata without rewriting a frozen benchmark policy."""
    metadata = {
        "release_status": benchmark.policy.get("release_status", "published"),
        "release_note": benchmark.policy.get("release_note"),
        "repository_ref": benchmark.policy.get("repository_ref", "main"),
        "publication": None,
    }
    path = benchmark.root / "data/publication.json"
    if not path.exists():
        return metadata
    record = read_json(path)
    freeze = frozen_release(benchmark)
    expected = {
        "benchmark_version": benchmark.policy["version"],
        "dataset_sha256": benchmark.digest,
        "taskset_sha256": suite["taskset_sha256"],
        "formalization_bundle_sha256": suite["formalization_bundle"]["bundle_sha256"],
        "freeze_sha256": sha256_file(benchmark.root / "data/freeze.json"),
        "baseline_audit_sha256": sha256_file(benchmark.root / "research/baseline-audit.json"),
    }
    if (not isinstance(record, dict) or record.get("schema_version") != 1 or
            record.get("status") != "published" or
            any(record.get(key) != value for key, value in expected.items()) or
            freeze["baseline_audit_sha256"] != expected["baseline_audit_sha256"]):
        raise InvalidEvidence("Publication record does not bind this exact frozen release")
    # Published documentation links use the immutable version tag. Keep the
    # provisional branch alive for links sealed in the original policy.
    if record.get("repository_ref") != "v" + benchmark.policy["version"]:
        raise InvalidEvidence("Publication record requires the release's version tag")
    if not isinstance(record.get("note"), str) or not record["note"].strip():
        raise InvalidEvidence("Publication record requires a release note")
    return {"release_status": record["status"], "release_note": record["note"],
            "repository_ref": record["repository_ref"], "publication": record}


def build():
    runpy.run_path(str(ROOT / "scripts/import_research.py"), run_name="__main__")
    benchmark = Benchmark(ROOT)
    if benchmark.policy["release_stage"] == "certified":
        benchmark.certified_eligibility()
        matrix = read_json(ROOT / "data/eligibility.json")
        matrix["counts"] = {status: sum(p["status"] == status for p in matrix["pairs"])
                            for status in ("inclusion", "separation", "independence", "open_at_cutoff", "unreviewed")}
    else:
        matrix = benchmark.matrix()
        write("data/eligibility.json", matrix)
    suite = taskset(benchmark)
    write("evaluation/tasks.json", suite)
    coverage = read_json(ROOT / "research/coverage.json")
    roster_examples = read_json(ROOT / "research/v0.4.0/representative-questions.json")
    scenarios = []
    cases = [
        {"id": "bpp-strictly-below-np", **read_json(ROOT / "examples/bpp-strictly-below-np.json")},
        {"id": "p-equals-np", **read_json(ROOT / "examples/p-equals-np.json")},
        *[s for s in coverage["scenarios"] if s["claims"]],
        *roster_examples["scenarios"],
    ]
    for case in cases:
        result = benchmark.score(case)
        closure = benchmark.closure(case["claims"])
        resolutions = [{k: v for k, v in row.items() if k != "proof"} | {"proof": {"target": row["proof"]["target"]}} for row in result["resolutions"]]
        scenarios.append({"id": case["id"], "title": case["title"], "claims": case["claims"], "score": result["score"], "official_points": 0, "resolutions": resolutions, "proof_steps": proof_steps(closure, benchmark.baseline.proofs), "notes": case.get("notes", "Hypothetical result, not a verified achievement.")})
    pairs = []
    opened, historically_known, history = history_status(benchmark)
    for pair in matrix["pairs"]:
        entry = dict(pair)
        decision = history.get((pair["left"], pair["right"]))
        if decision:
            entry["history_status"] = decision["status"]
            entry["history_review_sha256"] = decision["review_sha256"]
        if pair["status"] in {"inclusion", "separation", "independence"}:
            atom = Atom(pair["status"], pair["left"], pair["right"])
            if atom in benchmark.baseline.proofs:
                entry["proof"] = {"target": atom.key}
        pairs.append(entry)
    publication = publication_metadata(benchmark, suite)
    repository_ref = publication["repository_ref"]
    source_base = "https://github.com/tkwa/inclusion-bench/blob/" + repository_ref + "/"
    sources = []
    for original in benchmark.knowledge["sources"]:
        source = dict(original)
        if not source["url"].startswith("https://"):
            source["url"] = source_base + source["url"]
        sources.append(source)
    payload = {
        "name": "InclusionBench", "version": benchmark.policy["version"], "stage": benchmark.policy["release_stage"], "repository_url": "https://github.com/tkwa/inclusion-bench",
        "website_url": "https://tkwa.me",
        **publication,
        "independence_policy": benchmark.policy["independence"],
        "independence_premises": benchmark.policy["independence_premises"],
        "cutoff": benchmark.policy["cutoff"], "class_count": len(benchmark.ids), "ordered_pairs": len(benchmark.ids) ** 2,
        "dataset_sha256": benchmark.digest, "counts": matrix["counts"], "classes": benchmark.scored_classes,
        "background_classes": benchmark.background_classes,
        "context_class_count": len(benchmark.context_ids),
        "pairs": pairs, "baseline_proof_steps": proof_steps(benchmark.baseline),
        "leaderboard": leaderboard(benchmark, read_json(ROOT / "data/leaderboard_runs.json")),
        "baseline": {"name": "Pre-cutoff public knowledge", "score": 0, "date": benchmark.policy["cutoff"], "kind": "Historical reference; not an evaluated model"},
        "task_count": len(suite["tasks"]), "taskset_sha256": suite["taskset_sha256"],
        "scenarios": scenarios, "sources": sources, "coverage": coverage,
        "seed_fact_count": len(benchmark.knowledge["facts"]), "rule_count": len(benchmark.knowledge["rules"]),
        "historical_review": {
            "reviewed_open_count": len(opened),
            "reviewed_known_count": len(historically_known),
            "all_candidates_reviewed": benchmark.unresolved <= opened | historically_known,
            "report_url": source_base + "research/baseline-audit.md",
        },
    }
    write("web/benchmark.json", payload, compact=True)
    exports = [
        ("ExampleConsequence", read_json(ROOT / "examples/bpp-strictly-below-np.json")["claims"], Atom("separation", "PSPACE", "P")),
        ("ComplementExample", [], Atom("inclusion", "P", "coUP")),
        ("ComplementSwapExample", [dict(relation="separation", left="NP", right="coNP")], Atom("separation", "coNP", "NP")),
        ("ContrapositiveExample", [dict(relation="separation", left="PH", right="Sigma2P")], Atom("separation", "NP", "Ppoly")),
        ("CollapseExample", [dict(relation="inclusion", left="NP", right="P")], Atom("inclusion", "PH", "P")),
    ]
    for name, claims, target in exports:
        (ROOT / "lean" / f"{name}.lean").write_text(export_theorem(benchmark, benchmark.closure(claims), target, name))
    print(json.dumps({"dataset_sha256": benchmark.digest, "counts": matrix["counts"], "scenarios": len(scenarios), "website_bytes": (ROOT / "web/benchmark.json").stat().st_size}))


if __name__ == "__main__":
    build()
