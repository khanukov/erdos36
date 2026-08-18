#!/usr/bin/env python3
"""Strict semantic validation for generated preprint release evidence.

The release builder and archive verifier both use this module.  Keeping the
checks in one place prevents a release from accepting a collection of JSON
files which merely say ``PASS`` but do not encode the claimed computation.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation, localcontext
from typing import Mapping

TARGET = "0.3805603"
STATEMENT = "c_E > 0.3805603"
OUTER_MODE = "pinned-report-validation-no-arb-rerun"
OUTER_COMMIT = "6bc610e40083ef61a40966dfb5d38612cabc4c5b"
OUTER_HASH_FILES = 19
OUTER_BINS = 170
CENTRAL_BINS = [85, 86]

_CENTRAL_LOG_KEYS = {
    "precision_bits",
    "mpfr_version",
    "gmp_version",
    "target_exact",
    "target_binary64_diagnostic",
    "integral_upper_mpfr",
    "threshold_lower_mpfr",
    "implied_bound_lower_mpfr",
    "D_margin_lower_mpfr",
    "integral_upper_binary64_diagnostic",
    "threshold_lower_binary64_diagnostic",
    "implied_bound_lower_binary64_diagnostic",
    "D_margin_lower_binary64_diagnostic",
    "M1_upper",
    "M2_upper",
    "nodes",
    "positive_cells",
    "negative_cells",
    "terminal",
    "local_derivative",
    "components",
    "depth",
}
_CENTRAL_JSON_KEYS = (
    _CENTRAL_LOG_KEYS - {"target_exact"}
) | {
    "status",
    "run_id",
    "decimal_fields_are_diagnostic",
    "source_commit",
    "source_tree",
    "source_dirty",
    "target",
}
_OUTER_JSON_KEYS = {
    "status",
    "target",
    "run_id",
    "verification_mode",
    "checked_sha256_files",
    "outer_bins",
    "excluded_central_bins",
    "outer_max_D",
    "outer_max_bin",
    "threshold",
    "margin",
    "pinned_commit",
    "source_commit",
    "source_tree",
    "source_dirty",
}
_COMPOSITE_JSON_KEYS = {
    "status",
    "statement",
    "target",
    "run_id",
    "source_commit",
    "source_tree",
    "source_dirty",
    "central_check",
    "central_bins",
    "outer_check",
    "outer_bins",
    "outer_margin",
    "lean_verified",
    "peer_reviewed",
}
_DECIMAL_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
_KEY_RE = re.compile(r"^[A-Za-z0-9_]+$")
_LIBRARY_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}(?:[-+][A-Za-z0-9.-]+)?$")


class EvidenceError(ValueError):
    """Raised when generated release evidence is malformed or inconsistent."""


def _reject_constant(value: str) -> None:
    raise EvidenceError(f"non-standard JSON number: {value}")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_bytes(data: bytes, label: str) -> dict[str, object]:
    """Decode one strict, duplicate-free JSON object."""

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"{label}: JSON is not UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, EvidenceError) as exc:
        raise EvidenceError(f"{label}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"{label}: top-level JSON value is not an object")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def _exact_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    _require(not missing and not extra, f"{label}: schema mismatch; missing={missing}, extra={extra}")


def _integer(value: object, label: str) -> int:
    _require(type(value) is int, f"{label}: expected an integer")
    return int(value)


def _decimal(value: object, label: str) -> Decimal:
    _require(isinstance(value, str), f"{label}: decimal must be encoded as a string")
    _require(_DECIMAL_RE.fullmatch(value) is not None, f"{label}: malformed decimal")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise EvidenceError(f"{label}: malformed decimal") from exc
    _require(result.is_finite(), f"{label}: decimal is not finite")
    return result


def _source_binding(
    evidence: Mapping[str, object], label: str, commit: str, tree: str
) -> None:
    _require(evidence.get("source_commit") == commit, f"{label}: source commit mismatch")
    _require(evidence.get("source_tree") == tree, f"{label}: source tree mismatch")
    _require(evidence.get("source_dirty") is False, f"{label}: source is not clean")


def parse_central_log(data: bytes, label: str) -> dict[str, str]:
    """Parse the exact C-verifier transcript without ignoring malformed text."""

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"{label}: log is not UTF-8") from exc
    _require(text.endswith("\n"), f"{label}: log has no final newline")
    lines = text.splitlines()
    _require(lines and lines[0] == "PASS", f"{label}: log does not begin with an exact PASS line")
    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:], start=2):
        _require(bool(line), f"{label}: empty log line {line_number}")
        for token in line.split(" "):
            _require(bool(token) and token.count("=") == 1, f"{label}: malformed token on line {line_number}")
            key, value = token.split("=", 1)
            _require(_KEY_RE.fullmatch(key) is not None and bool(value), f"{label}: malformed field on line {line_number}")
            _require(key not in fields, f"{label}: duplicate log field {key}")
            fields[key] = value
    _require(set(fields) == _CENTRAL_LOG_KEYS, f"{label}: unexpected central log field set")
    return fields


def validate_central_log_fields(
    fields: Mapping[str, str], *, precision: int, label: str
) -> dict[str, Decimal]:
    """Check all load-bearing arithmetic relations in a central transcript."""

    _require(set(fields) == _CENTRAL_LOG_KEYS, f"{label}: unexpected central log field set")
    _require(fields["precision_bits"] == str(precision), f"{label}: log precision mismatch")
    _require(precision in (96, 128), f"{label}: unsupported release precision")
    _require(fields["target_exact"] == TARGET, f"{label}: exact target mismatch")

    numeric_fields = {
        key
        for key in _CENTRAL_LOG_KEYS
        if key
        not in {
            "precision_bits",
            "mpfr_version",
            "gmp_version",
            "target_exact",
            "nodes",
            "positive_cells",
            "negative_cells",
            "terminal",
            "local_derivative",
            "components",
            "depth",
        }
    }
    numbers = {key: _decimal(fields[key], f"{label}.{key}") for key in numeric_fields}
    for key in (
        "nodes",
        "positive_cells",
        "negative_cells",
        "terminal",
        "local_derivative",
        "components",
        "depth",
    ):
        _require(fields[key].isdigit(), f"{label}.{key}: expected a nonnegative decimal integer")
    _require(
        int(fields["nodes"]) > 0 and int(fields["components"]) > 0,
        f"{label}: empty subdivision result",
    )
    _require(int(fields["depth"]) == 7, f"{label}: release verification must use depth 7")
    for key in ("mpfr_version", "gmp_version"):
        _require(
            _LIBRARY_VERSION_RE.fullmatch(fields[key]) is not None,
            f"{label}.{key}: malformed runtime library version",
        )
    _require(
        numbers["M1_upper"] > 0 and numbers["M2_upper"] > 0,
        f"{label}: invalid derivative bounds",
    )

    integral = numbers["integral_upper_mpfr"]
    threshold = numbers["threshold_lower_mpfr"]
    implied = numbers["implied_bound_lower_mpfr"]
    margin = numbers["D_margin_lower_mpfr"]
    target = Decimal(TARGET)
    _require(integral > 0 and threshold > 0 and implied > 0, f"{label}: nonpositive proof quantity")
    _require(integral < threshold, f"{label}: integral is not below the threshold")
    _require(margin > 0, f"{label}: central margin is not positive")
    _require(implied > target, f"{label}: implied bound does not exceed the target")
    tolerance = Decimal("1e-25") if precision == 96 else Decimal("1e-35")
    with localcontext() as context:
        context.prec = 160
        _require(
            abs(threshold * target - 1) <= tolerance,
            f"{label}: threshold is inconsistent with target",
        )
        _require(
            abs(implied * integral - 1) <= tolerance,
            f"{label}: implied bound is inconsistent with integral",
        )
        _require(
            abs(margin - (threshold - integral)) <= tolerance,
            f"{label}: central margin is inconsistent",
        )
    return numbers


def _validate_central(
    evidence: Mapping[str, object],
    log: bytes,
    rc: bytes,
    *,
    precision: int,
    commit: str,
    tree: str,
    label: str,
) -> str:
    _exact_keys(evidence, _CENTRAL_JSON_KEYS, label)
    _require(rc == b"0\n", f"{label}: return-code file is not exactly zero")
    fields = parse_central_log(log, f"{label} log")
    _require(evidence.get("status") == "PASS", f"{label}: status is not PASS")
    run_id = evidence.get("run_id")
    _require(isinstance(run_id, str) and bool(run_id.strip()), f"{label}: empty or non-string run ID")
    _require(evidence.get("decimal_fields_are_diagnostic") is True, f"{label}: decimal disclosure missing")
    _source_binding(evidence, label, commit, tree)
    _require(_integer(evidence.get("precision_bits"), f"{label}.precision_bits") == precision, f"{label}: wrong precision")
    _require(evidence.get("target") == TARGET and fields["target_exact"] == TARGET, f"{label}: exact target mismatch")

    # Every value produced by the C process must survive log-to-JSON parsing
    # byte-for-byte (apart from the documented target rename and integer precision).
    for key, value in fields.items():
        if key in {"target_exact", "precision_bits"}:
            continue
        _require(evidence.get(key) == value, f"{label}: log/JSON mismatch for {key}")

    validate_central_log_fields(fields, precision=precision, label=label)
    return run_id


def _validate_outer(
    evidence: Mapping[str, object], *, commit: str, tree: str
) -> str:
    label = "outer evidence"
    _exact_keys(evidence, _OUTER_JSON_KEYS, label)
    _require(evidence.get("status") == "PASS", f"{label}: status is not PASS")
    _require(evidence.get("target") == TARGET, f"{label}: exact target mismatch")
    run_id = evidence.get("run_id")
    _require(isinstance(run_id, str) and bool(run_id.strip()), f"{label}: empty or non-string run ID")
    _source_binding(evidence, label, commit, tree)
    _require(evidence.get("verification_mode") == OUTER_MODE, f"{label}: verification mode mismatch")
    _require(evidence.get("pinned_commit") == OUTER_COMMIT, f"{label}: pinned commit mismatch")
    _require(_integer(evidence.get("checked_sha256_files"), f"{label}.checked_sha256_files") == OUTER_HASH_FILES, f"{label}: wrong pinned-file count")
    _require(_integer(evidence.get("outer_bins"), f"{label}.outer_bins") == OUTER_BINS, f"{label}: wrong outer-bin count")
    _require(evidence.get("excluded_central_bins") == CENTRAL_BINS, f"{label}: wrong central-bin exclusions")
    max_bin = _integer(evidence.get("outer_max_bin"), f"{label}.outer_max_bin")
    _require(0 <= max_bin <= 171 and max_bin not in CENTRAL_BINS, f"{label}: invalid maximizing bin")
    max_d = _decimal(evidence.get("outer_max_D"), f"{label}.outer_max_D")
    threshold = _decimal(evidence.get("threshold"), f"{label}.threshold")
    margin = _decimal(evidence.get("margin"), f"{label}.margin")
    _require(max_d > 0 and max_d < threshold, f"{label}: maximum does not satisfy threshold")
    _require(margin > 0, f"{label}: margin is not positive")
    with localcontext() as context:
        context.prec = 160
        _require(abs(threshold * Decimal(TARGET) - 1) <= Decimal("1e-90"), f"{label}: threshold is inconsistent with target")
        _require(margin == threshold - max_d, f"{label}: outer margin is inconsistent")
    return run_id


def _validate_composite(
    evidence: Mapping[str, object], *, commit: str, tree: str, outer_margin: object
) -> str:
    label = "composite evidence"
    _exact_keys(evidence, _COMPOSITE_JSON_KEYS, label)
    _require(evidence.get("status") == "PASS", f"{label}: status is not PASS")
    _require(evidence.get("statement") == STATEMENT, f"{label}: exact statement mismatch")
    _require(evidence.get("target") == TARGET, f"{label}: exact target mismatch")
    run_id = evidence.get("run_id")
    _require(isinstance(run_id, str) and bool(run_id.strip()), f"{label}: empty or non-string run ID")
    _source_binding(evidence, label, commit, tree)
    _require(evidence.get("central_check") == "fresh C/MPFR process PASS with directed-decimal enclosure", f"{label}: central scope mismatch")
    _require(evidence.get("central_bins") == CENTRAL_BINS, f"{label}: central bins mismatch")
    _require(evidence.get("outer_check") == "SHA-256-pinned upstream report validation; Arb not rerun", f"{label}: outer scope mismatch")
    _require(_integer(evidence.get("outer_bins"), f"{label}.outer_bins") == OUTER_BINS, f"{label}: wrong outer-bin count")
    _require(evidence.get("outer_margin") == outer_margin, f"{label}: outer margin does not match outer evidence")
    _require(_decimal(evidence.get("outer_margin"), f"{label}.outer_margin") > 0, f"{label}: nonpositive outer margin")
    _require(evidence.get("lean_verified") is False, f"{label}: unexpected Lean claim")
    _require(evidence.get("peer_reviewed") is False, f"{label}: unexpected review claim")
    return run_id


def validate_release_evidence(
    files: Mapping[str, bytes], *, commit: str, tree: str
) -> dict[str, dict[str, object]]:
    """Validate the four evidence objects and both central process transcripts."""

    required = {
        "evidence/central_verification.json",
        "evidence/central_verification.log",
        "evidence/central_verification.rc",
        "evidence/central_verification.128.json",
        "evidence/central_verification.128.log",
        "evidence/central_verification.128.rc",
        "evidence/outer_verification.json",
        "evidence/composite_verification.json",
    }
    missing = sorted(required - set(files))
    _require(not missing, f"missing generated release evidence: {missing}")
    central = load_json_bytes(files["evidence/central_verification.json"], "central evidence")
    central128 = load_json_bytes(files["evidence/central_verification.128.json"], "central-128 evidence")
    outer = load_json_bytes(files["evidence/outer_verification.json"], "outer evidence")
    composite = load_json_bytes(files["evidence/composite_verification.json"], "composite evidence")
    run_ids = {
        _validate_central(
            central,
            files["evidence/central_verification.log"],
            files["evidence/central_verification.rc"],
            precision=96,
            commit=commit,
            tree=tree,
            label="central evidence",
        ),
        _validate_central(
            central128,
            files["evidence/central_verification.128.log"],
            files["evidence/central_verification.128.rc"],
            precision=128,
            commit=commit,
            tree=tree,
            label="central-128 evidence",
        ),
        _validate_outer(outer, commit=commit, tree=tree),
        _validate_composite(
            composite,
            commit=commit,
            tree=tree,
            outer_margin=outer.get("margin"),
        ),
    }
    _require(len(run_ids) == 1, "release evidence does not share one verification run ID")
    _require(
        central.get("mpfr_version") == central128.get("mpfr_version")
        and central.get("gmp_version") == central128.get("gmp_version"),
        "96-bit and 128-bit evidence used different MPFR/GMP versions",
    )
    return {
        "central": central,
        "central128": central128,
        "outer": outer,
        "composite": composite,
    }
