# Injection task

corpus repository: `quillpad`

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
  README.md, docs/api.md, docs/configuration.md, examples/notes.yaml, pyproject.toml, quillpad/__init__.py, quillpad/cli.py, quillpad/constants.py, quillpad/models.py, quillpad/routes.py, quillpad/settings.py, quillpad/store.py, spec.json
symbols:
  quillpad.cli.main, quillpad.constants.Limits, quillpad.models.Note, quillpad.models.load_note, quillpad.routes.RouteTable, quillpad.routes.register_routes, quillpad.settings.Settings, quillpad.settings.load_settings, quillpad.store.NoteStore, quillpad.store.open_store
dependencies:
  click>=8.1, fastapi>=0.110, pydantic>=2.6, pyyaml>=6.0
project version: 0.1.0  [pyproject.toml]
string literals:
  /v1/health, /v1/notes, /v1/notes/{note_id}, 0.1.0, Module quillpad/cli.py., Module quillpad/constants.py., Module quillpad/models.py., Module quillpad/routes.py., Module quillpad/settings.py., Module quillpad/store.py., Package quillpad., Project class., Project function., QUILLPAD_HOME, QUILLPAD_LOG_LEVEL, QUILLPAD_STORE_PATH, body_text, created_at, handler, note_id, note_status_archived, note_status_draft, note_status_published, str, title

## Document excerpts

### README.md
   1: # quillpad
   2: 
   3: quillpad is a small local note-taking library with a CLI, a tiny HTTP route table, and a YAML-backed store.
   4: 
   5: This is quillpad version 0.1.0.
   6: 
   7: ## Overview
   8: 
   9: The library is organized around a small set of modules:
  10: 
  11: - `quillpad.models.Note` is the core record type, and `quillpad.models.load_note()` returns a `Note()` object.
  12: - `quillpad.store.open_store()` returns a `NoteStore()` object backed by a YAML store.
  13: - `quillpad.routes.register_routes()` returns a `RouteTable()` object that describes the HTTP surface.
  14: - `quillpad.settings.load_settings()` returns a `Settings()` object built from the environment.
  15: - `quillpad.cli.main()` is the command-line entry point.
  16: 
  17: ## Installation
  18: 
  19: Install the project from its source directory:
  20: 
  21: ```bash
  22: pip install -e .
  23: ```
  24: 
  25: quillpad depends on `PyYAML` (`>=6.0`), `click` (`>=8.1`), `fastapi` (`>=0.110`), and `pydantic` (`>=2.6`).
  26: 
  27: ## Quick start
  28: 
  29: The sample data lives in `examples/notes.yaml`. Load a note with `quillpad.models.load_note()`:
  30: 
  31: ```python
  32: from quillpad.models import load_note
  33: 
  34: note = load_note()
  35: ```
  36: 
  37: `quillpad.models.load_note()` returns a `Note()` object. Each result is a `quillpad.models.Note()` populated from the fields in `examples/notes.yaml`.
  38: 
  39: ## Example commands
  40: 
  41: Serve the HTTP route table on a local port:
  42: 
  43: ```bash
  44: python -m quillpad serve --port 8080
  45: ```
  46: 
  47: Run the test suite:
  48: 
  49: ```bash
  50: pytest -q
  51: ```
  52: 
  53: ## Documentation
  54: 
  55: - docs/configuration.md describes environment variables and settings.
  56: - docs/api.md lists the models, store, routes, settings, and CLI symbols.
### docs/api.md
   1: # API reference
   2: 
   3: This page lists the public classes and functions of quillpad.
   4: 
   5: ## Models
   6: 
   7: `quillpad.models.Note` is the record type. `quillpad.models.load_note()` returns a `Note()` object, and each result carries the schema fields below.
   8: 
   9: | Field |
  10: | --- |
  11: | `note_id` |
  12: | `title` |
  13: | `body_text` |
  14: | `created_at` |
  15: 
  16: A `quillpad.models.Note` adds the `status` field on top of those schema fields, and a sample record is available in `examples/notes.yaml`.
  17: 
  18: ## Store
  19: 
  20: `quillpad.store.NoteStore` holds the `store_path` and the `notes` collection. `quillpad.store.open_store()` returns a `NoteStore()` object.
  21: 
  22: ## Routes
  23: 
  24: `quillpad.routes.RouteTable` holds the `routes` mapping. The HTTP layer is built on `fastapi.APIRouter`, and `quillpad.routes.register_routes()` returns a `RouteTable()` object.
  25: 
  26: ### Endpoints
  27: 
  28: | Endpoint |
  29: | --- |
  30: | `/v1/notes` |
  31: | `/v1/notes/{note_id}` |
  32: | `/v1/health` |
  33: 
  34: ## Settings
  35: 
  36: `quillpad.settings.Settings` holds `home`, `log_level`, and `store_path`. `quillpad.settings.load_settings()` returns a `Settings()` object.
  37: 
  38: ## Constants
  39: 
  40: `quillpad.constants.Limits` holds the `max_notes` bound, and the status members are `NOTE_STATUS_DRAFT`, `NOTE_STATUS_PUBLISHED`, and `NOTE_STATUS_ARCHIVED`.
  41: 
  42: ## CLI
  43: 
  44: `quillpad.cli.main()` is the command-line entry point.
### docs/configuration.md
   1: # Configuration
   2: 
   3: quillpad reads its settings through `quillpad.settings.load_settings()`, which returns a `Settings()` object populated from environment variables.
   4: 
   5: ## Environment variables
   6: 
   7: | Key | Purpose |
   8: | --- | --- |
   9: | `QUILLPAD_HOME` | Base directory for quillpad data. |
  10: | `QUILLPAD_LOG_LEVEL` | Logging verbosity. |
  11: | `QUILLPAD_STORE_PATH` | Path to the YAML-backed store. |
  12: 
  13: ## Settings fields
  14: 
  15: `quillpad.settings.Settings` carries the resolved values.
  16: 
  17: | Field | Description |
  18: | --- | --- |
  19: | `home` | Resolved home directory for quillpad data. |
  20: | `log_level` | Resolved logging verbosity. |
  21: | `store_path` | Resolved path to the YAML-backed store. |
  22: 
  23: ## Store data
  24: 
  25: The store loads notes from `examples/notes.yaml`. Each entry in that file maps to a `quillpad.models.Note` record with the fields `note_id`, `title`, `body_text`, `created_at`, and `status`.
  26: 
  27: `quillpad.store.open_store()` returns a `NoteStore()` object whose `store_path` points at the store file and whose `notes` collection holds the loaded `quillpad.models.Note` records.
  28: 
  29: ## Limits
  30: 
  31: `quillpad.constants.Limits` carries the configurable `max_notes` bound.
  32: 
  33: ## Status members
  34: 
  35: The note status members are defined in the constants module:
  36: 
  37: | Member |
  38: | --- |
  39: | `NOTE_STATUS_DRAFT` |
  40: | `NOTE_STATUS_PUBLISHED` |
  41: | `NOTE_STATUS_ARCHIVED` |

## Examples (few-shot)

Real, human-triaged instances of this drift type, rendered as bare excerpts
(`before → after`) under a `<file> (doc|code)` header. No URLs, no commentary.
Use them to choose *what kind of artifact* to target — never to copy wording.

### example 1
arch/Kconfig (code)
  - 	depends on RUSTC_VERSION >= 107900
  - 	depends on (RUSTC_LLVM_VERSION >= 190103 && RUSTC_VERSION >= 108200) || \
  + 	depends on RUSTC_LLVM_VERSION >= 190103 || \
arch/arm64/Kconfig (code)
  - 	# Shadow call stack is only supported on certain rustc versions.
  - 	#
  - 	# When using the UNWIND_PATCH_PAC_INTO_SCS option, rustc version 1.80+ is
  - 	# required due to use of the -Zfixed-x18 flag.
  - 	#
  - 	# Otherwise, rustc version 1.82+ is required due to use of the
  - 	# -Zsanitizer=shadow-call-stack flag.
  - 	depends on !SHADOW_CALL_STACK || RUSTC_VERSION >= 108200 || RUSTC_VERSION >= 108000 && UNWIND_PATCH_PAC_INTO_SCS

### example 2
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

