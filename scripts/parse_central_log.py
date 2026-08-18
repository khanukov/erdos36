#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from release_evidence import (
    EvidenceError,
    parse_central_log,
    validate_central_log_fields,
)

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit("FAIL: source-bound verification requires a Git checkout") from exc


if len(sys.argv) != 3:
    raise SystemExit("usage: parse_central_log.py input.log output.json")
try:
    fields = parse_central_log(Path(sys.argv[1]).read_bytes(), "central log")
except EvidenceError as exc:
    raise SystemExit(str(exc)) from exc

precision_env = os.environ.get("CENTRAL_PRECISION_BITS")
if precision_env is None or re.fullmatch(r"(?:96|128)", precision_env) is None:
    raise SystemExit("CENTRAL_PRECISION_BITS must be 96 or 128")
logged_precision = int(fields["precision_bits"])
try:
    validate_central_log_fields(
        fields,
        precision=int(precision_env),
        label="central log",
    )
except EvidenceError as exc:
    raise SystemExit(str(exc)) from exc

values: dict[str, object] = {
    "status": "PASS",
    "run_id": os.environ.get("VERIFICATION_RUN_ID"),
    "decimal_fields_are_diagnostic": True,
    "source_commit": git("rev-parse", "HEAD"),
    "source_tree": git("rev-parse", "HEAD^{tree}"),
    "source_dirty": bool(git("status", "--porcelain=v1", "--untracked-files=all")),
}
if not values["run_id"]:
    raise SystemExit("VERIFICATION_RUN_ID is not set")
values.update(fields)
values["target"] = values.pop("target_exact")
values["precision_bits"] = logged_precision
Path(sys.argv[2]).write_text(json.dumps(values, indent=2) + "\n")
print(json.dumps(values, indent=2))
