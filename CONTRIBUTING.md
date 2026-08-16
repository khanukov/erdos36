# Contributing

Changes to load-bearing mathematics or verifier code require:

1. a written soundness argument;
2. a new certificate or proof that old certificates remain valid;
3. directed-rounding or exact verification;
4. updated hashes and logs;
5. review by someone other than the author of the change.

Do not weaken comparisons, replace interval arithmetic with floating-point
heuristics, or silently change the theorem target.
