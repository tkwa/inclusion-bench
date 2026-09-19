import argparse
import json
import sys
from pathlib import Path

from .benchmark import Benchmark, ROOT, read_json
from .engine import Atom, InvalidEvidence
from .lean_export import export_theorem
from .evaluation import taskset, run_adapter, evaluate_run
from .runner import preflight, run_config, freeze_release
from .reviews import review_packet, record_run_review, record_proof_review, record_history_review, publish_run


def main():
    parser = argparse.ArgumentParser(description="Evaluate AI proof runs on open complexity-class inclusion tasks")
    parser.add_argument("--data-root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("matrix")
    sub.add_parser("freeze", help="Freeze a versioned candidate suite without certifying all questions open")
    for command in ("preflight", "run"):
        configured = sub.add_parser(command, help="Check or run a budgeted provider configuration")
        configured.add_argument("--config", type=Path, required=True)
        configured.add_argument("--model")
        choice = configured.add_mutually_exclusive_group()
        choice.add_argument("--task", action="append")
        choice.add_argument("--all-tasks", action="store_true")
        if command == "preflight":
            configured.add_argument("--no-credentials", action="store_true")
        else:
            configured.add_argument("--output", type=Path, required=True)
            configured.add_argument("--resume", action="store_true")
    packet = sub.add_parser("review-packet")
    packet.add_argument("manifest", type=Path)
    packet.add_argument("--output", type=Path, required=True)
    for command in ("review-run", "review-proof"):
        review = sub.add_parser(command)
        review.add_argument("manifest", type=Path)
        review.add_argument("review", type=Path)
        if command == "review-proof":
            review.add_argument("--attempt-id")
    publish = sub.add_parser("publish-run", help="Package a reviewed run and register it for website publication")
    publish.add_argument("manifest", type=Path)
    history = sub.add_parser("review-history")
    history.add_argument("review", type=Path)
    verify = sub.add_parser("verify-proof")
    verify.add_argument("source", type=Path)
    verify.add_argument("--claims", type=Path, required=True)
    verify.add_argument("--report", type=Path, required=True)
    verify.add_argument("--host", default="tkwa-ubuntu-box-wan")
    verify.add_argument("--local", action="store_true", help="Use Docker on this Linux host")
    verify.add_argument("--image", default="nvidia/cuda:12.4.1-devel-ubuntu22.04")
    verify.add_argument("--toolchain-path")
    verify.add_argument("--remote-root", default="/home/tkwa/code/inclusion-quantum-build")
    verify.add_argument("--timeout-seconds", type=int, default=120)
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
        elif args.command == "freeze":
            result = freeze_release(benchmark)
        elif args.command in {"preflight", "run"}:
            config = read_json(args.config)
            if args.task:
                config["selection"] = {"task_ids": args.task}
            elif args.all_tasks:
                config["selection"] = {"all_tasks": True, "seed": 0}
            if args.command == "preflight":
                result = preflight(benchmark, config, args.model, require_credentials=not args.no_credentials)
            else:
                manifest = run_config(benchmark, config, args.output, model_override=args.model, resume=args.resume)
                result = {"manifest": str(manifest), "evaluation": evaluate_run(benchmark, manifest)}
        elif args.command == "review-packet":
            result = review_packet(benchmark, args.manifest)
            args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
            result = {"written": str(args.output), "run_sha256": result["run_sha256"]}
        elif args.command == "review-run":
            review = read_json(args.review)
            result = record_run_review(benchmark, args.manifest, review.get('run_review', review))
        elif args.command == "review-proof":
            review = read_json(args.review)
            if 'proof_reviews' in review:
                choices = [r for r in review['proof_reviews'] if not args.attempt_id or r.get('attempt_id') == args.attempt_id]
                if len(choices) != 1:
                    raise InvalidEvidence('Select exactly one proof review from the packet with --attempt-id')
                review = choices[0]
            if review.get('proof_report') and not Path(review['proof_report']).is_absolute():
                review['proof_report'] = str((args.review.parent / review['proof_report']).resolve())
            result = record_proof_review(benchmark, args.manifest, review)
        elif args.command == "review-history":
            review = read_json(args.review)
            result = record_history_review(benchmark, review.get('history_review', review))
        elif args.command == "publish-run":
            result = publish_run(benchmark, args.manifest)
        elif args.command == "verify-proof":
            from .proofcheck import verify_proof
            claims = read_json(args.claims)
            result = verify_proof(benchmark, args.source, claims.get("claims", []) if isinstance(claims, dict) else claims,
                                  report_path=args.report, host=None if args.local else args.host, remote_root=args.remote_root,
                                  image=args.image, toolchain_path=args.toolchain_path, timeout_seconds=args.timeout_seconds)
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
        if args.command == "verify-proof" and result.get("status") != "verified":
            return 1
    except (InvalidEvidence, ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
