import argparse
import json
import sys
from pathlib import Path

from .benchmark import Benchmark, ROOT, read_json
from .engine import Atom, InvalidEvidence
from .lean_export import export_theorem


def main():
    parser = argparse.ArgumentParser(description="Audit complexity inclusions and calculate hypothetical impact")
    parser.add_argument("--data-root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("matrix")
    score = sub.add_parser("score")
    score.add_argument("submission", type=Path)
    score.add_argument("--official", action="store_true")
    explain = sub.add_parser("explain")
    explain.add_argument("relation", choices=["inclusion", "separation", "independence"])
    explain.add_argument("left")
    explain.add_argument("right")
    explain.add_argument("--assuming", type=Path)
    lean = sub.add_parser("export-lean")
    lean.add_argument("relation", choices=["inclusion", "separation"])
    lean.add_argument("left")
    lean.add_argument("right")
    lean.add_argument("--assuming", type=Path)
    lean.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        benchmark = Benchmark(args.data_root)
        if args.command == "validate":
            matrix = benchmark.matrix()
            result = {"valid": True, "stage": benchmark.policy["release_stage"], "class_count": len(benchmark.ids), "ordered_pairs": len(benchmark.ids) ** 2, "counts": matrix["counts"], "dataset_sha256": benchmark.digest}
        elif args.command == "matrix":
            result = benchmark.matrix()
        elif args.command == "score":
            result = benchmark.score(read_json(args.submission), args.official)
        elif args.command == "export-lean":
            claims = read_json(args.assuming)["claims"] if args.assuming else []
            contents = export_theorem(benchmark, benchmark.closure(claims), Atom(args.relation, args.left, args.right))
            args.output.write_text(contents)
            result = {"written": str(args.output), "conditional": True, "dataset_sha256": benchmark.digest}
        else:
            claims = read_json(args.assuming)["claims"] if args.assuming else []
            result = benchmark.closure(claims).explanation(Atom(args.relation, args.left, args.right))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (InvalidEvidence, ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
