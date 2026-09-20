"""Keep descriptive claim schemas aligned with the full inference vocabulary.

Claims may name background endpoints. Task assignment and scoring separately
restrict the endpoints that can earn direct points.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ('ai-run.schema.json', 'adapter-response.schema.json', 'submission.schema.json')


def render(schema: dict, catalog: dict) -> dict:
    names = [entry['id'] for entry in catalog['classes']]
    if (not names or any(not isinstance(name, str) or
                        not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', name) for name in names)
            or len(set(names)) != len(names)):
        raise ValueError('Invalid inference vocabulary for claim schemas')
    result = copy.deepcopy(schema)
    for endpoint in ('left', 'right'):
        result['$defs']['atom']['properties'][endpoint]['enum'] = list(names)
    return result


def build(root: Path = ROOT) -> None:
    catalog = json.loads((root / 'data/classes.json').read_text())
    for name in SCHEMAS:
        path = root / 'schemas' / name
        schema = render(json.loads(path.read_text()), catalog)
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    build()
