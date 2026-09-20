"""Audit candidate labels using refutation in the existing cited relation theory.

This is an audit tool, not a source of uncited mathematical axioms. Each result
contains both sides of a contradiction under one explicit temporary assumption.
It leaves released data untouched. Run serially; memory is bounded by one closure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark
from inclusion_bench.engine import Atom, Closure, Contradiction


class AuditClosure(Closure):
    conflict = None

    def add(self, atom, reason, parents=(), source_ids=()):
        parents, source_ids = tuple(parents), tuple(source_ids)
        try:
            return super().add(atom, reason, parents, source_ids)
        except Contradiction:
            other = atom.opposite()
            assert other in self.proofs
            self.conflict = {
                'attempted': {**atom.json(), 'id': atom.key, 'reason': reason,
                              'parents': [p.key for p in parents], 'source_ids': list(source_ids)},
                'existing': self.explanation(other),
                'parent_proofs': [self.explanation(p) for p in parents],
            }
            raise


def audit(benchmark):
    findings = []
    tested = 0
    for left, right in sorted(benchmark.unresolved):
        for relation in ('inclusion', 'separation'):
            hypothesis = Atom(relation, left, right)
            closure = AuditClosure(benchmark.context_ids, benchmark.rules, benchmark.complements)
            closure.proofs = dict(benchmark.baseline.proofs)
            try:
                closure.add(hypothesis, 'audit-temporary-assumption')
                closure.saturate()
            except Contradiction:
                findings.append({'conclusion': hypothesis.opposite().json(),
                                 'discharged_assumption': hypothesis.json(),
                                 'contradiction': closure.conflict})
            tested += 1
            if tested % 200 == 0:
                print(json.dumps({'hypotheses_tested': tested, 'findings': len(findings)}), flush=True)
    return {'schema_version': 1, 'dataset_sha256': benchmark.digest,
            'method': 'Single-assumption refutation under the existing cited baseline and rules',
            'hypotheses_tested': tested, 'findings': findings,
            'limitations': 'Not complete propositional consequence finding; does not certify openness. Each proposed correction needs provenance and semantic review.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'research/audit-round1-logical.json')
    args = parser.parse_args()
    result = audit(Benchmark(ROOT))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'written': str(args.output), 'findings': len(result['findings'])}), flush=True)
