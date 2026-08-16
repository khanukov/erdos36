#!/usr/bin/env python3
"""Fail closed on release metadata, status, and source-tree hygiene."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    ".zenodo.json",
    "README.md",
    "RESULT.md",
    "STATUS.json",
    "CITATION.cff",
    "LICENSE",
    "LICENSE_SCOPE.md",
    "VERSION",
    "certificate/central_certificate.json",
    "verifier/verify_central_mpfr.c",
    "verifier/check_embedding.py",
    "verifier/test_embedding_mutations.py",
    "verifier/run_central_check.sh",
    "upstream/fetch_upstream.py",
    "upstream/verify_outer_bins.py",
    "upstream/SHA256SUMS.txt",
    "scripts/verify_all.sh",
    "scripts/verify_composite.py",
    "scripts/build_release.py",
    "scripts/verify_release.py",
    "paper/main.tex",
    "paper/references.bib",
    "paper/LICENSE",
    "docs/TRUST_BOUNDARY.md",
    "docs/REPRODUCIBILITY.md",
    "docs/FORMALIZATION_STATUS.md",
    "docs/ERDOS_PROBLEMS_SUBMISSION.md",
    "docs/INDEPENDENT_REVIEW.md",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


missing = sorted(path for path in REQUIRED if not (ROOT / path).is_file())
if missing:
    fail("missing required files:\n- " + "\n- ".join(missing))

for forbidden in ("zenodo.template.json", "paper/main.pdf"):
    if (ROOT / forbidden).exists():
        fail(f"generated or placeholder file present: {forbidden}")

version = (ROOT / "VERSION").read_text().strip()
if version != "0.1.0-preprint":
    fail(f"unexpected VERSION: {version}")

title = "A Parseval-Prefix Improvement for Erdős' Minimum-Overlap Problem"
zenodo = json.loads((ROOT / ".zenodo.json").read_text())
zenodo_checks = {
    "title": zenodo.get("title") == title,
    "resource type": zenodo.get("upload_type") == "publication" and zenodo.get("publication_type") == "preprint",
    "date": zenodo.get("publication_date") == "2026-08-16",
    "creator": zenodo.get("creators") == [{"name": "Khanukov, Dmitry"}],
    "license": zenodo.get("license") == "cc-by-4.0",
}
for name, passed in zenodo_checks.items():
    if not passed:
        fail(f".zenodo.json mismatch: {name}")

cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
for expected in (
    "cff-version: 1.2.0",
    f'title: "{title}"',
    f"version: {version}",
    "date-released: 2026-08-16",
    'repository-code: "https://github.com/khanukov/erdos36"',
    "license: MIT",
    "family-names: Khanukov",
    "given-names: Dmitry",
):
    if expected not in cff:
        fail(f"CITATION.cff missing expected metadata: {expected}")

paper = (
    (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
    + "\n"
    + (ROOT / "paper" / "author-config.tex").read_text(encoding="utf-8")
)
for expected in (
    r"\author{Dmitry Khanukov}",
    r"\date{August 16, 2026}",
    r"\textbf{Status: Preliminary and unrefereed.}",
    "not Lean-verified",
    r"\url{https://github.com/khanukov/erdos36}",
):
    if expected not in paper:
        fail(f"paper metadata/disclosure missing: {expected}")

status = json.loads((ROOT / "STATUS.json").read_text())
checks = {
    "version": status.get("version") == version,
    "statement": status.get("statement") == "c_E > 0.3805603",
    "preliminary status": status.get("status") == "PRELIMINARY_COMPOSITE_CERTIFICATE_PASS_UNREFEREED",
    "Lean status": status.get("lean_verified") is False and status.get("lean_checked_claims") == [],
    "review status": status.get("peer_reviewed") is False,
    "problem status": status.get("solves_erdos_problem_36") is False,
    "upstream pin": status.get("outer", {}).get("source_commit") == "6bc610e40083ef61a40966dfb5d38612cabc4c5b",
}
for name, passed in checks.items():
    if not passed:
        fail(f"STATUS.json mismatch: {name}")

critical = ["README.md", "RESULT.md", "CITATION.cff", ".zenodo.json", "paper/main.tex"]
text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in critical)
for token in ("OWNER/REPOSITORY", "NOASSERTION", "TO-BE-ADDED", "email@example.com"):
    if token in text:
        fail(f"placeholder remains in release metadata: {token}")
if "https://github.com/khanukov/erdos36" not in text:
    fail("canonical repository URL missing")
if not re.search(r"[Pp]reliminary", text) or not re.search(r"[Uu]nrefereed", text):
    fail("preliminary/unrefereed disclosure missing")

lean_files = list(ROOT.rglob("*.lean"))
if lean_files and status.get("lean_checked_claims") == []:
    fail("Lean files exist but STATUS.json still reports zero checked claims")

junk_names = {".pytest_cache", "__pycache__"}
for path in ROOT.rglob("*"):
    if path.name in junk_names:
        fail(f"junk path present: {path.relative_to(ROOT)}")

print(f"PASS: repository audit ({len(REQUIRED)} required files; status={status['status']})")
