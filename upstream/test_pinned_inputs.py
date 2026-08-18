#!/usr/bin/env python3
"""Negative tests for the pinned manifest and outer-bin cover."""

from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path

from pinned_manifest import (
    EXPECTED_FILENAMES,
    load_expected_manifest,
    unexpected_cache_entries,
    valid_cover_boundary,
)


ROOT = Path(__file__).resolve().parent
GOOD = (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8")


def rejected_manifest(text: str) -> bool:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        try:
            load_expected_manifest(Path(handle.name))
        except ValueError:
            return True
    return False


parsed = load_expected_manifest(ROOT / "SHA256SUMS.txt")
if set(parsed) != EXPECTED_FILENAMES or len(parsed) != 19:
    raise SystemExit("FAIL: committed manifest is not the exact pinned set")

lines = GOOD.splitlines()
if not rejected_manifest("\n".join(lines[1:]) + "\n"):
    raise SystemExit("FAIL: manifest with a missing required file was accepted")
if not rejected_manifest(GOOD + ("0" * 64) + "  unpinned.txt\n"):
    raise SystemExit("FAIL: manifest with an unexpected file was accepted")
if not rejected_manifest(GOOD + lines[0] + "\n"):
    raise SystemExit("FAIL: manifest with a duplicate file was accepted")


if not valid_cover_boundary(Decimal("0"), Decimal("0")):
    raise SystemExit("FAIL: exact adjacency was rejected")
if not valid_cover_boundary(Decimal("0"), Decimal("-9e-17")):
    raise SystemExit("FAIL: observed safe overlap was rejected")
if valid_cover_boundary(Decimal("0"), Decimal("9e-17")):
    raise SystemExit("FAIL: a positive coverage gap was accepted")
if valid_cover_boundary(Decimal("1e-12"), Decimal("0")):
    raise SystemExit("FAIL: a material overlap was accepted")

with tempfile.TemporaryDirectory() as directory:
    cache = Path(directory)
    (cache / "expected.txt").write_text("expected", encoding="utf-8")
    if unexpected_cache_entries(cache, {"expected.txt"}):
        raise SystemExit("FAIL: exact cache allowlist was rejected")
    (cache / "extra.txt").write_text("extra", encoding="utf-8")
    if unexpected_cache_entries(cache, {"expected.txt"}) != ["extra.txt"]:
        raise SystemExit("FAIL: additional cache input was accepted")

print("PASS: exact upstream/cache allowlists and no-gap boundary mutations rejected")
