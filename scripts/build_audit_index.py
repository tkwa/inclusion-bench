"""Bind a reviewed audit assessment to every current ordered pair.

This indexes the explicit judgment in audit-assessment.json. It neither infers
historical openness from SAT nor writes an admission decision to the registry.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark, canonical_hash, read_json
from inclusion_bench.engine import Atom


def build():
    benchmark = Benchmark(ROOT)
    assessment = read_json(ROOT / 'research/audit-assessment.json')
    if assessment['dataset_sha256'] != benchmark.digest:
        raise ValueError('Assessment does not bind the current dataset')
    if assessment['candidate_decision'] != 'open_at_cutoff':
        raise ValueError('This index requires an explicit reviewed historical decision')
    sat = read_json(ROOT / 'research/audit-final-sat.json')
    lean = read_json(ROOT / 'research/audit-final-lean-traces.json')
    if any(item['dataset_sha256'] != benchmark.digest for item in (sat, lean)):
        raise ValueError('Final logical checks do not bind this dataset')
    if sat['findings'] or sat['hypotheses_tested'] != 2 * len(benchmark.unresolved):
        raise ValueError('Unresolved or incomplete propositional audit')
    if {Atom.read(t) for t in lean['targets']} != set(benchmark.baseline.proofs):
        raise ValueError('Lean trace audit does not cover every known label')
    if (lean['status'] != 'all_conditional_inference_traces_kernel_checked' or
            lean['declaration_count'] != len(lean['targets']) or
            set(lean['allowed_axiom_dependencies']) != {'propext', 'Classical.choice', 'Quot.sound'}):
        raise ValueError('Lean report is not a completed trace and axiom audit')
    scopes = {}
    scope_paths = assessment.get('literature_scope_reports', [
        f'research/audit-round1-{name}.json'
        for name in ('classical', 'circuits-space', 'counting-quantum')
    ])
    if not isinstance(scope_paths, list) or not scope_paths or len(scope_paths) != len(set(scope_paths)):
        raise ValueError('Literature scope reports must be an explicit nonempty distinct list')
    for path in scope_paths:
        scope = read_json(ROOT / path)['scope']
        ids = scope['focus_classes'] if isinstance(scope, dict) else scope
        if not ids or not set(ids) <= set(benchmark.context_ids):
            raise ValueError('Literature review has empty or unknown class scope: ' + path)
        scopes[path] = set(ids)
    if set.union(*scopes.values()) != set(benchmark.context_ids):
        raise ValueError('Literature review scopes do not cover the full context catalog')
    reports = sorted(set(assessment['supporting_reports']) | set(scopes))
    manifest = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in reports}
    matrix = benchmark.matrix()
    pairs = []
    for item in matrix['pairs']:
        pair = {k: item[k] for k in ('left', 'right', 'status')}
        pair['review_dossiers'] = [p for p, ids in scopes.items()
                                  if pair['left'] in ids or pair['right'] in ids]
        if item['status'] == 'unreviewed':
            pair['historical_assessment'] = assessment['candidate_decision']
            pair['rationale'] = ('Reviewed in the linked domain dossiers and subsequent '
                'cross-reviews; no accepted pre-cutoff resolution identified. The final '
                'SAT check found no resolution forced by the encoded cited theory. '
                'This is a revisable literature judgment, not a proof of openness.')
            pair['evidence_source_ids'] = []
        else:
            atom = Atom(pair['status'], pair['left'], pair['right'])
            trace = benchmark.baseline.explanation(atom)
            pair['historical_assessment'] = 'known_at_cutoff'
            pair['closure_derivation_target'] = trace['target']
            pair['evidence_source_ids'] = sorted({source for step in trace['steps']
                                                 for source in step['source_ids']})
        pairs.append(pair)
    result = {
        'schema_version': 2,
        'audit_id': assessment['audit_id'],
        'recorded_at': assessment['recorded_at'],
        'cutoff': benchmark.policy['cutoff'],
        'cutoff_convention': benchmark.policy['cutoff_convention'],
        'status': 'revisable_release_wide_historical_audit',
        'reviewer': assessment['reviewer'],
        'binding': {
            'algorithm': 'SHA-256 of canonical UTF-8 JSON for data; SHA-256 of exact bytes for files',
            'dataset_sha256': benchmark.digest,
            'baseline_graph_sha256': canonical_hash({'classes': benchmark.catalog, 'knowledge': benchmark.knowledge}),
            'classes_sha256': canonical_hash(benchmark.catalog),
            'knowledge_sha256': canonical_hash(benchmark.knowledge),
            'assessment_sha256': hashlib.sha256((ROOT / 'research/audit-assessment.json').read_bytes()).hexdigest(),
        },
        'coverage': {'class_count': len(benchmark.ids), 'ordered_pair_count': len(pairs),
                     'context_class_count': len(benchmark.context_ids),
                     'background_class_count': len(benchmark.background_classes),
                     'counts': matrix['counts'], 'candidate_historical_decisions': len(benchmark.unresolved),
                     'known_inference_traces_kernel_checked': len(lean['targets']),
                     'literature_review_method': 'Domain and theorem-family review indexed to every pair; not 2500 independent searches.'},
        'corrections': assessment['corrections'],
        'residual_error_assessment': assessment['residual_error_assessment'],
        'stopping_decision': assessment['stopping_decision'],
        'limitations': assessment['limitations'],
        **({'policy_adoption': assessment['policy_adoption']} if 'policy_adoption' in assessment else {}),
        **({'roster_migration': assessment['roster_migration']} if 'roster_migration' in assessment else {}),
        'supporting_report_sha256': manifest,
        'pair_index': pairs,
    }
    path = ROOT / 'research/baseline-audit.json'
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'written': str(path.relative_to(ROOT)), 'pairs': len(pairs),
                      'candidate_decisions': len(benchmark.unresolved)}))


if __name__ == '__main__':
    build()
