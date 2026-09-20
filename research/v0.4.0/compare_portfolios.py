"""Measure old-question losses under simultaneous demotions, without ranking them.

Run against the frozen v0.3.1 checkout. Added-class facts are deliberately absent:
these results are a lower bound on surviving old-question consequence coverage,
not projected scores on any revised dataset. Independence does not propagate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark, canonical_hash
from inclusion_bench.engine import Atom, Closure

BASE = "6cf78ea6cf5edd43e5c327a90ba54765871cfd552800637cbecfbc646eef7742"
COMMON_DEMOTIONS = ["AC0", "coUP", "coMA", "coAM", "coQMA", "FewP", "LWPP", "WPP"]
COMMON_ADDITIONS = ["BPL", "UL", "ExistsR", "PSharpP", "CH", "QMA2", "StoqMA", "QSZK"]
OPTIONS = [
    ("A", [], []),
    ("B", ["coRP", "E"], ["PL", "BQL"]),
    ("B-NE", ["coRP", "NE"], ["PL", "BQL"]),
    ("B-uniform", ["coRP", "E", "Pi2P"], ["PL", "BQL", "UniformNC1"]),
    ("B-symmetric", ["coRP", "E", "Pi2P"], ["PL", "BQL", "S2P"]),
    ("B-physics", ["coRP", "E", "Pi2P"], ["PL", "BQL", "QPCP"]),
]


def compare(benchmark: Benchmark):
    if benchmark.digest != BASE:
        raise ValueError("This comparison requires the exact frozen v0.3.1 dataset")
    portfolios = []
    for name, extra_removed, extra_added in OPTIONS:
        removed = COMMON_DEMOTIONS + extra_removed
        added = COMMON_ADDITIONS + extra_added
        kept = set(benchmark.ids) - set(removed)
        assert len(kept) + len(added) == 50
        lost_pairs = benchmark.unresolved - {(a, b) for a in kept for b in kept}
        portfolios.append({
            "id": name, "demoted": removed, "added": added,
            "retained_old_ids": sorted(kept), "scored_class_count": 50,
            "old_open_pairs_without_two_scored_endpoints": len(lost_pairs),
            "ordinary_assumptions_tested": 0,
            "assumptions_without_any_retained_old_open_consequence": [],
            "surviving_consequence_count_histogram": Counter(),
        })
    to_test = sorted({pair for p in portfolios for pair in benchmark.unresolved
                      if pair[0] in p["demoted"] or pair[1] in p["demoted"]})
    for index, (left, right) in enumerate(to_test):
        for relation in ("inclusion", "separation"):
            claim = Atom(relation, left, right)
            closure = Closure(benchmark.context_ids, benchmark.rules, benchmark.complements)
            # Existing proof records are immutable during saturation. Reuse the
            # already-saturated baseline to avoid repeating the same computation.
            closure.proofs = dict(benchmark.baseline.proofs)
            closure.add(claim, "submission")
            closure.saturate()
            consequences = {a.pair for a in closure.proofs if a.pair in benchmark.unresolved}
            for p in portfolios:
                if left not in p["demoted"] and right not in p["demoted"]:
                    continue
                kept = set(p["retained_old_ids"])
                count = sum(a in kept and b in kept for a, b in consequences)
                p["ordinary_assumptions_tested"] += 1
                p["surviving_consequence_count_histogram"][count] += 1
                if not count:
                    p["assumptions_without_any_retained_old_open_consequence"].append(claim.json())
        if (index + 1) % 100 == 0:
            print(json.dumps({"old_pairs_tested": index + 1, "total": len(to_test)}), flush=True)
    for p in portfolios:
        p["surviving_consequence_count_histogram"] = {
            str(k): v for k, v in sorted(p["surviving_consequence_count_histogram"].items())}
        p["no_retained_consequence_count_by_relation"] = dict(Counter(
            item["relation"] for item in p["assumptions_without_any_retained_old_open_consequence"]))
    return {
        "schema_version": 1, "status": "scientific_selection_comparison_not_release_audit",
        "baseline_dataset_sha256": benchmark.digest,
        "baseline_classes_sha256": canonical_hash(benchmark.catalog),
        "baseline_knowledge_sha256": canonical_hash(benchmark.knowledge),
        "limitations": [
            "Counts describe the encoded ordinary implication library, not scientific importance.",
            "Added-class facts are absent; some losses may acquire consequences in the revised graph.",
            "Each tested assumption resolves one old open pair; compound results can behave differently.",
            "Independence is excluded and must not be propagated as noninclusion.",
            "No tractability estimate, literature-openness judgment, or new-class audit is supplied.",
        ], "portfolios": portfolios,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("portfolio-comparison.json"))
    args = parser.parse_args()
    result = compare(Benchmark(args.baseline_root))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({p["id"]: p["no_retained_consequence_count_by_relation"]
                      for p in result["portfolios"]}), flush=True)
