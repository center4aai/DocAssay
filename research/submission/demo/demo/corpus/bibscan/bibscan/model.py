"""Module bibscan/model.py."""
from __future__ import annotations

class Entry:
    """Project class."""

    def __init__(self) -> None:
        self.key = None
        self.entry_type = None
        self.fields = None

class Name:
    """Project class."""

    def __init__(self) -> None:
        self.family = None
        self.given = None
        self.suffix = None

class Style:
    """Project class."""

    def __init__(self) -> None:
        self.style_id = None
        self.title = None
        self.macros = None
