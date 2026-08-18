#!/usr/bin/env python3
"""Adversarial regression tests for semantic release-evidence validation."""

from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal, localcontext

sys.dont_write_bytecode = True
from release_evidence import (
    CENTRAL_BINS,
    OUTER_BINS,
    OUTER_COMMIT,
    OUTER_HASH_FILES,
    OUTER_MODE,
    STATEMENT,
    TARGET,
    EvidenceError,
    validate_release_evidence,
)
from verify_release import parse_manifest

COMMIT = "a" * 40
TREE = "b" * 40
RUN_ID = "release-mutation-test-run"


def central_fixture(precision: int) -> tuple[dict[str, object], bytes]:
    with localcontext() as context:
        context.prec = 100
        threshold = Decimal(1) / Decimal(TARGET)
        integral = threshold - Decimal("0.0000001")
        margin = threshold - integral
        implied = Decimal(1) / integral
    fields = {
        "precision_bits": str(precision),
        "mpfr_version": "4.2.1",
        "gmp_version": "6.3.0",
        "target_exact": TARGET,
        "target_binary64_diagnostic": "0.38056030000000002",
        "integral_upper_mpfr": str(integral),
        "threshold_lower_mpfr": str(threshold),
        "implied_bound_lower_mpfr": str(implied),
        "D_margin_lower_mpfr": str(margin),
        "integral_upper_binary64_diagnostic": str(float(integral)),
        "threshold_lower_binary64_diagnostic": str(float(threshold)),
        "implied_bound_lower_binary64_diagnostic": str(float(implied)),
        "D_margin_lower_binary64_diagnostic": str(float(margin)),
        "M1_upper": "54.0",
        "M2_upper": "15371.0",
        "nodes": "2000",
        "positive_cells": "500",
        "negative_cells": "600",
        "terminal": "700",
        "local_derivative": "800",
        "components": "1",
        "depth": "7",
    }
    log = ("PASS\n" + "\n".join(f"{key}={value}" for key, value in fields.items()) + "\n").encode()
    result: dict[str, object] = {
        "status": "PASS",
        "run_id": RUN_ID,
        "decimal_fields_are_diagnostic": True,
        "source_commit": COMMIT,
        "source_tree": TREE,
        "source_dirty": False,
    }
    for key, value in fields.items():
        if key == "target_exact":
            result["target"] = value
        elif key == "precision_bits":
            result[key] = int(value)
        else:
            result[key] = value
    return result, log


def fixture() -> dict[str, bytes]:
    central, log = central_fixture(96)
    central128, log128 = central_fixture(128)
    with localcontext() as context:
        context.prec = 100
        threshold = Decimal(1) / Decimal(TARGET)
        max_d = threshold - Decimal("0.0002")
        margin = threshold - max_d
    outer: dict[str, object] = {
        "status": "PASS",
        "target": TARGET,
        "run_id": RUN_ID,
        "verification_mode": OUTER_MODE,
        "checked_sha256_files": OUTER_HASH_FILES,
        "outer_bins": OUTER_BINS,
        "excluded_central_bins": CENTRAL_BINS,
        "outer_max_D": str(max_d),
        "outer_max_bin": 77,
        "threshold": str(threshold),
        "margin": str(margin),
        "pinned_commit": OUTER_COMMIT,
        "source_commit": COMMIT,
        "source_tree": TREE,
        "source_dirty": False,
    }
    composite: dict[str, object] = {
        "status": "PASS",
        "statement": STATEMENT,
        "target": TARGET,
        "run_id": RUN_ID,
        "source_commit": COMMIT,
        "source_tree": TREE,
        "source_dirty": False,
        "central_check": "fresh C/MPFR process PASS with directed-decimal enclosure",
        "central_bins": CENTRAL_BINS,
        "outer_check": "SHA-256-pinned upstream report validation; Arb not rerun",
        "outer_bins": OUTER_BINS,
        "outer_margin": str(margin),
        "lean_verified": False,
        "peer_reviewed": False,
    }

    def encode(value: object) -> bytes:
        return (json.dumps(value, indent=2) + "\n").encode()

    return {
        "evidence/central_verification.json": encode(central),
        "evidence/central_verification.log": log,
        "evidence/central_verification.rc": b"0\n",
        "evidence/central_verification.128.json": encode(central128),
        "evidence/central_verification.128.log": log128,
        "evidence/central_verification.128.rc": b"0\n",
        "evidence/outer_verification.json": encode(outer),
        "evidence/composite_verification.json": encode(composite),
    }


def mutate_json(files: dict[str, bytes], name: str, key: str, value: object) -> None:
    obj = json.loads(files[name])
    obj[key] = value
    files[name] = (json.dumps(obj, indent=2) + "\n").encode()


def mutate_central_pair(
    files: dict[str, bytes], json_key: str, log_key: str, value: str, *, suffix: str = ""
) -> None:
    stem = f"evidence/central_verification{suffix}"
    mutate_json(files, f"{stem}.json", json_key, value)
    lines = files[f"{stem}.log"].decode().splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith(f"{log_key}=")]
    if len(matches) != 1:
        raise AssertionError(f"fixture does not contain exactly one {log_key}")
    lines[matches[0]] = f"{log_key}={value}"
    files[f"{stem}.log"] = ("\n".join(lines) + "\n").encode()


def rejected(name: str, mutation) -> None:  # type: ignore[no-untyped-def]
    files = copy.deepcopy(fixture())
    mutation(files)
    try:
        validate_release_evidence(files, commit=COMMIT, tree=TREE)
    except EvidenceError:
        return
    raise AssertionError(f"forged evidence was accepted: {name}")


def main() -> int:
    validate_release_evidence(fixture(), commit=COMMIT, tree=TREE)
    central = "evidence/central_verification.json"
    central128 = "evidence/central_verification.128.json"
    outer = "evidence/outer_verification.json"
    composite = "evidence/composite_verification.json"
    cases = [
        ("coordinated wrong target", lambda f: mutate_central_pair(f, "target", "target_exact", "0.999")),
        ("wrong statement", lambda f: mutate_json(f, composite, "statement", "c_E > 0.999")),
        ("wrong 96-bit precision", lambda f: mutate_json(f, central, "precision_bits", 128)),
        ("wrong 128-bit precision", lambda f: mutate_json(f, central128, "precision_bits", 96)),
        ("coordinated negative central margin", lambda f: mutate_central_pair(f, "D_margin_lower_mpfr", "D_margin_lower_mpfr", "-1e-7")),
        ("non-finite central margin", lambda f: mutate_json(f, central, "D_margin_lower_mpfr", "NaN")),
        ("coordinated integral above threshold", lambda f: mutate_central_pair(f, "integral_upper_mpfr", "integral_upper_mpfr", "3")),
        ("log/JSON disagreement", lambda f: mutate_json(f, central128, "M1_upper", "999")),
        ("wrong upstream pin", lambda f: mutate_json(f, outer, "pinned_commit", "bogus")),
        ("wrong pinned-file count", lambda f: mutate_json(f, outer, "checked_sha256_files", 18)),
        ("wrong outer-bin count", lambda f: mutate_json(f, outer, "outer_bins", 169)),
        ("wrong central exclusions", lambda f: mutate_json(f, outer, "excluded_central_bins", [86])),
        ("nonpositive outer margin", lambda f: mutate_json(f, outer, "margin", "0")),
        ("composite margin mismatch", lambda f: mutate_json(f, composite, "outer_margin", "1")),
        ("different 128-bit run", lambda f: mutate_json(f, central128, "run_id", "other-run")),
        (
            "different 128-bit MPFR version",
            lambda f: mutate_central_pair(
                f, "mpfr_version", "mpfr_version", "4.2.2", suffix=".128"
            ),
        ),
        ("different outer run", lambda f: mutate_json(f, outer, "run_id", "other-run")),
        ("unbound outer source", lambda f: mutate_json(f, outer, "source_commit", "c" * 40)),
        ("dirty composite source", lambda f: mutate_json(f, composite, "source_dirty", True)),
        ("forged return code", lambda f: f.__setitem__("evidence/central_verification.rc", b"0\n1\n")),
        (
            "duplicate log proof field",
            lambda f: f.__setitem__(
                "evidence/central_verification.log",
                f["evidence/central_verification.log"] + b"target_exact=0.3805603\n",
            ),
        ),
        (
            "duplicate JSON key",
            lambda f: f.__setitem__(
                central,
                f[central].rstrip()[:-1] + b', "status": "PASS"}\n',
            ),
        ),
        ("unexpected evidence field", lambda f: mutate_json(f, composite, "claim", "verified")),
    ]
    for name, mutation in cases:
        rejected(name, mutation)
    digest = "d" * 64
    assert parse_manifest(f"{digest}  path.txt\n".encode(), "test manifest") == {
        "path.txt": digest
    }
    bad_manifests = [
        f"{digest}  path.txt\n{digest}  path.txt\n".encode(),
        f"{'z' * 64}  path.txt\n".encode(),
        f"{digest}  ../path.txt\n".encode(),
        f"{digest} path.txt\n".encode(),
    ]
    for data in bad_manifests:
        try:
            parse_manifest(data, "mutated manifest")
        except SystemExit:
            continue
        raise AssertionError("malformed or duplicate manifest entry was accepted")
    print(
        f"PASS: {len(cases)} forged release-evidence mutations and "
        f"{len(bad_manifests)} manifest mutations rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
