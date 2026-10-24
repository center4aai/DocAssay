"""Shared existence-negation detection for window-scanned predicates.

A path or symbol token tokenizes into several word tokens, so the verb-gated
negation in ``markers.context`` cannot attach a negator to it. The listing and
symbol predicates own this detection; the surrounding logic is identical and
lives here, while each predicate supplies its own ``existence`` pattern for the
referent-specific cue ("no such file/directory" vs. "no such symbol").
"""

from __future__ import annotations

import re

# A negator immediately before the anchor ("no `x`", "not `x`").
NEGATOR_BEFORE_RE = re.compile(
    r"(?:no|not|without|nor|neither)\s+[`]?\s*$",
    re.IGNORECASE,
)

# A negation inside a hypothetical/instructional construction is not an
# existence claim: "if ... there is no X", "Installing without X". The
# existence-negation detection must not fire there.
HYPOTHETICAL_NEG_RE = re.compile(
    r"\bif\b[^.;\n]{0,80}\b(?:no|without)\b|\b(?:installing|install)\s+without\b",
    re.IGNORECASE,
)


def window_negation(window: str, start: int, existence: re.Pattern[str]) -> bool:
    """Whether the window negates the existence of the anchor at ``start``.

    ``existence`` is the predicate's existence-negation pattern (the "no such
    file/directory" or "no such symbol" cue).
    """
    low = window.lower()
    around = low[max(0, start - 80) : min(len(low), start + 80)]
    hypothetical = HYPOTHETICAL_NEG_RE.search(low)
    if existence.search(around) and not hypothetical:
        return True
    before = low[max(0, start - 24) : start]
    return bool(NEGATOR_BEFORE_RE.search(before) and not hypothetical)
