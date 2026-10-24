"""Module gaugekit/models.py."""
from __future__ import annotations

class Reading:
    """Project class."""

    def __init__(self) -> None:
        self.timestamp = None
        self.discharge_cfs = None
        self.gauge_height_ft = None

class GaugeSeries:
    """Project class."""

    def __init__(self) -> None:
        self.station_id = None
        self.readings = None
