#!/usr/bin/env python3
"""Verify the release ZIP's closure, hashes, provenance, and external digest."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True
from release_evidence import EvidenceError, load_json_bytes, validate_release_evidence

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def parse_manifest(data: bytes, label: str) -> dict[str, str]:
    if not data.endswith(b"\n"):
        fail(f"{label} has no final newline")
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        fail(f"{label} is not UTF-8")
    if not lines:
        fail(f"{label} is empty")
    result: dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            fail(f"malformed {label} line {line_number}")
        digest, name = match.groups()
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
            fail(f"unsafe path in {label}: {name}")
        if name in result:
            fail(f"duplicate path in {label}: {name}")
        result[name] = digest
    return result


def main() -> int:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    version = (ROOT / "VERSION").read_text().strip()
    if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+-preprint", version) is None:
        fail(f"invalid preprint VERSION: {version}")
    expected = BUILD / f"erdos36-{version}-{commit[:12]}.zip"
    archive = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else expected
    if len(sys.argv) > 2:
        fail("usage: verify_release.py [archive.zip]")
    if not archive.is_file():
        fail(f"missing archive {archive}")

    digest_file = archive.with_suffix(archive.suffix + ".sha256")
    if not digest_file.is_file():
        fail("missing companion SHA-256 file")
    companion = parse_manifest(digest_file.read_bytes(), "companion SHA-256 file")
    if set(companion) != {archive.name} or companion[archive.name] != sha256(archive.read_bytes()):
        fail("companion SHA-256 mismatch")

    with zipfile.ZipFile(archive) as handle:
        if handle.testzip() is not None:
            fail("ZIP CRC failure")
        members = handle.namelist()
        if len(members) != len(set(members)):
            fail("duplicate ZIP member")
        if not members:
            fail("empty ZIP")
        if any(not PurePosixPath(name).parts for name in members):
            fail("empty ZIP member name")
        roots = {PurePosixPath(name).parts[0] for name in members}
        if len(roots) != 1:
            fail("archive must have one top-level directory")
        archive_root = next(iter(roots))
        if archive_root != f"erdos36-{version}-{commit[:12]}":
            fail("unexpected archive root directory")
        relative: dict[str, bytes] = {}
        for name in members:
            info = handle.getinfo(name)
            path = PurePosixPath(name)
            if (
                path.is_absolute()
                or ".." in path.parts
                or path.parts[0] != archive_root
                or path.as_posix() != name
            ):
                fail(f"unsafe archive path: {name}")
            rel = PurePosixPath(*path.parts[1:]).as_posix()
            if not rel:
                fail("archive contains an unexpected directory entry")
            mode_type = (info.external_attr >> 16) & 0o170000
            if info.create_system != 3 or mode_type != 0o100000:
                fail(f"archive member is not a normalized regular file: {name}")
            if rel in relative:
                fail(f"duplicate normalized ZIP path: {rel}")
            relative[rel] = handle.read(name)

    generated = {
        "preprint.pdf",
        "COMMIT_SHA.txt",
        "PROVENANCE.json",
        "VERIFICATION_SCOPE.txt",
        "ARTIFACT_SHA256SUMS.txt",
        "evidence/central_verification.json",
        "evidence/central_verification.log",
        "evidence/central_verification.rc",
        "evidence/central_verification.128.json",
        "evidence/central_verification.128.log",
        "evidence/central_verification.128.rc",
        "evidence/outer_verification.json",
        "evidence/composite_verification.json",
    }
    tracked = set(
        subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    )
    expected_archive_paths = tracked | generated
    if set(relative) != expected_archive_paths:
        fail(
            "archive member allowlist mismatch; "
            f"missing={sorted(expected_archive_paths - set(relative))}, "
            f"extra={sorted(set(relative) - expected_archive_paths)}"
        )
    for name in sorted(tracked):
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{name}"], cwd=ROOT
        )
        if relative[name] != committed:
            fail(f"archived source differs from the bound Git commit: {name}")

    forbidden_fragments = ("/.git/", "/upstream/cache/", "/__pycache__/", "/.pytest_cache/", "/internal-handoff/")
    for name in members:
        padded = f"/{name}/"
        if any(fragment in padded for fragment in forbidden_fragments):
            fail(f"forbidden archive member: {name}")

    try:
        provenance = load_json_bytes(relative["PROVENANCE.json"], "PROVENANCE.json")
    except EvidenceError as exc:
        fail(str(exc))
    tree = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip()
    commit_epoch = int(
        subprocess.check_output(
            ["git", "show", "-s", "--format=%ct", "HEAD"], cwd=ROOT, text=True
        ).strip()
    )
    expected_timestamp = datetime.fromtimestamp(commit_epoch, tz=timezone.utc).isoformat()
    expected_provenance_keys = {
        "version",
        "commit",
        "tree",
        "commit_timestamp_utc",
        "verification_run_id",
        "ci_run_url",
        "repository",
        "status",
        "outer_verification_mode",
    }
    if set(provenance) != expected_provenance_keys:
        fail("unexpected PROVENANCE.json schema")
    if (
        provenance.get("commit") != commit
        or provenance.get("tree") != tree
        or provenance.get("commit_timestamp_utc") != expected_timestamp
        or relative["COMMIT_SHA.txt"] != (commit + "\n").encode()
    ):
        fail("archive provenance does not match current commit")
    if provenance.get("status") != "preliminary-unrefereed-not-lean-verified":
        fail("unexpected release status")
    if provenance.get("version") != version:
        fail("archive provenance version does not match VERSION")
    if provenance.get("repository") != "https://github.com/khanukov/erdos36":
        fail("unexpected provenance repository")
    if provenance.get("outer_verification_mode") != "pinned-report-validation-no-arb-rerun":
        fail("unexpected provenance verification scope")
    ci_run_url = provenance.get("ci_run_url")
    if ci_run_url is not None and (
        not isinstance(ci_run_url, str)
        or re.fullmatch(
            r"https://github\.com/khanukov/erdos36/actions/runs/[0-9]+", ci_run_url
        )
        is None
    ):
        fail("invalid provenance CI run URL")
    expected_scope = (
        "Central bins 85-86: fresh directed-rounding C/MPFR verification.\n"
        "Other 170 bins: SHA-256-pinned Price report validation; Arb not rerun.\n"
        "Lean-verified claims: none. Independent reproduction: pending.\n"
    ).encode()
    if relative["VERIFICATION_SCOPE.txt"] != expected_scope:
        fail("unexpected verification-scope disclosure")
    if not relative["preprint.pdf"].startswith(b"%PDF-"):
        fail("packaged preprint is not a PDF")

    artifact_manifest = parse_manifest(
        relative["ARTIFACT_SHA256SUMS.txt"], "ARTIFACT_SHA256SUMS.txt"
    )
    expected_manifest_paths = set(relative) - {"ARTIFACT_SHA256SUMS.txt"}
    if set(artifact_manifest) != expected_manifest_paths:
        fail("internal artifact manifest is not closed")
    for name, digest in artifact_manifest.items():
        if sha256(relative[name]) != digest:
            fail(f"internal artifact hash mismatch: {name}")

    source_manifest = parse_manifest(relative["SHA256SUMS.txt"], "SHA256SUMS.txt")
    expected_source_paths = tracked - {"SHA256SUMS.txt"}
    if set(source_manifest) != expected_source_paths:
        fail(
            "source manifest is not closed over tracked source; "
            f"missing={sorted(expected_source_paths - set(source_manifest))}, "
            f"extra={sorted(set(source_manifest) - expected_source_paths)}"
        )
    for name, digest in source_manifest.items():
        if name not in relative or sha256(relative[name]) != digest:
            fail(f"source manifest mismatch in archive: {name}")

    try:
        evidence = validate_release_evidence(relative, commit=commit, tree=tree)
    except EvidenceError as exc:
        fail(f"invalid generated release evidence: {exc}")
    if provenance.get("verification_run_id") != evidence["composite"].get("run_id"):
        fail("provenance verification run does not match release evidence")

    print(f"PASS: closed release archive ({len(relative)} files)")
    print(f"archive_sha256={companion[archive.name]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
