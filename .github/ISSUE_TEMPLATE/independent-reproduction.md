---
name: Independent reproduction report
about: Report a clean-room verification of the new central certificate
title: "Independent reproduction: "
labels: verification
---

Please distinguish a clean-room reproduction from rerunning this repository's
own checker.

- Commit/tag verified:
- OS and architecture:
- Compiler and exact GMP/MPFR versions:
- Independent implementation or same C checker:
- Commands and complete output:
- Certificate SHA-256:
- Central-bin result and rigorous margin:
- Did you rerun Price's Arb computation for all 170 outer bins, or only validate its pinned reports?
- Differences, failures, or soundness concerns:

Do not mark the result independently verified merely because `make verify`
passes; that command is the authoring verification path.
