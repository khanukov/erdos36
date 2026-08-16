# Preprint release procedure

## Current state

This document is a release procedure, not release authorization. Preparing it
does not create a tag, GitHub Release, Zenodo record, arXiv submission, or
community post. This repository version has no DOI. No external contact or
publication should be made as part of documentation preparation.

The intended first public version is `0.1.0-preprint`, with tag
`v0.1.0-preprint`. It must be described as preliminary, unrefereed, not a
solution of Erdős Problem 36, not independently reproduced, and not
Lean-verified unless the underlying facts change before release and are
documented in the same commit.

## Release gates

The following are blocking for an honest priority release:

- the source tree is clean and the release commit is identified;
- `VERSION`, `STATUS.json`, `CITATION.cff`, `.zenodo.json`, the manuscript,
  and the release title agree on version, date, author, title, claim, and
  preliminary status;
- the MIT and CC BY 4.0 license scopes are accurate and no unlicensed upstream
  material is included in the archive;
- `make verify` passes as one fresh composite chain;
- `make verify-central-128` passes;
- the manuscript builds and has been visually inspected;
- the arXiv source builds after being unpacked into an empty directory;
- the release ZIP is built from the clean commit, passes `unzip -t`, and its
  companion SHA-256 file verifies;
- the ZIP contains `COMMIT_SHA.txt`, `PROVENANCE.json`,
  `VERIFICATION_SCOPE.txt`, and `ARTIFACT_SHA256SUMS.txt`;
- the GitHub release body and every deposit repeat the trust boundary without
  calling the upstream reports independently rerun;
- repository settings needed to protect the release and tag are enabled before
  publication.

Independent reproduction and a Lean proof are not prerequisites for an
accurately labelled preliminary timestamp. Their absence is a prerequisite
for using the explicit negative disclosures above. They become gates only for
later language claiming independent reproduction or Lean verification.

## Local release build

Run from the exact clean commit:

```bash
git status --short
make verify
make verify-central-128
make paper
python3 scripts/build_release.py
python3 scripts/verify_release.py
```

`git status --short` must print nothing before the build. The release builder
prints the ZIP path and SHA-256 digest. Verify the companion checksum from the
`build/` directory and test the archive before upload. Preserve the CI run URL
and the exact commit and tree identifiers in the release record.

Create and test the arXiv source after the release ZIP is complete:

```bash
make arxiv
temp_dir="$(mktemp -d)"
unzip build/erdos36-arxiv-source.zip -d "$temp_dir"
cd "$temp_dir"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The arXiv ZIP, release ZIP, and preprint PDF are different artifacts and should
not be substituted for one another.

## GitHub release

Create the tag and release only after all gates pass. Use:

- tag: `v0.1.0-preprint`;
- title: `v0.1.0-preprint — preliminary Parseval-prefix bound for Erdős Problem 36`;
- classification: preliminary priority preprint, not an accepted result;
- assets: the release ZIP, its companion `.sha256` file, and
  `build/erdos36-preprint-0.1.0-preprint.pdf`.

The release body should say:

> This preliminary, unrefereed release records the proposed composite lower
> bound \(c_E>0.3805603\) for Erdős Problem 36. It does not solve the problem.
>
> The new contribution replaces central bins 85 and 86 with a finite
> Parseval-prefix certificate checked by a directed-rounding C/MPFR verifier.
> The other 170 bins are validated from SHA-256-pinned reports at Price commit
> `6bc610e40083ef61a40966dfb5d38612cabc4c5b`; their Arb computation is not
> rerun by this repository.
>
> The release archive records its source commit, provenance, verification
> scope, generated evidence, and internal and external SHA-256 manifests. The
> new central result has not been independently reproduced or peer reviewed,
> and no claim in this repository is Lean-verified.

Do not mark the release as an accepted solution. If GitHub release immutability
is available for the repository, enable it before publishing; otherwise
preserve the signed or protected tag, release checksum, and archival deposit
as the public identity record.

## Manual Zenodo workflow

Use a manual Zenodo deposit for the archival record. Do not assume that the
GitHub-Zenodo integration will include CI-generated release assets; that
integration normally archives the tagged repository source rather than the
custom release ZIP and verification evidence.

1. After the release gates pass but before creating the final tag, create an
   unpublished Zenodo draft and select the resource type `Publication` and
   subtype `Preprint`.
2. Reserve a DOI in the draft if the DOI is to appear in the manuscript and
   repository metadata. Reserving a DOI is not publication and must not be
   described as a published record.
3. If a DOI is reserved, add the exact DOI to the manuscript and metadata,
   commit those changes, and rerun every release gate from that final commit.
4. Create the protected tag and GitHub Release from that exact commit. Upload
   the release ZIP, companion checksum, and preprint PDF to the Zenodo draft.
5. Enter and independently compare the title, author, version, publication
   date, description, keywords, license, repository URL, release URL, upstream
   reference, and DOI against the final source. The main preprint is CC BY 4.0;
   the archive's path-specific MIT and CC BY 4.0 terms remain recorded in
   `LICENSE_SCOPE.md`.
6. Download the draft files, verify their hashes, inspect the rendered record,
   and only then publish the Zenodo version.
7. Preserve later substantive corrections as linked new versions. Do not
   replace a public priority record silently.

The current `.zenodo.json` is a metadata cross-check for this repository. A
manual deposit must be checked field by field; the filename alone does not
populate or publish a manual Zenodo draft.

## arXiv and community sequence

After the GitHub release and Zenodo record are stable, submit the tested
`build/erdos36-arxiv-source.zip` to arXiv, inspect arXiv's generated PDF, and preserve
the v1 identifier. Then, and only then, use the conservative text in
`docs/ERDOS_PROBLEMS_SUBMISSION.md` and the exact request in
`docs/INDEPENDENT_REVIEW.md` for outreach.

Record each event separately: GitHub release time, Zenodo publication and DOI,
arXiv v1 time, independent review, and any Erdős Problems acknowledgement.
None implies the others.
