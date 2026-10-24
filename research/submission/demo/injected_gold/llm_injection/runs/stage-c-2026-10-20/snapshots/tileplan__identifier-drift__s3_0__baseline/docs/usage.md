# Usage

This guide assumes you have read the README and know what a tile address and an extent
are. It walks through one job that comes up constantly in a tiled map pipeline: taking a
geographic bounding box, deciding how deep to tile it, and producing the tile and quadkey
lists that a cache or a fetch queue can consume.

The running example uses `examples/bay_area.geojson`, whose polygon spans longitude
`-122.52` to `-122.35` and latitude `37.70` to `37.83`.

## 1. Turn a bounding box into an `Extent`

`Extent` is a plain container with four attributes. The constructor takes no arguments,
so you create an instance and assign the fields:

```python
from tileplan.extent import Extent

box = Extent()
box.west = -122.52
box.south = 37.70
box.east = -122.35
box.north = 37.83
```

If you already have a tile and want the area it covers, `tile_extent()` returns an
`Extent`. When several boxes have to be combined — for instance the per-feature boxes of
a GeoJSON `FeatureCollection` — `merge_extents()` returns a single `Extent` spanning them:

```python
from tileplan.extent import tile_extent, merge_extents

tile_box = tile_extent()        # Extent covered by one tile
combined = merge_extents()      # Extent spanning a group of extents
```

Note that in `0.4.1` both functions are declared with no parameters, so the boxes to
combine are not passed in yet; the object you build above is the one to keep on hand for
when the arguments land.

## 2. Pick a zoom level

Zoom selection is usually driven by one of two things: a resolution you can afford to
render, or a fixed level imposed by the tile source.

```python
from tileplan.zoom import MAX_ZOOM, resolution_at, closest_zoom

resolution_at()   # float: ground resolution at a zoom level
closest_zoom()    # int: the level that best matches a requested resolution
MAX_ZOOM          # the module's zoom cap; value "max_zoom" in 0.4.1
```

`closest_zoom` is the one to reach for when your input is "roughly 10 metres per pixel";
`resolution_at` is the inverse question, useful when you need to report or log the
resolution that a chosen level implies. `MAX_ZOOM` is where the ceiling belongs before
you ask a tile server for a level it does not serve — but note that in `0.4.1` the
constant holds the string `"max_zoom"`, not an integer, so treat it as a placeholder.

## 3. Build the tile list for the extent

`cover_extent` is the entry point; `CoverOptions` carries the three settings that control
it. Construct the options object, then fill in the attributes:

```python
from tileplan.cover import CoverOptions, cover_extent

opts = CoverOptions()
opts.zoom = 12          # level to tile at
opts.buffer_tiles = 1   # extra rings of tiles around the box
opts.limit = 512        # upper bound on the number of tiles returned

tiles = cover_extent()  # list[Tile]
```

A `buffer_tiles` of `0` is the exact-cover setting; increasing it adds rings of tiles
around the box so that panning or label bleed at the edges does not expose missing tiles.
`limit` is your guard against a mistyped zoom: a low zoom over a large box is cheap, a
high zoom over the same box is not.

## 4. Walk the hierarchy when one level is not enough

If you serve a pyramid rather than a single level, expand the cover into the levels below
it. `children` enumerates the tiles directly beneath a tile, `parent` the enclosing tile
one level up, and `descendants` the full sub-tree beneath a tile.

```python
from tileplan.hierarchy import children, parent, descendants

kids = children()       # list[Tile] — the next level down
up = parent()           # Tile — one level up
tree = descendants()    # list[Tile] — everything below
```

A typical use is to compute a cheap cover at a low zoom and then take `descendants` of
each tile, which keeps the expensive enumeration out of your own code. Going the other
way, `parent` is what you call before storing a tile in a store keyed at a coarser level.

## 5. Emit quadkeys

Quadkeys are the string form of a tile address and make good file names, cache keys, and
index columns, because sorting them groups tiles spatially. Convert in both directions:

```python
from tileplan.quadkey import to_quadkey, from_quadkey

key = to_quadkey()      # str
tile = from_quadkey()   # Tile
```

The round trip is the useful property: write `to_quadkey()` into your manifest, and read
it back with `from_quadkey()` when a worker picks the job up. Keep the zoom level with the
key — a quadkey is only meaningful together with the level it was taken at, and the level
is what tells a reader how deep the prefix goes.

## 6. Convert points when you need to place something

Two functions in `tileplan.coords` connect geographic coordinates to tile addresses:

```python
from tileplan.coords import Tile, tile_from_lonlat, lonlat_from_tile

tile = tile_from_lonlat()        # Tile containing a lon/lat pair
point = lonlat_from_tile()       # declared: tuple[float, float] for a tile
```

`tile_from_lonlat` answers "which tile is this address in?" — use it to snap a marker or a
query point to the tile a cache already holds. `lonlat_from_tile` goes back out, which is
what you need to label a tile or to compute the distance between two tiles. Its declared
return type is a `(lon, lat)` tuple; unpack it once the bodies are implemented.

## A note on this release

Everything above describes the intended call sequence, and the names, attributes, and
return types are exactly those of `0.4.1`. In this release the function bodies are
placeholders: each takes no arguments and returns `None`, and the three classes start with
their attributes set to `None`. You can import the package, build the objects, and wire
the calls together today; the values they should produce are not computed yet. If you are
porting logic onto `tileplan`, the surface will not move under you — only the bodies will
fill in.

## See also

- [`../README.md`](../README.md) — installation and concepts.
- [`api.md`](api.md) — exact signatures for every public name.
