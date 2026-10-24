# Real documentation drift on fresh HEAD — 2026-10-21

Sixteen well-known Python projects, cloned at their default-branch HEAD on
2026-10-21 (full git history, blob-filtered), analysed by the symbolic verifier,
then triaged claim by claim against the checkout and its git history.

| | |
|---|---:|
| repositories | 16 |
| documentation files scanned | 2,275 |
| claims extracted and checked | 68,915 |
| REFUTED claims | 871 |
| findings reviewed by an independent reviewer | 284 |
| **confirmed documentation defects (REAL_DRIFT)** | **32** |
| repositories with at least one confirmed defect | **8 / 16** |

Reviewed set is deliberately biased towards findings the git history can explain
(`EXISTED_AND_DELETED`, `MODULE_PRESENT`, plus every never-existed reference in
README/CONTRIBUTING/DOCS pages), so the 32/284 ratio is not an unbiased corpus
precision estimate — see `triage/summary.json` for the per-stratum breakdown.

Every case below was re-verified by hand against the checkout: the quoted line
was read from the file, the referenced artifact was checked with `find`/`rg`,
and the breaking commit was read from `git log`.

---

## Headline cases

### 1. celery — contributor guide points at a file deleted in 2016

`CONTRIBUTING.rst:1202` and `:1205`:

> adds additional configuration options, then these needs to be documented
> in :file:`docs/configuration.rst`.

- `docs/configuration.rst` does not exist at HEAD; the file is
  `docs/userguide/configuration.rst`.
- Deleted in `86dc8f20` — *"Docs: Moves configuration reference to userguide"*
  (2016-07-09).
- The citing line was rewritten in `d48c347a` — *"Grammatical & punctuation
  fixes for CONTRIBUTING.rst (#5804)"* (2019-10-30), three years after the move.
- Still broken at HEAD 2026-10-21: ten years of a contributor instruction that
  sends people to a nonexistent file.

### 2. sqlfluff — CONTRIBUTING cites a fixtures path that was moved a year earlier

`CONTRIBUTING.md:308`:

> See the required connection parameters in
> `plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles.yml`.

- The fixture now lives at `.../fixtures/dbt/profiles_yml/profiles.yml`
  (`profiles_yml/` directory exists, `profiles.yml` does not).
- The move happened in `286a5268` — *"Fix connection issue for dbt 1.0.0
  (#2230)"* (2022-01-07).
- The current line was written 2023-03-13 — i.e. it cites a path that had
  already been gone for more than a year when it was authored.

### 3. celery — the architecture map describes classes that no longer exist

`docs/internals/app-overview.rst:180-211` is presented as the current module
dependency map, but twelve of its nodes are dead:

| documented symbol | actual state at HEAD |
|---|---|
| `celery.worker.WorkerController` | renamed `WorkController` (`worker/worker.py:64`) |
| `celery.result.BaseAsyncResult` | renamed `ResultBase` (`result.py:62`) |
| `celery.result.TaskSetResult` | gone; task sets replaced by canvas groups |
| `celery.task.sets.TaskSet` | module gone (only an ORM model of that name remains) |
| `celery.worker.control.ControlDispatch` | gone |
| `celery.worker.control.registry.Panel` | collapsed into `celery.worker.control.Panel` |
| `celery.pidbox.BroadcastPublisher` / `.BroadcastConsumer` | `celery/pidbox.py` removed; now `worker/pidbox.py:Pidbox` |
| `celery.bin.worker.WorkerCommand` | CLI is click functions (`def worker()`) |
| `celery.bin.beat.BeatCommand` | click function `beat()` |
| `celery.bin.events.EvCommand` | click function `events()` |
| `celery.bin.amqp.AMQPAdmin` | replaced by `AMQPContext` |

The page was last edited in 2021 (`3cf5072e`), so it has been drifting for years.

### 4. pytest — reference docs point at a module renamed in 2016

`doc/en/reference/reference.rst:796`:

> in ``_pytest.pdb`` which interacts with ``_pytest.capture``

- `src/_pytest/pdb.py` does not exist; the module is `_pytest/debugging.py`.
- Renamed in `05b5554c` — *"Renamed pytest pdb to debugging which conflicts with
  python pdb"* (2016-06-25).

### 5. ruff — CONTRIBUTING path is missing the `rules/` segment

`CONTRIBUTING.md:398`:

> `Settings` in `crates/ruff_linter/src/flake8_unused_arguments/settings.rs`

- The file is at `crates/ruff_linter/src/rules/flake8_unused_arguments/settings.rs`;
  the documented path has never existed.

### 6. dbt-core — API contract calls a deleted handler "the structural template"

`crates/dbt-docs-server/API-CONTRACTS.md:6195` (risk register, present tense):

> The `/api/v1/models` handler
> (`crates/dbt-docs-server/src/handlers/models.rs`) is the structural template

- The whole `src/handlers/` directory was removed in `447e19b1` — *"generate docs
  v2 as a static site queried by DuckDB-WASM"* (2026-08-12).
- `src/lib.rs` now states there is no API at all, and `lists.ts` still names the
  same dead path.

---

## Full confirmed list

| # | repo | claim | location | broke in | class |
|---:|---|---|---|---|---|
| 1 | celery | `docs/configuration.rst` | CONTRIBUTING.rst:1202,1205 | 2016-07-09 `86dc8f20` | path |
| 2 | celery | `docs/include/introduction.txt` | CONTRIBUTING.rst:1467 | never existed (dir is `docs/includes/`) | path |
| 3 | celery | `requirements/doc.txt` | requirements/README.rst:35 | never existed (file is `docs.txt`) | path |
| 4 | celery | `celery.worker.WorkerController` | docs/internals/app-overview.rst:189 | renamed pre-3.0 | symbol |
| 5 | celery | `celery.result.BaseAsyncResult` | docs/internals/app-overview.rst:185 | Celery 4.0 | symbol |
| 6 | celery | `celery.result.TaskSetResult` | docs/internals/app-overview.rst:182 | task sets → groups | symbol |
| 7 | celery | `celery.task.sets.TaskSet` | docs/internals/app-overview.rst:180 | module removed | symbol |
| 8 | celery | `celery.worker.control.ControlDispatch` | docs/internals/app-overview.rst:193 | removed | symbol |
| 9 | celery | `celery.worker.control.registry.Panel` | docs/internals/app-overview.rst:194 | collapsed | symbol |
| 10 | celery | `celery.pidbox.BroadcastPublisher` | docs/internals/app-overview.rst:195 | module removed | symbol |
| 11 | celery | `celery.pidbox.BroadcastConsumer` | docs/internals/app-overview.rst:196 | module removed | symbol |
| 12 | celery | `celery.bin.worker.WorkerCommand` | docs/internals/app-overview.rst:187 | click rewrite | symbol |
| 13 | celery | `celery.bin.beat.BeatCommand` | docs/internals/app-overview.rst:211 | click rewrite | symbol |
| 14 | celery | `celery.bin.events.EvCommand` | docs/internals/app-overview.rst:199 | click rewrite | symbol |
| 15 | celery | `celery.bin.amqp.AMQPAdmin` | docs/internals/app-overview.rst:209 | click rewrite (2020) | symbol |
| 16 | dbt-core | `.gitattributes` | crates/proto-rust/README.md:53 | 2026-06-01 Copybara import | path |
| 17 | dbt-core | `crates/dbt-docs-server/src/handlers/models.rs` | .../API-CONTRACTS.md:6195 | 2026-08-12 `447e19b1` | path |
| 18 | dbt-core | `dbt.nodes.depends_on_macros` | .../API-CONTRACTS.md:2339 | no such column in `NodeRow` | symbol |
| 19 | fastapi | `pydantic>=2.7.0,<3.0.0` (min 2.7) | docs/en/docs/deployment/versions.md:92 | manifest requires `>=2.9.0` | dependency |
| 20 | httpx | `httpx.Mounts(...)` | docs/advanced/transports.md:190 | no such class; `mounts=` is a dict | symbol |
| 21 | pip | `build_env.py` | docs/html/development/architecture/anatomy.rst:69 | now `build_env/` package | path |
| 22 | pip | `pep425tags.py` | docs/html/development/architecture/anatomy.rst:86 | now `utils/compatibility_tags.py` | path |
| 23 | pytest | `_pytest.pdb` | doc/en/reference/reference.rst:796 | 2016-06-25 `05b5554c` | symbol |
| 24 | ruff | `crates/ruff_linter/src/flake8_unused_arguments/settings.rs` | CONTRIBUTING.md:398 | never existed (missing `rules/`) | path |
| 25 | sqlfluff | `plugins/.../fixtures/dbt/profiles.yml` | CONTRIBUTING.md:308 | 2022-01-07 `286a5268` | path |
| 26 | sqlfluff | `aliasing.yml` | test/AGENTS.md:447 | never existed (per-rule `AL01.yml`) | path |
| 27 | sqlfluff | `layout.yml` | test/AGENTS.md:448 | never existed (`LT01.yml`) | path |
| 28 | sqlfluff | `capitalisation.yml` | test/AGENTS.md:449 | never existed (`CP01.yml`) | path |
| 29 | sqlfluff | `convention.yml` | test/AGENTS.md:450 | never existed (`CV01.yml`) | path |
| 30 | sqlfluff | `structure.yml` | test/AGENTS.md:451 | never existed (`ST01.yml`) | path |
| 31 | sqlfluff | `references.yml` | test/AGENTS.md:452 | never existed (`RF01.yml`) | path |
| 32 | sqlfluff | `grammar.rs` | sqlfluffrs/sqlfluffrs_dialects/README.md:20 | generator emits `parser.rs`/`matcher.rs` | path |

---

## What the rest of the REFUTED population was

| label | reviewed | note |
|---|---:|---|
| PREDICATE_FP | 139 | extractor/matcher artefacts: dotted parquet columns read as Python symbols (dbt), build-time generated docs (`docs/rules/*.md` in ruff), external URLs, ambiguous basenames, case folding |
| GENRE_EXAMPLE | 66 | tutorial files the reader creates, `pip freeze` transcripts, placeholders |
| GENERATED_ARTIFACT | 34 | mkdocs/codegen output that is deliberately not committed |
| HISTORICAL | 13 | deprecation lists and migration prose |
| REAL_DRIFT | 32 | the table above |

The dominant systematic error is **dotted identifiers**: 409 `dbt.<table>.<column>`
references in dbt-core's API contract were read as Python symbols (95 findings).
The dominant genre error is **tutorial examples** (fastapi's
`app/routers/*.py`, ruff's mdtest fixtures).

## Reproduction

```bash
RW=research/submission/demo/validation/real_world
PYTHONPATH=src uv run python $RW/scripts/fetch_corpus.py          # clone + pin
PYTHONPATH=src uv run python $RW/scripts/run_corpus.py            # analyse
PYTHONPATH=src uv run python $RW/scripts/attribute_staleness.py   # git attribution
PYTHONPATH=src uv run python $RW/scripts/build_triage_batches.py  # reviewer batches
# reviewer verdicts land in $RW/triage/out/*.jsonl
PYTHONPATH=src uv run python $RW/scripts/merge_triage.py          # precision + confirmed.md
```

Pins, commit dates and the tool commit are in `corpus.lock.json`.
