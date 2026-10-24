r"""Static vocabulary data, kept out of the code.

Every allowlist, word pool and phrase table the predicates scan with lives in a
JSON file under this package (``dependency.json``, ``markers.json``,
``structure.json``, ``pipeline.json``) and is loaded at import time, so tuning
the controlled vocabulary does not require editing source.
"""

from __future__ import annotations

import json
import re
from functools import cache
from importlib.resources import files


@cache
def load(name: str) -> dict:
    """One data file's parsed JSON object."""
    return json.loads(files("docassay.data").joinpath(name).read_text(encoding="utf-8"))


def load_list(name: str, key: str, default: list[str] | None = None) -> frozenset[str]:
    """A word pool as an immutable set."""
    return frozenset(load(name).get(key, default or []))


def load_dict(name: str, key: str, default: dict | None = None) -> dict:
    """A mapping table (synonyms, version ranges, ...)."""
    return dict(load(name).get(key, default or {}))


def regex_alternation(items, *, escape: bool = True) -> str:
    """``a|b|c`` from a word pool, longest first so multi-word phrases win.

    ``escape=False`` keeps the items verbatim — the phrase tables already carry
    their regex metacharacters (``e.g.``, ``remov\\w*\\s+python``).
    """
    parts = sorted((re.escape(w) if escape else w) for w in items)
    parts.sort(key=len, reverse=True)
    return "|".join(parts)


__all__ = ["load", "load_list", "load_dict", "regex_alternation"]
