#!/usr/bin/env python3
"""Provision the public Linux verifier without installing host packages.

Docker, Python 3, Git, and a public repository checkout are needed on the host.
Downloads and cache extraction run in a trusted setup container, 1 CPU/8 GiB.
Submitted proofs are never used by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import uuid

VERSION = "4.19.0"
MODULES = ["Mathlib.Data.Complex.Basic", "Mathlib.Data.Real.Sqrt",
           "Mathlib.Data.Fintype.Pi", "Mathlib.Algebra.BigOperators.Group.Finset.Basic"]


def requested_modules(extra=()):
    """Extend the pinned cache explicitly, without reading candidate programs."""
    if not isinstance(extra, (list, tuple)) or any(
            not isinstance(module, str) or len(module) > 240 or
            not re.fullmatch(r"Mathlib(?:\.[A-Za-z_][A-Za-z0-9_]*)+", module)
            for module in extra):
        raise RuntimeError("Extra cache modules must be qualified Mathlib module names")
    return list(dict.fromkeys([*MODULES, *extra]))


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def version(toolchain):
    text = subprocess.check_output([str(toolchain / "bin/lean"), "--version"], text=True).strip()
    if f"version {VERSION}" not in text:
        raise RuntimeError(f"Expected Lean {VERSION}: {text}")
    return text


def locked_packages(root):
    manifest = json.loads((root / "quantum/lake-manifest.json").read_text())
    return [p for p in manifest["packages"] if p["type"] == "git"]


def check(root, toolchain, modules=None):
    modules = requested_modules(modules or [])
    info = {"lean": version(toolchain), "dependencies": {}, "mathlib_modules": modules}
    for package in locked_packages(root):
        path = root / "quantum/.lake/packages" / package["name"]
        revision = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
        if revision != package["rev"]:
            raise RuntimeError("Dependency revision mismatch: " + package["name"])
        run(["git", "-C", str(path), "diff", "--quiet"])
        run(["git", "-C", str(path), "diff", "--cached", "--quiet"])
        info["dependencies"][package["name"]] = revision
    cache = root / "quantum/.lake/packages/mathlib/.lake/build/lib/lean"
    for module in modules:
        if not (cache / (module.replace(".", "/") + ".olean")).is_file():
            raise RuntimeError("Missing requested Mathlib cache module: " + module)
    return info


def provision(request):
    # The outer Docker cgroup bounds aggregate memory and CPU. Affinity also
    # prevents cache extraction from seeing every CPU on the host.
    modules = requested_modules(request.get("mathlib_modules", []))
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    os.setgid(request["gid"])
    os.setuid(request["uid"])
    root, toolchain = Path("/workspace"), Path("/toolchain")
    home = Path("/tmp/provision-home")
    home.mkdir()
    os.environ.update(HOME=str(home), PATH="/toolchain/bin:/usr/bin:/bin",
                      LEAN_NUM_THREADS="1", MATHLIB_NO_CACHE_ON_UPDATE="1",
                      OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    if not (toolchain / "bin/lean").exists():
        machine = platform.machine()
        suffix = {"x86_64": "linux", "aarch64": "linux_aarch64"}.get(machine)
        if suffix is None:
            raise RuntimeError("Supported Linux architectures are x86_64 and aarch64")
        asset_name = f"lean-{VERSION}-{suffix}.tar.zst"
        api = f"https://api.github.com/repos/leanprover/lean4/releases/tags/v{VERSION}"
        with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": "InclusionBench-setup"})) as response:
            release = json.load(response)
        asset = next(a for a in release["assets"] if a["name"] == asset_name)
        archive = toolchain / "download.tar.zst"
        run(["curl", "--fail", "--location", "--retry", "3", "--proto", "=https",
             "--output", str(archive), asset["browser_download_url"]])
        hasher = hashlib.sha256()
        with archive.open("rb") as handle:
            while block := handle.read(1024 * 1024):
                hasher.update(block)
        digest = hasher.hexdigest()
        if asset.get("digest") and asset["digest"] != "sha256:" + digest:
            raise RuntimeError("Official release asset digest mismatch")
        run(["tar", "--zstd", "-xf", str(archive), "--strip-components=1", "-C", str(toolchain)])
        archive.unlink()
        (toolchain / "inclusion-install.json").write_text(json.dumps({
            "asset_url": asset["browser_download_url"], "archive_sha256": digest,
            "github_asset_digest": asset.get("digest")}, indent=2) + "\n")
    version(toolchain)
    quantum = root / "quantum"
    lock_before = (quantum / "lake-manifest.json").read_bytes()
    for package in locked_packages(root):
        path = quantum / ".lake/packages" / package["name"]
        if not path.exists():
            path.mkdir(parents=True)
            run(["git", "init", str(path)])
            run(["git", "-C", str(path), "remote", "add", "origin", package["url"]])
            run(["git", "-C", str(path), "fetch", "--depth", "1", "origin", package["rev"]])
            run(["git", "-C", str(path), "checkout", "--detach", "FETCH_HEAD"])
        actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
        if actual != package["rev"]:
            raise RuntimeError("Existing dependency differs from lock; use a fresh checkout: " + package["name"])
    # Respect the committed lock; `lake update` would re-resolve dependencies.
    run(["lake", "exe", "cache", "get", *modules], cwd=quantum)
    if (quantum / "lake-manifest.json").read_bytes() != lock_before:
        raise RuntimeError("Setup unexpectedly changed the dependency lock")
    info = check(root, toolchain, modules)
    (root / ".tools/proofcheck-provision.json").write_text(json.dumps(info, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--toolchain-path", type=Path)
    parser.add_argument("--image", default="ubuntu:22.04")
    parser.add_argument("--check-only", action="store_true", help="Inspect existing installation without downloading or changing it")
    parser.add_argument("--skip-pull", action="store_true", help="Require the selected image to be installed already")
    parser.add_argument("--mathlib-module", action="append", default=[],
                        help="Also install/check this pinned Mathlib module and its dependencies; repeat for more modules")
    parser.add_argument("--inside", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inside:
        provision(json.loads(args.inside.read_text()))
        return
    modules = requested_modules(args.mathlib_module)
    if platform.system() != "Linux":
        raise RuntimeError("Run setup on the Linux verifier host, locally or over SSH")
    root = (args.repo or Path(__file__).resolve().parents[2]).expanduser().resolve(strict=True)
    toolchain = (args.toolchain_path or root / ".tools/lean-4.19.0").expanduser().resolve()
    if args.check_only:
        print(json.dumps(check(root, toolchain, modules), indent=2))
        return
    if not shutil.which("docker"):
        raise RuntimeError("Install Docker Engine and allow your user to run it before setup")
    (root / ".tools").mkdir(exist_ok=True)
    toolchain.mkdir(parents=True, exist_ok=True)
    if not args.skip_pull:
        run(["docker", "pull", args.image])
    image_id = subprocess.check_output(["docker", "image", "inspect", args.image,
                                        "--format", "{{.Id}}"], text=True).strip()
    with tempfile.TemporaryDirectory(prefix="inclusion-setup-") as directory:
        setup = Path(directory)
        setup.chmod(0o755)
        shutil.copyfile(__file__, setup / "setup_linux.py")
        (setup / "request.json").write_text(json.dumps({"uid": os.getuid(), "gid": os.getgid(),
                                                      "mathlib_modules": modules}))
        name = "inclusion-provision-" + uuid.uuid4().hex
        # Network and writable mounts are confined to this trusted dependency
        # installer. The candidate proof verifier always disables both.
        command = ["docker", "run", "--rm", "--name", name,
                   "--cpus=1", "--memory=8g", "--memory-swap=8g", "--pids-limit=128",
                   "--mount", f"type=bind,src={root},dst=/workspace",
                   "--mount", f"type=bind,src={toolchain},dst=/toolchain",
                   "--mount", f"type=bind,src={setup},dst=/setup,readonly",
                   "--entrypoint", "/bin/sh", image_id, "-c",
                   "set -eu\nexport DEBIAN_FRONTEND=noninteractive\n"
                   "apt-get update -qq\napt-get install -y -qq --no-install-recommends ca-certificates curl git zstd python3\n"
                   "exec python3 /setup/setup_linux.py --inside /setup/request.json"]
        try:
            run(command)
        finally:
            subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    configuration = {"host": None, "remote_root": str(root), "toolchain_path": str(toolchain),
                     "image": image_id}
    (root / ".tools/proofcheck-runtime.json").write_text(json.dumps(configuration, indent=2) + "\n")
    print("Verifier ready. Use these verify_proof keyword arguments:")
    print(json.dumps(configuration, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
