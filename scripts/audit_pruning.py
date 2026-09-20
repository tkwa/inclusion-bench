"""Measure what the full context theory loses when only50 endpoints are scored.

Every unresolved inactive pair is tested with each ordinary polarity. Claims
are assumptions for this scope experiment, not proofs or measured AI outputs.
The report uses the current full theory, including the newly added classes.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark
from inclusion_bench.engine import Atom, Closure, Contradiction


def assumed_closure(benchmark, claims):
    closure = Closure(benchmark.context_ids, benchmark.rules, benchmark.complements)
    closure.proofs = dict(benchmark.baseline.proofs)
    for claim in claims:
        closure.add(claim, 'submission')
    return closure.saturate()


def build():
    benchmark = Benchmark(ROOT)
    active = set(benchmark.ids)
    background = set(benchmark.context_ids) - active
    context_candidates = {(a, b) for a in benchmark.context_ids for b in benchmark.context_ids
                          if not any(Atom(r, a, b) in benchmark.baseline.proofs
                                     for r in ('inclusion', 'separation', 'independence'))}
    inactive = context_candidates - benchmark.unresolved
    rows = []
    contradictions = []
    for index, (left, right) in enumerate(sorted(inactive)):
        for relation in ('inclusion', 'separation'):
            claim = Atom(relation, left, right)
            try:
                closure = assumed_closure(benchmark, [claim])
            except Contradiction as error:
                contradictions.append({**claim.json(), 'reason': str(error)})
                continue
            all_pairs = {a.pair for a in closure.proofs if a.pair in context_candidates}
            scored = all_pairs & benchmark.unresolved
            rows.append({**claim.json(), 'all_context_resolutions': len(all_pairs),
                         'scored_resolutions': len(scored),
                         'resolutions_removed_by_pruning': len(all_pairs - scored),
                         'retained_example': list(min(scored)) if scored else None})
        if (index + 1) % 100 == 0:
            print(json.dumps({'inactive_pairs_tested': index + 1, 'total': len(inactive)}), flush=True)
    if contradictions:
        raise ValueError('Unresolved background assumptions exposed missing baseline consequences: '
                         + json.dumps(contradictions))
    lost = [row for row in rows if row['scored_resolutions'] == 0]
    per_class = []
    for name in benchmark.context_ids:
        if name not in background:
            continue
        incident = [row for row in rows if name in (row['left'], row['right'])]
        per_class.append({
            'class_id': name,
            'inactive_candidate_pairs_incident': sum(name in pair for pair in inactive),
            'ordinary_hypotheses_tested': len(incident),
            'zero_credit_by_relation': dict(Counter(row['relation'] for row in incident
                                                    if row['scored_resolutions'] == 0)),
            'ordinary_hypotheses_with_surviving_credit': sum(row['scored_resolutions'] > 0
                                                           for row in incident),
            'direct_independence_credit': 0,
        })
    examples = []
    for title, claims in (
        ('FewP = UP', [Atom('inclusion', 'FewP', 'UP')]),
        ('WPP = LWPP', [Atom('inclusion', 'WPP', 'LWPP')]),
        ('LWPP = SPP', [Atom('inclusion', 'LWPP', 'SPP')]),
        ('coRP = P', [Atom('inclusion', 'coRP', 'P')]),
        ('E has polynomial-size circuits', [Atom('inclusion', 'E', 'Ppoly')]),
        ('E has no polynomial-size circuits', [Atom('separation', 'E', 'Ppoly')]),
        ('coUP is contained in QMA', [Atom('inclusion', 'coUP', 'QMA')]),
        ('coUP is not contained in QMA', [Atom('separation', 'coUP', 'QMA')]),
        ('The polynomial hierarchy collapses to its second level',
         [Atom('inclusion', 'PH', 'Pi2P')]),
    ):
        closure = assumed_closure(benchmark, claims)
        pairs = {a.pair for a in closure.proofs if a.pair in context_candidates}
        scored = pairs & benchmark.unresolved
        examples.append({'title': title, 'claims': [c.json() for c in claims],
                         'all_context_resolutions': len(pairs), 'scored_resolutions': len(scored),
                         'retained_examples': [list(pair) for pair in sorted(scored)[:8]]})
    result = {
        'schema_version': 1, 'status': 'exhaustive_single_hypothesis_pruning_experiment',
        'dataset_sha256': benchmark.digest,
        'context_class_count': len(benchmark.context_ids), 'scored_class_count': len(active),
        'background_classes': sorted(background),
        'all_context_candidate_pairs': len(context_candidates),
        'scored_candidate_pairs': len(benchmark.unresolved),
        'inactive_candidate_pairs': len(inactive),
        'ordinary_hypotheses_tested': len(rows),
        'zero_credit_hypotheses_by_relation': dict(Counter(row['relation'] for row in lost)),
        'zero_credit_hypotheses': lost,
        'per_class': per_class,
        'representative_results': examples,
        'hypothesis_results': rows,
        'limitations': [
            'This compares50 scored endpoints with this61-class context, not with every important class in complexity theory.',
            'An unresolved pair means unresolved in the encoded cited baseline; the historical audit is a separate judgment.',
            'Counts measure consequences found by this inference engine, not importance, likelihood, tractability or all mathematical consequences.',
            'A claim may keep a positive score while losing most of its individual points; the full-context and scored counts are both recorded.',
            'Compound results can behave differently from single-pair assumptions. The representative compounds are examples, not an exhaustive enumeration.',
            'Every inactive pair loses its direct independence point. Independence is never propagated to other pairs.',
            'Per-class incident counts overlap when both endpoints are background classes and must not be summed.',
        ],
    }
    path = ROOT / 'research/v0.4.0/pruning-audit.json'
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({key: result[key] for key in (
        'all_context_candidate_pairs', 'scored_candidate_pairs', 'inactive_candidate_pairs',
        'ordinary_hypotheses_tested', 'zero_credit_hypotheses_by_relation')}))


if __name__ == '__main__':
    build()
