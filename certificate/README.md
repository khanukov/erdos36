# Central certificate

`central_certificate.json` is the human-readable source for the 150 load-bearing
rows used on the symmetric central-bin pair. The C verifier embeds the same
constants for speed. Before every run, `verifier/check_embedding.py` checks the
target, central bin, row schema and order, row counts, every frequency, bound,
and multiplier, the fixed `cos_pi` and Parseval bounds, and the C size
constants. `verifier/test_embedding_mutations.py` runs a negative mutation
suite covering representative load-bearing and explanatory fields.

Row counts:

- 1 second-moment row;
- 71 ordinary cosine upper rows;
- 75 integer-π cosine upper rows;
- 3 Parseval-prefix rows with `K = 191, 195, 200`.

The JSON's `floating_diagnostic` section records optimizer diagnostics and is
not used as rigorous numerical evidence. The C/MPFR pass comparison is the
load-bearing central numerical check.
