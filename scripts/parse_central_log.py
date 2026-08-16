#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


if len(sys.argv) != 3:
    raise SystemExit("usage: parse_central_log.py input.log output.json")
text = Path(sys.argv[1]).read_text()
if not text.startswith("PASS\n"):
    raise SystemExit("central log does not start with PASS")
values = {
    "status": "PASS",
    "run_id": os.environ.get("VERIFICATION_RUN_ID"),
    "decimal_fields_are_diagnostic": True,
    "source_commit": git("rev-parse", "HEAD"),
    "source_tree": git("rev-parse", "HEAD^{tree}"),
    "source_dirty": bool(git("status", "--porcelain=v1", "--untracked-files=all")),
}
for line in text.splitlines()[1:]:
    for key, value in re.findall(r"([A-Za-z0-9_]+)=([^ ]+)", line):
        if key in values:
            raise SystemExit(f"duplicate central log field: {key}")
        values[key] = value
required = [
    "target_exact",
    "integral_upper_mpfr",
    "threshold_lower_mpfr",
    "implied_bound_lower_mpfr",
    "D_margin_lower_mpfr",
]
for key in required:
    if key not in values:
        raise SystemExit(f"missing {key}")
if not values["run_id"]:
    raise SystemExit("VERIFICATION_RUN_ID is not set")
values["target"] = values.pop("target_exact")
values["precision_bits"] = int(os.environ.get("CENTRAL_PRECISION_BITS", "0"))
Path(sys.argv[2]).write_text(json.dumps(values, indent=2) + "\n")
print(json.dumps(values, indent=2))
