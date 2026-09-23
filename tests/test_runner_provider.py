"""Run the actual OpenAI adapter subprocess against a loopback-only fixture.

No provider SDK, network credential, paid model, or mocked runner is involved.
Every benchmark copy and model artifact is confined to a temporary directory.
"""
import copy
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from unittest.mock import patch

from inclusion_bench.benchmark import Benchmark, ROOT, canonical_hash, read_json
from inclusion_bench.engine import InvalidEvidence
from inclusion_bench.evaluation import evaluate_run, sha256_file, validate_run
from inclusion_bench.runner import _validate_response, freeze_release, run_config


def unsolved_response(*, complete=True, include_usage=True):
    answer = {'status': 'unsolved', 'claims': [], 'proof_markdown': '',
              'lean_sources': [], 'notes': 'Infrastructure fixture; not a model evaluation.'}
    text = json.dumps(answer) if complete else '{"status":"proof_cand'
    response = {'id': 'resp_loopback_fixture', 'model': 'mock-openai-snapshot',
                'status': 'completed' if complete else 'incomplete',
                'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': text}]}]}
    if include_usage:
        response['usage'] = {'input_tokens': 100, 'output_tokens': 40, 'total_tokens': 140,
                             'output_tokens_details': {'reasoning_tokens': 17}}
    return response


class RunnerProviderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='inclusion-provider-integration-')
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / 'data', self.root / 'data')
        for relative in read_json(ROOT / 'data/formalization.json')['files']:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        shutil.copytree(ROOT / 'evaluation/adapters', self.root / 'evaluation/adapters',
                        ignore=shutil.ignore_patterns('__pycache__'))
        if (ROOT / 'support').exists():
            shutil.copytree(ROOT / 'support', self.root / 'support',
                            ignore=shutil.ignore_patterns('__pycache__', '.lake'))
        self.benchmark = Benchmark(self.root)
        freeze_release(self.benchmark)
        self.config = {'provider': 'openai', 'track': 'closed-book',
                       'model': {'name': 'MOCK INFRASTRUCTURE ONLY', 'version': 'mock-openai-snapshot'},
                       'configuration': {'reasoning_effort': 'high'},
                       'selection': {'task_ids': ['inclusion.NP.P']},
                       'budget': {'wall_time_seconds': 30, 'per_task_wall_time_seconds': 10,
                                  'max_total_tokens': 175, 'max_output_tokens_per_task': 150,
                                  'max_cpu_cores': 1, 'memory_limit_mib': 512}}
        self.requests = []
        self.replies = []
        self.unexpected_requests = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                outer.requests.append((self.path, body, dict(self.headers)))
                if outer.replies:
                    status, reply = outer.replies.pop(0)
                else:
                    outer.unexpected_requests.append(self.path)
                    status, reply = 500, {'error': {'message': 'Unexpected fixture request'}}
                raw = json.dumps(reply).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(raw)))
                self.send_header('x-request-id', 'req_loopback_fixture')
                self.end_headers()
                self.wfile.write(raw)

        self.server = HTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={'poll_interval': 0.01}, daemon=True)
        self.thread.start()
        self.environment = {'PATH': os.defpath, 'OPENAI_API_KEY': 'test-only-no-real-key',
                            'INCLUSION_API_BASE_URL': f'http://127.0.0.1:{self.server.server_port}/v1',
                            'INCLUSION_ALLOW_TEST_ENDPOINT': '1'}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    def run_provider(self, *, another_task=False, expected_attempts=1):
        config = copy.deepcopy(self.config)
        if another_task:
            config['selection']['task_ids'].append('inclusion.QMA.BQP')
        # Clearing the environment prevents accidental use of any real credential
        # or inherited endpoint. The child invokes the adapter's actual CLI.
        with patch.dict(os.environ, self.environment, clear=True):
            manifest = run_config(self.benchmark, config, self.root / 'mock-run')
        run = read_json(manifest)
        self.assertEqual(run['state'], 'sealed')
        self.assertEqual(len(run['attempts']), expected_attempts)
        self.assertFalse(self.replies, 'The subprocess did not consume the expected HTTP responses')
        self.assertFalse(self.unexpected_requests, 'The adapter retried or made an unplanned HTTP request')
        validate_run(self.benchmark, run, manifest.parent)
        self.assertIsNone(evaluate_run(self.benchmark, manifest)['official_score'])
        return manifest, run, run['attempts'][0]

    def assert_evidence_preserved(self, manifest, run, attempt):
        self.assertTrue(attempt['artifacts'])
        for artifact in attempt['artifacts']:
            self.assertEqual(sha256_file(manifest.parent / artifact['path']), artifact['sha256'])
            self.assertEqual(run['evidence_index'][artifact['path']], artifact['sha256'])
        self.assertIn(attempt['request_path'], run['evidence_index'])
        for relative, digest in run['evidence_index'].items():
            path = manifest.parent / relative
            self.assertEqual(sha256_file(path), digest)
            self.assertNotIn('test-only-no-real-key', path.read_text())
        self.assertNotIn('test-only-no-real-key', manifest.read_text())
        return {Path(a['path']).name: manifest.parent / a['path'] for a in attempt['artifacts']}

    def test_unsolved_subprocess_seals_usage_and_respects_remaining_budget(self):
        self.replies = [(200, {'input_tokens': 100}), (200, unsolved_response())]
        manifest, run, attempt = self.run_provider()
        self.assertEqual(attempt['status'], 'unsolved')
        self.assertEqual(attempt['claims'], [])
        self.assertTrue(attempt['usage_complete'])
        self.assertTrue(attempt['request_made'])
        self.assertEqual(attempt['provider_model'], 'mock-openai-snapshot')
        self.assertEqual(attempt['usage']['reasoning_tokens'], 17)
        self.assertEqual(attempt['budget_charge_tokens'], 140)
        self.assertEqual(run['usage'], {'charged_tokens': 140, 'measured_input_tokens': 100,
                                       'measured_output_tokens': 40})
        self.assertEqual([request[0] for request in self.requests],
                         ['/v1/responses/input_tokens', '/v1/responses'])
        payload = self.requests[1][1]
        self.assertEqual(payload['model'], 'mock-openai-snapshot')
        self.assertEqual(payload['max_output_tokens'], 75)  # 175 quota minus 100 counted input
        self.assertEqual(payload['reasoning'], {'effort': 'high'})
        self.assertTrue(payload['text']['format']['strict'])
        self.assertNotIn('tools', payload)
        material = json.loads(payload['input'][0]['content'])
        bundle = read_json(self.root / 'data/formalization.json')
        self.assertEqual(material['formalization_bundle'], bundle)
        sources = material['formalizations']
        self.assertTrue(sources['TrustedBaseline.lean'].strip())
        for relative in bundle['files']:
            if relative.endswith('.lean'):
                self.assertEqual(sources[relative], (self.root / relative).read_text())
        support = material['submission_support']
        self.assertTrue(support['theorems'])
        self.assertEqual(support['cutoff'], self.benchmark.policy['cutoff'])
        for relative, body in support['lean_sources'].items():
            self.assertTrue(relative.startswith('support/'))
            self.assertEqual(body, (self.root / relative).read_text())
        config = read_json(manifest.parent / 'config.json')
        self.assertEqual(config['submission_support_sha256'], canonical_hash(support))
        files = self.assert_evidence_preserved(manifest, run, attempt)
        self.assertIn('generation-response.json', files)
        self.assertIn('model-output.txt', files)
        self.assertIn('transcript.json', files)
        self.assertEqual(read_json(files['generation-response.json'])['id'], 'resp_loopback_fixture')

    def test_literature_request_is_sealed_and_forwarded_to_explicit_proof_check(self):
        dependency = {'name': 'Literature.fixture', 'statement': 'True',
                      'sources': [{'title': 'Infrastructure fixture', 'url': 'https://example.com/paper',
                                   'locator': 'Theorem 1', 'publication_date': '1994'}],
                      'rationale': 'Fixture only; this is not a real submitted mathematical result.'}
        proof = {'status': 'proof_candidate',
                 'claims': [{'relation': 'inclusion', 'left': 'NP', 'right': 'P'}],
                 'proof_markdown': 'Infrastructure fixture only.',
                 'lean_sources': [{'filename': 'Result.lean', 'content': 'axiom Literature.fixture : True\n-- fixture only'}],
                 'literature_requests': [dependency], 'notes': 'No real proof is asserted.'}
        response = unsolved_response()
        response['output'][0]['content'][0]['text'] = json.dumps(proof)
        self.replies = [(200, {'input_tokens': 100}), (200, response)]
        manifest, run, attempt = self.run_provider()
        self.assertEqual(attempt['status'], 'proof_candidate')
        self.assertEqual(attempt['literature_requests'], [dependency])
        files = self.assert_evidence_preserved(manifest, run, attempt)
        self.assertEqual(read_json(files['literature.json']), {'requests': [dependency]})
        from inclusion_bench.submissions import check_submission
        with patch('inclusion_bench.submissions.verify_proof', return_value={'status': 'needs_literature_review'}) as verify:
            result = check_submission(self.benchmark, files['proof.lean'].parent)
        self.assertEqual(result['status'], 'needs_literature_review')
        self.assertEqual(verify.call_args.kwargs['literature_requests'], [dependency])
        self.assertIn(sha256_file(verify.call_args.args[1]), {item['sha256'] for item in attempt['artifacts']})

    def test_runner_rejects_post_cutoff_literature_before_sealing_an_attempt(self):
        request = {'name': 'Literature.future', 'statement': 'True',
                   'sources': [{'title': 'Future fixture', 'url': 'https://example.com/paper',
                                'locator': 'Theorem 1', 'publication_date': '2099'}],
                   'rationale': 'Fixture only'}
        response = {'status': 'proof_candidate',
                    'claims': [{'relation': 'inclusion', 'left': 'NP', 'right': 'P'}],
                    'artifacts': ['proof.lean'], 'literature_requests': [request]}
        with self.assertRaisesRegex(InvalidEvidence, 'cutoff'):
            _validate_response(self.benchmark, response, self.root, self.root, 100, 'openai')

    def test_multifile_provider_project_survives_runner_and_submission_check(self):
        proof = {'status': 'proof_candidate',
                 'claims': [{'relation': 'inclusion', 'left': 'NP', 'right': 'P'}],
                 'proof_markdown': 'Infrastructure fixture only; no proof is claimed.',
                 'lean_entrypoint': 'Main',
                 'lean_sources': [
                     {'filename': 'Main.lean', 'content': 'import Lemmas.Basic\n-- fixture\n'},
                     {'filename': 'Lemmas/Basic.lean', 'content': 'import TrustedBaseline\ntheorem fixture_helper : True := True.intro\n'},
                 ], 'literature_requests': [], 'notes': 'Fixture only.'}
        response = unsolved_response()
        response['output'][0]['content'][0]['text'] = json.dumps(proof)
        self.replies = [(200, {'input_tokens': 100}), (200, response)]
        manifest, run, attempt = self.run_provider()
        self.assertEqual(attempt['status'], 'proof_candidate', attempt.get('error'))
        self.assert_evidence_preserved(manifest, run, attempt)
        project_manifest = manifest.parent / attempt['submission_manifest']
        project = project_manifest.parent
        from inclusion_bench.proofbundle import load_proof_bundle
        bundle = load_proof_bundle(project)
        self.assertEqual(bundle.entrypoint, 'Main')
        sealed = {item['path']: item['sha256'] for item in attempt['artifacts']}
        for relative, digest in bundle.metadata['files'].items():
            self.assertEqual(sealed[str((project / relative).relative_to(manifest.parent))], digest)
        self.assertNotIn(bundle.proof_sha256, sealed.values())
        from inclusion_bench.submissions import check_submission
        with patch('inclusion_bench.submissions.verify_proof', return_value={'status': 'rejected'}) as verify:
            check_submission(self.benchmark, project)
        self.assertEqual(verify.call_args.args[1], project)
        self.assertEqual(verify.call_args.args[2][0]['theorem'], 'Submission.result_1')

        # The adapter may not drop an imported helper or project metadata from
        # its artifact list, even when those files are still present on disk.
        attempt_dir = (manifest.parent / attempt['request_path']).parent
        raw_response = read_json(attempt_dir / 'response.json')
        for suffix in ('Lemmas/Basic.lean', 'submission.json', 'claims.json', 'literature.json'):
            partial = {**raw_response, 'artifacts': [name for name in raw_response['artifacts'] if not name.endswith('/' + suffix)]}
            with self.subTest(suffix=suffix), self.assertRaisesRegex(InvalidEvidence, 'sealed artifact'):
                _validate_response(self.benchmark, partial, attempt_dir, manifest.parent, 175, 'openai')

        changed = read_json(project / 'claims.json')
        changed['claims'][0]['left'] = 'P'
        (project / 'claims.json').write_text(json.dumps(changed))
        with self.assertRaisesRegex(InvalidEvidence, 'match the submitted ordinary claims'):
            _validate_response(self.benchmark, raw_response, attempt_dir, manifest.parent, 175, 'openai')

    def test_unsolved_multifile_work_is_preserved_without_becoming_a_candidate(self):
        response = unsolved_response()
        answer = json.loads(response['output'][0]['content'][0]['text'])
        answer.update(lean_entrypoint='Main', lean_sources=[
            {'filename': 'Main.lean', 'content': 'import Lemmas.Partial\n'},
            {'filename': 'Lemmas/Partial.lean', 'content': 'import TrustedBaseline\n-- Unfinished argument.\n'},
        ])
        response['output'][0]['content'][0]['text'] = json.dumps(answer)
        self.replies = [(200, {'input_tokens': 100}), (200, response)]
        manifest, run, attempt = self.run_provider()
        self.assertEqual(attempt['status'], 'unsolved', attempt.get('error'))
        self.assertEqual(attempt['claims'], [])
        self.assertNotIn('submission_manifest', attempt)
        self.assertEqual(attempt['budget_charge_tokens'], 140)
        self.assertEqual(run['usage']['charged_tokens'], 140)
        artifacts = self.assert_evidence_preserved(manifest, run, attempt)
        self.assertEqual(read_json(artifacts['submission.json'])['files'],
                         ['Main.lean', 'Lemmas/Partial.lean'])
        self.assertEqual(artifacts['Partial.lean'].read_text(), answer['lean_sources'][1]['content'])

    def test_token_count_exhaustion_stops_without_a_generation_charge(self):
        self.replies = [(200, {'input_tokens': 176})]
        manifest, run, attempt = self.run_provider(another_task=True)
        self.assertEqual(attempt['status'], 'budget_exhausted')
        self.assertFalse(attempt['request_made'])
        self.assertTrue(attempt['usage_complete'])
        self.assertEqual(attempt['budget_charge_tokens'], 0)
        self.assertEqual(run['usage']['charged_tokens'], 0)
        self.assertEqual(run['unattempted_task_ids'], ['inclusion.QMA.BQP'])
        self.assertEqual([request[0] for request in self.requests], ['/v1/responses/input_tokens'])
        self.assert_evidence_preserved(manifest, run, attempt)

    def test_second_task_receives_only_the_unspent_run_quota(self):
        self.replies = [(200, {'input_tokens': 100}), (200, unsolved_response()),
                        (200, {'input_tokens': 36})]
        manifest, run, first = self.run_provider(another_task=True, expected_attempts=2)
        second = run['attempts'][1]
        self.assertEqual(first['status'], 'unsolved')
        self.assertEqual(second['status'], 'budget_exhausted')
        self.assertFalse(second['request_made'])
        self.assertEqual(second['budget_charge_tokens'], 0)
        self.assertEqual(run['usage']['charged_tokens'], 140)
        self.assertEqual(run['unattempted_task_ids'], [])
        request = read_json(manifest.parent / second['request_path'])
        self.assertEqual(request['limits']['max_total_tokens_remaining'], 35)
        self.assertEqual(request['limits']['max_output_tokens'], 35)
        self.assertEqual([request[0] for request in self.requests],
                         ['/v1/responses/input_tokens', '/v1/responses', '/v1/responses/input_tokens'])
        self.assert_evidence_preserved(manifest, run, first)
        self.assert_evidence_preserved(manifest, run, second)

    def test_generation_error_preserves_unknown_usage_and_charges_the_remaining_quota(self):
        self.replies = [(200, {'input_tokens': 100}),
                        (429, {'error': {'message': 'Rate limit fixture test-only-no-real-key'}})]
        manifest, run, attempt = self.run_provider(another_task=True)
        self.assertEqual(attempt['status'], 'error')
        self.assertFalse(attempt['usage_complete'])
        self.assertTrue(attempt['request_made'])
        self.assertIsNone(attempt['usage']['total_tokens'])
        self.assertEqual(attempt['budget_charge_tokens'], 175)
        self.assertEqual(run['usage'], {'charged_tokens': 175, 'measured_input_tokens': 0,
                                       'measured_output_tokens': 0})
        self.assertEqual(run['unattempted_task_ids'], ['inclusion.QMA.BQP'])
        self.assertEqual(len(self.requests), 2)
        files = self.assert_evidence_preserved(manifest, run, attempt)
        self.assertIn('generation-response.json', files)
        self.assertIn('Rate limit fixture', files['generation-response.json'].read_text())

    def test_truncated_generation_preserves_partial_output_and_actual_usage(self):
        self.replies = [(200, {'input_tokens': 100}), (200, unsolved_response(complete=False))]
        manifest, run, attempt = self.run_provider(another_task=True)
        self.assertEqual(attempt['status'], 'budget_exhausted')
        self.assertTrue(attempt['usage_complete'])
        self.assertTrue(attempt['request_made'])
        self.assertEqual(attempt['claims'], [])
        self.assertEqual(attempt['budget_charge_tokens'], 140)
        self.assertEqual(run['usage']['charged_tokens'], 140)
        self.assertEqual(run['unattempted_task_ids'], ['inclusion.QMA.BQP'])
        files = self.assert_evidence_preserved(manifest, run, attempt)
        self.assertEqual(files['model-output.txt'].read_text(), '{"status":"proof_cand')

    def test_completed_response_without_usage_preserves_answer_but_exhausts_quota(self):
        self.replies = [(200, {'input_tokens': 100}), (200, unsolved_response(include_usage=False))]
        manifest, run, attempt = self.run_provider(another_task=True)
        self.assertEqual(attempt['status'], 'unsolved')
        self.assertFalse(attempt['usage_complete'])
        self.assertTrue(attempt['request_made'])
        self.assertIsNone(attempt['usage']['total_tokens'])
        self.assertEqual(run['usage']['charged_tokens'], 175)
        self.assertEqual(run['unattempted_task_ids'], ['inclusion.QMA.BQP'])
        self.assert_evidence_preserved(manifest, run, attempt)


if __name__ == '__main__':
    unittest.main()
