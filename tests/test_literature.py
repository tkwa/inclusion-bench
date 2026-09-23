"""Approval must bind the exact mathematics and remain separate from replay."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark, canonical_hash
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.literature import (
    CHECKS, bind_dependencies, dependency_decisions, dependency_identity,
    record_literature_review, require_approved_dependencies, validate_requests,
)
from inclusion_bench.proofcheck import semantic_inputs, trusted_verification_inputs, verify_proof


def request():
    return {
        "name": "Literature.fact", "statement": "A cited mathematical statement.",
        "rationale": "This established lemma supplies a dependency of the new proof.",
        "sources": [{"title": "Test-only bibliography fixture", "url": "https://example.org/book",
                     "locator": "Theorem 1", "publication_date": "1999"}],
    }


def raw_dependency():
    return {
        "name": "Literature.fact", "statement": "True", "context": [],
        "declaration": {
            "kind": "axiom", "name": 2, "levels": [], "type": 0,
            "names": [["a"], ["s", 0, "Literature"], ["s", 1, "fact"], ["s", 0, "True"]],
            "universes": [], "expressions": [["c", 3, []]],
        },
    }


class LiteratureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="literature-tests-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        (root / "quantum").mkdir()
        (root / "quantum/lake-manifest.json").write_text("{}\n")
        self.benchmark = SimpleNamespace(root=root, digest="a" * 64,
                                         policy={"cutoff": "2026-06-01"})
        self.semantics = semantic_inputs(self.benchmark)[2]
        self.baseline = "b" * 64
        self.checker = "c" * 64
        self.dependencies = bind_dependencies(self.benchmark, [raw_dependency()], [request()],
                                              self.semantics, self.baseline, self.checker)
        # These registry unit tests use a minimal temporary benchmark. The
        # bridge tests below exercise real generated verification bindings.
        binding_patch = patch("inclusion_bench.proofcheck.verification_bindings", side_effect=lambda benchmark, claims: {
            "baseline_sha256": self.baseline, "checker_sha256": self.checker,
            "semantics_sha256": semantic_inputs(benchmark)[2],
        })
        binding_patch.start()
        self.addCleanup(binding_patch.stop)

    def decision(self, status="accepted", dependency=None):
        return {
            "schema_version": 1, "reviewer": "TEST-ONLY independent reviewer",
            "rationale": "TEST-ONLY review of the exact statement and cited source.",
            "status": status, "checks": {check: True for check in CHECKS},
            "dependency": copy.deepcopy(dependency or self.dependencies[0]),
        }

    def report(self):
        return {
            "status": "verified", "kernel_status": "verified",
            "baseline_sha256": self.baseline, "checker_sha256": self.checker,
            "semantics_sha256": self.semantics,
            "literature_dependencies": copy.deepcopy(self.dependencies),
            "literature_reviews": dependency_decisions(self.benchmark, self.dependencies, self.semantics),
            "targets": [{"theorem": "submitted", "axioms": ["Literature.fact"]}],
        }

    def test_citations_are_requests_not_approval(self):
        self.assertEqual(validate_requests(self.benchmark, [request()]), [request()])
        decisions = dependency_decisions(self.benchmark, self.dependencies, self.semantics)
        self.assertEqual(decisions[0]["status"], "pending")
        with self.assertRaises(InvalidEvidence):
            require_approved_dependencies(self.benchmark, self.report())

    def test_request_rejects_approval_flags_namespace_confusion_and_duplicates(self):
        for changed in ({**request(), "approved": True},
                        {**request(), "name": "LiteratureForgery.fact"},
                        {**request(), "name": "Literature"},
                        {**request(), "name": "Literature.fact\naxiom evil : False"}):
            with self.subTest(changed=changed), self.assertRaises(InvalidEvidence):
                validate_requests(self.benchmark, [changed])
        with self.assertRaises(InvalidEvidence):
            validate_requests(self.benchmark, [request(), request()])

    def test_partial_publication_dates_are_conservative_at_cutoff(self):
        for published, accepted in [("2025", True), ("2026", False), ("2026-05", True),
                                    ("2026-06", False), ("2026-06-01", True), ("2026-06-02", False)]:
            changed = request()
            changed["sources"][0]["publication_date"] = published
            with self.subTest(published=published):
                if accepted:
                    validate_requests(self.benchmark, [changed])
                else:
                    with self.assertRaises(InvalidEvidence):
                        validate_requests(self.benchmark, [changed])

    def test_sources_require_usable_citations(self):
        for key, value in [("url", "javascript:alert(1)"), ("url", "https://user:secret@example.org"),
                           ("publication_date", "2026-99"), ("locator", "")]:
            changed = request()
            changed["sources"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(InvalidEvidence):
                validate_requests(self.benchmark, [changed])

    def test_identity_binds_context_citations_baseline_checker_and_semantics(self):
        original = self.dependencies[0]
        for field, value in {
            "context": [{"kind": "definition", "value": "changed predicate meaning"}],
            "declaration": {**original["declaration"], "type": 1},
            "request": {**request(), "rationale": "different citation justification"},
            "statement": "False", "baseline_sha256": "d" * 64,
            "checker_sha256": "e" * 64, "semantics_sha256": "f" * 64,
            "dataset_sha256": "0" * 64,
        }.items():
            changed = copy.deepcopy(original)
            changed[field] = value
            with self.subTest(field=field):
                self.assertNotEqual(dependency_identity(changed), dependency_identity(original))

    def test_auditor_cannot_invent_or_duplicate_requested_dependencies(self):
        raw = raw_dependency()
        for values in [[{**raw, "name": "Literature.other"}], [raw, raw],
                       [{k: v for k, v in raw.items() if k != "context"}]]:
            with self.subTest(values=values), self.assertRaises(InvalidEvidence):
                bind_dependencies(self.benchmark, values, [request()], self.semantics,
                                  self.baseline, self.checker)

    def test_exact_checked_approval_is_required_and_can_be_revoked(self):
        missing = self.decision()
        missing["checks"]["exact_statement"] = False
        with self.assertRaises(InvalidEvidence):
            record_literature_review(self.benchmark, missing)
        record_literature_review(self.benchmark, self.decision())
        approved = self.report()
        self.assertEqual(require_approved_dependencies(self.benchmark, approved)[0]["status"], "accepted")
        record_literature_review(self.benchmark, self.decision("rejected"))
        with self.assertRaises(InvalidEvidence):
            require_approved_dependencies(self.benchmark, approved)

    def test_modified_dependency_cannot_reuse_approval_or_old_digest(self):
        record_literature_review(self.benchmark, self.decision())
        changed = copy.deepcopy(self.dependencies[0])
        changed["context"] = [{"kind": "definition", "type": "Prop", "value": "False"}]
        with self.assertRaisesRegex(InvalidEvidence, "hash mismatch"):
            dependency_decisions(self.benchmark, [changed], self.semantics)
        changed["dependency_sha256"] = dependency_identity(changed)
        self.assertEqual(dependency_decisions(self.benchmark, [changed], self.semantics)[0]["status"], "pending")

    def test_changed_support_semantics_invalidates_existing_approval(self):
        record_literature_review(self.benchmark, self.decision())
        approved = self.report()
        (self.benchmark.root / "support/Changed.lean").write_text("def changed := True\n")
        with self.assertRaisesRegex(InvalidEvidence, "semantic|trusted"):
            require_approved_dependencies(self.benchmark, approved)

    def test_report_cannot_substitute_baseline_or_checker(self):
        record_literature_review(self.benchmark, self.decision())
        for binding in ("baseline_sha256", "checker_sha256"):
            report = self.report()
            report[binding] = "d" * 64
            with self.subTest(binding=binding), self.assertRaises(InvalidEvidence):
                require_approved_dependencies(self.benchmark, report)

    def test_registry_corruption_and_stale_decisions_are_rejected(self):
        record_literature_review(self.benchmark, self.decision())
        stale = self.report()
        stale["literature_reviews"][0]["review_sha256"] = "0" * 64
        with self.assertRaises(InvalidEvidence):
            require_approved_dependencies(self.benchmark, stale)
        path = self.benchmark.root / "support/literature-reviews.json"
        registry = json.loads(path.read_text())
        registry[0]["rationale"] = "changed without updating the hash"
        path.write_text(json.dumps(registry))
        with self.assertRaisesRegex(InvalidEvidence, "registry hash mismatch"):
            dependency_decisions(self.benchmark, self.dependencies, self.semantics)

    def test_reported_literature_axiom_requires_dependency_metadata(self):
        report = self.report()
        report["literature_dependencies"] = []
        report["literature_reviews"] = []
        with self.assertRaises(InvalidEvidence):
            require_approved_dependencies(self.benchmark, report)


class LiteratureVerifierBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = Benchmark()
        cls.claim = {"relation": "inclusion", "left": "P", "right": "P", "theorem": "submitted"}

    def verify_response(self, response, *, returncode=0, reviews=None):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "proof.lean"
            source.write_text("-- TEST-ONLY bridge fixture, no compiler is invoked.\n")
            completed = subprocess.CompletedProcess([], returncode, json.dumps(response), "")
            with patch("inclusion_bench.proofcheck.subprocess.run", return_value=completed) as call, \
                    patch("inclusion_bench.literature.literature_reviews", return_value=reviews or []):
                report = verify_proof(self.benchmark, source, [self.claim], literature_requests=[request()])
            return report, json.loads(call.call_args.kwargs["input"])

    def test_conditional_replay_stays_pending_without_maintainer_decision(self):
        response = {"status": "needs_literature_review", "kernel_status": "verified",
                    "literature_dependencies": [raw_dependency()]}
        report, packet = self.verify_response(response)
        self.assertEqual(report["status"], "needs_literature_review")
        self.assertEqual(report["official_points"], 0)
        self.assertEqual(report["literature_reviews"][0]["status"], "pending")
        self.assertEqual(json.loads(packet["files"]["literature.json"]), {"requests": [request()]})
        self.assertIn('#proofcheck_export_targets ["submitted"]', packet["files"]["Candidate.lean"])

    def test_conflicting_status_missing_kernel_check_and_process_failure_never_verify(self):
        for response, code in [
            ({"status": "verified", "literature_dependencies": [raw_dependency()]}, 0),
            ({"status": "needs_literature_review", "kernel_status": "verified", "literature_dependencies": []}, 0),
            ({"status": "needs_literature_review", "literature_dependencies": [raw_dependency()]}, 0),
            ({"status": "verified"}, 1),
            ({"status": "verified", "proof_sha256": "0" * 64}, 0),
        ]:
            with self.subTest(response=response, code=code):
                report, _ = self.verify_response(response, returncode=code)
                self.assertEqual(report["status"], "unavailable", report)

    def test_exact_maintainer_approval_can_complete_conditional_replay(self):
        bindings = trusted_verification_inputs(self.benchmark, [self.claim])["bindings"]
        dependency = bind_dependencies(self.benchmark, [raw_dependency()], [request()],
                                       bindings["semantics_sha256"], bindings["baseline_sha256"],
                                       bindings["checker_sha256"])[0]
        decision = {
            "schema_version": 1, "reviewer": "TEST-ONLY maintainer", "rationale": "Fixture review",
            "status": "accepted", "checks": {check: True for check in CHECKS}, "dependency": dependency,
        }
        decision["review_sha256"] = canonical_hash(decision)
        report, _ = self.verify_response(
            {"status": "needs_literature_review", "kernel_status": "verified",
             "literature_dependencies": [raw_dependency()]}, reviews=[decision])
        self.assertEqual(report["status"], "verified", report)
        self.assertEqual(report["official_points"], 0)
        self.assertEqual(report["literature_reviews"][0]["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
