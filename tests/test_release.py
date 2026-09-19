import json
import unittest

from inclusion_bench.benchmark import Benchmark, ROOT


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = Benchmark()
        cls.site = json.loads((ROOT / "web/benchmark.json").read_text())

    def test_site_matches_dataset(self):
        self.assertEqual(self.site["dataset_sha256"], self.b.digest)
        self.assertEqual(len(self.site["pairs"]), 2500)
        self.assertEqual(self.site["counts"], self.b.matrix()["counts"])
        self.assertEqual(self.site["leaderboard"], [])
        self.assertEqual(self.site["baseline"]["score"], 0)
        suite = json.loads((ROOT / "evaluation/tasks.json").read_text())
        self.assertEqual(len(suite["tasks"]), len(self.b.unresolved))
        self.assertEqual(self.site["taskset_sha256"], suite["taskset_sha256"])

    def test_shared_proof_graphs_are_complete_and_acyclic(self):
        baseline = self.site["baseline_proof_steps"]
        for scenario in self.site["scenarios"]:
            nodes = baseline + scenario["proof_steps"]
            seen = set()
            for node in nodes:
                self.assertNotIn(node["id"], seen)
                self.assertTrue(set(node["parents"]) <= seen)
                seen.add(node["id"])
            pairs = set()
            for resolution in scenario["resolutions"]:
                pair = resolution["left"], resolution["right"]
                self.assertIn(pair, self.b.unresolved)
                self.assertNotIn(pair, pairs)
                pairs.add(pair)
                self.assertIn(resolution["proof"]["target"], seen)
            self.assertEqual(scenario["score"], len(pairs))
            self.assertEqual(scenario["official_points"], 0)

    def test_coverage_claims_only_use_catalog_classes(self):
        coverage = self.site["coverage"]
        self.assertEqual(len(coverage["scenarios"]), 50)
        for scenario in coverage["scenarios"]:
            for claim in scenario["claims"]:
                self.assertIn(claim["left"], self.b.ids)
                self.assertIn(claim["right"], self.b.ids)


if __name__ == "__main__":
    unittest.main()
