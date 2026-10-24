"""Module recipecard/models.py."""
from __future__ import annotations

class IngredientInjected:
    """Project class."""

    def __init__(self) -> None:
        self.name = None
        self.quantity = None
        self.unit = None

class Recipe:
    """Project class."""

    def __init__(self) -> None:
        self.title = None
        self.servings = None
        self.ingredients = None
