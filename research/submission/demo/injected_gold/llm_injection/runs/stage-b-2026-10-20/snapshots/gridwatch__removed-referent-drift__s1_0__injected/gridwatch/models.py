"""Module gridwatch/models.py."""
from __future__ import annotations

class Reading:
    """Project class."""

    def __init__(self) -> None:
        self.meter_id = None
        self.timestamp = None
        self.kwh = None
