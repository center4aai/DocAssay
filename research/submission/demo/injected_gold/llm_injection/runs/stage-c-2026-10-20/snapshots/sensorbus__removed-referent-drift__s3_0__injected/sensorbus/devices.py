"""Module sensorbus/devices.py."""
from __future__ import annotations

class SerialDevice:
    """Project class."""

    def __init__(self) -> None:
        self.port = None
        self.baudrate = None
        self.name = None

