# User guide

This guide covers the recipe file format and the three tasks `recipecard` is
built around: loading recipes, scaling them, and building shopping lists. For
the exact names and signatures, see the [API reference](api.md).

## Recipe files

A recipe file is a YAML document with three top-level keys:

| Key           | Description                                      |
| ------------- | ------------------------------------------------ |
| `title`       | The name of the recipe, such as `Pancakes`.      |
| `servings`    | The number of servings the listed quantities make. |
| `ingredients` | A list of ingredient entries.                    |

Each entry in `ingredients` has three keys:

| Key        | Description                                        |
| ---------- | -------------------------------------------------- |
| `name`     | The ingredient, such as `flour`.                   |
| `quantity` | The amount, as a number.                           |
| `unit`     | The unit of the quantity, such as `g`, `ml`, or `whole`. |

The file `examples/pancakes.yaml` in the repository shows a complete recipe:

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

The three keys and the entry fields above are the ones the `Recipe` and
`Ingredient` classes carry (see [`Recipe`](api.md#recipe) and
[`Ingredient`](api.md#ingredient)).

## Units

Units are plain strings. The `recipecard.units` module defines a `KNOWN_UNITS`
constant and a `normalize_unit` function for working with them. The current
source defines `KNOWN_UNITS` as a placeholder string, so it is not yet a
usable list of units. The example recipe uses `g`, `ml`, and `whole`.

## Loading recipes

`load_recipe` reads one recipe and returns a `Recipe`. `load_recipes` is the
multi-recipe counterpart and returns a `list[Recipe]`. Both are in
`recipecard.loader`.

## Scaling

Scaling changes the quantities of a recipe to a new serving count.

- `scale_quantity` returns a single quantity as a `float`.
- `scale_recipe` returns a `Recipe` whose ingredients are scaled.

Both live in `recipecard.scaling`.

## Shopping lists

`build_shopping_list` combines recipes into a `ShoppingList`, which holds the
combined ingredients in its `items` attribute. The function and the class are
in `recipecard.shopping`.

## Command-line interface

The package contains `recipecard.cli`, which defines a `main` function that
returns an `int`. The current source body of `main` is a placeholder, and the
project does not declare a console script in `pyproject.toml`, so there is no
`recipecard` executable installed by the package at this version. Use the
Python functions described in the [API reference](api.md) instead.
