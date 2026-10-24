# Injection task

corpus repository: `gridwatch`

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
  README.md, data/meter_jan.csv, data/tariff.yaml, docs/api.md, docs/guide.md, gridwatch/__init__.py, gridwatch/cli.py, gridwatch/costing.py, gridwatch/models.py, gridwatch/readers.py, gridwatch/tariff.py, pyproject.toml, spec.json
symbols:
  gridwatch.cli.main, gridwatch.costing.compute_cost, gridwatch.models.Reading, gridwatch.readers.read_csv, gridwatch.readers.read_json, gridwatch.tariff.Tariff, gridwatch.tariff.load_tariff
dependencies:
  click>=8.1, pyyaml>=6.0
string literals:
  0.3.0, Module gridwatch/cli.py., Module gridwatch/costing.py., Module gridwatch/models.py., Module gridwatch/readers.py., Module gridwatch/tariff.py., Package gridwatch., Project class., Project function., rounding_decimals

## Document excerpts

### README.md
   1: # gridwatch
   2: 
   3: `gridwatch` parses smart-meter interval readings from CSV or JSON files and
   4: computes electricity costs under a time-of-use tariff. It is intended for
   5: people who receive interval data from a meter and want to estimate what the
   6: consumption costs under peak and off-peak rates.
   7: 
   8: Version: 0.3.0 (requires Python 3.11 or newer).
   9: 
  10: ## Installation
  11: 
  12: From a checkout of this repository:
  13: 
  14: ```bash
  15: pip install .
  16: ```
  17: 
  18: Runtime dependencies, as declared in `pyproject.toml`:
  19: 
  20: - `PyYAML>=6.0`
  21: - `click>=8.1`
  22: 
  23: ## Quick start
  24: 
  25: The repository ships two sample files under `data/`:
  26: 
  27: - `data/meter_jan.csv`: three hourly readings for meter `M-1042` on
  28:   2026-01-05.
  29: - `data/tariff.yaml`: a tariff with a peak rate of 0.32, an off-peak rate of
  30:   0.11, and a peak window from hour 17 to hour 21.
  31: 
  32: ```python
  33: from gridwatch.readers import read_csv
  34: from gridwatch.tariff import load_tariff
  35: from gridwatch.costing import compute_cost
  36: 
  37: readings = read_csv()
  38: tariff = load_tariff()
  39: total = compute_cost()
  40: ```
  41: 
  42: The functions above are the public entry points. In the current source they
  43: are declared without parameters and their bodies are placeholders that return
  44: `None`, so the example shows the call shape rather than a working result. See
  45: the [API reference](docs/api.md) for the declared names and return types.
  46: 
  47: The project metadata also lists the command `gridwatch cost data/meter_jan.csv
  48: --tariff data/tariff.yaml`. The `main` function in `gridwatch/cli.py` exists,
  49: but no console script is declared in `pyproject.toml`, so this command is not
  50: installed by the package as it stands.
  51: 
  52: ## Documentation
  53: 
  54: - [User guide](docs/guide.md): input file formats, tariff fields, and how the
  55:   pieces fit together.
  56: - [API reference](docs/api.md): modules, classes, functions, and the
  57:   `ROUNDING_DECIMALS` constant.
### docs/api.md
   1: # gridwatch API reference
   2: 
   3: All public names are in the `gridwatch` package. The source declares the
   4: signatures below without parameters and the bodies return `None`; the
   5: parameter lists are therefore not yet specified in the code.
   6: 
   7: ## `gridwatch.models`
   8: 
   9: ### `class Reading`
  10: 
  11: A single interval reading. An instance has the attributes:
  12: 
  13: - `meter_id`: the meter identifier.
  14: - `timestamp`: the interval timestamp.
  15: - `kwh`: the energy consumed in the interval.
  16: 
  17: The constructor takes no arguments and sets all three attributes to `None`.
  18: 
  19: ## `gridwatch.readers`
  20: 
  21: ### `read_csv() -> list[Reading]`
  22: 
  23: Declared to read interval readings from a CSV file (see the
  24: [guide](guide.md#interval-readings-csv) for the columns). Returns a list of
  25: `Reading` objects.
  26: 
  27: ### `read_json() -> list[Reading]`
  28: 
  29: Declared to read interval readings from a JSON file. Returns a list of
  30: `Reading` objects. The JSON layout is not defined in the source.
  31: 
  32: ## `gridwatch.tariff`
  33: 
  34: ### `class Tariff`
  35: 
  36: Time-of-use tariff settings. An instance has the attributes:
  37: 
  38: - `peak_rate`
  39: - `offpeak_rate`
  40: - `peak_start_hour`
  41: - `peak_end_hour`
  42: 
  43: The constructor takes no arguments and sets all four attributes to `None`.
  44: The keys correspond to those in the [tariff file](guide.md#tariff-yaml).
  45: 
  46: ### `load_tariff() -> Tariff`
  47: 
  48: Declared to load a `Tariff`, presumably from a YAML file in the format
  49: described in the guide. The source does not yet name the file parameter.
  50: 
  51: ## `gridwatch.costing`
  52: 
  53: ### `compute_cost() -> float`
  54: 
  55: Declared to compute the electricity cost as a `float`. The source does not
  56: yet define its parameters.
  57: 
  58: ### `ROUNDING_DECIMALS`
  59: 
  60: A module-level constant in `gridwatch/costing.py`. Its current value is the
  61: string `"rounding_decimals"`. The source does not say how it is used.
  62: 
  63: ## `gridwatch.cli`
  64: 
  65: ### `main() -> int`
  66: 
  67: The command-line entry function. Declared to return an `int` exit code. It is
  68: not registered as a console script in `pyproject.toml`.
### docs/guide.md
   1: # gridwatch user guide
   2: 
   3: This guide describes the input files `gridwatch` works with and how the
   4: package is organized. For the function and class listing, see the
   5: [API reference](api.md).
   6: 
   7: ## Input data
   8: 
   9: ### Interval readings (CSV)
  10: 
  11: Meter readings are read from CSV files with the header:
  12: 
  13: ```
  14: meter_id,timestamp,kwh
  15: ```
  16: 
  17: Each row is one interval reading:
  18: 
  19: | Column      | Meaning                                  |
  20: |-------------|------------------------------------------|
  21: | `meter_id`  | Identifier of the meter, for example `M-1042`. |
  22: | `timestamp` | Start of the interval, ISO 8601 (for example `2026-01-05T16:00:00`). |
  23: | `kwh`       | Energy consumed during the interval, in kilowatt-hours. |
  24: 
  25: Example, from `data/meter_jan.csv`:
  26: 
  27: ```
  28: meter_id,timestamp,kwh
  29: M-1042,2026-01-05T16:00:00,0.82
  30: M-1042,2026-01-05T17:00:00,1.14
  31: M-1042,2026-01-05T18:00:00,0.97
  32: ```
  33: 
  34: ### Interval readings (JSON)
  35: 
  36: `gridwatch.readers.read_json` is declared to read readings from JSON. The
  37: source does not yet define the JSON layout, so this guide does not document
  38: one.
  39: 
  40: ### Tariff (YAML)
  41: 
  42: A time-of-use tariff is a YAML mapping with four keys:
  43: 
  44: | Key               | Meaning                                    |
  45: |-------------------|--------------------------------------------|
  46: | `peak_rate`       | Rate applied during peak hours.            |
  47: | `offpeak_rate`    | Rate applied outside peak hours.           |
  48: | `peak_start_hour` | Hour of day at which the peak window starts. |
  49: | `peak_end_hour`   | Hour of day at which the peak window ends.   |
  50: 
  51: Example, from `data/tariff.yaml`:
  52: 
  53: ```yaml
  54: peak_rate: 0.32
  55: offpeak_rate: 0.11
  56: peak_start_hour: 17
  57: peak_end_hour: 21
  58: ```
  59: 
  60: The rates are per kilowatt-hour. The file is read with PyYAML, which is why it
  61: is a runtime dependency.
  62: 
  63: ## Package layout
  64: 
  65: | Module                | Contents                                                |
  66: |-----------------------|---------------------------------------------------------|
  67: | `gridwatch/models.py` | `Reading`, the record for one interval reading.         |
  68: | `gridwatch/readers.py`| `read_csv` and `read_json`, which produce lists of `Reading`. |
  69: | `gridwatch/tariff.py` | `Tariff`, the tariff settings, and `load_tariff`.       |
  70: | `gridwatch/costing.py`| `compute_cost` and the `ROUNDING_DECIMALS` constant.    |
  71: | `gridwatch/cli.py`    | `main`, the command-line entry function.                |
  72: 
  73: A typical flow is: read readings with a reader, load a tariff, and pass both to
  74: the costing function. The current source declares these steps but does not
  75: connect them, so the flow is a plan for the API rather than working behavior.
  76: 
  77: ## Command line
  78: 
  79: The `main` function in `gridwatch/cli.py` is declared to return an `int`.
  80: The package metadata lists the command `gridwatch cost <readings file>
  81: --tariff <tariff file>`, but no console script is registered in
  82: `pyproject.toml`. To run `main` today, call it from Python:
  83: 
  84: ```python
  85: from gridwatch.cli import main
  86: 
  87: exit_code = main()
  88: ```

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

### example 1
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

### example 2
autogpt_platform/cloudflare_worker.js (code)
  + /**
  +  * Cloudflare Workers Script for docs.agpt.co → agpt.co/docs migration
  +  * 
  +  * Deploy this script to handle all redirects with a single JavaScript file.
  +  * No rule limits, easy to maintain, handles all edge cases.
  +  */
  + 
  + // URL mapping for special cases that don't follow patterns
docs/README.md (doc)
  + ---
  + description: Welcome to your team’s developer platform
  + cover: .gitbook/assets/Banner_image.png
  + coverY: 56.53835084561286
  + layout:
  +   width: wide
  +   cover:
  +     visible: true

### example 3
Documentation/process/changes.rst (doc)
  - Rust (optional)        1.78.0           rustc --version
  + Rust (optional)        1.85.0           rustc --version

### example 4
docs/capabilities/web-search.mdx (doc)
  - const results = await client.webSearch({ query: "what is ollama?" });
  - const fetchResult = await client.webFetch({ url: "https://ollama.com" });
  + const results = await client.webSearch("what is ollama?");
  + const fetchResult = await client.webFetch("https://ollama.com");

