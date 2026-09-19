import argparse
import json
import sys
from pathlib import Path

from .benchmark import Benchmark, ROOT, read_json
from .engine import Atom, InvalidEvidence
from .lean_export import export_theorem
from .evaluation import taskset, run_adapter, evaluate_run


def main():
    parser = argparse.ArgumentParser(description="Evaluate AI proof runs on open complexity-class inclusion tasks")
    parser.add_argument("--data-root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("matrix")
    tasks = sub.add_parser("tasks", help="Export the frozen public task suite")
    tasks.add_argument("--output", type=Path)
    run = sub.add_parser("run-adapter", help="Run a trusted model adapter under a shared wall-time budget")
    run.add_argument("--model", required=True)
    run.add_argument("--model-version", required=True)
    run.add_argument("--output", type=Path, required=True)
    selection = run.add_mutually_exclusive_group(required=True)
    selection.add_argument("--task", action="append")
    selection.add_argument("--all-tasks", action="store_true")
    run.add_argument("--wall-seconds", type=int, default=60)
    run.add_argument("--track", choices=["closed-book", "tool-assisted", "smoke-test"], default="tool-assisted")
    run.add_argument("adapter", nargs=argparse.REMAINDER)
    evaluate = sub.add_parser("evaluate-run", help="Aggregate only proof-reviewed attempts from one AI run")
    evaluate.add_argument("manifest", type=Path)
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
        elif args.command == "tasks":
            result = taskset(benchmark)
            if args.output:
                args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
                result = {"written": str(args.output), "task_count": len(result["tasks"]), "taskset_sha256": result["taskset_sha256"]}
        elif args.command == "run-adapter":
            command = args.adapter[1:] if args.adapter[:1] == ["--"] else args.adapter
            if not command:
                raise InvalidEvidence("Supply an adapter command after --")
            selected = [t["task_id"] for t in taskset(benchmark)["tasks"]] if args.all_tasks else args.task
            manifest = run_adapter(benchmark, command, args.model, args.model_version, selected, args.output.resolve(), args.wall_seconds, args.track)
            result = {"manifest": str(manifest), "evaluation": evaluate_run(benchmark, manifest)}
        elif args.command == "evaluate-run":
            result = evaluate_run(benchmark, args.manifest)
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
