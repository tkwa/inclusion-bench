"""Bounded, immutable snapshots of single-file and ordinary Lean projects."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from .benchmark import canonical_hash
from .engine import InvalidEvidence

MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_PROJECT_BYTES = 16 * 1024 * 1024
MAX_PROJECT_FILES = 128
MAX_MANIFEST_BYTES = 64 * 1024
MODULE_NAME = r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
SOURCE_PATH = r"(?:[A-Za-z_][A-Za-z0-9_]*/)*[A-Za-z_][A-Za-z0-9_]*\.lean"
APPROVED_IMPORT_ROOTS = frozenset({
    "Init", "Std", "Lean", "Mathlib", "Batteries", "Aesop", "Qq",
    "InclusionBench", "InclusionQuantum", "InclusionSupport", "TrustedBaseline",
})
RESERVED_MODULE_ROOTS = APPROVED_IMPORT_ROOTS | {
    "ProofCodec", "ProofExport", "ProofAudit", "Candidate", "AuditImports",
}


@dataclass(frozen=True)
class ProofBundle:
    files: dict[str, bytes]
    sources: dict[str, str]
    entrypoint: str | None
    module_order: tuple[str, ...]
    external_imports: tuple[str, ...]
    proof_sha256: str
    metadata: dict | None


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _read_fd(fd, limit):
    if limit < 0:
        raise InvalidEvidence("Proof input exceeds its size limit")
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        raise InvalidEvidence("Proof inputs must be regular files")
    with os.fdopen(os.dup(fd), "rb") as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise InvalidEvidence("Proof input exceeds its size limit")
    return data


def _read_relative(root_fd, relative, limit):
    """Open each component without following symlinks, then read that inode."""
    current = os.dup(root_fd)
    try:
        parts = relative.split("/")
        for part in parts[:-1]:
            following = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            os.close(current)
            current = following
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=current)
        try:
            return _read_fd(fd, limit)
        finally:
            os.close(fd)
    finally:
        os.close(current)


def _decode(data):
    try:
        return data.decode("utf-8")
    except UnicodeError as error:
        raise InvalidEvidence("Proof source must be UTF-8") from error


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidEvidence("Duplicate submission manifest key: " + key)
        result[key] = value
    return result


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
                    raise InvalidEvidence("Unterminated Lean import-header comment")
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
                    raise InvalidEvidence("Unterminated Lean import-header comment")
                rest_parts.append(" ")
                if "\n" in source[start:position]:
                    break
            else:
                rest_parts.append(source[position])
                position += 1
        rest = "".join(rest_parts).strip()
        if directive == "prelude":
            if rest or saw_prelude or imports:
                raise InvalidEvidence("Unsupported Lean prelude header")
            saw_prelude = True
        else:
            names = rest.split()
            if not names or any(not re.fullmatch(MODULE_NAME, name) for name in names):
                raise InvalidEvidence("Use ordinary ASCII module names in Lean import headers")
            imports.extend(names)


def _project(root_fd):
    manifest_bytes = _read_relative(root_fd, "submission.json", MAX_MANIFEST_BYTES)
    try:
        manifest = json.loads(_decode(manifest_bytes), object_pairs_hook=_unique_object)
    except (ValueError, TypeError) as error:
        raise InvalidEvidence("Invalid submission.json") from error
    if (not isinstance(manifest, dict) or set(manifest) != {"schema_version", "entrypoint", "files"}
            or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1):
        raise InvalidEvidence("Project manifest requires schema_version 1, entrypoint, and files")
    entrypoint, paths = manifest["entrypoint"], manifest["files"]
    if not isinstance(entrypoint, str) or not re.fullmatch(MODULE_NAME, entrypoint):
        raise InvalidEvidence("Project entrypoint must be an ASCII Lean module name")
    if not isinstance(paths, list) or not 1 <= len(paths) <= MAX_PROJECT_FILES:
        raise InvalidEvidence("A Lean project must list between 1 and 128 source files")
    seen, components = set(), {}
    for path in paths:
        if not isinstance(path, str) or len(path) > 240 or not re.fullmatch(SOURCE_PATH, path):
            raise InvalidEvidence("Project files must be relative ASCII .lean module paths")
        if path in seen:
            raise InvalidEvidence("Duplicate project file: " + path)
        seen.add(path)
        root = path.split("/", 1)[0].removesuffix(".lean")
        if root.casefold() in {name.casefold() for name in RESERVED_MODULE_ROOTS}:
            raise InvalidEvidence("Reserved trusted module name: " + path)
        parts = path[:-5].split("/")
        for i in range(1, len(parts) + 1):
            prefix = "/".join(parts[:i])
            folded = prefix.casefold()
            if folded in components and components[folded] != prefix:
                raise InvalidEvidence("Case-colliding project paths")
            components[folded] = prefix
    modules = {path[:-5].replace("/", "."): path for path in paths}
    if entrypoint not in modules:
        raise InvalidEvidence("Project entrypoint is not a listed source file")
    files, sources, remaining = {"submission.json": manifest_bytes}, {}, MAX_PROJECT_BYTES - len(manifest_bytes)
    for path in sorted(paths):
        data = _read_relative(root_fd, path, remaining)
        remaining -= len(data)
        files[path], sources[path] = data, _decode(data)
    dependencies, external = {}, {}
    for module, path in modules.items():
        dependencies[module], external[module] = [], []
        for imported in header_imports(sources[path]):
            if imported in modules:
                dependencies[module].append(imported)
            elif imported.split(".", 1)[0] in APPROVED_IMPORT_ROOTS:
                external[module].append(imported)
            else:
                raise InvalidEvidence(f"Unlisted or unapproved import: {module} imports {imported}")
    order, active, visited = [], set(), set()

    def visit(module):
        if module in active:
            raise InvalidEvidence("Cyclic project imports: " + module)
        if module in visited:
            return
        active.add(module)
        for dependency in sorted(set(dependencies[module])):
            visit(dependency)
        active.remove(module)
        visited.add(module)
        order.append(module)

    visit(entrypoint)
    required = tuple(order)
    imports = tuple(sorted({name for module in required for name in external[module]}))
    for module in sorted(modules):
        visit(module)  # Malformed unused modules still fail validation.
    metadata = {"kind": "project", "schema_version": 1, "entrypoint": entrypoint,
                "files": {path: _sha(data) for path, data in sorted(files.items())}}
    return ProofBundle(files, sources, entrypoint, required, imports, canonical_hash(metadata), metadata)


def load_proof_bundle(path) -> ProofBundle:
    """Snapshot once; callers must compile or seal these returned bytes."""
    path = Path(path)
    try:
        if path.is_dir():
            root_fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                return _project(root_fd)
            finally:
                os.close(root_fd)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            source = _read_fd(fd, MAX_SOURCE_BYTES)
        finally:
            os.close(fd)
        return ProofBundle({path.name: source}, {path.name: _decode(source)}, None, (), (), _sha(source), None)
    except OSError as error:
        raise InvalidEvidence("Cannot read proof input without following symlinks: " + str(error)) from error


def proof_digest(path) -> str:
    return load_proof_bundle(path).proof_sha256
