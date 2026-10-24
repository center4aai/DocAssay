# contourkit

contourkit is a small Python library for turning elevation rasters into
lightweight contour geometry. It is built around four steps that map onto four
modules: read a raster into an array plus its georeferencing, sample the surface
at arbitrary points, trace polylines at chosen elevations, and simplify those
polylines before they go into a map.

It is aimed at people who need contour lines for a tile, a printed map, or a
vector layer, and who would rather have a handful of explicit functions than a
full GIS stack. There is no map rendering, no projection code, and no file
format support beyond the ESRI ASCII grid reader.

The current release is **0.4.1**. It publishes the module layout, class
attributes, and function signatures described in [docs/api.md](docs/api.md);
the computational routines are placeholders at this stage. `load_ascii_grid`,
`contour_levels`, `trace_contour`, `simplify_contours` and the sampling helpers
all return `None` today, and the example below reflects that.

## Installation

contourkit requires Python 3.11 or newer. Runtime dependencies are
`numpy>=1.26` and `click>=8.1`.

From a checkout of this repository:

```bash
pip install -e .
```

The package is built with setuptools (`setuptools>=68`).

To check that the install worked:

```python
>>> import contourkit
>>> contourkit.__version__
'0.4.1'
```

## Quick start

```python
from contourkit import __version__
from contourkit.raster import load_ascii_grid, DEFAULT_NODATA
from contourkit.geometry import Polyline
from contourkit.marching import contour_levels

print(__version__)      # 0.4.1
print(DEFAULT_NODATA)   # default_nodata

raster = load_ascii_grid()

# A Polyline carries a list of points and the elevation it belongs to.
line = Polyline()
line.points = [(0.0, 0.0), (10.0, 5.0)]
line.level = 120.0
```

A full contour run follows the same shape:

```python
from contourkit.raster import load_ascii_grid
from contourkit.marching import contour_levels, trace_contour
from contourkit.simplify import simplify_contours

raster = load_ascii_grid()
levels = contour_levels()
contours = trace_contour()
light = simplify_contours()
```

In 0.4.1 each of these returns `None`, so the pipeline wires up but produces no
geometry yet. The signatures are what the package commits to; see
[docs/api.md](docs/api.md) for the exact surface.

## Main concepts

**Raster.** An `ElevationRaster` holds `data` (the elevation values),
`transform` (the georeferencing that maps cell indices to map coordinates), and
`nodata` (the value marking missing cells). `load_ascii_grid()` builds one from
an ESRI ASCII grid. The module constant `DEFAULT_NODATA` is the fallback nodata
marker, currently the string `"default_nodata"`.

**Sampling.** `contourkit.sampling` reads the surface between cells:
`sample_nearest` takes a cell value as-is, `sample_bilinear` interpolates
between neighbouring cells, and `gradient_magnitude` reports how steep the
surface is at a point, which is what you want for hillshading or for choosing
where contours will crowd together.

**Contour tracing.** `contour_levels()` chooses the elevations to draw, and
`trace_contour()` traces the isolines at those elevations. Each traced line is
returned as a `Polyline`.

**Polylines.** A `Polyline` has two attributes: `points`, the ordered
coordinates that make up the line, and `level`, the elevation it was traced at.
`polyline_length` measures one, and `close_ring` turns an open line into a
closed loop for filled or outlined areas.

**Simplification.** `douglas_peucker` thins a single polyline while keeping its
shape, and `simplify_contours` applies that to a whole contour set. The
tolerance you pass controls how aggressively points are dropped; the command
module exposes a fallback through `DEFAULT_TOLERANCE`.

## The example grid

`examples/terrain.asc` is a 5 × 5 ESRI ASCII grid with a header of `ncols 5`,
`nrows 5`, `xllcorner 0`, `yllcorner 0`, `cellsize 10`, and
`NODATA_value -9999`, followed by elevations from 100 to 140. With a cell size
of 10 it covers 50 × 50 map units, and its values rise smoothly, which makes it
a convenient fixture for trying the tracer.

## Command line

`contourkit.cli` provides `main()`, which returns an integer exit code, and the
`DEFAULT_TOLERANCE` constant. The package does not declare a `console_scripts`
entry point and has no `__main__` module, so in 0.4.1 you invoke the entry point
from Python:

```python
import sys
from contourkit.cli import main

sys.exit(main())
```

## Documentation

- [docs/walkthrough.md](docs/walkthrough.md) — a step-by-step tour of the
  contour pipeline using `examples/terrain.asc`.
- [docs/api.md](docs/api.md) — the public classes, functions, and constants.
