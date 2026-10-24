# palette guide

This guide describes the concepts behind the `palette` modules and how they are
organized. For exact signatures, see the [API reference](api.md).

## Colors

A color is represented by the `Color` class in `palette/colors.py`. It has four
attributes: `red`, `green`, `blue`, and `alpha`. `parse_color` is the function
intended to build a `Color` from a textual color specification.

## HSL

`palette/convert.py` defines the `HSL` class, which holds the three components of
the hue, saturation, lightness color model: `hue`, `saturation`, and
`lightness`. The `to_hsl` function is intended to convert a color to this model
and is annotated to return an `HSL`.

## Harmonious palettes

`palette/harmony.py` provides `generate_palette`, which is annotated to return a
`list[Color]`. The module also defines `HARMONY_SCHEMES`, a module-level constant
that names the harmony schemes the generator is meant to support. In the current
source the constant is a plain string, so it does not yet list individual
schemes.

## Contrast and WCAG

`palette/contrast.py` contains the contrast helpers:

- `contrast_ratio` returns a `float`, the contrast ratio between two colors.
- `passes_aa` returns a `bool`, indicating whether a contrast result meets the
  WCAG AA level.
- `WCAG_AA_MINIMUM` is a module-level constant intended to hold the minimum
  ratio used by `passes_aa`. In the current source it is a plain string.

WCAG contrast is computed from the relative luminance of two colors. The
library's contrast functions are the place where that check belongs; the
current source bodies return `None`, so no ratio is computed yet.

## Command line

`palette/cli.py` defines `main`, annotated to return an `int`. It is the entry
point for command-line use. The `pyproject.toml` in this tree does not register
a console script for it.

## Module layout

| Module | Public names |
| --- | --- |
| `palette/colors.py` | `Color`, `parse_color` |
| `palette/convert.py` | `HSL`, `to_hsl` |
| `palette/harmony.py` | `HARMONY_SCHEMES`, `generate_palette` |
| `palette/contrast.py` | `WCAG_AA_MINIMUM`, `contrast_ratio`, `passes_aa` |
| `palette/cli.py` | `main` |

`palette/__init__.py` only sets the package docstring and `__version__`
(`"0.4.0"`); it does not re-export the names above, so import them from their
modules.
