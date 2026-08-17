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
    "upstream/pinned_manifest.py",
    "upstream/test_pinned_inputs.py",
    "upstream/SHA256SUMS.txt",
    "scripts/verify_all.sh",
    "scripts/verify_composite.py",
    "scripts/build_arxiv.py",
    "scripts/build_release.py",
    "scripts/verify_release.py",
    "scripts/release_evidence.py",
    "scripts/test_release_mutations.py",
    "scripts/test_parse_central_log.py",
    "paper/main.tex",
    "paper/references.bib",
    "paper/LICENSE",
    "docs/TRUST_BOUNDARY.md",
    "docs/REPRODUCIBILITY.md",
    "docs/FORMALIZATION_STATUS.md",
    "docs/ERDOS_PROBLEMS_SUBMISSION.md",
    "docs/INDEPENDENT_REVIEW.md",
    ".github/workflows/publish-preprint.yml",
    "release/RELEASE_NOTES.template.md",
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
if version != "0.1.1-preprint":
    fail(f"unexpected VERSION: {version}")

title = "A Parseval-Prefix Improvement for Erdős' Minimum-Overlap Problem"
zenodo = json.loads((ROOT / ".zenodo.json").read_text())
zenodo_checks = {
    "title": zenodo.get("title") == title,
    "version": zenodo.get("version") == version,
    "resource type": zenodo.get("upload_type") == "publication" and zenodo.get("publication_type") == "preprint",
    "date": zenodo.get("publication_date") == "2026-08-17",
    "creator": zenodo.get("creators") == [{"name": "Khanukov, Dmitry"}],
    "mixed-scope license": zenodo.get("license") == "other-open",
}
for name, passed in zenodo_checks.items():
    if not passed:
        fail(f".zenodo.json mismatch: {name}")
zenodo_notes = zenodo.get("notes", "")
for expected in ("tagged source snapshot", "GitHub Release assets", "LICENSE_SCOPE.md"):
    if expected not in zenodo_notes:
        fail(f".zenodo.json notes missing trust-boundary text: {expected}")

cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
for expected in (
    "cff-version: 1.2.0",
    f'title: "{title}"',
    f"version: {version}",
    "date-released: 2026-08-17",
    'repository-code: "https://github.com/khanukov/erdos36"',
    "license: MIT",
    "family-names: Khanukov",
    "given-names: Dmitry",
):
    if expected not in cff:
        fail(f"CITATION.cff missing expected metadata: {expected}")
if "no DOI has been assigned" in cff:
    fail("CITATION.cff would become false when Zenodo assigns the release DOI")

paper = (
    (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
    + "\n"
    + (ROOT / "paper" / "author-config.tex").read_text(encoding="utf-8")
)
for expected in (
    r"\author{Dmitry Khanukov}",
    r"\date{August 17, 2026}",
    "Status: Preliminary and unrefereed.",
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

paper_license = (ROOT / "paper" / "LICENSE").read_text(encoding="utf-8")
for expected in (title, "https://github.com/khanukov/erdos36"):
    if expected not in paper_license:
        fail(f"paper license missing correct attribution metadata: {expected}")
if "erdos302" in paper_license.lower():
    fail("paper license still refers to Erdős Problem 302")

publish_workflow = (ROOT / ".github" / "workflows" / "publish-preprint.yml").read_text(
    encoding="utf-8"
)
for expected in (
    "workflow_run:",
    "workflows: [verify-priority-package]",
    "head_repository.full_name == github.repository",
    'python3 scripts/verify_release.py "${assets_dir}/${archive}"',
    '.ci_run_url == $run_url',
    "refusing to publish a stale main verification run",
    "--prerelease",
    'readonly tag="v${version}"',
    'readonly artifact="erdos36-priority-package-${VERIFIED_SHA}"',
    '${tag} — hardened preliminary Parseval-prefix bound for Erdős Problem 36',
):
    if expected not in publish_workflow:
        fail(f"publish workflow missing fail-closed release rule: {expected}")

release_notes = (ROOT / "release" / "RELEASE_NOTES.template.md").read_text(
    encoding="utf-8"
)
for token in (
    "@VERIFIED_SHA@",
    "@SOURCE_TREE@",
    "@SOURCE_RUN_ID@",
    "@ARCHIVE_SHA256@",
    "@PDF_SHA256@",
):
    if token not in release_notes:
        fail(f"release-note template missing provenance token: {token}")

lean_files = list(ROOT.rglob("*.lean"))
if lean_files and status.get("lean_checked_claims") == []:
    fail("Lean files exist but STATUS.json still reports zero checked claims")

junk_names = {".pytest_cache", "__pycache__"}
for path in ROOT.rglob("*"):
    if path.name in junk_names:
        fail(f"junk path present: {path.relative_to(ROOT)}")

print(f"PASS: repository audit ({len(REQUIRED)} required files; status={status['status']})")
