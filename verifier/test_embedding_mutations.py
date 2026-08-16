#!/usr/bin/env python3
"""Negative tests proving load-bearing certificate mutations are rejected."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verifier" / "check_embedding.py"
SOURCE = ROOT / "verifier" / "verify_central_mpfr.c"
BASE = json.loads((ROOT / "certificate" / "central_certificate.json").read_text())


def accepted(data: dict) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
        json.dump(data, handle)
        handle.flush()
        result = subprocess.run(
            [sys.executable, str(CHECKER), handle.name, str(SOURCE)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    return result.returncode == 0


if not accepted(BASE):
    raise SystemExit("FAIL: unmodified certificate was rejected")


def mutation(name: str, change) -> None:
    data = copy.deepcopy(BASE)
    change(data)
    if accepted(data):
        raise SystemExit(f"FAIL: mutation accepted: {name}")


mutation("target", lambda data: data.__setitem__("target", "0.3805604"))
mutation("bin endpoint", lambda data: data["bin"].__setitem__("hi", "0.0001"))
mutation("unknown row", lambda data: data["rows"][0].__setitem__("kind", "unknown"))
mutation("t2 B", lambda data: data["rows"][0].__setitem__("B", "0.6"))
mutation("free B", lambda data: data["rows"][1].__setitem__("B", "0"))
mutation(
    "cos_pi B",
    lambda data: next(row for row in data["rows"] if row["kind"] == "cos_pi").__setitem__("B", "1e-30"),
)
mutation(
    "nonpositive cos_pi mode",
    lambda data: next(row for row in data["rows"] if row["kind"] == "cos_pi").__setitem__("param", 0),
)
mutation(
    "parseval B",
    lambda data: next(row for row in data["rows"] if row["kind"] == "parseval").__setitem__("B", "0"),
)
mutation(
    "parseval prefix",
    lambda data: next(row for row in data["rows"] if row["kind"] == "parseval").__setitem__("param", 190),
)
mutation("negative multiplier", lambda data: data["rows"][1].__setitem__("lambda", "-1e-20"))
mutation("extra row", lambda data: data["rows"].append(copy.deepcopy(data["rows"][1])))

print("PASS: 11 load-bearing mutations rejected")
