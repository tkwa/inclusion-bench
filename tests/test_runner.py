import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark, ROOT, canonical_hash, read_json
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.evaluation import evaluate_run, sha256_file, validate_run
from inclusion_bench.reviews import record_run_review, record_proof_review, record_history_review, review_packet, publish_run
from inclusion_bench.runner import freeze_release, frozen_release, normalize_config, preflight, run_config


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / 'data', self.root / 'data')
        for relative in read_json(ROOT / 'data/formalization.json')['files']:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.b = Benchmark(self.root)
        freeze_release(self.b)
        self.config = {'provider': 'custom', 'track': 'closed-book', 'model': {'name': 'TEST FIXTURE', 'version': 'not-an-AI'},
            'selection': {'task_ids': ['inclusion.NP.P']},
            'budget': {'wall_time_seconds': 30, 'per_task_wall_time_seconds': 10, 'max_total_tokens': 1000,
                       'max_output_tokens_per_task': 100, 'max_cpu_cores': 1, 'memory_limit_mib': 4096},
            'adapter': [sys.executable, '-c', 'import json; print(json.dumps({"status":"unsolved","claims":[],"artifacts":[],"usage":{"input_tokens":10,"output_tokens":2,"total_tokens":12},"usage_complete":True,"request_made":True,"budget_charge_tokens":12}))']}

    def tearDown(self):
        self.temporary.cleanup()

    def accept_run(self, manifest):
        run = read_json(manifest)
        return record_run_review(self.b, manifest, {'run_sha256': canonical_hash(run), 'status': 'accepted',
            'reviewer': 'TEST ONLY', 'rationale': 'Synthetic run-integrity fixture, never a model result',
            'checks': {k: True for k in ('model_identity', 'configuration_and_tools', 'budgets_and_usage',
                                        'transcripts_and_artifacts', 'no_unreported_human_assistance')}})

    def candidate(self):
        config = copy.deepcopy(self.config)
        claim = {'relation': 'separation', 'left': 'NP', 'right': 'P'}
        config['adapter'] = [sys.executable, '-c', 'from pathlib import Path; import json; Path("candidate.lean").write_text("-- TEST ONLY; not a proof\\n"); print(json.dumps(' + repr({
            'status': 'proof_candidate', 'claims': [claim], 'artifacts': ['candidate.lean'],
            'usage': {'total_tokens': 12}, 'budget_charge_tokens': 12, 'usage_complete': True, 'request_made': True}) + '))']
        return run_config(self.b, config, self.root / 'candidate-run')

    def test_zero_run_can_be_reviewed_without_certifying_every_question_open(self):
        manifest = run_config(self.b, self.config, self.root / 'zero-run')
        run = read_json(manifest)
        self.assertEqual(run['state'], 'sealed')
        self.assertEqual(run['usage']['charged_tokens'], 12)
        self.assertTrue(run['evidence_index'])
        self.assertIsNone(evaluate_run(self.b, manifest)['official_score'])
        self.accept_run(manifest)
        result = evaluate_run(self.b, manifest)
        self.assertEqual(result['official_score'], 0)
        self.assertEqual(result['scope'], 'declared-subset')
        self.assertFalse(result['history_pending_pairs'])
        (manifest.parent / run['attempts'][0]['request_path']).write_text('{}')
        with self.assertRaisesRegex(InvalidEvidence, 'evidence hash mismatch'):
            evaluate_run(self.b, manifest)

    def test_candidates_need_both_proof_and_per_point_historical_review(self):
        manifest = self.candidate()
        run = read_json(manifest)
        self.accept_run(manifest)
        self.assertEqual(evaluate_run(self.b, manifest)['pending_attempt_ids'], ['attempt-0001'])
        attempt = run['attempts'][0]
        review = {'run_sha256': canonical_hash(run), 'attempt_id': attempt['attempt_id'],
            'attempt_sha256': canonical_hash(attempt), 'status': 'accepted', 'reviewer': 'TEST ONLY',
            'rationale': 'Tests registry binding with synthetic verifier evidence; not mathematics', 'verified_claims': attempt['claims']}
        with self.assertRaisesRegex(InvalidEvidence, 'sandboxed Lean'):
            record_proof_review(self.b, manifest, review)
        # The real checker is tested independently against actual Lean in test_proofcheck.
        # This isolated fake report only exercises the trusted-review/data flow.
        report = {'status': 'verified', 'dataset_sha256': self.b.digest, 'claims': attempt['claims'],
                  'source_sha256': attempt['artifacts'][0]['sha256'], 'test_only': True}
        report_file = self.root / 'TEST-ONLY-report.json'
        report_file.write_text(json.dumps(report))
        review['proof_report'] = str(report_file)
        record_proof_review(self.b, manifest, review)
        result = evaluate_run(self.b, manifest)
        self.assertIsNone(result['official_score'])
        self.assertGreater(len(result['history_pending_pairs']), 1)
        history = {'dataset_sha256': self.b.digest, 'status': 'accepted', 'reviewer': 'TEST ONLY',
            'rationale': 'Synthetic history fixture, never publish', 'pairs': [{**p, 'status': 'open_at_cutoff',
               'evidence': ['TEST ONLY'], 'rationale': 'TEST ONLY'} for p in result['history_pending_pairs']]}
        record_history_review(self.b, history)
        scored = evaluate_run(self.b, manifest)
        self.assertEqual(scored['official_score'], result['provisional_verified_points'])
        # A later correction excludes an already-known pair instead of awarding it.
        history['pairs'] = [{**history['pairs'][0], 'status': 'known_at_cutoff'}]
        record_history_review(self.b, history)
        self.assertEqual(evaluate_run(self.b, manifest)['official_score'], scored['official_score'] - 1)
        # A later proof rejection revokes its old accepted record.
        review['status'] = 'rejected'
        record_proof_review(self.b, manifest, review)
        self.assertEqual(evaluate_run(self.b, manifest)['official_score'], 0)

    def test_budget_stops_later_tasks_and_preserves_usage(self):
        config = copy.deepcopy(self.config)
        config['selection'] = {'task_ids': ['inclusion.NP.P', 'inclusion.QMA.BQP']}
        config['budget']['max_total_tokens'] = 10
        manifest = run_config(self.b, config, self.root / 'budget-run')
        run = read_json(manifest)
        self.assertEqual(len(run['attempts']), 1)
        self.assertEqual(run['unattempted_task_ids'], ['inclusion.QMA.BQP'])
        self.assertEqual(run['usage']['charged_tokens'], 12)
        self.assertIsNone(evaluate_run(self.b, manifest)['official_score'])

    def test_unknown_remote_usage_does_not_get_a_fresh_quota_on_resume(self):
        with patch('inclusion_bench.runner.execute_adapter', side_effect=SystemExit('simulated process loss')):
            with self.assertRaises(SystemExit):
                run_config(self.b, self.config, self.root / 'interrupted')
        manifest = self.root / 'interrupted/run.json'
        self.assertEqual(read_json(manifest)['state'], 'running')
        resumed = run_config(self.b, self.config, manifest.parent, resume=True)
        run = read_json(resumed)
        self.assertEqual(run['state'], 'sealed')
        self.assertEqual(run['usage']['charged_tokens'], 1000)
        self.assertEqual(run['attempts'][0]['status'], 'error')
        with self.assertRaisesRegex(InvalidEvidence, 'immutable'):
            run_config(self.b, self.config, manifest.parent, resume=True)

    def test_preflight_has_no_network_or_model_execution(self):
        with patch('inclusion_bench.runner.execute_adapter', side_effect=AssertionError('must not execute')):
            result = preflight(self.b, self.config)
        self.assertTrue(result['ready'])
        self.assertFalse(result['network_requests_made'])
        bad = {**self.config, 'api_key': 'fake-secret'}
        with self.assertRaisesRegex(InvalidEvidence, 'credentials'):
            normalize_config(self.b, bad)
        changed = self.root / next(iter(read_json(self.root / 'data/formalization.json')['files']))
        changed.write_text(changed.read_text() + '\n-- changed\n')
        with self.assertRaisesRegex(InvalidEvidence, 'source is missing or changed'):
            frozen_release(self.b)

    def test_review_packet_and_binding_requirements(self):
        manifest = run_config(self.b, self.config, self.root / 'packet-run')
        packet = review_packet(self.b, manifest)
        self.assertEqual(packet['run_review']['status'], 'pending')
        self.assertEqual(packet['proof_reviews'], [])
        with self.assertRaisesRegex(InvalidEvidence, 'all provenance'):
            record_run_review(self.b, manifest, {'run_sha256': packet['run_sha256'], 'reviewer': 'TEST',
                              'rationale': 'Incomplete review', 'status': 'accepted', 'checks': {}})

    def test_tampered_identity_usage_and_missing_capture_are_rejected(self):
        manifest = run_config(self.b, self.config, self.root / 'tamper-run')
        original = read_json(manifest)
        for mutate in (
            lambda r: r['model'].update(version='different-model'),
            lambda r: r['usage'].update(charged_tokens=0),
            lambda r: r['tools'].update(access_policy={}),
            lambda r: r.update(unattempted_task_ids=['inclusion.NP.P']),
            lambda r: r['evidence_index'].pop('attempts/0001/response.json'),
        ):
            run = copy.deepcopy(original)
            mutate(run)
            with self.assertRaises(InvalidEvidence):
                validate_run(self.b, run, manifest.parent)

    def test_model_identity_and_undercharged_usage_fail_closed(self):
        wrong = {**self.config, 'provider': 'openai', 'configuration': {'model_id': 'other'}}
        with self.assertRaisesRegex(InvalidEvidence, 'model.version'):
            normalize_config(self.b, wrong)
        config = copy.deepcopy(self.config)
        config['adapter'] = [sys.executable, '-c', 'import json; print(json.dumps({"status":"unsolved","claims":[],"artifacts":[],"usage":{"total_tokens":50},"usage_complete":True,"request_made":True,"budget_charge_tokens":1}))']
        manifest = run_config(self.b, config, self.root / 'undercharged')
        run = read_json(manifest)
        self.assertEqual(run['attempts'][0]['status'], 'error')
        self.assertEqual(run['usage']['charged_tokens'], 1000)
        self.accept_run(manifest)
        self.assertIsNone(evaluate_run(self.b, manifest)['official_score'])

    def test_versioned_freeze_is_idempotent_and_rejects_replacement(self):
        before = read_json(self.root / 'data/freeze.json')
        self.assertEqual(freeze_release(self.b), before)
        policy = read_json(self.root / 'data/policy.json')
        policy['test_only_note'] = 'change dataset'
        (self.root / 'data/policy.json').write_text(json.dumps(policy))
        with self.assertRaisesRegex(InvalidEvidence, 'new policy.version'):
            freeze_release(Benchmark(self.root))

    def test_publication_packages_only_reviewed_sealed_evidence(self):
        manifest = run_config(self.b, self.config, self.root / 'TEST-ONLY-publish')
        with self.assertRaisesRegex(InvalidEvidence, 'officially admissible'):
            publish_run(self.b, manifest)
        self.accept_run(manifest)
        (manifest.parent / 'unsealed-private-file.txt').write_text('DO NOT PUBLISH')
        result = publish_run(self.b, manifest)
        published = self.root / result['packaged']
        self.assertTrue(published.is_file())
        self.assertFalse((published.parent / 'unsealed-private-file.txt').exists())
        self.assertEqual(read_json(published), read_json(manifest))
        self.assertEqual(publish_run(self.b, manifest)['official_score'], 0)
        self.assertEqual(read_json(self.root / 'data/leaderboard_runs.json'), [result['packaged']])


if __name__ == '__main__':
    unittest.main()
