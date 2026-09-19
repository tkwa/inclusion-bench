import unittest
import json
import shutil
import tempfile
from pathlib import Path

from inclusion_bench.benchmark import Benchmark, canonical_hash
from inclusion_bench.engine import Atom, Contradiction, InvalidEvidence


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = Benchmark()

    def test_roster_and_baseline(self):
        self.assertEqual(len(self.b.ids), 50)
        self.assertEqual(sum(self.b.matrix()["counts"].values()), 2500)
        self.assertIn(Atom("inclusion", "P", "NP"), self.b.baseline.proofs)
        self.assertNotIn(Atom("inclusion", "Ppoly", "EXP"), self.b.baseline.proofs)
        self.assertIn(Atom("separation", "AC0", "EXP"), self.b.baseline.proofs)

    def test_known_facts_and_empty_submission_score_zero(self):
        for claims in [[], [{"relation": "inclusion", "left": "P", "right": "NP"}]]:
            self.assertEqual(self.b.score({"claims": claims})["score"], 0)

    def test_user_example_implies_p_strictly_below_pspace(self):
        claims = [{"relation": "inclusion", "left": "BPP", "right": "NP"}, {"relation": "separation", "left": "NP", "right": "BPP"}]
        result = self.b.score({"claims": claims})
        resolved = {(r["relation"], r["left"], r["right"]) for r in result["resolutions"]}
        self.assertIn(("separation", "PSPACE", "P"), resolved)
        self.assertGreater(result["score"], 1)
        self.assertEqual(result["official_points"], 0)

    def test_duplicate_claims_do_not_multiply_score(self):
        c = {"relation": "separation", "left": "NP", "right": "P"}
        self.assertEqual(self.b.score({"claims": [c]})["score"], self.b.score({"claims": [c, c]})["score"])

    def test_official_admission_fails_closed(self):
        with self.assertRaisesRegex(InvalidEvidence, "disabled"):
            self.b.score({"claims": [], "accepted": True, "proof_verified": True}, official=True)

    def test_contradiction_with_baseline_rejected(self):
        with self.assertRaises(Contradiction):
            self.b.score({"claims": [{"relation": "separation", "left": "P", "right": "NP"}]})

    def test_cutoff_unresolved_is_not_called_certified_open(self):
        self.assertTrue(all(not p["eligible"] for p in self.b.matrix()["pairs"]))
        self.assertNotIn("open_at_cutoff", {p["status"] for p in self.b.matrix()["pairs"]})

    def test_karp_lipton_consequence_and_contrapositive(self):
        c = self.b.closure([{"relation": "inclusion", "left": "NP", "right": "Ppoly"}])
        self.assertIn(Atom("inclusion", "PH", "Sigma2P"), c.proofs)
        d = self.b.closure([{"relation": "separation", "left": "PH", "right": "Sigma2P"}])
        self.assertIn(Atom("separation", "NP", "Ppoly"), d.proofs)

    def test_future_official_branch_rejects_known_pairs_in_manifest(self):
        # Isolated fixture tests validation only; it does not certify the real dataset.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(self.b.root / "data", root / "data")
            policy = json.loads((root / "data/policy.json").read_text())
            policy["release_stage"] = "certified"
            (root / "data/policy.json").write_text(json.dumps(policy))
            b = Benchmark(root)
            manifest = b.matrix()
            manifest["status"] = "certified"
            for pair in manifest["pairs"]:
                if pair["status"] == "unreviewed":
                    pair["status"] = "open_at_cutoff"
                if pair["left"] == "P" and pair["right"] == "NP":
                    pair["status"] = "open_at_cutoff"
            (root / "data/eligibility.json").write_text(json.dumps(manifest))
            submission = {"claims": []}
            reviews = [{"status": "accepted", "submission_sha256": canonical_hash(submission), "dataset_sha256": b.digest}]
            (root / "data/reviews.json").write_text(json.dumps(reviews))
            with self.assertRaisesRegex(InvalidEvidence, "Known baseline"):
                b.score(submission, official=True)

    def test_future_official_branch_rejects_unreviewed_or_duplicate_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(self.b.root / "data", root / "data")
            policy = json.loads((root / "data/policy.json").read_text())
            policy["release_stage"] = "certified"
            (root / "data/policy.json").write_text(json.dumps(policy))
            b = Benchmark(root)
            manifest = b.matrix()
            manifest["status"] = "certified"
            submission = {"claims": []}
            (root / "data/reviews.json").write_text(json.dumps([{"status": "accepted", "submission_sha256": canonical_hash(submission), "dataset_sha256": b.digest}]))
            (root / "data/eligibility.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(InvalidEvidence, "unreviewed"):
                b.score(submission, official=True)
            manifest["pairs"].append(manifest["pairs"][0])
            (root / "data/eligibility.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(InvalidEvidence, "exactly once"):
                b.score(submission, official=True)


if __name__ == "__main__":
    unittest.main()
