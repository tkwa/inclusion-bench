"""Actual bounded-container regressions for large candidate proof exports."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from inclusion_bench.benchmark import Benchmark
from inclusion_bench.proofcheck import verify_proof
from tests.proofcheck_large_fixture import large_export_source, large_literature_export_source


def raw_export_source(mebibytes, byte=120):
    """Bypass the exporter deliberately, as an adversarial candidate can."""
    return f'''#eval do
  let handle ← IO.FS.Handle.mk "/work/proof-export.json" .write
  let chunk := ByteArray.mk (Array.replicate (1024 * 1024) ({byte} : UInt8))
  for _ in [:{mebibytes}] do handle.write chunk
  handle.flush
  (IO.Process.exit 0 : IO Unit)
'''


@unittest.skipUnless(os.environ.get("INCLUSION_PROOFCHECK_INTEGRATION") == "1",
                     "set INCLUSION_PROOFCHECK_INTEGRATION=1 for actual isolated Ubuntu tests")
class LargeProofcheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = Benchmark()
        config = os.environ.get("INCLUSION_PROOFCHECK_CONFIG")
        cls.runtime = json.loads(Path(config).read_text()) if config else {}
        cls.runtime["timeout_seconds"] = 600
        cls.claim = {"relation": "inclusion", "left": "P", "right": "P", "theorem": "submitted"}

    def check_source(self, source, status, literature_requests=None):
        with tempfile.TemporaryDirectory(prefix="large-proofcheck-") as directory:
            path = Path(directory) / "proof.lean"
            path.write_text(source)
            report = verify_proof(self.benchmark, path, [self.claim],
                                  literature_requests=literature_requests or [], **self.runtime)
        runtime = report.get("runtime", {})
        print(json.dumps({"case": self._testMethodName, "status": report["status"],
                          "proof_export_bytes": runtime.get("proof_export_bytes"),
                          "stage_wall_seconds": runtime.get("stage_wall_seconds", report.get("stage_wall_seconds"))}),
              flush=True)
        self.assertEqual(report["status"], status, report.get("reason", "") + report.get("log", ""))
        self.assertEqual(report["official_points"], 0)
        return report

    def test_valid_export_above_32_mib(self):
        report = self.check_source(large_export_source(), "verified")
        self.assertGreater(report["runtime"]["proof_export_bytes"], 32 * 1024 * 1024)
        self.assertEqual(report["runtime"]["proof_export_limit_bytes"], 256 * 1024 * 1024)
        self.assertEqual(report["runtime"]["work_tmpfs_bytes"], 1024 * 1024 * 1024)
        self.assertEqual(report["declaration_count"], 131)

    def test_valid_export_near_256_mib(self):
        report = self.check_source(large_export_source(count=1000), "verified")
        self.assertGreater(report["runtime"]["proof_export_bytes"], 250 * 1024 * 1024)
        self.assertLessEqual(report["runtime"]["proof_export_bytes"], 256 * 1024 * 1024)
        self.assertEqual(report["declaration_count"], 1002)

    def test_malformed_large_json_rejected_inside_auditor(self):
        report = self.check_source(raw_export_source(33), "rejected")
        self.assertEqual(report["runtime"]["proof_export_bytes"], 33 * 1024 * 1024)
        self.assertIn("kernel_replay", report["runtime"]["stage_wall_seconds"])

    def test_invalid_utf8_large_export_rejected_inside_auditor(self):
        report = self.check_source(raw_export_source(33, 255), "rejected")
        self.assertEqual(report["runtime"]["proof_export_bytes"], 33 * 1024 * 1024)
        self.assertIn("kernel_replay", report["runtime"]["stage_wall_seconds"])

    def test_export_over_256_mib_rejected_before_auditor(self):
        report = self.check_source(raw_export_source(257), "rejected")
        self.assertIn("stdout exceeds 268435456 bytes", report["reason"])
        self.assertNotIn("kernel_replay", report["stage_wall_seconds"])

    def test_large_literature_context_rejected_without_truncation(self):
        request = {"name": "Literature.large", "statement": "TEST-ONLY reflexive inclusion.",
                   "rationale": "Exercise the exact literature-context report budget with synthetic local definitions.",
                   "sources": [{"title": "Computational Complexity: A Modern Approach",
                                "url": "https://theory.cs.princeton.edu/complexity/book.pdf",
                                "locator": "Chapter 1: complexity classes and reflexivity of inclusion.",
                                "publication_date": "2009"}]}
        report = self.check_source(large_literature_export_source(), "rejected", [request])
        self.assertIn("Audit report exceeds byte limit", report["reason"])
        self.assertGreater(report["runtime"]["proof_export_bytes"], 32 * 1024 * 1024)
        self.assertFalse(report.get("literature_dependencies"))


if __name__ == "__main__":
    unittest.main()
