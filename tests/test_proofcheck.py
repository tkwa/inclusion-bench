import json
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
import shutil
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.proofcheck import baseline_name, trusted_baseline, validate_claims, verify_proof
from inclusion_bench.literature import CHECKS, record_literature_review, require_approved_dependencies
from inclusion_bench.proofcheck import semantic_inputs


class ProofcheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = Benchmark()
        cls.claim = {"relation": "inclusion", "left": "P", "right": "P", "theorem": "submitted"}

    def test_exact_target_is_generated_from_roster(self):
        source, entries, targets = trusted_baseline(self.benchmark, [self.claim])
        self.assertIn("def TrustedBaseline.expected_0 : Prop := Includes (Quantum.completeInterpretation .P) (Quantum.completeInterpretation .P)", source)
        self.assertEqual(targets, [{"theorem": "submitted", "expected": "InclusionBench.TrustedBaseline.expected_0"}])
        self.assertTrue(all(e["source_ids"] and e["sources_sha256"] for e in entries))
        self.assertEqual(len(entries), len({e["name"] for e in entries}))

    def test_baseline_names_cannot_collide_by_punctuation(self):
        self.assertNotEqual(baseline_name("a/b"), baseline_name("a:b"))
        self.assertNotIn("-", baseline_name("fact:p-in-np"))

    def test_no_assumed_submitted_claim(self):
        claim = {**self.claim, "left": "NP", "right": "P"}
        source, entries, _ = trusted_baseline(self.benchmark, [claim])
        self.assertTrue(source.count("def TrustedBaseline.expected_0") == 1)
        self.assertFalse(any(e["statement"] == "Includes (Quantum.completeInterpretation .NP) (Quantum.completeInterpretation .P)" for e in entries))

    def test_background_proof_targets_remain_available(self):
        claim = {'relation': 'inclusion', 'left': 'LWPP', 'right': 'WPP',
                 'theorem': 'background_result'}
        validate_claims(self.benchmark, [claim])
        source, _, _ = trusted_baseline(self.benchmark, [claim])
        self.assertIn('Includes (Quantum.completeInterpretation .LWPP) (Quantum.completeInterpretation .WPP)', source)
        self.assertEqual(self.benchmark.score({'claims': [claim]})['score'], 0)

    def test_rejects_invalid_claims_and_independence(self):
        for claims in ([], [self.claim, self.claim], [{**self.claim, "left": "invented"}],
                       [{**self.claim, "theorem": "x\naxiom bad : False"}],
                       [{**self.claim, "relation": "independence"}]):
            with self.subTest(claims=claims), self.assertRaises(InvalidEvidence):
                validate_claims(self.benchmark, claims)

    def test_unavailable_never_becomes_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "proof.lean"
            report_path = Path(directory) / "report.json"
            source.write_text("theorem submitted : True := True.intro")
            with patch("inclusion_bench.proofcheck.subprocess.run", side_effect=OSError("offline")):
                report = verify_proof(self.benchmark, source, [self.claim], report_path=report_path)
            self.assertEqual(report["status"], "unavailable")
            self.assertEqual(report["official_points"], 0)
            self.assertEqual(json.loads(report_path.read_text()), report)

    def test_public_runtime_options_reach_local_driver(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "proof.lean"
            source.write_text("theorem submitted : True := True.intro")
            response = subprocess.CompletedProcess([], 0, '{"status":"rejected"}', "")
            with patch("inclusion_bench.proofcheck.subprocess.run", return_value=response) as call:
                verify_proof(self.benchmark, source, [self.claim], host=None,
                             remote_root="/public/repository", image="ubuntu:22.04",
                             toolchain_path="/public/lean-4.19.0")
            args, kwargs = call.call_args
            self.assertEqual(args[0][:2], ["python3", "-c"])
            packet = json.loads(kwargs["input"])
            self.assertEqual(packet["image"], "ubuntu:22.04")
            self.assertEqual(packet["toolchain_path"], "/public/lean-4.19.0")
            self.assertEqual(packet["remote_root"], "/public/repository")


@unittest.skipUnless(os.environ.get("INCLUSION_PROOFCHECK_INTEGRATION") == "1",
                     "set INCLUSION_PROOFCHECK_INTEGRATION=1 for actual isolated Ubuntu tests")
class IsolatedProofcheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = Benchmark()
        cls.claim = {"relation": "inclusion", "left": "P", "right": "P", "theorem": "submitted"}
        config = os.environ.get("INCLUSION_PROOFCHECK_CONFIG")
        cls.runtime = json.loads(Path(config).read_text()) if config else {}

    def check_source(self, source, status, claim=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proof.lean"
            path.write_text(source)
            report = verify_proof(self.benchmark, path, [claim or self.claim], **self.runtime)
            self.assertEqual(report["status"], status, report.get("reason", "") + report.get("log", ""))
            self.assertEqual(report["official_points"], 0)
            return report

    def test_positive_kernel_proof(self):
        report = self.check_source("open InclusionBench\ntheorem submitted : Includes (Quantum.completeInterpretation .P) (Quantum.completeInterpretation .P) := includes_refl _", "verified")
        self.assertLessEqual(set(report["targets"][0]["axioms"]), {"propext", "Classical.choice", "Quot.sound"})
        self.assertEqual(report["runtime"]["cpu_limit"], 1)
        self.assertEqual(report["runtime"]["pids_limit"], 64)
        self.assertFalse(report["runtime"]["async_elaboration"])

    def test_positive_cited_baseline(self):
        fact = next(f for f in self.benchmark.knowledge["facts"] if f["relation"] == "inclusion")
        name = baseline_name("fact:" + fact["id"])
        claim = {key: fact[key] for key in ("relation", "left", "right")}
        claim["theorem"] = "submitted"
        source = f"open InclusionBench\ntheorem submitted : Includes (Quantum.completeInterpretation .{fact['left']}) (Quantum.completeInterpretation .{fact['right']}) := {name}"
        report = self.check_source(source, "verified", claim)
        self.assertIn(name, report["targets"][0]["axioms"])

    def test_shipped_multifile_project(self):
        project = self.benchmark.root / "examples/submissions/multifile"
        claims = json.loads((project / "claims.json").read_text())["claims"]
        report = verify_proof(self.benchmark, project, claims, **self.runtime)
        self.assertEqual(report["status"], "verified", report.get("reason", "") + report.get("log", ""))
        self.assertEqual(report["proof_project"]["entrypoint"], "Main")
        self.assertEqual(set(report["proof_project"]["files"]),
                         {"submission.json", "Main.lean", "Lemmas/Reflexivity.lean"})
        self.assertEqual(report["declaration_count"], 2)
        self.assertFalse(report["runtime"]["candidate_host_writes"])

    def test_project_imported_target_with_extra_mathlib_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Lemmas").mkdir()
            (root / "submission.json").write_text(json.dumps({"schema_version": 1, "entrypoint": "Main",
                "files": ["Main.lean", "Lemmas/External.lean"]}))
            (root / "Main.lean").write_text("import Lemmas.External\n")
            (root / "Lemmas/External.lean").write_text("""import TrustedBaseline
import Mathlib.NumberTheory.Primorial
open InclusionBench InclusionBench.Support
unsafe def unusedTool : IO Unit := pure ()
axiom unusedFabrication : False
theorem Submission.imported : Includes Classes.P Classes.P :=
  And.right (And.intro (primorial_pos 2) (includes_refl _))
""")
            report = verify_proof(self.benchmark, root, [{**self.claim, "theorem": "Submission.imported"}], **self.runtime)
        self.assertEqual(report["status"], "verified", report.get("reason", "") + report.get("log", ""))
        self.assertEqual(report["declaration_count"], 1)
        self.assertEqual(report["literature_dependencies"], [])

    def test_project_literature_dependency_from_imported_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "submission.json").write_text(json.dumps({"schema_version": 1, "entrypoint": "Main",
                "files": ["Main.lean", "Assumptions.lean"]}))
            (root / "Assumptions.lean").write_text("""import TrustedBaseline
open InclusionBench InclusionBench.Support
def Submission.LocalStatement : Prop := Includes Classes.P Classes.P
axiom Literature.project_fact : Submission.LocalStatement
""")
            (root / "Main.lean").write_text("""import Assumptions
open InclusionBench InclusionBench.Support
theorem submitted : Includes Classes.P Classes.P := Literature.project_fact
""")
            rejected = verify_proof(self.benchmark, root, [self.claim], **self.runtime)
            self.assertEqual(rejected["status"], "rejected", rejected)
            request = {"name": "Literature.project_fact", "statement": "Test-only reflexive inclusion.",
                       "rationale": "Exercise literature type context across local modules.",
                       "sources": [{"title": "Computational Complexity: A Modern Approach",
                                    "url": "https://theory.cs.princeton.edu/complexity/book.pdf",
                                    "locator": "Chapter 1, complexity classes and reflexivity of inclusion.",
                                    "publication_date": "2009"}]}
            pending = verify_proof(self.benchmark, root, [self.claim], literature_requests=[request], **self.runtime)
        self.assertEqual(pending["status"], "needs_literature_review", pending.get("reason", "") + pending.get("log", ""))
        dependency = pending["literature_dependencies"][0]
        self.assertEqual(dependency["statement"], "Submission.LocalStatement")
        self.assertEqual([item["kind"] for item in dependency["context"]], ["definition"])
        self.assertEqual(pending["official_points"], 0)

    def test_integer_array_support_survives_fresh_replay(self):
        fixture = self.benchmark.root / "tests/lean/SupportArrayReplayTests.lean"
        source = "\n".join(fixture.read_text().splitlines()[1:])
        source = source.replace("Machines.polynomialTime", "Classes.P")
        report = self.check_source(source, "verified")
        expected = {"InclusionBench.Support.Literature.integer_mul",
                    "InclusionBench.Support.Literature.integerArray_zipWith",
                    "InclusionBench.Support.Literature.integerArray_sum"}
        self.assertTrue(expected <= set(report["targets"][0]["axioms"]), report)
        cited = {item["name"]: item for item in report["support_axioms"]}
        for name in expected:
            self.assertTrue(cited[name]["sources"])
            self.assertTrue(cited[name]["model_alignment"])
        self.assertEqual(report["literature_dependencies"], [])

    def test_curated_reduction_support_with_familiar_class_aliases(self):
        source = """open InclusionBench InclusionBench.Support
theorem submitted : Includes Classes.P Classes.P := by
  intro language member
  exact p_closed_under_reductions (reduction_refl language) member
"""
        report = self.check_source(source, "verified")
        self.assertEqual(report.get("literature_dependencies"), [])
        self.assertTrue({"InclusionBench.Support.Literature.polytime_identity",
                         "InclusionBench.Support.Literature.p_precompose"} <=
                        set(report["targets"][0]["axioms"]), report)
        cited = {entry["name"]: entry for entry in report["support_axioms"]}
        for name in ("InclusionBench.Support.Literature.polytime_identity",
                     "InclusionBench.Support.Literature.p_precompose"):
            self.assertTrue(cited[name]["sources"])
            self.assertTrue(all(source["locator"] and source["publication_date"]
                                for source in cited[name]["sources"]))

    def test_curated_gap_algebra_replays_for_pp_alias(self):
        source = """open InclusionBench InclusionBench.Support
theorem submitted : Includes Classes.PP Classes.PP := by
  intro language member
  obtain ⟨gap, computable, correct⟩ := member
  apply pp_of_gap (gapP_add computable gapP_zero)
  intro word
  simpa only [Int.add_zero] using correct word
"""
        report = self.check_source(source, "verified", {**self.claim, "left": "PP", "right": "PP"})
        self.assertEqual(report.get("literature_dependencies"), [])
        self.assertIn("InclusionBench.Support.Literature.sharpP_add", report["targets"][0]["axioms"])

    def test_all_familiar_class_aliases_match_frozen_targets(self):
        names = self.benchmark.context_ids
        self.assertEqual(len(names), 61)
        claims = [{"relation": "inclusion", "left": name, "right": name,
                   "theorem": "alias_" + name} for name in names]
        source = "open InclusionBench InclusionBench.Support\n" + "\n".join(
            f"theorem alias_{name} : Includes Classes.{name} Classes.{name} := includes_refl _"
            for name in names)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.lean"
            path.write_text(source)
            report = verify_proof(self.benchmark, path, claims, timeout_seconds=180, **self.runtime)
        self.assertEqual(report["status"], "verified", report.get("reason", "") + report.get("log", ""))
        self.assertEqual(len(report["targets"]), 61)
        self.assertEqual(report["official_points"], 0)

    def test_target_closure_excludes_unused_unsafe_and_unjustified_declarations(self):
        source = """open InclusionBench InclusionBench.Support
unsafe def unusedTactic : IO Unit := pure ()
axiom unusedUnjustified : False
axiom Literature.unused : False
theorem submitted : Includes Classes.P Classes.P := includes_refl _
"""
        report = self.check_source(source, "verified")
        self.assertEqual(report["declaration_count"], 1)
        self.assertEqual(report["literature_dependencies"], [])

    def test_literature_dependency_requires_exact_review_and_definition_context(self):
        # Every registry mutation is confined to this temporary benchmark.
        # The assertions are reflexive test fixtures, never benchmark results.
        with tempfile.TemporaryDirectory(prefix="isolated-literature-review-") as directory:
            root = Path(directory)
            shutil.copytree(self.benchmark.root / "data", root / "data")
            shutil.copytree(self.benchmark.root / "scripts/proofcheck", root / "scripts/proofcheck")
            shutil.copytree(self.benchmark.root / "support", root / "support")
            for relative in semantic_inputs(self.benchmark)[0]:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.benchmark.root / relative, target)
            (root / "support/literature-reviews.json").write_text("[]\n")
            benchmark = Benchmark(root)
            path = root / "proof.lean"
            request = {
                "name": "Literature.identity",
                "statement": "TEST-ONLY metadata summary; the auditor must print the actual Lean type.",
                "rationale": "Synthetic reflexivity fixture for the literature review mechanism.",
                "sources": [{"title": "Computational Complexity: A Modern Approach",
                             "url": "https://theory.cs.princeton.edu/complexity/book.pdf",
                             "locator": "Chapter 1: complexity classes as sets of languages; reflexivity of inclusion.",
                             "publication_date": "2009"}],
            }

            def run_source(conjunction=False):
                target = "Includes Classes.P Classes.P" + (" ∧ True" if conjunction else "")
                proof = "Literature.identity.1" if conjunction else "Literature.identity"
                path.write_text("open InclusionBench InclusionBench.Support\n"
                                f"def Submission.LocalTarget : Prop := {target}\n"
                                "axiom Literature.identity : Submission.LocalTarget\n"
                                f"theorem submitted : Includes Classes.P Classes.P := {proof}\n")
                return verify_proof(benchmark, path, [self.claim], literature_requests=[request],
                                    timeout_seconds=180, **self.runtime)

            pending = run_source()
            self.assertEqual(pending["status"], "needs_literature_review",
                             pending.get("reason", "") + pending.get("log", ""))
            self.assertEqual(pending["kernel_status"], "verified")
            self.assertEqual(pending["official_points"], 0)
            self.assertEqual(len(pending["literature_dependencies"]), 1)
            dependency = pending["literature_dependencies"][0]
            self.assertEqual(dependency["statement"], "Submission.LocalTarget")
            self.assertNotEqual(dependency["statement"], request["statement"])
            self.assertEqual(dependency["declaration"]["kind"], "axiom")
            self.assertNotIn("value", dependency["declaration"])
            self.assertEqual([item["kind"] for item in dependency["context"]], ["definition"])
            self.assertIn("Literature.identity", pending["targets"][0]["axioms"])
            with self.assertRaises(InvalidEvidence):
                require_approved_dependencies(benchmark, pending)

            review = {"schema_version": 1, "reviewer": "TEST-ONLY maintainer fixture",
                      "rationale": "Synthetic review of an elementary reflexive test statement.",
                      "status": "accepted", "checks": {check: True for check in CHECKS},
                      "dependency": dependency}
            record_literature_review(benchmark, review)
            approved = run_source()
            self.assertEqual(approved["status"], "verified", approved.get("reason", "") + approved.get("log", ""))
            self.assertEqual(approved["literature_reviews"][0]["status"], "accepted")
            self.assertEqual(require_approved_dependencies(benchmark, approved)[0]["status"], "accepted")
            self.assertEqual(approved["official_points"], 0)

            changed = run_source(conjunction=True)
            self.assertEqual(changed["status"], "needs_literature_review",
                             changed.get("reason", "") + changed.get("log", ""))
            changed_dependency = changed["literature_dependencies"][0]
            self.assertEqual(changed_dependency["declaration"], dependency["declaration"])
            self.assertNotEqual(changed_dependency["context"], dependency["context"])
            self.assertNotEqual(changed_dependency["dependency_sha256"], dependency["dependency_sha256"])
            self.assertEqual(changed["literature_reviews"][0]["status"], "pending")

            record_literature_review(benchmark, {**review, "status": "rejected",
                                                "rationale": "TEST-ONLY revocation fixture."})
            with self.assertRaises(InvalidEvidence):
                require_approved_dependencies(benchmark, approved)

    def test_all_new_context_targets_replay_in_the_isolated_kernel(self):
        names = ('BPL', 'UL', 'PL', 'BQL', 'ExistsR', 'PSharpP', 'CH',
                 'QMA2', 'StoqMA', 'QSZK', 'UniformNC1')
        claims = [{'relation': 'inclusion', 'left': name, 'right': name,
                   'theorem': 'target_' + name} for name in names]
        source = 'open InclusionBench\n' + '\n'.join(
            f'theorem target_{name} : Includes (Quantum.completeInterpretation .{name}) '
            f'(Quantum.completeInterpretation .{name}) := includes_refl _'
            for name in names)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'new-targets.lean'
            path.write_text(source)
            report = verify_proof(self.benchmark, path, claims,
                                  timeout_seconds=180, **self.runtime)
        self.assertEqual(report['status'], 'verified', report.get('reason', '') + report.get('log', ''))
        self.assertEqual(len(report['targets']), len(names))
        self.assertEqual(report['official_points'], 0)
        for target in report['targets']:
            self.assertLessEqual(set(target['axioms']), {'propext', 'Classical.choice', 'Quot.sound'})

    def test_wrong_target(self):
        self.check_source("theorem submitted : True := True.intro", "rejected")

    def test_sorry_is_rejected(self):
        self.check_source("open InclusionBench\ntheorem submitted : Includes (Quantum.completeInterpretation .P) (Quantum.completeInterpretation .P) := by sorry", "rejected")

    def test_extra_axiom_is_rejected(self):
        self.check_source("axiom fabricated : False\nopen InclusionBench\ntheorem submitted : Includes (Quantum.completeInterpretation .P) (Quantum.completeInterpretation .P) := False.elim fabricated", "rejected")

    def test_fake_diagnostic_does_not_verify(self):
        self.check_source('#eval IO.println "verified"\ntheorem submitted : True := True.intro', "rejected")

    def test_forged_export_is_rechecked_by_kernel(self):
        def name(text):
            value = ["a"]
            for part in text.split("."):
                value = ["s", value, part]
            return value

        payload = {"schema_version": 1, "declarations": [{
            "kind": "theorem", "name": name("submitted"), "levels": [],
            "type": ["c", name("InclusionBench.TrustedBaseline.expected_0"), []],
            "value": ["c", name("True.intro"), []]}]}
        # A deliberately malicious candidate bypasses the exporter entirely.
        # Successful elaborator exit and a fabricated payload still cannot
        # convince the clean kernel that True.intro proves the target.
        literal = json.dumps(json.dumps(payload))
        source = f'#eval do\n  IO.FS.writeFile "/work/proof-export.json" {literal}\n  (IO.Process.exit 0 : IO Unit)'
        report = self.check_source(source, "rejected")
        self.assertIn("Kernel rejected declaration", report.get("reason", ""), report)


    def test_forged_dag_export_is_rechecked_by_kernel(self):
        # All references are structurally valid; the proof has the wrong type.
        payload = {"schema_version": 2, "declarations": [{
            "kind": "theorem", "name": 1, "levels": [], "type": 0, "value": 1,
            "names": [["a"], ["s", 0, "submitted"], ["s", 0, "InclusionBench"],
                      ["s", 2, "TrustedBaseline"], ["s", 3, "expected_0"],
                      ["s", 0, "True"], ["s", 5, "intro"]],
            "universes": [], "expressions": [["c", 4, []], ["c", 6, []]]}]}
        literal = json.dumps(json.dumps(payload))
        source = f'#eval do\n  IO.FS.writeFile "/work/proof-export.json" {literal}\n  (IO.Process.exit 0 : IO Unit)'
        report = self.check_source(source, "rejected")
        self.assertIn("Kernel rejected declaration", report.get("reason", ""), report)

    def test_legacy_export_still_verifies(self):
        # Generate a real legacy payload using the retained v1 codec, then
        # bypass the v2 export command to exercise audit version dispatch.
        source = """open InclusionBench Lean Elab Command InclusionProofcheck
 theorem submitted : Includes (Quantum.completeInterpretation .P) (Quantum.completeInterpretation .P) := includes_refl _
 run_cmd do
   let env ← getEnv
   let some info := env.find? `submitted | throwError "missing theorem"
   let .ok declaration := encodeDeclarationV1 info | throwError "legacy export failed"
   let payload := Json.mkObj [("schema_version", toJson (1 : Nat)),
     ("declarations", Json.arr #[declaration])]
   liftIO <| IO.FS.writeFile "/work/proof-export.json" payload.compress
   liftIO <| (IO.Process.exit 0 : IO Unit)
"""
        self.check_source(source, "verified")


if __name__ == "__main__":
    unittest.main()
