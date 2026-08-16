#!/usr/bin/env python3
"""Verify the release ZIP's closure, hashes, provenance, and external digest."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    version = (ROOT / "VERSION").read_text().strip()
    expected = BUILD / f"erdos36-{version}-{commit[:12]}.zip"
    archive = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else expected
    if len(sys.argv) > 2:
        fail("usage: verify_release.py [archive.zip]")
    if not archive.is_file():
        fail(f"missing archive {archive}")

    digest_file = archive.with_suffix(archive.suffix + ".sha256")
    if not digest_file.is_file():
        fail("missing companion SHA-256 file")
    fields = digest_file.read_text().strip().split()
    if len(fields) != 2 or fields[1] != archive.name or fields[0] != sha256(archive.read_bytes()):
        fail("companion SHA-256 mismatch")

    with zipfile.ZipFile(archive) as handle:
        if handle.testzip() is not None:
            fail("ZIP CRC failure")
        members = handle.namelist()
        if len(members) != len(set(members)):
            fail("duplicate ZIP member")
        if not members:
            fail("empty ZIP")
        roots = {PurePosixPath(name).parts[0] for name in members}
        if len(roots) != 1:
            fail("archive must have one top-level directory")
        archive_root = next(iter(roots))
        relative: dict[str, bytes] = {}
        for name in members:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or path.parts[0] != archive_root:
                fail(f"unsafe archive path: {name}")
            rel = PurePosixPath(*path.parts[1:]).as_posix()
            if not rel:
                continue
            relative[rel] = handle.read(name)

    required = {
        "README.md",
        "LICENSE",
        "LICENSE_SCOPE.md",
        "paper/LICENSE",
        "paper/main.tex",
        "certificate/central_certificate.json",
        "verifier/verify_central_mpfr.c",
        "preprint.pdf",
        "COMMIT_SHA.txt",
        "PROVENANCE.json",
        "VERIFICATION_SCOPE.txt",
        "ARTIFACT_SHA256SUMS.txt",
        "evidence/central_verification.json",
        "evidence/central_verification.128.json",
        "evidence/outer_verification.json",
        "evidence/composite_verification.json",
    }
    missing = required - set(relative)
    if missing:
        fail(f"missing required members: {sorted(missing)}")

    forbidden_fragments = ("/.git/", "/upstream/cache/", "/__pycache__/", "/.pytest_cache/", "/internal-handoff/")
    for name in members:
        padded = f"/{name}/"
        if any(fragment in padded for fragment in forbidden_fragments):
            fail(f"forbidden archive member: {name}")

    provenance = json.loads(relative["PROVENANCE.json"])
    tree = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip()
    if (
        provenance.get("commit") != commit
        or provenance.get("tree") != tree
        or relative["COMMIT_SHA.txt"].decode().strip() != commit
    ):
        fail("archive provenance does not match current commit")
    if provenance.get("status") != "preliminary-unrefereed-not-lean-verified":
        fail("unexpected release status")

    artifact_manifest: dict[str, str] = {}
    for line in relative["ARTIFACT_SHA256SUMS.txt"].decode().splitlines():
        digest, name = line.split(maxsplit=1)
        artifact_manifest[name.strip()] = digest
    expected_manifest_paths = set(relative) - {"ARTIFACT_SHA256SUMS.txt"}
    if set(artifact_manifest) != expected_manifest_paths:
        fail("internal artifact manifest is not closed")
    for name, digest in artifact_manifest.items():
        if sha256(relative[name]) != digest:
            fail(f"internal artifact hash mismatch: {name}")

    source_manifest: dict[str, str] = {}
    for line in relative["SHA256SUMS.txt"].decode().splitlines():
        digest, name = line.split(maxsplit=1)
        source_manifest[name.strip()] = digest
    for name, digest in source_manifest.items():
        if name not in relative or sha256(relative[name]) != digest:
            fail(f"source manifest mismatch in archive: {name}")

    central = json.loads(relative["evidence/central_verification.json"])
    central128 = json.loads(relative["evidence/central_verification.128.json"])
    outer = json.loads(relative["evidence/outer_verification.json"])
    composite = json.loads(relative["evidence/composite_verification.json"])
    if not (
        central.get("status") == outer.get("status") == composite.get("status") == "PASS"
        and central.get("run_id") == outer.get("run_id") == composite.get("run_id")
    ):
        fail("release evidence is not one successful verification run")
    for label, evidence in (
        ("central", central),
        ("central128", central128),
        ("composite", composite),
    ):
        if (
            evidence.get("source_commit") != commit
            or evidence.get("source_tree") != tree
            or evidence.get("source_dirty") is not False
        ):
            fail(f"{label} evidence is not bound to this clean source commit")
    if outer.get("verification_mode") != "pinned-report-validation-no-arb-rerun":
        fail("outer evidence overstates its verification mode")
    if central128.get("status") != "PASS" or central128.get("precision_bits") != 128:
        fail("missing successful 128-bit central cross-check")
    if central128.get("target") != "0.3805603":
        fail("128-bit cross-check target mismatch")
    for suffix in ("", ".128"):
        if relative[f"evidence/central_verification{suffix}.rc"].decode().strip() != "0":
            fail(f"central{suffix} return code is not zero")
        if not relative[f"evidence/central_verification{suffix}.log"].startswith(b"PASS\n"):
            fail(f"central{suffix} log does not start with PASS")

    print(f"PASS: closed release archive ({len(relative)} files)")
    print(f"archive_sha256={fields[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
