"""Run codec and fresh-auditor regressions without Docker or benchmark dependencies."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProofCodecTests(unittest.TestCase):
    def test_lean_codec_roundtrips_sharing_and_malformed_inputs(self):
        lean = os.environ.get("LEAN_BIN") or shutil.which("lean")
        if not lean:
            self.skipTest("set LEAN_BIN or put Lean 4.19.0 on PATH for codec tests")
        with tempfile.TemporaryDirectory(prefix="proofcodec-tests-") as temporary:
            folder = Path(temporary)
            for source in (ROOT / "scripts" / "proofcheck" / "ProofCodec.lean",
                           ROOT / "scripts" / "proofcheck" / "ProofExport.lean",
                           ROOT / "scripts" / "proofcheck" / "ProofAudit.lean",
                           ROOT / "tests" / "lean" / "TrustedBaseline.lean",
                           ROOT / "tests" / "lean" / "ProofCodecTests.lean",
                           ROOT / "tests" / "lean" / "ProofAuditTests.lean"):
                shutil.copyfile(source, folder / source.name)
            environment = os.environ.copy()
            environment["LEAN_PATH"] = str(folder)
            commands = [[lean, "-j1", "-o", str(folder / f"{name}.olean"), str(folder / f"{name}.lean")]
                        for name in ("ProofCodec", "ProofExport", "TrustedBaseline", "ProofAudit")]
            commands.append([lean, "-j1", "--run", str(folder / "ProofCodecTests.lean"), "80", "80"])
            for command in commands:
                result = subprocess.run(command, cwd=folder, env=environment,
                                        capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ProofCodec tests passed", result.stdout)
            result = subprocess.run([lean, "-j1", str(folder / "ProofAuditTests.lean")],
                                    cwd=folder, env=environment, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ProofAudit tests passed", result.stdout)
            # Sparse invalid input proves the real 256 MiB check runs before
            # reading or parsing; this allocates no large payload in memory.
            oversized = folder / "oversized.json"
            with oversized.open("wb") as handle:
                handle.truncate(256 * 1024 * 1024 + 1)
            result = subprocess.run([lean, "-j1", "--run", str(folder / "ProofAudit.lean"),
                                     str(oversized), str(folder / "missing-targets.json")],
                                    cwd=folder, env=environment, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "rejected")
            self.assertIn("Proof export byte limit exceeded", report["reason"])


if __name__ == "__main__":
    unittest.main()
