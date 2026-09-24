import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark, ROOT, canonical_hash
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.proofbundle import load_proof_bundle, proof_digest
from inclusion_bench.proofcheck import verify_proof


spec = importlib.util.spec_from_file_location("project_remote", ROOT / "scripts/proofcheck/remote_runner.py")
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)


class ProofBundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def project(self, sources=None, **changes):
        sources = sources or {"Main.lean": "import Lemmas.Basic\n", "Lemmas/Basic.lean": "import Std\n"}
        manifest = {"schema_version": 1, "entrypoint": "Main", "files": list(sources)}
        manifest.update(changes)
        for path, source in sources.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source)
        (self.root / "submission.json").write_text(json.dumps(manifest))
        return load_proof_bundle(self.root)

    def packet(self, bundle):
        return {"sources": bundle.sources, "entrypoint": bundle.entrypoint,
                "manifest": bundle.files["submission.json"].decode(), "metadata": bundle.metadata,
                "module_order": list(bundle.module_order), "external_imports": list(bundle.external_imports)}

    def test_exact_snapshot_digest_includes_manifest_unused_files_and_paths(self):
        bundle = self.project({"Main.lean": "import Lemmas.Basic\n", "Lemmas/Basic.lean": "import Std\n",
                               "Unused.lean": "def unused := 1\n"})
        self.assertEqual(bundle.module_order, ("Lemmas.Basic", "Main"))
        self.assertEqual(bundle.external_imports, ("Std",))
        self.assertEqual(bundle.proof_sha256, canonical_hash(bundle.metadata))
        self.assertEqual(bundle.proof_sha256, proof_digest(self.root))
        self.assertEqual(bundle.metadata["files"], {
            path: hashlib.sha256(body).hexdigest() for path, body in bundle.files.items()})
        self.assertEqual(remote.candidate_plan(self.packet(bundle))[1], list(bundle.module_order))
        (self.root / "Unused.lean").write_text("def unused := 2\n")
        changed = load_proof_bundle(self.root)
        self.assertNotEqual(bundle.proof_sha256, changed.proof_sha256)
        self.assertEqual(bundle.files["Unused.lean"], b"def unused := 1\n")
        with (self.root / "submission.json").open("a") as handle:
            handle.write("\n")
        self.assertNotEqual(changed.proof_sha256, proof_digest(self.root))

    def test_legacy_digest_is_unchanged_and_file_limit_remains(self):
        path = self.root / "proof.lean"
        path.write_bytes(b"-- exact bytes\r\ntheorem t : True := True.intro\r\n")
        bundle = load_proof_bundle(path)
        self.assertIsNone(bundle.metadata)
        self.assertEqual(bundle.proof_sha256, hashlib.sha256(path.read_bytes()).hexdigest())
        path.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(path)

    def test_invalid_manifest_shape_duplicates_and_missing_entrypoint(self):
        for changes in ({"schema_version": True}, {"schema_version": 2}, {"entrypoint": "Missing"},
                        {"files": []}, {"files": ["Main.lean"] * 2}, {"files": ["Main.lean"] * 129},
                        {"extra": 1}):
            with self.subTest(changes=changes), self.assertRaises(InvalidEvidence):
                self.project({"Main.lean": ""}, **changes)
        (self.root / "submission.json").write_text('{"schema_version":1,"schema_version":1,"entrypoint":"Main","files":["Main.lean"]}')
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(self.root)

    def test_unsafe_paths_reserved_names_and_case_collisions(self):
        for path in ("../Bad.lean", "/Bad.lean", "A\\B.lean", "A.olean", "Bad;touch.lean",
                     "Lean.lean", "mathlib/Foo.lean", "TrustedBaseline.lean", "ProofExport/X.lean",
                     "AuditImports.lean", "Candidate.lean"):
            (self.root / "submission.json").write_text(json.dumps({
                "schema_version": 1, "entrypoint": "Main", "files": ["Main.lean", path]}))
            with self.subTest(path=path), self.assertRaises(InvalidEvidence):
                load_proof_bundle(self.root)
        for paths in (("Main.lean", "main.lean"), ("Main.lean", "Foo/A.lean", "foo/B.lean"),
                      ("Main.lean", "Foo.lean", "foo/B.lean")):
            with self.subTest(paths=paths), self.assertRaises(InvalidEvidence):
                self.project({path: "" for path in paths})

    def test_symlink_file_directory_manifest_and_root_fail_closed(self):
        self.project()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "Basic.lean").write_text("import Std\n")
        shutil.rmtree(self.root / "Lemmas")
        (self.root / "Lemmas").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(self.root)
        (self.root / "Lemmas").unlink()
        (self.root / "Lemmas").mkdir()
        (self.root / "Lemmas/Basic.lean").symlink_to(outside / "Basic.lean")
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(self.root)
        (self.root / "Lemmas/Basic.lean").unlink()
        (self.root / "Lemmas/Basic.lean").write_text("")
        manifest = self.root / "submission.json"
        manifest.rename(outside / "manifest.json")
        manifest.symlink_to(outside / "manifest.json")
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(self.root)
        link = self.root / "project-link"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(link)

    def test_missing_unapproved_and_cyclic_imports_including_unused_modules(self):
        for sources in ({"Main.lean": "import Missing\n"}, {"Main.lean": "import Evil.Library\n"},
                        {"Main.lean": "import Main\n"},
                        {"Main.lean": "import A\n", "A.lean": "import Main\n"},
                        {"Main.lean": "", "Unused.lean": "import Unused\n"},
                        {"Main.lean": "import Std; #eval IO.println 1\n"}):
            with self.subTest(sources=sources), self.assertRaises(InvalidEvidence):
                self.project(sources)
        (self.root / "submission.json").write_text(json.dumps({"schema_version": 1, "entrypoint": "Main", "files": ["Main.lean", "Missing.lean"]}))
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(self.root)

    def test_nested_header_comments_utf8_and_aggregate_limit(self):
        bundle = self.project({"Main.lean": "/- outer /- inner -/ -/\nimport /- nested /- inline -/ -/\n A -- comment\n", "A.lean": "import\n Mathlib.Data.Nat.Prime /- final -/\n"})
        self.assertEqual(bundle.external_imports, ("Mathlib.Data.Nat.Prime",))
        self.assertEqual(remote.candidate_plan(self.packet(bundle))[2], list(bundle.external_imports))
        with patch("inclusion_bench.proofbundle.MAX_PROJECT_BYTES", 1), self.assertRaises(InvalidEvidence):
            load_proof_bundle(self.root)
        (self.root / "A.lean").write_bytes(b"\xff")
        with self.assertRaises(InvalidEvidence):
            load_proof_bundle(self.root)

    def test_remote_plan_rejects_tampered_hashes_paths_and_graph(self):
        bundle = self.project()
        for mutate in (lambda p: p["sources"].update({"Main.lean": "different"}),
                       lambda p: p.update(module_order=["Main", "Lemmas.Basic"]),
                       lambda p: p.update(external_imports=["Evil"]),
                       lambda p: p["sources"].update({"../Bad.lean": ""})):
            packet = json.loads(json.dumps(self.packet(bundle)))
            mutate(packet)
            with self.assertRaises(RuntimeError):
                remote.candidate_plan(packet)

    def test_verifier_binds_snapshot_and_hydrates_only_trusted_imports(self):
        bundle = self.project()
        benchmark = Benchmark()
        claim = {"relation": "inclusion", "left": "P", "right": "P", "theorem": "submitted"}
        response = subprocess.CompletedProcess([], 0, '{"status":"rejected"}', "")
        with patch("inclusion_bench.proofcheck._run_verifier", return_value=response) as call:
            report = verify_proof(benchmark, self.root, [claim], host=None)
        packet = json.loads(call.call_args.kwargs["input"])
        self.assertEqual(report["proof_project"], bundle.metadata)
        self.assertEqual(report["proof_sha256"], bundle.proof_sha256)
        self.assertEqual(packet["candidate_project"]["sources"], bundle.sources)
        self.assertEqual(packet["files"]["AuditImports.lean"], "import TrustedBaseline\nimport Std\n")
        self.assertIn('import Main\n', packet["files"]["Candidate.lean"])
        self.assertIn('#proofcheck_export_project ["Lemmas.Basic", "Main"] ["submitted"]', packet["files"]["Candidate.lean"])
        self.assertNotIn("import Main", packet["files"]["ProofAudit.lean"])
        self.assertNotIn("import Main", packet["files"]["AuditImports.lean"])


class ProjectExportLeanTests(unittest.TestCase):
    def test_imported_candidate_closure_and_fresh_library_imports(self):
        lean = os.environ.get("LEAN_BIN") or shutil.which("lean")
        if not lean:
            self.skipTest("set LEAN_BIN for imported-module export tests")
        with tempfile.TemporaryDirectory(prefix="project-export-tests-") as temporary:
            folder = Path(temporary)
            for name in ("ProofCodec", "ProofExport", "ProofAudit"):
                shutil.copyfile(ROOT / f"scripts/proofcheck/{name}.lean", folder / f"{name}.lean")
            shutil.copyfile(ROOT / "tests/lean/TrustedBaseline.lean", folder / "TrustedBaseline.lean")
            for name in ("ProjectImported", "ProjectRoot", "ProjectExternal", "ProofProjectTests"):
                shutil.copyfile(ROOT / f"tests/lean/{name}.lean", folder / f"{name}.lean")
            (folder / "AuditImports.lean").write_text("import ProjectExternal\n")
            env = {**os.environ, "LEAN_PATH": str(folder)}
            for name in ("ProofCodec", "ProofExport", "TrustedBaseline", "ProofAudit", "ProjectExternal", "AuditImports", "ProjectImported", "ProjectRoot"):
                result = subprocess.run([lean, "-j1", "-DElab.async=false", "-o", name + ".olean", name + ".lean"],
                                        cwd=folder, env=env, capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run([lean, "-j1", "ProofProjectTests.lean"], cwd=folder, env=env,
                                    capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Project export tests passed", result.stdout)
            # Exercise Lean's actual CLI argument boundary as well as runAudit.
            # The final fixture leaves an export requiring the extra imports.
            auditor = folder / "ProofAudit.lean"
            auditor.write_text("import AuditImports\n" + auditor.read_text())
            result = subprocess.run([lean, "-j1", "-DElab.async=false", "--run", "ProofAudit.lean", "--",
                                     "project-payload.json", "project-targets.json", "project-literature.json",
                                     "--project-imports"], cwd=folder, env=env,
                                    capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "verified")


if __name__ == "__main__":
    unittest.main()
