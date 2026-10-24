# Stage C run — `stage-c-2026-10-20`

**Status:** complete through S7; **provisional engine-only** (no non-author
annotator, OPEN-C9). The corpus is frozen as
`synthetic-natural-stage-c-2026-10-20-v2`; the scope/engine freeze and the corpus
freeze both verify after scoring.

**Result:** **KPI = caught (REFUTED or NEI).** 65/69 verified bundles caught
(`R_detect = 0.942`, repo-cluster 95% CI 0.873–0.986): 50 `REFUTED`, 15 explicit
`NEI`, 4 `none`. Target-line attribution is 39/69 (`R_target = 0.565`, CI
0.476–0.639) and is diagnostic only. Controls 24/24 clean; 0 baseline findings;
3/72 `verify_failed` (tileplan dependency breaks). A defect found through another
mention, or explicitly abstained on, counts as caught. No delta against Stage B
is reported. See `report.md`, `metrics_stage_c.json`, `metrics.md`, and
`verification.json`.

**LLM annotation arm (supplementary):** 3 models (Claude Haiku, GLM Flash,
Qwen Flash), 132 blind rows; κ 1.000 for `claim_type`/`defect_is_real`/
`none_claim_not_extracted`/`control_false_positive`, 0.987 `claim_form`, 0.905
`context_source`, **0.489 `nei_reason_applies`**. 8/15 NEI are judged legitimate;
counting only those, detection is 58/69 = 0.841. No independent labels; see
`annotation_agreement.md` and report T14.

**Normative plan:** `research/submission/demo/validation/stage-c-plan.md`.
**Arm:** **C-ext** — `SCOPE.md` §3.3.2 section-qualified names adopted verbatim
from plan §9.1.

## Sign-off decisions

| id | decision | value |
|---|---|---|
| C1 | scope arm | **C-ext** (section-qualified name adopted) |
| C2 | engine composition | E1 + E2 + E3 + E4 + E5 + E6 + §3.3.2 |
| C3 | docwriter family | `opencode-go/gpt-6-luna` (OpenAI family; not Stage B Claude, not injector DeepSeek) |
| C4 | domains | 3 × 2: geospatial, language, instrument |
| C5 | controls | C-ext: A1–A4 (24) + B (6) + optional C (≤6) |
| C6 | seeds | free choice per document; distribution reported |
| C7 | `doc_side` arm | not run (`n/a`) |
| C8 | capability controls | not pooled; opportunistic only |
| C9 | annotators | **none at sign-off**; provisional engine-only until a non-author annotator exists |
| C10 | C-base fallback | not taken (C1 = C-ext) |
| C11 | protocol §5 | amended: repo-cluster bootstrap replaces Wilson |
| C12 | E6 | implemented, unit-tested, frozen in the engine commit |

The 8 new real-repo `REFUTED` claims found in the pre-S0 precision check are
**accepted as-is** by an explicit operator decision (2026-10-20): they are not
fixed before the freeze. They are not used to select the Stage C corpus, and a
later fix is a new engine version with a new freeze (Stage D).

## S0 artifacts (all hashed in `scope_engine_freeze.json`)

| artifact | path |
|---|---|
| taxonomy | `taxonomy.json` |
| corpus design | `corpus_design.json` |
| control config | `control_config.json` |
| annotation codebook | `annotation_codebook.md` |
| engine-free classifier | `injected_gold/scripts/classify_claim_context.py` |
| freeze tooling | `injected_gold/scripts/freeze_scope_engine.py` |
| prompts | `prompts_natural_c/` |
| prompt provenance | `prompts_natural_c/DIFF.md` |
| judge rubric | `judge_rubric.md` |
| Stage C metrics | `injected_gold/scripts/stage_c_metrics.py` |
| bootstrap | `injected_gold/scripts/bootstrap_repo_cluster.py` |
| checkers | `check_corpus_surface.py`, `check_genres.py`, `check_contamination.py` |
| control selector / sheet | `build_controls.py`, `build_annotation_sheet.py` |
| scope amendment | `validation/SCOPE.md` §3.3.2 |
| protocol amendment | `validation/protocol.md` §5 |

## Freeze verification

```bash
B=research/submission/demo/injected_gold
RUN=$B/llm_injection/runs/stage-c-2026-10-20
PYTHONPATH=src uv run python $B/scripts/freeze_scope_engine.py \
    --verify --freeze $RUN/scope_engine_freeze.json
```

Verify at the four recorded points: before S1, before the injector run, before
scoring, and after scoring. A mismatch aborts; there is no override.

## S1 (next)

Write six specs under `synthetic-natural-c/` from the descriptions in
`corpus_design.json` (architect role, blindness attested), materialise them
deterministically, and re-materialise to an empty diff. No engine run.

## Deviations

See `deviations.md`. Two S0 corrections were made at S1b, before any document
existed: the four agent prompt files were added to the freeze, and the
`repo-docwriter` agent prompt was made presentation-neutral. The implementation
choices recorded in the freeze: `git_commit` is provenance and the **engine tree
hash** is the binding check (research-only commits may advance `HEAD` after the
freeze); `entries.json` + a separate `annotation_sheet_key.jsonl` keep the
target/cross role out of the blind sheet.
