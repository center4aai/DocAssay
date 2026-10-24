# Injection task

corpus repository: `tileplan`

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
  README.md, docs/api.md, docs/usage.md, examples/bay_area.geojson, pyproject.toml, spec.json, tileplan/__init__.py, tileplan/coords.py, tileplan/cover.py, tileplan/extent.py, tileplan/hierarchy.py, tileplan/quadkey.py, tileplan/zoom.py
symbols:
  tileplan.coords.Tile, tileplan.coords.lonlat_from_tile, tileplan.coords.tile_from_lonlat, tileplan.cover.CoverOptions, tileplan.cover.cover_extent, tileplan.extent.Extent, tileplan.extent.merge_extents, tileplan.extent.tile_extent, tileplan.hierarchy.children, tileplan.hierarchy.descendants, tileplan.hierarchy.parent, tileplan.quadkey.from_quadkey, tileplan.quadkey.to_quadkey, tileplan.zoom.closest_zoom, tileplan.zoom.resolution_at
dependencies:
  (none)
string literals:
  0.4.1, Module tileplan/coords.py., Module tileplan/cover.py., Module tileplan/extent.py., Module tileplan/hierarchy.py., Module tileplan/quadkey.py., Module tileplan/zoom.py., Package tileplan., Project class., Project function., max_zoom

## Document excerpts

### README.md
   1: # tileplan
   2: 
   3: Slippy-map tile coordinates, extents, and zoom arithmetic for tiled map pipelines.
   4: 
   5: `tileplan` is a small, dependency-free library for the coordinate bookkeeping that every
   6: tiled map pipeline ends up writing by hand: which tile contains a lon/lat pair, what
   7: ground area a tile covers, which zoom level matches a desired resolution, how tiles nest
   8: into each other, and which tiles are needed to cover a bounding box. It has no runtime
   9: dependencies and targets Python 3.11 or newer.
  10: 
  11: This release is `0.4.1`.
  12: 
  13: ## Install
  14: 
  15: From a checkout of this repository:
  16: 
  17: ```bash
  18: pip install .
  19: ```
  20: 
  21: Or, while working on the library itself:
  22: 
  23: ```bash
  24: pip install -e .
  25: ```
  26: 
  27: Only the build backend (`setuptools>=68`) is fetched; there are no runtime dependencies
  28: to install.
  29: 
  30: ## Quick start
  31: 
  32: ```python
  33: from tileplan.coords import Tile, tile_from_lonlat, lonlat_from_tile
  34: from tileplan.extent import Extent, tile_extent, merge_extents
  35: from tileplan.zoom import MAX_ZOOM, resolution_at, closest_zoom
  36: from tileplan.hierarchy import children, parent, descendants
  37: from tileplan.quadkey import to_quadkey, from_quadkey
  38: from tileplan.cover import CoverOptions, cover_extent
  39: 
  40: tile = tile_from_lonlat()          # declared return type: Tile
  41: box = tile_extent()                # declared return type: Extent
  42: zoom = closest_zoom()              # declared return type: int
  43: key = to_quadkey()                 # declared return type: str
  44: 
  45: options = CoverOptions()
  46: options.zoom = 10
  47: options.buffer_tiles = 1
  48: options.limit = 256
  49: tiles = cover_extent()             # declared return type: list[Tile]
  50: ```
  51: 
  52: > **Implementation status.** `0.4.1` publishes the interface, not the arithmetic. Every
  53: > function in the package has an empty parameter list and a body that returns `None`,
  54: > and `Tile`/`Extent`/`CoverOptions` are constructed with no arguments and start with
  55: > their documented attributes set to `None`. The module layout, names, attribute sets,
  56: > and return annotations below are stable; code that calls them should treat the values
  57: > as not yet available.
  58: 
  59: ## Concepts
  60: 
  61: **Tiles and zoom levels.** A tile is addressed by three integers: `z` (the zoom level),
  62: `x` (the column) and `y` (the row). At zoom `z` the world is divided into a
  63: `2**z × 2**z` grid, so the number of tiles grows fourfold per level. `tileplan` targets
  64: the usual XYZ / Google / OpenStreetMap convention for the origin of `x` and `y`.
  65: `tileplan.coords.Tile` holds the triple as the attributes `z`, `x`, and `y`.
  66: 
  67: **Extents.** An extent is a geographic bounding box in degrees, stored as `west`,
  68: `south`, `east`, and `north` on `tileplan.extent.Extent`. `tile_extent` maps a tile to
  69: the box it covers; `merge_extents` combines boxes.
  70: 
  71: **Zoom arithmetic.** `tileplan.zoom.resolution_at` relates a zoom level to ground
  72: resolution, and `closest_zoom` picks the best integer level for a requested resolution.
  73: The module exposes the zoom cap as `MAX_ZOOM`; as shipped in `0.4.1` the constant's value
  74: is the string `"max_zoom"` rather than a number.
  75: 
  76: **Tile hierarchy.** Tiles at one zoom nest exactly into tiles at the next:
  77: `children`, `parent`, and `descendants` in `tileplan.hierarchy` move between levels.
  78: 
  79: **Quadkeys.** A quadkey is the string form of a tile address, one digit per zoom level,
  80: which is convenient as a cache key or database column. `to_quadkey` and `from_quadkey`
  81: in `tileplan.quadkey` convert between the two representations.
  82: 
  83: **Covering an extent.** `tileplan.cover` answers "which tiles do I need for this box?".
  84: `CoverOptions` carries the target `zoom`, a `buffer_tiles` margin around the box, and a
  85: `limit` on how many tiles to return; `cover_extent` produces the list.
  86: 
  87: ## Package layout
  88: 
  89: | Module | Contents |
  90: | --- | --- |
  91: | `tileplan/coords.py` | `Tile`, `tile_from_lonlat`, `lonlat_from_tile` |
  92: | `tileplan/extent.py` | `Extent`, `tile_extent`, `merge_extents` |
  93: | `tileplan/zoom.py` | `MAX_ZOOM`, `resolution_at`, `closest_zoom` |
  94: | `tileplan/hierarchy.py` | `children`, `parent`, `descendants` |
  95: | `tileplan/quadkey.py` | `to_quadkey`, `from_quadkey` |
  96: | `tileplan/cover.py` | `CoverOptions`, `cover_extent` |
  97: 
  98: The package version is available as `tileplan.__version__`.
  99: 
 100: ## Example data
 101: 
 102: `examples/bay_area.geojson` is a GeoJSON `FeatureCollection` with a single `Polygon`
 103: feature named `Bay Area view`. Its ring spans longitude `-122.52` to `-122.35` and
 104: latitude `37.70` to `37.83`, which makes it a convenient stand-in for a real extent when
 105: you are sketching a pipeline.
 106: 
 107: ## Further reading
 108: 
 109: - [`docs/usage.md`](docs/usage.md) — a worked walkthrough of covering an extent and
 110:   emitting quadkeys.
 111: - [`docs/api.md`](docs/api.md) — the full public interface.
### docs/api.md
   1: # API reference
   2: 
   3: `tileplan` version `0.4.1`, importable as `tileplan`. The package exports its version as
   4: `tileplan.__version__` (`"0.4.1"`) and otherwise keeps its public names in submodules;
   5: there is no re-export at the top level, so import from the module you need.
   6: 
   7: ```python
   8: from tileplan.coords import Tile, tile_from_lonlat, lonlat_from_tile
   9: from tileplan.extent import Extent, tile_extent, merge_extents
  10: from tileplan.zoom import MAX_ZOOM, resolution_at, closest_zoom
  11: from tileplan.hierarchy import children, parent, descendants
  12: from tileplan.quadkey import to_quadkey, from_quadkey
  13: from tileplan.cover import CoverOptions, cover_extent
  14: ```
  15: 
  16: Every public function in this release is declared with an empty parameter list and a body
  17: that returns `None`; the return annotations below record the intended type. The three
  18: classes take no constructor arguments and assign `None` to each of the attributes listed.
  19: 
  20: ## `tileplan.coords`
  21: 
  22: ### `class Tile`
  23: 
  24: A tile address. `Tile()` takes no arguments.
  25: 
  26: | Attribute | Meaning |
  27: | --- | --- |
  28: | `z` | Zoom level |
  29: | `x` | Column |
  30: | `y` | Row |
  31: 
  32: All three attributes are initialised to `None`.
  33: 
  34: ### `tile_from_lonlat() -> Tile`
  35: 
  36: Returns the `Tile` that contains the point being converted. Takes no arguments.
  37: 
  38: ### `lonlat_from_tile() -> tuple[float, float]`
  39: 
  40: Returns the longitude and latitude for the tile being converted, as a two-element tuple.
  41: Takes no arguments.
  42: 
  43: ## `tileplan.extent`
  44: 
  45: ### `class Extent`
  46: 
  47: A geographic bounding box in degrees. `Extent()` takes no arguments.
  48: 
  49: | Attribute | Meaning |
  50: | --- | --- |
  51: | `west` | Western edge, in degrees |
  52: | `south` | Southern edge, in degrees |
  53: | `east` | Eastern edge, in degrees |
  54: | `north` | Northern edge, in degrees |
  55: 
  56: All four attributes are initialised to `None`.
  57: 
  58: ### `tile_extent() -> Extent`
  59: 
  60: Returns the `Extent` covered by the tile being converted. Takes no arguments.
  61: 
  62: ### `merge_extents() -> Extent`
  63: 
  64: Returns an `Extent` spanning the extents being merged. Takes no arguments.
  65: 
  66: ## `tileplan.zoom`
  67: 
  68: ### `MAX_ZOOM`
  69: 
  70: Module-level constant naming the zoom ceiling. In `0.4.1` its value is the string
  71: `"max_zoom"`.
  72: 
  73: ### `resolution_at() -> float`
  74: 
  75: Returns the ground resolution at a zoom level. Takes no arguments.
  76: 
  77: ### `closest_zoom() -> int`
  78: 
  79: Returns the zoom level whose resolution best matches the requested value. Takes no
  80: arguments.
  81: 
  82: ## `tileplan.hierarchy`
  83: 
  84: ### `children() -> list[Tile]`
  85: 
  86: Returns the tiles directly below the given tile at the next zoom level. Takes no
  87: arguments.
  88: 
  89: ### `parent() -> Tile`
  90: 
  91: Returns the tile one zoom level above the given tile. Takes no arguments.
  92: 
  93: ### `descendants() -> list[Tile]`
  94: 
  95: Returns every tile below the given tile. Takes no arguments.
  96: 
  97: The three return annotations name `Tile`, but this module does not import it; the
  98: annotations are stored as strings (the module uses `from __future__ import annotations`),
  99: so they do not affect importing `tileplan.hierarchy`. Import `Tile` from `tileplan.coords`
 100: when you need the class itself.
 101: 
 102: ## `tileplan.quadkey`
 103: 
 104: ### `to_quadkey() -> str`
 105: 
 106: Returns the quadkey string for the tile being converted. Takes no arguments.
 107: 
 108: ### `from_quadkey() -> Tile`
 109: 
 110: Returns the `Tile` encoded by the quadkey being converted. Takes no arguments.
 111: 
 112: ## `tileplan.cover`
 113: 
 114: ### `class CoverOptions`
 115: 
 116: Settings for `cover_extent`. `CoverOptions()` takes no arguments.
 117: 
 118: | Attribute | Meaning |
 119: | --- | --- |
 120: | `zoom` | Zoom level to cover at |
 121: | `buffer_tiles` | Number of extra tile rings to include around the extent |
 122: | `limit` | Upper bound on the number of tiles returned |
 123: 
 124: All three attributes are initialised to `None`.
 125: 
 126: ### `cover_extent() -> list[Tile]`
 127: 
 128: Returns the tiles covering an extent under the given `CoverOptions`. Takes no arguments.
 129: 
 130: ## Example data
 131: 
 132: `examples/bay_area.geojson` is a GeoJSON `FeatureCollection` containing one `Feature`
 133: named `Bay Area view`. Its geometry is a single `Polygon` ring:
 134: 
 135: ```json
 136: [[-122.52, 37.70], [-122.35, 37.70], [-122.35, 37.83], [-122.52, 37.83], [-122.52, 37.70]]
 137: ```
 138: 
 139: The file is there for examples and manual experimentation; nothing in the package reads it.
### docs/usage.md
   1: # Usage
   2: 
   3: This guide assumes you have read the README and know what a tile address and an extent
   4: are. It walks through one job that comes up constantly in a tiled map pipeline: taking a
   5: geographic bounding box, deciding how deep to tile it, and producing the tile and quadkey
   6: lists that a cache or a fetch queue can consume.
   7: 
   8: The running example uses `examples/bay_area.geojson`, whose polygon spans longitude
   9: `-122.52` to `-122.35` and latitude `37.70` to `37.83`.
  10: 
  11: ## 1. Turn a bounding box into an `Extent`
  12: 
  13: `Extent` is a plain container with four attributes. The constructor takes no arguments,
  14: so you create an instance and assign the fields:
  15: 
  16: ```python
  17: from tileplan.extent import Extent
  18: 
  19: box = Extent()
  20: box.west = -122.52
  21: box.south = 37.70
  22: box.east = -122.35
  23: box.north = 37.83
  24: ```
  25: 
  26: If you already have a tile and want the area it covers, `tile_extent()` returns an
  27: `Extent`. When several boxes have to be combined — for instance the per-feature boxes of
  28: a GeoJSON `FeatureCollection` — `merge_extents()` returns a single `Extent` spanning them:
  29: 
  30: ```python
  31: from tileplan.extent import tile_extent, merge_extents
  32: 
  33: tile_box = tile_extent()        # Extent covered by one tile
  34: combined = merge_extents()      # Extent spanning a group of extents
  35: ```
  36: 
  37: Note that in `0.4.1` both functions are declared with no parameters, so the boxes to
  38: combine are not passed in yet; the object you build above is the one to keep on hand for
  39: when the arguments land.
  40: 
  41: ## 2. Pick a zoom level
  42: 
  43: Zoom selection is usually driven by one of two things: a resolution you can afford to
  44: render, or a fixed level imposed by the tile source.
  45: 
  46: ```python
  47: from tileplan.zoom import MAX_ZOOM, resolution_at, closest_zoom
  48: 
  49: resolution_at()   # float: ground resolution at a zoom level
  50: closest_zoom()    # int: the level that best matches a requested resolution
  51: MAX_ZOOM          # the module's zoom cap; value "max_zoom" in 0.4.1
  52: ```
  53: 
  54: `closest_zoom` is the one to reach for when your input is "roughly 10 metres per pixel";
  55: `resolution_at` is the inverse question, useful when you need to report or log the
  56: resolution that a chosen level implies. `MAX_ZOOM` is where the ceiling belongs before
  57: you ask a tile server for a level it does not serve — but note that in `0.4.1` the
  58: constant holds the string `"max_zoom"`, not an integer, so treat it as a placeholder.
  59: 
  60: ## 3. Build the tile list for the extent
  61: 
  62: `cover_extent` is the entry point; `CoverOptions` carries the three settings that control
  63: it. Construct the options object, then fill in the attributes:
  64: 
  65: ```python
  66: from tileplan.cover import CoverOptions, cover_extent
  67: 
  68: opts = CoverOptions()
  69: opts.zoom = 12          # level to tile at
  70: opts.buffer_tiles = 1   # extra rings of tiles around the box
  71: opts.limit = 512        # upper bound on the number of tiles returned
  72: 
  73: tiles = cover_extent()  # list[Tile]
  74: ```
  75: 
  76: A `buffer_tiles` of `0` is the exact-cover setting; increasing it adds rings of tiles
  77: around the box so that panning or label bleed at the edges does not expose missing tiles.
  78: `limit` is your guard against a mistyped zoom: a low zoom over a large box is cheap, a
  79: high zoom over the same box is not.
  80: 
  81: ## 4. Walk the hierarchy when one level is not enough
  82: 
  83: If you serve a pyramid rather than a single level, expand the cover into the levels below
  84: it. `children` enumerates the tiles directly beneath a tile, `parent` the enclosing tile
  85: one level up, and `descendants` the full sub-tree beneath a tile.
  86: 
  87: ```python
  88: from tileplan.hierarchy import children, parent, descendants
  89: 
  90: kids = children()       # list[Tile] — the next level down
  91: up = parent()           # Tile — one level up
  92: tree = descendants()    # list[Tile] — everything below
  93: ```
  94: 
  95: A typical use is to compute a cheap cover at a low zoom and then take `descendants` of
  96: each tile, which keeps the expensive enumeration out of your own code. Going the other
  97: way, `parent` is what you call before storing a tile in a store keyed at a coarser level.
  98: 
  99: ## 5. Emit quadkeys
 100: 
 101: Quadkeys are the string form of a tile address and make good file names, cache keys, and
 102: index columns, because sorting them groups tiles spatially. Convert in both directions:
 103: 
 104: ```python
 105: from tileplan.quadkey import to_quadkey, from_quadkey
 106: 
 107: key = to_quadkey()      # str
 108: tile = from_quadkey()   # Tile
 109: ```
 110: 
 111: The round trip is the useful property: write `to_quadkey()` into your manifest, and read
 112: it back with `from_quadkey()` when a worker picks the job up. Keep the zoom level with the
 113: key — a quadkey is only meaningful together with the level it was taken at, and the level
 114: is what tells a reader how deep the prefix goes.
 115: 
 116: ## 6. Convert points when you need to place something
 117: 
 118: Two functions in `tileplan.coords` connect geographic coordinates to tile addresses:
 119: 
 120: ```python
 121: from tileplan.coords import Tile, tile_from_lonlat, lonlat_from_tile
 122: 
 123: tile = tile_from_lonlat()        # Tile containing a lon/lat pair
 124: point = lonlat_from_tile()       # declared: tuple[float, float] for a tile
 125: ```
 126: 
 127: `tile_from_lonlat` answers "which tile is this address in?" — use it to snap a marker or a
 128: query point to the tile a cache already holds. `lonlat_from_tile` goes back out, which is
 129: what you need to label a tile or to compute the distance between two tiles. Its declared
 130: return type is a `(lon, lat)` tuple; unpack it once the bodies are implemented.
 131: 
 132: ## A note on this release
 133: 
 134: Everything above describes the intended call sequence, and the names, attributes, and
 135: return types are exactly those of `0.4.1`. In this release the function bodies are
 136: placeholders: each takes no arguments and returns `None`, and the three classes start with
 137: their attributes set to `None`. You can import the package, build the objects, and wire
 138: the calls together today; the values they should produce are not computed yet. If you are
 139: porting logic onto `tileplan`, the surface will not move under you — only the bodies will
 140: fill in.
 141: 
 142: ## See also
 143: 
 144: - [`../README.md`](../README.md) — installation and concepts.
 145: - [`api.md`](api.md) — exact signatures for every public name.

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

### example 1
include/linux/swap.h (code)
  - 	SWP_CONTINUED	= (1 << 5),	/* swap_map has count continuation */
  - /* Bit flag in swap_map */
  - #define COUNT_CONTINUED	0x80	/* Flag swap_map continuation for full count */
  - 
  - /* Special value in first swap_map */
  - #define SWAP_MAP_MAX	0x3e	/* Max count */
  - #define SWAP_MAP_BAD	0x3f	/* Note page is bad */
  - 
  + 	unsigned int	max;		/* size of this swap device */
  + 					 * inuse_pages and all cluster lists.
  + 					 * Other fields are only changed
mm/memory.c (code)
  - 		if (add_swap_count_continuation(entry, GFP_KERNEL) < 0) {
  + 		if (swap_retry_table_alloc(entry, GFP_KERNEL) < 0) {

### example 2
Documentation/rust/quick-start.rst (doc)
  - 
  - If GDB/Binutils is used and Rust symbols are not getting demangled, the reason
  - is the toolchain does not support Rust's new v0 mangling scheme yet.
  - There are a few ways out:
  - 
  - - Install a newer release (GDB >= 10.2, Binutils >= 2.36).
  - 
  - - Some versions of GDB (e.g. vanilla GDB 10.1) are able to use

### example 3
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

### example 4
MAINTAINERS (code)
  - ACENIC DRIVER
  - M:	Jes Sorensen <jes@trained-monkey.org>
  - L:	linux-acenic@sunsite.dk
  - S:	Maintained
  - F:	drivers/net/ethernet/alteon/acenic*
  - 
arch/loongarch/configs/loongson32_defconfig (code)
  - # CONFIG_NET_VENDOR_ALTEON is not set

