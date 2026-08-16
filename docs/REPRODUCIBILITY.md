# Reproducibility

## What can be reproduced

The supported command reproduces the repository audit, the new two-bin
directed-rounding C/MPFR check, validation of the SHA-256-pinned upstream
reports for the other 170 bins, and a fresh composite decision at the target
`0.3805603`.

It does not rerun Price's Arb computation, reproduce the optimizer that found
the central multipliers, provide an independent checker implementation, or
check a Lean proof. Those distinctions are part of the result, not optional
caveats.

## System requirements

The checked workflow targets Ubuntu or Debian with:

- Python 3.12 or a compatible Python 3 installation;
- a C11 compiler;
- GMP and MPFR development libraries;
- Git and CA certificates for the pinned upstream download;
- `latexmk` and the standard LaTeX packages used by `paper/main.tex` when the
  manuscript is built.

On Ubuntu 24.04, install the dependencies with:

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  build-essential libgmp-dev libmpfr-dev python3 git ca-certificates \
  latexmk texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

The Ubuntu package archive is mutable. Record the installed package versions
when producing a review report.

## Reproduce the composite decision

Use a clean checkout. After the intended first release tag exists, the release
checkout is:

```bash
git clone https://github.com/khanukov/erdos36.git
cd erdos36
git checkout --detach v0.1.0-preprint
git rev-parse HEAD
make verify
```

Before that tag exists, review the exact commit supplied with the candidate
archive and record `git rev-parse HEAD` in the report. Do not treat a moving
branch name as a reproducible identifier.

`make verify` runs one dependency-gated chain:

1. repository structure and disclosure checks;
2. closed source-tree checksum verification;
3. certificate-to-C embedding checks and mutation tests;
4. a fresh 96-bit central MPFR run;
5. download and SHA-256 verification of 19 files from the pinned upstream
   commit;
6. structural and numerical validation of the 170 noncentral report rows;
7. composition of results carrying the same fresh run identifier.

The final line must be:

```text
PASS: fresh composite verification of c_E > 0.3805603
```

Generated evidence is written under `build/`, including:

- `central_verification.json`, `.log`, and `.rc`;
- `outer_verification.json`;
- `composite_verification.json`.

The central, outer, and composite JSON files must all report `PASS`, and their
`run_id` values must agree. The outer JSON must report
`pinned-report-validation-no-arb-rerun`.

## Precision cross-check

Run the central checker separately at 128-bit MPFR precision:

```bash
make verify-central-128
```

This writes `build/central_verification.128.json`, `.log`, and `.rc`. Agreement
with the 96-bit result is a useful implementation cross-check; it is not an
independent algorithm or a Lean proof.

## Offline use of the pinned inputs

The fetcher accepts a pre-populated `upstream/cache/` directory. All 19 files
must match `upstream/SHA256SUMS.txt`; otherwise verification stops. Once the
matching files are present, the composite run does not need to trust the
network transport. The cache is intentionally ignored by Git and excluded
from release archives because the upstream material is not relicensed here.

## Build the manuscript and release candidate

From a clean committed source tree, run the release steps in this order:

```bash
make verify
make verify-central-128
make paper
python3 scripts/build_release.py
python3 scripts/verify_release.py
```

The manuscript is written to
`build/erdos36-preprint-0.1.0-preprint.pdf`. The release builder refuses a dirty
Git tree, reads the exact commit and tree identifiers, packages tracked source
files and the required generated evidence, and emits a companion SHA-256 file.
The builder also rejects verification evidence unless the 96-bit composite run
and 128-bit cross-check both record that exact clean commit and tree.
Verify the ZIP with the companion checksum from inside the `build/` directory
and test it with `unzip -t` before any upload.

The archive uses sorted paths, fixed permissions, and the commit timestamp.
The current evidence includes a per-run UUID, and PDF bytes can depend on the
TeX toolchain. Therefore the current project does not claim that two complete
rebuilds are byte-for-byte identical. The published ZIP's companion checksum,
`COMMIT_SHA.txt`, `PROVENANCE.json`, and `ARTIFACT_SHA256SUMS.txt` identify the
exact deposited artifact and its source.

Create the arXiv source only after the release archive has been built, because
the arXiv ZIP is a separate generated file:

```bash
make arxiv
temp_dir="$(mktemp -d)"
unzip build/erdos36-arxiv-source.zip -d "$temp_dir"
cd "$temp_dir"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Inspect the resulting PDF before submission. Preparing these artifacts does
not authorize uploading or publishing them.

## Container convenience path

The included Dockerfile can run the default verification command:

```bash
docker build -t erdos36-local .
docker run --rm erdos36-local
```

`ubuntu:24.04` and the packages installed by `apt` are not digest- or
snapshot-pinned. The container is a convenience environment, not a claim of
bit-for-bit archival reproducibility.

## Minimum review record

A useful reproduction report records:

- the exact Git commit and, if used, release tag;
- the release ZIP SHA-256 digest;
- operating system and architecture;
- Python, compiler, GMP, and MPFR versions;
- every command run and its exit status;
- the three matching composite `run_id` values;
- the central margins at both precisions and the outer reported margin;
- whether the upstream Arb computation was rerun or only its reports checked;
- whether the reviewer inspected this checker or used an independent one.

Do not summarize a report-only validation as a full independent reproduction.
