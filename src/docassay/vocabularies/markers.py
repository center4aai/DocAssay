"""Context-marker word pools and their compiled patterns.

``platform``, ``time``, ``arch`` are matched window-wide; ``polarity``
(negation) and ``restriction`` (exclusion) words are matched per-anchor with
verb gating in ``markers.context``. The pools live in ``data/markers.json``.
"""

from __future__ import annotations

import re

from docassay.data import load_list, regex_alternation

# Negation words fix the verdict (§6.1); exclusion words qualify the referent
# without negating its existence.
NEGATION_WORDS: frozenset[str] = load_list("markers.json", "negation_words")
EXCLUSION_WORDS: frozenset[str] = load_list("markers.json", "exclusion_words")

PLATFORM_WORDS: frozenset[str] = load_list("markers.json", "platform_words")
TIME_WORDS: frozenset[str] = load_list("markers.json", "time_words")
ARCH_WORDS: frozenset[str] = load_list("markers.json", "arch_words")

# Past-state word markers (downgrade REFUTED→NEI in the structure predicates).
HISTORICAL_TIME: frozenset[str] = load_list("markers.json", "historical_time")
# Past-copula constructions ("was split off", "were exposed") — a past state
# mention the word-level markers cannot see. Phrase pool (escape=False).
HISTORICAL_VERB_FORMS: list[str] = load_list("markers.json", "historical_verb_forms")

# Time words that are historical only NEXT TO a version or a date ("since 2.0",
# "until v3", "before 2024", "as of Airflow 2.7.0") — "after installing",
# "blocks until interrupted" and "time series" are not historical references.
# Shared with the DEPENDENCY predicate, where the same rule was introduced in
# Phase 1 (predicates/dependency.py).
_CONTEXTUAL_TIME: frozenset[str] = frozenset({"as of", "before", "after", "since", "until"})
_ALWAYS_HISTORICAL_TIME: frozenset[str] = frozenset(
    w for w in HISTORICAL_TIME if w not in _CONTEXTUAL_TIME
)
_VERSION_OR_DATE_NEAR = re.compile(
    r"\b(?:as\s+of|after|before|since|until)\s+(?:the\s+)?(?:version\s+)?"
    r"(?:v?\d+(?:\.\d+){0,3}|\d{4})\b",
    re.IGNORECASE,
)

# Order matters: multi-word phrases ("mac os x") must match before their parts
# (regex_alternation sorts longest-first).
_PLATFORM_RE = re.compile(
    rf"(?<![a-z0-9])(?:{regex_alternation(PLATFORM_WORDS)})(?![a-z0-9])",
    re.IGNORECASE,
)
_TIME_RE = re.compile(
    rf"(?<![a-z0-9])(?:{regex_alternation(TIME_WORDS)})(?![a-z0-9])",
    re.IGNORECASE,
)
_ARCH_RE = re.compile(
    rf"(?<![a-z0-9])(?:{regex_alternation(ARCH_WORDS)})(?![a-z0-9])",
    re.IGNORECASE,
)
_POLARITY_RE = re.compile(
    rf"(?<![a-z0-9])(?:{regex_alternation(NEGATION_WORDS)})(?![a-z0-9])",
    re.IGNORECASE,
)
_RESTRICTION_RE = re.compile(
    rf"(?<![a-z0-9])(?:{regex_alternation(EXCLUSION_WORDS)})(?![a-z0-9])",
    re.IGNORECASE,
)
_HISTORICAL_VERB_RE = re.compile(
    rf"(?<![a-z0-9])(?:{regex_alternation(HISTORICAL_VERB_FORMS, escape=False)})(?![a-z0-9])",
    re.IGNORECASE,
)

# Performance notes ("faster/slower/less memory ... with X <version> or
# later"): a version mention describing a performance property, not a project
# requirement (the abstention rules E:PERF). Shared by the DEPENDENCY predicate
# layer and the triage classifier.
_PERF_RE = re.compile(
    r"\b(?:faster|slower|speed(?:ier|iest)?|performance|performant|optimiz\w*|"
    r"efficien\w*|less\s+memory|more\s+memory|memory\s+(?:usage|footprint)|scal\w+)\b",
    re.IGNORECASE,
)


def platform_regex() -> re.Pattern[str]:
    return _PLATFORM_RE


def time_regex() -> re.Pattern[str]:
    return _TIME_RE


def arch_regex() -> re.Pattern[str]:
    return _ARCH_RE


def polarity_regex() -> re.Pattern[str]:
    return _POLARITY_RE


def restriction_regex() -> re.Pattern[str]:
    return _RESTRICTION_RE


def perf_re() -> re.Pattern[str]:
    return _PERF_RE


def is_historical_mention(context, raw_context: str) -> bool:
    """Whether a mention is historical (past/ceased state), downgrading REFUTED→NEI.

    The word-level ``historical_time`` markers are matched window-wide into
    ``context.time``; the past-copula constructions ("was split off", "were
    exposed") are an additive, phrase-level signal on the raw window. Both make
    a mention a past-state reference rather than a current existence claim.

    ``as of``/``after``/``before``/``since``/``until`` are historical only next
    to a version or a date ("since 2.0", "until v3"); "after installing" and
    "blocks until interrupted" stay current-state. This mirrors
    the DEPENDENCY predicate's contextual rule from Phase 1.
    """
    if context.time & _ALWAYS_HISTORICAL_TIME:
        return True
    if context.time & _CONTEXTUAL_TIME:
        if _VERSION_OR_DATE_NEAR.search(raw_context):
            return True
    return bool(_HISTORICAL_VERB_RE.search(raw_context))
