"""Compare optional 55/56 endpoint sets on selected pruning hypotheses.

This is a targeted follow-up to audit_pruning.py, not an exhaustive experiment
for either alternative. It reuses that experiment's zero-credit hypotheses and
nine illustrative results. Both alternatives use the identical context theory.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from audit_pruning import ROOT, Benchmark, Atom, assumed_closure


def build():
    benchmark = Benchmark(ROOT)
    source_path = ROOT / "research/v0.4.0/pruning-audit.json"
    source_bytes = source_path.read_bytes()
    source = json.loads(source_bytes)
    if source["dataset_sha256"] != benchmark.digest:
        raise ValueError("Regenerate the full pruning audit against this dataset first")
    active = set(benchmark.ids)
    restore55 = {"FewP", "LWPP", "WPP", "coUP", "coRP"}
    restore56 = restore55 | {"coQMA"}
    rosters = {"selected50": active, "optional55": active | restore55,
               "optional56": active | restore56}
    assert [len(roster) for roster in rosters.values()] == [50, 55, 56]
    context_candidates = {
        (a, b) for a in benchmark.context_ids for b in benchmark.context_ids
        if not any(Atom(r, a, b) in benchmark.baseline.proofs
                   for r in ("inclusion", "separation", "independence"))
    }
    candidates = {name: {pair for pair in context_candidates
                         if set(pair) <= roster}
                  for name, roster in rosters.items()}
    assert candidates["selected50"] == benchmark.unresolved
    cache = {}

    def evaluate(claims):
        key = tuple(sorted((c["relation"], c["left"], c["right"]) for c in claims))
        if key not in cache:
            closure = assumed_closure(benchmark, [Atom(*values) for values in key])
            pairs = {atom.pair for atom in closure.proofs if atom.pair in context_candidates}
            cache[key] = {
                "all_context_resolutions": len(pairs),
                "scores": {name: len(pairs & possible) for name, possible in candidates.items()},
                "retained_examples": {
                    name: [list(pair) for pair in sorted(pairs & possible)[:8]]
                    for name, possible in candidates.items()},
            }
        return cache[key]

    zero_rows = []
    for row in source["zero_credit_hypotheses"]:
        claim = {key: row[key] for key in ("relation", "left", "right")}
        result = evaluate([claim])
        assert result["scores"]["selected50"] == 0
        zero_rows.append({**claim, **result,
                          "direct_pair_scored": {
                              name: (claim["left"], claim["right"]) in possible
                              for name, possible in candidates.items()}})
    examples = []
    for row in source["representative_results"]:
        result = evaluate(row["claims"])
        assert result["scores"]["selected50"] == row["scored_resolutions"]
        assert result["all_context_resolutions"] == row["all_context_resolutions"]
        examples.append({"title": row["title"], "claims": row["claims"], **result})
    result = {
        "schema_version": 1,
        "status": "targeted_alternative_roster_experiment",
        "dataset_sha256": benchmark.digest,
        "source_exhaustive_experiment": {
            "path": str(source_path.relative_to(ROOT)),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
        },
        "context_class_count": len(benchmark.context_ids),
        "all_context_candidate_pairs": len(context_candidates),
        "distinct_assumption_sets_tested": len(cache),
        "rosters": {name: {
            "scored_class_count": len(roster),
            "restored_classes": sorted(roster - active),
            "background_classes": sorted(set(benchmark.context_ids) - roster),
            "scored_candidate_pairs": len(candidates[name]),
            "candidate_slots_restored_relative_to_50": len(candidates[name] - benchmark.unresolved),
            "inactive_candidate_pairs_and_direct_independence_slots": len(context_candidates - candidates[name]),
            "former_zero_credit_hypotheses_now_scoring": sum(row["scores"][name] > 0 for row in zero_rows),
            "former_zero_credit_claims_with_direct_endpoint_point": sum(row["direct_pair_scored"][name] for row in zero_rows),
        } for name, roster in rosters.items()},
        "former_zero_credit_hypotheses": zero_rows,
        "representative_results": examples,
        "limitations": [
            "Only the full 50-endpoint pruning experiment was exhaustive; this adjunct tests its zero-credit hypotheses and nine representative results.",
            "Scores count consequences in the same encoded theory and are neither importance weights nor breakthrough probabilities.",
            "Restoring a consequence does not restore a removed claim's direct point or independence certificate.",
            "Candidate slot counts cover this 61-class context only, not the full landscape of important total-language complexity classes.",
            "The 55/56 options exceed the user's original approximate 40–50 target and are optional comparisons, not adopted rosters.",
        ],
    }
    if Benchmark(ROOT).digest != benchmark.digest:
        raise ValueError("Dataset changed during the comparison; rerun before saving")
    output = ROOT / "research/v0.4.0/pruning-alternatives.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"dataset_sha256": benchmark.digest, "distinct_assumption_sets_tested": len(cache),
                      "rosters": result["rosters"]}, indent=2))


if __name__ == "__main__":
    build()
