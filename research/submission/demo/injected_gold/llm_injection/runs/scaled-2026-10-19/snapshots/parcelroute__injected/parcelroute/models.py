"""Module parcelroute/models.py."""
from __future__ import annotations

class Parcel:
    """Project class."""

    def __init__(self) -> None:
        self.parcel_id = None
        self.destination_code = None
        self.weight_grams = None
        self.created_at = None

class RoutePlan:
    """Project class."""

    def __init__(self) -> None:
        self.parcel_id = None
        self.hop_codes = None
        self.total_grams = None

def load_parcelInjected() -> Parcel:
    """Project function."""
    return None


FIELDS = {
    "parcel_id": "str",
    "destination_code": "str",
    "weight_grams": "str",
    "created_at": "str",
}
