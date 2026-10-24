# Stage B — independent annotation instructions

**Status:** the annotation sheet is produced blank. Independent annotation is not
included; Stage B reports **no independent labels and no IAA**.
Nothing in this file substitutes an LLM label for an independent label.

## What you are annotating

`annotation_sheet.jsonl` contains one row per **verified injection** and one row
per **control**. Each row gives:

- `repo_name`, `class`, `kind`, `mutation_form`;
- `doc_path` and `line`;
- `target` — the exact text on the document line that the injection targets;
- `old` and `new` — the code/manifest change (for a deletion or removal, `new`
  is `null`);
- `symbol` — the bare symbol or dependency name, where applicable;
- `target_claim` — the claim the injector says the change falsifies;
- `control` — `none` for injections, `consistent_present` (or
  `consistent_absent`) for controls.

The sheet deliberately does **not** contain the tool's verdict, layer, reason,
or reaction. Do not open `metrics.md`, `entries.json`, `bootstrap.json`, or the
`claims/` directory, and do not run the tool. Annotate independently.

## Fields

Fill each field with one of the listed values. Leave `nei_reason_applies`,
`none_claim_not_extracted`, and `control_false_positive` as `n/a` when they do
not apply to the row. Do not leave a field blank.

| field | values | meaning |
|---|---|---|
| `claim_type` | `current_claim` / `historical` / `illustrative` / `conditional` / `not_a_claim` | Is the document line a current-state claim about this project's artifact? `historical` = a past release/old name; `illustrative` = a generic example, not this project; `conditional` = depends on an unstated condition; `not_a_claim` = no checkable assertion. |
| `claim_form` | `qualified` / `bare_call` / `bare` / `path` / `dependency` | How the target is written: a dotted/qualified symbol, a call (`name()`), a bare name, a path, or a dependency name. |
| `defect_is_real` | `yes` / `no` | Does the mutation make the document statement false in the repository as frozen? For controls, use `n/a`. |
| `nei_reason_applies` | `yes` / `no` / `n/a` | For rows the tool abstained on: does the abstention reason apply? For example, if the target is a bare name that could be a parameter, builtin, or external symbol, a bare-name abstention applies. |
| `none_claim_not_extracted` | `yes` / `no` / `n/a` | For rows where no claim was formed: was the target genuinely not extracted (as opposed to extracted at a different referent or wrongly supported)? |
| `control_false_positive` | `yes` / `no` / `n/a` | For controls: is a refutation of this row a false positive? |
| `annotator_id` | string | Your identifier (e.g. `A1`, `A2`). |
| `notes` | string | Optional short note; use `""` if none. |

## Streams

- **Miss stream:** rows with no claim formed. Confirm the defect is real and the
  claim was genuinely never extracted.
- **Abstention stream:** rows where the tool formed a claim and abstained.
  Confirm the stated abstention reason applies and that it is not a disguised
  miss.
- **Control stream:** consistent-present/absent rows. Confirm whether a
  refutation would be a false positive.

## IAA

Two annotators work independently on the same sheet. Agreement is reported as
Cohen's κ on `defect_is_real` and `claim_type`, and on each stream field. Target
κ ≥ 0.60; the observed value is reported whatever it is. If only one annotator
is available, no IAA is claimed. If independent annotation is not available, the sheet
stays blank and the limitation is reported.
