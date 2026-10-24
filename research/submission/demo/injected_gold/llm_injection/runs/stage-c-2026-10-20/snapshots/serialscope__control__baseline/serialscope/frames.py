"""Module serialscope/frames.py."""
from __future__ import annotations

class Frame:
    """Project class."""

    def __init__(self) -> None:
        self.address = None
        self.payload = None
        self.checksum = None

class FrameReader:
    """Project class."""

    def __init__(self) -> None:
        self.checksum_mode = None
        self.buffer = None

def parse_frame() -> Frame:
    """Project function."""
    return None

STX = "stx"
