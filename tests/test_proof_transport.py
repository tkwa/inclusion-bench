"""Exercise the caller's response bounds with real child processes."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from inclusion_bench.proofcheck import _run_verifier


class ProofTransportTests(unittest.TestCase):
    def run_child(self, source, *, request="{}", timeout=5):
        return _run_verifier([sys.executable, "-c", source], input=request, timeout=timeout)

    def test_large_request_does_not_deadlock_early_diagnostics(self):
        request = json.dumps({"source": "λ" * 200000})
        result = self.run_child(
            "import sys,json; sys.stderr.write('d'*200000); sys.stderr.flush(); "
            "print(json.dumps({'length':len(json.load(sys.stdin)['source'])}))",
            request=request)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {"length": 200000})
        self.assertEqual(len(result.stderr), 200000)

    def test_stdout_exact_byte_boundary_and_one_byte_over(self):
        with patch("inclusion_bench.proofcheck.MAX_VERIFIER_RESPONSE_BYTES", 1024):
            result = self.run_child("import os; os.write(1, 'λ'.encode()*512)")
            self.assertEqual(result.stdout, "λ" * 512)
            with self.assertRaisesRegex(ValueError, "response exceeded"):
                self.run_child("import os; os.write(1, 'λ'.encode()*512+b'x')")

    def test_diagnostics_have_independent_limit(self):
        with patch("inclusion_bench.proofcheck.MAX_VERIFIER_DIAGNOSTIC_BYTES", 1024):
            with self.assertRaisesRegex(ValueError, "diagnostics exceeded"):
                self.run_child("import os; os.write(1,b'{}'); os.write(2,b'x'*1025)")

    def test_timeout_with_open_and_closed_pipes(self):
        for close in (False, True):
            with self.subTest(close=close):
                source = "import os,time; " + ("os.close(1); os.close(2); " if close else "")
                started = time.monotonic()
                with self.assertRaisesRegex(ValueError, "timed out"):
                    self.run_child(source + "time.sleep(10)", timeout=0.2)
                self.assertLess(time.monotonic() - started, 3)

    def test_exit_code_and_invalid_utf8_are_preserved(self):
        result = self.run_child("import sys; print('{}'); sys.exit(7)")
        self.assertEqual(result.returncode, 7)
        with self.assertRaises(UnicodeDecodeError):
            self.run_child("import os; os.write(1,b'\\xff')")

    def test_timeout_allows_driver_cleanup_and_bounds_unresponsive_shutdown(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "cleanup"
            source = ("import signal,time\n"
                      "from pathlib import Path\n"
                      "def stop(signum, frame): raise SystemExit(143)\n"
                      "signal.signal(signal.SIGTERM, stop)\n"
                      "try: time.sleep(30)\n"
                      f"finally: time.sleep(0.05); Path({str(marker)!r}).write_text('removed')\n")
            with self.assertRaisesRegex(ValueError, "timed out"):
                self.run_child(source, timeout=0.2)
            self.assertEqual(marker.read_text(), "removed")
        with patch("inclusion_bench.proofcheck.VERIFIER_SHUTDOWN_GRACE_SECONDS", 0.2):
            started = time.monotonic()
            with self.assertRaisesRegex(ValueError, "timed out"):
                self.run_child("import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)",
                               timeout=0.2)
            self.assertLess(time.monotonic() - started, 3)
