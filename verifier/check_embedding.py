#!/usr/bin/env python3
"""Check every load-bearing certificate field embedded in the C verifier."""

from __future__ import annotations

import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: check_embedding.py certificate.json verifier.c")

certificate_path, source_path = map(Path, sys.argv[1:])
candidate = json.loads(certificate_path.read_text(encoding="utf-8"))
source = source_path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def string_array(name: str) -> list[str]:
    match = re.search(
        rf"static const char \*{re.escape(name)}\[[^\]]+\] = \{{(.*?)\n\}};",
        source,
        re.S,
    )
    require(match is not None, f"missing C string array {name}")
    return re.findall(r'"([^"]*)"', match.group(1))


def int_array(name: str) -> list[int]:
    match = re.search(
        rf"static const int {re.escape(name)}\[[^\]]+\] = \{{(.*?)\}};",
        source,
        re.S,
    )
    require(match is not None, f"missing C integer array {name}")
    return [int(value) for value in re.findall(r"-?\d+", match.group(1))]


def scalar(name: str) -> str:
    match = re.search(
        rf'static const char \*{re.escape(name)} = "([^"]*)";', source
    )
    require(match is not None, f"missing C scalar {name}")
    return match.group(1)


def define(name: str) -> int:
    match = re.search(rf"^#define {re.escape(name)} (\d+)$", source, re.M)
    require(match is not None, f"missing C define {name}")
    return int(match.group(1))


require(
    set(candidate) == {"description", "bin", "target", "rows", "floating_diagnostic", "lemma"},
    "unexpected top-level certificate fields",
)
require(candidate["bin"] == {"lo": "-0.003125", "hi": "0"}, "wrong central bin")
require(candidate["target"] == "0.3805603", "wrong certificate target")
require(isinstance(candidate["rows"], list), "rows must be a list")

allowed_kinds = {"t2", "cos", "cos_pi", "parseval"}
for index, row in enumerate(candidate["rows"]):
    require(set(row) == {"kind", "param", "B", "lambda"}, f"row {index}: wrong fields")
    require(row["kind"] in allowed_kinds, f"row {index}: unknown kind")
    require(isinstance(row["B"], str), f"row {index}: B must be a decimal string")
    require(isinstance(row["lambda"], str), f"row {index}: lambda must be a decimal string")
    try:
        multiplier = Decimal(row["lambda"])
        Decimal(row["B"])
    except InvalidOperation as exc:
        raise AssertionError(f"row {index}: invalid decimal") from exc
    require(multiplier >= 0, f"row {index}: negative multiplier")

free = [row for row in candidate["rows"] if row["kind"] == "cos"]
cos_pi = [row for row in candidate["rows"] if row["kind"] == "cos_pi"]
parseval = [row for row in candidate["rows"] if row["kind"] == "parseval"]
t2 = [row for row in candidate["rows"] if row["kind"] == "t2"]

require(len(t2) == 1 and t2[0]["param"] is None, "expected one t2 row")
require(all(row["B"] == "0" for row in cos_pi), "cos_pi B must be exactly 0")
require(all(row["B"] == "0.5" for row in parseval), "parseval B must be exactly 0.5")
require([int(row["param"]) for row in parseval] == [191, 195, 200], "wrong prefixes")
require(all(isinstance(row["param"], int) for row in cos_pi + parseval), "integer mode required")
require(all(isinstance(row["param"], str) for row in free), "free frequency must be a string")
require(all(int(row["param"]) >= 1 for row in cos_pi + parseval), "mode must be positive")
require(all(Decimal(row["param"]) > 0 for row in free), "free frequency must be positive")

require(define("NFREE") == len(free), "NFREE mismatch")
require(define("NCP") == len(cos_pi), "NCP mismatch")
require(define("NPV") == len(parseval), "NPV mismatch")
require(define("KMAX") == max(int(row["param"]) for row in cos_pi + parseval), "KMAX mismatch")
require(string_array("FREE_X") == [str(row["param"]) for row in free], "FREE_X mismatch")
require(string_array("FREE_B") == [row["B"] for row in free], "FREE_B mismatch")
require(string_array("FREE_L") == [row["lambda"] for row in free], "FREE_L mismatch")
require(int_array("CP_K") == [int(row["param"]) for row in cos_pi], "CP_K mismatch")
require(string_array("CP_L") == [row["lambda"] for row in cos_pi], "CP_L mismatch")
require(int_array("PV_K") == [int(row["param"]) for row in parseval], "PV_K mismatch")
require(string_array("PV_L") == [row["lambda"] for row in parseval], "PV_L mismatch")
require(scalar("T2_B") == t2[0]["B"], "T2_B mismatch")
require(scalar("T2_L") == t2[0]["lambda"], "T2_L mismatch")
require(scalar("TARGET") == candidate["target"], "TARGET mismatch")

print(f"PASS: all load-bearing fields embedded ({len(candidate['rows'])} rows)")
