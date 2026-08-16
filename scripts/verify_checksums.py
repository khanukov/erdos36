#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", "build", "internal-handoff", "__pycache__", ".pytest_cache"}
EXCLUDED_PREFIXES = {"upstream/cache"}
EXCLUDED_NAMES = {"SHA256SUMS.txt"}
GENERATED_SUFFIXES = {".aux", ".blg", ".fdb_latexmk", ".fls", ".log", ".out", ".toc", ".synctex.gz"}


def excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if path.name in EXCLUDED_NAMES or any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    if any(rel == prefix or rel.startswith(prefix + "/") for prefix in EXCLUDED_PREFIXES):
        return True
    if any(path.name.endswith(suffix) for suffix in GENERATED_SUFFIXES):
        return True
    if rel.startswith("paper/") and path.suffix == ".pdf":
        return True
    return False


manifest: dict[str, str] = {}
failures: list[str] = []
for number, line in enumerate((ROOT / "SHA256SUMS.txt").read_text().splitlines(), 1):
    if not line.strip():
        continue
    try:
        digest, name = line.split(maxsplit=1)
    except ValueError:
        failures.append(f"malformed manifest line {number}")
        continue
    name = name.strip()
    if name in manifest:
        failures.append(f"duplicate manifest path: {name}")
    manifest[name] = digest

actual_paths = {
    path.relative_to(ROOT).as_posix()
    for path in ROOT.rglob("*")
    if path.is_file() and not excluded(path)
}
listed_paths = set(manifest)
for name in sorted(actual_paths - listed_paths):
    failures.append(f"unlisted file: {name}")
for name in sorted(listed_paths - actual_paths):
    failures.append(f"missing or excluded file listed: {name}")
for name in sorted(actual_paths & listed_paths):
    path = ROOT / name
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != manifest[name]:
        failures.append(f"hash mismatch: {name}")

if failures:
    print("\n".join(failures), file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: closed repository checksum manifest ({len(actual_paths)} files)")
