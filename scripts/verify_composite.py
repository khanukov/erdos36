#!/usr/bin/env python3
"""Compose only freshly generated central and outer verification results."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 100
ROOT = Path(__file__).resolve().parents[1]
TARGET = Decimal("0.3805603")


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit("FAIL: source-bound verification requires a Git checkout") from exc


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing generated result: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-fresh",
        action="store_true",
        help="require both components to carry this process's VERIFICATION_RUN_ID",
    )
    args = parser.parse_args()

    central_path = ROOT / "build" / "central_verification.json"
    outer_path = ROOT / "build" / "outer_verification.json"
    central = load_json(central_path)
    outer = load_json(outer_path)

    if central.get("status") != "PASS":
        raise SystemExit("FAIL: fresh central checker did not report PASS")
    rc_path = ROOT / "build" / "central_verification.rc"
    if not rc_path.is_file() or rc_path.read_text().strip() != "0":
        raise SystemExit("FAIL: fresh central checker return code is not zero")
    log_path = ROOT / "build" / "central_verification.log"
    if not log_path.is_file() or not log_path.read_text().startswith("PASS\n"):
        raise SystemExit("FAIL: fresh central log does not start with PASS")
    if outer.get("status") != "PASS":
        raise SystemExit("FAIL: outer report verification did not report PASS")
    if Decimal(str(central.get("target"))) != TARGET:
        raise SystemExit("FAIL: central target does not match the claimed target")
    if central.get("precision_bits") != 96:
        raise SystemExit("FAIL: composite proof expects the standard 96-bit central run")
    if Decimal(str(outer.get("target"))) != TARGET:
        raise SystemExit("FAIL: outer target does not match the claimed target")
    if outer.get("verification_mode") != "pinned-report-validation-no-arb-rerun":
        raise SystemExit("FAIL: unrecognized outer verification mode")
    if outer.get("pinned_commit") != "6bc610e40083ef61a40966dfb5d38612cabc4c5b":
        raise SystemExit("FAIL: outer evidence does not use the pinned Price commit")
    if outer.get("checked_sha256_files") != 19:
        raise SystemExit("FAIL: outer evidence does not cover the exact 19-file manifest")
    if outer.get("outer_bins") != 170 or outer.get("excluded_central_bins") != [85, 86]:
        raise SystemExit("FAIL: outer evidence has the wrong bin scope")

    source_commit = git("rev-parse", "HEAD")
    source_tree = git("rev-parse", "HEAD^{tree}")
    source_dirty = bool(git("status", "--porcelain=v1", "--untracked-files=all"))
    if (
        central.get("source_commit") != source_commit
        or central.get("source_tree") != source_tree
        or central.get("source_dirty") != source_dirty
    ):
        raise SystemExit("FAIL: central evidence does not match the current source state")
    if (
        outer.get("source_commit") != source_commit
        or outer.get("source_tree") != source_tree
        or outer.get("source_dirty") != source_dirty
    ):
        raise SystemExit("FAIL: outer evidence does not match the current source state")

    run_id = os.environ.get("VERIFICATION_RUN_ID")
    if args.require_fresh:
        if not run_id:
            raise SystemExit("FAIL: VERIFICATION_RUN_ID is required for a fresh composition")
        if central.get("run_id") != run_id or outer.get("run_id") != run_id:
            raise SystemExit("FAIL: component results are not from this verification run")

    # The central comparison is performed inside MPFR and represented by the
    # process PASS/return code. The `*_mpfr` strings are also emitted with
    # directed decimal rounding and independently checked for the expected sign.
    if Decimal(str(central["D_margin_lower_mpfr"])) <= 0:
        raise SystemExit("FAIL: nonpositive directed-decimal central margin")
    if Decimal(str(outer["margin"])) <= 0:
        raise SystemExit("FAIL: nonpositive outer report margin")

    result = {
        "status": "PASS",
        "statement": "c_E > 0.3805603",
        "target": str(TARGET),
        "run_id": run_id or central.get("run_id"),
        "source_commit": source_commit,
        "source_tree": source_tree,
        "source_dirty": source_dirty,
        "central_check": "fresh C/MPFR process PASS with directed-decimal enclosure",
        "central_bins": [85, 86],
        "outer_check": "SHA-256-pinned upstream report validation; Arb not rerun",
        "outer_bins": 170,
        "outer_margin": str(outer["margin"]),
        "lean_verified": False,
        "peer_reviewed": False,
    }
    out = ROOT / "build" / "composite_verification.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("PASS: fresh composite verification of c_E > 0.3805603")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
