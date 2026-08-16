#!/usr/bin/env python3
"""Create a deterministic minimal arXiv source archive under build/."""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "erdos36-arxiv-source.zip"
FILES = ["paper/main.tex", "paper/author-config.tex", "paper/references.tex"]
README = (
    "main.tex is the top-level file. Compile with PDFLaTeX.\n"
    "Status: preliminary and unrefereed; no claim is Lean-verified.\n"
).encode()
DATE = (2026, 8, 16, 0, 0, 0)


def info(name: str) -> zipfile.ZipInfo:
    value = zipfile.ZipInfo(name, date_time=DATE)
    value.compress_type = zipfile.ZIP_DEFLATED
    value.create_system = 3
    value.external_attr = 0o100644 << 16
    return value


OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    archive.writestr(info("00README"), README)
    for relative in FILES:
        path = ROOT / relative
        archive.writestr(info(path.name), path.read_bytes())
print(f"created {OUT.relative_to(ROOT)}")
