# Trust boundary

## Scope of the checked claim

This repository presents a preliminary, unrefereed composite certificate for

\[
c_E>0.3805603.
\]

It does not determine the exact value of \(c_E\), solve Erdős Problem 36,
recompute the complete upstream Arb certificate, or formally verify any claim
in Lean.

A successful `make verify` run has a deliberately narrower meaning: the new
central certificate passes this repository's C/MPFR checker, the pinned
upstream report files pass their integrity and structural checks, and the two
results are composed only when they were generated under the same fresh run
identifier. The conclusion still depends on the mathematical reduction and
row inequalities stated in the manuscript and on the correctness of the
pinned upstream Arb reports.

## Evidence chain

| Layer | Checked here | Not established by that check |
|---|---|---|
| Repository closure | `scripts/check_repo.py` checks required files and conservative status metadata; `scripts/verify_checksums.py` rejects missing, changed, and unlisted non-generated files within its declared scope. | Mathematical correctness, authorship, novelty, or external acceptance. |
| Certificate embedding | `verifier/check_embedding.py` checks the certificate schema, target, central interval, row types, row constants, multipliers, and their exact embedding in the C source. `verifier/test_embedding_mutations.py` checks rejection of eleven load-bearing mutations. | That the analytic inequality represented by each row is valid. |
| Central interval check | `verifier/run_central_check.sh` compiles and runs `verifier/verify_central_mpfr.c`. The program uses directed MPFR rounding, verifies the central interval `[-0.003125, 0]`, bounds the positive-part integral, and makes the strict comparison with `1/0.3805603`. | Correctness of MPFR, the compiler, the checker implementation, the manuscript's symmetry argument for `[0, 0.003125]`, or an independent implementation. |
| Pinned outer reports | `upstream/fetch_upstream.py` obtains 19 files from Price's repository at commit `6bc610e40083ef61a40966dfb5d38612cabc4c5b` and checks their recorded SHA-256 digests. `upstream/verify_outer_bins.py` checks the aggregate flag, the complete ordered list of 172 rows, the 170 noncentral reported upper endpoints, and their margin at the new target. | A fresh execution of Price's Arb verifier, the correctness of Arb, or the truth of a report merely because its bytes match. |
| Composite result | `scripts/verify_all.sh` assigns one fresh `VERIFICATION_RUN_ID`; `scripts/verify_composite.py --require-fresh` accepts only passing central and outer results carrying that identifier and the same target. | Peer review, independent reproduction, formal verification, or acceptance by the Erdős Problems project. |

## Trusted mathematical inputs

The composite argument relies on the following mathematical inputs. They must
be reviewed as mathematics; a passing executable cannot substitute for that
review.

- the reduction from the discrete minimum-overlap problem to the continuous
  profile optimization used in the manuscript;
- the positive-part dual lemma and every moment and Fourier row admitted by
  the certificate;
- the normalization and sign in the finite Parseval-prefix inequality;
- the evenness and symmetry argument that transfers the checked negative
  central bin to its positive partner;
- the splice showing that replacing bins 85 and 86 while retaining the other
  170 bins proves the stated global lower bound;
- the strict-inequality interpretation of the reported interval margins.

The optimizer that found the multipliers is not trusted. Floating-point search
output and printed decimal diagnostics are not proof inputs. Only the embedded
certificate constants and the directed-rounding comparisons made by the
checker are load-bearing in the new central computation.

## Trusted computing base

For the central check, the trusted computing base includes the C source, the
embedding checker, the C compiler and linker, GMP, MPFR and its elementary
functions and rounding modes, the operating system, and the hardware. For the
outer bins it additionally includes the upstream Arb computation that produced
the pinned reports. SHA-256 protects identity of those report bytes; it does
not validate their derivation.

The source hash manifest excludes generated build products and the downloaded
`upstream/cache/` directory by design. The release builder places generated
evidence in the release archive and writes an internal artifact manifest plus
a companion checksum for the ZIP. Those hashes establish file identity, not
mathematical validity.

## Explicitly absent assurances

- There are no Lean sources, Lean toolchain pin, Lake dependency lockfile, or
  Lean theorem checked by this repository.
- No independent clean-room reproduction of the new central certificate is
  recorded.
- No independent rerun of all 172 upstream Arb bins is performed by this
  repository.
- No peer-review decision or acceptance decision is recorded.
- No DOI has been assigned to this repository version.

The machine-readable status in `STATUS.json` is authoritative for these
negative disclosures. Any future review, formalization, or publication event
must update that file and the corresponding human-readable documents in the
same reviewed commit.

## Failure handling

Any certificate mismatch, unexpected schema field, nonpositive multiplier,
failed interval precondition, nonpositive margin, stale run identifier,
upstream hash mismatch, missing report row, or checker failure invalidates the
composite run. A failure must not be converted into a warning or repaired by
editing generated evidence. Correct the source or certificate, rerun the full
chain, and publish the new result as a distinct version.
