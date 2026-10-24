"""Module ledgerly/models.py."""
from __future__ import annotations

class Entry:
    """Project class."""

    def __init__(self) -> None:
        self.entry_id = None
        self.account = None
        self.amount = None
        self.memo = None
        self.posted_at = None

def parse_entry() -> Entry:
    """Project function."""
    return None



FIELDS = {
    "entry_id": "str",
    "account": "str",
    "amount": "str",
    "posted_at": "str",
}
