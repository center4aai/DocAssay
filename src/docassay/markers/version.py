"""Version marker extraction and not-contradiction semantics.

Extraction: a version-shaped token becomes a constraint only when
it is explicitly modified ("or higher", "at least", "exactly") or sits next to
its dependency anchor — never from an unrelated number. A bare single-component
version ("Pydantic v2") reads as a line reference ``>=X``.

Matching (decided 2026-09-13): the doc is REFUTED when it admits a
version the manifest excludes — a finite list/pin is supported iff every listed
version is allowed; a range whose lower bound sits below the manifest floor (or
upper bound above the ceiling) is REFUTED; a doc that is merely stricter than
the manifest (lower bound above the floor) is undecidable (NEI). A bare major
line ("Python 3") is compared by major only; an upper-bound-only claim ("<4")
is NEI.
"""

from __future__ import annotations

import re

from docassay.data import load_dict, load_list
from docassay.vocabularies.dependency import DEPENDENCY_NAMES

_VERSION_OP_RE = re.compile(r"(>=|<=|>|<|==|~=|\^|!=)\s*(v?\d+(?:\.\d+){0,3})", re.IGNORECASE)
_VERSION_NUMBER_RE = re.compile(r"\bv?\d+(?:\.\d+){0,3}\b(?!\.\d)", re.IGNORECASE)

# Comparative-modifier phrases and ordinal/section nouns (data/markers.json).
_GE_SUFFIXES: frozenset[str] = load_list("markers.json", "ge_suffixes")
_LE_SUFFIXES: frozenset[str] = load_list("markers.json", "le_suffixes")
_GE_PREFIXES: frozenset[str] = load_list("markers.json", "ge_prefixes")
_LE_PREFIXES: frozenset[str] = load_list("markers.json", "le_prefixes")
_EQ_PREFIXES: frozenset[str] = load_list("markers.json", "eq_prefixes")

_BEFORE_WINDOW_CHARS = 28
_NON_VERSION_PREFIXES = set("=/?&:[-,(*'\"{")

# A version after ``:`` is usually a listing/section value ("Python version:
# 3.10"), not an argument or timestamp. It is admitted only when the token
# before the colon is a version word or a known dependency name — "Supported
# versions: 3.10+" and "Python: 3.10 or newer" keep their version, while
# "8080:8080", "localhost:8000" and "20:42" stay blocked.
_VERSION_COLON_WORDS: frozenset[str] = frozenset(
    {"version", "versions", "release", "revision", "rev"}
)
_DEP_NAMES_LOWER: frozenset[str] = frozenset(n.lower() for n in DEPENDENCY_NAMES)


def _version_after_colon_ok(before: str) -> bool:
    """Whether the text before a ``:``-prefixed number reads like a version slot."""
    head = before.rstrip()
    if not head.endswith(":"):
        return False
    tokens = re.findall(r"[a-z][a-z0-9._-]*", head[:-1].lower())
    last = tokens[-1] if tokens else ""
    return last in _VERSION_COLON_WORDS or last in _DEP_NAMES_LOWER


# A number followed by " bit"/" bits" is a bitness, not a version ("32 bit").
_BITNESS_RE = re.compile(r"bits?\b")
# A bare number preceded by a CLI flag ("-p 8080", "--num_cores 8", "-c 1000")
# or followed by a timestamp/ratio colon ("20:42") is an argument, not a version.
_FLAG_BEFORE_RE = re.compile(r"(?<![a-z0-9])--?[a-z][a-z0-9-]*\s*$")
# A number preceded by a comma is a version-list member ("3.9, 3.10 or 3.11")
# only when the token before the comma is itself a version number AND the
# member carries a minor component or is followed by a conjunction. Bare
# single-component argument lists ("permute(1, 2, 0)") stay rejected.
_LIST_MEMBER_RE = re.compile(r"(?:>=|<=|>|<|==|~=|\^|!=)?\s*v?\d+(?:\.\d+){0,3}\s*,\s*$")


def _is_version_list_member(low: str, start: int, end: int) -> bool:
    """Whether the number ``low[start:end]`` is a member of a version list."""
    before = low[max(0, start - 24) : start]
    if not _LIST_MEMBER_RE.search(before):
        return False
    if "." in low[start:end]:
        return True
    after = low[end : end + 12]
    return bool(re.match(r"\s+(?:or|and)\b", after))


# Ordinal/section nouns that make a following bare number a step/phase/test
# reference rather than a version ("Phase 3", "Stage 6", "test 12").
# (data/markers.json)
_ORDINAL_CONTEXT: frozenset[str] = load_list("markers.json", "ordinal_context")

_CLAUSE_RE = re.compile(r"^\s*(>=|<=|>|<|==|~=|\^|!=)?\s*(v?)([0-9]+(?:\.[0-9]+)*)(.*?)\s*$")
_VERSION_COMPONENT_RE = re.compile(r"^([0-9]+)(.*)$")


def _num_token(value: str) -> str:
    return value.lower().lstrip("v")


def _phrase_precedes(text: str, phrase: str) -> bool:
    """Whether ``phrase`` precedes the number (the anchor may sit between).

    Markdown emphasis (``*``/``_``/``#```) is stripped first so ``Minimum**:
    Python 3.10`` still reads ``minimum``.
    """
    tail = re.sub(r"[*_`#]+", "", text).rstrip()
    tail = re.sub(r"[^a-z]+$", "", tail)
    if tail.endswith(phrase):
        return True
    head, _, _ = tail.rpartition(" ")
    head = re.sub(r"[^a-z]+$", "", head)
    return head.endswith(phrase)


def version_candidates(low: str) -> list[tuple[str, str, int]]:
    """Every ``(op, num, position)`` version-shaped token in the window."""
    candidates: list[tuple[str, str, int]] = []
    op_spans: list[tuple[int, int]] = []
    for m in _VERSION_OP_RE.finditer(low):
        candidates.append((m.group(1).lower(), _num_token(m.group(2)), m.start()))
        op_spans.append((m.start(), m.end()))
    for m in _VERSION_NUMBER_RE.finditer(low):
        if any(s <= m.start() and m.end() <= e for s, e in op_spans):
            continue
        start = m.start()
        before = low[max(0, start - _BEFORE_WINDOW_CHARS) : start]
        after = low[m.end() : m.end() + 18].lstrip()
        # Issue/PR references (#3902), percentages (100%), and values in URLs,
        # query strings, paths or env assignments (=, /, ?, &, :, -, [) are not
        # versions; such a number is discarded before modifier detection.
        if before.rstrip().endswith("#") or after.startswith("%"):
            continue
        if before.rstrip() and before.rstrip()[-1] in _NON_VERSION_PREFIXES:
            if not _is_version_list_member(low, start, m.end()):
                if before.rstrip()[-1] == ":" and _version_after_colon_ok(before):
                    pass  # "Python version: 3.10" — a version slot, not an argument
                else:
                    continue
        if after.startswith("/") or _BITNESS_RE.match(after):
            continue  # path segment like "v3/api-ref", or bitness "32 bit"
        if after.startswith(":"):
            continue  # timestamp/ratio like "20:42"
        if _FLAG_BEFORE_RE.search(before):
            continue  # CLI-flag argument value like "-p 8080" or "--num_cores 8"
        preceding_token = before.rstrip().rsplit(" ", 1)[-1]
        if preceding_token in _ORDINAL_CONTEXT:
            continue
        modifier = "=="
        num = _num_token(m.group(0))
        matched_phrase = False
        if any(_phrase_precedes(before, p) for p in _GE_PREFIXES):
            modifier = ">="
            matched_phrase = True
        elif any(_phrase_precedes(before, p) for p in _LE_PREFIXES):
            modifier = "<="
            matched_phrase = True
        elif any(_phrase_precedes(before, p) for p in _EQ_PREFIXES):
            modifier = "=="
            matched_phrase = True
        elif after.startswith("+") or any(after.startswith(s) for s in _GE_SUFFIXES):
            modifier = ">="
            matched_phrase = True
        elif any(after.startswith(s) for s in _LE_SUFFIXES):
            modifier = "<="
            matched_phrase = True
        # A bare single-component version is a line reference, not a pin:
        # "Pydantic v2" / "Python 3" means "2.x or newer", so it reads >=X.
        if modifier == "==" and not matched_phrase and "." not in num:
            modifier = ">="
        candidates.append((modifier, num, start))
    return candidates


def _version_sort_key(item: tuple[str, str]) -> tuple[tuple[int, ...], str]:
    op, num = item
    return (tuple(int(part) for part in num.split(".")), op)


def combine_version(cands: list[tuple[str, str]]) -> str | None:
    """One constraint string from the candidates owned by an anchor.

    ``None`` when there is nothing or the candidates conflict (two bounds of the
    same kind, a pin mixed with a bound) — the §4.3 LLM-fallback case. Multiple
    ``==`` pins owned by one anchor form a disjunctive set claim ("Python 3.9,
    3.10 or 3.11") and combine to ``==3.9,==3.10,==3.11``.
    """
    if not cands:
        return None
    if len(cands) == 1:
        op, num = cands[0]
        return f"{op}{num}"
    ops = {op for op, _ in cands}
    if "==" in ops:
        pins = sorted(
            {num for op, num in cands if op == "=="}, key=lambda n: _version_sort_key(("==", n))
        )
        if len(pins) == len(cands):
            return ",".join(f"=={num}" for num in pins)
        return None
    if "!=" in ops:
        return None
    by_op: dict[str, set[str]] = {}
    for op, num in cands:
        by_op.setdefault(op, set()).add(num)
    if any(len(vals) > 1 for vals in by_op.values()):
        return None
    return ",".join(f"{op}{num}" for op, num in sorted(cands, key=_version_sort_key))


def parse_constraint(spec: str) -> tuple[tuple[str, tuple[tuple[int, str], ...]], ...] | None:
    """Canonicalize a constraint into sorted ``(op, version)`` clauses.

    Returns ``None`` when the constraint is empty or not reducible to an exact
    comparison (wildcards, unknown operators). ``~=`` and ``^`` are expanded to
    their PEP 440 / caret bounding clauses.
    """
    if not spec or not spec.strip():
        return None
    clauses: list[tuple[str, tuple[tuple[int, str], ...]]] = []
    for raw in spec.split(","):
        match = _CLAUSE_RE.match(raw)
        if not match:
            return None
        op, prefix, digits, suffix = match.groups()
        op = (op or "==").lower()
        if "*" in suffix or "*" in digits or ".x" in suffix.lower() or ".x" in digits.lower():
            return None
        version = _parse_version(digits, suffix)
        if version is None:
            return None
        if op == "~=":
            clauses.append((">=", version))
            clauses.append(("<", _bump(version, len(version) - 2)))
        elif op == "^":
            clauses.append((">=", version))
            clauses.append(("<", _bump(version, 0)))
        else:
            clauses.append((op, version))
    return tuple(sorted(clauses))


def _parse_version(digits: str, suffix: str) -> tuple[tuple[int, str], ...] | None:
    """Normalize ``3.12.1rc1`` into ((3, ''), (12, ''), (1, 'rc1'))."""
    if not digits:
        return None
    parts: list[tuple[int, str]] = []
    for component in digits.split("."):
        m = _VERSION_COMPONENT_RE.match(component)
        if not m:
            return None
        parts.append((int(m.group(1)), m.group(2).lower()))
    while len(parts) > 1 and parts[-1] == (0, ""):
        parts.pop()
    return tuple(parts)


def _bump(version: tuple[tuple[int, str], ...], index: int) -> tuple[tuple[int, str], ...]:
    parts = list(version)
    if index < 0:
        index = 0
    value, suffix = parts[index]
    parts[index] = (value + 1, suffix)
    return tuple(parts[: index + 1])


def constraint_satisfied(claim_constraint: str, manifest_constraint: str) -> bool | None:
    """Whether the doc's version claim is *not contradicted* by the manifest.

    Semantics (decided 2026-09-13; replaces the 2026-08-27
    "manifest ⊆ claim" containment rule):

    - a **pin / finite list** claim (``==3.9,==3.10``) is SUPPORTED iff every
      listed version is allowed by the manifest — ``3.9`` outside ``>=3.10``
      is REFUTED;
    - a **range** claim is REFUTED when its lower bound sits below the
      manifest floor (``3.8+`` doc vs ``>=3.10`` code promises versions the
      code excludes), its upper bound above the manifest ceiling, or the two
      intervals are disjoint (``>=8.1`` doc vs ``<8.1`` code); a doc that is
      merely stricter than an intersecting manifest (``3.12+`` doc vs
      ``>=3.10``) is undecidable (NEI);
    - a **bare major line** ("Python 3", "Pydantic v2") is compared by major
      only;
    - an **upper-bound-only** claim (``<4``) is NEI.

    ``None`` when the comparison is undecidable (wildcard, unknown form).
    """
    claim = parse_constraint(claim_constraint)
    manifest = parse_constraint(manifest_constraint)
    if claim is None or manifest is None:
        return None
    m_low, m_low_inc, m_high, m_high_inc, m_excluded = _version_interval(manifest)
    if m_low is None and m_high is None:
        return None
    # A disjunctive set claim ("3.9, 3.10 or 3.11") or a pin: supported iff
    # every listed version is allowed by the manifest.
    if all(op == "==" for op, _ in claim):
        return all(
            _version_in_interval(v, m_low, m_low_inc, m_high, m_high_inc) and v not in m_excluded
            for _, v in claim
        )
    claim_interval = _version_interval(claim)
    c_low, c_low_inc, c_high, _c_high_inc, _c_excluded = claim_interval
    # Disjoint intervals contradict even when one side has no matching bound:
    # doc ``click>=8.1`` vs manifest ``click<8.1`` shares no version, so every
    # version the doc admits is excluded by the manifest (Stage B E2). The check
    # runs before the lower/upper comparisons, which cannot see across an
    # open side. An upper-bound-only claim (``<4``) keeps its existing NEI
    # semantics; a ``!=``-only claim has no bounds and is checked here.
    if not (c_low is None and c_high is not None) and _intersection_is_empty(
        claim_interval,
        (m_low, m_low_inc, m_high, m_high_inc, m_excluded),
    ):
        return False
    if c_low is None and c_high is None:
        return None
    # A bare major line ("Python 3", "Pydantic v2"): compare majors only.
    if c_low is not None and len(c_low) == 1 and c_high is None and m_low is not None:
        major_c, major_m = c_low[0][0], m_low[0][0]
        return True if major_c == major_m else (False if major_c < major_m else None)
    if c_low is not None and m_low is not None:
        cmp = _cmp_version(c_low, m_low)
        if cmp < 0 or (cmp == 0 and c_low_inc and not m_low_inc):
            return False  # the doc admits versions the manifest excludes
        if cmp > 0:
            return None  # the doc is stricter: an understatement, not a contradiction
    if c_low is None and m_low is not None:
        return None  # an upper-bound-only claim is undecidable
    if c_high is not None and m_high is not None and _cmp_version(c_high, m_high) > 0:
        return False  # the doc admits versions above the manifest ceiling
    return True


def _version_interval(
    clauses: tuple[tuple[str, tuple[tuple[int, str], ...]], ...],
) -> tuple[
    tuple[tuple[int, str], ...] | None,
    bool,
    tuple[tuple[int, str], ...] | None,
    bool,
    frozenset[tuple[tuple[int, str], ...]],
]:
    """Bounding interval ``[low, high]`` plus the excluded ``!=`` points.

    ``low``/``high`` are version tuples, or ``None`` for an open side. ``!=``
    clauses are collected separately: their removed points may matter for
    deciding refutation.
    """
    low: tuple[tuple[int, str], ...] | None = None
    low_inc = True
    high: tuple[tuple[int, str], ...] | None = None
    high_inc = True
    excluded: set[tuple[tuple[int, str], ...]] = set()
    has_pin = False
    pin: tuple[tuple[int, str], ...] = ()

    for op, version in clauses:
        if op == "==":
            has_pin = True
            pin = version
        elif op == "!=":
            excluded.add(version)
        elif op in {">=", ">"}:
            if low is None or _cmp_version(version, low) > 0:
                low, low_inc = version, op == ">="
        elif op in {"<=", "<"}:
            if high is None or _cmp_version(version, high) < 0:
                high, high_inc = version, op == "<="

    if has_pin:
        for op, version in clauses:
            if op == "==" or op == "!=":
                continue
            if not _clause_holds(op, pin, version):
                return (None, True, None, True, frozenset(excluded))
        return (pin, True, pin, True, frozenset(excluded))
    return (low, low_inc, high, high_inc, frozenset(excluded))


_Version = tuple[tuple[int, str], ...]
_Interval = tuple[
    _Version | None,
    bool,
    _Version | None,
    bool,
    frozenset[_Version],
]


def _intersection_is_empty(claim: _Interval, manifest: _Interval) -> bool:
    """Whether two bounding intervals share no version.

    ``low``/``high`` are version tuples or ``None`` for an open side; the
    booleans record inclusivity. A single surviving point is empty when either
    side excludes it (``!=8.1`` against a manifest pin ``==8.1``), and an open
    bound on either side means infinitely many points survive.
    """
    low, low_inc, high, high_inc, excluded = claim
    m_low, m_low_inc, m_high, m_high_inc, m_excluded = manifest
    if m_low is not None:
        if low is None:
            low, low_inc = m_low, m_low_inc
        else:
            cmp = _cmp_version(m_low, low)
            if cmp > 0:
                low, low_inc = m_low, m_low_inc
            elif cmp == 0:
                low_inc = low_inc and m_low_inc
    if m_high is not None:
        if high is None:
            high, high_inc = m_high, m_high_inc
        else:
            cmp = _cmp_version(m_high, high)
            if cmp < 0:
                high, high_inc = m_high, m_high_inc
            elif cmp == 0:
                high_inc = high_inc and m_high_inc
    if low is None or high is None:
        return False
    cmp = _cmp_version(low, high)
    if cmp > 0:
        return True
    if cmp == 0:
        return not (low_inc and high_inc) or low in excluded or low in m_excluded
    return False


def _clause_holds(op: str, version: tuple[tuple[int, str], ...], bound) -> bool:
    cmp_result = _cmp_version(version, bound)
    if op == ">=":
        return cmp_result >= 0
    if op == ">":
        return cmp_result > 0
    if op == "<=":
        return cmp_result <= 0
    if op == "<":
        return cmp_result < 0
    return True


def _version_in_interval(
    version: tuple[tuple[int, str], ...],
    low,
    low_inc: bool,
    high,
    high_inc: bool,
) -> bool:
    if low is not None:
        c = _cmp_version(version, low)
        if c < 0 or (c == 0 and not low_inc):
            return False
    if high is not None:
        c = _cmp_version(version, high)
        if c > 0 or (c == 0 and not high_inc):
            return False
    return True


_VERSION_SUFFIX_ORDER: dict[str, int] = load_dict("markers.json", "version_suffix_order")


def _component_key(component: tuple[int, str]) -> tuple[int, int, int]:
    number, suffix = component
    match = re.match(r"^(dev|a|b|rc|post)([0-9]*)$", suffix or "")
    if match:
        return (number, _VERSION_SUFFIX_ORDER.get(match.group(1), 5), int(match.group(2) or 0))
    return (number, 5, 0)


def _cmp_version(a: tuple[tuple[int, str], ...], b: tuple[tuple[int, str], ...]) -> int:
    """Compare two normalized version tuples: -1 / 0 / 1."""
    width = max(len(a), len(b))
    for i in range(width):
        ca = a[i] if i < len(a) else (0, "")
        cb = b[i] if i < len(b) else (0, "")
        ka, kb = _component_key(ca), _component_key(cb)
        if ka < kb:
            return -1
        if ka > kb:
            return 1
    return 0
