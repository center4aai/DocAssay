# Injection task

corpus repository: `tidecast`

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

# Injector — `path-location-drift` (code-side path drift)

**Defect.** A repository file or directory that a document references **by path**
is renamed or moved, so the path the documentation names no longer exists in the
tree. The document still points at the old location.

- **Artifact:** a file path (never a symbol).
- **Direction:** mutate the **code/tree**; the document is left unchanged and
  becomes stale.
- **Dispatch kind:** `path_rename` (harness applies `rename` on disk).

## What the exemplars anchor

Choose a target the same *way* the real incidents do: a path a document treats as
a current, existing location (a linked file, a config example, a module path in a
command), not a path that is already described as historical or illustrative.

## Target-selection rules

1. The path must be a **file** that actually exists in the repository inventory below.
2. It must be named in a document line in the excerpts below (the `doc_path` and
   `doc_line_text` you report).
3. Prefer a file with a **unique basename** so the mention resolves unambiguously.
4. Do not target a document that is itself excluded from analysis (changelogs,
   release notes, translations); pick a README- or guide-like document.

## Required mutation

Rename the file to a minimal, plausible new name (e.g. append `_v2`, change a
word), keeping the same extension and directory unless the incident pattern is a
move. The old path must be gone and the new path present after the change. The
named document line still contains the **old** path token.

Report `target` as the exact path token as written on the doc line.

## Output skeleton (fill and emit as JSON only)

```json
{
  "injectable": true,
  "drift_type": "path-location-drift",
  "artifact_class": "path",
  "direction": "code_side",
  "kind": "path_rename",
  "file": "<old path, relative>",
  "old": "<old path, relative>",
  "new": "<new path, relative>",
  "target": "<path token as written in the doc line>",
  "doc_path": "<document file>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the claim the document makes that the rename falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one or two sentences: which exemplar pattern you followed>"
}
```

## Repository inventory

files:
  README.md, docs/api.md, docs/configuration.md, examples/forecast.json, pyproject.toml, spec.json, tidecast/__init__.py, tidecast/cli.py, tidecast/config.py, tidecast/constants.py, tidecast/models.py, tidecast/routes.py, tidecast/store.py
symbols:
  tidecast.cli.main, tidecast.cli.serve, tidecast.config.Settings, tidecast.config.load_settings, tidecast.models.Forecast, tidecast.models.parse_forecast, tidecast.routes.RouteTable, tidecast.routes.build_routes, tidecast.store.ForecastStore, tidecast.store.default_store
dependencies:
  click>=8.1, flask>=3.0, platformdirs>=4.2, requests>=2.31
project version: 0.4.1  [pyproject.toml]
string literals:
  /v1/forecast, /v1/health, /v1/stations, 0.4.1, Module tidecast/cli.py., Module tidecast/config.py., Module tidecast/constants.py., Module tidecast/models.py., Module tidecast/routes.py., Module tidecast/store.py., Package tidecast., Project class., Project function., TIDECAST_CACHE_TTL, TIDECAST_HOME, TIDECAST_HTTP_PORT, TIDECAST_LOG_LEVEL, handler, issued_at, sky_clear, sky_cloudy, sky_condition, sky_rain, station_id, str, temperature_c

## Document excerpts

### README.md
   1: # tidecast
   2: 
   3: A small local weather-forecast cache that fetches forecasts and serves them from a
   4: JSON-file store.
   5: 
   6: This is tidecast version 0.4.1.
   7: 
   8: ## Overview
   9: 
  10: `tidecast` keeps a local cache of weather forecasts. The cache layer is modeled by
  11: `tidecast.store.ForecastStore`, the value object by `tidecast.models.Forecast`, the
  12: routing table by `tidecast.routes.RouteTable`, and the environment settings by
  13: `tidecast.config.Settings`. A `tidecast.models.Forecast` value carries the station
  14: identifier, the issue time, the temperature in Celsius, and the sky condition. The
  15: sample payload in `examples/forecast.json` shows one complete `tidecast.models.Forecast`
  16: record.
  17: 
  18: ## Requirements
  19: 
  20: The runtime dependencies are `requests` (`>=2.31`), `flask` (`>=3.0`),
  21: `click` (`>=8.1`), and `platformdirs` (`>=4.2`).
  22: 
  23: | Dependency | Constraint |
  24: | --- | --- |
  25: | `requests` | `>=2.31` |
  26: | `flask` | `>=3.0` |
  27: | `click` | `>=8.1` |
  28: | `platformdirs` | `>=4.2` |
  29: 
  30: The HTTP surface is served through the web framework exposed as `flask.Flask`.
  31: 
  32: ## Installation
  33: 
  34: ```bash
  35: pip install -e .
  36: ```
  37: 
  38: ## Quick start
  39: 
  40: ```bash
  41: python -m tidecast serve --port 8080
  42: ```
  43: 
  44: Run the test suite with:
  45: 
  46: ```bash
  47: pytest -q
  48: ```
  49: 
  50: ## Sample data
  51: 
  52: `examples/forecast.json` holds a single cached forecast with these fields:
  53: 
  54: | Field | Example value |
  55: | --- | --- |
  56: | `station_id` | `KSFO` |
  57: | `issued_at` | `2026-10-12T09:00:00Z` |
  58: | `temperature_c` | `16.5` |
  59: | `sky_condition` | `SKY_CLOUDY` |
  60: 
  61: ## HTTP endpoints
  62: 
  63: The route table built by `build_routes()` exposes these paths:
  64: 
  65: | Endpoint | Purpose |
  66: | --- | --- |
  67: | `/v1/forecast` | Return the cached forecast record |
  68: | `/v1/stations` | List the known stations |
  69: | `/v1/health` | Report service liveness |
  70: 
  71: ## Sky conditions
  72: 
  73: The sky condition of a `tidecast.models.Forecast` is one of:
  74: 
  75: | Member | Meaning |
  76: | --- | --- |
  77: | `SKY_CLEAR` | Clear sky |
  78: | `SKY_CLOUDY` | Cloud cover |
  79: | `SKY_RAIN` | Rain |
  80: 
  81: ## Reading a record
  82: 
  83: `parse_forecast()` returns a `Forecast()` object built from a stored payload, and
  84: `default_store()` returns a `ForecastStore()` rooted at the configured home
  85: directory. Settings come from `load_settings()`, which returns a `Settings()` value.
  86: 
  87: ## Configuration
  88: 
  89: The environment keys `TIDECAST_HOME`, `TIDECAST_LOG_LEVEL`, `TIDECAST_CACHE_TTL`, and
  90: `TIDECAST_HTTP_PORT` drive the runtime. See the configuration guide for details.
  91: 
  92: ## Command line
  93: 
  94: The entry points are `tidecast.cli.main` and `tidecast.cli.serve`. Run
  95: `tidecast.cli.serve` to start the HTTP service, and `tidecast.cli.main` for the
  96: top-level dispatcher.
### docs/api.md
   1: # API reference
   2: 
   3: This reference describes the public classes and functions of `tidecast`, the HTTP
   4: endpoints it serves, and the shape of a cached forecast record.
   5: 
   6: ## Modules and symbols
   7: 
   8: | Module | Symbol | Kind |
   9: | --- | --- | --- |
  10: | models | `tidecast.models.Forecast` | class |
  11: | models | `parse_forecast()` | function |
  12: | store | `tidecast.store.ForecastStore` | class |
  13: | store | `default_store()` | function |
  14: | routes | `tidecast.routes.RouteTable` | class |
  15: | routes | `build_routes()` | function |
  16: | config | `tidecast.config.Settings` | class |
  17: | config | `load_settings()` | function |
  18: | cli | `tidecast.cli.main` | function |
  19: | cli | `tidecast.cli.serve` | function |
  20: 
  21: ## Value model
  22: 
  23: `tidecast.models.Forecast` is the value object for a single cached forecast. Its
  24: fields are:
  25: 
  26: | Field | Description |
  27: | --- | --- |
  28: | `station_id` | Station identifier |
  29: | `issued_at` | Issue timestamp |
  30: | `temperature_c` | Temperature in degrees Celsius |
  31: | `sky_condition` | Sky condition member |
  32: 
  33: `parse_forecast()` returns a `Forecast()` built from a stored payload. A payload that
  34: matches `examples/forecast.json` produces a `tidecast.models.Forecast` with the
  35: `station_id` `KSFO`, the `issued_at` `2026-10-12T09:00:00Z`, the `temperature_c` `16.5`,
  36: and the `sky_condition` `SKY_CLOUDY`.
  37: 
  38: ## Sky conditions
  39: 
  40: The `sky_condition` field of a `tidecast.models.Forecast` is one of:
  41: 
  42: | Member | Meaning |
  43: | --- | --- |
  44: | `SKY_CLEAR` | Clear sky |
  45: | `SKY_CLOUDY` | Cloud cover |
  46: | `SKY_RAIN` | Rain |
  47: 
  48: ## Cache store
  49: 
  50: `tidecast.store.ForecastStore` holds the store root together with its load and save
  51: operations. `default_store()` returns a `ForecastStore()` bound to the configured home
  52: directory. Records written by the store use the same fields as
  53: `examples/forecast.json`.
  54: 
  55: ## Routing
  56: 
  57: `tidecast.routes.RouteTable` collects the served routes and offers an add operation.
  58: `build_routes()` returns a `RouteTable()` populated with the service endpoints.
  59: 
  60: | Endpoint | Method | Purpose |
  61: | --- | --- | --- |
  62: | `/v1/forecast` | GET | Return the cached forecast record |
  63: | `/v1/stations` | GET | List the known stations |
  64: | `/v1/health` | GET | Report service liveness |
  65: 
  66: The HTTP layer is provided by the web framework exposed as `flask.Flask`.
  67: 
  68: ## Settings
  69: 
  70: `load_settings()` returns a `Settings()` object. `tidecast.config.Settings` carries the
  71: `home`, `log_level`, and `cache_ttl` attributes, populated from the `TIDECAST_HOME`,
  72: `TIDECAST_LOG_LEVEL`, `TIDECAST_CACHE_TTL`, and `TIDECAST_HTTP_PORT` environment keys.
  73: 
  74: ## Command line
  75: 
  76: `tidecast.cli.main` is the top-level dispatcher and `tidecast.cli.serve` starts the HTTP
  77: service. Launch the service with:
  78: 
  79: ```bash
  80: python -m tidecast serve --port 8080
  81: ```
  82: 
  83: Verify the package with:
  84: 
  85: ```bash
  86: pytest -q
  87: ```
### docs/configuration.md
   1: # Configuration
   2: 
   3: `tidecast` reads its runtime configuration from environment variables, collects them
   4: into a `tidecast.config.Settings` value, and applies them to the cache and the HTTP
   5: service.
   6: 
   7: ## Environment keys
   8: 
   9: `load_settings()` returns a `Settings()` object populated from these keys:
  10: 
  11: | Key | Purpose |
  12: | --- | --- |
  13: | `TIDECAST_HOME` | Root directory of the local store |
  14: | `TIDECAST_LOG_LEVEL` | Logging verbosity for the service |
  15: | `TIDECAST_CACHE_TTL` | Lifetime of a cached forecast |
  16: | `TIDECAST_HTTP_PORT` | Port bound by the HTTP service |
  17: 
  18: ## Settings object
  19: 
  20: `tidecast.config.Settings` holds the resolved values:
  21: 
  22: | Attribute | Description |
  23: | --- | --- |
  24: | `home` | The resolved store directory |
  25: | `log_level` | The resolved logging level |
  26: | `cache_ttl` | The resolved cache lifetime |
  27: 
  28: Call `load_settings()` to obtain a `Settings()` value that carries all three
  29: attributes.
  30: 
  31: ## Store location
  32: 
  33: `default_store()` returns a `ForecastStore()` rooted at the configured home
  34: directory. The store keeps cached `tidecast.models.Forecast` records in a JSON file
  35: inside that directory. A cached record mirrors the sample payload in
  36: `examples/forecast.json`.
  37: 
  38: ## Cached fields
  39: 
  40: Each cached `tidecast.models.Forecast` uses these fields:
  41: 
  42: | Field | Description |
  43: | --- | --- |
  44: | `station_id` | Station identifier, such as `KSFO` |
  45: | `issued_at` | Issue timestamp in ISO 8601 form |
  46: | `temperature_c` | Temperature in degrees Celsius |
  47: | `sky_condition` | Sky condition member |
  48: 
  49: ## Sky condition members
  50: 
  51: The `sky_condition` field carries one of these members:
  52: 
  53: | Member | Meaning |
  54: | --- | --- |
  55: | `SKY_CLEAR` | Clear sky |
  56: | `SKY_CLOUDY` | Cloud cover |
  57: | `SKY_RAIN` | Rain |
  58: 
  59: ## Starting the service
  60: 
  61: Apply the port with `TIDECAST_HTTP_PORT` and launch the HTTP service:
  62: 
  63: ```bash
  64: python -m tidecast serve --port 8080
  65: ```
  66: 
  67: ## Verifying a configuration
  68: 
  69: Run the test suite to confirm that the configuration path resolves:
  70: 
  71: ```bash
  72: pytest -q
  73: ```

## Examples (few-shot)

Real, human-triaged instances of this drift type, rendered as bare excerpts
(`before → after`) under a `<file> (doc|code)` header. No URLs, no commentary.
Use them to choose *what kind of artifact* to target — never to copy wording.

### example 1
docs/cloud.md (doc)
  - # Turbo
  - > ⚠️ Turbo is preview
  - Ollama’s [Turbo](https://ollama.com/turbo) is a new way to run open-source models with acceleration from datacenter-grade hardware.
  - Currently, the following models are available in Turbo:
  - - `gpt-oss:20b`
  - - `gpt-oss:120b`
  - ## Get started
  - ### Ollama for macOS & Windows
  + # Cloud
  + | Ollama's cloud is currently in preview. For full documentation, see [Ollama's documentation](https://docs.ollama.com/cloud).
  + ## Cloud Models
  + [Cloud models](https://ollama.com/cloud) are a new kind of model in Ollama that can run without a powerful GPU. Instead, cloud models are automatically offloaded to Ollama's cloud while offering the same capabilities as local models, making it possible to keep using your local tools while running larger models that wouldn’t fit on a personal computer.
  + Ollama currently supports the following cloud models, with more coming soon:
  + - `gpt-oss:20b-cloud`
  + - `gpt-oss:120b-cloud`
  + - `deepseek-v3.1:671b-cloud`

### example 2
docs/windows.md (doc)
  - ### Changing Model Location
  - 
  - To change where Ollama stores the downloaded models instead of using your home directory, set the environment variable `OLLAMA_MODELS` in your user account.
  - 
  - 1. Start the Settings (Windows 11) or Control Panel (Windows 10) application and search for _environment variables_.
  - 
  - 2. Click on _Edit environment variables for your account_.
  - 

### example 3
cmd/cmd.go (code)
  - 	"github.com/ollama/ollama/x/create"
  - 			// No Modelfile found - check if current directory is an image gen model
  - 			if create.IsTensorModelDir(".") {
  - 				if !isLocalhost() {
  - 					return errors.New("remote safetensor model creation not yet supported")
  - 				}
  - 				quantize, _ := cmd.Flags().GetString("quantize")
  - 				return xcreateclient.CreateModel(xcreateclient.CreateOptions{
  + 	// This gates both safetensors LLM and imagegen model creation
  + 
  + 	// Standard Modelfile + API path

### example 4
autogpt_platform/frontend/src/services/feature-flags/use-get-flag.ts (code)
  -   AGENT_ACTIVITY = "agent-activity",
  -   [Flag.AGENT_ACTIVITY]: boolean;
  -   [Flag.AGENT_ACTIVITY]: true,

