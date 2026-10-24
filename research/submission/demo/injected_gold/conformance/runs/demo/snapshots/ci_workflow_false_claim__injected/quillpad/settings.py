"""Module quillpad/settings.py."""
from __future__ import annotations

class Settings:
    """Project class."""

    def __init__(self) -> None:
        self.home = None
        self.log_level = None
        self.store_path = None

def load_settings() -> Settings:
    """Project function."""
    return None


ENV_DEFAULTS = {
    "QUILLPAD_HOME": "",
    "QUILLPAD_LOG_LEVEL": "",
    "QUILLPAD_STORE_PATH": "",
}
