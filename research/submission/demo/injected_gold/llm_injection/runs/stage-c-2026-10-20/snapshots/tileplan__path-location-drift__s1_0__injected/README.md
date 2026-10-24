# tileplan

Slippy-map tile coordinates, extents, and zoom arithmetic for tiled map pipelines.

`tileplan` is a small, dependency-free library for the coordinate bookkeeping that every
tiled map pipeline ends up writing by hand: which tile contains a lon/lat pair, what
ground area a tile covers, which zoom level matches a desired resolution, how tiles nest
into each other, and which tiles are needed to cover a bounding box. It has no runtime
dependencies and targets Python 3.11 or newer.

This release is `0.4.1`.

## Install

From a checkout of this repository:

```bash
pip install .
```

Or, while working on the library itself:

```bash
pip install -e .
```

Only the build backend (`setuptools>=68`) is fetched; there are no runtime dependencies
to install.

## Quick start

```python
from tileplan.coords import Tile, tile_from_lonlat, lonlat_from_tile
from tileplan.extent import Extent, tile_extent, merge_extents
from tileplan.zoom import MAX_ZOOM, resolution_at, closest_zoom
from tileplan.hierarchy import children, parent, descendants
from tileplan.quadkey import to_quadkey, from_quadkey
from tileplan.cover import CoverOptions, cover_extent

tile = tile_from_lonlat()          # declared return type: Tile
box = tile_extent()                # declared return type: Extent
zoom = closest_zoom()              # declared return type: int
key = to_quadkey()                 # declared return type: str

options = CoverOptions()
options.zoom = 10
options.buffer_tiles = 1
options.limit = 256
tiles = cover_extent()             # declared return type: list[Tile]
```

> **Implementation status.** `0.4.1` publishes the interface, not the arithmetic. Every
> function in the package has an empty parameter list and a body that returns `None`,
> and `Tile`/`Extent`/`CoverOptions` are constructed with no arguments and start with
> their documented attributes set to `None`. The module layout, names, attribute sets,
> and return annotations below are stable; code that calls them should treat the values
> as not yet available.

## Concepts

**Tiles and zoom levels.** A tile is addressed by three integers: `z` (the zoom level),
`x` (the column) and `y` (the row). At zoom `z` the world is divided into a
`2**z × 2**z` grid, so the number of tiles grows fourfold per level. `tileplan` targets
the usual XYZ / Google / OpenStreetMap convention for the origin of `x` and `y`.
`tileplan.coords.Tile` holds the triple as the attributes `z`, `x`, and `y`.

**Extents.** An extent is a geographic bounding box in degrees, stored as `west`,
`south`, `east`, and `north` on `tileplan.extent.Extent`. `tile_extent` maps a tile to
the box it covers; `merge_extents` combines boxes.

**Zoom arithmetic.** `tileplan.zoom.resolution_at` relates a zoom level to ground
resolution, and `closest_zoom` picks the best integer level for a requested resolution.
The module exposes the zoom cap as `MAX_ZOOM`; as shipped in `0.4.1` the constant's value
is the string `"max_zoom"` rather than a number.

**Tile hierarchy.** Tiles at one zoom nest exactly into tiles at the next:
`children`, `parent`, and `descendants` in `tileplan.hierarchy` move between levels.

**Quadkeys.** A quadkey is the string form of a tile address, one digit per zoom level,
which is convenient as a cache key or database column. `to_quadkey` and `from_quadkey`
in `tileplan.quadkey` convert between the two representations.

**Covering an extent.** `tileplan.cover` answers "which tiles do I need for this box?".
`CoverOptions` carries the target `zoom`, a `buffer_tiles` margin around the box, and a
`limit` on how many tiles to return; `cover_extent` produces the list.

## Package layout

| Module | Contents |
| --- | --- |
| `tileplan/coords.py` | `Tile`, `tile_from_lonlat`, `lonlat_from_tile` |
| `tileplan/extent.py` | `Extent`, `tile_extent`, `merge_extents` |
| `tileplan/zoom.py` | `MAX_ZOOM`, `resolution_at`, `closest_zoom` |
| `tileplan/hierarchy.py` | `children`, `parent`, `descendants` |
| `tileplan/quadkey.py` | `to_quadkey`, `from_quadkey` |
| `tileplan/cover.py` | `CoverOptions`, `cover_extent` |

The package version is available as `tileplan.__version__`.

## Example data

`examples/bay_area.geojson` is a GeoJSON `FeatureCollection` with a single `Polygon`
feature named `Bay Area view`. Its ring spans longitude `-122.52` to `-122.35` and
latitude `37.70` to `37.83`, which makes it a convenient stand-in for a real extent when
you are sketching a pipeline.

## Further reading

- [`docs/usage.md`](docs/usage.md) — a worked walkthrough of covering an extent and
  emitting quadkeys.
- [`docs/api.md`](docs/api.md) — the full public interface.
