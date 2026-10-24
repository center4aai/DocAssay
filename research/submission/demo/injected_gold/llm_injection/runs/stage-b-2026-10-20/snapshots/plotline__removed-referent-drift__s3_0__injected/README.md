# plotline

plotline is a small Python library of SVG chart primitives. It is meant for
building line and bar charts as plain SVG markup. The package is at version 0.4.2.

The library is organized as a handful of building blocks:

- a `Canvas` that holds the drawing size and background,
- a `LinearScale` that maps data values onto drawing coordinates,
- `nice_ticks` for picking axis tick values,
- `LineMark` and `BarMark` for the two supported chart types,
- a categorical palette, and
- `render_svg` and `write_svg` for producing the final markup.

See the [user guide](docs/guide.md) for how these pieces fit together and the
[API reference](docs/api.md) for every public name.

## Installation

plotline requires Python 3.11 or newer and declares a dependency on
`numpy>=1.24`. Install it from a local checkout with pip:

```bash
pip install .
```

For development, an editable install works as well:

```bash
pip install -e .
```

## Quick start

Every public name is importable from its module under the `plotline` package:

```python
from plotline.canvas import Canvas
from plotline.marks import LineMark, BarMark
from plotline.render import render_svg, write_svg
```

A minimal session creates a canvas, a mark, and renders the result:

```python
from plotline.canvas import Canvas
from plotline.marks import LineMark
from plotline.render import render_svg

canvas = Canvas()
line = LineMark()
svg_text = render_svg()
```

> **Note:** In the current release the constructors take no arguments, and
> the functions take no arguments and their bodies return `None`. The names
> and attributes described in the [API reference](docs/api.md) are what the
> package currently defines; the rendering behavior is not implemented yet.

## Documentation

- [User guide](docs/guide.md): concepts, coordinates and scales, and a
  typical workflow.
- [API reference](docs/api.md): every public module, class, constant and
  function.
