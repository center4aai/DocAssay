# plotline API reference

All public names live in the `plotline` package, in the modules listed below.
The package itself exports nothing at the top level; import from the module.

## `plotline.canvas`

### `class Canvas`

```python
from plotline.canvas import Canvas
```

A drawing surface. `Canvas()` takes no arguments.

| Attribute | Description |
|---|---|
| `width` | Drawing width. Set to `None` by the constructor. |
| `height` | Drawing height. Set to `None` by the constructor. |
| `background` | Background of the drawing. Set to `None` by the constructor. |

### `DEFAULT_BACKGROUND`

The string constant `"default_background"`. It is the default background
value named by this module.

## `plotline.scales`

### `class LinearScale`

```python
from plotline.scales import LinearScale
```

A linear mapping between a data domain and a drawing range. `LinearScale()`
takes no arguments.

| Attribute | Description |
|---|---|
| `domain_min` | Lower bound of the data domain. Set to `None` by the constructor. |
| `domain_max` | Upper bound of the data domain. Set to `None` by the constructor. |
| `range_min` | Lower bound of the drawing range. Set to `None` by the constructor. |
| `range_max` | Upper bound of the drawing range. Set to `None` by the constructor. |

### `nice_ticks() -> list[float]`

Intended to return round tick values for an axis. Takes no arguments in
this release, and the body currently returns `None`.

## `plotline.marks`

### `class LineMark`

```python
from plotline.marks import LineMark
```

A line series. `LineMark()` takes no arguments.

| Attribute | Description |
|---|---|
| `xs` | X values of the line. Set to `None` by the constructor. |
| `ys` | Y values of the line. Set to `None` by the constructor. |
| `stroke` | Stroke color of the line. Set to `None` by the constructor. |

### `class BarMark`

```python
from plotline.marks import BarMark
```

A bar series. `BarMark()` takes no arguments.

| Attribute | Description |
|---|---|
| `labels` | Labels for the bars. Set to `None` by the constructor. |
| `values` | Values for the bars. Set to `None` by the constructor. |
| `fill` | Fill color of the bars. Set to `None` by the constructor. |

## `plotline.palette`

### `CATEGORY_COLORS`

The string constant `"category_colors"`, the name of the categorical palette.

### `categorical_colors() -> list[str]`

```python
from plotline.palette import categorical_colors
```

Intended to return the list of colors for distinct series. Takes no
arguments in this release, and the body currently returns `None`.

## `plotline.render`

### `render_svg() -> str`

```python
from plotline.render import render_svg
```

Intended to return the SVG markup for a chart. Takes no arguments in this
release, and the body currently returns `None`.

### `write_svg() -> None`

```python
from plotline.render import write_svg
```

Intended to write SVG markup to a file. Takes no arguments in this release,
and the body currently returns `None`.
