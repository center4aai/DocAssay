# Baseline REFUTED evidence from held-out validation repos

Source: archived baseline claim dumps from
the private deterministic-operator run `sweep-2026-10-12` (claims not shipped).
These are **baseline** runs (no injection) on the held-out validation repos. They
show that a 0-REFUTED acceptance gate is not realistic for ordinary repositories.

| repo | claims | SUPPORTED | NEI | REFUTED | REFUTED share |
|---|---:|---:|---:|---:|---:|
| bitsandbytes | 2821 | 1249 | 1538 | 34 | 1.2% |
| fastapi | 4265 | 1329 | 2874 | 62 | 1.5% |
| pydantic | 3294 | 870 | 2395 | 29 | 0.9% |

Examples that look like baseline false positives:

- `bitsandbytes`: `DEPENDENCY python @ COMPILE_H100_L40.md:8` — "Python >= 3.9"
  (a build instruction, not a declared project dependency).
- `bitsandbytes`: `DEPENDENCY torch @ agents/code_standards.md:220` — "The
  codebase supports PyTorch 2.3+. The API names changed in PyTorch 2.4:" (a
  historical/compatibility note).
- `fastapi`: `DEPENDENCY pydantic @ docs/en/docs/how-to/migrate-from-pydantic-v1-to-pydantic-v2.md`
  — migration guide mentions of Pydantic v1/v2, not a current requirement.
- `pydantic`: `PATH_EXISTS llms.txt @ README.md:11` — a badge linking to an
  external `llms.txt` URL, not a repository file.
- `pydantic`: `PATH_EXISTS flamegraph.svg @ pydantic-core/README.md:131` — a
  command output path, not a tracked repository file.

Conclusion: on real repositories the engine produces tens of baseline
`REFUTED` claims, several of which are false positives. A workflow that
requires `0 REFUTED` before accepting a corpus will either discard such
repositories or edit the documentation until the tool is happy. That is a
tool-conditioned selection loop and hides the baseline precision problem.
Baseline findings should be frozen, recorded, and adjudicated (true doc bug vs
false positive), not used as an acceptance gate.
