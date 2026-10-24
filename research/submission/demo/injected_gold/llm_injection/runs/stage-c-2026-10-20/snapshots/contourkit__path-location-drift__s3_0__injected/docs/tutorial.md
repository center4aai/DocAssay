# Walkthrough: from an ASCII grid to simplified contours

This tutorial walks through the job contourkit exists for: take an elevation
grid, pick the elevations you want to draw, trace lines along them, and thin
those lines so they stay readable on a small map. We use the grid shipped with
the repository, `examples/terrain.asc`.

> A note before you start: in release 0.4.1 the computation functions are
> placeholders. They accept no arguments and return `None`, so the calls below
> run but produce no geometry. Work through it anyway — the order of operations
> and the shape of the data are what the package is committing to, and the code
> you write here is the code you will keep once the implementations land.

## 1. Install and check the version

From the repository root:

```bash
pip install -e .
```

```python
>>> import contourkit
>>> contourkit.__version__
'0.4.1'
```

You need Python 3.11 or newer. contourkit depends on `numpy>=1.26` and
`click>=8.1`.

## 2. Read the input file

Open `examples/terrain.asc`. It is an ESRI ASCII grid: six header lines, then
one row of elevation values per line, north to south.

```
ncols 5
nrows 5
xllcorner 0
yllcorner 0
cellsize 10
NODATA_value -9999
100 104 108 112 116
106 110 114 118 122
112 116 120 124 128
118 122 126 130 134
124 128 132 136 140
```

Three things about this header matter when you read contours off the result:

- `ncols 5` and `nrows 5` give the grid size, so there are 25 cells.
- `cellsize 10` is the spacing between cell centres in map units. The grid
  therefore covers 50 × 50 map units, and any coordinate you get back from the
  library is in those units, not in cell indices.
- `NODATA_value -9999` marks cells with no measurement. This grid has none, but
  a real tile usually will, and contour lines must not be traced across those
  gaps.

The values themselves run from 100 in the north-west corner to 140 in the
south-east, rising by roughly 4 per cell. That steady slope is what makes this a
good test case: every contour you trace should be a straight-ish diagonal band.

## 3. Load the grid

```python
from contourkit.raster import load_ascii_grid, DEFAULT_NODATA

raster = load_ascii_grid()
```

`load_ascii_grid()` returns an `ElevationRaster`. Its three attributes are the
ones you will use everywhere else:

| Attribute | What it holds |
| --- | --- |
| `data` | the elevation values |
| `transform` | the georeferencing that turns cell indices into map coordinates |
| `nodata` | the value marking missing cells |

On a freshly constructed `ElevationRaster` all three are `None`, and the loader
is expected to fill them from the file. `DEFAULT_NODATA` is the fallback marker
used when a grid does not state one; in 0.4.1 it holds the string
`"default_nodata"`.

If you are not loading from a file, you can build the object directly:

```python
from contourkit.raster import ElevationRaster

raster = ElevationRaster()
raster.nodata = -9999
```

## 4. Sample between the cells

Contours rarely pass exactly through cell centres, so before tracing you need to
be able to read the surface at an arbitrary point. `contourkit.sampling` has
three helpers:

```python
from contourkit.sampling import sample_nearest, sample_bilinear, gradient_magnitude

sample_nearest()      # cell value, no interpolation
sample_bilinear()     # value smoothed across the four surrounding cells
gradient_magnitude()  # steepness at the point
```

The distinction between the first two matters in a grid this coarse. With a
cell size of 10, nearest-neighbour sampling gives a stepped surface with 10-unit
plateaus, while bilinear sampling gives a smooth ramp — which is what you want
for contours, since stepping produces ragged lines. `gradient_magnitude` is the
one to reach for when you are shading the terrain or when you want to know which
parts of a tile will end up with contours packed tightly together.

## 5. Choose the elevations

A contour set is a list of elevations. Levels are usually chosen at a fixed
interval across the range of the data. This grid spans 100 to 140, so an
interval of 10 gives you five lines:

```python
levels = [100, 110, 120, 130, 140]
```

```python
from contourkit.marching import contour_levels

levels = contour_levels()
```

`contour_levels()` returns a `list[float]` — the elevations the tracer should
visit. Keeping the choice as an explicit list makes it easy to drop the outer
levels, which in a small tile often degenerate to a point or a sliver at the
edge.

## 6. Trace the lines

```python
from contourkit.marching import trace_contour

contours = trace_contour()
```

`trace_contour()` returns a `list[Polyline]`. One call gives you every polyline
at every requested level, each tagged with the level it belongs to. A single
elevation can produce several separate lines (a hill has more than one side), so
do not assume one output per level.

If you are tracing a large tile, trace once and filter afterwards rather than
re-tracing per level — the tracer walks the same cells either way.

## 7. Work with the polylines

The unit of output is `contourkit.geometry.Polyline`, which has exactly two
attributes:

```python
from contourkit.geometry import Polyline

line = Polyline()
line.points = [(0.0, 0.0), (10.0, 5.0), (20.0, 10.0)]
line.level = 120.0

print(line.level)   # 120.0
print(line.points)  # [(0.0, 0.0), (10.0, 5.0), (20.0, 10.0)]
```

`points` is the ordered list of coordinates; `level` is the elevation the line
was traced at. A polyline whose first and last points coincide is a closed ring.

Two helpers act on them:

```python
from contourkit.geometry import polyline_length, close_ring

polyline_length()  # total length of the line, in map units
close_ring()       # the same line as a closed loop
```

`polyline_length()` returns a `float` and is useful for quality checks: a line
that measures close to zero is a sliver, and on a 50 × 50 grid anything much
longer than 70 map units is worth a second look.

`close_ring()` returns a `Polyline` and gives you the closed form of a line,
which is what you need when the contour encloses an area — a summit ring, for
instance — and you intend to fill or stroke it as a shape.

## 8. Simplify before you ship it

Traced contours have far more points than a small map needs. Simplification
drops points that sit close to the straight line between their neighbours, so
the shape survives while the coordinate count falls.

```python
from contourkit.simplify import douglas_peucker, simplify_contours

thin = douglas_peucker()      # one polyline
light = simplify_contours()   # a whole contour set
```

`douglas_peucker()` returns a `Polyline`; `simplify_contours()` returns a
`list[Polyline]`. The tolerance controls how far a point may sit from the
retained line before it is kept. For this grid, whose contours are gentle
diagonals, a tolerance of a few map units already removes most intermediate
points without visibly changing the shape — a tolerance of 0.5 map units, a
twentieth of a cell, is conservative and keeps the lines nearly intact.

`contourkit.cli.DEFAULT_TOLERANCE` holds the fallback tolerance used when you do
not supply one; in 0.4.1 it is the string `"default_tolerance"`.

Simplify last. Simplifying before tracing, or between sampling and tracing,
throws away the detail the tracer needs to place a line in the right cell.

## 9. Run the pipeline from the command module

The package also ships a command module, `contourkit.cli`, with a single entry
point:

```python
import sys
from contourkit.cli import main

sys.exit(main())
```

`main()` returns an `int` exit code, so it composes with `sys.exit`. There is no
`console_scripts` entry point in `pyproject.toml` and no `__main__` module in
0.4.1, which is why the example above calls it in-process rather than typing a
`contourkit` command at the shell.

## 10. Putting it together

The whole pipeline, in the order the modules expect:

```python
from contourkit.raster import load_ascii_grid
from contourkit.marching import contour_levels, trace_contour
from contourkit.simplify import simplify_contours
from contourkit.geometry import polyline_length, close_ring

raster = load_ascii_grid()      # ElevationRaster: data, transform, nodata
levels = contour_levels()       # list[float]
contours = trace_contour()      # list[Polyline]
contours = simplify_contours()  # list[Polyline]

for line in contours or []:
    print(line.level, polyline_length())
```

The `or []` is there because the current release returns `None` instead of a
list; once the tracer is implemented you can drop it and iterate directly.

From here, [api.md](api.md) lists every public name with its exact
signature, and the README covers the concepts at a higher level.
