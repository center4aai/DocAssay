# API reference

`tileplan` version `0.4.1`, importable as `tileplan`. The package exports its version as
`tileplan.__version__` (`"0.4.1"`) and otherwise keeps its public names in submodules;
there is no re-export at the top level, so import from the module you need.

```python
from tileplan.coords import Tile, tile_from_lonlat, lonlat_from_tile
from tileplan.extent import Extent, tile_extent, merge_extents
from tileplan.zoom import MAX_ZOOM, resolution_at, closest_zoom
from tileplan.hierarchy import children, parent, descendants
from tileplan.quadkey import to_quadkey, from_quadkey
from tileplan.cover import CoverOptions, cover_extent
```

Every public function in this release is declared with an empty parameter list and a body
that returns `None`; the return annotations below record the intended type. The three
classes take no constructor arguments and assign `None` to each of the attributes listed.

## `tileplan.coords`

### `class Tile`

A tile address. `Tile()` takes no arguments.

| Attribute | Meaning |
| --- | --- |
| `z` | Zoom level |
| `x` | Column |
| `y` | Row |

All three attributes are initialised to `None`.

### `tile_from_lonlat() -> Tile`

Returns the `Tile` that contains the point being converted. Takes no arguments.

### `lonlat_from_tile() -> tuple[float, float]`

Returns the longitude and latitude for the tile being converted, as a two-element tuple.
Takes no arguments.

## `tileplan.extent`

### `class Extent`

A geographic bounding box in degrees. `Extent()` takes no arguments.

| Attribute | Meaning |
| --- | --- |
| `west` | Western edge, in degrees |
| `south` | Southern edge, in degrees |
| `east` | Eastern edge, in degrees |
| `north` | Northern edge, in degrees |

All four attributes are initialised to `None`.

### `tile_extent() -> Extent`

Returns the `Extent` covered by the tile being converted. Takes no arguments.

### `merge_extents() -> Extent`

Returns an `Extent` spanning the extents being merged. Takes no arguments.

## `tileplan.zoom`

### `MAX_ZOOM`

Module-level constant naming the zoom ceiling. In `0.4.1` its value is the string
`"max_zoom"`.

### `resolution_at() -> float`

Returns the ground resolution at a zoom level. Takes no arguments.

### `closest_zoom() -> int`

Returns the zoom level whose resolution best matches the requested value. Takes no
arguments.

## `tileplan.hierarchy`

### `children() -> list[Tile]`

Returns the tiles directly below the given tile at the next zoom level. Takes no
arguments.

### `parent() -> Tile`

Returns the tile one zoom level above the given tile. Takes no arguments.

### `descendants() -> list[Tile]`

Returns every tile below the given tile. Takes no arguments.

The three return annotations name `Tile`, but this module does not import it; the
annotations are stored as strings (the module uses `from __future__ import annotations`),
so they do not affect importing `tileplan.hierarchy`. Import `Tile` from `tileplan.coords`
when you need the class itself.

## `tileplan.quadkey`

### `to_quadkey() -> str`

Returns the quadkey string for the tile being converted. Takes no arguments.

### `from_quadkey() -> Tile`

Returns the `Tile` encoded by the quadkey being converted. Takes no arguments.

## `tileplan.cover`

### `class CoverOptions`

Settings for `cover_extent`. `CoverOptions()` takes no arguments.

| Attribute | Meaning |
| --- | --- |
| `zoom` | Zoom level to cover at |
| `buffer_tiles` | Number of extra tile rings to include around the extent |
| `limit` | Upper bound on the number of tiles returned |

All three attributes are initialised to `None`.

### `cover_extent() -> list[Tile]`

Returns the tiles covering an extent under the given `CoverOptions`. Takes no arguments.

## Example data

`examples/bay_area.geojson` is a GeoJSON `FeatureCollection` containing one `Feature`
named `Bay Area view`. Its geometry is a single `Polygon` ring:

```json
[[-122.52, 37.70], [-122.35, 37.70], [-122.35, 37.83], [-122.52, 37.83], [-122.52, 37.70]]
```

The file is there for examples and manual experimentation; nothing in the package reads it.
