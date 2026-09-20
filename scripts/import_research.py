"""Deterministically assemble cited inputs. Never certifies cutoff eligibility.

The original research files remain the source of the old context theory.
The versioned v0.4.0 dossiers extend it; demoting an endpoint does not discard its
facts, definitions, or implication rules.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = (
    "research/v0.4.0/classical-new-baseline.json",
    "research/v0.4.0/counting-new-baseline.json",
    "research/v0.4.0/quantum-new-baseline.json",
    "research/v0.4.0/counting-cross-review.json",
    "research/v0.4.0/classical-baseline-cross-review.json",
)


def read(path):
    return json.loads((ROOT / path).read_text())


def write(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def unique_sources(documents):
    """Shared primary sources may recur only with an identical source record."""
    by_id = {}
    for document in documents:
        for item in document["sources"]:
            previous = by_id.get(item["id"])
            if previous is not None and previous != item:
                raise ValueError(f"Conflicting source records: {item['id']}")
            by_id[item["id"]] = item
    return list(by_id.values())


def intersection_rules(new_ids):
    """Instantiate the old class-independent intersection rules for new nodes."""
    result = []
    for name in new_ids:
        for left, right, target, prefix, sources, explanation in (
            ("NP", "coNP", "NPcapcoNP", "intersection-np-conp",
             ["ClassicalDerivations"], "Class intersection introduction."),
            ("RP", "coRP", "ZPP", "intersection-rp-corp",
             ["Gill1977", "AB2007"], "ZPP = RP ∩ coRP."),
        ):
            result.append({
                "id": f"{prefix}-{name}",
                "premises": [{"relation": "inclusion", "left": name, "right": x}
                             for x in (left, right)],
                "conclusions": [{"relation": "inclusion", "left": name, "right": target}],
                "source_ids": sources,
                "justification": explanation,
            })
    return result


def build():
    classical = read("research/classical.json")
    quantum = read("research/quantum.json")
    extensions = [read(path) for path in EXTENSIONS]
    documents = [classical, quantum, *extensions]
    catalog = read("data/classes.json")
    recommendations = classical["class_recommendations"]
    complements = [
        {"left": name, "right": name,
         "source_ids": recommendations["complement_sources"].get(
             name, recommendations["complement_sources"]["default"])}
        for name in recommendations["complement_self"]
    ]
    complements.extend(
        {"left": left, "right": right,
         "source_ids": recommendations["complement_sources"]["default"]}
        for left, right in recommendations["complement_pairs"]
    )
    complements.extend(quantum["complement_pairs"])
    for document in extensions:
        complements.extend(document.get("complements", []))
    seen_complements = set()
    for item in complements:
        key = tuple(sorted((item["left"], item["right"])))
        if key in seen_complements:
            raise ValueError(f"Duplicate complement identity: {key}")
        seen_complements.add(key)
    catalog["complements"] = complements

    defined = set(re.findall(r"\|\s+\.(\w+)\s+=>\s+some",
                            (ROOT / "lean/InclusionBench/Definitions.lean").read_text()))
    complete = set(re.findall(r"\|\s+\.(\w+)\s+=>",
                             (ROOT / "quantum/InclusionQuantum/Complete.lean").read_text()))
    ids = {item["id"] for item in catalog["classes"]}
    if complete != ids or not defined <= ids:
        raise ValueError("Complete Lean interpretation must cover exactly the context catalog")
    sources = unique_sources(documents)
    source_ids = {item["id"] for item in sources}
    for item in catalog["classes"]:
        citations = item.get("definition_source_ids", [])
        if not citations or not set(citations) <= source_ids:
            raise ValueError(f"Missing explicit definition citations: {item['id']}")
        item["formalization_status"] = "operational_model_defined_equivalence_unproved"
        item["lean_definition_file"] = (
            "lean/InclusionBench/Definitions.lean" if item["id"] in defined
            else "quantum/InclusionQuantum/Complete.lean"
        )

    new_ids = [item["id"] for item in catalog["classes"]
               if any(item["id"] in extension["scope"]["focus_classes"]
                      for extension in extensions)]
    facts = [item for document in documents for item in document["facts"]]
    rules = [item for document in documents for item in document["rules"]]
    rules.extend(intersection_rules(new_ids))
    names = [item["id"] for item in [*facts, *rules]]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate fact/rule identifiers in research inputs")
    knowledge = {
        "schema_version": 1,
        "status": "trusted cited baseline; existing literature proofs need not be formalized",
        "sources": sources, "facts": facts, "rules": rules,
        "audit_limitations": classical["cutoff_limitations"] + quantum["notes"] + [
            "The v0.4.0 domain dossiers extend the full context theory. Only the explicit scored roster earns points; background endpoints can still support consequences.",
            "New model equivalences and historical classifications are audited separately from successful Lean compilation. See the versioned review and release-wide assessment.",
        ],
    }
    for item in [*facts, *rules, *complements]:
        if not item.get("source_ids") or not set(item["source_ids"]) <= source_ids:
            raise ValueError(f"Missing research source: {item}")
        atoms = [*item["premises"], *item["conclusions"]] if "premises" in item else [item]
        if any(atom["left"] not in ids or atom["right"] not in ids for atom in atoms):
            raise ValueError(f"Unknown research endpoint: {item}")
    write("data/classes.json", catalog)
    write("data/knowledge.json", knowledge)
    runpy.run_path(str(ROOT / "scripts/generate_catalog.py"), run_name="__main__")
    runpy.run_path(str(ROOT / "scripts/generate_schemas.py"), run_name="__main__")
    paths = sorted([
        ROOT / "lean/InclusionBench.lean", ROOT / "quantum/InclusionQuantum.lean",
        *ROOT.glob("lean/InclusionBench/*.lean"),
        *ROOT.glob("quantum/InclusionQuantum/*.lean"),
        ROOT / "lean/lean-toolchain", ROOT / "quantum/lake-manifest.json",
    ])
    files = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in paths}
    write("data/formalization.json", {
        "schema_version": 1,
        "status": "canonical operational definitions supplied; existing model-equivalence and literature results are trusted inputs",
        "definition_count": len(complete),
        "core_definition_count": len(defined),
        "extension_definition_count": len(complete - defined),
        "scored_class_count": len(catalog.get("scored_class_ids", ids)),
        "files": files,
        "bundle_sha256": hashlib.sha256(json.dumps(
            files, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    })


if __name__ == "__main__":
    build()
