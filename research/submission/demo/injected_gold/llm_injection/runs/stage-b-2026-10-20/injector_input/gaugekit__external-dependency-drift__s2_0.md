# Injection task

corpus repository: `gaugekit`

# Injector — natural documentation defects

You are given one documentation-drift type, a clean repository, and a few real
incident excerpts. Propose **one** concrete inconsistency between the
documentation and the repository, of exactly the requested type.

## Rules

1. **One drift type only.** Use the type named by the per-class task. Do not
   combine types or invent a new one.
2. **Choose a natural current-state statement.** Pick a statement in the
   documentation that a maintainer would treat as a current, checkable fact
   about the project — something a reader could rely on. Prefer ordinary
   present-tense statements. Avoid historical notes, examples, conditionals,
   proposals, and statements that are already ambiguous.
3. **Name a real artifact.** The statement must refer to something that actually
   exists in this repository: a file or directory, a class or function, or a
   dependency the project manifest lists. Do not invent anything.
4. **Make the smallest concrete change.** Change the artifact (or, only where
   the class says so, the document) in a way that makes the chosen statement
   false. The change must be a concrete edit to a named artifact: rename or move
   a file, rename or delete a class/function definition, or change/remove a
   dependency in the project manifest.
5. **Do not optimize for a checker.** Choose the target and the change the way a
   maintainer would, from the documentation and the repository. Do not reason
   about any analysis or verification tool, and do not avoid a natural target
   because you think some tool might miss it.
6. **If nothing fits, decline.** If the repository has no natural current-state
   statement of the requested type, return
   `{"injectable": false, "reason": "<short reason>"}`.
7. **Output exactly one JSON object.** No Markdown fence, no commentary, no
   text outside the object. The `rationale` field is a single short field, not
   prose around the object.

## Process

1. Read the per-class task.
2. Read the repository inventory and document excerpts.
3. Choose one statement and one artifact.
4. Check that the artifact exists and the document line is copied exactly.
5. Run the self-check, then emit the JSON object.

## Self-check

- [ ] The drift type is exactly the requested one.
- [ ] The chosen statement is a current-state statement, not historical,
      illustrative, conditional, or already ambiguous.
- [ ] The artifact exists in the repository under the name used.
- [ ] `doc_path` and `doc_line_text` are copied verbatim from the document.
- [ ] The change is minimal and makes exactly that statement false.
- [ ] The named file still parses after the change.
- [ ] No other kind of defect is introduced as a side effect.
- [ ] `exemplar_ids` lists the exemplar ids that informed target selection.


---

# Injector — external-dependency drift

**Defect.** A document presents a third-party dependency as a current
requirement, but the project manifest is changed so that the dependency no longer
satisfies the documented requirement, or the dependency is removed while the
document still names it.

- **Artifact:** a dependency listed in the project manifest.
- **Direction:** change the manifest; leave the document unchanged.

## What to look for

Choose a statement that presents a dependency as a current requirement. If the
document states a version requirement, use the constraint form of the mutation.
If it only names the dependency as something the project uses, use the removal
form.

The mutation edits the project manifest (`pyproject.toml`, `setup.cfg`,
`setup.py`, or `requirements*.txt`), so the dependency must be one the manifest
actually lists; otherwise there is nothing to change. This is a property of the
edit, not a rule about how the document should be written.

## The change

- **Constraint form:** change the manifest constraint to a clearly
  non-overlapping bound (for example `>=999`). The new constraint must be
  parseable and must not intersect the requirement stated in the document.
- **Removal form:** remove the dependency from the manifest while the document
  still names it. Use this form only when the document does not state a
  constraint.

The document line must still name the dependency.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "external-dependency-drift",
  "direction": "code_side",
  "file": "<manifest file>",
  "old": "<the existing constraint, or the dependency name for removal>",
  "new": "<the new constraint, or null for removal>",
  "symbol": "<normalized dependency name>",
  "target": "<the exact dependency text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the change falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-requirement statement>"
}
```

If no natural current-requirement statement exists, emit:

```json
{"injectable": false, "reason": "<short reason>"}
```

## Repository inventory

files:
  README.md, docs/api.md, docs/guide.md, examples/sample_gauge.csv, gaugekit/__init__.py, gaugekit/errors.py, gaugekit/loader.py, gaugekit/models.py, gaugekit/stats.py, gaugekit/units.py, pyproject.toml, spec.json
symbols:
  gaugekit.errors.GaugeFormatError, gaugekit.loader.load_csv, gaugekit.loader.read_station_id, gaugekit.models.GaugeSeries, gaugekit.models.Reading, gaugekit.stats.monthly_means, gaugekit.stats.summarize, gaugekit.units.cfs_to_cms
dependencies:
  numpy>=1.24
string literals:
  0.4.2, Module gaugekit/errors.py., Module gaugekit/loader.py., Module gaugekit/models.py., Module gaugekit/stats.py., Module gaugekit/units.py., Package gaugekit., Project class., Project function., cfs_per_cms

## Document excerpts

### README.md
   1: # gaugekit
   2: 
   3: gaugekit is a small Python library for loading public stream-gauge CSV exports and computing summary statistics for discharge and gauge height. It is aimed at people who work with river gauge data downloaded as CSV and want a few typed building blocks for reading it and summarizing it.
   4: 
   5: Current version: **0.4.2**. Requires Python 3.11 or newer.
   6: 
   7: ## Installation
   8: 
   9: gaugekit depends on NumPy (`numpy>=1.24`). From a checkout of the repository:
  10: 
  11: ```bash
  12: pip install .
  13: ```
  14: 
  15: ## Quick start
  16: 
  17: The package exposes its public functions from submodules rather than from the top-level `gaugekit` package:
  18: 
  19: ```python
  20: from gaugekit.loader import load_csv
  21: from gaugekit.stats import summarize, monthly_means
  22: from gaugekit.units import cfs_to_cms
  23: 
  24: series = load_csv("examples/sample_gauge.csv")
  25: stats = summarize(series)
  26: by_month = monthly_means(series)
  27: ```
  28: 
  29: The repository includes `examples/sample_gauge.csv`, a four-row file in the expected layout (see the [guide](docs/guide.md#csv-format)).
  30: 
  31: > **Status:** the functions in this release are declared with their signatures and return types, but their bodies are placeholders that return `None`. The quick start shows the intended calling pattern; it will not produce values until the implementations are filled in.
  32: 
  33: ## Documentation
  34: 
  35: - [Guide](docs/guide.md): data format, module layout, and typical usage.
  36: - [API reference](docs/api.md): every public class, function, and constant.
### docs/api.md
   1: # API reference
   2: 
   3: All public names live in submodules of `gaugekit`. The top-level package exposes only `__version__` (`"0.4.2"`).
   4: 
   5: In this release the functions and class constructors are declared with the signatures shown below but take no parameters and their bodies return `None`. Parameters are therefore not yet documented here.
   6: 
   7: ## `gaugekit.models`
   8: 
   9: ### `Reading`
  10: 
  11: A single observation. Instances carry these attributes:
  12: 
  13: | Attribute | Description |
  14: | --- | --- |
  15: | `timestamp` | Reading time. |
  16: | `discharge_cfs` | Discharge in cubic feet per second. |
  17: | `gauge_height_ft` | Gauge height in feet. |
  18: 
  19: ### `GaugeSeries`
  20: 
  21: A station's data. Instances carry these attributes:
  22: 
  23: | Attribute | Description |
  24: | --- | --- |
  25: | `station_id` | Gauge station identifier. |
  26: | `readings` | The collection of readings for the station. |
  27: 
  28: ## `gaugekit.loader`
  29: 
  30: ### `load_csv() -> GaugeSeries`
  31: 
  32: Loads a CSV export into a `GaugeSeries`. The expected columns are described in the [guide](guide.md#csv-format).
  33: 
  34: ### `read_station_id() -> str`
  35: 
  36: Returns the station identifier from a CSV export as a string.
  37: 
  38: ## `gaugekit.stats`
  39: 
  40: ### `summarize() -> dict[str, float]`
  41: 
  42: Computes summary statistics for a series, keyed by statistic name.
  43: 
  44: ### `monthly_means() -> dict[str, float]`
  45: 
  46: Computes monthly mean values for a series, returned as a dictionary of floats.
  47: 
  48: ## `gaugekit.units`
  49: 
  50: ### `CFS_PER_CMS`
  51: 
  52: Module-level constant with the value `"cfs_per_cms"`. It is a string label and is not a numeric conversion factor.
  53: 
  54: ### `cfs_to_cms() -> float`
  55: 
  56: Converts a discharge from cubic feet per second to cubic metres per second. Declared to return a `float`.
  57: 
  58: ## `gaugekit.errors`
  59: 
  60: ### `GaugeFormatError`
  61: 
  62: Error for malformed input. Instances carry:
  63: 
  64: | Attribute | Description |
  65: | --- | --- |
  66: | `line_number` | Line in the input where the problem was found. |
  67: | `message` | Description of the problem. |
  68: 
  69: In the current source, `GaugeFormatError` is defined as a plain class and does not subclass `Exception`.
### docs/guide.md
   1: # gaugekit guide
   2: 
   3: This guide covers the CSV layout gaugekit expects, how the package is organized, and how the pieces fit together. For signatures and return types, see the [API reference](api.md).
   4: 
   5: ## Package layout
   6: 
   7: | Module | Contents |
   8: | --- | --- |
   9: | `gaugekit.models` | `Reading` and `GaugeSeries` data containers. |
  10: | `gaugekit.loader` | `load_csv` and `read_station_id` for reading CSV exports. |
  11: | `gaugekit.stats` | `summarize` and `monthly_means` summary statistics. |
  12: | `gaugekit.units` | `CFS_PER_CMS` constant and the `cfs_to_cms` conversion. |
  13: | `gaugekit.errors` | `GaugeFormatError`, the error type for malformed input. |
  14: 
  15: The top-level `gaugekit` package only defines `__version__`. Import from the submodules directly.
  16: 
  17: ## CSV format
  18: 
  19: The loader works with CSV exports that have a header row and the following four columns:
  20: 
  21: | Column | Meaning |
  22: | --- | --- |
  23: | `station_id` | Gauge station identifier, for example `01646500`. |
  24: | `timestamp` | Reading time in ISO 8601 form, for example `2026-01-01T00:00:00`. |
  25: | `discharge_cfs` | Discharge in cubic feet per second. |
  26: | `gauge_height_ft` | Gauge height in feet. |
  27: 
  28: The bundled example, `examples/sample_gauge.csv`, looks like this:
  29: 
  30: ```csv
  31: station_id,timestamp,discharge_cfs,gauge_height_ft
  32: 01646500,2026-01-01T00:00:00,412.0,3.41
  33: 01646500,2026-01-01T01:00:00,405.5,3.38
  34: 01646500,2026-02-01T00:00:00,530.2,3.92
  35: 01646500,2026-02-01T01:00:00,548.9,3.99
  36: ```
  37: 
  38: Discharge is given in cfs; `gaugekit.units` provides `cfs_to_cms` for converting to cubic metres per second.
  39: 
  40: ## Data containers
  41: 
  42: - `Reading` holds one observation with the attributes `timestamp`, `discharge_cfs`, and `gauge_height_ft`.
  43: - `GaugeSeries` holds one station's data with the attributes `station_id` and `readings`.
  44: 
  45: `load_csv` is declared to return a `GaugeSeries`, and `summarize` and `monthly_means` are declared to return `dict[str, float]`.
  46: 
  47: ## Errors
  48: 
  49: Malformed input is reported with `GaugeFormatError`, which carries `line_number` and `message` attributes.
  50: 
  51: ## Typical workflow
  52: 
  53: 1. Read a file with `load_csv` to get a `GaugeSeries`.
  54: 2. Use `read_station_id` when you only need the station identifier.
  55: 3. Pass the series to `summarize` for overall statistics, or to `monthly_means` for monthly values.
  56: 4. Convert discharge with `cfs_to_cms` when metric units are needed.
  57: 
  58: As noted in the [README](../README.md), the function bodies in this release are placeholders, so this workflow describes the intended usage rather than working output.

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

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
autogpt_platform/backend/backend/copilot/tools/agent_browser.py (code)
  + """Agent-browser tools — multi-step browser automation for the Copilot.
  + 
  + Uses the agent-browser CLI (https://github.com/vercel-labs/agent-browser)
  + which runs a local Chromium instance managed by a persistent daemon.
  + 
  + - Runs locally — no cloud account required
  + - Full interaction support: click, fill, scroll, login flows, multi-step
  + - Session persistence via --session-name: cookies/auth carry across tool calls

### example 4
Documentation/process/changes.rst (doc)
  - bindgen (optional)     0.65.1           bindgen --version
  + bindgen (optional)     0.71.1           bindgen --version
scripts/min-tool-version.sh (code)
  - 	echo 0.65.1
  + 	echo 0.71.1

