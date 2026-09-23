import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark
from inclusion_bench.cli import main
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.submissions import (
    check_submission, find_theorems, format_theorems, init_submission, submission_runtime,
)


class SubmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = Benchmark()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "submission"
        self.claims = [{"relation": "inclusion", "left": "NP", "right": "P"},
                       {"relation": "separation", "left": "PSPACE", "right": "P"}]

    def initialize(self):
        return init_submission(self.benchmark, self.directory, self.claims)

    def run_cli(self, *arguments):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["inclusion-bench", *map(str, arguments)]), \
                patch("inclusion_bench.cli.Benchmark", return_value=self.benchmark), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = main()
        return code, output.getvalue(), errors.getvalue()

    def test_scaffold_binds_mixed_claims_to_exact_unconditional_targets(self):
        result = self.initialize()
        claims = json.loads((self.directory / "claims.json").read_text())["claims"]
        self.assertEqual(claims, [{**claim, "theorem": f"Submission.result_{i}"}
                                  for i, claim in enumerate(self.claims, 1)])
        body = (self.directory / "proof.lean").read_text()
        self.assertIn("theorem result_1 : Includes NP P := by", body)
        self.assertIn("theorem result_2 : NonIncludes PSPACE P := by", body)
        self.assertEqual(body.count("  sorry"), 2)
        self.assertNotIn("axiom", body)
        self.assertEqual(json.loads((self.directory / "literature.json").read_text()), {"requests": []})
        self.assertEqual(result["dataset_sha256"], self.benchmark.digest)
        guide = (self.directory / "AGENTS.md").read_text()
        self.assertIn("axiom Literature.my_dependency : TYPE", guide)
        self.assertIn("needs_literature_review", guide)

    def test_short_class_search_does_not_match_input_or_sharpP(self):
        from inclusion_bench.submissions import find_theorems
        records = [{"name": "input_helper", "statement": "an input word"},
                   {"name": "np_of_relation", "statement": "NP witness"},
                   {"name": "sharpP_mul", "statement": "counting"},
                   {"name": "rp_lemma", "statement": "RP computation"}]
        with patch("inclusion_bench.submissions._theorem_catalog", return_value=records):
            self.assertEqual(find_theorems(self.benchmark, "NP"), [records[1]])
            self.assertEqual(find_theorems(self.benchmark, "RP"), [records[3]])

    def test_bad_claims_never_create_a_partial_project(self):
        for claims in ([], self.claims[:1] * 2,
                       [{"relation": "inclusion", "left": "invented", "right": "P"}],
                       [{"relation": "independence", "left": "NP", "right": "P"}]):
            with self.subTest(claims=claims), self.assertRaises(InvalidEvidence):
                init_submission(self.benchmark, self.directory, claims)
            self.assertFalse(self.directory.exists())

    def test_scaffold_preserves_existing_work_and_dangling_links(self):
        self.directory.mkdir()
        proof = self.directory / "proof.lean"
        proof.write_text("existing proof")
        with self.assertRaisesRegex(InvalidEvidence, "preserving"):
            self.initialize()
        self.assertEqual(proof.read_text(), "existing proof")
        self.assertFalse((self.directory / "claims.json").exists())
        proof.unlink()
        proof.symlink_to("missing.lean")
        with self.assertRaisesRegex(InvalidEvidence, "preserving"):
            self.initialize()
        self.assertTrue(proof.is_symlink())

    def test_runtime_defaults_are_local_and_overrides_are_explicit(self):
        defaults = submission_runtime(self.benchmark, self.directory)
        self.assertIsNone(defaults["host"])
        self.assertEqual(defaults["remote_root"], str(self.benchmark.root.resolve()))
        self.assertEqual(defaults["image"], "ubuntu:22.04")
        config = self.directory / ".tools/proofcheck-runtime.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"host": "my-verifier", "remote_root": "/srv/benchmark",
                                      "image": "ubuntu:22.04", "timeout_seconds": 300}))
        resolved = submission_runtime(self.benchmark, self.directory, overrides={"host": None, "timeout_seconds": 180})
        self.assertIsNone(resolved["host"])
        self.assertEqual(resolved["remote_root"], "/srv/benchmark")
        self.assertEqual(resolved["timeout_seconds"], 180)
        explicit = Path(self.temporary.name) / "runtime.json"
        explicit.write_text(json.dumps({"host": "explicit-host", "toolchain_path": "/srv/lean"}))
        resolved = submission_runtime(self.benchmark, self.directory, explicit)
        self.assertEqual(resolved["host"], "explicit-host")
        self.assertEqual(resolved["toolchain_path"], "/srv/lean")

    def test_runtime_cannot_override_proof_inputs(self):
        config = Path(self.temporary.name) / "runtime.json"
        for value in ({"claims": []}, {"literature_requests": []}, {"host": ""}, []):
            config.write_text(json.dumps(value))
            with self.subTest(value=value), self.assertRaises(InvalidEvidence):
                submission_runtime(self.benchmark, self.directory, config)

    def test_check_passes_claims_requests_and_report_path_to_verifier(self):
        self.initialize()
        request = {"name": "Literature.test", "statement": "A cited statement", "sources": []}
        (self.directory / "literature.json").write_text(json.dumps({"requests": [request]}))
        response = {"status": "needs_literature_review", "official_points": 0,
                    "literature_dependencies": [{"name": "Literature.test"}]}
        with patch("inclusion_bench.submissions.verify_proof", return_value=response) as verify:
            result = check_submission(self.benchmark, self.directory)
        self.assertEqual(result, response)
        args, kwargs = verify.call_args
        self.assertEqual(args[1], self.directory / "proof.lean")
        self.assertEqual(args[2][0]["theorem"], "Submission.result_1")
        self.assertEqual(kwargs["literature_requests"], [request])
        self.assertEqual(kwargs["report_path"], self.directory / "proof-report.json")
        self.assertIsNone(kwargs["host"])

    def test_malformed_literature_does_not_reach_verifier(self):
        self.initialize()
        with patch("inclusion_bench.submissions.verify_proof") as verify:
            for document in ([], {}, {"requests": "not a list"}):
                (self.directory / "literature.json").write_text(json.dumps(document))
                with self.subTest(document=document), self.assertRaisesRegex(InvalidEvidence, "requests array"):
                    check_submission(self.benchmark, self.directory)
            verify.assert_not_called()

    def test_theorem_search_preserves_citations_and_support_metadata(self):
        catalog = [{"name": "Baseline.p_np", "statement": "Includes P NP", "source_ids": ["textbook"]},
                   {"name": "Literature.counting", "statement": "Counting statement",
                    "sources": [{"title": "Example paper", "locator": "Theorem 5"}], "review_sha256": "abc"}]
        with patch("inclusion_bench.submissions._theorem_catalog", return_value=catalog):
            self.assertEqual(find_theorems(self.benchmark, "EXAMPLE theorem 5"), [catalog[1]])
            self.assertEqual(find_theorems(self.benchmark), catalog)
            self.assertEqual(find_theorems(self.benchmark, "missing"), [])
        self.assertIn("Literature.counting", format_theorems([catalog[1]]))
        self.assertIn("Example paper", format_theorems([catalog[1]]))

    def test_cli_scaffold_and_pending_check_exit_status(self):
        code, output, errors = self.run_cli("submission-init", self.directory,
                                             "--claim", "inclusion", "NP", "P",
                                             "--claim", "separation", "PSPACE", "P")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(len(json.loads(output)["claims"]), 2)
        for status, expected in (("verified", 0), ("needs_literature_review", 1), ("rejected", 1), ("unavailable", 1)):
            with self.subTest(status=status), patch("inclusion_bench.submissions.verify_proof", return_value={"status": status}) as verify:
                code, output, errors = self.run_cli("check-submission", self.directory, "--local", "--timeout-seconds", "180")
                self.assertEqual(code, expected, errors)
                self.assertEqual(json.loads(output)["status"], status)
                self.assertEqual(verify.call_args.kwargs["timeout_seconds"], 180)
                self.assertIsNone(verify.call_args.kwargs["host"])

    def test_cli_catalog_json_and_review_forward_exact_records(self):
        catalog = [{"name": "Literature.test", "statement": "Prop", "sources": ["source"]}]
        with patch("inclusion_bench.submissions._theorem_catalog", return_value=catalog):
            code, output, errors = self.run_cli("theorems", "--search", "test", "--json")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(json.loads(output), catalog)
        review = {"schema_version": 1, "status": "accepted", "dependency": {"type_sha256": "abc"}}
        review_path = Path(self.temporary.name) / "review.json"
        review_path.write_text(json.dumps(review))
        module = types.ModuleType("inclusion_bench.literature")
        with patch.object(module, "record_literature_review", create=True, return_value={"recorded": True}) as record, \
                patch.dict(sys.modules, {"inclusion_bench.literature": module}):
            code, output, errors = self.run_cli("review-literature", review_path)
        self.assertEqual((code, errors), (0, ""))
        record.assert_called_once_with(self.benchmark, review)
        self.assertEqual(json.loads(output), {"recorded": True})


if __name__ == "__main__":
    unittest.main()
