# Injection task

corpus repository: `contourkit`

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

# Injector — path-location drift

**Defect.** A document points to a file or directory as a current location, but
that file or directory is renamed or moved. The document is left unchanged, so it
now points at a location that no longer exists.

- **Artifact:** a file or directory path.
- **Direction:** change the repository tree; leave the document unchanged.

## What to look for

Choose a statement that presents a location as current — for example, "the guide
is at …", "configuration lives in …", "the example data is in …", or a command
that names a path. Do not choose a path that the document explicitly describes as
historical, illustrative, or already gone.

## The change

Rename or move the file/directory to a plausible new name or location. Keep the
same kind of artifact (a file stays a file; a directory stays a directory). The
old path must be gone after the change and the new path must exist. The document
line must still contain the **old** path.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "path-location-drift",
  "direction": "code_side",
  "file": "<old path, relative to the repository>",
  "old": "<old path, relative to the repository>",
  "new": "<new path, relative to the repository>",
  "target": "<the exact path text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the change falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-location statement>"
}
```

If no natural current-location statement exists, emit:

```json
{"injectable": false, "reason": "<short reason>"}
```

## Repository inventory

files:
  README.md, contourkit/__init__.py, contourkit/cli.py, contourkit/geometry.py, contourkit/marching.py, contourkit/raster.py, contourkit/sampling.py, contourkit/simplify.py, docs/api.md, docs/walkthrough.md, examples/terrain.asc, pyproject.toml, spec.json
symbols:
  contourkit.cli.main, contourkit.geometry.Polyline, contourkit.geometry.close_ring, contourkit.geometry.polyline_length, contourkit.marching.contour_levels, contourkit.marching.trace_contour, contourkit.raster.ElevationRaster, contourkit.raster.load_ascii_grid, contourkit.sampling.gradient_magnitude, contourkit.sampling.sample_bilinear, contourkit.sampling.sample_nearest, contourkit.simplify.douglas_peucker, contourkit.simplify.simplify_contours
dependencies:
  click>=8.1, numpy>=1.26
string literals:
  0.4.1, Module contourkit/cli.py., Module contourkit/geometry.py., Module contourkit/marching.py., Module contourkit/raster.py., Module contourkit/sampling.py., Module contourkit/simplify.py., Package contourkit., Project class., Project function., default_nodata, default_tolerance

## Document excerpts

### README.md
   1: # contourkit
   2: 
   3: contourkit is a small Python library for turning elevation rasters into
   4: lightweight contour geometry. It is built around four steps that map onto four
   5: modules: read a raster into an array plus its georeferencing, sample the surface
   6: at arbitrary points, trace polylines at chosen elevations, and simplify those
   7: polylines before they go into a map.
   8: 
   9: It is aimed at people who need contour lines for a tile, a printed map, or a
  10: vector layer, and who would rather have a handful of explicit functions than a
  11: full GIS stack. There is no map rendering, no projection code, and no file
  12: format support beyond the ESRI ASCII grid reader.
  13: 
  14: The current release is **0.4.1**. It publishes the module layout, class
  15: attributes, and function signatures described in [docs/api.md](docs/api.md);
  16: the computational routines are placeholders at this stage. `load_ascii_grid`,
  17: `contour_levels`, `trace_contour`, `simplify_contours` and the sampling helpers
  18: all return `None` today, and the example below reflects that.
  19: 
  20: ## Installation
  21: 
  22: contourkit requires Python 3.11 or newer. Runtime dependencies are
  23: `numpy>=1.26` and `click>=8.1`.
  24: 
  25: From a checkout of this repository:
  26: 
  27: ```bash
  28: pip install -e .
  29: ```
  30: 
  31: The package is built with setuptools (`setuptools>=68`).
  32: 
  33: To check that the install worked:
  34: 
  35: ```python
  36: >>> import contourkit
  37: >>> contourkit.__version__
  38: '0.4.1'
  39: ```
  40: 
  41: ## Quick start
  42: 
  43: ```python
  44: from contourkit import __version__
  45: from contourkit.raster import load_ascii_grid, DEFAULT_NODATA
  46: from contourkit.geometry import Polyline
  47: from contourkit.marching import contour_levels
  48: 
  49: print(__version__)      # 0.4.1
  50: print(DEFAULT_NODATA)   # default_nodata
  51: 
  52: raster = load_ascii_grid()
  53: 
  54: # A Polyline carries a list of points and the elevation it belongs to.
  55: line = Polyline()
  56: line.points = [(0.0, 0.0), (10.0, 5.0)]
  57: line.level = 120.0
  58: ```
  59: 
  60: A full contour run follows the same shape:
  61: 
  62: ```python
  63: from contourkit.raster import load_ascii_grid
  64: from contourkit.marching import contour_levels, trace_contour
  65: from contourkit.simplify import simplify_contours
  66: 
  67: raster = load_ascii_grid()
  68: levels = contour_levels()
  69: contours = trace_contour()
  70: light = simplify_contours()
  71: ```
  72: 
  73: In 0.4.1 each of these returns `None`, so the pipeline wires up but produces no
  74: geometry yet. The signatures are what the package commits to; see
  75: [docs/api.md](docs/api.md) for the exact surface.
  76: 
  77: ## Main concepts
  78: 
  79: **Raster.** An `ElevationRaster` holds `data` (the elevation values),
  80: `transform` (the georeferencing that maps cell indices to map coordinates), and
  81: `nodata` (the value marking missing cells). `load_ascii_grid()` builds one from
  82: an ESRI ASCII grid. The module constant `DEFAULT_NODATA` is the fallback nodata
  83: marker, currently the string `"default_nodata"`.
  84: 
  85: **Sampling.** `contourkit.sampling` reads the surface between cells:
  86: `sample_nearest` takes a cell value as-is, `sample_bilinear` interpolates
  87: between neighbouring cells, and `gradient_magnitude` reports how steep the
  88: surface is at a point, which is what you want for hillshading or for choosing
  89: where contours will crowd together.
  90: 
  91: **Contour tracing.** `contour_levels()` chooses the elevations to draw, and
  92: `trace_contour()` traces the isolines at those elevations. Each traced line is
  93: returned as a `Polyline`.
  94: 
  95: **Polylines.** A `Polyline` has two attributes: `points`, the ordered
  96: coordinates that make up the line, and `level`, the elevation it was traced at.
  97: `polyline_length` measures one, and `close_ring` turns an open line into a
  98: closed loop for filled or outlined areas.
  99: 
 100: **Simplification.** `douglas_peucker` thins a single polyline while keeping its
 101: shape, and `simplify_contours` applies that to a whole contour set. The
 102: tolerance you pass controls how aggressively points are dropped; the command
 103: module exposes a fallback through `DEFAULT_TOLERANCE`.
 104: 
 105: ## The example grid
 106: 
 107: `examples/terrain.asc` is a 5 × 5 ESRI ASCII grid with a header of `ncols 5`,
 108: `nrows 5`, `xllcorner 0`, `yllcorner 0`, `cellsize 10`, and
 109: `NODATA_value -9999`, followed by elevations from 100 to 140. With a cell size
 110: of 10 it covers 50 × 50 map units, and its values rise smoothly, which makes it
 111: a convenient fixture for trying the tracer.
 112: 
 113: ## Command line
 114: 
 115: `contourkit.cli` provides `main()`, which returns an integer exit code, and the
 116: `DEFAULT_TOLERANCE` constant. The package does not declare a `console_scripts`
 117: entry point and has no `__main__` module, so in 0.4.1 you invoke the entry point
 118: from Python:
 119: 
 120: ```python
 121: import sys
 122: from contourkit.cli import main
 123: 
 124: sys.exit(main())
 125: ```
 126: 
 127: ## Documentation
 128: 
 129: - [docs/walkthrough.md](docs/walkthrough.md) — a step-by-step tour of the
 130:   contour pipeline using `examples/terrain.asc`.
 131: - [docs/api.md](docs/api.md) — the public classes, functions, and constants.
### docs/api.md
   1: # contourkit API reference
   2: 
   3: Version 0.4.1. Python 3.11 or newer.
   4: 
   5: The package is organised as five computation modules plus a command module.
   6: Import from the module that owns a symbol; the top-level `contourkit` package
   7: exports only `__version__`:
   8: 
   9: ```python
  10: >>> import contourkit
  11: >>> contourkit.__version__
  12: '0.4.1'
  13: ```
  14: 
  15: > **State of the 0.4.1 surface.** Every function in this release is declared with
  16: > an empty parameter list and a return annotation, and every body currently
  17: > returns `None`. The annotations below describe the type each call is committed
  18: > to producing; treat them as the contract, not as behaviour you can observe
  19: > today. Constructors and constants are fully implemented as described.
  20: 
  21: ## Modules at a glance
  22: 
  23: | Module | Contents |
  24: | --- | --- |
  25: | `contourkit.raster` | `ElevationRaster`, `load_ascii_grid`, `DEFAULT_NODATA` |
  26: | `contourkit.sampling` | `sample_nearest`, `sample_bilinear`, `gradient_magnitude` |
  27: | `contourkit.marching` | `contour_levels`, `trace_contour` |
  28: | `contourkit.geometry` | `Polyline`, `polyline_length`, `close_ring` |
  29: | `contourkit.simplify` | `douglas_peucker`, `simplify_contours` |
  30: | `contourkit.cli` | `main`, `DEFAULT_TOLERANCE` |
  31: 
  32: ## contourkit.raster
  33: 
  34: ### `class ElevationRaster()`
  35: 
  36: An elevation grid together with its georeferencing and its missing-data marker.
  37: 
  38: ```python
  39: from contourkit.raster import ElevationRaster
  40: 
  41: raster = ElevationRaster()
  42: ```
  43: 
  44: `__init__` takes no arguments and sets three public attributes, each initially
  45: `None`:
  46: 
  47: | Attribute | Meaning |
  48: | --- | --- |
  49: | `data` | the elevation values |
  50: | `transform` | the mapping from cell indices to map coordinates |
  51: | `nodata` | the value that marks cells with no measurement |
  52: 
  53: Assign them directly when you are constructing a raster by hand:
  54: 
  55: ```python
  56: raster.data = [[100, 104], [106, 110]]
  57: raster.nodata = -9999
  58: ```
  59: 
  60: ### `load_ascii_grid() -> ElevationRaster`
  61: 
  62: Reads an ESRI ASCII grid into an `ElevationRaster`. Takes no arguments in
  63: 0.4.1. Returns `None` in the current release.
  64: 
  65: An ESRI ASCII grid is a text file with a six-line header — `ncols`, `nrows`,
  66: `xllcorner`, `yllcorner`, `cellsize`, `NODATA_value` — followed by one
  67: whitespace-separated row of values per line. `examples/terrain.asc` in this
  68: repository is an example. See the walkthrough for a line-by-line reading of that
  69: header.
  70: 
  71: ### `DEFAULT_NODATA`
  72: 
  73: ```python
  74: >>> from contourkit.raster import DEFAULT_NODATA
  75: >>> DEFAULT_NODATA
  76: 'default_nodata'
  77: ```
  78: 
  79: The fallback marker used for missing cells when a grid does not supply its own.
  80: It is a string, not a number.
  81: 
  82: ## contourkit.sampling
  83: 
  84: Point sampling of the elevation surface. All three functions take no arguments
  85: in 0.4.1 and return `None`; their annotations are `float`.
  86: 
  87: ### `sample_nearest() -> float`
  88: 
  89: Reads the surface without interpolation: the value of the cell containing the
  90: point. Use it when you want the stored measurements untouched.
  91: 
  92: ### `sample_bilinear() -> float`
  93: 
  94: Reads the surface by interpolating across neighbouring cells. Use it when you
  95: want a smooth surface; nearest-neighbour sampling on a coarse grid produces
  96: plateaus that show up as stair-stepped contours.
  97: 
  98: ### `gradient_magnitude() -> float`
  99: 
 100: The magnitude of the surface gradient at the point — how steep the terrain is.
 101: Useful for shading and for anticipating where contour lines will bunch together.
 102: 
 103: ## contourkit.marching
 104: 
 105: ### `contour_levels() -> list[float]`
 106: 
 107: Returns the elevations to trace. Takes no arguments in 0.4.1 and returns `None`
 108: in the current release.
 109: 
 110: The list is the input to the tracer: every elevation in it becomes one or more
 111: polylines. Keeping it explicit lets a caller drop levels that fall outside the
 112: data range or that would only produce edge slivers.
 113: 
 114: ### `trace_contour() -> list[Polyline]`
 115: 
 116: Returns the traced contours, one `Polyline` per connected line, each carrying the
 117: elevation it was traced at in its `level` attribute. Takes no arguments in 0.4.1
 118: and returns `None` in the current release.
 119: 
 120: A single elevation can yield several polylines, so the result is not one entry
 121: per requested level. The `Polyline` type lives in `contourkit.geometry`.
 122: 
 123: ## contourkit.geometry
 124: 
 125: ### `class Polyline()`
 126: 
 127: One traced contour line.
 128: 
 129: ```python
 130: from contourkit.geometry import Polyline
 131: 
 132: line = Polyline()
 133: line.points = [(0.0, 0.0), (10.0, 5.0)]
 134: line.level = 120.0
 135: ```
 136: 
 137: `__init__` takes no arguments and sets two public attributes, both initially
 138: `None`:
 139: 
 140: | Attribute | Meaning |
 141: | --- | --- |
 142: | `points` | ordered coordinates making up the line |
 143: | `level` | the elevation the line was traced at |
 144: 
 145: A polyline whose first and last point coincide is a closed ring.
 146: 
 147: ### `polyline_length() -> float`
 148: 
 149: The total length of a polyline, in map units. Takes no arguments in 0.4.1 and
 150: returns `None` in the current release.
 151: 
 152: ### `close_ring() -> Polyline`
 153: 
 154: The closed form of a polyline, for contours that enclose an area. Takes no
 155: arguments in 0.4.1 and returns `None` in the current release.
 156: 
 157: ## contourkit.simplify
 158: 
 159: Both functions take no arguments in 0.4.1 and return `None` in the current
 160: release. Their annotations name the types they are committed to returning.
 161: 
 162: ### `douglas_peucker() -> Polyline`
 163: 
 164: Simplifies a single polyline, dropping points that lie within the tolerance of
 165: the line through their neighbours.
 166: 
 167: ### `simplify_contours() -> list[Polyline]`
 168: 
 169: Simplifies a whole contour set and returns the result as a list of `Polyline`.
 170: 
 171: Simplify after tracing. Removing points before the tracer runs discards the
 172: detail it uses to place a line correctly.
 173: 
 174: ## contourkit.cli
 175: 
 176: ### `main() -> int`
 177: 
 178: The command entry point. Takes no arguments and returns an integer exit code, so
 179: it can be passed straight to `sys.exit`:
 180: 
 181: ```python
 182: import sys
 183: from contourkit.cli import main
 184: 
 185: sys.exit(main())
 186: ```
 187: 
 188: `pyproject.toml` declares no `console_scripts` entry point and the package has no
 189: `__main__` module, so in 0.4.1 there is no installed `contourkit` command;
 190: `main()` is called in-process. Note that although `click>=8.1` is a declared
 191: dependency of the package, `contourkit/cli.py` does not import it.
 192: 
 193: ### `DEFAULT_TOLERANCE`
 194: 
 195: ```python
 196: >>> from contourkit.cli import DEFAULT_TOLERANCE
 197: >>> DEFAULT_TOLERANCE
 198: 'default_tolerance'
 199: ```
 200: 
 201: The fallback simplification tolerance used when a caller does not supply one.
 202: It is a string, not a number.
 203: 
 204: ## Package metadata
 205: 
 206: - Distribution and import name: `contourkit`
 207: - Version: `0.4.1` (also in `contourkit.__version__`)
 208: - Requires Python: `>=3.11`
 209: - Dependencies: `numpy>=1.26`, `click>=8.1`
 210: - Build backend: setuptools, requiring `setuptools>=68`
 211: - Packaged directory: `contourkit`
### docs/walkthrough.md
   1: # Walkthrough: from an ASCII grid to simplified contours
   2: 
   3: This tutorial walks through the job contourkit exists for: take an elevation
   4: grid, pick the elevations you want to draw, trace lines along them, and thin
   5: those lines so they stay readable on a small map. We use the grid shipped with
   6: the repository, `examples/terrain.asc`.
   7: 
   8: > A note before you start: in release 0.4.1 the computation functions are
   9: > placeholders. They accept no arguments and return `None`, so the calls below
  10: > run but produce no geometry. Work through it anyway — the order of operations
  11: > and the shape of the data are what the package is committing to, and the code
  12: > you write here is the code you will keep once the implementations land.
  13: 
  14: ## 1. Install and check the version
  15: 
  16: From the repository root:
  17: 
  18: ```bash
  19: pip install -e .
  20: ```
  21: 
  22: ```python
  23: >>> import contourkit
  24: >>> contourkit.__version__
  25: '0.4.1'
  26: ```
  27: 
  28: You need Python 3.11 or newer. contourkit depends on `numpy>=1.26` and
  29: `click>=8.1`.
  30: 
  31: ## 2. Read the input file
  32: 
  33: Open `examples/terrain.asc`. It is an ESRI ASCII grid: six header lines, then
  34: one row of elevation values per line, north to south.
  35: 
  36: ```
  37: ncols 5
  38: nrows 5
  39: xllcorner 0
  40: yllcorner 0
  41: cellsize 10
  42: NODATA_value -9999
  43: 100 104 108 112 116
  44: 106 110 114 118 122
  45: 112 116 120 124 128
  46: 118 122 126 130 134
  47: 124 128 132 136 140
  48: ```
  49: 
  50: Three things about this header matter when you read contours off the result:
  51: 
  52: - `ncols 5` and `nrows 5` give the grid size, so there are 25 cells.
  53: - `cellsize 10` is the spacing between cell centres in map units. The grid
  54:   therefore covers 50 × 50 map units, and any coordinate you get back from the
  55:   library is in those units, not in cell indices.
  56: - `NODATA_value -9999` marks cells with no measurement. This grid has none, but
  57:   a real tile usually will, and contour lines must not be traced across those
  58:   gaps.
  … (truncated)

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

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
autogpt_platform/frontend/src/components/renderers/InputRenderer/docs/HEIRARCHY.md (doc)
  + # Input Renderer 2 - Hierarchy
  + 
  + ## Flow Overview
  + 
  + ```
  + FormRenderer2 → Form (RJSF) → ObjectFieldTemplate → FieldTemplate → Widget/Field
  + ```
  + 

### example 3
autogpt_platform/backend/load-tests/README.md (doc)
  - # 4. Verify setup and run quick test
  - node run-tests.js verify
  - # 5. Run tests locally (development/debugging)
  - node run-tests.js run all DEV
  - 
  - # 6. Run tests in k6 cloud (performance testing)
  - node run-tests.js cloud all DEV
  - ## 📋 Unified Test Runner
  + # 4. Run orchestrated load tests locally
  + node orchestrator/orchestrator.js DEV local
  + # 5. Run orchestrated load tests in k6 cloud (recommended)
  + node orchestrator/orchestrator.js DEV cloud
  + ## 📋 Load Test Orchestrator
  + The AutoGPT Platform uses a comprehensive load test orchestrator (`orchestrator/orchestrator.js`) that runs 12 optimized tests with maximum VU counts:
  + # Run 12 optimized tests locally (for debugging)
  + node orchestrator/orchestrator.js DEV local
autogpt_platform/backend/load-tests/orchestrator/orchestrator.js (code)
  + #!/usr/bin/env node
  + 
  + /**
  +  * AutoGPT Platform Load Test Orchestrator
  +  * 
  +  * Optimized test suite with only the highest VU count for each unique test type.
  +  * Eliminates duplicate tests and focuses on maximum load testing.
  +  */

