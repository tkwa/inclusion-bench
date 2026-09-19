import copy
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

from inclusion_bench.benchmark import Benchmark, ROOT, canonical_hash
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.evaluation import artifact_path, evaluate_run, leaderboard, run_adapter, sha256_file, taskset, validate_run


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = Benchmark()
        cls.suite = taskset(cls.b)

    def manifest(self, directory, claims=None):
        artifacts = []
        if claims:
            proof = directory / 'candidate.lean'
            proof.write_text('-- Unverified test fixture; this is not a proof.\n')
            artifacts = [{'path': proof.name, 'sha256': sha256_file(proof)}]
        return {'schema_version': 1, 'run_id': 'fixture', 'model': {'name': 'fixture', 'version': 'test-only'},
                'track': 'tool-assisted', 'dataset_sha256': self.b.digest, 'taskset_sha256': self.suite['taskset_sha256'],
                'budget': {'wall_time_seconds': 5}, 'started_at': '2026-09-19T00:00:00+00:00',
                'finished_at': '2026-09-19T00:00:01+00:00', 'attempts': [{'attempt_id': 'a1', 'task_id': 'inclusion.NP.P',
                'status': 'proof_candidate' if claims else 'unsolved', 'claims': claims or [], 'artifacts': artifacts}]}

    def test_suite_is_frozen_and_only_provisional_unknowns(self):
        suite = self.suite
        self.assertEqual({(t['left'], t['right']) for t in suite['tasks']}, self.b.unresolved)
        self.assertEqual(suite['taskset_sha256'], canonical_hash({k: v for k, v in suite.items() if k != 'taskset_sha256'}))
        self.assertEqual(suite['formalization_bundle']['definition_count'], 50)
        self.assertEqual({t['eligibility'] for t in suite['tasks']}, {'unreviewed'})

    def test_unsolved_adapter_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = run_adapter(self.b, [sys.executable, str(ROOT / 'evaluation/unsolved_adapter.py')],
                                   'Infrastructure fixture', 'not-an-AI', ['inclusion.NP.P'], Path(tmp) / 'run', 5, 'smoke-test')
            result = evaluate_run(self.b, manifest)
            self.assertEqual(result['provisional_verified_points'], 0)
            self.assertIsNone(result['official_score'])
            self.assertFalse(result['full_suite'])
            self.assertEqual(result['status'], 'not-rankable')

    def test_claimed_acceptance_is_not_verification_and_artifacts_are_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            run = self.manifest(directory, [{'relation': 'separation', 'left': 'NP', 'right': 'P'}])
            run['accepted'] = True
            run['attempts'][0]['verified'] = True
            manifest = directory / 'run.json'
            manifest.write_text(json.dumps(run))
            result = evaluate_run(self.b, manifest)
            self.assertEqual(result['provisional_verified_points'], 0)
            (directory / 'candidate.lean').write_text('changed')
            with self.assertRaisesRegex(InvalidEvidence, 'hash mismatch'):
                evaluate_run(self.b, manifest)

    def test_reviews_bind_exact_run_and_pool_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            shutil.copytree(ROOT / 'data', directory / 'data')
            benchmark = Benchmark(directory)
            run = self.manifest(directory, [{'relation': 'separation', 'left': 'NP', 'right': 'P'}])
            second = copy.deepcopy(run['attempts'][0])
            second['attempt_id'] = 'a2'
            run['attempts'].append(second)
            reviews = [{'run_sha256': canonical_hash(run), 'dataset_sha256': benchmark.digest,
                        'attempt_id': a['attempt_id'], 'attempt_sha256': canonical_hash(a), 'status': 'accepted',
                        'verified_claims': a['claims'], 'artifact_hashes': [p['sha256'] for p in a['artifacts']],
                        'verification_record': 'TEST-ONLY trusted review fixture'} for a in run['attempts']]
            (directory / 'data/ai_reviews.json').write_text(json.dumps(reviews))
            manifest = directory / 'run.json'
            manifest.write_text(json.dumps(run))
            result = evaluate_run(benchmark, manifest)
            expected = benchmark.score({'claims': run['attempts'][0]['claims']})['score']
            self.assertEqual(result['provisional_verified_points'], expected)
            self.assertEqual(result['direct_verified_pairs'], 1)
            self.assertEqual(len(result['provisional_resolutions']), expected)
            self.assertEqual(len(result['verified_claim_provenance']['separation:NP:P']), 2)
            run['run_id'] = 'another-run'
            manifest.write_text(json.dumps(run))
            self.assertEqual(evaluate_run(benchmark, manifest)['provisional_verified_points'], 0)

    def test_invalid_identity_paths_and_prompt_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            run = self.manifest(directory)
            for key, bad in [('budget', {}), ('finished_at', 'yesterday'), ('taskset_sha256', 'wrong')]:
                altered = {**run, key: bad}
                with self.assertRaises(InvalidEvidence):
                    validate_run(self.b, altered, directory)
            with self.assertRaises(InvalidEvidence):
                artifact_path(directory, '../outside.lean')
            (directory / 'link').symlink_to(ROOT / 'README.md')
            with self.assertRaises(InvalidEvidence):
                artifact_path(directory, 'link')
            run['attempts'][0]['request_path'] = 'request.json'
            run['attempts'][0]['prompt_sha256'] = 'bad'
            (directory / 'request.json').write_text('{}')
            with self.assertRaisesRegex(InvalidEvidence, 'prompt'):
                validate_run(self.b, run, directory)

    def test_malformed_adapter_response_preserves_error_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = run_adapter(self.b, [sys.executable, '-c', 'print("[]")'], 'fixture', 'test-only',
                                   ['inclusion.NP.P'], Path(tmp) / 'run', 5, 'smoke-test')
            self.assertEqual(json.loads(manifest.read_text())['attempts'][0]['status'], 'error')

    def test_adapter_deadline_includes_child_processes(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = 'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); time.sleep(30)'
            started = time.monotonic()
            manifest = run_adapter(self.b, [sys.executable, '-c', command], 'fixture', 'test-only',
                                   ['inclusion.NP.P'], Path(tmp) / 'run', 1, 'smoke-test')
            self.assertLess(time.monotonic() - started, 5)
            self.assertEqual(json.loads(manifest.read_text())['attempts'][0]['status'], 'budget_exhausted')

    def test_adapter_output_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = run_adapter(self.b, [sys.executable, '-c', 'import sys; sys.stdout.write("x" * 8_100_000)'],
                                   'fixture', 'test-only', ['inclusion.NP.P'], Path(tmp) / 'run', 5, 'smoke-test')
            run = json.loads(manifest.read_text())
            self.assertEqual(run['attempts'][0]['status'], 'error')
            self.assertIn('output limit', run['attempts'][0]['error'])
            self.assertLessEqual((manifest.parent / 'response-0001.json').stat().st_size, 8_000_000)

    def test_certified_taskset_and_separate_run_integrity_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            shutil.copytree(ROOT / 'data', directory / 'data')
            policy = json.loads((directory / 'data/policy.json').read_text())
            policy['release_stage'] = 'certified'
            (directory / 'data/policy.json').write_text(json.dumps(policy))
            benchmark = Benchmark(directory)
            manifest_data = benchmark.matrix()
            manifest_data['status'] = 'certified'
            for p in manifest_data['pairs']:
                if p['status'] == 'unreviewed':
                    p['status'] = 'open_at_cutoff'
            (directory / 'data/eligibility.json').write_text(json.dumps(manifest_data))
            suite = taskset(benchmark)
            self.assertEqual({t['eligibility'] for t in suite['tasks']}, {'open_at_cutoff'})
            self.assertEqual(suite['eligibility_manifest_sha256'], canonical_hash(manifest_data))
            run = self.manifest(directory)
            run.update(dataset_sha256=benchmark.digest, taskset_sha256=suite['taskset_sha256'])
            manifest = directory / 'run.json'
            manifest.write_text(json.dumps(run))
            result = evaluate_run(benchmark, manifest)
            self.assertIsNone(result['official_score'])
            run['attempts'] = [{'attempt_id': str(i), 'task_id': t['task_id'], 'status': 'unsolved', 'claims': [], 'artifacts': []}
                               for i, t in enumerate(suite['tasks'])]
            manifest.write_text(json.dumps(run))
            self.assertIsNone(evaluate_run(benchmark, manifest)['official_score'])
            (directory / 'data/ai_run_reviews.json').write_text(json.dumps([{
                'run_sha256': canonical_hash(run), 'dataset_sha256': benchmark.digest,
                'taskset_sha256': suite['taskset_sha256'], 'status': 'accepted', 'verification_record': 'TEST-ONLY run audit'}]))
            result = evaluate_run(benchmark, manifest)
            self.assertTrue(result['full_suite'])
            self.assertEqual(result['official_score'], 0)
            rows = leaderboard(benchmark, ['run.json'])
            self.assertEqual(rows[0]['rank'], 1)
            self.assertEqual(rows[0]['score'], 0)
            with self.assertRaisesRegex(InvalidEvidence, 'only once'):
                leaderboard(benchmark, ['run.json', 'run.json'])
            run['attempts'] = run['attempts'][:1]
            manifest.write_text(json.dumps(run))
            self.assertIsNone(evaluate_run(benchmark, manifest)['official_score'])
            with self.assertRaisesRegex(InvalidEvidence, 'not officially admissible'):
                leaderboard(benchmark, ['run.json'])


if __name__ == '__main__':
    unittest.main()
