# Post-score re-score — 2026-10-21

**Question.** Demo-surface changes landed on the engine tree after the Stage C run
was scored (container-ready web server, tolerant zip upload, `find_project_root`
wrapper descent, MCP `repo://summary`, `mcp>=2,<3`). Do any of them move a scored
number?

**Answer: no.** The frozen snapshots were re-scored with the submitted tree
(commit `9067b51`, engine tree `bc6af4f7…`) and every claim dump came back
byte-identical.

## Command

```bash
R=research/submission/demo/injected_gold/llm_injection/runs/stage-c-2026-10-20
OUT=/tmp/rescore
PYTHONPATH=src uv run python \
    research/submission/demo/injected_gold/scripts/score_injections.py \
    --manifest   $R/scoring_manifest.jsonl \
    --snapshots  $R/snapshots \
    --out        $OUT \
    --force
diff -rq $OUT/claims $R/claims
```

`--force` re-runs the engine on both the baseline and the injected snapshot of
every entry (162 runs); `diff -rq` prints nothing.

## Results

| check | frozen | re-run on the submitted tree |
|---|---|---|
| claim dumps | 150 files | **150/150 byte-identical** (`claims.sha256`) |
| detected by refutation | 50 (0.725) | 50 (0.725) |
| abstention rate | 0.217 | 0.217 |
| detection (KPI: refuted + NEI) | 65/69 | 65/69, per-class split unchanged |

`scorer_metrics.json` is the scorer output of this run.

## Why the changes cannot reach the verdict layer

- `core/pipeline.py`: `find_project_root` descends into a wrapper directory only
  when it holds exactly one child **and no files**. Every scored input is a
  repository root with a top-level manifest, so `_looks_like_repo_root` returns on
  the first iteration and the new branch is never reached.
- `core/cli.py`, `webapp/server.py`, `webapp/zip_safe.py`, `mcp_server.py`: the
  `web`/`mcp` subcommands, the upload path and the agent transport. None is
  imported by the claim extractor or the adjudicator.
- No predicate, gate, threshold, vocabulary entry, extraction rule or verdict
  rule differs from the scored tree.

## Real-world rows

Re-ran the three rows the paper and video cite, on the same inputs as
`evidence/real-world/aggregate-2026-10-21.md` (`validation/real_world/repos/`):

| repository | published aggregate | re-run |
|---|---|---|
| sqlfluff | 68 docs / 2175 claims / 16 REFUTED | 68 / 2175 / 16 |
| celery | 204 / 4553 / 34 | 204 / 4553 / 34 |
| httpx | 25 / 1023 / 110 SUPPORTED / 1 REFUTED / 113 NEI, cov 0.50 | identical |

The freeze that covers this tree, and the post-score note that records this
change, are in `../scope_engine_freeze.json` → `postscore_note`.
