"""Per-anchor context assembly.

For DEPENDENCY the used marker subset is ``version, platform, polarity,
restriction, time, arch``. Version, polarity and restriction are anchored: a
version token is owned by its nearest anchor, a negator negates the anchor only
in an explicit negative construction, and an exclusion word qualifies the anchor
by token proximity. Platform/time/arch are window-wide.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from docassay.core.models import Context
from docassay.core.windows import anchor_line_text
from docassay.data import load_list
from docassay.markers.version import combine_version, version_candidates
from docassay.vocabularies.dependency import is_plausible_version, normalize_dependency_name
from docassay.vocabularies.markers import (
    arch_regex,
    platform_regex,
    polarity_regex,
    restriction_regex,
    time_regex,
)

_RESTRICTION_TOKEN_RADIUS = 4
# A version candidate belongs to an anchor only within this many tokens of it.
# Character distance let ports, counts and argument values near a mention slip
# in ("docker run -p 8080:8080", "python train.py --learning-rate 0.2").
_VERSION_TOKEN_RADIUS = 2
_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Negation applies to the anchor only when it sits in an explicit negative
# construction: ``<neg> <exist-verb> X`` or ``X is <neg> <exist-verb>``. A "not"
# that modifies another predicate ("coverage is not a limitation", "should not
# decrease coverage") is not a negation of the dependency's existence.
# (data/markers.json)
EXIST_VERBS: frozenset[str] = load_list("markers.json", "exist_verbs")
_COPULA: frozenset[str] = load_list("markers.json", "copula")

# Articles/adjectives that may stand between the existence verb and the anchor
# ("We do not provide **a** Dockerfile", "ships **an official** image"). A
# noun/verb between them breaks the construction.
_ATTRIBUTIVE: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "the",
        "any",
        "some",
        "another",
        "own",
        "official",
        "separate",
        "custom",
        "default",
        "extra",
        "special",
        "dedicated",
        "built-in",
        "generated",
        "bundled",
    }
)

# Do-support copulas ("does", "do", "did") in "X does not V Y" make X the
# subject of the verb, not the negated object: "Flask does not include a
# database layer" says nothing against Flask's existence.
_DO_COPULA: frozenset[str] = frozenset({"do", "does", "did"})

# A version that is *not adjacent* to its anchor (two tokens apart:
# ``<anchor> <word> <version>``) is a command-line-output argument, not a
# dependency version, when the version is ``v``-prefixed ("celery multi
# v4.0.0") or annotated by a single-word parenthetical ("celery multi 4.0.0
# (latentcall)"). Both are verbose-command output shapes. An adjacent version
# ("Django 5.0 (LTS)", "Python v3.10") keeps the anchor.
_PAREN_WORD_RE = re.compile(r"\([a-z0-9_-]+\)")
_GAP_RE = re.compile(r"[\s,;]+")
_ENUM_CONJUNCTIONS: frozenset[str] = load_list("markers.json", "enum_conjunctions")
_VERSION_SPAN_RE = re.compile(r"(?:>=|<=|>|<|==|~=|\^|!=)?\s*v?[0-9]+(?:\.[0-9]+){0,3}")

# Contractions of the negator ("don't", "doesn't", ...) tokenize into two
# non-negator tokens ("don", "t") and are not in the negation pool, so a
# "We don't ship a Dockerfile" claim loses its polarity. They
# are folded to a same-length "not" (padding keeps every window offset valid)
# before tokenization and polarity matching.
_CONTRACTION_RE = re.compile(
    r"\b(?:don'?t|doesn'?t|didn'?t|isn'?t|aren'?t|wasn'?t|weren'?t|won'?t|"
    r"wouldn'?t|can'?t|cannot|couldn'?t|shouldn'?t|hasn'?t|haven'?t|ain'?t|"
    r"mustn'?t|needn'?t)\b",
    re.IGNORECASE,
)


def _fold_contractions(text: str) -> str:
    """Replace a negator contraction with same-length ``not`` (offsets stable)."""
    return _CONTRACTION_RE.sub(lambda m: "not" + " " * (len(m.group(0)) - 3), text)


def _candidate_end(low: str, position: int) -> int:
    """End offset of the version number starting at ``position``."""
    m = _VERSION_SPAN_RE.match(low[position:])
    return position + len(m.group(0)) if m else position


def _is_cli_arg(
    a_idx: int,
    candidate_idx: int,
    low: str,
    version_start: int,
    version_end: int,
    tokens: list[tuple[int, int]],
) -> bool:
    """Whether the candidate is a command-line argument of the anchor.

    ``"celery multi v4.0.0"`` / ``"celery multi 4.0.0 (latentcall)"``: the
    anchor is followed by a word and then the version. The version is treated
    as a CLI-output argument when it is ``v``-prefixed or followed by a
    single-word parenthetical annotation; an adjacent version keeps the anchor.
    A hyphenated dependency name ("dbt-core", "grpcio-status") tokenizes into
    two tokens, so the "word" between them is part of the name, not a CLI word.
    """
    if candidate_idx != a_idx + 2:
        return False
    intermed = tokens[a_idx + 1]
    if low[intermed[0] - 1 : intermed[0]] == "-":
        return False
    if low[version_start : version_start + 1].lower() == "v":
        return True
    return bool(_PAREN_WORD_RE.match(low[version_end:].lstrip()))


def _version_chains(low: str, candidates: list[tuple[str, str, int, int]]) -> list[list[int]]:
    """Index chains of version candidates separated only by ``,``/conjunctions.

    ``"3.9, 3.10 or 3.11"`` groups into one chain; ``"3.9, then upgrade to
    3.10"`` stays split. A distant version (gap > 20 chars) never chains.
    """
    chains: list[list[int]] = []
    current: list[int] = []
    for ci, (_op, _num, start, _end) in enumerate(candidates):
        if current:
            prev_end = candidates[current[-1]][3]
            if not _same_enumeration(low, prev_end, start):
                chains.append(current)
                current = []
        current.append(ci)
    if current:
        chains.append(current)
    return chains


def _same_enumeration(low: str, prev_end: int, cur_start: int) -> bool:
    """Whether the gap between two versions is only separators and conjunctions."""
    gap = low[prev_end:cur_start]
    if len(gap) > 20:
        return False
    words = [w for w in _GAP_RE.split(gap) if w]
    if not words:
        return True
    return all(w.lower() in _ENUM_CONJUNCTIONS for w in words)


def _anchor_polarity_restriction(
    low: str, anchors: list[tuple[int, int, str]]
) -> tuple[dict[int, frozenset[str]], dict[int, frozenset[str]]]:
    """Polarity and restriction words belonging to each anchor.

    A negator (``not``/``no``/``never``/``without``/…) negates the anchor only in
    an explicit negative construction around it:

    - ``<neg> [exist-verb]+ X`` — negator before the anchor, with only
      existence verbs between ("does not use redis");
    - ``X is <neg> <exist-verb>`` — negator after a copula ("redis is not used").

    A "not" that modifies another predicate ("coverage is not a limitation",
    "should not decrease coverage", "without a Docker daemon") does not negate
    the dependency. Exclusion words (``only``/``except``/…) are attached by plain
    token proximity — they qualify the referent but never negate it (§5).
    """
    tokens = [(m.start(), m.end()) for m in _TOKEN_RE.finditer(low)]
    token_text = [low[s:e] for s, e in tokens]
    polarity_matches = list(polarity_regex().finditer(low))
    restriction_matches = list(restriction_regex().finditer(low))

    def token_index(position: int) -> int | None:
        for idx, (start, end) in enumerate(tokens):
            if start <= position < end:
                return idx
        return None

    polarities: dict[int, frozenset[str]] = {}
    restrictions: dict[int, frozenset[str]] = {}
    for start, _end, _name in anchors:
        a_idx = None
        for idx, (ts, te) in enumerate(tokens):
            if ts <= start < te:
                a_idx = idx
                break
        if a_idx is None:
            continue
        negation: set[str] = set()
        for m in polarity_matches:
            s_idx = token_index(m.start())
            if s_idx is None:
                continue
            if _negates(s_idx, a_idx, token_text):
                negation.add(m.group(0).lower())
        exclusion: set[str] = set()
        for m in restriction_matches:
            s_idx = token_index(m.start())
            if s_idx is None:
                continue
            if abs(s_idx - a_idx) <= _RESTRICTION_TOKEN_RADIUS:
                exclusion.add(m.group(0).lower())
        polarities[start] = frozenset(negation)
        restrictions[start] = frozenset(exclusion)
    return polarities, restrictions


def _negates(neg_idx: int, a_idx: int, tokens: list[str]) -> bool:
    """Whether the negator at ``neg_idx`` negates the anchor at ``a_idx``."""
    if neg_idx < a_idx:
        between = tokens[neg_idx + 1 : a_idx]
        if len(between) > 3:
            return False
        if not between:
            # "no X" / "without X". If X is attributive ("no pytest fixtures")
            # the negator targets the noun after it, not the dependency.
            following = tokens[a_idx + 1 : a_idx + 2]
            if following and following[0] not in _COPULA and following[0] not in EXIST_VERBS:
                return False
            return True
        # "<neg> <exist-verb> ... X": the first token must be an existence verb,
        # and any tokens up to the anchor may be articles/adjectives
        # ("do not provide a Dockerfile").
        if between[0] not in EXIST_VERBS:
            return False
        return all(w in EXIST_VERBS or w in _ATTRIBUTIVE for w in between)
    between = tokens[a_idx + 1 : neg_idx]
    if len(between) > 2 or not between:
        return False
    if not all(w in _COPULA for w in between):
        return False
    after = tokens[neg_idx + 1 : neg_idx + 2]
    if not after or after[0] not in EXIST_VERBS:
        return False
    # "X does not V Y": the do-support active construction makes X the subject
    # of V ("Flask does not include a database layer"), not the negated object.
    # The passive "X is not used" (is/are/was/were/be/been) negates X.
    if any(w in _DO_COPULA for w in between):
        return False
    return True


def extract_contexts(
    window: str,
    anchors: list[tuple[int, int, str]],
    *,
    normalize: Callable[[str], str] = normalize_dependency_name,
    is_plausible: Callable[[str, str], bool] = is_plausible_version,
    line_map=None,
) -> dict[int, Context]:
    """Context per anchor (keyed by anchor start) for one window.

    ``normalize``/``is_plausible`` come from the predicate's vocabulary: a
    version number is owned by an anchor only when it is plausible for that
    referent. The DEPENDENCY defaults canonicalize package names and check
    major-version ranges; other predicates pass their own or ``is_plausible``
    that always rejects (no version claims).

    ``line_map`` is the merged-window offset→line map. Negation
    and version are extracted over the whole (merged) window — a "does not\\n
    require NumPy" split across a line break stays one sentence. But the
    window-wide markers (platform / time / arch) that feed the historical and
    test-env gates are taken from the anchor's OWN line: foreign words from a
    neighbouring line ("older", "tested on") must not turn a live claim into a
    historical/test-env mention.
    """
    low = _fold_contractions(window.lower())

    polarities, restrictions = _anchor_polarity_restriction(low, anchors)

    def markers_for(start: int) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
        mwin = anchor_line_text(window, line_map, start) if line_map is not None else window
        return (
            frozenset(m.group(0).lower() for m in platform_regex().finditer(mwin)),
            frozenset(m.group(0).lower() for m in time_regex().finditer(mwin)),
            frozenset(m.group(0).lower() for m in arch_regex().finditer(mwin)),
        )

    owned: dict[int, list[tuple[str, str]]] = {}
    tokens = [(m.start(), m.end()) for m in _TOKEN_RE.finditer(low)]

    def token_index(position: int) -> int | None:
        best_idx: int | None = None
        best_dist = 2**31
        for idx, (ts, te) in enumerate(tokens):
            if ts <= position < te:
                return idx
            dist = min(abs(position - ts), abs(position - te))
            if dist < best_dist:
                best_idx = idx
                best_dist = dist
        return best_idx

    anchor_idx = {start: token_index(start) for start, _end, _name in anchors}
    candidates = [
        (op, num, position, _candidate_end(low, position))
        for op, num, position in version_candidates(low)
    ]

    # Base pass: assign each candidate to the nearest anchor within the token
    # radius. Version candidates that follow a CLI command word of their anchor
    # ("celery multi v4.0.0 (latentcall)") are argument values, not versions.
    assigned: dict[int, tuple[int, int]] = {}
    for ci, (_op, num, position, cand_end) in enumerate(candidates):
        candidate_idx = token_index(position)
        if candidate_idx is None:
            continue
        best_start: int | None = None
        best_dist = _VERSION_TOKEN_RADIUS + 1
        for start, _end, name in anchors:
            # Extras syntax `pkg[extra]`: the version belongs to pkg, not the
            # extra ("apache-airflow[celery]==3.1.0" is airflow's version).
            if start > 0 and low[start - 1] == "[":
                continue
            if not is_plausible(normalize(name), num):
                continue
            a_idx = anchor_idx.get(start)
            if a_idx is None:
                continue
            if _is_cli_arg(a_idx, candidate_idx, low, position, cand_end, tokens):
                continue
            dist = abs(candidate_idx - a_idx)
            if dist < best_dist:
                best_start = start
                best_dist = dist
        if best_start is not None:
            assigned[ci] = (best_start, best_dist)

    # Disjunctive list extension: "Python 3.9, 3.10 or 3.11" — a version that is
    # part of the same enumeration as an assigned one belongs to the same anchor.
    for chain in _version_chains(low, candidates):
        assigned_members = [ci for ci in chain if ci in assigned]
        if not assigned_members:
            continue
        unassigned = [ci for ci in chain if ci not in assigned]
        if not unassigned:
            continue
        for ci in unassigned:
            anchor_start = min(
                assigned_members,
                key=lambda m: abs(candidates[m][2] - candidates[ci][2]),
            )
            owner = assigned[anchor_start][0]
            name = next(n for s, _e, n in anchors if s == owner)
            op, num, _pos, _end = candidates[ci]
            if not is_plausible(normalize(name), num):
                continue
            assigned[ci] = (owner, _VERSION_TOKEN_RADIUS + 1)

    for ci, (start, _dist) in assigned.items():
        op, num, _pos, _end = candidates[ci]
        owned.setdefault(start, []).append((op, num))

    contexts: dict[int, Context] = {}
    for start, _end, _name in anchors:
        version = combine_version(owned.get(start, []))
        platform, time_vals, arch = markers_for(start)
        contexts[start] = Context(
            version=version,
            platform=platform,
            polarity=polarities.get(start, frozenset()),
            restriction=restrictions.get(start, frozenset()),
            time=time_vals,
            arch=arch,
        )
    return contexts
