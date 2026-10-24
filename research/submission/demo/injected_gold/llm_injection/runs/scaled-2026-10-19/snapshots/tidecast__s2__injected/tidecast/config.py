"""Module tidecast/config.py."""
from __future__ import annotations

class Settings:
    """Project class."""

    def __init__(self) -> None:
        self.home = None
        self.log_level = None
        self.cache_ttl = None

def load_settings() -> Settings:
    """Project function."""
    return None


ENV_DEFAULTS = {
    "TIDECAST_HOME": "",
    "TIDECAST_LOG_LEVEL": "",
    "TIDECAST_CACHE_TTL": "",
    "TIDECAST_HTTP_PORT": "",
}
