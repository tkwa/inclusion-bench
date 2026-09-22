import json
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.proofcheck import baseline_name, trusted_baseline, validate_claims, verify_proof


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
            report = verify_proof(self.benchmark, path, [claim or self.claim], timeout_seconds=180, **self.runtime)
            self.assertEqual(report["status"], status, report.get("reason", "") + report.get("log", ""))
            self.assertEqual(report["official_points"], 0)
            return report

    def test_positive_kernel_proof(self):
        report = self.check_source("open InclusionBench\ntheorem submitted : Includes (Quantum.completeInterpretation .P) (Quantum.completeInterpretation .P) := includes_refl _", "verified")
        self.assertLessEqual(set(report["targets"][0]["axioms"]), {"propext", "Classical.choice", "Quot.sound"})
        self.assertEqual(report["runtime"]["cpu_limit"], 1)

    def test_positive_cited_baseline(self):
        fact = next(f for f in self.benchmark.knowledge["facts"] if f["relation"] == "inclusion")
        name = baseline_name("fact:" + fact["id"])
        claim = {key: fact[key] for key in ("relation", "left", "right")}
        claim["theorem"] = "submitted"
        source = f"open InclusionBench\ntheorem submitted : Includes (Quantum.completeInterpretation .{fact['left']}) (Quantum.completeInterpretation .{fact['right']}) := {name}"
        report = self.check_source(source, "verified", claim)
        self.assertIn(name, report["targets"][0]["axioms"])

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
