#!/usr/bin/env python3
"""Negative tests for central-log evidence parsing."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "scripts" / "parse_central_log.py"
GOOD = """PASS
precision_bits=96
mpfr_version=4.2.1
gmp_version=6.2.1
target_exact=0.3805603
target_binary64_diagnostic=0.38056030000000002
integral_upper_mpfr=2.62770434388489007452190373282
threshold_lower_mpfr=2.62770446628300429655957281927
implied_bound_lower_mpfr=0.380560317726447488726080215466
D_margin_lower_mpfr=1.22398114222037669086465328947e-7
integral_upper_binary64_diagnostic=2.6277043438848904
threshold_lower_binary64_diagnostic=2.6277044662830042
implied_bound_lower_binary64_diagnostic=0.38056031772644749
D_margin_lower_binary64_diagnostic=1.2239811422203767e-7
M1_upper=54
M2_upper=15371
nodes=91420 positive_cells=13628 negative_cells=47573 terminal=4674 local_derivative=25545 components=8 depth=7
"""


def parse(text: str, *, precision: str = "96") -> tuple[int, dict[str, object] | None]:
    with tempfile.TemporaryDirectory() as directory:
        input_path = Path(directory) / "input.log"
        output_path = Path(directory) / "output.json"
        input_path.write_text(text, encoding="utf-8")
        env = os.environ.copy()
        env.update(
            {
                "VERIFICATION_RUN_ID": "test-run-id",
                "CENTRAL_PRECISION_BITS": precision,
                "PYTHONDONTWRITEBYTECODE": "1",
            }
        )
        result = subprocess.run(
            [sys.executable, str(PARSER), str(input_path), str(output_path)],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        payload = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else None
        return result.returncode, payload


returncode, payload = parse(GOOD)
if returncode != 0 or payload is None or payload.get("precision_bits") != 96:
    raise SystemExit("FAIL: valid central log was rejected or logged precision was not preserved")

mutations = {
    "environment/log precision mismatch": (GOOD, "128"),
    "wrong exact target": (GOOD.replace("target_exact=0.3805603", "target_exact=0.3805604"), "96"),
    "non-finite margin": (GOOD.replace("D_margin_lower_mpfr=1.22398114222037669086465328947e-7", "D_margin_lower_mpfr=NaN"), "96"),
    "negative margin": (GOOD.replace("D_margin_lower_mpfr=1.22398114222037669086465328947e-7", "D_margin_lower_mpfr=-1e-7"), "96"),
    "non-strict integral bound": (GOOD.replace("integral_upper_mpfr=2.62770434388489007452190373282", "integral_upper_mpfr=3"), "96"),
    "threshold/target mismatch": (GOOD.replace("threshold_lower_mpfr=2.62770446628300429655957281927", "threshold_lower_mpfr=2.63"), "96"),
    "bound/integral mismatch": (GOOD.replace("implied_bound_lower_mpfr=0.380560317726447488726080215466", "implied_bound_lower_mpfr=0.381"), "96"),
    "margin/difference mismatch": (GOOD.replace("D_margin_lower_mpfr=1.22398114222037669086465328947e-7", "D_margin_lower_mpfr=1e-6"), "96"),
    "duplicate proof field": (GOOD + "target_exact=0.3805603\n", "96"),
    "malformed token": (GOOD.replace("M1_upper=54", "M1_upper=54 malformed"), "96"),
    "unexpected field": (GOOD + "claim=PASS\n", "96"),
}
for name, (text, precision) in mutations.items():
    if parse(text, precision=precision)[0] == 0:
        raise SystemExit(f"FAIL: central-log mutation accepted: {name}")

print(f"PASS: valid central log parsed and {len(mutations)} evidence mutations rejected")
