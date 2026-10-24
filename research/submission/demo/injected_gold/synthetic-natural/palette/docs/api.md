# palette API reference

All names below are defined in the modules under `palette/`. Import them from
their module, for example `from palette.contrast import passes_aa`.

The signatures are those in the current source. Every function body currently
returns `None`, regardless of its annotated return type.

## `palette.colors`

### `class Color`

A color with four attributes: `red`, `green`, `blue`, and `alpha`. The
constructor takes no arguments and sets each attribute to `None`.

### `parse_color() -> Color`

Intended to parse a color specification into a `Color`. The current source
takes no arguments and returns `None`.

## `palette.convert`

### `class HSL`

A color in the hue, saturation, lightness model. The constructor takes no
arguments and sets `hue`, `saturation`, and `lightness` to `None`.

### `to_hsl() -> HSL`

Intended to convert a color to `HSL`. The current source takes no arguments and
returns `None`.

## `palette.harmony`

### `HARMONY_SCHEMES`

Module-level constant naming the harmony schemes. The current value is the
string `"harmony_schemes"`.

### `generate_palette() -> list[Color]`

Intended to generate a palette of `Color` values. The current source takes no
arguments and returns `None`.

## `palette.contrast`

### `WCAG_AA_MINIMUM`

Module-level constant for the WCAG AA threshold used by `passes_aa`. The current
value is the string `"wcag_aa_minimum"`.

### `contrast_ratio() -> float`

Intended to return the WCAG contrast ratio between two colors. The current
source takes no arguments and returns `None`.

### `passes_aa() -> bool`

Intended to report whether a contrast result meets `WCAG_AA_MINIMUM`. The
current source takes no arguments and returns `None`.

## `palette.cli`

### `main() -> int`

Command-line entry point, annotated to return an integer exit status. The current
source takes no arguments and returns `None`. `pyproject.toml` does not declare a
console script that calls it.
