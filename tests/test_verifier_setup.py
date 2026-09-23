"""Validate cache requests without downloading or provisioning anything."""
import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[1] / "scripts/proofcheck/setup_linux.py"
SPEC = importlib.util.spec_from_file_location("verifier_setup", PATH)
SETUP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SETUP)


class VerifierSetupTests(unittest.TestCase):
    def test_explicit_additions_preserve_required_modules_and_remove_duplicates(self):
        modules = SETUP.requested_modules(["Mathlib.Data.Int.Basic", SETUP.MODULES[0], "Mathlib.Data.Int.Basic"])
        self.assertEqual(modules, [*SETUP.MODULES, "Mathlib.Data.Int.Basic"])

    def test_unqualified_paths_options_and_other_module_roots_are_rejected(self):
        for value in (["../Other"], ["Mathlib/Other.lean"], ["--all"], ["Main"],
                      ["Mathlib"], ["Mathlib.X; echo bad"], ["Mathlib.X\nimport Main"],
                      [None], "Mathlib.Data.Int.Basic"):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                SETUP.requested_modules(value)
