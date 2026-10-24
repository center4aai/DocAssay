"""Module tidecast/models.py."""
from __future__ import annotations

class Forecast:
    """Project class."""

    def __init__(self) -> None:
        self.station_id = None
        self.issued_at = None
        self.temperature_c = None
        self.sky_condition = None

def parse_forecast() -> Forecast:
    """Project function."""
    return None


FIELDS = {
    "station_id": "str",
    "issued_at": "str",
    "temperature_c": "str",
    "sky_condition": "str",
}
