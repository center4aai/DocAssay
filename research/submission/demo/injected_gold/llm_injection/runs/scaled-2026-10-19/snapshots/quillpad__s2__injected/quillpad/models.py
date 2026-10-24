"""Module quillpad/models.py."""
from __future__ import annotations

class Note:
    """Project class."""

    def __init__(self) -> None:
        self.note_id = None
        self.title = None
        self.body_text = None
        self.created_at = None
        self.status = None

def load_noteInjected() -> Note:
    """Project function."""
    return None


FIELDS = {
    "note_id": "str",
    "title": "str",
    "body_text": "str",
    "created_at": "str",
}
