"""Module tidecast/store.py."""
from __future__ import annotations

class ForecastStore:
    """Project class."""

    def __init__(self) -> None:
        self.root = None
        self.load = None
        self.save = None

def default_store() -> ForecastStore:
    """Project function."""
    return None
