# Priority and acceptance

## Public timestamp is not acceptance

A commit, Git tag, GitHub Release, arXiv version, or Zenodo deposit can document
what was publicly disclosed by a particular date. It does not by itself show
that the mathematics is correct, novel, independently reproduced, peer
reviewed, or accepted by the Erdős Problems project.

This project has Zenodo concept DOI
[`10.5281/zenodo.21969298`](https://doi.org/10.5281/zenodo.21969298). Its
historical `v0.1.0-preprint` snapshot has version DOI
[`10.5281/zenodo.21969299`](https://doi.org/10.5281/zenodo.21969299), exact
[GitHub release](https://github.com/khanukov/erdos36/releases/tag/v0.1.0-preprint),
and exact source commit
[`e11e4bfd2575494c44d5c66542b8f5f27d64c400`](https://github.com/khanukov/erdos36/commit/e11e4bfd2575494c44d5c66542b8f5f27d64c400).
No `v0.1.1-preprint` version DOI is claimed before Zenodo assigns it. The
project still records no independent reproduction of the new central pair,
peer-review decision, Lean proof, or Erdős Problems acceptance. Those absences
must remain visible in every priority statement.

## Evidence from recorded Erdős-problem results

The examples below are observations, not a universal acceptance policy. The
community database itself says that its status classification is unofficial
and that [erdosproblems.com](https://www.erdosproblems.com) is authoritative
when the two differ. Its
[contribution guide](https://github.com/teorth/erdosproblems/blob/main/CONTRIBUTING.md)
also separates a human-readable `informal_status` from a machine-proof
`formal_status`.

| Example | Public evidence | What it demonstrates |
|---|---|---|
| [Problem 90](https://www.erdosproblems.com/90) | The project's provisional [AI-contributions record](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems) marks the May 2026 work as a full solution and separately records a later improved explicit bound produced with substantial participation from a named group of human mathematicians. | A numerically explicit improvement was digested collaboratively and recorded with named human involvement; the bare model output was not the whole evidence trail. The wiki itself warns that its labels are provisional, so this is an observed pattern rather than an official acceptance rule. |
| [Problem 38](https://www.erdosproblems.com/38) | The community data entry records `informal_status: proved`, `formal_status: Lean`, and the derived status `proved (Lean)`, all dated 2026-05-01. | Human mathematical digestion and formal verification are separate recorded dimensions; a formalized statement alone is not a verified solution. |
| [Problem 728](https://www.erdosproblems.com/728) | [arXiv:2601.07421](https://arxiv.org/abs/2601.07421), first submitted 2026-01-12, explicitly presents a human-readable write-up of a Lean proof and states the precise theorem proved. | The visible record combines an exact theorem, a machine-checked artifact, and an informal explanation suitable for expert scrutiny. |
| [Problem 1196](https://www.erdosproblems.com/1196) | Community-database commit [`ec9e798`](https://github.com/teorth/erdosproblems/commit/ec9e7984943c688f41ea05a1ea758b9ce7a66138) changed the status from `proved` to `proved (Lean)` on 2026-04-16. The multi-author preprint [arXiv:2605.00301](https://arxiv.org/abs/2605.00301) was submitted on 2026-05-01. | In this case the public Lean-status update preceded the arXiv preprint. An arXiv identifier or DOI was therefore not a prerequisite for that database marker. It does not follow that every future claim will be treated the same way. |

The database currently records Problem 36 as open with solution formal status
`unformalized`. A proposed improvement to one lower bound is partial progress
and would not change that logical status.

The same provisional AI-contributions record labels the June 2026 Price lower
bound for Problem 36 as a **candidate partial result**, even though its public
certificate was subsequently rerun by the `occisn` project. This is direct
evidence that a repository and successful computation do not automatically
become a recorded/accepted improvement; clear exposition, independent review,
and explicit maintainer/community follow-up remain important.

Accordingly, Price's value is described in this repository as the strongest
public computer-certified lower-bound claim found in the audit and as the
comparison point for the present numerical improvement. It is not described
as an officially recorded or accepted lower-bound record.

## Inference from the examples

No published universal checklist was found. The recurring observable pattern
is nevertheless useful:

1. state an exact theorem or construction, with no ambiguity about whether it
   resolves the whole problem;
2. expose a stable artifact that experts can inspect and rerun;
3. provide a human-readable proof or soundness argument;
4. obtain independent, expert, or formal verification appropriate to the
   claim;
5. bring the evidence to the problem's discussion venue or maintainers with
   complete provenance and an AI-assistance disclosure.

For an explicit upper construction, evaluation of a finite witness can often
be sufficient. A universal computer-assisted lower bound has a larger trust
surface: the reduction, all analytic inequalities, interval implementation,
and complete case coverage need review. That difference is an inference about
the evidence required, not a statement of official policy.

Another author's self-published repository or priority release is a useful
engineering example but is not evidence that this result has been accepted.

## Vocabulary gates

| Phrase | When it becomes accurate |
|---|---|
| `publicly timestamped` | The exact theorem, source, and evidence are publicly retrievable from a dated immutable tag, release, or archival deposit. |
| `preprint` | A public manuscript version exists in a recognized preprint or archival record. |
| `independently reproduced` | An identified independent party publishes enough commands, hashes, outputs, and methodology to establish what was reproduced. |
| `peer reviewed` | An identifiable scholarly review process has produced that outcome. |
| `Lean-verified` | The exact public theorem is accepted by the pinned Lean environment and passes the documented trust and axiom audit. |
| `recorded by the Erdős Problems project` | The authoritative problem page or its maintainers explicitly record the result and its scope. |
| `accepted` | The accepting body and the nature of acceptance are named; the word is not inferred from a DOI, repository star, citation, or silence. |

## Priority record for this result

Parseval energy constraints themselves are prior work in White's framework.
The priority claim should therefore be limited to the finite profile-space
Parseval-prefix projection, the resulting central-bin certificate and
directed-rounding verification, and the proposed composite lower bound
`c_E > 0.3805603`, conditional on the pinned outer-bin reports. A defensible
public record should preserve:

- the exact theorem and explicit statement that Problem 36 remains open;
- the exact source commit and release tag;
- the manuscript, certificate, verifier, generated evidence, and checksums;
- the upstream repository, commit, filenames, and hashes;
- the absence or presence of independent reproduction and Lean verification;
- authorship, AI-assistance, licensing, and prior-art disclosures;
- later corrections as new versions rather than silent replacement.

The historical first publication honestly establishes a preliminary priority
timestamp but not correctness or acceptance. Corrections belong in linked new
versions, never in a rewritten `v0.1.0-preprint` tag or record. Independent
review and community recording are later, separately evidenced events.
