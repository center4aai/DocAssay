# Stage B natural corpus (`synthetic-natural/`)

This is the **held-out** corpus for Stage B of the tool-validation protocol
(`../../validation/protocol.md`, `runs/stage-b-2026-10-20/PREREGISTRATION.md`).
It is separate from the four dev/regression repos in `../synthetic/`.

## Repos

| repo | domain | natural project |
|---|---|---|
| `gaugekit` | environmental data | stream-gauge CSV loading and summary statistics |
| `gridwatch` | energy/utility data | smart-meter interval parsing and tariff calculation |
| `plotline` | creative/visual | SVG chart primitives (scales, marks, canvas) |
| `palette` | creative/visual | color palette generation and contrast checks |
| `sheetmusic` | music | chord/progression parsing and transposition |
| `recipecard` | everyday/consumer | recipe scaling and shopping-list generation |

The corpus has three domains (environmental/energy data, creative/visual,
music/everyday), two repos each. It is designed from what the software does, not
from a list of surfaces: config keys, HTTP endpoints, schema fields, enum
members, example commands and example files are optional in the spec schema and
are present only when the project naturally has them.

## Generation

The LLM roles are pre-created OpenCode subagents (`.opencode/agents/`):

- `repo-architect` — writes `spec.json` (natural project design).
- `repo-docwriter` — writes `README.md` + the guide + `docs/api.md` from the
  spec and source.
- `repo-auditor` — read-only consistency audit against spec + source, no engine.

The deterministic parts live in `../scripts/generate_synthetic.py`
(`spec-validate`, `materialize`, `baseline-report`). Code is materialized
deterministically from the spec.

### Commands

```bash
B=research/submission/demo/injected_gold
for r in gaugekit gridwatch plotline palette sheetmusic recipecard; do
  PYTHONPATH=src uv run python $B/scripts/generate_synthetic.py spec-validate \
      --spec $B/synthetic-natural/$r/spec.json
  PYTHONPATH=src uv run python $B/scripts/generate_synthetic.py materialize \
      --spec $B/synthetic-natural/$r/spec.json --out $B/synthetic-natural/$r
done
```

Then the `repo-docwriter` and `repo-auditor` subagents write and audit the docs.
Audit findings and fixes are recorded under
`../llm_injection/runs/stage-b-2026-10-20/audit/`.

## Freeze

After the independent audit and any factual fixes, `scripts/freeze_corpus.py`
hashes every corpus file, spec, prompt and model ID into
`../llm_injection/runs/stage-b-2026-10-20/corpus_freeze.json`. The freeze is
**before** any injector or scoring run. Do not edit these files after the
freeze. `baseline-report` is a diagnostic, never an acceptance gate.
