#!/usr/bin/env python3
"""Schema and parser for the exact pinned Price certificate file set."""

from __future__ import annotations

import re
from collections.abc import Collection
from decimal import Decimal
from pathlib import Path


EXPECTED_FILENAMES = frozenset(
    {
        "arb_0_84_0380554700.csv",
        "arb_0_84_0380554700.json",
        "arb_0_84_0380554700.out",
        "arb_85_88_0380554700.csv",
        "arb_85_88_0380554700.json",
        "arb_85_88_0380554700.out",
        "arb_89_171_0380554700.csv",
        "arb_89_171_0380554700.json",
        "arb_89_171_0380554700.out",
        "combine_arb_reports.py",
        "combine_theorem_target_reports.py",
        "erdos_0380554700_theorem_target_aggregate.json",
        "erdos_0380554700_theorem_target_per_bin.csv",
        "erdos_aug_central_gridF400.json",
        "MANIFEST.md",
        "prove_erdos_0380554275_arb.py",
        "README.md",
        "requirements.txt",
        "run_arb_verification_chunks.sh",
    }
)

COVERAGE_OVERLAP_TOLERANCE = Decimal("1e-15")


def valid_cover_boundary(
    current_hi: Decimal,
    next_lo: Decimal,
    tolerance: Decimal = COVERAGE_OVERLAP_TOLERANCE,
) -> bool:
    """Accept adjacency or a tiny overlap, but never a coverage gap."""

    overlap = current_hi - next_lo
    return overlap >= 0 and overlap <= tolerance


def unexpected_cache_entries(cache: Path, expected: Collection[str]) -> list[str]:
    """Return every cache entry that is not one of the pinned input names."""

    expected_names = set(expected)
    if not cache.is_dir():
        return []
    return sorted(path.name for path in cache.iterdir() if path.name not in expected_names)


def load_expected_manifest(path: Path) -> dict[str, str]:
    """Read a SHA-256 manifest and require exactly the pinned allowlist."""

    result: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            digest, name = line.split(maxsplit=1)
        except ValueError as exc:
            raise ValueError(f"malformed upstream manifest line {number}") from exc
        name = name.strip()
        if name in result:
            raise ValueError(f"duplicate upstream hash path: {name}")
        if Path(name).name != name or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError(f"unsafe name or invalid SHA-256: {name}")
        result[name] = digest

    names = set(result)
    missing = sorted(EXPECTED_FILENAMES - names)
    unexpected = sorted(names - EXPECTED_FILENAMES)
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise ValueError("upstream manifest is not the exact pinned 19-file set (" + "; ".join(details) + ")")
    return result
