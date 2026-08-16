# Preliminary Parseval-prefix bound for Erdős Problem 36

This **preliminary, unrefereed** priority release records the proposed
composite lower bound \(c_E>0.3805603\) for Erdős Problem 36. It does not solve
the problem.

The new contribution replaces central bins 85 and 86 with a finite
Parseval-prefix certificate checked by a directed-rounding C/MPFR verifier.
The other 170 bins are validated from SHA-256-pinned reports at Price commit
`6bc610e40083ef61a40966dfb5d38612cabc4c5b`; this repository does not rerun
their Arb computation.

The release archive records its source commit, provenance, verification scope,
generated evidence, and internal SHA-256 manifest. The new central result has
not been independently reproduced or peer reviewed, and no claim in this
repository is Lean-verified.

Release identity:

- exact commit: `@VERIFIED_SHA@`
- exact tree: `@SOURCE_TREE@`
- required GitHub Actions run: https://github.com/khanukov/erdos36/actions/runs/@SOURCE_RUN_ID@
- release archive: `@ARCHIVE_NAME@`
- release archive SHA-256: `@ARCHIVE_SHA256@`
- manuscript PDF: `@PDF_NAME@`
- manuscript PDF SHA-256: `@PDF_SHA256@`

`GITHUB_RELEASE_SHA256SUMS.txt` authenticates all three substantive GitHub
release assets. Licensing is path-specific: original repository material
outside `paper/` is MIT-licensed, while original manuscript material under
`paper/` is CC BY 4.0. See `LICENSE_SCOPE.md` in the source and release archive.
