# Real-world corpus (demo)

Fresh clones of widely-used Python projects at default-branch HEAD, analysed by
the verifier, with every REFUTED finding attributed to the git history that
explains it and then reviewed by an independent reviewer.

Produces the headline evidence for the demo: **32 confirmed documentation
defects across 8 of 16 popular repositories**, each traceable to the commit that
broke it. See [`findings.md`](findings.md).

## Corpus

`corpus.lock.json` is the single source of truth: repo, URL, HEAD SHA, commit
date, nearest tag and the tool commit, captured at fetch time (2026-10-21).

| repo | HEAD | repo | HEAD |
|---|---|---|---|
| fastapi | `b2ce629` | pip | `9dbd9c3` |
| flask | `d086db8` | black | `287d570` |
| click | `2247b35` | pytest | `49ea4d0` |
| celery | `d6d754e` | mkdocs | `2862536` |
| sqlfluff | `ad1231e` | ruff | `d2d9e8a` |
| dbt-core | `6c62423` | poetry | `20d6940` |
| pydantic | `e3b6f55` | sqlalchemy | `8301bec` |
| httpx | `b5addb6` | aiohttp | `72a735c` |

Clones use `--filter=blob:none --single-branch`: commit and tree history is
local (needed for staleness attribution), file contents are fetched lazily.
`repos/`, `runs/` and `triage/` are gitignored.

## Pipeline

```bash
RW=research/submission/demo/validation/real_world

# 1. clone/pin (idempotent: refresh to origin HEAD if the clone exists)
PYTHONPATH=src uv run python $RW/scripts/fetch_corpus.py [--only celery,pip]

# 2. analyse every repo -> runs/<date>/<repo>/{claims,findings}.jsonl, report.md
PYTHONPATH=src uv run python $RW/scripts/run_corpus.py [--date 2026-10-21]

# 3. attribute each REFUTED finding to its history event -> staleness.jsonl
PYTHONPATH=src uv run python $RW/scripts/attribute_staleness.py [--only celery]

# 4. build reviewer batches (prioritised selection) -> triage/inbox/*.jsonl
PYTHONPATH=src uv run python $RW/scripts/build_triage_batches.py

# 5. reviewers write triage/out/<batch>.jsonl (one verdict per uid)
# 6. merge verdicts -> triage/merged.jsonl, summary.json, confirmed.md
PYTHONPATH=src uv run python $RW/scripts/merge_triage.py
```

## Staleness attribution

`attribute_staleness.py` answers "was this ever real, and who removed it":

| status | meaning |
|---|---|
| `EXISTED_AND_DELETED` / `EXISTED_AND_RENAMED` | the artifact existed; `git log --diff-filter=DR` names the commit, date, subject and rename target |
| `NEVER_EXISTED` | no commit ever contained it — an example/placeholder or a rename the extractor normalised away |
| `MODULE_PRESENT` | the module survives, the symbol does not (symbol-level drift) |
| `PRESENT_NOW` | the object is in the tree, so the verdict is a matcher artefact |
| `CASE_VARIANT` | present with different case (normalisation bug) |

For stale paths the script also blames the citing line, so it can distinguish
"the line predates the removal" from the much stronger "the line was rewritten
*after* the removal and still cites the dead path" (celery, sqlfluff).

## Review protocol

Each reviewer gets a JSONL batch with the claim, the surrounding document
excerpt, refuting evidence and the staleness chain, and labels every item with
exactly one of: `REAL_DRIFT`, `GENRE_EXAMPLE`, `GENERATED_ARTIFACT`,
`PREDICATE_FP`, `HISTORICAL`, `AMBIGUOUS`, plus confidence and evidence. Batches
are grouped by repository; reviewers work read-only against the checkout.

The reviewed set is **not** a uniform sample: it includes every finding that
history says was once real, every symbol-level finding, and every never-existed
path in a README/CONTRIBUTING/DOCS page. Treat `32/284` as a yield on the
prioritised set, not as corpus precision.
`../../evidence/real-world/adjudication-summary.json` carries the per-stratum
and per-predicate breakdown; the full sheet is in `triage/`.

## Results at a glance

- 2,275 docs → 68,915 claims → 871 REFUTED across 16 repos.
- 284 reviewed → 32 `REAL_DRIFT` (8 repos), 139 `PREDICATE_FP`,
  66 `GENRE_EXAMPLE`, 34 `GENERATED_ARTIFACT`, 13 `HISTORICAL`.
- Dominant systematic error: dotted identifiers (dbt parquet columns) read as
  Python symbols. Dominant genre error: tutorial example paths.
