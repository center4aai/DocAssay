"""Module sensorbus/readings.py."""
from __future__ import annotations

class Reading:
    """Project class."""

    def __init__(self) -> None:
        self.sensor_id = None
        self.value = None
        self.unit = None
        self.timestamp = None

class ReadingBatch:
    """Project class."""

    def __init__(self) -> None:
        self.readings = None
        self.sensor_id = None

def parse_line() -> Reading:
    """Project function."""
    return None
