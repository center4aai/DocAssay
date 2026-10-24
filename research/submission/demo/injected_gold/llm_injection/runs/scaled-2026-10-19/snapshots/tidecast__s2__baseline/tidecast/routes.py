"""Module tidecast/routes.py."""
from __future__ import annotations

class RouteTable:
    """Project class."""

    def __init__(self) -> None:
        self.routes = None
        self.add = None

def build_routes() -> RouteTable:
    """Project function."""
    return None


ROUTES = {
    "/v1/forecast": "handler",
    "/v1/stations": "handler",
    "/v1/health": "handler",
}
