"""Trusted stdin/stdout bridge. Run on Linux with an existing Docker image.

Never execute this file from a candidate submission. The caller supplies the
trusted copy distributed with InclusionBench. No Docker image is pulled.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import tempfile
import time
import uuid

MODULE_NAME = r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
SOURCE_PATH = re.compile(r"(?:lean|quantum|support)/(?:[A-Za-z_][A-Za-z0-9_]*/)*[A-Za-z_][A-Za-z0-9_]*\.lean")
FIRST_PARTY = {"InclusionBench": "lean", "InclusionQuantum": "quantum", "InclusionSupport": "support"}


def header_imports(source):
    """Read the deliberately restricted import headers of trusted sources.

    Comments may nest. Only ASCII module names on the import line are
    accepted; this is not a parser for candidate Lean programs. Unsupported
    trusted header syntax fails closed instead of silently losing an edge.
    """
    position = 0
    imports = []
    while position < len(source):
        if source[position].isspace():
            position += 1
            continue
        if source.startswith("--", position):
            end = source.find("\n", position)
            position = len(source) if end < 0 else end + 1
            continue
        if source.startswith("/-", position):
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
                raise RuntimeError("Unterminated trusted Lean header comment")
            continue
        match = re.match(r"(import|prelude)\b([^\n]*)", source[position:])
        if not match:
            break
        directive, rest = match.groups()
        rest = rest.split("--", 1)[0].strip()
        if directive == "prelude":
            if rest or imports:
                raise RuntimeError("Unsupported trusted Lean prelude header")
        else:
            names = rest.split()
            if not names or any(not re.fullmatch(MODULE_NAME, name) for name in names):
                raise RuntimeError("Unsupported trusted Lean import header")
            imports.extend(names)
        position += match.end()
    return imports


def semantic_build_order(sources, trusted_hashes):
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
    required = list(order)
    # Also reject a malformed orphan graph, without compiling unused examples.
    for module in sorted(modules):
        visit(module)
    return required


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(command, timeout, limit=40 * 1024 * 1024):
    """Bound both pipes while the process runs, including hostile diagnostics."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    selector = selectors.DefaultSelector()
    for pipe in (process.stdout, process.stderr):
        os.set_blocking(pipe.fileno(), False)
        selector.register(pipe, selectors.EVENT_READ)
    chunks = {process.stdout: bytearray(), process.stderr: bytearray()}
    deadline = time.monotonic() + timeout
    error = None
    try:
        while selector.get_map():
            if time.monotonic() > deadline:
                raise RuntimeError("Verifier wall-time limit exceeded")
            for key, _ in selector.select(timeout=0.1):
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj)
                else:
                    chunks[key.fileobj].extend(data)
                    if sum(map(len, chunks.values())) > limit:
                        raise RuntimeError("Verifier output limit exceeded")
        code = process.wait(timeout=max(1, deadline - time.monotonic()))
    except BaseException as exception:
        error = exception
        process.kill()
        process.wait()
        code = -1
    finally:
        selector.close()
        process.stdout.close()
        process.stderr.close()
    if error:
        raise error
    return code, chunks[process.stdout].decode("utf-8", "replace"), chunks[process.stderr].decode("utf-8", "replace")


def main(packet):
    build_order = semantic_build_order(packet["semantic_sources"], packet["trusted_hashes"])
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
        env = ["-e", "LEAN_PATH=" + ":".join(lean_path), "-e", "LEAN_NUM_THREADS=1", "-e", "HOME=/tmp", "-e", "PATH=/toolchain/bin:/usr/bin:/bin"]
        common = ["docker", "run", "--rm", "--network=none", "--read-only", "--cap-drop=ALL",
                  "--security-opt=no-new-privileges", "--memory=8g", "--memory-swap=8g", "--cpus=1",
                  "--pids-limit=64", "--user", f"{os.getuid()}:{os.getgid()}",
                  "--tmpfs", "/tmp:rw,nosuid,nodev,size=128m", "--tmpfs", "/work:rw,nosuid,nodev,size=256m",
                  "--mount", f"type=bind,src={toolchain},dst=/toolchain,readonly",
                  "--mount", f"type=bind,src={package_root},dst=/packages,readonly", *env,
                  "--entrypoint", "/bin/sh"]

        stage_wall_seconds = {}

        def run(stage, script, writable=False):
            started = time.monotonic()
            name = "inclusion-proofcheck-" + uuid.uuid4().hex
            binding = f"type=bind,src={config},dst=/config" + ("" if writable else ",readonly")
            command = [*common, "--name", name, "--mount", binding, image, "-c", script]
            try:
                return capture(command, timeout)
            finally:
                # Also kills the container if the Docker client timed out or
                # output overflowed; an orphaned candidate cannot keep running.
                subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=20)
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
        code, output, error = run("trusted_build", "set -eu\ncd /config\n" + "\n".join(compile_steps), writable=True)
        if code:
            return {"status": "unavailable", "reason": "Trusted verifier build failed", "log": (output + error)[-16000:],
                    "stage_wall_seconds": stage_wall_seconds}
        # No host directory is writable during candidate execution. Its only
        # output is a bounded JSON value, never an olean or native library.
        code, output, error = run("candidate", f"cd /work\n{lean_command} /config/Candidate.lean >/work/compile.log 2>&1\nresult=$?\nif [ $result -ne 0 ]; then cat /work/compile.log >&2; exit $result; fi\ncat /work/proof-export.json")
        if code:
            return {"status": "rejected", "reason": "Candidate elaboration/export failed", "log": error[-16000:],
                    "stage_wall_seconds": stage_wall_seconds}
        if len(output.encode()) > 32 * 1024 * 1024:
            return {"status": "rejected", "reason": "Proof export exceeds 32 MiB"}
        # Parsing on the host accepts JSON only. No pickle/eval/import/module
        # execution is performed on candidate-controlled output.
        json.loads(output)
        export_sha256 = hashlib.sha256(output.encode()).hexdigest()
        (config / "proof-export.json").write_text(output)
        code, output, error = run("kernel_replay", f"cd /config\n{lean_command} --run /config/ProofAudit.lean /config/proof-export.json /config/targets.json /config/literature.json")
        try:
            report = json.loads(output)
        except ValueError:
            return {"status": "unavailable", "reason": "Trusted kernel replay failed to start", "log": (output + error)[-16000:]}
        if not isinstance(report, dict) or report.get("status") not in {"verified", "needs_literature_review", "rejected", "unavailable"}:
            return {"status": "unavailable", "reason": "Trusted kernel replay returned an invalid status"}
        if code and report.get("status") in {"verified", "needs_literature_review"}:
            raise RuntimeError("Kernel replay process failed after reporting success")
        report["proof_export_sha256"] = export_sha256
        report["runtime"] = {"lean": lean_version, "image_id": image, "image_requested": image_name,
                             "toolchain_objects_sha256": toolchain_hash.hexdigest(),
                             "mathlib_objects_sha256": object_hash.hexdigest(),
                             "cpu_limit": 1, "memory_bytes": 8 * 1024**3,
                             "pids_limit": 64, "async_elaboration": False,
                             "network": "none", "candidate_host_writes": False,
                             "stage_wall_seconds": stage_wall_seconds,
                             "wall_seconds_per_stage": timeout}
        return report


if __name__ == "__main__":
    try:
        request = json.load(__import__("sys").stdin)
        result = main(request)
    except Exception as error:
        result = {"status": "unavailable", "reason": str(error)}
    print(json.dumps(result))
