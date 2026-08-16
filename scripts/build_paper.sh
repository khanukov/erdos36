#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/build/paper"
mkdir -p "$OUT"
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$ROOT" show -s --format=%ct HEAD)}"
fi
export FORCE_SOURCE_DATE=1
export TZ=UTC
cd "$ROOT/paper"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$OUT" main.tex
cp "$OUT/main.pdf" "$ROOT/build/erdos36-preprint-0.1.0-preprint.pdf"
echo "created build/erdos36-preprint-0.1.0-preprint.pdf"
