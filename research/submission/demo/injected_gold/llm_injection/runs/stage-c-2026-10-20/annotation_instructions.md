# LLM annotation task — Stage C (supplementary arm)

You are an annotator. You label documentation statements against the
frozen repository; you do **not** see any tool verdict, metric, claim dump, or
the annotation key. Your labels are an LLM supplementary arm, confirmation only.

## Inputs

- Codebook: `annotation_codebook.md` (read it first; it defines every field and
  the decision order).
- Six batch files: `annotation_batches/<repo>.jsonl`. Each line is one row.
- For a **non-control** row, the truth tree is the **injected snapshot** named by
  the row's `snapshot_id`:
  `snapshots/<snapshot_id>__injected/`
- For a **control** row, the truth tree is the clean baseline:
  `synthetic-natural-c/<repo>/`
  (a control's `snapshot_id` is `<repo>__control`; the snapshot is identical to
  the baseline).

The rows carry `old`/`new` (the mutation), the document line, and the injector's
description. The mutation is already applied in the injected snapshot; the
baseline under `synthetic-natural-c/` is **not** the tree to judge a non-control
row against.

**Do not read** `annotation_sheet_key.jsonl`, `entries.json`, `metrics.md`,
`metrics_stage_c.json`, `claims/`, `judge/`, `manifest.jsonl`, or any file under
`injected_gold/llm_injection/runs/stage-c-2026-10-20/` other than this file, the
codebook, the batch files, and the snapshot trees. The snapshot trees contain
only the frozen corpus (documents, source, examples), no tool output.

## What to do

For every row, fill exactly these fields:

| field | allowed values |
|---|---|
| `claim_type` | `current_claim` / `historical` / `illustrative` / `conditional` / `not_a_claim` |
| `claim_form` | `path` / `dependency` / `qualified` / `section_qualified` / `bare_call` / `bare` / `not_a_claim` |
| `context_source` | `heading` / `table` / `prose` / `list` / `path_prose` / `none` |
| `defect_is_real` | `yes` / `no` / `n/a` |
| `nei_reason_applies` | `yes` / `no` / `n/a` |
| `none_claim_not_extracted` | `yes` / `no` / `n/a` |
| `control_false_positive` | `yes` / `no` / `n/a` |
| `same_artifact` | `n/a` for every row in this sheet (the separate attribution sheet is not part of this task) |

Rules of thumb:

- `defect_is_real`: for a non-control row, does the frozen tree contradict the
  line's current claim about the mutated artifact? Controls are `n/a`; for a
  control row use `control_false_positive` instead.
- `nei_reason_applies`: would an abstention be legitimate (bare name with no
  project qualifier, external/foreign symbol, dynamic surface, undecidable
  removal)? `n/a` if the line is not an abstention candidate.
- `none_claim_not_extracted`: is "no claim" the right reaction because the line
  supplies no current-state claim about the artifact? `n/a` otherwise.
- `control_false_positive`: for a control row, is the statement true in the
  frozen tree (so refuting it would be a tool error)? Non-controls are `n/a`.
- `target_claim` is the injector's own description, **not ground truth**. Judge
  the line and the tree yourself.
- A fenced code block is not a claim; a pluralized or external name is not a
  member token; a dunder/builtin/keyword is not a member token.

## Output

For each input batch file, write one JSONL file with the same rows in any order:

`annotations/<annotator>/<repo>.jsonl`

Each line:

```json
{"mention_id": "...", "claim_type": "...", "claim_form": "...",
 "context_source": "...", "defect_is_real": "...",
 "nei_reason_applies": "...", "none_claim_not_extracted": "...",
 "control_false_positive": "...", "same_artifact": "n/a",
 "notes": "short free text"}
```

Cover every `mention_id` exactly once. Do not add commentary to the JSONL.
When done, reply with the six file paths and the row count for each.
