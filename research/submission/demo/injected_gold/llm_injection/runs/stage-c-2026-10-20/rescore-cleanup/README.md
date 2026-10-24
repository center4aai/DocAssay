# Public-artifact re-score — 2026-10-24

**Question.** The public-artifact cleanup touched the protocol, the agent
prompts, the freeze tooling and several analysis scripts, and one engine comment
changed in the code tree. Do any of these edits move a scored number?

**Answer: no.** The frozen snapshots were re-scored with the cleaned tree and all
150 claim dumps came back byte-identical. `metrics.md` is also byte-identical;
`metrics.json` differs only in the `date`, `seed` and engine-path metadata that
the scorer records, not in any metric value.

## Command

```bash
R=research/submission/demo/injected_gold/llm_injection/runs/stage-c-2026-10-20
OUT=/tmp/stage-c-cleanup
PYTHONPATH=src uv run python \
    research/submission/demo/injected_gold/scripts/score_injections.py \
    --manifest  $R/scoring_manifest.jsonl \
    --snapshots $R/snapshots \
    --out       $OUT \
    --force
```

`claim dumps` below means `$OUT/claims/*.jsonl` compared with the shipped
`$R/claims/*.jsonl`.

## Results

| check | frozen | re-run on the cleaned tree |
|---|---|---|
| claim dumps | 150 files | **150/150 byte-identical** (`claims.sha256`) |
| detected by refutation | 50 (0.725) | 50 (0.725) |
| abstention rate | 0.217 | 0.217 |
| detection (KPI: refuted + NEI) | 65/69 | 65/69, per-class split unchanged |
| `metrics.md` | tracked | byte-identical |

`metrics.md`, `metrics.json` and `metrics_stage_c.json` in this directory are the
scorer outputs of the re-run.

## Why the changes cannot reach the verdict layer

- The engine change is a comment in `tests/test_extraction_gaps.py`; no predicate,
  gate, threshold, vocabulary entry, extraction rule or verdict rule differs.
- The research edits are path renames, neutral wording and absolute-path
  normalisation. They change no input that the scorer reads.
- The freeze is rebuilt on the tree that is actually published; see
  `../scope_engine_freeze.json` → `cleanup_note`.
