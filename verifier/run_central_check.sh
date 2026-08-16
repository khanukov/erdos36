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

if ldconfig -p 2>/dev/null | grep -q 'libmpfr.so.6'; then
  MPFR_LINK='-Wl,-l:libmpfr.so.6'
else
  MPFR_LINK='-lmpfr'
fi
if ldconfig -p 2>/dev/null | grep -q 'libgmp.so.10'; then
  GMP_LINK='-Wl,-l:libgmp.so.10'
else
  GMP_LINK='-lgmp'
fi

BINARY="build/verify_central_mpfr${SUFFIX}"
STEM="build/central_verification${SUFFIX}"
${CC:-gcc} -std=c11 -O3 -Wall -Wextra -Wpedantic -Werror \
  -DPREC="$PRECISION" verifier/verify_central_mpfr.c \
  "$MPFR_LINK" "$GMP_LINK" -lm -o "$BINARY"

set +e
"$BINARY" "${1:-7}" | tee "${STEM}.log"
rc=${PIPESTATUS[0]}
set -e
printf '%s\n' "$rc" > "${STEM}.rc"
if [[ "$rc" -eq 0 ]]; then
  python3 scripts/parse_central_log.py "${STEM}.log" "${STEM}.json"
fi
exit "$rc"
