# A Parseval-Prefix Improvement for Erdős' Minimum-Overlap Problem

> **Preliminary and unrefereed — v0.1.1-preprint (2026-08-17).**
> This repository records a priority claim for the computer-assisted bound
> \(c_E>0.3805603\). It is not a solution of Erdős Problem 36, has not been
> independently reproduced, and is not Lean-verified.

[![Zenodo concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21969298.svg)](https://doi.org/10.5281/zenodo.21969298)

This repository contains the manuscript, certificate, and verifier for a
proposed improvement of the lower bound in the minimum-overlap problem.  The
Parseval energy constraint was already used by White; the new contribution
claimed here is its finite profile-space prefix projection, its use in the two
binding central mean bins of Price's compact certificate, and the corresponding
directed-rounding verification.  The numerical improvement over the strongest
public computer-certified claim used as the comparison point is

\[
0.3805603-0.380554702762594012\ldots
=5.597237405987\ldots\times 10^{-6}.
\]

## Verification status

The evidence has two deliberately separated parts:

| Component | What this repository checks | Status |
|---|---|---|
| Central bins 85–86 | JSON/C embedding, analytic row preconditions, and the positive-part integral with directed-rounding MPFR | Fresh run required by `make verify` and CI; local 96/128-bit PASS |
| Other 170 bins | SHA-256 integrity and the reported Arb upper bounds from Price's pinned commit | Report verification only; Arb is not rerun here |
| Composite bound | Both preceding results are from the same fresh verification command and are below \(1/0.3805603\) | Candidate, unrefereed |
| Lean | No theorem in this repository is checked by Lean | 0 claims formalized |

The exact upstream revision is
[`Leeham06972452/erdos-36-lower-bound@6bc610e`](https://github.com/Leeham06972452/erdos-36-lower-bound/commit/6bc610e40083ef61a40966dfb5d38612cabc4c5b).
The outer-bin step accepts the upstream reports as inputs; it is not an
independent reproduction of their Arb computation.  See
[`docs/TRUST_BOUNDARY.md`](docs/TRUST_BOUNDARY.md).

Price's candidate is a public, independently rerun computer-certified claim;
neither it nor this proposed improvement is described here as an officially
recorded or accepted lower-bound record for Erdős Problem 36.

## Reproduce the checked claim

On Ubuntu/Debian, install Python 3, a C compiler, GMP, and MPFR, then run:

```bash
sudo apt-get update
sudo apt-get install -y build-essential libgmp-dev libmpfr-dev python3
make verify
```

`make verify` performs one dependency-gated chain: repository audit, checksum
closure, a fresh central MPFR run, download and hash verification of the
pinned upstream reports, outer-report validation, and composite validation.
The last line is:

```text
PASS: fresh composite verification of c_E > 0.3805603
```

For a second central run at 128-bit MPFR precision:

```bash
make verify-central-128
```

Downloaded upstream inputs and generated results live under ignored
`upstream/cache/` and `build/` directories.

## Repository map

- `paper/` — manuscript source and manuscript license;
- `certificate/central_certificate.json` — new central certificate;
- `verifier/` — C/MPFR checker, embedding audit, and mutation tests;
- `upstream/` — immutable upstream pin, file hashes, fetcher, and report checker;
- `scripts/` — composite verifier, repository audit, and normalized allowlisted release tooling;
- `docs/REPRODUCIBILITY.md` — exact reproduction and interpretation;
- `docs/FORMALIZATION_STATUS.md` — precise Lean status and formalization plan;
- `docs/ERDOS_PROBLEMS_SUBMISSION.md` — conservative community-review submission draft.

## Claim and priority scope

The priority claim is the finite Parseval-prefix central-bin replacement and
the resulting **proposed composite lower bound** \(c_E>0.3805603\), conditional
on the pinned outer-bin reports.  A Git commit, release, or Zenodo DOI provides
a public timestamp; it does not constitute review or acceptance by the Erdős
Problems project.  The requested review scope is stated in
[`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md).

The Zenodo concept DOI for all archived versions is
[`10.5281/zenodo.21969298`](https://doi.org/10.5281/zenodo.21969298). The
historical `v0.1.0-preprint` priority snapshot has version DOI
[`10.5281/zenodo.21969299`](https://doi.org/10.5281/zenodo.21969299) and is
tied to [GitHub release `v0.1.0-preprint`](https://github.com/khanukov/erdos36/releases/tag/v0.1.0-preprint)
and exact source commit
[`e11e4bfd2575494c44d5c66542b8f5f27d64c400`](https://github.com/khanukov/erdos36/commit/e11e4bfd2575494c44d5c66542b8f5f27d64c400).
No version DOI is claimed for `v0.1.1-preprint` until Zenodo assigns it.

## Authorship, AI assistance, and licenses

Dmitry Khanukov is the author and is responsible for the mathematical claim.
AI systems assisted with exploration, code drafting, testing, and editorial
work; all load-bearing files remain subject to human and independent review.
See [`AUTHORS_AND_CREDIT.md`](AUTHORS_AND_CREDIT.md).

Original code, certificate data, and repository documentation are MIT licensed.
The manuscript in `paper/` is CC BY 4.0.  Third-party upstream material is not
vendored or relicensed; see [`LICENSE_SCOPE.md`](LICENSE_SCOPE.md).
