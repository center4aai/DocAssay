# plotline user guide

This guide explains the main ideas behind plotline and how the pieces are
meant to fit together. For signatures and attribute lists, see the
[API reference](api.md).

## The model

plotline builds charts from a few small objects rather than from a single
chart call:

| Piece | Module | Role |
|---|---|---|
| `Canvas` | `plotline.canvas` | Drawing size and background. |
| `LinearScale` | `plotline.scales` | Maps a data domain onto a drawing range. |
| `nice_ticks` | `plotline.scales` | Chooses tick values for an axis. |
| `LineMark` | `plotline.marks` | A line series: x values, y values, stroke. |
| `BarMark` | `plotline.marks` | A bar series: labels, values, fill. |
| `categorical_colors` | `plotline.palette` | Colors for distinct series. |
| `render_svg`, `write_svg` | `plotline.render` | Produce SVG markup, or write it to a file. |

## Coordinates and scales

Data values and drawing coordinates are different spaces. A
`LinearScale` describes the mapping between them with four attributes:

- `domain_min` and `domain_max`: the range of data values.
- `range_min` and `range_max`: the range of drawing coordinates they map to.

The names follow the usual linear-scale convention, where a data value
between `domain_min` and `domain_max` is placed proportionally between
`range_min` and `range_max`. The current source only defines these
attributes; the mapping itself is not implemented yet.

`nice_ticks` is intended to pick round tick values for an axis covering a
domain, so that axis labels are easy to read. Like the other functions in
this release, it is a placeholder and does not yet return tick values.

The `Canvas` holds the overall `width`, `height`, and `background` of the
drawing.

## Marks

plotline has two mark types.

- `LineMark` describes a line series with `xs`, `ys`, and `stroke`.
- `BarMark` describes a bar series with `labels`, `values`, and `fill`.

Each mark is created empty and its attributes are filled in by the caller.

## Colors

`plotline.palette` provides a categorical palette. The module-level
constant `CATEGORY_COLORS` is the palette's name, and `categorical_colors()`
is the function that returns the list of colors for distinct series.

## Rendering and output

`render_svg()` is meant to return the SVG markup for a chart as a `str`.
`write_svg()` is meant to write that markup to a file. Neither function
accepts arguments in this release, and both are placeholders that return
`None`.

## Typical workflow

1. Create a `Canvas` and set its size and background.
2. Create a `LinearScale` for each axis and set its domain and range.
3. Pick ticks with `nice_ticks` and colors with `categorical_colors`.
4. Create one or more `LineMark` or `BarMark` objects and fill them in.
5. Render the chart with `render_svg`, or save it with `write_svg`.

Because the functions are placeholders in this release, the workflow above
describes the intended use of the API rather than output you can produce
today.
