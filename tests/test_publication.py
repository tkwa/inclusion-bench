import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from inclusion_bench.benchmark import Benchmark, ROOT, read_json
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.evaluation import taskset
from scripts.build_release import publication_metadata


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / 'data', self.root / 'data')
        (self.root / 'research').mkdir()
        shutil.copyfile(ROOT / 'research/baseline-audit.json',
                        self.root / 'research/baseline-audit.json')
        for relative in read_json(ROOT / 'data/formalization.json')['files']:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.benchmark = Benchmark(self.root)
        self.suite = taskset(self.benchmark)
        self.record_path = self.root / 'data/publication.json'
        self.record = read_json(self.record_path)

    def test_publication_preserves_frozen_inputs_and_task_identity(self):
        paths = [self.root / p for p in (
            'data/policy.json', 'data/freeze.json', 'data/history_reviews.json',
            'research/baseline-audit.json')]
        before = [p.read_bytes() for p in paths]
        result = publication_metadata(self.benchmark, self.suite)
        self.assertEqual(result['release_status'], 'published')
        self.assertEqual(result['repository_ref'], 'v0.4.0')
        self.assertEqual(result['publication']['dataset_sha256'], self.benchmark.digest)
        self.assertEqual(self.benchmark.policy['release_status'], 'provisional')
        self.assertEqual(before, [p.read_bytes() for p in paths])
        self.assertEqual(taskset(Benchmark(self.root)), self.suite)

    def test_wrong_release_bindings_are_rejected(self):
        for field in ('benchmark_version', 'dataset_sha256', 'taskset_sha256',
                      'formalization_bundle_sha256', 'freeze_sha256',
                      'baseline_audit_sha256', 'repository_ref'):
            with self.subTest(field=field):
                wrong = copy.deepcopy(self.record)
                wrong[field] = 'another-release'
                self.record_path.write_text(json.dumps(wrong))
                with self.assertRaises(InvalidEvidence):
                    publication_metadata(self.benchmark, self.suite)

    def test_changed_audit_cannot_reuse_publication(self):
        path = self.root / 'research/baseline-audit.json'
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaises(InvalidEvidence):
            publication_metadata(self.benchmark, self.suite)

    def test_snapshot_without_publication_keeps_review_metadata(self):
        self.record_path.unlink()
        result = publication_metadata(self.benchmark, self.suite)
        self.assertEqual(result['release_status'], 'provisional')
        self.assertEqual(result['repository_ref'], 'provisional-v0.4.0')
        self.assertIsNone(result['publication'])


if __name__ == '__main__':
    unittest.main()
