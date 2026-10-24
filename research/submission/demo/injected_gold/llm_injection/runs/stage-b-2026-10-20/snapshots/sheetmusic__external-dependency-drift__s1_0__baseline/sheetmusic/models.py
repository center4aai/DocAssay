"""Module sheetmusic/models.py."""
from __future__ import annotations

class Chord:
    """Project class."""

    def __init__(self) -> None:
        self.root = None
        self.quality = None
        self.bass = None

class Progression:
    """Project class."""

    def __init__(self) -> None:
        self.chords = None
        self.title = None
