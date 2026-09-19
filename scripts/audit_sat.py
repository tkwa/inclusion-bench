"""Find missing propositional consequences of the cited relation theory.

Requires the optional research dependency python-sat (not a runtime dependency).
Runs a single solver, one assumption at a time. SAT is a discovery check, not a
mathematical proof checker: proposed deltas still require reviewed derivations.
Only inclusion/noninclusion atoms are encoded; independence is metatheoretic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark
from inclusion_bench.engine import Atom


def encode(benchmark):
    ids = sorted(benchmark.ids)
    variables = {(a, b): i + 1 for i, (a, b) in
                 enumerate((a, b) for a in ids for b in ids)}
    clauses = []

    def lit(atom):
        assert atom.relation in {'inclusion', 'separation'}
        return variables[atom.pair] * (1 if atom.relation == 'inclusion' else -1)

    def add(values):
        values = set(values)
        if any(-v in values for v in values):
            return
        clauses.append(sorted(values, key=lambda v: (abs(v), v)))

    # Start from cited seeds, rather than trusting the closure being audited.
    for fact in benchmark.knowledge['facts']:
        add([lit(Atom.read(fact))])
    for a in ids:
        add([variables[a, a]])
        for b in ids:
            for c in ids:
                add([-variables[a, b], -variables[b, c], variables[a, c]])
    for a, ca in benchmark.complements.items():
        for b, cb in benchmark.complements.items():
            add([-variables[a, b], variables[ca, cb]])
    for rule in benchmark.rules:
        add([-lit(p) for p in rule.premises] + [lit(rule.conclusion)])
    clauses = sorted(set(tuple(c) for c in clauses))
    return variables, clauses


def audit(benchmark):
    from pysat.solvers import Solver
    import pysat
    variables, clauses = encode(benchmark)
    findings = []
    tested = 0
    with Solver(name='g4', bootstrap_with=clauses) as solver:
        if not solver.solve():
            raise ValueError('Cited relation theory is propositionally inconsistent')
        for a, b in sorted(benchmark.unresolved):
            for sign in (1, -1):
                assumption = sign * variables[a, b]
                if not solver.solve(assumptions=[assumption]):
                    findings.append({'relation': 'separation' if sign == 1 else 'inclusion',
                                     'left': a, 'right': b})
                tested += 1
                if tested % 200 == 0:
                    print(json.dumps({'hypotheses_tested': tested,
                                      'findings': len(findings)}), flush=True)
    return {'schema_version': 1, 'dataset_sha256': benchmark.digest,
            'method': 'Complete propositional entailment in the encoded finite cited theory',
            'solver': {'package': 'python-sat', 'version': pysat.__version__, 'backend': 'Glucose4'},
            'variable_count': len(variables), 'clause_count': len(clauses),
            'cnf_sha256': hashlib.sha256(json.dumps(clauses, separators=(',', ':')).encode()).hexdigest(),
            'hypotheses_tested': tested, 'findings': findings,
            'limitations': 'A SAT model is not a model of complexity theory or ZFC. This detects consequences only of the encoded cited facts, complements, transitivity and registered rules. Solver output is discovery evidence; no classification is changed automatically.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=ROOT / 'research/audit-round1-sat.json')
    args = parser.parse_args()
    result = audit(Benchmark(args.root))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'written': str(args.output), 'findings': len(result['findings'])}), flush=True)
