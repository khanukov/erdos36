#!/usr/bin/env python3
"""Build a normalized, allowlisted manual-deposit archive from a clean commit."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def zip_info(name: str, date_time: tuple[int, int, int, int, int, int]) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=date_time)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def main() -> int:
    if git("status", "--porcelain=v1", "--untracked-files=all"):
        raise SystemExit("refusing release build from a dirty source tree")

    version = (ROOT / "VERSION").read_text().strip()
    commit = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    commit_epoch = int(git("show", "-s", "--format=%ct", "HEAD"))
    date = datetime.fromtimestamp(commit_epoch, tz=timezone.utc)
    # ZIP timestamps have two-second resolution and cannot predate 1980.
    date_time = (date.year, date.month, date.day, date.hour, date.minute, date.second // 2 * 2)
    short = commit[:12]
    archive_root = f"erdos36-{version}-{short}"

    tracked = [name for name in git("ls-files").splitlines() if name]
    if not tracked:
        raise SystemExit("no tracked source files")
    files: dict[str, bytes] = {}
    for name in sorted(tracked):
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"tracked path is missing, non-file, or symlink: {name}")
        files[name] = path.read_bytes()

    generated = {
        "preprint.pdf": BUILD / f"erdos36-preprint-{version}.pdf",
        "evidence/central_verification.json": BUILD / "central_verification.json",
        "evidence/central_verification.log": BUILD / "central_verification.log",
        "evidence/central_verification.rc": BUILD / "central_verification.rc",
        "evidence/central_verification.128.json": BUILD / "central_verification.128.json",
        "evidence/central_verification.128.log": BUILD / "central_verification.128.log",
        "evidence/central_verification.128.rc": BUILD / "central_verification.128.rc",
        "evidence/outer_verification.json": BUILD / "outer_verification.json",
        "evidence/composite_verification.json": BUILD / "composite_verification.json",
    }
    for name, path in generated.items():
        if not path.is_file():
            raise SystemExit(f"missing generated release input: {path.relative_to(ROOT)}")
        files[name] = path.read_bytes()

    central = json.loads(files["evidence/central_verification.json"])
    outer = json.loads(files["evidence/outer_verification.json"])
    composite = json.loads(files["evidence/composite_verification.json"])
    if not (
        central.get("status") == outer.get("status") == composite.get("status") == "PASS"
        and central.get("run_id") == outer.get("run_id") == composite.get("run_id")
    ):
        raise SystemExit("release evidence is not one successful composite run")
    if (
        composite.get("source_commit") != commit
        or composite.get("source_tree") != tree
        or composite.get("source_dirty") is not False
        or central.get("source_commit") != commit
        or central.get("source_tree") != tree
        or central.get("source_dirty") is not False
    ):
        raise SystemExit("composite evidence is not bound to this clean source commit")

    central128 = json.loads(files["evidence/central_verification.128.json"])
    if (
        central128.get("status") != "PASS"
        or central128.get("precision_bits") != 128
        or central128.get("source_commit") != commit
        or central128.get("source_tree") != tree
        or central128.get("source_dirty") is not False
    ):
        raise SystemExit("128-bit evidence is not bound to this clean source commit")

    run_url = None
    if os.environ.get("GITHUB_SERVER_URL") and os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_RUN_ID"):
        run_url = (
            f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
            f"/actions/runs/{os.environ['GITHUB_RUN_ID']}"
        )
    provenance = {
        "version": version,
        "commit": commit,
        "tree": tree,
        "commit_timestamp_utc": date.isoformat(),
        "verification_run_id": composite["run_id"],
        "ci_run_url": run_url,
        "repository": "https://github.com/khanukov/erdos36",
        "status": "preliminary-unrefereed-not-lean-verified",
        "outer_verification_mode": "pinned-report-validation-no-arb-rerun",
    }
    files["PROVENANCE.json"] = (json.dumps(provenance, indent=2) + "\n").encode()
    files["COMMIT_SHA.txt"] = (commit + "\n").encode()
    files["VERIFICATION_SCOPE.txt"] = (
        "Central bins 85-86: fresh directed-rounding C/MPFR verification.\n"
        "Other 170 bins: SHA-256-pinned Price report validation; Arb not rerun.\n"
        "Lean-verified claims: none. Independent reproduction: pending.\n"
    ).encode()

    manifest_lines = [f"{sha256(data)}  {name}" for name, data in sorted(files.items())]
    files["ARTIFACT_SHA256SUMS.txt"] = ("\n".join(manifest_lines) + "\n").encode()

    BUILD.mkdir(exist_ok=True)
    archive = BUILD / f"erdos36-{version}-{short}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for name, data in sorted(files.items()):
            member = str(PurePosixPath(archive_root) / name)
            handle.writestr(zip_info(member, date_time), data)

    digest = sha256(archive.read_bytes())
    digest_path = archive.with_suffix(archive.suffix + ".sha256")
    digest_path.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(f"created {archive.relative_to(ROOT)}")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
