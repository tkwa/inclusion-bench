"""Trusted stdin/stdout bridge. Run on Linux with an existing Docker image.

Never execute this file from a candidate submission. The caller supplies the
trusted copy distributed with InclusionBench. No Docker image is pulled.
"""
import hashlib
import json
import os
from collections import namedtuple
from pathlib import Path
import re
import selectors
import shutil
import signal
import subprocess
import tempfile
import time
import uuid

MODULE_NAME = r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
SOURCE_PATH = re.compile(r"(?:lean|quantum|support)/(?:[A-Za-z_][A-Za-z0-9_]*/)*[A-Za-z_][A-Za-z0-9_]*\.lean")
FIRST_PARTY = {"InclusionBench": "lean", "InclusionQuantum": "quantum", "InclusionSupport": "support"}
PROJECT_PATH = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_]*/)*[A-Za-z_][A-Za-z0-9_]*\.lean")
APPROVED_IMPORT_ROOTS = {"Init", "Std", "Lean", "Mathlib", "Batteries", "Aesop", "Qq",
                         "InclusionBench", "InclusionQuantum", "InclusionSupport", "TrustedBaseline"}
RESERVED_MODULE_ROOTS = APPROVED_IMPORT_ROOTS | {"ProofCodec", "ProofExport", "ProofAudit", "Candidate", "AuditImports"}
PROOF_EXPORT_LIMIT_BYTES = 256 * 1024 * 1024
DIAGNOSTIC_LIMIT_BYTES = 8 * 1024 * 1024
AUDIT_REPORT_LIMIT_BYTES = 32 * 1024 * 1024
RESPONSE_LIMIT_BYTES = 40 * 1024 * 1024
WORK_TMPFS_BYTES = 1024 * 1024 * 1024
CaptureResult = namedtuple("CaptureResult", "returncode stdout stderr stdout_bytes stdout_sha256")


class CaptureLimitError(RuntimeError):
    """The bounded subprocess exceeded its time or output allowance."""


def header_imports(source):
    """Read ordinary ASCII import headers, including nested Lean comments."""
    position, imports, saw_prelude = 0, [], False

    def skip():
        nonlocal position
        while position < len(source):
            if source[position].isspace():
                position += 1
            elif source.startswith("--", position):
                end = source.find("\n", position)
                position = len(source) if end < 0 else end + 1
            elif source.startswith("/-", position):
                depth = 1
                position += 2
                while depth and position < len(source):
                    if source.startswith("/-", position):
                        depth += 1
                        position += 2
                    elif source.startswith("-/", position):
                        depth -= 1
                        position += 2
                    else:
                        position += 1
                if depth:
                    raise RuntimeError("Unterminated Lean import-header comment")
            else:
                break

    while True:
        skip()
        match = re.match(r"(import|prelude)\b", source[position:])
        if not match:
            return imports
        directive = match.group()
        position += match.end()
        if directive == "import":
            skip()  # Lean permits comments/newlines before the module name.
        rest_parts = []
        while position < len(source) and source[position] != "\n":
            if source.startswith("--", position):
                end = source.find("\n", position)
                position = len(source) if end < 0 else end
                break
            if source.startswith("/-", position):
                start, depth = position, 1
                position += 2
                while depth and position < len(source):
                    if source.startswith("/-", position):
                        depth += 1
                        position += 2
                    elif source.startswith("-/", position):
                        depth -= 1
                        position += 2
                    else:
                        position += 1
                if depth:
                    raise RuntimeError("Unterminated Lean import-header comment")
                rest_parts.append(" ")
                if "\n" in source[start:position]:
                    break
            else:
                rest_parts.append(source[position])
                position += 1
        rest = "".join(rest_parts).strip()
        if directive == "prelude":
            if rest or saw_prelude or imports:
                raise RuntimeError("Unsupported Lean prelude header")
            saw_prelude = True
        else:
            names = rest.split()
            if not names or any(not re.fullmatch(MODULE_NAME, name) for name in names):
                raise RuntimeError("Use ordinary ASCII module names in Lean import headers")
            imports.extend(names)


def semantic_build_order(sources, trusted_hashes, extra_roots=()):
    """Validate the supplied first-party graph and order the root imports.

    Every path is a trusted packet source, never a path or import extracted
    from Candidate.lean. Auxiliary examples/audits are carried in the packet
    but do not become dependencies merely by being present.
    """
    expected = {path for path in trusted_hashes if path.endswith(".lean")}
    if set(sources) != expected:
        raise RuntimeError("Trusted semantic source set does not match its hash manifest")
    modules = {}
    for path, source in sources.items():
        if not SOURCE_PATH.fullmatch(path) or not isinstance(source, str):
            raise RuntimeError("Unsafe trusted semantic source path or contents")
        if hashlib.sha256(source.encode()).hexdigest() != trusted_hashes[path]:
            raise RuntimeError("Semantic source hash mismatch")
        directory, relative = path.split("/", 1)
        module = relative[:-5].replace("/", ".")
        family = module.split(".", 1)[0]
        if family in FIRST_PARTY:
            if directory != FIRST_PARTY[family] or module in modules:
                raise RuntimeError("Ambiguous first-party Lean module path")
            modules[module] = path
    dependencies = {}
    for module, path in modules.items():
        dependencies[module] = []
        for imported in header_imports(sources[path]):
            if imported.split(".", 1)[0] in FIRST_PARTY:
                if imported not in modules:
                    raise RuntimeError(f"Missing trusted first-party import: {module} imports {imported}")
                dependencies[module].append(imported)
    order, visiting, visited = [], set(), set()

    def visit(module):
        if module in visiting:
            raise RuntimeError("Cyclic trusted first-party imports: " + module)
        if module in visited:
            return
        visiting.add(module)
        for dependency in sorted(set(dependencies[module])):
            visit(dependency)
        visiting.remove(module)
        visited.add(module)
        order.append(modules[module])

    for root in FIRST_PARTY:
        if root not in modules:
            if root == "InclusionSupport" and not any(name.startswith(root + ".") for name in modules):
                continue  # Older packets have no support library.
            raise RuntimeError("Missing trusted root module: " + root)
        visit(root)
    for root in extra_roots:
        if root.split(".", 1)[0] in FIRST_PARTY:
            if root not in modules:
                raise RuntimeError("Missing trusted first-party import: " + root)
            visit(root)
    required = list(order)
    # Also reject a malformed orphan graph, without compiling unused examples.
    for module in sorted(modules):
        visit(module)
    return required


def candidate_plan(project):
    """Validate paths before any snapshot is written outside the sandbox.

    Only text sources are carried on the host. Compiled candidate artifacts
    are created later inside the candidate container's private tmpfs.
    """
    if project is None:
        return {}, [], []
    sources = project["sources"]
    if not isinstance(sources, dict) or not 1 <= len(sources) <= 128:
        raise RuntimeError("Invalid candidate source count")
    manifest_text = project["manifest"]
    if not isinstance(manifest_text, str) or len(manifest_text.encode()) > 64 * 1024:
        raise RuntimeError("Invalid candidate manifest size")
    manifest = json.loads(manifest_text)
    if (not isinstance(manifest, dict) or set(manifest) != {"schema_version", "entrypoint", "files"}
            or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or not isinstance(manifest["files"], list) or len(manifest["files"]) != len(sources)
            or set(manifest["files"]) != set(sources) or manifest["entrypoint"] != project["entrypoint"]):
        raise RuntimeError("Candidate manifest does not match its source snapshot")
    modules, paths_seen = {}, {}
    for path, source in sources.items():
        if (not isinstance(path, str) or len(path) > 240 or not PROJECT_PATH.fullmatch(path)
                or not isinstance(source, str)):
            raise RuntimeError("Unsafe candidate source path or contents")
        module = path[:-5].replace("/", ".")
        if module.split(".", 1)[0].casefold() in {name.casefold() for name in RESERVED_MODULE_ROOTS}:
            raise RuntimeError("Candidate shadows a trusted module")
        parts = module.split(".")
        for length in range(1, len(parts) + 1):
            prefix = ".".join(parts[:length])
            if prefix.casefold() in paths_seen and paths_seen[prefix.casefold()] != prefix:
                raise RuntimeError("Case-colliding candidate modules")
            paths_seen[prefix.casefold()] = prefix
        modules[module] = path
    if len(manifest_text.encode()) + sum(len(source.encode()) for source in sources.values()) > 16 * 1024 * 1024:
        raise RuntimeError("Candidate project exceeds 16 MiB")
    hashes = {path: hashlib.sha256(source.encode()).hexdigest() for path, source in sources.items()}
    hashes["submission.json"] = hashlib.sha256(manifest_text.encode()).hexdigest()
    expected = {"kind": "project", "schema_version": 1, "entrypoint": project["entrypoint"], "files": hashes}
    if project["metadata"] != expected:
        raise RuntimeError("Candidate source hashes do not match metadata")
    dependencies, external = {}, {}
    for module, path in modules.items():
        dependencies[module], external[module] = [], []
        for imported in header_imports(sources[path]):
            if imported in modules:
                dependencies[module].append(imported)
            elif imported.split(".", 1)[0] in APPROVED_IMPORT_ROOTS:
                external[module].append(imported)
            else:
                raise RuntimeError("Unlisted or unapproved candidate import: " + imported)
    order, visited, active = [], set(), set()

    def visit(module):
        if module not in modules:
            raise RuntimeError("Candidate entrypoint is missing")
        if module in active:
            raise RuntimeError("Cyclic candidate imports")
        if module in visited:
            return
        active.add(module)
        for dependency in sorted(set(dependencies[module])):
            visit(dependency)
        active.remove(module)
        visited.add(module)
        order.append(module)

    visit(project["entrypoint"])
    required = list(order)
    imports = sorted({name for module in required for name in external[module]})
    for module in sorted(modules):
        visit(module)
    if required != project["module_order"] or imports != project["external_imports"]:
        raise RuntimeError("Candidate import plan differs from its sources")
    return sources, required, imports


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(command, timeout, *, stdout_limit=DIAGNOSTIC_LIMIT_BYTES,
            stderr_limit=DIAGNOSTIC_LIMIT_BYTES, stdout_path=None):
    """Bound each pipe, optionally streaming exact stdout bytes into a file.

    Streamed output never enters a host-sized bytearray or JSON parser. The
    returned hash covers its original bytes, including invalid UTF-8, so only
    the limited fresh auditor decides whether an export is valid JSON.
    """
    process, output_file = None, None
    selector = selectors.DefaultSelector()
    hasher = hashlib.sha256()
    output_path = Path(stdout_path) if stdout_path is not None else None
    try:
        if output_path is not None:
            output_file = output_path.open("xb")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
        counts = {process.stdout: 0, process.stderr: 0}
        limits = {process.stdout: stdout_limit, process.stderr: stderr_limit}
        chunks = {process.stdout: bytearray(), process.stderr: bytearray()}
        for pipe in counts:
            os.set_blocking(pipe.fileno(), False)
            selector.register(pipe, selectors.EVENT_READ)
        deadline = time.monotonic() + timeout
        while selector.get_map():
            if time.monotonic() >= deadline:
                raise CaptureLimitError("Verifier wall-time limit exceeded")
            for key, _ in selector.select(timeout=0.1):
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj)
                else:
                    counts[key.fileobj] += len(data)
                    if counts[key.fileobj] > limits[key.fileobj]:
                        channel = "stdout" if key.fileobj is process.stdout else "stderr"
                        raise CaptureLimitError(f"Verifier {channel} exceeds {limits[key.fileobj]} bytes")
                    if key.fileobj is process.stdout:
                        hasher.update(data)
                    if key.fileobj is process.stdout and output_file is not None:
                        output_file.write(data)
                    else:
                        chunks[key.fileobj].extend(data)
        try:
            code = process.wait(timeout=max(0.001, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as error:
            raise CaptureLimitError("Verifier wall-time limit exceeded") from error
        return CaptureResult(code, chunks[process.stdout].decode("utf-8", "replace"),
                             chunks[process.stderr].decode("utf-8", "replace"),
                             counts[process.stdout], hasher.hexdigest())
    except BaseException:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        if output_file is not None:
            output_file.close()
            output_path.unlink(missing_ok=True)
        raise
    finally:
        selector.close()
        if output_file is not None:
            output_file.close()
        if process is not None:
            process.stdout.close()
            process.stderr.close()


def capture_container(command, name, timeout, **capture_options):
    """Remove the container even when the client times out or its pipes overflow."""
    try:
        return capture(command, timeout, **capture_options)
    finally:
        subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=20)


def serialize_response(result):
    """Bound the exact UTF-8 wire response, including its terminating newline."""
    output = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    if len(output.encode("utf-8")) + 1 > RESPONSE_LIMIT_BYTES:
        output = json.dumps({"status": "rejected", "reason": "Verifier report exceeds 40 MiB"},
                            separators=(",", ":"))
    return output


def cancel_driver(signum, _frame):
    """Let capture and container finally blocks run on local caller cancellation."""
    raise SystemExit(128 + signum)


def main(packet):
    candidate_sources, candidate_order, candidate_imports = candidate_plan(packet.get("candidate_project"))
    build_order = semantic_build_order(packet["semantic_sources"], packet["trusted_hashes"], candidate_imports)
    if not shutil.which("docker"):
        return {"status": "unavailable", "reason": "Docker is required; there is no unsandboxed fallback"}
    root = Path(packet["remote_root"]).expanduser().resolve(strict=True)
    toolchain = Path(packet.get("toolchain_path") or
                     "~/.elan/toolchains/leanprover--lean4---v4.19.0").expanduser().resolve(strict=True)
    for relative, expected in packet["trusted_hashes"].items():
        if relative.endswith(".lean"):
            if hashlib.sha256(packet["semantic_sources"][relative].encode()).hexdigest() != expected:
                raise RuntimeError("Semantic source hash mismatch")
            continue
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root) or digest(path) != expected:
            return {"status": "unavailable", "reason": "Trusted source/lock mismatch: " + relative}
    image_name = packet["image"]
    image = subprocess.check_output(["docker", "image", "inspect", image_name, "--format", "{{.Id}}"], text=True).strip()
    if not image.startswith("sha256:"):
        raise RuntimeError("Could not resolve installed container image")
    lean_version = subprocess.check_output([str(toolchain / "bin/lean"), "--version"], text=True).strip()
    if "version 4.19.0" not in lean_version:
        raise RuntimeError("Expected pinned Lean 4.19.0")
    package_root = root / "quantum/.lake/packages"
    packages = sorted(p / ".lake/build/lib/lean" for p in package_root.iterdir() if (p / ".lake/build/lib/lean").exists())
    lean_path = ["/config", "/config/lean", "/config/quantum", "/config/support"] + ["/packages/" + str(p.relative_to(package_root)) for p in packages] + ["/toolchain/lib/lean"]
    # The object manifest identifies the exact trusted Mathlib dependencies.
    # Repository semantics are rebuilt below from source on every invocation.
    object_hash = hashlib.sha256()
    for folder in packages:
        for path in sorted(folder.rglob("*.olean")):
            object_hash.update(str(path.relative_to(package_root)).encode())
            object_hash.update(bytes.fromhex(digest(path)))
    toolchain_hash = hashlib.sha256()
    toolchain_files = [toolchain / "bin/lean"] + sorted((toolchain / "lib/lean").rglob("*.olean"))
    toolchain_files += sorted((toolchain / "lib/lean").glob("*.so*"))
    for path in toolchain_files:
        toolchain_hash.update(str(path.relative_to(toolchain)).encode())
        toolchain_hash.update(bytes.fromhex(digest(path)))
    timeout = packet["timeout_seconds"]
    with tempfile.TemporaryDirectory(prefix="inclusion-proofcheck-") as temporary:
        config = Path(temporary)
        config.chmod(0o755)
        for name, source in packet["files"].items():
            if Path(name).name != name:
                raise RuntimeError("Unexpected package path")
            (config / name).write_text(source)
        for relative in packet["trusted_hashes"]:
            if relative.endswith(".lean"):
                path = config / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(packet["semantic_sources"][relative])
        for relative, source in candidate_sources.items():
            path = config / "candidate_sources" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source)
        env = ["-e", "LEAN_PATH=" + ":".join(lean_path), "-e", "LEAN_NUM_THREADS=1", "-e", "HOME=/tmp", "-e", "PATH=/toolchain/bin:/usr/bin:/bin"]
        common = ["docker", "run", "--rm", "--network=none", "--read-only", "--cap-drop=ALL",
                  "--security-opt=no-new-privileges", "--memory=8g", "--memory-swap=8g", "--cpus=1",
                  "--pids-limit=64", "--user", f"{os.getuid()}:{os.getgid()}",
                  "--tmpfs", "/tmp:rw,nosuid,nodev,size=128m", "--tmpfs", f"/work:rw,nosuid,nodev,size={WORK_TMPFS_BYTES}",
                  "--mount", f"type=bind,src={toolchain},dst=/toolchain,readonly",
                  "--mount", f"type=bind,src={package_root},dst=/packages,readonly", *env,
                  "--entrypoint", "/bin/sh"]

        stage_wall_seconds = {}

        def run(stage, script, writable=False, **capture_options):
            started = time.monotonic()
            name = "inclusion-proofcheck-" + uuid.uuid4().hex
            binding = f"type=bind,src={config},dst=/config" + ("" if writable else ",readonly")
            command = [*common, "--name", name, "--mount", binding, image, "-c", script]
            try:
                return capture_container(command, name, timeout, **capture_options)
            finally:
                stage_wall_seconds[stage] = round(time.monotonic() - started, 3)

        # Paths have been restricted to ASCII module components above. Their
        # dependency order is derived only from hash-checked trusted sources.
        # Async elaboration can start many blocked runtime threads even with
        # -j1, exhausting a bounded process budget on long dependency chains.
        # This sandbox has one CPU, so elaborate sequentially in every phase.
        lean_command = "lean -j1 -DElab.async=false"

        def compile_step(path):
            return (f"{lean_command} -o /config/{path[:-5]}.olean /config/{path} || "
                    f"{{ code=$?; echo 'Trusted compilation failed: {path}' >&2; exit $code; }}")

        compile_steps = [compile_step(path) for path in build_order]
        compile_steps += [compile_step(f"{m}.lean") for m in ("ProofCodec", "ProofExport", "TrustedBaseline")]
        if candidate_sources:
            compile_steps.append(compile_step("AuditImports.lean"))
        build = run("trusted_build", "set -eu\ncd /config\n" + "\n".join(compile_steps), writable=True)
        if build.returncode:
            return {"status": "unavailable", "reason": "Trusted verifier build failed", "log": (build.stdout + build.stderr)[-16000:],
                    "stage_wall_seconds": stage_wall_seconds}
        # No host directory is writable during candidate execution. Its only
        # output is a bounded JSON value, never an olean or native library.
        candidate_steps = ["cd /work"]
        if candidate_sources:
            candidate_steps += ["mkdir -p /work/modules", "cp -R /config/candidate_sources/. /work/modules/",
                                'export LEAN_PATH="/work/modules:$LEAN_PATH"', "cd /work/modules"]
            for module in candidate_order:
                path = module.replace(".", "/")
                candidate_steps.append(f"{lean_command} -o {path}.olean {path}.lean || exit $?")
        candidate_steps.append(f"{lean_command} /config/Candidate.lean")
        candidate_script = "\n".join(candidate_steps)
        export_path = config / "proof-export.json"
        try:
            candidate = run("candidate", "(\n" + candidate_script +
                "\n) >/work/compile.log 2>&1\nresult=$?\nif [ $result -ne 0 ]; then cat /work/compile.log >&2; exit $result; fi\ncat /work/proof-export.json",
                stdout_path=export_path, stdout_limit=PROOF_EXPORT_LIMIT_BYTES)
        except CaptureLimitError as error:
            return {"status": "rejected", "reason": "Candidate export failed: " + str(error),
                    "stage_wall_seconds": stage_wall_seconds}
        if candidate.returncode:
            return {"status": "rejected", "reason": "Candidate elaboration/export failed", "log": candidate.stderr[-16000:],
                    "stage_wall_seconds": stage_wall_seconds}
        # Only the fresh, memory-limited auditor parses the candidate JSON.
        export_sha256 = candidate.stdout_sha256
        project_flag = " --project-imports" if candidate_sources else ""
        try:
            replay = run("kernel_replay", f"cd /config\n{lean_command} --run /config/ProofAudit.lean -- /config/proof-export.json /config/targets.json /config/literature.json{project_flag}",
                         stdout_limit=AUDIT_REPORT_LIMIT_BYTES)
        except CaptureLimitError as error:
            return {"status": "rejected", "reason": "Kernel replay failed: " + str(error),
                    "stage_wall_seconds": stage_wall_seconds}
        try:
            report = json.loads(replay.stdout)
        except ValueError:
            return {"status": "unavailable", "reason": "Trusted kernel replay failed to start", "log": (replay.stdout + replay.stderr)[-16000:]}
        if not isinstance(report, dict) or report.get("status") not in {"verified", "needs_literature_review", "rejected", "unavailable"}:
            return {"status": "unavailable", "reason": "Trusted kernel replay returned an invalid status"}
        if replay.returncode and report.get("status") in {"verified", "needs_literature_review"}:
            raise RuntimeError("Kernel replay process failed after reporting success")
        report["proof_export_sha256"] = export_sha256
        report["runtime"] = {"lean": lean_version, "image_id": image, "image_requested": image_name,
                             "toolchain_objects_sha256": toolchain_hash.hexdigest(),
                             "mathlib_objects_sha256": object_hash.hexdigest(),
                             "cpu_limit": 1, "memory_bytes": 8 * 1024**3,
                             "pids_limit": 64, "async_elaboration": False,
                             "proof_export_limit_bytes": PROOF_EXPORT_LIMIT_BYTES,
                             "proof_export_bytes": candidate.stdout_bytes,
                             "work_tmpfs_bytes": WORK_TMPFS_BYTES,
                             "diagnostic_limit_bytes": DIAGNOSTIC_LIMIT_BYTES,
                             "audit_report_limit_bytes": AUDIT_REPORT_LIMIT_BYTES,
                             "response_limit_bytes": RESPONSE_LIMIT_BYTES,
                             "network": "none", "candidate_host_writes": False,
                             "stage_wall_seconds": stage_wall_seconds,
                             "wall_seconds_per_stage": timeout}
        return report


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, cancel_driver)
    signal.signal(signal.SIGHUP, cancel_driver)
    try:
        request = json.load(__import__("sys").stdin)
        result = main(request)
    except Exception as error:
        result = {"status": "unavailable", "reason": str(error)}
    print(serialize_response(result))
