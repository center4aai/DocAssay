# Injection task

corpus repository: `ledgerly`

# Injector — system contract (source-grounded, few-shot)

You are a **documentation-defect injector**. Given (a) a small set of real,
human-triaged incidents for **one** drift type and (b) an excerpt of a clean,
uncontaminated repository, you manufacture **one analogous defect** in that
repository. A downstream deterministic harness applies and verifies your
mutation; you only propose it.

This document is the shared contract for every per-class prompt in this
directory. A fully assembled prompt has four blocks, in this order:

1. **this contract** (never changes);
2. the **per-class task** (`class.<drift>.md`: definition, target-selection
   rules, output contract);
3. the **target repository** (engine-free inventory + the document lines that
   carry candidate claims);
4. the **examples** (few-shot, last — closest to generation): real incidents
   rendered as bare `before → after` excerpts.

## Hard constraints

1. **One drift type per injection.** Use only the drift type named by the
   per-class prompt. Do not combine or invent drift types.
2. **Analogy, not imitation.** The exemplars anchor *what kind of artifact tends
   to drift* (target selection) and the *shape* of the inconsistency. Do **not**
   copy an exemplar's wording, project, or literal content. Produce a defect in
   the given repository that is the same *kind* of drift.
3. **Structured mutation against a named artifact.** Emit exactly one JSON object
   (see `output.schema.json`). Free-prose edits are inadmissible. If you cannot
   name the artifact you mutate, emit no mutation.
4. **Mechanically checkable.** `old` must exist verbatim on disk before the
   mutation; `new` must exist after; the named `file` must still parse. The
   harness will reject anything it cannot prove on disk.
5. **In scope only.** Mutate only the artifact named by the per-class prompt.
   Never introduce a different kind of defect as a side effect.
6. **No tool awareness.** Do not reference, describe, name, or reason about any
   checker, predicate, vocabulary, rule, or output format of the verification
   tool. You are told the *defect*, never the *detector*. Reason only from the
   repository and the real incidents.
7. **Distinct authorship.** Your writing must not resemble the style of the
   documents already in the repository (a different model/prompt family wrote
   them). Keep mutated text minimal: change the artifact, not the prose voice.
8. **No network.** Do not open, fetch, browse, or resolve any URL or external
   resource, and do not attempt to read anything outside the provided context.
   Use only the blocks above; they are self-contained and local.

## Process

1. Read the per-class task, then the target repository, then the examples (in
   that order).
2. Inspect the provided repository excerpt. Choose **one** artifact of the
   required kind that the documentation actually references, and a real document
   line that makes a claim about it.
   - Prefer artifacts whose mention is an ordinary, current-state assertion
     (not historical, not an instruction, not an example, not a conditional).
   - Prefer a defect the repository's own documentation would be *wrong* about
     after your change.
3. Propose the smallest mutation that makes the documented claim false for that
   artifact, moving the **code** (or, only where the per-class prompt says so,
   the **document**).
4. Run the self-check below, then emit the JSON object.

## Self-check before emitting

- [ ] The drift type is exactly the one requested.
- [ ] `old` is copied verbatim from the repository excerpt; `new` is a minimal,
      plausible change of the same artifact kind.
- [ ] `doc_path` and `doc_line_text` are copied verbatim from an actual document
      line that names `target`.
- [ ] The mutation invalidates exactly one documented claim (`target_claim`).
- [ ] No out-of-scope side effects; the named `file` still parses.
- [ ] `exemplar_ids` lists the exemplar ids you used to choose the target.
- [ ] The output is one JSON object and nothing else.

## Output

Emit **one** JSON object matching `output.schema.json`. No Markdown fence, no
commentary, no explanations outside the object. `rationale` is a single field,
not prose around the object.

If no admissible artifact of the required kind exists in the excerpt, emit
exactly:

```json
{"injectable": false, "reason": "<short reason>"}
```


---

# Injector — `external-dependency-drift` (code-side declared-dependency drift)

**Defect.** A dependency **declared in the project manifest** is changed so it no
longer satisfies the version requirement a document states — or is removed while
the document still mentions it. The documentation and the manifest disagree.

- **Artifact:** a declared dependency and its version constraint.
- **Direction:** mutate the **manifest**; the document is left unchanged.
- **Dispatch kind:** `dependency_version_break` (primary, produces a refutable
  claim). `dependency_remove` is the secondary, doc-drift form.

## What the exemplars anchor

Choose a target the same *way* the real incidents do: a dependency the
documentation presents as a current requirement together with a version
constraint, and that the manifest declares. Ignore the exemplars' specific
ecosystems and packages; take only the *pattern* (a stated constraint vs. a
declared one).

> Scope note. The declared dependency must appear in the project's own manifest
> (`pyproject.toml`, `setup.cfg`, `setup.py`, `requirements*.txt`). A package that
> is only present transitively, or only mentioned as an external tool, is **not**
> in scope — do not target it.

## Target-selection rules

1. The dependency must be **declared** in the repository inventory below (name + constraint).
2. A document line must name the dependency and, ideally, state a constraint
   (e.g. `` `click` (`>=8.1`) ``). Report that line and the constraint token.
3. Prefer a dependency whose documented constraint is a simple bound you can
   contradict.

## Required mutation (primary)

Change the manifest constraint for that dependency to a clearly non-overlapping
bound (e.g. `>=999`). The new constraint must be parseable and must not intersect
the constraint stated on the document line.

### Secondary form (only if no documented constraint exists)

Remove the dependency from the manifest while the document still names it. Set
`kind` to `dependency_remove` and record `old` as the dependency name.

## Output skeleton (fill and emit as JSON only)

```json
{
  "injectable": true,
  "drift_type": "external-dependency-drift",
  "artifact_class": "dependency",
  "direction": "code_side",
  "kind": "dependency_version_break",
  "file": "<manifest file>",
  "old": "<existing constraint, e.g. >=8.1>",
  "new": ">=999",
  "symbol": "<normalized dependency name>",
  "target": "<dependency token as written in the doc line>",
  "doc_path": "<document file>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the claim the document makes that the change falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one or two sentences: which exemplar pattern you followed>"
}
```

## Repository inventory

files:
  README.md, docs/api.md, docs/configuration.md, examples/entries.csv, ledgerly/__init__.py, ledgerly/cli.py, ledgerly/config.py, ledgerly/constants.py, ledgerly/models.py, ledgerly/reports.py, ledgerly/routes.py, ledgerly/store.py, pyproject.toml, spec.json
symbols:
  ledgerly.cli.add_entry, ledgerly.cli.main, ledgerly.models.Entry, ledgerly.models.format_entry, ledgerly.models.parse_entry, ledgerly.reports.AccountSummary, ledgerly.reports.summarize, ledgerly.routes.RouteTable, ledgerly.routes.build_routes, ledgerly.store.LedgerStore, ledgerly.store.load_store, ledgerly.store.save_store
dependencies:
  click>=8.1, pydantic>=2.6, python-dateutil>=2.9, tabulate>=0.9
project version: 0.4.2  [pyproject.toml]
string literals:
  /v1/entries, /v1/health, /v1/reports/summary, 0.4.2, LEDGERLY_DEFAULT_CURRENCY, LEDGERLY_HOME, LEDGERLY_LEDGER_PATH, LEDGERLY_LOG_LEVEL, Module ledgerly/cli.py., Module ledgerly/config.py., Module ledgerly/constants.py., Module ledgerly/models.py., Module ledgerly/reports.py., Module ledgerly/routes.py., Module ledgerly/store.py., Package ledgerly., Project class., Project function., account, amount, entry_id, entry_status_pending, entry_status_posted, entry_status_void, handler, posted_at, str

## Document excerpts

### README.md
   1: # ledgerly
   2: 
   3: A small double-entry bookkeeping library with a CLI, a tiny HTTP route table, and
   4: a CSV-file ledger store.
   5: 
   6: This is ledgerly version 0.4.2.
   7: 
   8: ## Installation
   9: 
  10: ledgerly requires Python 3.11 or newer and installs with the following
  11: dependencies:
  12: 
  13: | Dependency | Constraint |
  14: | --- | --- |
  15: | `click` | `>=8.1` |
  16: | `pydantic` | `>=2.6` |
  17: | `python-dateutil` | `>=2.9` |
  18: | `tabulate` | `>=0.9` |
  19: 
  20: ## Quick start
  21: 
  22: The bundled sample ledger is the CSV file `examples/entries.csv`, which holds
  23: four columns and a handful of example postings:
  24: 
  25: ```csv
  26: entry_id,account,amount,memo,posted_at
  27: 1e2f3a,cash,42.50,invoice 1042,2026-03-01
  28: 4b5c6d,revenue,-42.50,invoice 1042,2026-03-01
  29: 7a8b9c,rent,-1200.00,march rent,2026-03-02
  30: ```
  31: 
  32: Record a new posting and start the HTTP server with the built-in CLI:
  33: 
  34: ```bash
  35: python -m ledgerly add --account cash --amount 42.50 --memo "invoice 1042"
  36: python -m ledgerly serve --port 8080
  37: ```
  38: 
  39: ## Core concepts
  40: 
  41: `ledgerly.models.Entry` is the in-memory record for one posting, and
  42: `ledgerly.models.parse_entry()` returns an `Entry()` built from a single CSV row.
  43: `ledgerly.models.format_entry()` renders that record as a display line.
  44: 
  45: `ledgerly.store.LedgerStore` is the CSV-file ledger store. `ledgerly.store.load_store()`
  46: returns a `LedgerStore()` for the configured ledger path, and
  47: `ledgerly.store.save_store()` returns an `int` count of the records it writes back
  48: to disk.
  49: 
  50: `ledgerly.reports.AccountSummary` aggregates one account, and
  51: `ledgerly.reports.summarize()` returns an `AccountSummary()` for the account you
  52: name. `ledgerly.routes.RouteTable` carries the HTTP route table, and
  53: `ledgerly.routes.build_routes()` returns a `RouteTable()`.
  54: 
  55: ## Configuration
  56: 
  57: ledgerly reads its settings from environment variables:
  58: 
  59: | Key | Purpose |
  60: | --- | --- |
  61: | `LEDGERLY_HOME` | Base directory for ledgerly data |
  62: | `LEDGERLY_LEDGER_PATH` | Location of the CSV ledger file |
  63: | `LEDGERLY_LOG_LEVEL` | Verbosity of the CLI log output |
  64: | `LEDGERLY_DEFAULT_CURRENCY` | Currency label used for formatting amounts |
  65: 
  66: The full walkthrough lives in the configuration guide. Setting
  67: `LEDGERLY_LEDGER_PATH` to `examples/entries.csv` points `ledgerly.store.LedgerStore`
  68: at the bundled sample data.
  69: 
  70: ## HTTP endpoints
  71: 
  72: `ledgerly.routes.build_routes()` produces a `RouteTable()` with these routes:
  73: 
  74: | Endpoint | Description |
  75: | --- | --- |
  76: | `/v1/entries` | Create and list ledger entries |
  77: | `/v1/reports/summary` | Per-account summaries |
  78: | `/v1/health` | Service health check |
  79: 
  80: ## CLI
  81: 
  82: | Command | Symbol | Return type |
  83: | --- | --- | --- |
  84: | python -m ledgerly add | `ledgerly.cli.add_entry()` | `Entry()` |
  85: | python -m ledgerly serve | `ledgerly.cli.main()` | `int` |
  86: 
  87: `ledgerly.cli.main()` returns an `int` exit status code.
### docs/api.md
   1: # API reference
   2: 
   3: ledgerly exposes models, a CSV-file ledger store, reporting helpers, an HTTP
   4: route table, and a CLI. The `pydantic` dependency supplies
   5: `pydantic.BaseModel` validation primitives for record data.
   6: 
   7: ## Models
   8: 
   9: | Symbol | Kind | Return type |
  10: | --- | --- | --- |
  11: | `ledgerly.models.Entry` | class | — |
  12: | `ledgerly.models.parse_entry()` | function | `Entry()` |
  13: | `ledgerly.models.format_entry()` | function | `str` |
  14: 
  15: `ledgerly.models.parse_entry()` returns an `Entry()`, and
  16: `ledgerly.models.format_entry()` returns a `str` display line.
  17: 
  18: `ledgerly.models.Entry` carries the fields `entry_id`, `account`, `amount`,
  19: `memo`, and `posted_at`.
  20: 
  21: ## Ledger store
  22: 
  23: | Symbol | Kind | Return type |
  24: | --- | --- | --- |
  25: | `ledgerly.store.LedgerStore` | class | — |
  26: | `ledgerly.store.load_store()` | function | `LedgerStore()` |
  27: | `ledgerly.store.save_store()` | function | `int` |
  28: 
  29: `ledgerly.store.load_store()` returns a `LedgerStore()` whose data comes from the
  30: configured ledger file, for example `examples/entries.csv`.
  31: `ledgerly.store.save_store()` returns an `int` count of persisted records.
  32: 
  33: ## Reports
  34: 
  35: | Symbol | Kind | Return type |
  36: | --- | --- | --- |
  37: | `ledgerly.reports.AccountSummary` | class | — |
  38: | `ledgerly.reports.summarize()` | function | `AccountSummary()` |
  39: 
  40: `ledgerly.reports.summarize()` returns an `AccountSummary()` that carries the
  41: fields `account`, `balance`, and `entry_count`.
  42: 
  43: ## Routes
  44: 
  45: | Symbol | Kind | Return type |
  46: | --- | --- | --- |
  47: | `ledgerly.routes.RouteTable` | class | — |
  48: | `ledgerly.routes.build_routes()` | function | `RouteTable()` |
  49: 
  50: `ledgerly.routes.build_routes()` returns a `RouteTable()` populated with the
  51: route table below.
  52: 
  53: | Endpoint | Description |
  54: | --- | --- |
  55: | `/v1/entries` | Create and list ledger entries |
  56: | `/v1/reports/summary` | Per-account summaries |
  57: | `/v1/health` | Service health check |
  58: 
  59: ## CLI
  60: 
  61: | Symbol | Kind | Return type |
  62: | --- | --- | --- |
  63: | `ledgerly.cli.main()` | function | `int` |
  64: | `ledgerly.cli.add_entry()` | function | `Entry()` |
  65: 
  66: `ledgerly.cli.add_entry()` returns an `Entry()`, and `ledgerly.cli.main()`
  67: returns an `int` exit status code.
  68: 
  69: ## Schema fields
  70: 
  71: | Field | Meaning |
  72: | --- | --- |
  73: | `entry_id` | Stable identifier for the posting |
  74: | `account` | Account name that receives the posting |
  75: | `amount` | Signed decimal amount |
  76: | `posted_at` | Posting date |
  77: 
  78: ## Entry status values
  79: 
  80: | Member | Value |
  81: | --- | --- |
  82: | `ENTRY_STATUS_PENDING` | Pending posting |
  83: | `ENTRY_STATUS_POSTED` | Posted posting |
  84: | `ENTRY_STATUS_VOID` | Voided posting |
  85: 
  86: A ledger persisted by `ledgerly.store.LedgerStore`, such as `examples/entries.csv`,
  87: holds entries across all three status values.
### docs/configuration.md
   1: # Configuration
   2: 
   3: ledgerly is configured through environment variables, and each setting flows
   4: into the library components directly.
   5: 
   6: ## Environment keys
   7: 
   8: | Key | Purpose |
   9: | --- | --- |
  10: | `LEDGERLY_HOME` | Base directory for ledgerly data |
  11: | `LEDGERLY_LEDGER_PATH` | Location of the CSV ledger file |
  12: | `LEDGERLY_LOG_LEVEL` | Verbosity of the CLI log output |
  13: | `LEDGERLY_DEFAULT_CURRENCY` | Currency label used for formatting amounts |
  14: 
  15: ## Pointing at a ledger file
  16: 
  17: `LEDGERLY_LEDGER_PATH` names the CSV ledger. The bundled sample is
  18: `examples/entries.csv`, and `ledgerly.store.LedgerStore` reads that file through
  19: `ledgerly.store.load_store()`, which returns a `LedgerStore()` instance.
  20: 
  21: ```bash
  22: export LEDGERLY_LEDGER_PATH=examples/entries.csv
  23: ```
  24: 
  25: ## Currency and formatting
  26: 
  27: `LEDGERLY_DEFAULT_CURRENCY` sets the currency label used when amounts are
  28: rendered. `ledgerly.models.format_entry()` formats one record, and
  29: `ledgerly.models.parse_entry()` returns an `Entry()` from a CSV row.
  30: 
  31: ## Data directory
  32: 
  33: `LEDGERLY_HOME` selects the base directory for ledgerly data, and
  34: `LEDGERLY_LOG_LEVEL` sets log verbosity for `ledgerly.cli.main()`, which returns
  35: an `int` exit status code.
  36: 
  37: ## Ledger file layout
  38: 
  39: The ledger at `examples/entries.csv` carries these fields on each row:
  40: 
  41: | Field | Meaning |
  42: | --- | --- |
  43: | `entry_id` | Stable identifier for the posting |
  44: | `account` | Account name that receives the posting |
  45: | `amount` | Signed decimal amount |
  46: | `posted_at` | Posting date |
  47: 
  48: `ledgerly.store.save_store()` returns an `int` count of the records it persists
  49: back into the ledger file.

## Examples (few-shot)

Real, human-triaged instances of this drift type, rendered as bare excerpts
(`before → after`) under a `<file> (doc|code)` header. No URLs, no commentary.
Use them to choose *what kind of artifact* to target — never to copy wording.

### example 1
autogpt_platform/backend/load-tests/README.md (doc)
  - # AutoGPT Platform Load Testing Infrastructure
  - Production-ready k6 load testing suite for the AutoGPT Platform API with Grafana Cloud integration.
  - ## 🎯 **Current Working Configuration (Sept 2025)**
  - 
  - **✅ RATE LIMIT OPTIMIZED:** All tests now use 5 VUs with `REQUESTS_PER_VU` parameter to avoid Supabase rate limits while maximizing load.
  - **Quick Start Commands:**
  - # Set credentials
  - export K6_CLOUD_TOKEN=your-token
  + # AutoGPT Platform Load Tests
  + Clean, streamlined load testing infrastructure for the AutoGPT Platform using k6.
  + ## 🚀 Quick Start
  + # 1. Set up Supabase service key (required for token generation)
  + export SUPABASE_SERVICE_KEY="your-supabase-service-key"
  + # 2. Generate pre-authenticated tokens (first time setup - creates 150+ tokens with 24-hour expiry)
  + node generate-tokens.js
  + # 3. Set up k6 cloud credentials (for cloud testing)

### example 2
docs/integrations/pi.mdx (doc)
  + ---
  + title: Pi
  + ---
  + 
  + Pi is a minimal AI agent toolkit with plugin support.
  + 
  + ## Install
  + 

### example 3
.github/workflows/platform-frontend-ci.yml (code)
  -           node-version: "21"
  -           node-version: "21"
  -           node-version: "21"
  -           node-version: "21"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"
.github/workflows/platform-fullstack-ci.yml (code)
  -           node-version: "21"
  -           node-version: "21"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"

### example 4
autogpt_platform/backend/backend/copilot/tools/agent_browser.py (code)
  + """Agent-browser tools — multi-step browser automation for the Copilot.
  + 
  + Uses the agent-browser CLI (https://github.com/vercel-labs/agent-browser)
  + which runs a local Chromium instance managed by a persistent daemon.
  + 
  + - Runs locally — no cloud account required
  + - Full interaction support: click, fill, scroll, login flows, multi-step
  + - Session persistence via --session-name: cookies/auth carry across tool calls

