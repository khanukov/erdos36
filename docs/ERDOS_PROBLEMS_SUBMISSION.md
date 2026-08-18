# Erdős Problems submission

## Purpose and current restriction

This file contains a conservative submission text for review of a partial
bound improvement. It is not an authorization to contact maintainers, post on
the problem page, open a database pull request, or publish an artifact. The
historical `v0.1.0-preprint` priority release exists; outreach for the corrected
package should wait until the exact `v0.1.1-preprint` release exists and the
release gates in `docs/PREPRINT_RELEASE.md` have passed.

Erdős Problem 36 remains open. A lower-bound improvement does not solve it and
does not justify changing its status to `proved`, `solved`, or `proved (Lean)`.
The appropriate initial request is to record and review partial progress.

## Where the submission belongs

The authoritative place for detailed mathematical discussion is the
[Erdős Problem 36 page](https://www.erdosproblems.com/36). The community
[database contribution guide](https://github.com/teorth/erdosproblems/blob/main/CONTRIBUTING.md)
directs detailed mathematical commentary to the corresponding problem page;
its pull requests and issues are suitable for concise database updates and
methodology links. That database also states that its status classification is
unofficial and that the main website is the more reliable source when they
differ.

## Submission text

Use the following text only after `v0.1.1-preprint` is public and its checksums
and exact release commit have been verified.

> **Preliminary partial result: proposed lower bound \(c_E>0.3805603\).**
>
> I am sharing a preliminary, unrefereed computer-assisted certificate for
> the lower bound \(c_E>0.3805603\) in Erdős Problem 36. The new contribution
> is not the Parseval energy constraint itself, which is prior work due to
> White, but its finite profile-space prefix projection and use to replace the
> two binding central mean bins, 85 and 86, of the public 172-bin Price
> certificate at
> commit `6bc610e40083ef61a40966dfb5d38612cabc4c5b`.
>
> The repository's directed-rounding C/MPFR checker freshly verifies the new
> central pair. For the other 170 bins, it downloads SHA-256-pinned upstream
> report files and checks their structure and reported upper endpoints; it
> does not rerun the upstream Arb computation. A fresh composite run requires
> the central and outer results to carry the same run identifier.
>
> Repository and reproduction instructions:
> https://github.com/khanukov/erdos36
>
> Zenodo concept DOI: https://doi.org/10.5281/zenodo.21969298
>
> Historical `v0.1.0-preprint` version DOI:
> https://doi.org/10.5281/zenodo.21969299
>
> I request review of (1) the Parseval-prefix normalization and sign, (2) the
> positive-part integration and interval bounds in the C checker, (3) the
> symmetry and 172-bin splice, (4) an independent rerun of the upstream Arb
> computation or another verification of the 170 outer bins, and (5) novelty
> and attribution relative to White, Price, and the independent `occisn`
> audit.
>
> This is a proposed partial bound improvement, not a solution of Erdős
> Problem 36. It has not been peer reviewed or independently reproduced, and
> no claim is verified in Lean. AI systems assisted with exploration, code and
> test drafting, auditing, and editorial work; responsibility for the claim
> and release remains with the author.

Price's `0.38055470` result should be described as the strongest public
computer-certified claim currently used as the comparison point, not as an
officially accepted record. The concept DOI above is stable. The historical
`v0.1.0-preprint` record is tied to
[release `v0.1.0-preprint`](https://github.com/khanukov/erdos36/releases/tag/v0.1.0-preprint)
and exact commit
[`e11e4bfd2575494c44d5c66542b8f5f27d64c400`](https://github.com/khanukov/erdos36/commit/e11e4bfd2575494c44d5c66542b8f5f27d64c400).
Do not invent a `v0.1.1-preprint` version DOI; add it only after Zenodo assigns
one, together with the exact new release commit.

## Requested disposition

The initial request should be limited to:

- mathematical and computational review of the stated partial result;
- addition of a clearly labelled preliminary reference or comment if the
  maintainers consider that appropriate;
- correction of any attribution, priority, or prior-art omission;
- guidance on what independent evidence is required before the improvement is
  described as verified or recorded.

It should not request that Problem 36 be marked solved. It should not request a
`Lean` status, because this repository contains no Lean proof. It should not
call the result accepted, published, independently verified, or peer reviewed.

## Evidence to attach after release

Provide links to the exact `v0.1.1-preprint` release page, protected tag or
exact commit, manuscript, release ZIP, companion SHA-256 file, Zenodo concept
record, and `docs/INDEPENDENT_REVIEW.md`. Report
the actual CI run and external review records rather than a checklist of work
that has not occurred.

If a mathematical correction is required after the first public version,
preserve the original record and issue a new version. Do not silently replace
the theorem statement, certificate, verifier, or evidence behind an existing
priority timestamp.
