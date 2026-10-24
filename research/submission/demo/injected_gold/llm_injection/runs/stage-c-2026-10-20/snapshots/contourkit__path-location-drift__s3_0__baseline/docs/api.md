# contourkit API reference

Version 0.4.1. Python 3.11 or newer.

The package is organised as five computation modules plus a command module.
Import from the module that owns a symbol; the top-level `contourkit` package
exports only `__version__`:

```python
>>> import contourkit
>>> contourkit.__version__
'0.4.1'
```

> **State of the 0.4.1 surface.** Every function in this release is declared with
> an empty parameter list and a return annotation, and every body currently
> returns `None`. The annotations below describe the type each call is committed
> to producing; treat them as the contract, not as behaviour you can observe
> today. Constructors and constants are fully implemented as described.

## Modules at a glance

| Module | Contents |
| --- | --- |
| `contourkit.raster` | `ElevationRaster`, `load_ascii_grid`, `DEFAULT_NODATA` |
| `contourkit.sampling` | `sample_nearest`, `sample_bilinear`, `gradient_magnitude` |
| `contourkit.marching` | `contour_levels`, `trace_contour` |
| `contourkit.geometry` | `Polyline`, `polyline_length`, `close_ring` |
| `contourkit.simplify` | `douglas_peucker`, `simplify_contours` |
| `contourkit.cli` | `main`, `DEFAULT_TOLERANCE` |

## contourkit.raster

### `class ElevationRaster()`

An elevation grid together with its georeferencing and its missing-data marker.

```python
from contourkit.raster import ElevationRaster

raster = ElevationRaster()
```

`__init__` takes no arguments and sets three public attributes, each initially
`None`:

| Attribute | Meaning |
| --- | --- |
| `data` | the elevation values |
| `transform` | the mapping from cell indices to map coordinates |
| `nodata` | the value that marks cells with no measurement |

Assign them directly when you are constructing a raster by hand:

```python
raster.data = [[100, 104], [106, 110]]
raster.nodata = -9999
```

### `load_ascii_grid() -> ElevationRaster`

Reads an ESRI ASCII grid into an `ElevationRaster`. Takes no arguments in
0.4.1. Returns `None` in the current release.

An ESRI ASCII grid is a text file with a six-line header — `ncols`, `nrows`,
`xllcorner`, `yllcorner`, `cellsize`, `NODATA_value` — followed by one
whitespace-separated row of values per line. `examples/terrain.asc` in this
repository is an example. See the walkthrough for a line-by-line reading of that
header.

### `DEFAULT_NODATA`

```python
>>> from contourkit.raster import DEFAULT_NODATA
>>> DEFAULT_NODATA
'default_nodata'
```

The fallback marker used for missing cells when a grid does not supply its own.
It is a string, not a number.

## contourkit.sampling

Point sampling of the elevation surface. All three functions take no arguments
in 0.4.1 and return `None`; their annotations are `float`.

### `sample_nearest() -> float`

Reads the surface without interpolation: the value of the cell containing the
point. Use it when you want the stored measurements untouched.

### `sample_bilinear() -> float`

Reads the surface by interpolating across neighbouring cells. Use it when you
want a smooth surface; nearest-neighbour sampling on a coarse grid produces
plateaus that show up as stair-stepped contours.

### `gradient_magnitude() -> float`

The magnitude of the surface gradient at the point — how steep the terrain is.
Useful for shading and for anticipating where contour lines will bunch together.

## contourkit.marching

### `contour_levels() -> list[float]`

Returns the elevations to trace. Takes no arguments in 0.4.1 and returns `None`
in the current release.

The list is the input to the tracer: every elevation in it becomes one or more
polylines. Keeping it explicit lets a caller drop levels that fall outside the
data range or that would only produce edge slivers.

### `trace_contour() -> list[Polyline]`

Returns the traced contours, one `Polyline` per connected line, each carrying the
elevation it was traced at in its `level` attribute. Takes no arguments in 0.4.1
and returns `None` in the current release.

A single elevation can yield several polylines, so the result is not one entry
per requested level. The `Polyline` type lives in `contourkit.geometry`.

## contourkit.geometry

### `class Polyline()`

One traced contour line.

```python
from contourkit.geometry import Polyline

line = Polyline()
line.points = [(0.0, 0.0), (10.0, 5.0)]
line.level = 120.0
```

`__init__` takes no arguments and sets two public attributes, both initially
`None`:

| Attribute | Meaning |
| --- | --- |
| `points` | ordered coordinates making up the line |
| `level` | the elevation the line was traced at |

A polyline whose first and last point coincide is a closed ring.

### `polyline_length() -> float`

The total length of a polyline, in map units. Takes no arguments in 0.4.1 and
returns `None` in the current release.

### `close_ring() -> Polyline`

The closed form of a polyline, for contours that enclose an area. Takes no
arguments in 0.4.1 and returns `None` in the current release.

## contourkit.simplify

Both functions take no arguments in 0.4.1 and return `None` in the current
release. Their annotations name the types they are committed to returning.

### `douglas_peucker() -> Polyline`

Simplifies a single polyline, dropping points that lie within the tolerance of
the line through their neighbours.

### `simplify_contours() -> list[Polyline]`

Simplifies a whole contour set and returns the result as a list of `Polyline`.

Simplify after tracing. Removing points before the tracer runs discards the
detail it uses to place a line correctly.

## contourkit.cli

### `main() -> int`

The command entry point. Takes no arguments and returns an integer exit code, so
it can be passed straight to `sys.exit`:

```python
import sys
from contourkit.cli import main

sys.exit(main())
```

`pyproject.toml` declares no `console_scripts` entry point and the package has no
`__main__` module, so in 0.4.1 there is no installed `contourkit` command;
`main()` is called in-process. Note that although `click>=8.1` is a declared
dependency of the package, `contourkit/cli.py` does not import it.

### `DEFAULT_TOLERANCE`

```python
>>> from contourkit.cli import DEFAULT_TOLERANCE
>>> DEFAULT_TOLERANCE
'default_tolerance'
```

The fallback simplification tolerance used when a caller does not supply one.
It is a string, not a number.

## Package metadata

- Distribution and import name: `contourkit`
- Version: `0.4.1` (also in `contourkit.__version__`)
- Requires Python: `>=3.11`
- Dependencies: `numpy>=1.26`, `click>=8.1`
- Build backend: setuptools, requiring `setuptools>=68`
- Packaged directory: `contourkit`
