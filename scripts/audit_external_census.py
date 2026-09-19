"""Compare a downloaded Complexity Zoology census with the cited baseline.

Input is the HTML at https://www.math.ucdavis.edu/~greg/zoology/relations.html.
Only universally relativizing inclusions are extracted. Oracle separations and
the source's open/blank labels are never treated as unrelativized classifications.
The HTML is parsed as data, never executed. No network access is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark
from inclusion_bench.engine import Atom

OVERRIDES = {
    'AC0': 'AC^0/poly', 'ACC0': 'ACC^0/poly', 'TC0': 'TC^0/poly',
    'NC1': 'NC^1/poly', 'LogCFL': 'SAC^1', 'CeqP': 'C_=P',
    'parityP': '+P', 'NPcapcoNP': 'cocap.NP', 'Sigma2P': 'Sigma_2P',
    'Pi2P': 'co.Sigma_2P', 'Delta2P': 'Delta_2P', 'Theta2P': 'P^{NP[log]}',
    'Ppoly': 'P/poly', 'NPpoly': 'NP/poly',
    **{name: 'co.' + name[2:] for name in ['coRP', 'coUP', 'coNP', 'coMA', 'coAM', 'coQMA']},
}


def extract(text):
    edges = set()
    for body in re.findall(r'<dt>Best inclusions:.*?</dt>\s*<dd>(.*?)</dd>', text, re.S):
        body = html.unescape(body)
        if not re.match(r'\s*∀X:', body):
            raise ValueError('Unexpected inclusion scope in external census')
        groups = []
        for segment in body.split('⊆'):
            names = re.findall(r'<a href="#[^"]+">(.*?)</a>|<b>(.*?)</b>', segment, re.S)
            groups.append([re.sub(r'<[^>]*>', '', a or b) for a, b in names])
        if any(not group for group in groups):
            raise ValueError('Unparsed endpoint in inclusion chain')
        for left, right in zip(groups, groups[1:]):
            edges.update((a, b) for a in left for b in right)
    if not edges:
        raise ValueError('No universal inclusions found')
    return edges


def compare(benchmark, raw):
    edges = extract(raw.decode())
    extracted = set(edges)
    original_nodes = {v for edge in edges for v in edge}
    mapping = {name: OVERRIDES.get(name, name) for name in benchmark.ids}
    comp = {mapping[a]: mapping[b] for a, b in benchmark.complements.items()}

    def co(name):
        if name in comp:
            return comp[name]
        if name.startswith('co.'):
            return name[3:]
        if name.startswith('cocap.'):
            return name
        return 'co.' + name

    for name in original_nodes:
        if name.startswith('cocap.'):
            base = name[6:]
            edges.add((name, base))
            edges.add((name, co(base)))
    edges |= {(co(a), co(b)) for a, b in list(edges)}
    nodes = {v for edge in edges for v in edge}
    reachable = {a: {a} for a in nodes}
    for a, b in edges:
        reachable[a].add(b)
    for middle in sorted(nodes):
        for a in nodes:
            if middle in reachable[a]:
                reachable[a].update(reachable[middle])
    confirmed, missing = [], []
    for a, ea in mapping.items():
        for b, eb in mapping.items():
            # Retain only endpoints explicitly appearing in the source graph.
            if ea not in original_nodes or eb not in original_nodes:
                continue
            if eb in reachable[ea]:
                row = {'left': a, 'right': b, 'external_left': ea, 'external_right': eb}
                (confirmed if Atom('inclusion', a, b) in benchmark.baseline.proofs else missing).append(row)
    return {
        'schema_version': 1,
        'source_url': 'https://www.math.ucdavis.edu/~greg/zoology/relations.html',
        'intro_url': 'https://www.math.ucdavis.edu/~greg/zoology/',
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'extracted_edge_count': len(extracted), 'explicit_node_count': len(original_nodes),
        'dataset_sha256': benchmark.digest,
        'scope': 'External universal-oracle inclusion edges only; oracle separations NEVER counted as unrelativized separations. Source is an older discovery census, not a 2026 openness certification.',
        'mapping': mapping,
        'mapping_limitations': [
            'Uniform NC convention and uniform SAC1/LogCFL equivalence require explicit review.',
            'Nonuniform classes mapped to /poly variants; unavailable nodes excluded.',
            'Complement identities reused from our catalog, so this component is not independent.',
        ],
        'confirmed_inclusions': confirmed,
        'potential_missing_inclusions': missing,
        'unmatched_classes': [a for a, ea in mapping.items() if ea not in original_nodes],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=ROOT / 'research/audit-round1-external-census.json')
    args = parser.parse_args()
    result = compare(Benchmark(args.root), args.html.read_bytes())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({key: len(result[key]) for key in
                      ['confirmed_inclusions', 'potential_missing_inclusions', 'unmatched_classes']}))
