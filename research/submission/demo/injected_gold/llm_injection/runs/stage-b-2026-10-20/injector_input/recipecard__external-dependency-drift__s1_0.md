# Injection task

corpus repository: `recipecard`

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
  README.md, docs/api.md, docs/guide.md, examples/pancakes.yaml, pyproject.toml, recipecard/__init__.py, recipecard/cli.py, recipecard/loader.py, recipecard/models.py, recipecard/scaling.py, recipecard/shopping.py, recipecard/units.py, spec.json
symbols:
  recipecard.cli.main, recipecard.loader.load_recipe, recipecard.loader.load_recipes, recipecard.models.Ingredient, recipecard.models.Recipe, recipecard.scaling.scale_quantity, recipecard.scaling.scale_recipe, recipecard.shopping.ShoppingList, recipecard.shopping.build_shopping_list, recipecard.units.normalize_unit
dependencies:
  click>=8.1, pyyaml>=6.0
string literals:
  0.3.0, Module recipecard/cli.py., Module recipecard/loader.py., Module recipecard/models.py., Module recipecard/scaling.py., Module recipecard/shopping.py., Module recipecard/units.py., Package recipecard., Project class., Project function., known_units

## Document excerpts

### README.md
   1: # recipecard
   2: 
   3: `recipecard` is a small Python library and command-line tool for working with
   4: recipe files. It is meant for home cooks and small scripts that need to:
   5: 
   6: - load a recipe from a YAML file,
   7: - scale its ingredient quantities to a different number of servings, and
   8: - combine several recipes into a single shopping list.
   9: 
  10: The current version is 0.3.0.
  11: 
  12: > **Status:** this is an early release. The public names described in the
  13: > [API reference](docs/api.md) are present, but the function bodies in the
  14: > current source tree are placeholders, so the library does not yet return
  15: > real results. The documentation describes the intended surface.
  16: 
  17: ## Installation
  18: 
  19: `recipecard` requires Python 3.11 or newer. It depends on:
  20: 
  21: - PyYAML `>=6.0`
  22: - click `>=8.1`
  23: 
  24: From a checkout of the project, install it with pip:
  25: 
  26: ```bash
  27: pip install .
  28: ```
  29: 
  30: For development, an editable install works the same way:
  31: 
  32: ```bash
  33: pip install -e .
  34: ```
  35: 
  36: ## Quick start
  37: 
  38: A recipe is a YAML file with a title, a serving count, and a list of
  39: ingredients. The repository includes one at `examples/pancakes.yaml`:
  40: 
  41: ```yaml
  42: title: Pancakes
  43: servings: 4
  44: ingredients:
  45:   - name: flour
  46:     quantity: 240
  47:     unit: g
  48:   - name: milk
  49:     quantity: 300
  50:     unit: ml
  51:   - name: egg
  52:     quantity: 2
  53:     unit: whole
  54: ```
  55: 
  56: Import the public names from their modules:
  57: 
  58: ```python
  59: from recipecard.loader import load_recipe
  60: from recipecard.scaling import scale_recipe
  61: from recipecard.shopping import build_shopping_list
  62: ```
  63: 
  64: The main steps are to load a recipe with `load_recipe`, scale it with
  65: `scale_recipe`, and combine recipes with `build_shopping_list`.
  66: 
  67: ## Documentation
  68: 
  69: - [User guide](docs/guide.md): the recipe file format, units, and how the
  70:   pieces fit together.
  71: - [API reference](docs/api.md): every public class and function.
  72: 
  73: ## License
  74: 
  75: No license file is included in this source tree.
### docs/api.md
   1: # API reference
   2: 
   3: All public names below are importable from the module listed for each entry.
   4: The package version is available as `recipecard.__version__` (`"0.3.0"`).
   5: 
   6: Note that the function bodies in the current source tree are placeholders
   7: that return `None`. The signatures and return types below are the ones
   8: declared in the source.
   9: 
  10: ## `recipecard.models`
  11: 
  12: ### `Ingredient`
  13: 
  14: A single ingredient line in a recipe.
  15: 
  16: Attributes:
  17: 
  18: | Attribute  | Description                                  |
  19: | ---------- | -------------------------------------------- |
  20: | `name`     | The ingredient name.                         |
  21: | `quantity` | The amount of the ingredient.                |
  22: | `unit`     | The unit of `quantity`, as a string.         |
  23: 
  24: The constructor takes no arguments in the current source; each attribute is
  25: set to `None` when an instance is created.
  26: 
  27: ### `Recipe`
  28: 
  29: A recipe, with a title, a serving count, and its ingredients.
  30: 
  31: Attributes:
  32: 
  33: | Attribute     | Description                                |
  34: | ------------- | ------------------------------------------ |
  35: | `title`       | The recipe title.                          |
  36: | `servings`    | The number of servings.                    |
  37: | `ingredients` | The ingredients, as `Ingredient` objects.  |
  38: 
  39: The constructor takes no arguments in the current source; each attribute is
  40: set to `None` when an instance is created.
  41: 
  42: ## `recipecard.units`
  43: 
  44: ### `KNOWN_UNITS`
  45: 
  46: A module-level constant intended to hold the known units. In the current
  47: source it is the string `"known_units"`.
  48: 
  49: ### `normalize_unit() -> str`
  50: 
  51: Returns a normalized unit string. The current source declares no parameters
  52: and returns `None`.
  53: 
  54: ## `recipecard.loader`
  55: 
  56: ### `load_recipe() -> Recipe`
  57: 
  58: Loads a single recipe. The current source declares no parameters and returns
  59: `None`.
  60: 
  61: ### `load_recipes() -> list[Recipe]`
  62: 
  63: Loads several recipes. The current source declares no parameters and returns
  64: `None`.
  65: 
  66: ## `recipecard.scaling`
  67: 
  68: ### `scale_quantity() -> float`
  69: 
  70: Scales a single ingredient quantity to a new serving count. The current source
  71: declares no parameters and returns `None`.
  72: 
  73: ### `scale_recipe() -> Recipe`
  74: 
  75: Scales a recipe's ingredients to a new serving count and returns the resulting
  76: `Recipe`. The current source declares no parameters and returns `None`.
  77: 
  78: ## `recipecard.shopping`
  79: 
  80: ### `ShoppingList`
  81: 
  82: A shopping list. It has one attribute:
  83: 
  84: | Attribute | Description                              |
  85: | --------- | ---------------------------------------- |
  86: | `items`   | The combined ingredients on the list.    |
  87: 
  88: The constructor takes no arguments in the current source; `items` is set to
  89: `None` when an instance is created.
  90: 
  91: ### `build_shopping_list() -> ShoppingList`
  92: 
  93: Builds a `ShoppingList` from one or more recipes. The current source declares
  94: no parameters and returns `None`.
  95: 
  96: ## `recipecard.cli`
  97: 
  98: ### `main() -> int`
  99: 
 100: The command-line entry point. The current source declares no parameters and
 101: returns `None`. No console script is registered in `pyproject.toml`.
### docs/guide.md
   1: # User guide
   2: 
   3: This guide covers the recipe file format and the three tasks `recipecard` is
   4: built around: loading recipes, scaling them, and building shopping lists. For
   5: the exact names and signatures, see the [API reference](api.md).
   6: 
   7: ## Recipe files
   8: 
   9: A recipe file is a YAML document with three top-level keys:
  10: 
  11: | Key           | Description                                      |
  12: | ------------- | ------------------------------------------------ |
  13: | `title`       | The name of the recipe, such as `Pancakes`.      |
  14: | `servings`    | The number of servings the listed quantities make. |
  15: | `ingredients` | A list of ingredient entries.                    |
  16: 
  17: Each entry in `ingredients` has three keys:
  18: 
  19: | Key        | Description                                        |
  20: | ---------- | -------------------------------------------------- |
  21: | `name`     | The ingredient, such as `flour`.                   |
  22: | `quantity` | The amount, as a number.                           |
  23: | `unit`     | The unit of the quantity, such as `g`, `ml`, or `whole`. |
  24: 
  25: The file `examples/pancakes.yaml` in the repository shows a complete recipe:
  26: 
  27: ```yaml
  28: title: Pancakes
  29: servings: 4
  30: ingredients:
  31:   - name: flour
  32:     quantity: 240
  33:     unit: g
  34:   - name: milk
  35:     quantity: 300
  36:     unit: ml
  37:   - name: egg
  38:     quantity: 2
  39:     unit: whole
  40: ```
  41: 
  42: The three keys and the entry fields above are the ones the `Recipe` and
  43: `Ingredient` classes carry (see [`Recipe`](api.md#recipe) and
  44: [`Ingredient`](api.md#ingredient)).
  45: 
  46: ## Units
  47: 
  48: Units are plain strings. The `recipecard.units` module defines a `KNOWN_UNITS`
  49: constant and a `normalize_unit` function for working with them. The current
  50: source defines `KNOWN_UNITS` as a placeholder string, so it is not yet a
  51: usable list of units. The example recipe uses `g`, `ml`, and `whole`.
  52: 
  53: ## Loading recipes
  54: 
  55: `load_recipe` reads one recipe and returns a `Recipe`. `load_recipes` is the
  56: multi-recipe counterpart and returns a `list[Recipe]`. Both are in
  57: `recipecard.loader`.
  58: 
  59: ## Scaling
  60: 
  61: Scaling changes the quantities of a recipe to a new serving count.
  62: 
  63: - `scale_quantity` returns a single quantity as a `float`.
  64: - `scale_recipe` returns a `Recipe` whose ingredients are scaled.
  65: 
  66: Both live in `recipecard.scaling`.
  67: 
  68: ## Shopping lists
  69: 
  70: `build_shopping_list` combines recipes into a `ShoppingList`, which holds the
  71: combined ingredients in its `items` attribute. The function and the class are
  72: in `recipecard.shopping`.
  73: 
  74: ## Command-line interface
  75: 
  76: The package contains `recipecard.cli`, which defines a `main` function that
  77: returns an `int`. The current source body of `main` is a placeholder, and the
  78: project does not declare a console script in `pyproject.toml`, so there is no
  79: `recipecard` executable installed by the package at this version. Use the
  80: Python functions described in the [API reference](api.md) instead.

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

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
docs/development.md (doc)
  - 
  + - (Optional) VULKAN GPU support
  +     - [VULKAN SDK](https://vulkan.lunarg.com/sdk/home) - useful for AMD/Intel GPUs
  + > Building for Vulkan requires VULKAN_SDK environment variable:
  + > 
  + > PowerShell
  + > ```powershell
  + > $env:VULKAN_SDK="C:\VulkanSDK\<version>"
  + > ```

### example 3
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

### example 4
docs/capabilities/web-search.mdx (doc)
  - const results = await client.webSearch({ query: "what is ollama?" });
  - const fetchResult = await client.webFetch({ url: "https://ollama.com" });
  + const results = await client.webSearch("what is ollama?");
  + const fetchResult = await client.webFetch("https://ollama.com");

