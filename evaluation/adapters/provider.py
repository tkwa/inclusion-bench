#!/usr/bin/env python3
"""Dependency-free, one-shot provider adapters. No retries or model defaults."""
from __future__ import annotations

import argparse
import http.client
import json
import math
import os
from pathlib import Path
import re
import socket
import sys
import time
from urllib.parse import urlsplit
import uuid


MAX_BYTES = 8_000_000
MAX_RESPONSE_BYTES = 128 * 1024 * 1024
MAX_PROJECT_BYTES = 16 * 1024 * 1024
MAX_LEGACY_BYTES = 2 * 1024 * 1024
MODULE_NAME = r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*'
SOURCE_PATH = r'(?:[A-Za-z_][A-Za-z0-9_]*/)*[A-Za-z_][A-Za-z0-9_]*\.lean'
RESERVED_MODULES = {'init', 'std', 'lean', 'mathlib', 'batteries', 'aesop', 'qq',
                    'inclusionbench', 'inclusionquantum', 'inclusionsupport',
                    'trustedbaseline', 'proofcodec', 'proofexport', 'proofaudit',
                    'auditimports', 'candidate'}
PROVIDERS = {
    'openai': ('OPENAI_API_KEY', 'https://api.openai.com/v1', '/responses', '/responses/input_tokens'),
    'anthropic': ('ANTHROPIC_API_KEY', 'https://api.anthropic.com/v1', '/messages', '/messages/count_tokens'),
}
INSTRUCTIONS = """You are taking a public mathematical research benchmark. Resolve the assigned
complexity-class inclusion under its exact definitions and conventions. Give a complete,
checkable mathematical proof, or return unsolved. Conjectures and oracle separations do not
resolve the task. Ordinary inclusion or non-inclusion proofs may not add unproved assumptions.
Independence may be unconditional or conditional on Con(ZFC) or arithmetic soundness of ZFC:
every first-order arithmetic sentence whose standard translation ZFC proves is true in
standard N. Prove both nonderivability directions under the same explicitly retained premise.
No stronger unproved assumption is permitted. Independence uses a separate expert metatheory
review; the ordinary Lean proof checker does not automatically verify it. Record exact
claims, a human-readable proof in proof_markdown, and any Lean source in lean_sources.
Existing cited theorems may be used with precise references; expose every assumption.
Formalize the new argument. Use the standard mathematical results and textbook
abstractions in submission_support without rebuilding their published proofs.
For a missing published dependency, declare axiom Literature.your_name : EXACT_TYPE
in your Lean body and include a matching literature_requests entry with its name,
statement, sources (title, URL, theorem/page locator, publication_date), and rationale
for its application to these exact models. A maintainer reviews the source, actual
Lean type, and model alignment; the published proof need not be re-formalized.
Use an empty literature_requests list when no additional dependency is needed.
Never claim that your proof has been verified. For unsolved, claims must be empty; explain
the limitation in notes. Put normal Lean modules in lean_sources, using relative
paths such as Main.lean or Lemmas/Arithmetic.lean. Set lean_entrypoint to the module
that imports the complete argument, such as Main. Import helpers normally with
`import Lemmas.Arithmetic`; import TrustedBaseline for benchmark definitions,
support, and known results. Pinned Lean/Std/Mathlib imports are also available.
Each named module is compiled in isolation as part of the same project. You may
use up to 128 files totaling 16 MiB of Lean source. Do not emit build scripts or
compiled objects. Use lean_entrypoint: null when no Lean proof is supplied.
The formalizations field supplies the canonical Lean sources and TrustedBaseline.lean.
Name the theorem for claim 1 Submission.result_1,
claim 2 Submission.result_2, and so on. Prove the exact target over
InclusionBench.Quantum.completeInterpretation; the short names in
InclusionBench.Support.Classes are definitionally identical targets. Use ordinary
definitions and theorems over imported types. New inductive types and structures
are not supported by the current exporter. Literature declarations
must name existing pre-cutoff results; a new claim cannot be assumed as its own proof.
No tools or external retrieval are available in this attempt. Return only the requested JSON.
"""


class AdapterError(ValueError):
    pass


def positive_int(value, name, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, int) or value < (0 if allow_zero else 1):
        raise AdapterError(f'{name} must be an explicit {"nonnegative" if allow_zero else "positive"} integer')
    return value


def secrets_from(env):
    return [env[key] for key in ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY') if env.get(key)]


def scrub(value, secrets):
    if isinstance(value, str):
        for secret in secrets:
            value = value.replace(secret, '[REDACTED]')
        return value
    if isinstance(value, list):
        return [scrub(v, secrets) for v in value]
    if isinstance(value, dict):
        return {k: '[REDACTED]' if k.lower().replace('-', '_') in
                {'authorization', 'api_key', 'openai_api_key', 'anthropic_api_key', 'x_api_key'}
                else scrub(v, secrets) for k, v in value.items()}
    return value


class Archive:
    def __init__(self, directory, provider, secrets):
        self.root = Path(directory).resolve()
        self.path = self.root / 'adapter-artifacts' / f'{provider}-{uuid.uuid4().hex}'
        self.path.mkdir(parents=True, exist_ok=False)
        self.secrets = secrets
        self.artifacts = []

    def text(self, name, value):
        path = self.path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(scrub(value, self.secrets), encoding='utf-8')
        relative = path.relative_to(self.root).as_posix()
        if relative not in self.artifacts:
            self.artifacts.append(relative)
        return relative

    def json(self, name, value):
        return self.text(name, json.dumps(scrub(value, self.secrets), indent=2, ensure_ascii=False) + '\n')


def configuration(request, provider, env):
    if not isinstance(request, dict):
        raise AdapterError('Adapter input must be a JSON object')
    config = request.get('configuration', {})
    limits = request.get('limits', {})
    if not isinstance(config, dict) or not isinstance(limits, dict):
        raise AdapterError('configuration and limits must be objects')
    configured = config.get('model_id')
    environment_model = env.get('INCLUSION_MODEL')
    if configured and environment_model and configured != environment_model:
        raise AdapterError('configuration.model_id and INCLUSION_MODEL disagree')
    declared = request.get('model', {})
    model = configured or environment_model or (declared.get('version') if isinstance(declared, dict) else None)
    if not isinstance(model, str) or not model.strip():
        raise AdapterError('Set an explicit model ID in configuration.model_id, INCLUSION_MODEL, or model.version')
    maximum = positive_int(limits.get('max_output_tokens'), 'limits.max_output_tokens')
    total = positive_int(limits.get('max_total_tokens_remaining'), 'limits.max_total_tokens_remaining', True)
    if limits.get('remaining_output_tokens') is not None:
        maximum = min(maximum, positive_int(limits['remaining_output_tokens'], 'limits.remaining_output_tokens', True))
    seconds = request.get('time_remaining_seconds', limits.get('wall_seconds'))
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
        raise AdapterError('An explicit positive time_remaining_seconds or limits.wall_seconds is required')
    reserve = positive_int(config.get('input_token_reserve', 256 if provider == 'anthropic' else 0), 'configuration.input_token_reserve', True)
    base = env.get('INCLUSION_API_BASE_URL', PROVIDERS[provider][1]).rstrip('/')
    parsed = urlsplit(base)
    expected = urlsplit(PROVIDERS[provider][1])
    official = parsed.scheme == 'https' and parsed.hostname == expected.hostname and parsed.port in (None, 443) and parsed.path == '/v1'
    local_test = env.get('INCLUSION_ALLOW_TEST_ENDPOINT') == '1' and parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', '::1', 'localhost'}
    if not (official or local_test) or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise AdapterError('API endpoint must be the official provider endpoint, or an explicitly enabled loopback test server')
    return {'model': model.strip(), 'maximum': maximum, 'total': total, 'seconds': float(seconds),
            'reserve': reserve, 'base': base, 'options': config}


def output_schema(request):
    catalog = request.get('classes', {})
    classes = catalog.get('classes', []) if isinstance(catalog, dict) else catalog
    ids = [c['id'] for c in classes if isinstance(c, dict) and isinstance(c.get('id'), str)] if isinstance(classes, list) else []
    identifier = {'type': 'string', **({'enum': ids} if ids else {})}
    atom = {'type': 'object', 'properties': {'relation': {'type': 'string', 'enum': ['inclusion', 'separation', 'independence']},
            'left': identifier, 'right': identifier}, 'required': ['relation', 'left', 'right'], 'additionalProperties': False}
    source = {'type': 'object', 'properties': {'filename': {'type': 'string'}, 'content': {'type': 'string'}},
              'required': ['filename', 'content'], 'additionalProperties': False}
    citation = {'type': 'object', 'properties': {key: {'type': 'string'} for key in
                ('title', 'url', 'locator', 'publication_date')},
                'required': ['title', 'url', 'locator', 'publication_date'], 'additionalProperties': False}
    dependency = {'type': 'object', 'properties': {
        'name': {'type': 'string'}, 'statement': {'type': 'string'},
        'sources': {'type': 'array', 'items': citation}, 'rationale': {'type': 'string'}},
        'required': ['name', 'statement', 'sources', 'rationale'], 'additionalProperties': False}
    return {'type': 'object', 'properties': {'status': {'type': 'string', 'enum': ['unsolved', 'proof_candidate']},
            'claims': {'type': 'array', 'items': atom}, 'proof_markdown': {'type': 'string'},
            'lean_sources': {'type': 'array', 'items': source},
            'lean_entrypoint': {'type': ['string', 'null']},
            'literature_requests': {'type': 'array', 'items': dependency}, 'notes': {'type': 'string'}},
            'required': ['status', 'claims', 'proof_markdown', 'lean_sources', 'lean_entrypoint', 'literature_requests', 'notes'], 'additionalProperties': False}


def payloads(request, provider, config):
    # Only benchmark material enters the model prompt. Credentials, budgets and local paths do not.
    material = {k: request[k] for k in ('task', 'classes', 'knowledge', 'formalization_bundle', 'formalizations', 'submission_support', 'dataset_sha256') if k in request}
    prompt = json.dumps(material, ensure_ascii=False, sort_keys=True)
    schema = output_schema(request)
    options = config['options']
    if provider == 'openai':
        body = {'model': config['model'], 'instructions': INSTRUCTIONS, 'input': [{'role': 'user', 'content': prompt}],
                'text': {'format': {'type': 'json_schema', 'name': 'complexity_proof', 'strict': True, 'schema': schema}},
                'max_output_tokens': config['maximum'], 'store': False, 'stream': False}
        if options.get('reasoning_effort'):
            body['reasoning'] = {'effort': options['reasoning_effort']}
        count = {k: v for k, v in body.items() if k in {'model', 'instructions', 'input', 'text', 'reasoning'}}
    else:
        body = {'model': config['model'], 'system': INSTRUCTIONS, 'messages': [{'role': 'user', 'content': prompt}],
                'output_config': {'format': {'type': 'json_schema', 'schema': schema}},
                'max_tokens': config['maximum'], 'stream': False}
        if options.get('reasoning_effort'):
            body['output_config']['effort'] = options['reasoning_effort']
        if options.get('thinking') in {'adaptive', 'disabled'}:
            body['thinking'] = {'type': options['thinking']}
        elif options.get('thinking_budget_tokens') is not None:
            body['thinking'] = {'type': 'enabled', 'budget_tokens': positive_int(options['thinking_budget_tokens'], 'thinking_budget_tokens')}
        count = {k: v for k, v in body.items() if k in {'model', 'system', 'messages', 'output_config', 'thinking'}}
    if options.get('temperature') is not None:
        temperature = options['temperature']
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)) or not math.isfinite(temperature):
            raise AdapterError('configuration.temperature must be finite')
        body['temperature'] = temperature
    return body, count


def post_json(base, suffix, payload, provider, api_key, deadline, archive, label):
    """One bounded HTTP call, no redirect following, retries, or credential logging."""
    parsed = urlsplit(base)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError('Attempt deadline reached')
    headers = {'Content-Type': 'application/json', 'User-Agent': 'InclusionBench-provider-adapter/1'}
    if provider == 'openai':
        headers['Authorization'] = f'Bearer {api_key}'
    else:
        headers['x-api-key'] = api_key
        headers['anthropic-version'] = '2023-06-01'
    archive.json(f'{label}-request.json', {'url': base + suffix, 'body': payload})
    cls = http.client.HTTPSConnection if parsed.scheme == 'https' else http.client.HTTPConnection
    connection = cls(parsed.hostname, parsed.port, timeout=remaining)
    chunks = []
    size = 0
    metadata = {}
    try:
        connection.request('POST', parsed.path + suffix, json.dumps(payload).encode('utf-8'), headers)
        response = connection.getresponse()
        metadata = {'http_status': response.status,
                    'request_id': response.getheader('x-request-id') or response.getheader('request-id')}
        archive.json(f'{label}-http.json', metadata)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Attempt deadline reached')
            if connection.sock is not None:
                connection.sock.settimeout(remaining)
            chunk = response.read1(min(65536, MAX_RESPONSE_BYTES + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > MAX_RESPONSE_BYTES:
                raise AdapterError('Provider response exceeded 128 MiB')
        raw = b''.join(chunks).decode('utf-8', errors='replace')
        if response.status < 200 or response.status >= 300:
            raise AdapterError(f'Provider HTTP {response.status}; response retained in artifacts')
        decoded = json.loads(raw)
        if not isinstance(decoded, dict):
            raise AdapterError('Provider response must be a JSON object')
        return decoded
    finally:
        connection.close()
        archive.text(f'{label}-response.json', b''.join(chunks).decode('utf-8', errors='replace'))


def normalize_usage(response, provider):
    raw = response.get('usage')
    raw = raw if isinstance(raw, dict) else {}
    def count(key):
        value = raw.get(key)
        return value if type(value) is int and value >= 0 else None
    input_tokens, output_tokens = count('input_tokens'), count('output_tokens')
    if provider == 'anthropic' and input_tokens is not None:
        for key in ('cache_creation_input_tokens', 'cache_read_input_tokens'):
            if raw.get(key) is not None:
                value = count(key)
                input_tokens = input_tokens + value if value is not None and input_tokens is not None else None
    complete = input_tokens is not None and output_tokens is not None
    total = input_tokens + output_tokens if complete else None
    # Never double-count reasoning: both APIs already include it in output_tokens.
    details = raw.get('output_tokens_details', {})
    reasoning = details.get('reasoning_tokens' if provider == 'openai' else 'thinking_tokens') if isinstance(details, dict) else None
    return {'input_tokens': input_tokens, 'output_tokens': output_tokens, 'total_tokens': total,
            'reasoning_tokens': reasoning, 'provider_usage': raw}, complete


def response_text(response, provider):
    blocks = response.get('content', []) if provider == 'anthropic' else [c for item in response.get('output', [])
        if isinstance(item, dict) and item.get('type') == 'message' for c in item.get('content', [])]
    return ''.join(b.get('text', '') for b in blocks if isinstance(b, dict) and b.get('type') in {'text', 'output_text'} and isinstance(b.get('text'), str))


def validate_proof(proof, request):
    required = {'status', 'claims', 'proof_markdown', 'lean_sources', 'notes'}
    if not isinstance(proof, dict) or not required <= set(proof) or set(proof) - required - {'literature_requests', 'lean_entrypoint'}:
        raise AdapterError('Model output needs status, claims, proof_markdown, lean_sources, notes, and optional lean_entrypoint/literature_requests')
    if proof['status'] not in {'unsolved', 'proof_candidate'} or not isinstance(proof['claims'], list) or not isinstance(proof['lean_sources'], list):
        raise AdapterError('Invalid model proof status or list fields')
    if not all(isinstance(proof[k], str) for k in ('proof_markdown', 'notes')):
        raise AdapterError('Model proof text and notes must be strings')
    allowed = output_schema(request)['properties']['claims']['items']['properties']['left'].get('enum')
    for claim in proof['claims']:
        if not isinstance(claim, dict) or set(claim) != {'relation', 'left', 'right'} or claim['relation'] not in {'inclusion', 'separation', 'independence'}:
            raise AdapterError('Invalid exact claim')
        if not all(isinstance(claim[k], str) and (allowed is None or claim[k] in allowed) for k in ('left', 'right')):
            raise AdapterError('Unknown class in claim')
    if len(proof['lean_sources']) > 128:
        raise AdapterError('A Lean project may contain at most 128 source files')
    filenames = set()
    module_components = {}
    total_bytes = 0
    for source in proof['lean_sources']:
        if not isinstance(source, dict) or set(source) != {'filename', 'content'} or not isinstance(source['content'], str):
            raise AdapterError('Invalid Lean source object')
        filename = source['filename']
        if not isinstance(filename, str) or len(filename) > 240 or not re.fullmatch(SOURCE_PATH, filename) or filename.casefold() in filenames:
            raise AdapterError('Lean filenames must be distinct relative .lean module paths without case collisions')
        if filename[:-5].split('/')[0].casefold() in RESERVED_MODULES:
            raise AdapterError('A Lean module cannot shadow a trusted library or verifier module')
        parts = filename[:-5].split('/')
        for length in range(1, len(parts) + 1):
            component = '/'.join(parts[:length])
            previous = module_components.setdefault(component.casefold(), component)
            if previous != component:
                raise AdapterError('Lean module paths must not have case-colliding components')
        filenames.add(filename.casefold())
        total_bytes += len(source['content'].encode('utf-8'))
    entrypoint = proof.get('lean_entrypoint')
    if entrypoint is not None:
        if not isinstance(entrypoint, str) or len(entrypoint) > 240 or not re.fullmatch(MODULE_NAME, entrypoint):
            raise AdapterError('lean_entrypoint must be a qualified Lean module name or null')
        if entrypoint.replace('.', '/') + '.lean' not in {s['filename'] for s in proof['lean_sources']}:
            raise AdapterError('lean_entrypoint must identify one of the supplied source files')
        manifest = {'schema_version': 1, 'entrypoint': entrypoint,
                    'files': [source['filename'] for source in proof['lean_sources']]}
        manifest_bytes = len((json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
        if total_bytes + manifest_bytes > MAX_PROJECT_BYTES:
            raise AdapterError('Lean project source exceeds 16 MiB')
    elif len(proof['lean_sources']) > 1:
        raise AdapterError('Multiple Lean files require lean_entrypoint')
    elif total_bytes > MAX_LEGACY_BYTES:
        raise AdapterError('Legacy Lean source exceeds 2 MiB; use a project entrypoint for larger submissions')
    # The standalone adapter validates the wire shape. The runner applies the
    # canonical literature validator with the real benchmark cutoff before sealing.
    literature = proof.get('literature_requests', [])
    if not isinstance(literature, list) or len(literature) > 128 or len(json.dumps(literature, ensure_ascii=False).encode()) > 1024 * 1024:
        raise AdapterError('literature_requests must be a list of at most 128 dependencies and 1 MiB')
    names = set()
    for dependency in literature:
        if not isinstance(dependency, dict) or set(dependency) != {'name', 'statement', 'sources', 'rationale'}:
            raise AdapterError('Literature dependencies need name, statement, sources, and rationale')
        name = dependency['name']
        if not isinstance(name, str) or len(name) > 240 or not re.fullmatch(r'Literature\.[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*', name) or name in names:
            raise AdapterError('Literature names must be distinct qualified names under Literature')
        names.add(name)
        if any(not isinstance(dependency[key], str) or not dependency[key].strip() or len(dependency[key]) > 20000 for key in ('statement', 'rationale')):
            raise AdapterError('Literature statement and rationale must be nonempty text')
        citations = dependency['sources']
        if not isinstance(citations, list) or not 1 <= len(citations) <= 16:
            raise AdapterError('A literature dependency needs between 1 and 16 cited sources')
        for citation in citations:
            fields = {'title', 'url', 'locator', 'publication_date'}
            if not isinstance(citation, dict) or set(citation) != fields or any(
                    not isinstance(citation[key], str) or not citation[key].strip() or len(citation[key]) > 4000 for key in fields):
                raise AdapterError('Literature sources need title, URL, theorem/page locator, and publication date')
    if literature and (proof['status'] != 'proof_candidate' or not proof['lean_sources']):
        raise AdapterError('Literature dependencies require a proof candidate with Lean declarations')
    if proof['status'] == 'unsolved' and proof['claims']:
        raise AdapterError('An unsolved answer cannot assert claims')
    if proof['status'] == 'proof_candidate' and (not proof['claims'] or not
        (proof['proof_markdown'].strip() or any(s['content'].strip() for s in proof['lean_sources']))):
        raise AdapterError('A proof candidate needs claims and substantive proof text or Lean source')


def run(request, provider, directory=None, env=None, dry_run=False):
    env = os.environ if env is None else env
    archive = Archive(directory or Path.cwd(), provider, secrets_from(env))
    result = {'status': 'error', 'claims': [], 'artifacts': [], 'provider': provider,
              'usage': {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
              'usage_complete': True, 'request_made': False, 'budget_charge_tokens': 0,
              'provider_model': None, 'response_id': None}
    archive.json('harness-request.json', request)
    config = None
    generation_started = False
    usage_received = False
    try:
        config = configuration(request, provider, env)
        result['model_requested'] = config['model']
        deadline = time.monotonic() + config['seconds']
        body, count_body = payloads(request, provider, config)
        archive.json('planned-request.json', body)
        if dry_run:
            result.update(status='unsolved', dry_run=True, finish_reason='dry_run_no_api_call')
            return result
        key_name, _, generation_path, count_path = PROVIDERS[provider]
        api_key = env.get(key_name)
        if not api_key:
            raise AdapterError(f'{key_name} is required; no credential was logged')
        if config['total'] == 0 or config['maximum'] == 0:
            result.update(status='budget_exhausted', finish_reason='no_token_budget')
            return result
        counted = post_json(config['base'], count_path, count_body, provider, api_key, deadline, archive, 'count')
        input_count = positive_int(counted.get('input_tokens'), 'provider input token count', True)
        allowance = min(config['maximum'], config['total'] - input_count - config['reserve'])
        result['input_tokens_counted'] = input_count
        result['input_token_reserve'] = config['reserve']
        result['max_output_tokens_sent'] = max(0, allowance)
        if allowance < 1:
            result.update(status='budget_exhausted', finish_reason='input_exceeds_remaining_budget')
            return result
        body['max_output_tokens' if provider == 'openai' else 'max_tokens'] = allowance
        if body.get('thinking', {}).get('type') == 'enabled':
            thinking = body['thinking']['budget_tokens']
            if thinking < 1024 or thinking >= allowance:
                raise AdapterError('Anthropic thinking_budget_tokens must be at least 1024 and below the available output budget')
        generation_started = True
        result['request_made'] = True
        response = post_json(config['base'], generation_path, body, provider, api_key, deadline, archive, 'generation')
        result['provider_model'] = response.get('model')
        result['response_id'] = response.get('id')
        result['usage'], result['usage_complete'] = normalize_usage(response, provider)
        usage_received = True
        result['budget_charge_tokens'] = result['usage']['total_tokens'] if result['usage_complete'] else config['total']
        finish = response.get('status') if provider == 'openai' else response.get('stop_reason')
        result['finish_reason'] = finish
        text = response_text(response, provider)
        archive.text('model-output.txt', text)
        archive.json('transcript.json', {'provider': provider, 'model_requested': config['model'],
                     'request': body, 'response': response})
        if result['usage_complete'] and result['budget_charge_tokens'] > config['total']:
            result.update(status='budget_exhausted', error='Actual provider usage exceeded the remaining total-token budget', budget_overrun=True)
        elif finish in {'incomplete', 'max_tokens'}:
            result.update(status='budget_exhausted', error='Provider reached its output limit; partial response retained')
        elif finish not in {'completed', 'end_turn'}:
            result.update(status='error', error='Provider response did not complete normally; response retained')
        else:
            proof = json.loads(text)
            validate_proof(proof, request)
            archive.json('model-proof.json', proof)
            if proof['proof_markdown']:
                archive.text('proof.md', proof['proof_markdown'])
            project = proof.get('lean_entrypoint') is not None
            for source in proof['lean_sources']:
                archive.text(('submission/' if project else 'lean/') + source['filename'], source['content'])
            if proof['lean_sources']:
                mapped = {'claims': [{**claim, 'theorem': f'Submission.result_{i}'}
                    for i, claim in enumerate(proof['claims'], 1) if claim['relation'] != 'independence']}
                archive.json('claims-map.json', mapped)
                if project:
                    manifest_path = archive.json('submission/submission.json', {
                        'schema_version': 1, 'entrypoint': proof['lean_entrypoint'],
                        'files': [source['filename'] for source in proof['lean_sources']]})
                    if proof['status'] == 'proof_candidate':
                        result['submission_manifest'] = manifest_path
                    archive.json('submission/claims.json', mapped)
                    archive.json('submission/literature.json', {'requests': proof.get('literature_requests', [])})
                else:
                    # The archived directory can be checked directly with
                    # check-submission; preserve original named sources as well.
                    archive.text('proof.lean', proof['lean_sources'][0]['content'])
                    archive.json('claims.json', mapped)
                    archive.json('literature.json', {'requests': proof.get('literature_requests', [])})
            if proof['notes']:
                archive.text('notes.txt', proof['notes'])
            result.update(status=proof['status'], claims=proof['claims'],
                          literature_requests=proof.get('literature_requests', []))
    except (AdapterError, ValueError, TypeError, KeyError, OSError, http.client.HTTPException) as exc:
        result.update(status='budget_exhausted' if isinstance(exc, (TimeoutError, socket.timeout)) else 'error',
                      claims=[], error=scrub(str(exc), archive.secrets))
        if generation_started and not usage_received:
            result.update(usage={'input_tokens': None, 'output_tokens': None, 'total_tokens': None},
                          usage_complete=False, budget_charge_tokens=config['total'])
    finally:
        archive.json('usage.json', {k: result[k] for k in ('usage', 'usage_complete', 'request_made', 'budget_charge_tokens')})
        archive.json('adapter-result.json', {k: v for k, v in result.items() if k != 'artifacts'})
        result['artifacts'] = archive.artifacts
        cleaned = scrub(result, archive.secrets)
        result.clear()
        result.update(cleaned)
    return result


def main(provider=None):
    parser = argparse.ArgumentParser(description=__doc__)
    if provider is None:
        parser.add_argument('--provider', required=True, choices=sorted(PROVIDERS))
    parser.add_argument('--preflight', action='store_true', help='Check explicit model and credential presence; no network or stdin')
    parser.add_argument('--dry-run', action='store_true', help='Read a harness request and archive its planned API request; no network')
    args = parser.parse_args()
    provider = provider or args.provider
    if args.preflight:
        key = PROVIDERS[provider][0]
        ready = bool(os.environ.get('INCLUSION_MODEL', '').strip()) and bool(os.environ.get(key))
        print(json.dumps({'provider': provider, 'ready': ready, 'model_explicit': bool(os.environ.get('INCLUSION_MODEL', '').strip()),
                          'credential_present': bool(os.environ.get(key)), 'network_request_made': False}))
        return 0 if ready else 2
    try:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise AdapterError('Harness request exceeded 8 MB')
        request = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        print(json.dumps({'status': 'error', 'claims': [], 'artifacts': [], 'error': type(exc).__name__ + ': invalid harness JSON',
                          'usage': {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
                          'usage_complete': True, 'request_made': False, 'budget_charge_tokens': 0}))
        return 0
    result = run(request, provider, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
