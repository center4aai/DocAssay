# palette

`palette` is a small Python library for parsing colors, generating harmonious
palettes, and checking WCAG contrast ratios. It is aimed at developers who need
these color operations inside their own tools, scripts, or design pipelines.

Version: 0.4.0 (requires Python 3.11 or newer).

## Installation

Install from a local checkout:

```bash
pip install .
```

The only declared runtime dependency is `click>=8.1`.

## Quick start

The package exposes its public names from the `palette` modules:

```python
from palette.colors import parse_color
from palette.convert import to_hsl
from palette.harmony import generate_palette
from palette.contrast import contrast_ratio, passes_aa

color = parse_color()
hsl = to_hsl()
palette = generate_palette()
ratio = contrast_ratio()
ok = passes_aa()
```

The functions above take no arguments in the current source, and their bodies
return `None`. The example shows the import paths and call names; see the
[API reference](docs/api.md) for the signatures and return annotations as they
are written in the source.

## Documentation

- [Guide](docs/guide.md): the color and palette concepts used by the library and
  how the modules fit together.
- [API reference](docs/api.md): every public class, function, and constant.

## Command line

The package includes a `main` function in `palette/cli.py`. The `pyproject.toml`
in this tree does not declare a console script, so no `palette` command is
installed by `pip install .`.
