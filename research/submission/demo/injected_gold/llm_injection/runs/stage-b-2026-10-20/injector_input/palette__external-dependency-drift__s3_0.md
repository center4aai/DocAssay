# Injection task

corpus repository: `palette`

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
  README.md, docs/api.md, docs/guide.md, palette/__init__.py, palette/cli.py, palette/colors.py, palette/contrast.py, palette/convert.py, palette/harmony.py, pyproject.toml, spec.json
symbols:
  palette.cli.main, palette.colors.Color, palette.colors.parse_color, palette.contrast.contrast_ratio, palette.contrast.passes_aa, palette.convert.HSL, palette.convert.to_hsl, palette.harmony.generate_palette
dependencies:
  click>=8.1
string literals:
  0.4.0, Module palette/cli.py., Module palette/colors.py., Module palette/contrast.py., Module palette/convert.py., Module palette/harmony.py., Package palette., Project class., Project function., harmony_schemes, wcag_aa_minimum

## Document excerpts

### README.md
   1: # palette
   2: 
   3: `palette` is a small Python library for parsing colors, generating harmonious
   4: palettes, and checking WCAG contrast ratios. It is aimed at developers who need
   5: these color operations inside their own tools, scripts, or design pipelines.
   6: 
   7: Version: 0.4.0 (requires Python 3.11 or newer).
   8: 
   9: ## Installation
  10: 
  11: Install from a local checkout:
  12: 
  13: ```bash
  14: pip install .
  15: ```
  16: 
  17: The only declared runtime dependency is `click>=8.1`.
  18: 
  19: ## Quick start
  20: 
  21: The package exposes its public names from the `palette` modules:
  22: 
  23: ```python
  24: from palette.colors import parse_color
  25: from palette.convert import to_hsl
  26: from palette.harmony import generate_palette
  27: from palette.contrast import contrast_ratio, passes_aa
  28: 
  29: color = parse_color()
  30: hsl = to_hsl()
  31: palette = generate_palette()
  32: ratio = contrast_ratio()
  33: ok = passes_aa()
  34: ```
  35: 
  36: The functions above take no arguments in the current source, and their bodies
  37: return `None`. The example shows the import paths and call names; see the
  38: [API reference](docs/api.md) for the signatures and return annotations as they
  39: are written in the source.
  40: 
  41: ## Documentation
  42: 
  43: - [Guide](docs/guide.md): the color and palette concepts used by the library and
  44:   how the modules fit together.
  45: - [API reference](docs/api.md): every public class, function, and constant.
  46: 
  47: ## Command line
  48: 
  49: The package includes a `main` function in `palette/cli.py`. The `pyproject.toml`
  50: in this tree does not declare a console script, so no `palette` command is
  51: installed by `pip install .`.
### docs/api.md
   1: # palette API reference
   2: 
   3: All names below are defined in the modules under `palette/`. Import them from
   4: their module, for example `from palette.contrast import passes_aa`.
   5: 
   6: The signatures are those in the current source. Every function body currently
   7: returns `None`, regardless of its annotated return type.
   8: 
   9: ## `palette.colors`
  10: 
  11: ### `class Color`
  12: 
  13: A color with four attributes: `red`, `green`, `blue`, and `alpha`. The
  14: constructor takes no arguments and sets each attribute to `None`.
  15: 
  16: ### `parse_color() -> Color`
  17: 
  18: Intended to parse a color specification into a `Color`. The current source
  19: takes no arguments and returns `None`.
  20: 
  21: ## `palette.convert`
  22: 
  23: ### `class HSL`
  24: 
  25: A color in the hue, saturation, lightness model. The constructor takes no
  26: arguments and sets `hue`, `saturation`, and `lightness` to `None`.
  27: 
  28: ### `to_hsl() -> HSL`
  29: 
  30: Intended to convert a color to `HSL`. The current source takes no arguments and
  31: returns `None`.
  32: 
  33: ## `palette.harmony`
  34: 
  35: ### `HARMONY_SCHEMES`
  36: 
  37: Module-level constant naming the harmony schemes. The current value is the
  38: string `"harmony_schemes"`.
  39: 
  40: ### `generate_palette() -> list[Color]`
  41: 
  42: Intended to generate a palette of `Color` values. The current source takes no
  43: arguments and returns `None`.
  44: 
  45: ## `palette.contrast`
  46: 
  47: ### `WCAG_AA_MINIMUM`
  48: 
  49: Module-level constant for the WCAG AA threshold used by `passes_aa`. The current
  50: value is the string `"wcag_aa_minimum"`.
  51: 
  52: ### `contrast_ratio() -> float`
  53: 
  54: Intended to return the WCAG contrast ratio between two colors. The current
  55: source takes no arguments and returns `None`.
  56: 
  57: ### `passes_aa() -> bool`
  58: 
  59: Intended to report whether a contrast result meets `WCAG_AA_MINIMUM`. The
  60: current source takes no arguments and returns `None`.
  61: 
  62: ## `palette.cli`
  63: 
  64: ### `main() -> int`
  65: 
  66: Command-line entry point, annotated to return an integer exit status. The current
  67: source takes no arguments and returns `None`. `pyproject.toml` does not declare a
  68: console script that calls it.
### docs/guide.md
   1: # palette guide
   2: 
   3: This guide describes the concepts behind the `palette` modules and how they are
   4: organized. For exact signatures, see the [API reference](api.md).
   5: 
   6: ## Colors
   7: 
   8: A color is represented by the `Color` class in `palette/colors.py`. It has four
   9: attributes: `red`, `green`, `blue`, and `alpha`. `parse_color` is the function
  10: intended to build a `Color` from a textual color specification.
  11: 
  12: ## HSL
  13: 
  14: `palette/convert.py` defines the `HSL` class, which holds the three components of
  15: the hue, saturation, lightness color model: `hue`, `saturation`, and
  16: `lightness`. The `to_hsl` function is intended to convert a color to this model
  17: and is annotated to return an `HSL`.
  18: 
  19: ## Harmonious palettes
  20: 
  21: `palette/harmony.py` provides `generate_palette`, which is annotated to return a
  22: `list[Color]`. The module also defines `HARMONY_SCHEMES`, a module-level constant
  23: that names the harmony schemes the generator is meant to support. In the current
  24: source the constant is a plain string, so it does not yet list individual
  25: schemes.
  26: 
  27: ## Contrast and WCAG
  28: 
  29: `palette/contrast.py` contains the contrast helpers:
  30: 
  31: - `contrast_ratio` returns a `float`, the contrast ratio between two colors.
  32: - `passes_aa` returns a `bool`, indicating whether a contrast result meets the
  33:   WCAG AA level.
  34: - `WCAG_AA_MINIMUM` is a module-level constant intended to hold the minimum
  35:   ratio used by `passes_aa`. In the current source it is a plain string.
  36: 
  37: WCAG contrast is computed from the relative luminance of two colors. The
  38: library's contrast functions are the place where that check belongs; the
  39: current source bodies return `None`, so no ratio is computed yet.
  40: 
  41: ## Command line
  42: 
  43: `palette/cli.py` defines `main`, annotated to return an `int`. It is the entry
  44: point for command-line use. The `pyproject.toml` in this tree does not register
  45: a console script for it.
  46: 
  47: ## Module layout
  48: 
  49: | Module | Public names |
  50: | --- | --- |
  51: | `palette/colors.py` | `Color`, `parse_color` |
  52: | `palette/convert.py` | `HSL`, `to_hsl` |
  53: | `palette/harmony.py` | `HARMONY_SCHEMES`, `generate_palette` |
  54: | `palette/contrast.py` | `WCAG_AA_MINIMUM`, `contrast_ratio`, `passes_aa` |
  55: | `palette/cli.py` | `main` |
  56: 
  57: `palette/__init__.py` only sets the package docstring and `__version__`
  58: (`"0.4.0"`); it does not re-export the names above, so import them from their
  59: modules.

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
docs/capabilities/web-search.mdx (doc)
  - const results = await client.webSearch({ query: "what is ollama?" });
  - const fetchResult = await client.webFetch({ url: "https://ollama.com" });
  + const results = await client.webSearch("what is ollama?");
  + const fetchResult = await client.webFetch("https://ollama.com");

### example 4
Documentation/process/changes.rst (doc)
  - bindgen (optional)     0.65.1           bindgen --version
  + bindgen (optional)     0.71.1           bindgen --version
scripts/min-tool-version.sh (code)
  - 	echo 0.65.1
  + 	echo 0.71.1

