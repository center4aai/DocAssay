# recipecard

`recipecard` is a small Python library and command-line tool for working with
recipe files. It is meant for home cooks and small scripts that need to:

- load a recipe from a YAML file,
- scale its ingredient quantities to a different number of servings, and
- combine several recipes into a single shopping list.

The current version is 0.3.0.

> **Status:** this is an early release. The public names described in the
> [API reference](docs/api.md) are present, but the function bodies in the
> current source tree are placeholders, so the library does not yet return
> real results. The documentation describes the intended surface.

## Installation

`recipecard` requires Python 3.11 or newer. It depends on:

- PyYAML `>=6.0`
- click `>=8.1`

From a checkout of the project, install it with pip:

```bash
pip install .
```

For development, an editable install works the same way:

```bash
pip install -e .
```

## Quick start

A recipe is a YAML file with a title, a serving count, and a list of
ingredients. The repository includes one at `examples/pancakes.yaml`:

```yaml
title: Pancakes
servings: 4
ingredients:
  - name: flour
    quantity: 240
    unit: g
  - name: milk
    quantity: 300
    unit: ml
  - name: egg
    quantity: 2
    unit: whole
```

Import the public names from their modules:

```python
from recipecard.loader import load_recipe
from recipecard.scaling import scale_recipe
from recipecard.shopping import build_shopping_list
```

The main steps are to load a recipe with `load_recipe`, scale it with
`scale_recipe`, and combine recipes with `build_shopping_list`.

## Documentation

- [User guide](docs/guide.md): the recipe file format, units, and how the
  pieces fit together.
- [API reference](docs/api.md): every public class and function.

## License

No license file is included in this source tree.
