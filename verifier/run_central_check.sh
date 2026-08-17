#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p build

PRECISION="${MPFR_PREC:-96}"
case "$PRECISION" in
  96) SUFFIX="" ;;
  128) SUFFIX=".128" ;;
  *) echo "MPFR_PREC must be 96 or 128" >&2; exit 2 ;;
esac

if [[ -z "${VERIFICATION_RUN_ID:-}" ]]; then
  VERIFICATION_RUN_ID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
  export VERIFICATION_RUN_ID
fi
export CENTRAL_PRECISION_BITS="$PRECISION"

python3 verifier/check_embedding.py certificate/central_certificate.json verifier/verify_central_mpfr.c
python3 verifier/test_embedding_mutations.py

MPFR_CFLAGS=()
MPFR_LIBS=(-lmpfr -lgmp)
if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists mpfr gmp; then
  read -r -a MPFR_CFLAGS <<< "$(pkg-config --cflags mpfr gmp)"
  read -r -a MPFR_LIBS <<< "$(pkg-config --libs mpfr gmp)"
fi

BINARY="build/verify_central_mpfr${SUFFIX}"
STEM="build/central_verification${SUFFIX}"
${CC:-gcc} -std=c11 -O3 -Wall -Wextra -Wpedantic -Werror \
  "${MPFR_CFLAGS[@]}" -DPREC="$PRECISION" verifier/verify_central_mpfr.c \
  "${MPFR_LIBS[@]}" -lm -o "$BINARY"

set +e
"$BINARY" "${1:-7}" | tee "${STEM}.log"
rc=${PIPESTATUS[0]}
set -e
printf '%s\n' "$rc" > "${STEM}.rc"
if [[ "$rc" -eq 0 ]]; then
  python3 scripts/parse_central_log.py "${STEM}.log" "${STEM}.json"
fi
exit "$rc"
