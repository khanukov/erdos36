# Pinned upstream inputs

- Repository: `Leeham06972452/erdos-36-lower-bound`
- Commit: `6bc610e40083ef61a40966dfb5d38612cabc4c5b`
- Certificate input: `certificate/erdos_aug_central_gridF400.json`
- Arb verifier source: `certificate/prove_erdos_0380554275_arb.py`
- Aggregate report: `certificate/erdos_0380554700_theorem_target_aggregate.json`
- Per-bin report: `certificate/erdos_0380554700_theorem_target_per_bin.csv`

Recorded report facts used by the composite check:

- the upstream report marks all 172 bins proved at its target;
- central bins 85 and 86 cover `[-0.003125,0]` and `[0,0.003125]`;
- the largest reported `D` outside that pair is
  `2.627538530873375790090272175878307131812586378`.

The new package leaves the 170 outer rows unchanged and replaces only the
symmetric central pair. It checks the immutable reports but does not claim to
reproduce their Arb computation.
