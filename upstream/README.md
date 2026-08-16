# SHA-256-pinned upstream reports

The outer 170 mean bins use publicly posted reports from
`Leeham06972452/erdos-36-lower-bound` at exact commit
`6bc610e40083ef61a40966dfb5d38612cabc4c5b`.

```bash
python3 upstream/fetch_upstream.py
python3 upstream/verify_outer_bins.py
```

The fetcher downloads 19 named files and checks them against this repository's
`upstream/SHA256SUMS.txt`. The report checker repeats those hash checks,
validates the 172 ordered bin records, excludes the replaced central pair, and
checks the reported outer maximum against the new target.

This is **report validation, not an Arb rerun**. The upstream verifier and its
dependency environment are not executed here. Downloaded files live in the
ignored `upstream/cache/` directory and are neither committed nor relicensed.
