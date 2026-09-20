"""Trusted-source build ordering and context-roster census regressions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

from inclusion_bench.benchmark import Benchmark, ROOT


def load_script(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


remote = load_script('trusted_remote_runner', 'scripts/proofcheck/remote_runner.py')
census = load_script('external_census', 'scripts/audit_external_census.py')
schemas = load_script('generate_schemas', 'scripts/generate_schemas.py')


class SemanticBuildOrderTests(unittest.TestCase):
    def order(self, sources):
        hashes = {path: hashlib.sha256(body.encode()).hexdigest() for path, body in sources.items()}
        return remote.semantic_build_order(sources, hashes)

    def graph(self):
        return {
            'lean/InclusionBench.lean': 'import InclusionBench.Definitions\n',
            'lean/InclusionBench/Definitions.lean': 'import InclusionBench.LogspaceClasses\nimport InclusionBench.CountingHierarchy\n',
            'lean/InclusionBench/LogspaceClasses.lean': 'import Std\n',
            'lean/InclusionBench/CountingHierarchy.lean': 'import InclusionBench.LogspaceClasses\n',
            'lean/InclusionBench/RealSyntax.lean': 'import Std\n',
            'quantum/InclusionQuantum.lean': 'import InclusionQuantum.Complete\nimport InclusionQuantum.SemanticChecks\n',
            'quantum/InclusionQuantum/Complete.lean': 'import InclusionQuantum.RealFeasibility\nimport InclusionQuantum.Stoquastic\n',
            'quantum/InclusionQuantum/RealFeasibility.lean': 'import Mathlib.Data.Real.Sqrt\nimport InclusionBench.RealSyntax\n',
            'quantum/InclusionQuantum/Stoquastic.lean': 'import InclusionBench\n',
            'quantum/InclusionQuantum/SemanticChecks.lean': 'import InclusionQuantum.Stoquastic\n',
            'lean/UnusedExample.lean': 'import InclusionBench\n',
        }

    def test_new_cross_package_dependencies_are_built_before_importers(self):
        sources = self.graph()
        order = self.order(sources)
        self.assertNotIn('lean/UnusedExample.lean', order)
        self.assertEqual(order, self.order(dict(reversed(list(sources.items())))))
        for path in order:
            for imported in remote.header_imports(sources[path]):
                family = imported.split('.')[0]
                if family in remote.FIRST_PARTY:
                    dependency = remote.FIRST_PARTY[family] + '/' + imported.replace('.', '/') + '.lean'
                    self.assertLess(order.index(dependency), order.index(path))
        self.assertIn('lean/InclusionBench/RealSyntax.lean', order)
        self.assertIn('quantum/InclusionQuantum/RealFeasibility.lean', order)
        self.assertIn('quantum/InclusionQuantum/SemanticChecks.lean', order)

    def test_actual_repository_graph_includes_every_new_definition_and_check(self):
        sources = {str(path.relative_to(ROOT)): path.read_text()
                   for folder in ('lean', 'quantum') for path in (ROOT / folder).rglob('*.lean')
                   if '.lake' not in path.parts}
        order = self.order(sources)
        for name in ('LogspaceClasses', 'CountingHierarchy', 'AlternatingLogtime', 'RealSyntax', 'ClassicalSemanticChecks'):
            self.assertIn(f'lean/InclusionBench/{name}.lean', order)
        for name in ('Unentangled', 'Logspace', 'Stoquastic', 'Statistical', 'RealFeasibility', 'SemanticChecks'):
            self.assertIn(f'quantum/InclusionQuantum/{name}.lean', order)
        self.assertEqual(order[-1], 'quantum/InclusionQuantum.lean')

    def test_missing_dependency_and_missing_root_fail_closed(self):
        for missing in ('lean/InclusionBench/RealSyntax.lean', 'quantum/InclusionQuantum.lean'):
            with self.subTest(missing=missing):
                sources = self.graph()
                del sources[missing]
                with self.assertRaisesRegex(RuntimeError, 'Missing trusted'):
                    self.order(sources)

    def test_cycles_fail_closed_in_required_and_orphan_modules(self):
        for orphan in (False, True):
            sources = self.graph()
            path = 'lean/InclusionBench/Orphan.lean' if orphan else 'lean/InclusionBench/LogspaceClasses.lean'
            name = path[len('lean/'):-5].replace('/', '.')
            sources[path] = f'import {name}\n'
            with self.subTest(orphan=orphan), self.assertRaisesRegex(RuntimeError, 'Cyclic'):
                self.order(sources)

    def test_unsafe_paths_unhashed_sources_and_hash_mismatches_fail_closed(self):
        for unsafe in ('../Candidate.lean', 'lean/../Candidate.lean', 'quantum/Bad;echo.lean', 'quantum/InclusionBench.lean'):
            sources = self.graph()
            sources[unsafe] = ''
            with self.subTest(path=unsafe), self.assertRaises(RuntimeError):
                self.order(sources)
        sources = self.graph()
        with self.assertRaisesRegex(RuntimeError, 'hash manifest'):
            remote.semantic_build_order(sources, {})
        hashes = {path: hashlib.sha256(body.encode()).hexdigest() for path, body in sources.items()}
        hashes['lean/InclusionBench.lean'] = '0' * 64
        with self.assertRaisesRegex(RuntimeError, 'hash mismatch'):
            remote.semantic_build_order(sources, hashes)

    def test_import_header_comments_and_restricted_syntax(self):
        source = '-- generated\n/- outer /- nested -/ comment -/\nimport InclusionBench.X Std -- note\n\ndef x := "import Forged"\n'
        self.assertEqual(remote.header_imports(source), ['InclusionBench.X', 'Std'])
        for bad in ('import Foo; echo bad\n', 'import ../Candidate\n', 'import\n', '/- unterminated'):
            with self.subTest(header=bad), self.assertRaises(RuntimeError):
                remote.header_imports(bad)


class CensusContextTests(unittest.TestCase):
    def test_background_complements_do_not_break_scored_roster_census(self):
        benchmark = Benchmark()
        html = ('<dt>Best inclusions:</dt><dd>∀X: <a href="#P">P</a> '
                '⊆ <a href="#NP">NP</a></dd>').encode()
        result = census.compare(benchmark, html)
        self.assertEqual(set(result['mapping']), set(benchmark.context_ids))
        self.assertIn('coRP', result['mapping'])
        self.assertTrue(any(row['left'] == 'P' and row['right'] == 'NP'
                            for row in result['confirmed_inclusions']))
        self.assertEqual(result['potential_missing_inclusions'], [])


class SchemaContextTests(unittest.TestCase):
    def test_every_published_claim_schema_matches_all_context_endpoints(self):
        benchmark = Benchmark()
        for name in schemas.SCHEMAS:
            schema = json.loads((ROOT / 'schemas' / name).read_text())
            self.assertEqual(schema, schemas.render(schema, benchmark.catalog))
            for endpoint in ('left', 'right'):
                with self.subTest(schema=name, endpoint=endpoint):
                    names = schema['$defs']['atom']['properties'][endpoint]['enum']
                    self.assertEqual(names, benchmark.context_ids)
                    self.assertIn('coRP', names)
                    self.assertIn('QMA2', names)
                    self.assertIn('ExistsR', names)

    def test_schema_generation_preserves_background_and_handles_future_context_nodes(self):
        schema = {'$defs': {'atom': {'properties': {'left': {'enum': []}, 'right': {'enum': []}}}}, 'title': 'preserved'}
        catalog = {'classes': [{'id': 'P'}, {'id': 'Background'}, {'id': 'NewEndpoint'}], 'scored_class_ids': ['P', 'NewEndpoint']}
        generated = schemas.render(schema, catalog)
        self.assertEqual(generated['title'], 'preserved')
        self.assertEqual(generated['$defs']['atom']['properties']['left']['enum'], ['P', 'Background', 'NewEndpoint'])
        self.assertEqual(schema['$defs']['atom']['properties']['left']['enum'], [])


if __name__ == '__main__':
    unittest.main()
