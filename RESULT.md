# Claimed result

**Status: preliminary, unrefereed, and not Lean-verified.**

Let \(c_E\) denote the asymptotic minimum-overlap constant defined in the
manuscript.  The composite certificate in this repository supports the claim

\[
\boxed{c_E>0.3805603}.
\]

This improves the pinned Price lower bound
\(0.3805547027625940123745836877\ldots\) by
\(5.5972374059876254\ldots\times10^{-6}\).

The new contribution is a symmetric certificate for central bins 85 and 86,
using finite Parseval prefixes 191, 195, and 200.  A directed-rounding MPFR
checker proves its dual objective is below \(1/0.3805603\).  For the other 170
bins, this repository verifies hashes and reads the successful Arb reports from
Price's pinned commit; it does not rerun those Arb computations.

Accordingly this is a computer-assisted composite theorem candidate, not a
complete solution of Erdős Problem 36, not an independent reproduction of the
outer certificate, and not a formal proof in Lean.
