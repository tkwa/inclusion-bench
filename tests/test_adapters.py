"""Provider protocol tests use a loopback server and fake credentials only."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('inclusion_provider_adapter', ROOT / 'evaluation/adapters/provider.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def answer(status='unsolved'):
    return {'status': status, 'claims': [] if status == 'unsolved' else [
        {'relation': 'separation', 'left': 'NP', 'right': 'P'}],
        'proof_markdown': '' if status == 'unsolved' else 'A mock proof, for testing only.',
        'lean_sources': [] if status == 'unsolved' else [{'filename': 'Result.lean', 'content': '-- fixture only\n'}],
        'notes': 'This is a test fixture, not a mathematical result.'}


def openai_response(proof=None, status='completed', usage=True):
    response = {'id': 'resp_mock', 'model': 'explicit-snapshot-123', 'status': status,
                'output': [{'type': 'reasoning', 'summary': []}, {'type': 'message', 'content': [
                    {'type': 'output_text', 'text': json.dumps(proof if proof is not None else answer())}]}]}
    if usage:
        response['usage'] = {'input_tokens': 100, 'output_tokens': 40, 'total_tokens': 140,
                             'output_tokens_details': {'reasoning_tokens': 17}}
    return response


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.requests = []
        self.replies = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                outer.requests.append((self.path, body, dict(self.headers)))
                status, reply, delay = outer.replies.pop(0)
                if delay:
                    time.sleep(delay)
                raw = reply if isinstance(reply, bytes) else json.dumps(reply).encode()
                try:
                    self.send_response(status)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(raw)))
                    self.send_header('x-request-id', 'request_mock')
                    self.end_headers()
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        self.server = HTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        self.thread.start()
        self.env = {'OPENAI_API_KEY': 'mock-secret-key', 'ANTHROPIC_API_KEY': 'mock-anthropic-key',
                    'INCLUSION_API_BASE_URL': f'http://127.0.0.1:{self.server.server_port}/v1',
                    'INCLUSION_ALLOW_TEST_ENDPOINT': '1'}
        self.request = {'task': {'task_id': 'inclusion.NP.P', 'prompt': 'Resolve NP ⊆ P.'},
                        'classes': {'classes': [{'id': 'P'}, {'id': 'NP'}]}, 'knowledge': {'facts': []},
                        'model': {'name': 'explicit-model', 'version': 'explicit-snapshot-123'},
                        'configuration': {}, 'limits': {'max_output_tokens': 500, 'max_total_tokens_remaining': 800},
                        'time_remaining_seconds': 4}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def invoke(self, provider='openai'):
        return adapter.run(self.request, provider, self.directory, self.env)

    def assert_preserved(self, result):
        self.assertTrue(result['artifacts'])
        self.assertNotIn('mock-secret-key', json.dumps(result))
        self.assertNotIn('mock-anthropic-key', json.dumps(result))
        for relative in result['artifacts']:
            self.assertTrue((self.directory / relative).is_file())
            self.assertNotIn('mock-secret-key', (self.directory / relative).read_text())
            self.assertNotIn('mock-anthropic-key', (self.directory / relative).read_text())

    def test_openai_exact_model_schema_proof_and_reasoning_accounting(self):
        self.replies = [(200, {'input_tokens': 100}, 0), (200, openai_response(answer('proof_candidate')), 0)]
        self.request['limits']['remaining_output_tokens'] = 120
        self.request['configuration']['reasoning_effort'] = 'high'
        result = self.invoke()
        self.assertEqual(result['status'], 'proof_candidate')
        self.assertEqual(result['budget_charge_tokens'], 140)
        self.assertEqual(result['usage']['reasoning_tokens'], 17)
        self.assertEqual(result['usage']['total_tokens'], 140)  # reasoning is already included
        self.assertEqual([r[0] for r in self.requests], ['/v1/responses/input_tokens', '/v1/responses'])
        payload = self.requests[1][1]
        self.assertEqual(payload['model'], 'explicit-snapshot-123')
        self.assertEqual(payload['max_output_tokens'], 120)
        self.assertEqual(payload['reasoning'], {'effort': 'high'})
        self.assertTrue(payload['text']['format']['strict'])
        self.assertFalse(payload['store'])
        self.assertNotIn('tools', payload)
        self.assertTrue(any(p.endswith('/proof.md') for p in result['artifacts']))
        self.assertTrue(any(p.endswith('/lean/Result.lean') for p in result['artifacts']))
        self.assert_preserved(result)

    def test_anthropic_schema_cache_usage_and_total_budget_reservation(self):
        response = {'id': 'msg_mock', 'model': 'explicit-snapshot-123', 'stop_reason': 'end_turn',
                    'content': [{'type': 'text', 'text': json.dumps(answer())}],
                    'usage': {'input_tokens': 100, 'cache_read_input_tokens': 30, 'cache_creation_input_tokens': 20,
                              'output_tokens': 40, 'output_tokens_details': {'thinking_tokens': 10}}}
        self.replies = [(200, {'input_tokens': 100}, 0), (200, response, 0)]
        result = self.invoke('anthropic')
        self.assertEqual(result['status'], 'unsolved')
        self.assertEqual(result['usage']['input_tokens'], 150)
        self.assertEqual(result['budget_charge_tokens'], 190)
        self.assertEqual(self.requests[1][1]['max_tokens'], 444)  # 800 - 100 - reserve256
        self.assertEqual(self.requests[1][2]['anthropic-version'], '2023-06-01')
        self.assertEqual(self.requests[1][1]['output_config']['format']['type'], 'json_schema')
        self.assertEqual(self.requests[0][0], '/v1/messages/count_tokens')
        self.assert_preserved(result)

    def test_support_reaches_prompt_and_literature_is_archived_for_direct_checking(self):
        support = {'theorems': [{'name': 'InclusionBench.Support.fixture', 'statement': 'True'}],
                   'lean_sources': {'support/InclusionSupport.lean': '-- trusted fixture only'}}
        self.request['submission_support'] = support
        self.request['private_runtime'] = {'host': 'private-verifier-host'}
        proof = answer('proof_candidate')
        dependency = {'name': 'Literature.fixture', 'statement': 'A fixture proposition',
                      'sources': [{'title': 'Fixture mock-secret-key', 'url': 'https://example.com/paper',
                                   'locator': 'Theorem 1', 'publication_date': '1994'}],
                      'rationale': 'Infrastructure metadata only; no mathematical claim.'}
        proof['literature_requests'] = [dependency]
        self.replies = [(200, {'input_tokens': 100}, 0), (200, openai_response(proof), 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'proof_candidate')
        payload = self.requests[1][1]
        material = json.loads(payload['input'][0]['content'])
        self.assertEqual(material['submission_support'], support)
        self.assertNotIn('private-verifier-host', json.dumps(payload))
        self.assertIn('literature_requests', payload['text']['format']['schema']['required'])
        files = {Path(path).name: self.directory / path for path in result['artifacts']}
        literature = json.loads(files['literature.json'].read_text())
        self.assertEqual(literature['requests'], result['literature_requests'])
        self.assertEqual(literature['requests'][0]['sources'][0]['title'], 'Fixture [REDACTED]')
        self.assertEqual(files['proof.lean'].read_text(), files['Result.lean'].read_text())
        self.assertEqual(json.loads(files['claims.json'].read_text()), json.loads(files['claims-map.json'].read_text()))
        self.assert_preserved(result)

    def test_legacy_answer_without_literature_still_gets_an_empty_request_file(self):
        self.replies = [(200, {'input_tokens': 100}, 0), (200, openai_response(answer('proof_candidate')), 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'proof_candidate')
        self.assertEqual(result['literature_requests'], [])
        path = next(self.directory / name for name in result['artifacts'] if name.endswith('/literature.json'))
        self.assertEqual(json.loads(path.read_text()), {'requests': []})

    def test_malformed_literature_wire_data_is_rejected(self):
        dependency = {'name': 'Literature.fixture', 'statement': 'True',
                      'sources': [{'title': 'Fixture', 'url': 'https://example.com/paper',
                                   'locator': 'Theorem 1', 'publication_date': '1994'}],
                      'rationale': 'Fixture only'}
        for requests in ({}, [dependency, dependency], [{**dependency, 'name': 'TrustedBaseline.fake'}],
                         [{**dependency, 'sources': []}], [{**dependency, 'rationale': ''}]):
            proof = {**answer('proof_candidate'), 'literature_requests': requests}
            with self.subTest(requests=requests), self.assertRaises(adapter.AdapterError):
                adapter.validate_proof(proof, self.request)

    def test_count_blocks_generation_when_input_exhausts_budget(self):
        self.replies = [(200, {'input_tokens': 801}, 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'budget_exhausted')
        self.assertFalse(result['request_made'])
        self.assertEqual(result['budget_charge_tokens'], 0)
        self.assertEqual(len(self.requests), 1)

    def test_generation_http_error_reserves_unknown_charge_and_redacts_key(self):
        self.replies = [(200, {'input_tokens': 100}, 0), (429, {'error': {'message': 'mock-secret-key mock-anthropic-key'}}, 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['usage_complete'])
        self.assertIsNone(result['usage']['total_tokens'])
        self.assertEqual(result['budget_charge_tokens'], 800)
        self.assertEqual(len(self.requests), 2)  # no automatic retry
        self.assert_preserved(result)

    def test_count_error_does_not_claim_generation_usage(self):
        self.replies = [(401, {'error': 'invalid credential'}, 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['request_made'])
        self.assertEqual(result['usage']['total_tokens'], 0)
        self.assertEqual(result['budget_charge_tokens'], 0)

    def test_truncation_retains_partial_output_and_known_usage(self):
        response = openai_response(status='incomplete')
        response['output'][1]['content'][0]['text'] = '{"status":"proof_cand'
        self.replies = [(200, {'input_tokens': 100}, 0), (200, response, 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'budget_exhausted')
        self.assertTrue(result['usage_complete'])
        self.assertEqual(result['budget_charge_tokens'], 140)
        self.assertEqual(result['claims'], [])
        self.assertTrue(any(p.endswith('model-output.txt') for p in result['artifacts']))

    def test_malformed_model_json_retains_known_usage(self):
        response = openai_response()
        response['output'][1]['content'][0]['text'] = 'not json'
        self.replies = [(200, {'input_tokens': 100}, 0), (200, response, 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertTrue(result['usage_complete'])
        self.assertEqual(result['budget_charge_tokens'], 140)

    def test_missing_usage_is_unknown_not_zero(self):
        self.replies = [(200, {'input_tokens': 100}, 0), (200, openai_response(usage=False), 0)]
        result = self.invoke()
        self.assertFalse(result['usage_complete'])
        self.assertIsNone(result['usage']['total_tokens'])
        self.assertEqual(result['budget_charge_tokens'], 800)

    def test_timeout_preserves_artifacts_and_stops_spending(self):
        self.request['time_remaining_seconds'] = 0.08
        self.replies = [(200, {'input_tokens': 100}, 0), (200, openai_response(), 0.15)]
        result = self.invoke()
        self.assertEqual(result['status'], 'budget_exhausted')
        self.assertEqual(result['budget_charge_tokens'], 800)
        self.assertFalse(result['usage_complete'])
        self.assert_preserved(result)

    def test_source_path_traversal_rejected(self):
        proof = answer('proof_candidate')
        proof['lean_sources'][0]['filename'] = '../../escape.lean'
        self.replies = [(200, {'input_tokens': 100}, 0), (200, openai_response(proof), 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertFalse((self.directory / 'escape.lean').exists())
        self.assertEqual(result['budget_charge_tokens'], 140)

    def test_multifile_modules_are_archived_as_one_checkable_project(self):
        proof = answer('proof_candidate')
        proof['lean_entrypoint'] = 'Main'
        proof['lean_sources'] = [
            {'filename': 'Main.lean', 'content': 'import Lemmas.Arithmetic\n-- fixture only\n'},
            {'filename': 'Lemmas/Arithmetic.lean', 'content': 'import TrustedBaseline\ntheorem helper : True := True.intro\n'},
        ]
        self.replies = [(200, {'input_tokens': 100}, 0), (200, openai_response(proof), 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'proof_candidate', result.get('error'))
        manifest_path = self.directory / result['submission_manifest']
        project = manifest_path.parent
        self.assertEqual(json.loads(manifest_path.read_text()), {
            'schema_version': 1, 'entrypoint': 'Main',
            'files': ['Main.lean', 'Lemmas/Arithmetic.lean']})
        for source in proof['lean_sources']:
            path = project / source['filename']
            self.assertEqual(path.read_text(), source['content'])
            self.assertIn(path.relative_to(self.directory).as_posix(), result['artifacts'])
        for name in ('submission.json', 'claims.json', 'literature.json'):
            self.assertIn((project / name).relative_to(self.directory).as_posix(), result['artifacts'])
        self.assertEqual(json.loads((project / 'claims.json').read_text())['claims'][0]['theorem'], 'Submission.result_1')
        self.assertFalse((project / 'proof.lean').exists())
        self.assertIn('lean_entrypoint', self.requests[1][1]['text']['format']['schema']['required'])

    def test_multifile_wire_validation_rejects_ambiguous_or_unsafe_projects(self):
        valid = {'filename': 'Main.lean', 'content': 'import TrustedBaseline\n'}
        cases = [
            ([valid, {'filename': 'Helper.lean', 'content': ''}], None),
            ([valid], 'Missing'),
            ([valid], '../Main'),
            ([valid, {'filename': 'main.lean', 'content': ''}], 'Main'),
            ([valid, {'filename': 'Lemmas/A.lean', 'content': ''}, {'filename': 'lemmas/B.lean', 'content': ''}], 'Main'),
            ([valid, {'filename': 'ProofAudit.lean', 'content': ''}], 'Main'),
            ([valid, {'filename': 'Mathlib/Fake.lean', 'content': ''}], 'Main'),
            ([valid, {'filename': 'A/../../Escape.lean', 'content': ''}], 'Main'),
            ([valid, {'filename': 'A\\Helper.lean', 'content': ''}], 'Main'),
        ]
        for sources, entrypoint in cases:
            with self.subTest(sources=[s['filename'] for s in sources], entrypoint=entrypoint):
                proof = {**answer('proof_candidate'), 'lean_sources': sources, 'lean_entrypoint': entrypoint}
                with self.assertRaises(adapter.AdapterError):
                    adapter.validate_proof(proof, self.request)

    def test_project_limit_is_aggregate_and_legacy_limit_is_preserved(self):
        from unittest.mock import patch
        proof = {**answer('proof_candidate'), 'lean_entrypoint': 'Main',
                 'lean_sources': [{'filename': 'Main.lean', 'content': '12345'},
                                  {'filename': 'Helper.lean', 'content': '67890'}]}
        with patch.object(adapter, 'MAX_PROJECT_BYTES', 9), self.assertRaisesRegex(adapter.AdapterError, '16 MiB'):
            adapter.validate_proof(proof, self.request)
        proof.pop('lean_entrypoint')
        proof['lean_sources'] = proof['lean_sources'][:1]
        with patch.object(adapter, 'MAX_LEGACY_BYTES', 4), self.assertRaisesRegex(adapter.AdapterError, '2 MiB'):
            adapter.validate_proof(proof, self.request)

    def test_dry_run_without_credentials_never_contacts_provider(self):
        self.env.pop('OPENAI_API_KEY')
        result = adapter.run(self.request, 'openai', self.directory, self.env, dry_run=True)
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['budget_charge_tokens'], 0)
        self.assertEqual(self.requests, [])
        self.assert_preserved(result)

    def test_missing_explicit_model_or_credentials_never_contacts_provider(self):
        self.request['model'] = {}
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertEqual(self.requests, [])
        self.request['model'] = {'version': 'explicit-snapshot-123'}
        self.env.pop('OPENAI_API_KEY')
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertEqual(self.requests, [])

    def test_endpoint_cannot_send_credentials_to_arbitrary_host(self):
        self.env['INCLUSION_API_BASE_URL'] = 'https://example.com/v1'
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['request_made'])
        self.assertEqual(self.requests, [])

    def test_conflicting_model_configuration_rejected_before_network(self):
        self.env['INCLUSION_MODEL'] = 'environment-model'
        self.request['configuration']['model_id'] = 'different-model'
        result = self.invoke()
        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['request_made'])
        self.assertEqual(self.requests, [])

    def test_oversized_provider_response_is_bounded_and_charge_unknown(self):
        self.replies = [(200, {'input_tokens': 100}, 0), (200, b'x' * 513, 0)]
        previous = adapter.MAX_RESPONSE_BYTES
        try:
            adapter.MAX_RESPONSE_BYTES = 512
            result = self.invoke()
        finally:
            adapter.MAX_RESPONSE_BYTES = previous
        self.assertEqual(result['status'], 'error')
        self.assertIn('Provider response exceeded', result['error'])
        self.assertEqual(result['budget_charge_tokens'], 800)
        self.assertFalse(result['usage_complete'])
        body = next(self.directory / p for p in result['artifacts'] if p.endswith('/generation-response.json'))
        self.assertLessEqual(body.stat().st_size, 513)

    def test_observed_total_overrun_is_not_an_accepted_candidate(self):
        response = openai_response(answer('proof_candidate'))
        response['usage']['input_tokens'] = 900
        self.replies = [(200, {'input_tokens': 100}, 0), (200, response, 0)]
        result = self.invoke()
        self.assertEqual(result['status'], 'budget_exhausted')
        self.assertEqual(result['claims'], [])
        self.assertTrue(result['budget_overrun'])
        self.assertEqual(result['budget_charge_tokens'], 940)

    def test_preflight_is_offline_and_does_not_print_credentials(self):
        environment = {'PATH': '/usr/bin:/bin', 'INCLUSION_MODEL': 'explicit-snapshot-123', 'OPENAI_API_KEY': 'mock-secret-key'}
        result = subprocess.run([sys.executable, str(ROOT / 'evaluation/adapters/openai_responses.py'), '--preflight'],
                                env=environment, text=True, capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)['ready'])
        self.assertNotIn('mock-secret-key', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
