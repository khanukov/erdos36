# Formalization status

## Current status

No claim in this repository is verified in Lean.

The repository contains no `.lean` source file, `lean-toolchain`, `lakefile`,
or Lake dependency manifest. `STATUS.json` records
`"lean_checked_claims": []` and `"lean_verified": false`. The C/MPFR checker is
a rigorous computer-assisted verification program, but it is not a Lean
kernel proof and must not be described as one.

The fact that the statement of Erdős Problem 36 has been represented in an
external formal-conjectures collection does not formalize this new bound or
this repository's argument. Formalizing a problem statement and formally
checking a proposed solution are different accomplishments.

## Claims still outside Lean

Every load-bearing part of the proposed result remains outside Lean,
including:

- the discrete-to-continuous reduction for the minimum-overlap constant;
- the positive-part dual lemma in the precise normalization used here;
- the moment and Fourier inequalities used by all certificate rows;
- the finite Parseval-prefix identity and its projected inequality;
- the symmetry step joining central bins 85 and 86;
- parsing and semantic interpretation of the 150 certificate rows;
- the interval enclosure of the positive-part integral;
- the interpretation of the 170 pinned upstream Arb report rows;
- the final composite implication `c_E > 0.3805603`.

## A defensible formalization plan

Formalization should proceed in layers so that each boundary is explicit.

1. **Statement and normalization.** Define the discrete overlap quantity,
   the asymptotic constant, the continuous profile model, Fourier
   normalization, and the exact theorem statement.
2. **Analytic reduction.** Formalize the step-function limiting argument,
   admissibility conditions, overlap-profile identities, and the
   positive-part dual lemma.
3. **Parseval-prefix lemma.** Prove the period-two Parseval identity, the sign
   of the integer Fourier coefficients, the finite-prefix inequality, and the
   symmetry used by the central pair.
4. **Certificate semantics.** Define a small typed certificate language and
   prove that a well-formed list of nonnegative multipliers produces a valid
   dual function for its mean bin.
5. **Certified numerics.** Either implement and prove a kernel-checked interval
   evaluator or import exact certificates whose checking theorem is proved in
   Lean. Calling the current C binary from Lean would not by itself remove the
   C/MPFR checker from the trusted base.
6. **Composition.** Formalize all 172 bin obligations, the replacement of bins
   85 and 86, and the strict comparison at the target.

A useful intermediate milestone is a Lean proof of the Parseval-prefix lemma
and positive-part dual lemma alone. That would formalize the new analytic
ingredient but would still not justify calling the numerical bound
Lean-verified.

## Conditions for a future Lean claim

The phrase "Lean-verified" may be used only after the repository contains all
of the following in one reviewed commit:

- the exact theorem statement corresponding to the public mathematical claim;
- a pinned Lean toolchain and dependency manifest;
- a clean build from the documented command in CI;
- no `sorry`, `admit`, disabled declaration, or unreviewed custom axiom on the
  theorem's dependency path;
- an axiom audit such as `#print axioms` for the exported theorem;
- documentation of any native-code, oracle, or external-checker trust;
- a public link to the exact formal proof revision.

Until then, use "computer-assisted", "directed-rounding MPFR checked", and
"not Lean-verified" together. Do not use "formally verified" without naming a
different formal system and its exact artifact.
