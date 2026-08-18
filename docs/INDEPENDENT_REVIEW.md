# Independent review

## Current status

As of `v0.1.1-preprint`, the new central certificate has not received an
independent clean-room reproduction or peer review. This repository validates
pinned upstream reports for the other 170 bins but does not rerun their Arb
computation. No review request has been sent by preparing this document.

## Exact review request

The following request is ready for use only after the public corrected
`v0.1.1-preprint` release exists. The reviewer must confirm the exact commit
shown on that release before beginning; a moving `main` branch is not a review
identifier.

> **Subject: Independent verification request — proposed Erdős 36 lower bound \(c_E>0.3805603\)**
>
> I request an independent review of a preliminary computer-assisted lower
> bound for Erdős Problem 36. The proposed statement is
> \(c_E>0.3805603\). The new work replaces only central bins 85 and 86 of
> Liam Price's public 172-bin certificate at commit
> `6bc610e40083ef61a40966dfb5d38612cabc4c5b`.
>
> Please review the exact source commit attached to release
> `v0.1.1-preprint` at https://github.com/khanukov/erdos36 and record that
> commit and the release ZIP SHA-256 digest in your report.
> The stable Zenodo concept DOI is
> https://doi.org/10.5281/zenodo.21969298. The earlier priority snapshot,
> which this correction does not rewrite, is `v0.1.0-preprint` at exact commit
> `e11e4bfd2575494c44d5c66542b8f5f27d64c400` with version DOI
> https://doi.org/10.5281/zenodo.21969299.
>
> The minimum reproduction is a clean `make verify` run followed by
> `make verify-central-128`. A stronger review would independently inspect or
> reimplement the Parseval-prefix row semantics and central positive-part
> integral, and rerun Price's Arb verifier for all 172 bins rather than trusting
> its pinned reports.
>
> Please determine separately whether: (1) the analytic reduction and
> Parseval-prefix inequality are correct in the stated normalization; (2) the
> JSON certificate and C constants agree completely; (3) the directed-rounding
> MPFR integration and strict comparison are sound; (4) symmetry covers both
> central bins; (5) the 170 retained outer bins are below the new threshold;
> and (6) the composite implication proves exactly the stated lower bound.
>
> Please report the operating system, architecture, compiler, GMP and MPFR
> versions, commands, exit statuses, generated `run_id` values, numerical
> margins, and hashes. State explicitly whether you only ran the supplied code,
> audited it line by line, used an independent implementation, and reran the
> upstream Arb computation.
>
> The claim is preliminary and unrefereed. It is not a solution of Erdős
> Problem 36 and is not Lean-verified. Please report any counterexample,
> unsound interval step, missing assumption, attribution issue, or ambiguity
> before describing the result as independently reproduced.

## Review checklist

### Mathematical reduction

- Match the definition of \(c_E\) in the theorem, manuscript, certificate, and
  metadata.
- Check the discrete-to-continuous reduction and all normalizations.
- Check the positive-part dual lemma and the direction of every inequality.
- Derive the period-two Parseval identity and the finite-prefix inequality
  independently.
- Verify the sign convention for integer Fourier modes and the factor of two.
- Check the symmetry step and the strict final inequality.

### Certificate semantics and embedding

- Confirm that all 150 rows have the declared type, parameter, right-hand side,
  and nonnegative multiplier.
- Confirm that every load-bearing JSON field is embedded in the C source and
  that unexpected or reordered semantic content cannot pass unnoticed.
- Run the supplied mutation tests and add adversarial changes for any newly
  identified field or parser ambiguity.
- Confirm that optimizer output is unnecessary once the certificate is fixed.

### Central numerical checker

- Audit every directed rounding mode and interval operation.
- Audit MPFR sine, cosine, and pi use, derivative enclosures, dyadic
  subdivision, positive-cell merging, terminal-cell bounds, and the
  positive-part antiderivative.
- Check that all analytic preconditions are enforced before a row is used.
- Confirm that printed binary floating-point diagnostics are not used as proof
  endpoints.
- Compare 96-bit and 128-bit results and, preferably, implement the check with
  a distinct interval or exact-arithmetic backend.

### Outer reports and composition

- Confirm the upstream repository, exact commit, 19 file hashes, target, bin
  ordering, and excluded central indices.
- Distinguish byte identity and report parsing from a fresh Arb rerun.
- Prefer a clean rerun of the upstream Arb verifier or an independent
  verification of all retained rows.
- Confirm that central, outer, and composite outputs carry one fresh `run_id`
  and the same target.
- Confirm that the release provenance and internal and external checksum
  manifests match the reviewed files.

### Scholarship and wording

- Check the novelty claim against White's Fourier/convex framework, Price's
  certificate, the `occisn` independent audit, and other public lower-bound
  work.
- Treat White's Parseval energy constraint as prior work; assess only the
  claimed finite profile-space prefix projection, certificate construction,
  central-bin application, and resulting numerical bound as possible novelty.
- Check that copied or derivative material is neither vendored nor relicensed
  without permission.
- Confirm that every public description says preliminary, unrefereed, partial,
  not independently reproduced until that changes, and not Lean-verified.

## Review outcome vocabulary

Use the narrowest supported description:

| Description | Minimum evidence |
|---|---|
| Supplied workflow reproduced | Clean execution of the exact `v0.1.1-preprint` release with matching hashes and passing outputs. |
| Supplied implementation audited | A documented line-by-line soundness review in addition to execution. |
| Central result independently reproduced | A distinct implementation checks the analytic rows and central integral at the stated target. |
| Full composite independently reproduced | The central result is independently checked and the upstream Arb computation or all retained outer rows are independently rerun. |
| Peer reviewed | A review decision exists from an identified scholarly venue; repository comments alone do not establish this. |
| Lean-verified | The exact exported theorem is accepted by a documented Lean toolchain with an axiom and trust audit. |

A reviewer should publish enough detail to distinguish these categories. An
anonymous statement, a screenshot, or a bare `PASS` line is not a sufficient
independent-review record.
