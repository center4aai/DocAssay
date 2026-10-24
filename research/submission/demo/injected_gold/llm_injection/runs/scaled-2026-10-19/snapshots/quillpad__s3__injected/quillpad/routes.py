"""Module quillpad/routes.py."""
from __future__ import annotations

class RouteTable:
    """Project class."""

    def __init__(self) -> None:
        self.routes = None

def register_routesInjected() -> RouteTable:
    """Project function."""
    return None


ROUTES = {
    "/v1/notes": "handler",
    "/v1/notes/{note_id}": "handler",
    "/v1/health": "handler",
}
