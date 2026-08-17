#!/usr/bin/env python3
"""Validate pinned Price reports for the 170 noncentral bins.

This intentionally does not rerun the upstream Arb verifier.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import uuid
from decimal import Decimal, getcontext
from pathlib import Path

from pinned_manifest import (
    load_expected_manifest,
    unexpected_cache_entries,
    valid_cover_boundary,
)

getcontext().prec = 100
ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
TARGET = Decimal("0.3805603")
CENTRAL = {85, 86}
COMMIT = "6bc610e40083ef61a40966dfb5d38612cabc4c5b"
BALL = re.compile(r"^\[([^ ]+) \+/- ([^\]]+)\]$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT.parent, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit("FAIL: source-bound verification requires a Git checkout") from exc


def verify_cache() -> int:
    try:
        expected = load_expected_manifest(ROOT / "SHA256SUMS.txt")
    except ValueError as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
    extras = unexpected_cache_entries(CACHE, expected)
    require(not extras, "unexpected cache entries: " + ", ".join(extras))
    for name, digest in expected.items():
        path = CACHE / name
        require(path.is_file(), f"missing pinned input {name}")
        require(sha256(path) == digest, f"hash mismatch for {name}")
    return len(expected)


def parse_upper(text: str) -> Decimal:
    match = BALL.match(text.strip())
    if not match:
        raise SystemExit(f"FAIL: bad Arb ball: {text}")
    radius = Decimal(match.group(2))
    require(radius >= 0, "negative Arb radius")
    return Decimal(match.group(1)) + radius


def main() -> int:
    checked_files = verify_cache()
    csv_path = CACHE / "erdos_0380554700_theorem_target_per_bin.csv"
    aggregate_path = CACHE / "erdos_0380554700_theorem_target_aggregate.json"
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    require(aggregate.get("proved_all_bins") is True, "aggregate does not prove all bins")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None, "CSV has no header")
        require(len(reader.fieldnames) == len(set(reader.fieldnames)), "duplicate CSV column")
        rows = list(reader)
    required_columns = {"bin_index", "lo", "hi", "proved", "D_upper_ball"}
    require(rows and required_columns <= set(rows[0]), "missing required CSV columns")
    require(all(None not in row for row in rows), "CSV row has unexpected extra columns")
    require(len(rows) == 172, "expected exactly 172 bin rows")
    indices = [int(row["bin_index"]) for row in rows]
    require(indices == list(range(172)), "bin indices must be ordered and contiguous 0..171")
    require(all(row["proved"].strip().lower() == "true" for row in rows), "unproved bin in report")
    lo_values = [Decimal(row["lo"]) for row in rows]
    hi_values = [Decimal(row["hi"]) for row in rows]
    require(lo_values[0] == Decimal("-1") and hi_values[-1] == Decimal("1"), "bin cover must span [-1,1]")
    require(all(lo <= hi for lo, hi in zip(lo_values, hi_values)), "reversed bin interval")
    # The CSV was emitted through binary64 at one boundary.  Permit only a
    # tiny overlap; a positive gap of any size leaves the domain uncovered.
    for index in range(171):
        overlap = hi_values[index] - lo_values[index + 1]
        require(
            valid_cover_boundary(hi_values[index], lo_values[index + 1]),
            (
                f"gap between bins {index} and {index + 1}"
                if overlap < 0
                else f"material overlap between bins {index} and {index + 1}"
            ),
        )
    require(
        (lo_values[85], hi_values[85], lo_values[86], hi_values[86])
        == (Decimal("-0.003125"), Decimal("0"), Decimal("0"), Decimal("0.003125")),
        "unexpected central-bin endpoints",
    )
    require(aggregate.get("bin_ranges_verified") == [[0, 84], [85, 88], [89, 171]], "unexpected aggregate chunks")
    require(aggregate.get("row_coverage") == "0..171 exactly", "aggregate lacks exact row coverage")
    require(aggregate.get("target") == "0.38055470", "unexpected upstream theorem target")
    for row in rows:
        parse_upper(row["D_upper_ball"])

    outer = [row for row in rows if int(row["bin_index"]) not in CENTRAL]
    require(len(outer) == 170, "expected 170 noncentral bins")
    maxima = [(parse_upper(row["D_upper_ball"]), int(row["bin_index"])) for row in outer]
    max_d, max_bin = max(maxima)
    threshold = Decimal(1) / TARGET
    margin = threshold - max_d
    require(margin > 0, f"outer bin {max_bin} exceeds target threshold")

    run_id = os.environ.get("VERIFICATION_RUN_ID") or str(uuid.uuid4())
    result = {
        "status": "PASS",
        "target": str(TARGET),
        "run_id": run_id,
        "verification_mode": "pinned-report-validation-no-arb-rerun",
        "checked_sha256_files": checked_files,
        "outer_bins": len(outer),
        "excluded_central_bins": sorted(CENTRAL),
        "outer_max_D": str(max_d),
        "outer_max_bin": max_bin,
        "threshold": str(threshold),
        "margin": str(margin),
        "pinned_commit": COMMIT,
        "source_commit": git("rev-parse", "HEAD"),
        "source_tree": git("rev-parse", "HEAD^{tree}"),
        "source_dirty": bool(git("status", "--porcelain=v1", "--untracked-files=all")),
    }
    out = ROOT.parent / "build" / "outer_verification.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("PASS: 170 SHA-256-pinned outer-bin reports satisfy the target (Arb not rerun)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
