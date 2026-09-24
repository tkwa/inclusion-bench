"""Bounded transport of candidate bytes into the fresh proof auditor."""
import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import tracemalloc
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("streaming_remote_runner", ROOT / "scripts/proofcheck/remote_runner.py")
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)


class RemoteTransportTests(unittest.TestCase):
    def test_streams_over_32_mib_without_buffering_or_parsing(self):
        chunk, repetitions = b"a" * 65536, 640
        expected = hashlib.sha256()
        for _ in range(repetitions):
            expected.update(chunk)
        command = [sys.executable, "-c", "import os\nfor _ in range(640): os.write(1, b'a' * 65536)"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            tracemalloc.start()
            try:
                with patch.object(remote.json, "loads", side_effect=AssertionError("Host must not parse candidate JSON")):
                    result = remote.capture(command, 10, stdout_path=path,
                                            stdout_limit=remote.PROOF_EXPORT_LIMIT_BYTES)
                _, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stdout_bytes, 40 * 1024 * 1024)
            self.assertEqual(path.stat().st_size, result.stdout_bytes)
            self.assertEqual(result.stdout_sha256, expected.hexdigest())
            self.assertLess(peak, 2 * 1024 * 1024, "Export accumulated in Python memory")

    def test_stream_preserves_invalid_utf8_and_hashes_original_bytes(self):
        data = b'{"bad": "\xff\xfe"}\r\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            result = remote.capture([sys.executable, "-c", f"import os; os.write(1, {data!r})"],
                                    5, stdout_path=path, stdout_limit=len(data))
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(result.stdout_sha256, hashlib.sha256(data).hexdigest())
            self.assertEqual(result.stdout_bytes, len(data))

    def test_export_overflow_deletes_partial_file_and_reaps_process(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            processes = []
            popen = subprocess.Popen

            def spawn(*args, **kwargs):
                process = popen(*args, **kwargs)
                processes.append(process)
                return process

            with patch.object(remote.subprocess, "Popen", side_effect=spawn):
                with self.assertRaisesRegex(remote.CaptureLimitError, "stdout exceeds 4096 bytes"):
                    remote.capture([sys.executable, "-c", "import os,time; os.write(1,b'a'*4097); time.sleep(30)"],
                                   5, stdout_path=path, stdout_limit=4096)
            self.assertFalse(path.exists())
            self.assertIsNotNone(processes[0].returncode)

    def test_diagnostic_limit_is_separate_from_stdout_limit(self):
        result = remote.capture([sys.executable, "-c", "import os; os.write(1,b'a'*64); os.write(2,b'b'*64)"],
                                5, stdout_limit=64, stderr_limit=64)
        self.assertEqual(result.stdout, "a" * 64)
        self.assertEqual(result.stderr, "b" * 64)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            with self.assertRaisesRegex(remote.CaptureLimitError, "stderr exceeds 64 bytes"):
                remote.capture([sys.executable, "-c", "import os; os.write(1,b'ok'); os.write(2,b'b'*65)"],
                               5, stdout_path=path, stdout_limit=1000, stderr_limit=64)
            self.assertFalse(path.exists())

    def test_timeout_removes_partial_output_and_kills_pipe_holding_descendants(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            started = time.monotonic()
            with self.assertRaisesRegex(remote.CaptureLimitError, "wall-time limit"):
                remote.capture([sys.executable, "-c",
                                "import os,time; os.write(1,b'partial'); os.fork(); time.sleep(30)"],
                               0.2, stdout_path=path)
            self.assertLess(time.monotonic() - started, 3)
            self.assertFalse(path.exists())

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            path.write_bytes(b"preserve")
            with self.assertRaises(FileExistsError):
                remote.capture([sys.executable, "-c", "print('replace')"], 5, stdout_path=path)
            self.assertEqual(path.read_bytes(), b"preserve")

    def test_container_cleanup_runs_after_timeout_overflow_or_success(self):
        for outcome in (remote.CaptureLimitError("timeout"), remote.CaptureLimitError("overflow"),
                        remote.CaptureResult(0, "", "", 0, hashlib.sha256().hexdigest())):
            with self.subTest(outcome=outcome):
                options = {"side_effect": outcome} if isinstance(outcome, Exception) else {"return_value": outcome}
                with patch.object(remote, "capture", **options), patch.object(remote.subprocess, "run") as remove:
                    if isinstance(outcome, Exception):
                        with self.assertRaises(remote.CaptureLimitError):
                            remote.capture_container(["docker", "run"], "test-container", 5)
                    else:
                        remote.capture_container(["docker", "run"], "test-container", 5)
                    self.assertEqual(remove.call_args.args[0], ["docker", "rm", "-f", "test-container"])

    def test_exact_response_wire_bound_preserves_or_rejects_whole_report(self):
        report = {"status": "needs_literature_review", "literature_dependencies": [{"statement": "λ" * 40}]}
        with patch.object(remote, "RESPONSE_LIMIT_BYTES", 100):
            encoded = remote.serialize_response(report)
        self.assertEqual(json.loads(encoded)["status"], "rejected")
        self.assertLessEqual(len(encoded.encode()) + 1, 100)
        encoded = remote.serialize_response(report)
        exact = len(encoded.encode()) + 1
        with patch.object(remote, "RESPONSE_LIMIT_BYTES", exact):
            self.assertEqual(json.loads(remote.serialize_response(report)), report)
        with patch.object(remote, "RESPONSE_LIMIT_BYTES", exact - 1):
            self.assertEqual(json.loads(remote.serialize_response(report))["status"], "rejected")

    def test_driver_cancellation_runs_capture_and_container_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            for cancellation in (signal.SIGTERM, signal.SIGHUP):
                with self.subTest(cancellation=cancellation):
                    self.check_driver_cancellation(Path(directory), cancellation)

    def check_driver_cancellation(self, directory, cancellation):
        path = directory / f"export-{cancellation}.json"
        marker = directory / f"removed-{cancellation}"
        source = f'''import importlib.util, signal, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("driver", {str(ROOT / "scripts/proofcheck/remote_runner.py")!r})
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
signal.signal(signal.SIGTERM, driver.cancel_driver)
signal.signal(signal.SIGHUP, driver.cancel_driver)
driver.subprocess.run = lambda *args, **kwargs: Path({str(marker)!r}).write_text("removed")
driver.capture_container([sys.executable, "-c", "import time; time.sleep(30)"],
                         "test-container", 30, stdout_path={str(path)!r})
'''
        process = subprocess.Popen([sys.executable, "-c", source], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 5
            while not path.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.01)
            self.assertTrue(path.exists(), "Driver never entered capture")
            process.send_signal(cancellation)
            output, error = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 128 + cancellation, output + error)
            self.assertTrue(marker.exists(), "Container cleanup was bypassed")
            self.assertFalse(path.exists(), "Partial candidate output survived cancellation")
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
            process.stdout.close()
            process.stderr.close()


if __name__ == "__main__":
    unittest.main()
