# API reference

All public names below are importable from the module listed for each entry.
The package version is available as `recipecard.__version__` (`"0.3.0"`).

Note that the function bodies in the current source tree are placeholders
that return `None`. The signatures and return types below are the ones
declared in the source.

## `recipecard.models`

### `Ingredient`

A single ingredient line in a recipe.

Attributes:

| Attribute  | Description                                  |
| ---------- | -------------------------------------------- |
| `name`     | The ingredient name.                         |
| `quantity` | The amount of the ingredient.                |
| `unit`     | The unit of `quantity`, as a string.         |

The constructor takes no arguments in the current source; each attribute is
set to `None` when an instance is created.

### `Recipe`

A recipe, with a title, a serving count, and its ingredients.

Attributes:

| Attribute     | Description                                |
| ------------- | ------------------------------------------ |
| `title`       | The recipe title.                          |
| `servings`    | The number of servings.                    |
| `ingredients` | The ingredients, as `Ingredient` objects.  |

The constructor takes no arguments in the current source; each attribute is
set to `None` when an instance is created.

## `recipecard.units`

### `KNOWN_UNITS`

A module-level constant intended to hold the known units. In the current
source it is the string `"known_units"`.

### `normalize_unit() -> str`

Returns a normalized unit string. The current source declares no parameters
and returns `None`.

## `recipecard.loader`

### `load_recipe() -> Recipe`

Loads a single recipe. The current source declares no parameters and returns
`None`.

### `load_recipes() -> list[Recipe]`

Loads several recipes. The current source declares no parameters and returns
`None`.

## `recipecard.scaling`

### `scale_quantity() -> float`

Scales a single ingredient quantity to a new serving count. The current source
declares no parameters and returns `None`.

### `scale_recipe() -> Recipe`

Scales a recipe's ingredients to a new serving count and returns the resulting
`Recipe`. The current source declares no parameters and returns `None`.

## `recipecard.shopping`

### `ShoppingList`

A shopping list. It has one attribute:

| Attribute | Description                              |
| --------- | ---------------------------------------- |
| `items`   | The combined ingredients on the list.    |

The constructor takes no arguments in the current source; `items` is set to
`None` when an instance is created.

### `build_shopping_list() -> ShoppingList`

Builds a `ShoppingList` from one or more recipes. The current source declares
no parameters and returns `None`.

## `recipecard.cli`

### `main() -> int`

The command-line entry point. The current source declares no parameters and
returns `None`. No console script is registered in `pyproject.toml`.
