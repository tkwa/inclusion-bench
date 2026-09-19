from __future__ import annotations

import hashlib
import json
import sys
import re
from datetime import date
from pathlib import Path

from .engine import Atom, Closure, InvalidEvidence, Rule

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "data" / "classes.json").exists():
    ROOT = Path(sys.prefix) / "share" / "inclusion-bench"


def read_json(path: Path):
    return json.loads(path.read_text())


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


class Benchmark:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.documents = {name: read_json(root / "data" / f"{name}.json") for name in ("classes", "knowledge", "policy")}
        self.catalog = self.documents["classes"]
        self.knowledge = self.documents["knowledge"]
        self.policy = self.documents["policy"]
        self.digest = canonical_hash(self.documents)
        self.classes = self.catalog["classes"]
        self.ids = [c["id"] for c in self.classes]
        if len(self.ids) != len(set(self.ids)):
            raise InvalidEvidence("Duplicate class identifiers")
        if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name) for name in self.ids):
            raise InvalidEvidence("Class identifiers must be safe ASCII Lean/Python names")
        self.sources = {s["id"]: s for s in self.knowledge["sources"]}
        if len(self.sources) != len(self.knowledge["sources"]):
            raise InvalidEvidence("Duplicate source identifiers")
        cutoff = date.fromisoformat(self.policy["cutoff"])
        for source in self.sources.values():
            if source.get("publication_date"):
                parts = source["publication_date"].split("-")
                earliest = date(*[int(x) for x in parts + ["01"] * (3 - len(parts))])
                if earliest > cutoff:
                    raise InvalidEvidence(f"Post-cutoff baseline source: {source['id']}")
            if source.get("year", 0) > cutoff.year:
                raise InvalidEvidence(f"Post-cutoff source year: {source['id']}")
        self.rules = []
        names = set()
        for item in self.knowledge["facts"] + self.knowledge["rules"]:
            if item["id"] in names:
                raise InvalidEvidence(f"Duplicate fact/rule id: {item['id']}")
            names.add(item["id"])
            if not item.get("source_ids") or not set(item["source_ids"]) <= self.sources.keys():
                raise InvalidEvidence(f"Missing citation for {item['id']}")
        for raw in self.knowledge["rules"]:
            for i, conclusion in enumerate(raw["conclusions"]):
                self.rules.append(Rule(raw["id"] + f"/{i}", tuple(Atom.read(p) for p in raw["premises"]), Atom.read(conclusion), tuple(raw["source_ids"])))
        self.complements = {}
        for item in self.catalog["complements"]:
            if not item.get("source_ids") or not set(item["source_ids"]) <= self.sources.keys():
                raise InvalidEvidence(f"Missing complement citation: {item}")
            a, b = item["left"], item["right"]
            if a in self.complements and self.complements[a] != b:
                raise InvalidEvidence(f"Ambiguous complement: {a}")
            if b in self.complements and self.complements[b] != a:
                raise InvalidEvidence(f"Ambiguous complement: {b}")
            self.complements[a] = b
            self.complements[b] = a
        self.baseline = self.closure()
        self.unresolved = {(a, b) for a in self.ids for b in self.ids if not any(Atom(r, a, b) in self.baseline.proofs for r in ("inclusion", "separation", "independence"))}

    def closure(self, claims=()) -> Closure:
        closure = Closure(self.ids, self.rules, self.complements)
        for raw in self.knowledge["facts"]:
            closure.add(Atom.read(raw), "baseline:" + raw["id"], source_ids=raw["source_ids"])
        # Complete baseline first so explanations don't credit known facts to a submission.
        closure.saturate()
        for raw in claims:
            closure.add(Atom.read(raw), "submission")
        return closure.saturate()

    def score(self, submission: dict, official: bool = False) -> dict:
        claims = submission.get("claims")
        if not isinstance(claims, list):
            raise InvalidEvidence("Submission must contain a claims list")
        if len(claims) > 2500:
            raise InvalidEvidence("At most 2,500 claims are allowed")
        if official:
            # A draft never awards public points, irrespective of submitted metadata.
            if self.policy["release_stage"] != "certified":
                raise InvalidEvidence("Official scoring is disabled: cutoff audit and semantic Lean formalization are incomplete. Use scenario mode to inspect consequences.")
            manifest = read_json(self.root / "data" / "eligibility.json")
            reviews = read_json(self.root / "data" / "reviews.json")
            if manifest.get("dataset_sha256") != self.digest or manifest.get("status") != "certified":
                raise InvalidEvidence("No certified eligibility manifest for this dataset")
            review = next((r for r in reviews if r.get("submission_sha256") == canonical_hash(submission) and r.get("dataset_sha256") == self.digest and r.get("status") == "accepted"), None)
            if review is None:
                raise InvalidEvidence("No accepted maintainer review for this exact submission and dataset")
            pairs = [(p["left"], p["right"]) for p in manifest["pairs"]]
            if len(pairs) != len(set(pairs)) or set(pairs) != {(a, b) for a in self.ids for b in self.ids}:
                raise InvalidEvidence("Certified manifest must classify every ordered pair exactly once")
            eligible = {(p["left"], p["right"]) for p in manifest["pairs"] if p["status"] == "open_at_cutoff"}
            if not eligible <= self.unresolved:
                raise InvalidEvidence("Known baseline pairs cannot be eligible")
            if any(p["status"] not in {"open_at_cutoff", "inclusion", "separation", "independence"} for p in manifest["pairs"]):
                raise InvalidEvidence("Certified manifest contains unreviewed pairs")
        else:
            eligible = self.unresolved
        result = self.closure(claims)
        awarded = sorted((a for a in result.proofs if a.pair in eligible), key=lambda a: a.pair)
        if len({a.pair for a in awarded}) != len(awarded):
            raise InvalidEvidence("Multiple resolutions of one ordered pair")
        return {
            "mode": "official" if official else "scenario",
            "score": len(awarded),
            "official_points": len(awarded) if official else 0,
            "eligible_pair_count": len(eligible),
            "dataset_sha256": self.digest,
            "cutoff": self.policy["cutoff"],
            "warning": None if official else "Hypothetical impact on a provisional dataset; claims are assumed, not verified. This is not an official score.",
            "resolutions": [{**a.json(), "proof": result.explanation(a)} for a in awarded],
        }

    def matrix(self) -> dict:
        counts = {"inclusion": 0, "separation": 0, "independence": 0, "unreviewed": 0}
        pairs = []
        for a in self.ids:
            for b in self.ids:
                known = next((r for r in ("inclusion", "separation", "independence") if Atom(r, a, b) in self.baseline.proofs), "unreviewed")
                counts[known] += 1
                pairs.append({"left": a, "right": b, "status": known, "eligible": False})
        return {"dataset_sha256": self.digest, "status": "draft", "cutoff": self.policy["cutoff"], "counts": counts, "pairs": pairs}
