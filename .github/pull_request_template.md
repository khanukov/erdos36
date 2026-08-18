## Scope

- Exact claim or artifact changed:
- Load-bearing files changed:
- Upstream pin changed: no / yes (explain)

## Mandatory status

- [ ] Described as preliminary and unrefereed.
- [ ] Not described as a solution of Erdős Problem 36.
- [ ] Outer 170 bins described as pinned-report validation unless Arb was actually rerun.
- [ ] No independent-reproduction, peer-review, acceptance, DOI, or Lean claim exceeds recorded evidence.

## Verification

- [ ] `make release-candidate` (one source-bound run at 96/128 bits plus archive verification)
- [ ] visual inspection of every page in the generated PDF
- [ ] `make arxiv` and clean unpacked compilation
- [ ] `git diff --check`

Record the exact commit, run IDs, margins, and any deviation from the documented
trust boundary. A passing authoring workflow is not an independent reproduction.
