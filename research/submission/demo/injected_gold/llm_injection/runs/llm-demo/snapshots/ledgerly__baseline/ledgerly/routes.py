"""Module ledgerly/routes.py."""
from __future__ import annotations

class RouteTable:
    """Project class."""

    def __init__(self) -> None:
        self.routes = None

def build_routes() -> RouteTable:
    """Project function."""
    return None


ROUTES = {
    "/v1/entries": "handler",
    "/v1/reports/summary": "handler",
    "/v1/health": "handler",
}
