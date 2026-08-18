# Claimed result

**Status: preliminary, unrefereed, and not Lean-verified.**

Let \(c_E\) denote the asymptotic minimum-overlap constant defined in the
manuscript.  The composite certificate in this repository supports the claim

\[
\boxed{c_E>0.3805603}.
\]

This is a proposed improvement over the strongest public computer-certified
lower-bound claim found in the audit, Price's pinned candidate bound
\(0.3805547027625940123745836877\ldots\) by
\(5.5972374059876254\ldots\times10^{-6}\).
Neither claim is described here as an officially recorded or accepted
lower-bound record by the Erdős Problems project.

White already used Parseval energy constraints. The new contribution claimed
here is their finite profile-space prefix projection and a symmetric
certificate for central bins 85 and 86 using prefixes 191, 195, and 200. A
directed-rounding MPFR checker proves its dual objective is below
\(1/0.3805603\). For the other 170 bins, this repository verifies hashes and
reads the successful Arb reports from Price's pinned commit; it does not rerun
those Arb computations.

Accordingly this is a computer-assisted composite theorem candidate, not a
complete solution of Erdős Problem 36, not an independent reproduction of the
outer certificate, and not a formal proof in Lean.

The archival concept DOI is
[`10.5281/zenodo.21969298`](https://doi.org/10.5281/zenodo.21969298). The
historical `v0.1.0-preprint` record has version DOI
[`10.5281/zenodo.21969299`](https://doi.org/10.5281/zenodo.21969299); no
version DOI is asserted for `v0.1.1-preprint` before its deposit is created.
