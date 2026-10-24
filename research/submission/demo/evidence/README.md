# Evidence map — every reported number, and where it lives

This directory is a **curated copy**. The authoritative run is
`injected_gold/llm_injection/runs/stage-c-2026-10-20/`; the copies here exist so a
reader can check the reported numbers without walking the run tree. If a copy
and the run ever disagree, the run wins — they are byte-identical at commit time.

---

## 1. Stage C — injection-based conformance

| reported number | value | file | field / table |
|---|---|---|---|
| planned injections | 72 | `stage-c/report.md` T9 | `planned` |
| verified injections | 69 (0.958) | `stage-c/report.md` T9 | `verified` |
| detected (`R_detect`) | **65/69 = 0.942**, CI [0.873, 0.986] | `stage-c/report.md` T2 | `detected`, `R_detect` |
| decomposition | 50 `REFUTED` (0.725) / 15 `NEI` / 4 `none` | `stage-c/report.md` T2 | same row |
| attribution (`R_target`) | 39/69 = 0.565, CI [0.476, 0.639] | `stage-c/report.md` T2 | diagnostic only |
| per class | path 0.778 · dependency 1.000 · identifier 1.000 · removed-referent 1.000 | `stage-c/report.md` T3 | `R_detect` |
| assertion-level detail | — | `stage-c/metrics_stage_c.json` | `overall`, `by_class` |
| effective sample | 46 distinct (repo, artifact) of 69 entries | `stage-c/report.md` T13 | `distinct` |
| baseline findings | 0 `REFUTED` on six clean baselines | `stage-c/report.md` T12 | — |
| controls | 24 evaluated, 0 refuted; shortfalls reported | `stage-c/report.md` T11 | `specificity` |

**Attribution caveat carried into the reported results.** `identifier-drift` has
`R_target = 0.111` (2/18): the drift is caught through another mention of the
same artifact or by an explicit `NEI`, not on the recorded line. The report says
so in the same row; it is not a miss count.

## 2. LLM annotation arm (confirmation only)

| number | value | file |
|---|---|---|
| annotators | `claude-haiku-5-5`, `glm-5.3-flash`, `qwen3.8-flash` | `stage-c/annotation_agreement.md` |
| rows | 132 (69 target + 39 cross-mention + 24 controls) | same, `coverage` |
| agreement `claim_type` / `claim_form` / `context_source` | κ 1.000 / 0.987 / 0.905 | same |
| agreement `defect_is_real` | κ 1.000 (105/105) | same |
| agreement `nei_reason_applies` | **κ 0.489** | same |
| legitimate `NEI` | 8/15 | same, `nei_legitimate_yes` |
| conservative detection | **58/69 = 0.841** | `stage-c/report.md` T14 |

Both `0.942` and `0.841` are reported. The arm is labelled **supplementary**: it
uses language models, and the sheet is blind to the tool's verdict
but not to the mutation record. See `stage-c/annotation_codebook.md` and
`stage-c/annotation_sheet.jsonl`.

## 3. Real repositories (confirmed drift and its cost)

| number | value | file |
|---|---|---|
| repositories | 16 Python projects, pinned by commit | `../validation/real_world/corpus.lock.json` |
| documents / claims | 2 275 / 68 915 | `real-world/aggregate-2026-10-21.md` |
| resolved claims | 4 394 | same |
| `REFUTED` candidates | 871 | same |
| adjudicated sample | 284 | `real-world/adjudication-summary.json` |
| **confirmed drift** | **32 (11.3 %)** | `real-world/confirmed.md` |
| predicate false positive | 139 | `real-world/adjudication-summary.json` |
| tutorial / illustrative example | 66 | same |
| generated artifact | 34 | same |
| historical statement | 13 | same |

Per repository (`confirmed`): celery 15, sqlfluff 8, dbt-core 3, pip 2,
ruff 1, fastapi 1, pytest 1, httpx 1.

Adjudication is **not** an LLM label: each candidate was checked against the
current tree and `git log` / `git blame`, and `confirmed.md` records the
evidence and the commit that introduced the drift. Every confirmed entry names
a file, a line, the deleted or renamed referent, and the commit that moved it.
The per-repo clones are not redistributed (they are reproducible from
`corpus.lock.json`); the per-repo findings and the triage sheet are tracked in
`validation/real_world/runs/` and `validation/real_world/triage/`.

## 4. Freeze and provenance

| item | value | file |
|---|---|---|
| **scored** engine tree | `21ac874c78f80ccdfa597dea824d4ff37f098f92` | `stage-c/verification.json` → `identifier_update` |
| **scored** scope/engine freeze | aggregate `043f45af2a8d…`, 131 files | same |
| **identifier-update** engine tree | `bdec549f5665c31653319d93541590e753f5eaba`, aggregate `59cbfe105c80…` | same |
| **pre-release** engine tree | `bc6af4f78d83440a20f69215767488a3f49f300a` | `stage-c/verification.json` → `postscore` |
| **release** engine tree | `877b681596112d37d4937bb099514e497872508c` | `stage-c/verification.json` → `release` |
| **release** scope/engine freeze | aggregate `db5b7520…`, 132 files | run's `scope_engine_freeze.json` → `release_note` |
| **packaging** scope/engine freeze | aggregate `dc1a943e…`, 132 files, `--verify` passes | run's `scope_engine_freeze.json` → `packaging_note` |
| **cleanup** scope/engine freeze | aggregate `50c0e9f6…`, 132 files, `--verify` passes | run's `scope_engine_freeze.json` → `cleanup_note` |
| corpus freeze | `synthetic-natural-stage-c-2026-10-20-v2`, aggregate `5cbfa8893d1b…`, 78 files | `stage-c/verification.json` |
| verification points | before S1, before injection, before scoring, **after scoring**, after the re-freeze, **release** — all `pass` | same |
| identifier update | identifier-only; no predicate, threshold, vocabulary entry, gate or verdict rule changed | `stage-c/verification.json` → `identifier_update` |
| demo-surface re-freeze | decision path unchanged; 150/150 claim dumps reproduce byte-identically | `stage-c/verification.json` → `postscore` |
| release re-freeze | decision path unchanged; 150/150 claim dumps reproduce byte-identically | `stage-c/verification.json` → `release` |
| cleanup re-freeze | decision path unchanged; 150/150 claim dumps reproduce byte-identically | `stage-c/verification.json` → `cleanup` |
| deviations | 19 entries, including the KPI amendment, the identifier update, the demo-surface re-freeze, the release cleanup and the artifact cleanup | `stage-c/deviations.md` |

**Why six freezes.** The scored run is bound to `21ac874c…`. The rename
changed every module that imports the package, so a content hash taken before it
cannot match the final tree. The demo-surface changes (web server, zip
upload, `find_project_root` wrapper descent, MCP summary, `mcp>=2`) touch
`engine_code`/`environment` without touching the verdict layer. The
release cleanup (dead code removal, legacy naming, packaging) touches the
same groups. The packaging cleanup moves the artifact into the public tree and
neutralises annotation wording; it edits the protocol, the plan, the annotation
documents and three annotation scripts, so the freeze is rebuilt again. The
artifact cleanup moves the private staging out, renames the tree and neutralises
wording and paths; it edits the protocol, the agent prompts, the freeze tooling
and analysis scripts, so the freeze is rebuilt once more. Each
time the freeze was rebuilt on the final tree, so that
`--verify` is meaningful for the artifact. The proof that the scored engine was
not otherwise changed is the scored tree hash plus, for the demo-surface,
release and packaging re-freezes, an engine re-run:
`score_injections.py --force` on the frozen snapshots reproduces **all 150 claim
dumps byte-identically** and the same 65/69, and the cited real-world rows
reproduce (sqlfluff 68/2175/16, celery 204/4553/34, httpx 25/1023/110-1-113).
Evidence: `runs/stage-c-2026-10-20/rescore-2026-10-21/`,
`runs/stage-c-2026-10-20/rescore-publicrelease/` and
`runs/stage-c-2026-10-20/rescore-cleanup/`; the packaging and cleanup re-runs were
checked against the shipped claims at packaging time.

## 5. How to regenerate

The experiment-by-experiment matrix (what is byte-identical, what needs the
network, and what is not bit-reproducible) is in `../REPRODUCING.md`.

```bash
uv run pytest -q                                     # 659 passed, 11 xfailed
B=research/submission/demo/injected_gold
RUN=$B/llm_injection/runs/stage-c-2026-10-20
PYTHONPATH=src uv run python $B/scripts/freeze_scope_engine.py --verify --freeze $RUN/scope_engine_freeze.json
PYTHONPATH=src uv run python $B/scripts/freeze_corpus.py      --verify --freeze $RUN/corpus_freeze.json
PYTHONPATH=src uv run python $B/scripts/stage_c_metrics.py    --run $RUN
```
