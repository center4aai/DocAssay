"""Module plotline/marks.py."""
from __future__ import annotations

class LineMark:
    """Project class."""

    def __init__(self) -> None:
        self.xs = None
        self.ys = None
        self.stroke = None

class BarMark:
    """Project class."""

    def __init__(self) -> None:
        self.labels = None
        self.values = None
        self.fill = None
