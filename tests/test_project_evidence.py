"""Synthetic report fixtures exercise provenance only, never mathematical validity."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark, ROOT, canonical_hash
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.evaluation import evaluate_run, run_adapter, sha256_file, taskset
from inclusion_bench.proofbundle import load_proof_bundle
from inclusion_bench.proofevidence import validate_proof_evidence
from inclusion_bench.reviews import record_proof_review


class ProjectEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "data", self.root / "data")
        self.benchmark = Benchmark(self.root)
        self.directory = self.root / "run"
        self.project = self.directory / "attempt/submission"
        (self.project / "Lemmas").mkdir(parents=True)
        self.manifest = {"schema_version": 1, "entrypoint": "Main",
                         "files": ["Main.lean", "Lemmas/Basic.lean"]}
        self.write("submission.json", self.manifest)
        (self.project / "Main.lean").write_text("import Lemmas.Basic\n-- synthetic fixture, not a proof\n")
        (self.project / "Lemmas/Basic.lean").write_text("theorem fixture : True := True.intro\n")
        self.claim = {"relation": "separation", "left": "NP", "right": "P"}
        self.claims = [{**self.claim, "theorem": "Submission.result_1"}]
        self.write("claims.json", {"claims": self.claims})
        self.write("literature.json", {"requests": []})
        self.attempt = {"attempt_id": "attempt-1", "task_id": "inclusion.NP.P",
                        "status": "proof_candidate", "claims": [self.claim],
                        "literature_requests": [], "submission_manifest": "attempt/submission/submission.json",
                        "artifacts": []}
        self.seal()
        bundle = load_proof_bundle(self.project)
        self.bindings = {name: value * 64 for name, value in
                         (("semantics_sha256", "a"), ("checker_sha256", "b"), ("baseline_sha256", "c"))}
        self.report = {"status": "verified", "method": "lean4-data-only-fresh-kernel-replay",
                       "dataset_sha256": self.benchmark.digest, "claims": self.claims,
                       "proof_sha256": bundle.proof_sha256, "proof_project": bundle.metadata,
                       "literature_requests": [], **self.bindings}
        mocked = patch("inclusion_bench.proofcheck.verification_bindings", return_value=self.bindings)
        mocked.start()
        self.addCleanup(mocked.stop)

    def write(self, filename, value):
        (self.project / filename).write_text(json.dumps(value, indent=2) + "\n")

    def seal(self):
        self.attempt["artifacts"] = [{"path": path.relative_to(self.directory).as_posix(),
                                      "sha256": sha256_file(path)}
                                     for path in sorted(self.project.rglob("*")) if path.is_file()]

    def check(self, report=None, attempt=None):
        return validate_proof_evidence(self.benchmark, report or self.report,
                                       attempt or self.attempt, self.directory)

    def test_complete_project_binds_all_files_under_one_root(self):
        bound = self.check()
        self.assertEqual(bound["manifest"], self.attempt["submission_manifest"])
        self.assertEqual(bound["proof_sha256"], self.report["proof_sha256"])
        self.assertIn("Lemmas/Basic.lean", bound["proof_project"]["files"])
        without_pointer = {k: v for k, v in self.attempt.items() if k != "submission_manifest"}
        self.assertEqual(self.check(attempt=without_pointer), bound)

    def test_missing_sealed_helper_cannot_borrow_another_copy(self):
        helper = self.project / "Lemmas/Basic.lean"
        borrowed = self.directory / "elsewhere.lean"
        shutil.copyfile(helper, borrowed)
        self.attempt["artifacts"] = [a for a in self.attempt["artifacts"] if not a["path"].endswith("Basic.lean")]
        self.attempt["artifacts"].append({"path": "elsewhere.lean", "sha256": sha256_file(borrowed)})
        with self.assertRaisesRegex(InvalidEvidence, "not a sealed artifact"):
            self.check()

    def test_project_cannot_downgrade_to_entrypoint_only_or_helper_only(self):
        for name in ("Main.lean", "Lemmas/Basic.lean"):
            report = {k: v for k, v in self.report.items() if k != "proof_project"}
            report["proof_sha256"] = sha256_file(self.project / name)
            with self.subTest(name=name), self.assertRaisesRegex(InvalidEvidence, "complete project"):
                self.check(report=report)
            without_pointer = {k: v for k, v in self.attempt.items() if k != "submission_manifest"}
            with self.subTest(name=name, pointer=False), self.assertRaisesRegex(InvalidEvidence, "complete project"):
                self.check(report=report, attempt=without_pointer)

    def test_modified_helper_still_fails_when_new_bytes_are_sealed(self):
        (self.project / "Lemmas/Basic.lean").write_text("axiom fixture : False\n")
        self.seal()
        with self.assertRaisesRegex(InvalidEvidence, "verified snapshot"):
            self.check()

    def test_manifest_bytes_and_entrypoint_are_bound(self):
        for changed in (json.dumps(self.manifest), json.dumps({**self.manifest, "entrypoint": "Lemmas.Basic"})):
            (self.project / "submission.json").write_text(changed)
            self.seal()
            with self.subTest(changed=changed), self.assertRaises(InvalidEvidence):
                self.check()

    def test_named_manifest_cannot_be_replaced_with_identical_unrelated_copy(self):
        other = self.directory / "unrelated/submission"
        shutil.copytree(self.project, other)
        self.attempt["artifacts"] = [a for a in self.attempt["artifacts"] if not a["path"].endswith("submission.json")]
        self.attempt["artifacts"].extend({"path": p.relative_to(self.directory).as_posix(), "sha256": sha256_file(p)}
                                        for p in other.rglob("*") if p.is_file())
        with self.assertRaisesRegex(InvalidEvidence, "not a sealed artifact"):
            self.check()

    def test_metadata_must_be_sealed_and_match_the_report_and_attempt(self):
        original = copy.deepcopy(self.attempt)
        self.attempt["artifacts"] = [a for a in self.attempt["artifacts"] if not a["path"].endswith("claims.json")]
        with self.assertRaisesRegex(InvalidEvidence, "not a sealed artifact"):
            self.check()
        self.attempt = original
        self.write("claims.json", {"claims": [{**self.claims[0], "theorem": "Submission.other"}]})
        self.seal()
        with self.assertRaisesRegex(InvalidEvidence, "theorem mapping"):
            self.check()
        self.write("claims.json", {"claims": self.claims})
        self.seal()
        self.attempt["claims"] = [{**self.claim, "right": "PSPACE"}]
        with self.assertRaisesRegex(InvalidEvidence, "outside this attempt"):
            self.check()

    def test_citation_metadata_must_match_both_attempt_and_report(self):
        request = {"name": "Literature.fixture", "statement": "True", "rationale": "Synthetic fixture",
                   "sources": [{"title": "Fixture", "url": "https://example.com/paper", "locator": "Theorem 1",
                                "publication_date": "1994"}]}
        self.write("literature.json", {"requests": [request]})
        self.seal()
        with self.assertRaisesRegex(InvalidEvidence, "literature.json"):
            self.check()
        self.report["literature_requests"] = [request]
        with self.assertRaisesRegex(InvalidEvidence, "do not match this attempt"):
            self.check()
        self.attempt["literature_requests"] = [request]
        self.check()

    def test_source_symlink_and_duplicate_artifact_paths_fail(self):
        self.attempt["artifacts"].append(copy.deepcopy(self.attempt["artifacts"][0]))
        with self.assertRaisesRegex(InvalidEvidence, "distinct"):
            self.check()
        self.attempt["artifacts"].pop()
        helper = self.project / "Lemmas/Basic.lean"
        copy_path = self.directory / "helper-copy.lean"
        shutil.copyfile(helper, copy_path)
        helper.unlink()
        helper.symlink_to(copy_path)
        with self.assertRaisesRegex(InvalidEvidence, "symlink"):
            self.check()

    def test_legacy_single_file_and_unrelated_manifest_are_preserved(self):
        proof = self.directory / "legacy.lean"
        proof.write_text("-- legacy source fixture\n")
        unrelated = self.directory / "submission.json"
        unrelated.write_text('{"not": "a Lean project"}')
        attempt = {"artifacts": [{"path": p.name, "sha256": sha256_file(p)} for p in (proof, unrelated)]}
        bound = self.check(report={"source_sha256": sha256_file(proof)}, attempt=attempt)
        self.assertEqual(bound["kind"], "single-file")
        self.assertEqual(bound["path"], "legacy.lean")

    def run_manifest(self):
        run = {"schema_version": 1, "run_id": "project-test", "model": {"name": "fixture", "version": "test"},
               "track": "tool-assisted", "dataset_sha256": self.benchmark.digest,
               "taskset_sha256": taskset(self.benchmark)["taskset_sha256"], "budget": {"wall_time_seconds": 5},
               "started_at": "2026-09-22T00:00:00+00:00", "finished_at": "2026-09-22T00:00:01+00:00",
               "attempts": [self.attempt]}
        path = self.directory / "run.json"
        path.write_text(json.dumps(run))
        return path, run

    def accept_review(self):
        manifest, run = self.run_manifest()
        report_file = self.root / "synthetic-report.json"
        report_file.write_text(json.dumps(self.report))
        review = {"run_sha256": canonical_hash(run), "attempt_sha256": canonical_hash(self.attempt),
                  "attempt_id": self.attempt["attempt_id"], "status": "accepted", "reviewer": "TEST ONLY",
                  "rationale": "Synthetic provenance regression, not mathematical evidence",
                  "verified_claims": [self.claim], "proof_report": str(report_file)}
        record_proof_review(self.benchmark, manifest, review)
        return manifest

    def test_review_and_scoring_recheck_project_and_preserve_provenance(self):
        manifest = self.accept_review()
        result = evaluate_run(self.benchmark, manifest)
        proof = result["verified_claim_provenance"]["separation:NP:P"][0]["proof_source"]
        self.assertEqual(proof["proof_project"], self.report["proof_project"])
        registry = self.root / "data/ai_reviews.json"
        records = json.loads(registry.read_text())
        records[-1]["proof_verification"]["proof_project"]["files"].pop("Lemmas/Basic.lean")
        registry.write_text(json.dumps(records))
        with self.assertRaisesRegex(InvalidEvidence, "verified snapshot"):
            evaluate_run(self.benchmark, manifest)

    def test_scoring_rejects_stale_project_checker_and_pending_status(self):
        manifest = self.accept_review()
        registry = self.root / "data/ai_reviews.json"
        original = json.loads(registry.read_text())
        for field, value in (("checker_sha256", "0" * 64), ("status", "needs_literature_review")):
            records = copy.deepcopy(original)
            records[-1]["proof_verification"][field] = value
            registry.write_text(json.dumps(records))
            with self.subTest(field=field), self.assertRaises(InvalidEvidence):
                evaluate_run(self.benchmark, manifest)

    def test_review_rejects_incomplete_source_set(self):
        self.attempt["artifacts"] = [a for a in self.attempt["artifacts"] if not a["path"].endswith("Basic.lean")]
        with self.assertRaisesRegex(InvalidEvidence, "not a sealed artifact"):
            self.accept_review()

    def legacy_adapter(self, output, omit=None):
        script = "\n".join([
            "from pathlib import Path",
            "import json, shutil",
            "destination = Path.cwd() / 'project'",
            f"shutil.copytree({str(self.project)!r}, destination)",
            "artifacts = [p.relative_to(Path.cwd()).as_posix() for p in destination.rglob('*') if p.is_file()]",
            f"artifacts = [p for p in artifacts if not p.endswith({omit!r})]" if omit else "",
            f"print(json.dumps({{'status': 'proof_candidate', 'claims': [{self.claim!r}], "
            "'artifacts': artifacts, 'literature_requests': [], 'submission_manifest': 'project/submission.json'}))",
        ])
        return run_adapter(self.benchmark, [sys.executable, "-c", script], "fixture", "test-only",
                           ["inclusion.NP.P"], output, 5, "smoke-test")

    def test_legacy_adapter_preserves_and_seals_a_project_without_usage_fields(self):
        manifest = self.legacy_adapter(self.root / "legacy-project-run")
        attempt = json.loads(manifest.read_text())["attempts"][0]
        self.assertEqual(attempt["status"], "proof_candidate", attempt.get("error"))
        self.assertEqual(attempt["submission_manifest"], "project/submission.json")
        self.assertEqual(attempt["literature_requests"], [])
        self.assertNotIn("usage", attempt)
        self.assertEqual(len(attempt["artifacts"]), 5)
        bound = validate_proof_evidence(self.benchmark, self.report, attempt, manifest.parent)
        self.assertEqual(bound["proof_project"], self.report["proof_project"])

    def test_legacy_adapter_rejects_unsealed_helper_and_mismatched_mapping(self):
        manifest = self.legacy_adapter(self.root / "legacy-missing-helper", omit="Basic.lean")
        attempt = json.loads(manifest.read_text())["attempts"][0]
        self.assertEqual(attempt["status"], "error")
        self.assertIn("not a sealed artifact", attempt["error"])
        self.write("claims.json", {"claims": [{**self.claims[0], "right": "PSPACE"}]})
        manifest = self.legacy_adapter(self.root / "legacy-bad-mapping")
        attempt = json.loads(manifest.read_text())["attempts"][0]
        self.assertEqual(attempt["status"], "error")
        self.assertIn("submitted ordinary claims", attempt["error"])


if __name__ == "__main__":
    unittest.main()
