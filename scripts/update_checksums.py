#!/usr/bin/env python3
from __future__ import annotations

import hashlib
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


rows: list[str] = []
for path in sorted(ROOT.rglob("*")):
    if path.is_file() and not excluded(path):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
(ROOT / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(f"wrote {len(rows)} checksums")
