"""Run wire-codec regressions locally without Docker or benchmark dependencies."""

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
                           ROOT / "tests" / "lean" / "ProofCodecTests.lean"):
                shutil.copyfile(source, folder / source.name)
            environment = os.environ.copy()
            environment["LEAN_PATH"] = str(folder)
            commands = [
                [lean, "-j1", "-o", str(folder / "ProofCodec.olean"), str(folder / "ProofCodec.lean")],
                [lean, "-j1", "--run", str(folder / "ProofCodecTests.lean"), "80", "80"],
            ]
            for command in commands:
                result = subprocess.run(command, cwd=folder, env=environment,
                                        capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ProofCodec tests passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
