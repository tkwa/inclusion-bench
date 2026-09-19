"""Replay every current baseline classification's inference trace in Lean.

Literature facts and named implications remain explicit theorem hypotheses.
This checks inference over those premises, not their historical proofs or the
equivalence of operational class definitions. Uses one CPU. An 8 GiB address-space
limit is applied on Linux; peak RSS is recorded on both Linux and macOS.
Build the core Lean library first with scripts/check_lean.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inclusion_bench.benchmark import Benchmark
from inclusion_bench.lean_export import export_theorem


def check(benchmark, compiler):
    version = subprocess.check_output([compiler, '--version'], text=True).strip()
    if 'version 4.19.0' not in version:
        raise ValueError('Lean 4.19.0 required')
    chunks = ['import InclusionBench.Catalog\n']
    targets = []
    for i, atom in enumerate(sorted(benchmark.baseline.proofs)):
        if atom.relation == 'independence':
            raise ValueError('Independence needs its separate metatheory lane')
        name = 'auditBaseline' + str(i)
        targets.append({'declaration': 'InclusionBench.' + name, **atom.json()})
        chunks.append(export_theorem(benchmark, benchmark.baseline, atom, name)
                      .removeprefix('import InclusionBench.Catalog\n'))
    source = '\n'.join(chunks)
    with tempfile.TemporaryDirectory(prefix='inclusion-traces-') as temp:
        path = Path(temp) / 'AllBaseline.lean'
        path.write_text(source)
        env = {**os.environ, 'LEAN_PATH': str(ROOT / 'lean'), 'LEAN_NUM_THREADS': '1'}
        def memory_limit():
            if sys.platform.startswith('linux'):
                resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, 8 * 1024**3))
        run = subprocess.run([compiler, '-j1', str(path)], env=env,
                             text=True, capture_output=True, timeout=600,
                             preexec_fn=memory_limit)
        output = run.stdout + run.stderr
        if run.returncode or 'sorryAx' in output:
            raise RuntimeError(output)
        audits = re.findall(r"'(InclusionBench\.auditBaseline\d+)' (?:depends on axioms: \[(.*?)\]|does not depend on any axioms)", output, re.S)
        if len(audits) != len(targets) or {name for name, _ in audits} != {t['declaration'] for t in targets}:
            raise ValueError('Missing declaration axiom audit output')
        allowed = {'propext', 'Classical.choice', 'Quot.sound'}
        for name, raw in audits:
            dependencies = {a.strip() for a in raw.split(',') if a.strip()}
            if not dependencies <= allowed:
                raise ValueError('Unexpected axiom dependencies for ' + name + ': ' + str(dependencies - allowed))
    return {'schema_version': 1, 'dataset_sha256': benchmark.digest,
            'lean_version': version, 'declaration_count': len(targets),
            'child_peak_rss_bytes': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * (1 if sys.platform == 'darwin' else 1024),
            'generated_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'compiler_output_sha256': hashlib.sha256(output.encode()).hexdigest(),
            'status': 'all_conditional_inference_traces_kernel_checked',
            'allowed_axiom_dependencies': sorted(allowed),
            'targets': targets,
            'scope': 'Checks structural inference only. Cited facts, cited conditional rules and complement identities are explicit hypotheses, not proofs reconstructed from the literature.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    compiler = os.environ.get('LEAN_BIN') or shutil.which('lean')
    if not compiler:
        raise SystemExit('Set LEAN_BIN to Lean 4.19.0')
    result = check(Benchmark(ROOT), compiler)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': result['status'], 'declaration_count': result['declaration_count']}))
