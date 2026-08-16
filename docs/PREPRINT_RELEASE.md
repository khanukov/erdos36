# Preprint release procedure

## Current state

This document is a release procedure, not release authorization. The
`publish-priority-preprint` workflow is deliberately armed only by a successful
`main`-branch `verify-priority-package` run. Merging that workflow to `main`
can therefore create the tag and public GitHub prerelease. Do not merge or
manually dispatch publication work until the author has authorized publication
and the Zenodo GitHub integration is enabled for this repository.

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
- the author's Zenodo account is connected to GitHub and `khanukov/erdos36` is
  enabled in the Zenodo GitHub repository list before the publishing commit is
  merged.

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

The `publish-priority-preprint` workflow creates the tag and release from the
exact successful `main` verification run. It refuses to move an existing tag,
checks the downloaded Actions artifact and its embedded provenance again, and
uses:

- tag: `v0.1.0-preprint`;
- title: `v0.1.0-preprint — preliminary Parseval-prefix bound for Erdős Problem 36`;
- status: public, non-draft GitHub prerelease;
- classification: preliminary priority preprint, not an accepted result;
- assets: the release ZIP, its companion `.sha256` file, and
  `build/erdos36-preprint-0.1.0-preprint.pdf`, plus an external
  `GITHUB_RELEASE_SHA256SUMS.txt` manifest.

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

## Automatic GitHub-to-Zenodo workflow

Use the Zenodo GitHub integration for the first archival timestamp. Before the
publishing commit reaches `main`, sign in to Zenodo through GitHub, synchronize
the repository list, and enable `khanukov/erdos36`. The successful `main` CI
then triggers `publish-priority-preprint`, which creates the annotated tag and
GitHub prerelease. The enabled Zenodo integration receives that release event
and archives the tagged repository snapshot.

Official setup references: [link the GitHub account][zenodo-link], choose
`Sync now` and [enable the repository][zenodo-enable], then follow Zenodo's
[GitHub release archiving flow][zenodo-archive].

The automatic Zenodo record contains GitHub's source snapshot, not the custom
GitHub Release assets. Consequently every load-bearing source file,
certificate, verifier, upstream retrieval rule and hash, license, and metadata
file must be in the tagged tree. The pinned upstream reports themselves remain
runtime downloads and are not vendored. The deterministic release ZIP,
generated verification evidence, compiled PDF, and their external manifest
remain attached to the GitHub prerelease and are linked by its exact commit and
Actions run.

The GitHub integration does not support reserving the first version DOI in
advance. After Zenodo finishes processing, record the version DOI and concept
DOI, inspect the title, author, description, version, licenses, related links,
and archived source snapshot, and verify that they match `.zenodo.json` and the
tag. Add the DOI to `CITATION.cff`, the manuscript, and repository badges only
in a later commit/version; never rewrite the published priority tag.

If the Zenodo record does not appear, preserve the existing tag and prerelease,
diagnose the integration, and do not silently recreate or retag the release.
Preserve substantive corrections as linked new versions.

[zenodo-link]: https://help.zenodo.org/docs/profile/linking-accounts/
[zenodo-enable]: https://help.zenodo.org/docs/github/enable-repository/
[zenodo-archive]: https://help.zenodo.org/docs/github/archive-software/github-upload/

## arXiv and community sequence

After the GitHub release and Zenodo record are stable, submit the tested
`build/erdos36-arxiv-source.zip` to arXiv, inspect arXiv's generated PDF, and preserve
the v1 identifier. Then, and only then, use the conservative text in
`docs/ERDOS_PROBLEMS_SUBMISSION.md` and the exact request in
`docs/INDEPENDENT_REVIEW.md` for outreach.

Record each event separately: GitHub release time, Zenodo publication and DOI,
arXiv v1 time, independent review, and any Erdős Problems acknowledgement.
None implies the others.
