# Stage B — held-out natural corpus

**Date:** 2026-10-20
**Branch:** `demo`
**Status:** completed; no independent labels or IAA are claimed here.

Stage B evaluates the **current** tool on a new, frozen, independently audited
natural corpus that was never used to build the tool or the exemplar bank. It
uses the four active injection classes only and reports three outcomes
(`refuted` / `NEI` / `none`). It is held out and was **not** used to tune
prompts, specs, or tool code.

## Headline

| outcome (72 verified injections) | count | rate | repo-cluster 95% CI |
|---|---:|---:|---|
| refuted | 35/72 | **0.486** | [0.375, 0.611] |
| NEI (claim formed, abstained) | 7/72 | 0.097 | [0.042, 0.167] |
| none (no refutation/abstention) | 30/72 | 0.417 | [0.278, 0.569] |

`none` is not one thing: **16** no claim on the target line, **8** a claim at a
different referent, **6** a formed target claim wrongly `SUPPORTED`.

| class | n | refuted | NEI | none | refutation |
|---|---:|---:|---:|---:|---:|
| `path-location-drift` | 18 | 18 | 0 | 0 | **1.000** |
| `external-dependency-drift` | 18 | 14 | 0 | 4 | **0.778** |
| `identifier-drift` | 18 | 1 | 1 | 16 | **0.056** |
| `removed-referent-drift` | 18 | 2 | 6 | 10 | **0.111** |

Controls: **18/18 clean (0 false positives)**, but only 13 controls formed a
supported claim; 1 was `NEI`, 2 had no claim, and 2 had another referent.
Precision is therefore 1.0 on a small, partly unconsumed control set.

Baseline: **0 `REFUTED`** claims across the six frozen baselines (260 claims;
182 `SUPPORTED`, 78 `NEI`). There were no baseline findings to adjudicate.
This is a clean-by-construction corpus, not evidence of real-world precision.

## What is in this directory

- **`report.md`** — full design, results, caveats, and what B does not establish.
- **`metrics.md`** — compact three-outcome, per-class, per-form, control, and
  bootstrap tables.
- **`PREREGISTRATION.md`** — the hypotheses and stop rules, written before
  corpus generation.
- **`corpus_freeze.json`** — SHA-256 of 71 corpus files, 8 prompts, 4 agent
  prompts, and the exact model IDs. Aggregate:
  `0a739f4ef52b62db0041b8ff36fde5ac22be00b50fea1fc1f9ff5c11e713ca41`.
- **`manifest.jsonl`** — 72 verified injections, one per snapshot.
- **`provenance.json`** — per-bundle prompt hash, model ID, seed, exemplar IDs,
  and verifier result.
- **`controls.jsonl`** — 18 engine-free consistent-present controls.
- **`entries.json`** — per-entry outcome, `none` sub-flag, and matched finding.
- **`bootstrap.json`** — repo-cluster bootstrap results.
- **`baseline_findings.json`** / **`baseline_summary.json`** — baseline record.
- **`annotation_sheet.jsonl`** / **`ANNOTATION.md`** — the blind
  annotation sheet (90 rows) and instructions.
- **`audit/`** — independent audit trail and the recipecard fixes.
- **`prompts_natural/`** — the frozen docwriter/auditor/injector prompts.
- **`HARNESS_FIX.md`** — the two pre-scoring harness/oracle fixes (55 → 70 → 72
  verified) and why they are not prompt/spec/tool tuning.
- **`ENGINE_FOLLOWUPS.md`** — prioritized post-B engine work. Bare-name policy
  unchanged; real refutation fixes are +4 (35 → 39/72); extraction fixes move
  `none` → `NEI`/`SUPPORTED`, not `REFUTED`. It also links the post-hoc trial
  below.
- **`regression-context-qualification/`** — post-hoc trial of module-context
  qualification: **68/72 (0.944)** on the frozen snapshots, 0 baseline/control
  false positives, 9/68 refutations off the target line. This is **not** the
  Stage B headline; adoption requires a `SCOPE.md` decision and a new held-out
  evaluation.
- **`regression-trial-plus-e1e2/`** — the same trial plus the E1/E2 dependency
  fixes: **72/72 credited**, **63/72 target-line**, controls 18/18, baseline 0.
  The real-repo precision audit found the symbol rule nearly dormant and E1
  amplifying migration/compatibility false positives; E6 is the new precision
  gate. Post-hoc only, not a new held-out headline.
- **`regression-trial-e1e2-e6/`** — final post-hoc state with E6: Stage B stays
  **72/72 credited / 63/72 target-line**, controls 18/18, baseline 0; targeted
  real-repo FPs drop (fastapi 75→55, prefect 7→6, sklearn 30→26) without
  changing Stage B. Post-hoc only.

## Provenance

| role | model |
|---|---|
| architect | `opencode-go/claude-haiku-5-5` |
| docwriter | `opencode-go/claude-haiku-5-5` |
| auditor | `opencode-go/qwen3.8-flash` (GPT-6 region-blocked; recorded substitution) |
| injector | `opencode-go/deepseek-v4.1-flash` |

Docwriter and injector are different model families; the auditor is a third
family. Independent annotation is pending. See `report.md` §2 and §8.

## Caveats in one paragraph

The corpus is synthetic and small (6 repos, 3 domains). The 72 entries are not
72 independent claims: path has 6 distinct targets, external 8, identifier 15,
removed-referent 14. Six of the 35 refutations come from a document mention
other than the recorded target line. The symbol classes are dominated by bare
names; many produce no claim at all, and the few refutations cluster on one
qualified `read_json` mention. The controls show 0 false positives but four
controls were not extracted. There are no independent labels. See `report.md` §9–§10.
