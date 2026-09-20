"""Compare the provisional roster with its preserved parent mathematical data.

This checks preservation and describes changed scoring scope. It does not
certify historical openness, assign importance weights, or migrate model scores.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark, canonical_hash, read_json
from inclusion_bench.engine import Atom
from inclusion_bench.evaluation import sha256_file


def status(benchmark, left, right):
    return next((relation for relation in ('inclusion', 'separation', 'independence')
                 if Atom(relation, left, right) in benchmark.baseline.proofs), 'unreviewed')


def preserved_records(previous, current, kind):
    current_by_id = {item['id']: item for item in current[kind]}
    changed = [item['id'] for item in previous[kind]
               if current_by_id.get(item['id']) != item]
    if changed:
        raise ValueError(f'Parent {kind} were removed or changed: {changed}')
    return len(previous[kind])


def compare():
    reference_path = ROOT / 'research/v0.4.0/parent-baseline.json'
    reference = read_json(reference_path)
    if canonical_hash(reference['documents']) != reference['dataset_sha256']:
        raise ValueError('Preserved parent documents do not match the parent dataset hash')
    with tempfile.TemporaryDirectory(prefix='inclusion-parent-audit-') as folder:
        parent_root = Path(folder)
        (parent_root / 'data').mkdir()
        for name, document in reference['documents'].items():
            (parent_root / 'data' / f'{name}.json').write_text(json.dumps(document))
        parent = Benchmark(parent_root)
    current = Benchmark(ROOT)
    if not set(parent.context_ids) <= set(current.context_ids):
        raise ValueError('The provisional catalog lost a parent context endpoint')
    retained = set(parent.ids) & set(current.ids)
    added = set(current.ids) - set(parent.ids)
    demoted = set(parent.ids) - set(current.ids)
    inherited = {
        kind: preserved_records(parent.knowledge, current.knowledge, kind)
        for kind in ('sources', 'facts', 'rules')
    }
    current_complements = {tuple(sorted((item['left'], item['right']))): item
                           for item in current.catalog['complements']}
    if any(current_complements.get(tuple(sorted((item['left'], item['right'])))) != item
           for item in parent.catalog['complements']):
        raise ValueError('A parent complement identity was removed or changed')
    changed = []
    retained_counts = {'inclusion': 0, 'separation': 0, 'independence': 0, 'unreviewed': 0}
    added_counts = dict(retained_counts)
    for left in parent.ids:
        for right in parent.ids:
            before, after = status(parent, left, right), status(current, left, right)
            if before != after:
                changed.append({'left': left, 'right': right, 'previous_status': before,
                                'current_status': after})
    for left in current.ids:
        for right in current.ids:
            counts = added_counts if left in added or right in added else retained_counts
            counts[status(current, left, right)] += 1
    result = {
        'schema_version': 1,
        'status': 'provisional_roster_scope_comparison',
        'parent_version': parent.policy['version'],
        'parent_commit': reference['source_commit'],
        'parent_dataset_sha256': parent.digest,
        'parent_reference_sha256': sha256_file(reference_path),
        'dataset_sha256': current.digest,
        'version': current.policy['version'],
        'preserved_parent_records': inherited,
        'preserved_parent_complements': len(parent.catalog['complements']),
        'scored_class_count': len(current.ids),
        'context_class_count': len(current.context_ids),
        'added_scored_classes': sorted(added),
        'demoted_to_background': sorted(demoted),
        'retained_scored_classes': sorted(retained),
        'changed_parent_context_pairs': changed,
        'retained_scored_pair_counts': retained_counts,
        'new_endpoint_pair_counts': added_counts,
        'parent_open_pairs_no_longer_scored_directly': len(
            {pair for pair in parent.unresolved if not set(pair) <= retained}),
        'parent_open_pairs_retained_directly': len(
            {pair for pair in parent.unresolved if set(pair) <= retained}),
        'scoring_comparability': 'Scores and denominators are release-specific. Do not merge leaderboards or transfer a run score between the parent and provisional tasksets.',
        'limitations': [
            'An unchanged parent classification is not automatically an independently repeated literature review.',
            'Preserved background claims can earn points through consequences on active pairs, but never earn a point for their own inactive pair.',
            'This report measures scoring scope and preservation, not the importance or tractability of a research question.',
        ],
    }
    return result


def build():
    result = compare()
    path = ROOT / 'research/v0.4.0/roster-migration.json'
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({key: result[key] for key in (
        'scored_class_count', 'context_class_count', 'added_scored_classes',
        'demoted_to_background', 'changed_parent_context_pairs',
        'retained_scored_pair_counts', 'new_endpoint_pair_counts')}))


if __name__ == '__main__':
    build()
