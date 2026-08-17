#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "FAIL: source-bound verification requires a Git checkout" >&2
  exit 1
fi
export VERIFICATION_RUN_ID="${VERIFICATION_RUN_ID:-$(python3 -c 'import uuid; print(uuid.uuid4())')}"
export PYTHONDONTWRITEBYTECODE=1

echo "verification_run_id=$VERIFICATION_RUN_ID"
bash verifier/run_central_check.sh
python3 upstream/fetch_upstream.py
python3 upstream/verify_outer_bins.py
python3 scripts/verify_composite.py --require-fresh
