# Injection task

corpus repository: `plotline`

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

# Injector — removed-referent drift

**Defect.** A document names a class or function as current API, but that
definition is deleted from the code. The document is left unchanged, so it names
something that no longer exists.

- **Artifact:** a class or function defined in the repository.
- **Direction:** change the code; leave the document unchanged.

## What to look for

Choose a statement that presents a class or function as current, available API.
Do not choose a name that is already described as deprecated, historical, or
illustrative.

The mutation removes a **definition** (a top-level class or function), not a
method or an attribute. Prefer a definition that is not imported or called
elsewhere, so the rest of the tree still parses after the removal.

## The change

Delete the definition as a whole block. The old name must be absent after the
change and the file must still parse. The document line must still name the
**deleted** symbol.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "removed-referent-drift",
  "direction": "code_side",
  "file": "<source file that defines the symbol>",
  "old": "<the name as the document writes it>",
  "new": null,
  "symbol": "<bare symbol name>",
  "target": "<the exact name text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the removal falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-API statement>"
}
```

If no natural current-API statement exists, emit:

```json
{"injectable": false, "reason": "<short reason>"}
```

## Repository inventory

files:
  README.md, docs/api.md, docs/guide.md, plotline/__init__.py, plotline/canvas.py, plotline/marks.py, plotline/palette.py, plotline/render.py, plotline/scales.py, pyproject.toml, spec.json
symbols:
  plotline.canvas.Canvas, plotline.marks.BarMark, plotline.marks.LineMark, plotline.palette.categorical_colors, plotline.render.render_svg, plotline.render.write_svg, plotline.scales.LinearScale, plotline.scales.nice_ticks
dependencies:
  numpy>=1.24
string literals:
  0.4.2, Module plotline/canvas.py., Module plotline/marks.py., Module plotline/palette.py., Module plotline/render.py., Module plotline/scales.py., Package plotline., Project class., Project function., category_colors, default_background

## Document excerpts

### README.md
   1: # plotline
   2: 
   3: plotline is a small Python library of SVG chart primitives. It is meant for
   4: building line and bar charts as plain SVG markup. The package is at version 0.4.2.
   5: 
   6: The library is organized as a handful of building blocks:
   7: 
   8: - a `Canvas` that holds the drawing size and background,
   9: - a `LinearScale` that maps data values onto drawing coordinates,
  10: - `nice_ticks` for picking axis tick values,
  11: - `LineMark` and `BarMark` for the two supported chart types,
  12: - a categorical palette, and
  13: - `render_svg` and `write_svg` for producing the final markup.
  14: 
  15: See the [user guide](docs/guide.md) for how these pieces fit together and the
  16: [API reference](docs/api.md) for every public name.
  17: 
  18: ## Installation
  19: 
  20: plotline requires Python 3.11 or newer and declares a dependency on
  21: `numpy>=1.24`. Install it from a local checkout with pip:
  22: 
  23: ```bash
  24: pip install .
  25: ```
  26: 
  27: For development, an editable install works as well:
  28: 
  29: ```bash
  30: pip install -e .
  31: ```
  32: 
  33: ## Quick start
  34: 
  35: Every public name is importable from its module under the `plotline` package:
  36: 
  37: ```python
  38: from plotline.canvas import Canvas
  39: from plotline.marks import LineMark, BarMark
  40: from plotline.render import render_svg, write_svg
  41: ```
  42: 
  43: A minimal session creates a canvas, a mark, and renders the result:
  44: 
  45: ```python
  46: from plotline.canvas import Canvas
  47: from plotline.marks import LineMark
  48: from plotline.render import render_svg
  49: 
  50: canvas = Canvas()
  51: line = LineMark()
  52: svg_text = render_svg()
  53: ```
  54: 
  55: > **Note:** In the current release the constructors take no arguments, and
  56: > the functions take no arguments and their bodies return `None`. The names
  57: > and attributes described in the [API reference](docs/api.md) are what the
  58: > package currently defines; the rendering behavior is not implemented yet.
  59: 
  60: ## Documentation
  61: 
  62: - [User guide](docs/guide.md): concepts, coordinates and scales, and a
  63:   typical workflow.
  64: - [API reference](docs/api.md): every public module, class, constant and
  65:   function.
### docs/api.md
   1: # plotline API reference
   2: 
   3: All public names live in the `plotline` package, in the modules listed below.
   4: The package itself exports nothing at the top level; import from the module.
   5: 
   6: ## `plotline.canvas`
   7: 
   8: ### `class Canvas`
   9: 
  10: ```python
  11: from plotline.canvas import Canvas
  12: ```
  13: 
  14: A drawing surface. `Canvas()` takes no arguments.
  15: 
  16: | Attribute | Description |
  17: |---|---|
  18: | `width` | Drawing width. Set to `None` by the constructor. |
  19: | `height` | Drawing height. Set to `None` by the constructor. |
  20: | `background` | Background of the drawing. Set to `None` by the constructor. |
  21: 
  22: ### `DEFAULT_BACKGROUND`
  23: 
  24: The string constant `"default_background"`. It is the default background
  25: value named by this module.
  26: 
  27: ## `plotline.scales`
  28: 
  29: ### `class LinearScale`
  30: 
  31: ```python
  32: from plotline.scales import LinearScale
  33: ```
  34: 
  35: A linear mapping between a data domain and a drawing range. `LinearScale()`
  36: takes no arguments.
  37: 
  38: | Attribute | Description |
  39: |---|---|
  40: | `domain_min` | Lower bound of the data domain. Set to `None` by the constructor. |
  41: | `domain_max` | Upper bound of the data domain. Set to `None` by the constructor. |
  42: | `range_min` | Lower bound of the drawing range. Set to `None` by the constructor. |
  43: | `range_max` | Upper bound of the drawing range. Set to `None` by the constructor. |
  44: 
  45: ### `nice_ticks() -> list[float]`
  46: 
  47: Intended to return round tick values for an axis. Takes no arguments in
  48: this release, and the body currently returns `None`.
  49: 
  50: ## `plotline.marks`
  51: 
  52: ### `class LineMark`
  53: 
  54: ```python
  55: from plotline.marks import LineMark
  56: ```
  57: 
  58: A line series. `LineMark()` takes no arguments.
  59: 
  60: | Attribute | Description |
  61: |---|---|
  62: | `xs` | X values of the line. Set to `None` by the constructor. |
  63: | `ys` | Y values of the line. Set to `None` by the constructor. |
  64: | `stroke` | Stroke color of the line. Set to `None` by the constructor. |
  65: 
  66: ### `class BarMark`
  67: 
  68: ```python
  69: from plotline.marks import BarMark
  70: ```
  71: 
  72: A bar series. `BarMark()` takes no arguments.
  73: 
  74: | Attribute | Description |
  75: |---|---|
  76: | `labels` | Labels for the bars. Set to `None` by the constructor. |
  77: | `values` | Values for the bars. Set to `None` by the constructor. |
  78: | `fill` | Fill color of the bars. Set to `None` by the constructor. |
  79: 
  80: ## `plotline.palette`
  81: 
  82: ### `CATEGORY_COLORS`
  83: 
  84: The string constant `"category_colors"`, the name of the categorical palette.
  85: 
  86: ### `categorical_colors() -> list[str]`
  87: 
  88: ```python
  89: from plotline.palette import categorical_colors
  90: ```
  91: 
  92: Intended to return the list of colors for distinct series. Takes no
  93: arguments in this release, and the body currently returns `None`.
  94: 
  95: ## `plotline.render`
  96: 
  97: ### `render_svg() -> str`
  98: 
  99: ```python
 100: from plotline.render import render_svg
 101: ```
 102: 
 103: Intended to return the SVG markup for a chart. Takes no arguments in this
 104: release, and the body currently returns `None`.
 105: 
 106: ### `write_svg() -> None`
 107: 
 108: ```python
 109: from plotline.render import write_svg
 110: ```
 111: 
 112: Intended to write SVG markup to a file. Takes no arguments in this release,
 113: and the body currently returns `None`.
### docs/guide.md
   1: # plotline user guide
   2: 
   3: This guide explains the main ideas behind plotline and how the pieces are
   4: meant to fit together. For signatures and attribute lists, see the
   5: [API reference](api.md).
   6: 
   7: ## The model
   8: 
   9: plotline builds charts from a few small objects rather than from a single
  10: chart call:
  11: 
  12: | Piece | Module | Role |
  13: |---|---|---|
  14: | `Canvas` | `plotline.canvas` | Drawing size and background. |
  15: | `LinearScale` | `plotline.scales` | Maps a data domain onto a drawing range. |
  16: | `nice_ticks` | `plotline.scales` | Chooses tick values for an axis. |
  17: | `LineMark` | `plotline.marks` | A line series: x values, y values, stroke. |
  18: | `BarMark` | `plotline.marks` | A bar series: labels, values, fill. |
  19: | `categorical_colors` | `plotline.palette` | Colors for distinct series. |
  20: | `render_svg`, `write_svg` | `plotline.render` | Produce SVG markup, or write it to a file. |
  21: 
  22: ## Coordinates and scales
  23: 
  24: Data values and drawing coordinates are different spaces. A
  25: `LinearScale` describes the mapping between them with four attributes:
  26: 
  27: - `domain_min` and `domain_max`: the range of data values.
  28: - `range_min` and `range_max`: the range of drawing coordinates they map to.
  29: 
  30: The names follow the usual linear-scale convention, where a data value
  31: between `domain_min` and `domain_max` is placed proportionally between
  32: `range_min` and `range_max`. The current source only defines these
  33: attributes; the mapping itself is not implemented yet.
  34: 
  35: `nice_ticks` is intended to pick round tick values for an axis covering a
  36: domain, so that axis labels are easy to read. Like the other functions in
  37: this release, it is a placeholder and does not yet return tick values.
  38: 
  39: The `Canvas` holds the overall `width`, `height`, and `background` of the
  40: drawing.
  41: 
  42: ## Marks
  43: 
  44: plotline has two mark types.
  45: 
  46: - `LineMark` describes a line series with `xs`, `ys`, and `stroke`.
  47: - `BarMark` describes a bar series with `labels`, `values`, and `fill`.
  48: 
  49: Each mark is created empty and its attributes are filled in by the caller.
  50: 
  51: ## Colors
  52: 
  53: `plotline.palette` provides a categorical palette. The module-level
  54: constant `CATEGORY_COLORS` is the palette's name, and `categorical_colors()`
  55: is the function that returns the list of colors for distinct series.
  56: 
  57: ## Rendering and output
  58: 
  59: `render_svg()` is meant to return the SVG markup for a chart as a `str`.
  60: `write_svg()` is meant to write that markup to a file. Neither function
  61: accepts arguments in this release, and both are placeholders that return
  62: `None`.
  63: 
  64: ## Typical workflow
  65: 
  66: 1. Create a `Canvas` and set its size and background.
  67: 2. Create a `LinearScale` for each axis and set its domain and range.
  68: 3. Pick ticks with `nice_ticks` and colors with `categorical_colors`.
  69: 4. Create one or more `LineMark` or `BarMark` objects and fill them in.
  70: 5. Render the chart with `render_svg`, or save it with `write_svg`.
  71: 
  72: Because the functions are placeholders in this release, the workflow above
  73: describes the intended use of the API rather than output you can produce
  74: today.

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

### example 1
classic/forge/forge/llm/providers/groq.py (code)
  -     LLAMA3_8B = "llama3-8b-8192"
  -     LLAMA3_70B = "llama3-70b-8192"
  -         ChatModelInfo(
  -             name=GroqModelName.LLAMA3_8B,
  -             provider_name=ModelProviderName.GROQ,
  -             prompt_token_cost=0.05 / 1e6,
  -             completion_token_cost=0.10 / 1e6,
  -             max_tokens=8192,

### example 2
cmd/tui/tui.go (code)
  - 	"github.com/ollama/ollama/internal/modelref"
  - 	if name == "" {
  - 		return false
  - 	}
  - 	if modelref.HasExplicitCloudSource(name) {
  - 		return true
  - 	}
  - 	if m.availableModels == nil {
  + 	if m.availableModels == nil || name == "" {
  + 	return strings.HasSuffix(name, ":cloud") || strings.HasSuffix(name, "-cloud")
server/create.go (code)
  - 			fromRef, err := parseAndValidateModelRef(r.From)
  - 			if err != nil {
  - 
  - 			fromName := fromRef.Name
  - 			remoteHost := r.RemoteHost
  - 			if fromRef.Source == modelSourceCloud && remoteHost == "" {
  - 				remoteHost = cloudProxyBaseURL
  - 			}
  + 			fromName := model.ParseName(r.From)
  + 			if !fromName.IsValid() {
  + 			if r.RemoteHost != "" {
  + 				ru, err := remoteURL(r.RemoteHost)
  + 				config.RemoteModel = r.From

### example 3
Documentation/dev-tools/kasan.rst (doc)
  - For slab, both software KASAN modes support SLUB and SLAB allocators, while
  - Hardware Tag-Based KASAN only supports SLUB.
  - 

### example 4
Documentation/admin-guide/mm/kho.rst (doc)
  - First, before you perform a KHO kexec, you need to move the system into
  - the :ref:`KHO finalization phase <kho-finalization-phase>` ::
  - 
  -   $ echo 1 > /sys/kernel/debug/kho/out/finalize
  - 
  - After this command, the KHO FDT is available in
  - ``/sys/kernel/debug/kho/out/fdt``. Other subsystems may also register
  - their own preserved sub FDTs under
  + To perform a KHO kexec, load the target payload and kexec into it. It
  + is important that you use the ``-s`` parameter to use the in-kernel
  + kexec file loader, as user space kexec tooling currently has no
  + support for KHO with the user space based file loader ::
  + These debugfs interfaces are available when the kernel is compiled with
  + ``CONFIG_KEXEC_HANDOVER_DEBUGFS`` enabled.
  + 
  +     The kernel exposes the flattened device tree blob that carries its

