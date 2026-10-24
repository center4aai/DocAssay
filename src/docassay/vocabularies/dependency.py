"""The DEPENDENCY controlled vocabulary.

A pure allowlist: only names in the anchor set can anchor a claim, and a name
outside it is not a claim (§3 — the dictionary is the controlled instrument).
Synonyms fix canonicalization for grouping and matching (§7.1 name
normalization): a ``surface -> canonical`` map that folds every spelling of a
dependency (``pytorch``/``torch``, ``sklearn``/``scikit-learn``,
``k8s``/``kubernetes``, ``scikit_learn``/``scikit-learn``) into one referent.
The allowlist, synonyms and per-package version ranges live in
``data/dependency.json``.

The allowlist is derived from a dated PyPI distribution ranking plus a small
documented toolchain/alias layer and
is Python-specific: non-Python topics are not anchored. At runtime the project's
own manifest declarations extend the anchor set, so a dependency the tool
harvests is always anchorable (see ``Predicate.scan`` extra-names wiring in the
pipeline).
"""

from __future__ import annotations

import functools
import re

from docassay.data import load_dict, load_list

# Canonical distribution name for each non-canonical surface form. A surface is
# *also* in the anchor set so it anchors claims, but normalizes to the canonical
# name for grouping/matching.
DEPENDENCY_SYNONYMS: dict[str, str] = load_dict("dependency.json", "synonyms")

# The fixed, external anchor allowlist (PyPI top-N + toolchain + alias surfaces).
DEPENDENCY_NAMES: frozenset[str] = load_list("dependency.json", "names")

_NAMES_LOWER: frozenset[str] = frozenset(n.lower() for n in DEPENDENCY_NAMES)


class DependencyAllowlist:
    """The anchor set: the fixed allowlist plus the project's declared deps.

    A project's manifest declarations extend the anchor set at runtime so the
    tool always sees a dependency it harvests — the DEPENDENCY world is closed
    over the project's own manifests. The fixed allowlist and the extra names
    are matched by the same fast whole-run lookup. Instances are immutable and
    cheap to rebuild; the pipeline memoizes one per distinct extra set.
    """

    __slots__ = ("_extra_lower", "lower", "names", "plus_re")

    def __init__(self, extra_names: frozenset[str] = frozenset()):
        variants: set[str] = set()
        for name in extra_names:
            low = name.lower()
            variants.add(low)
            variants.add(low.replace("-", "_"))
        self._extra_lower: frozenset[str] = frozenset(variants)
        self.names: frozenset[str] = DEPENDENCY_NAMES | frozenset(extra_names)
        # The scan patterns belong to the instance, so concurrent analyses with
        # different declared names never share mutable state.
        self.plus_re: re.Pattern[str] | None = _compile_plus(self.names)
        self.lower: frozenset[str] = frozenset(n.lower() for n in self.names) | self._extra_lower

    def __contains__(self, token: str) -> bool:
        return token in _NAMES_LOWER or token in self._extra_lower


# Fast anchor pass: a name occurrence is precisely a maximal ``[A-Za-z0-9_-]+``
# run that equals an anchored name (case-insensitively). Names carrying
# characters outside the run class (``clang++``, a dotted token) are matched by
# a small separate pattern; when one matches it suppresses a same-position
# prefix run, mirroring the alternation's longest-first order.
_RUNS_RE = re.compile(r"[A-Za-z0-9_-]+")


def _plus_names(allowlist: frozenset[str]) -> tuple[str, ...]:
    return tuple(sorted((n for n in allowlist if not _RUNS_RE.fullmatch(n)), key=len, reverse=True))


def _compile_plus(allowlist: frozenset[str]) -> re.Pattern[str] | None:
    plus = _plus_names(allowlist)
    if not plus:
        return None
    return re.compile(
        r"(?<![a-z0-9_-])(?:" + "|".join(re.escape(n) for n in plus) + r")(?![a-z0-9_-])",
        re.IGNORECASE,
    )


@functools.lru_cache(maxsize=16)
def allowlist_for(extra_names: frozenset[str] = frozenset()) -> DependencyAllowlist:
    """The (immutable, memoized) allowlist for one set of declared names."""
    return DependencyAllowlist(extra_names)


def dependency_anchors(
    window: str, allowlist: DependencyAllowlist | None = None
) -> list[tuple[int, int, str]]:
    """Every dependency-name occurrence in ``window`` as ``(start, end, token)``.

    Uses the given allowlist (fixed plus declared extras) or the fixed allowlist
    when none is passed. Yields the same anchors as the equivalent alternation
    (same positions, same matched text, same order) while scanning each
    character once.
    """
    allowlist = allowlist or _FIXED
    plus_re, lower = allowlist.plus_re, allowlist.lower
    anchors: list[tuple[int, int, str]] = [
        (m.start(), m.end(), m.group(0))
        for m in _RUNS_RE.finditer(window)
        if m.group(0).lower() in lower
    ]
    if plus_re is not None:
        for m in plus_re.finditer(window):
            s, e, g = m.start(), m.end(), m.group(0)
            anchors = [
                a
                for a in anchors
                if not (a[0] == s and g.lower().startswith(a[2].lower()) and len(g) > len(a[2]))
            ]
            anchors.append((s, e, g))
    anchors.sort()
    return anchors


_FIXED = DependencyAllowlist()


# Plausible version range per canonical dependency, `[lo, hi)` on the major
# version, with margin ("Python" will never plausibly be 2507, "docker" never
# 8080). A number outside the range is not a version — it is a year, port,
# count, permission or argument value. Default (0, 100) still rejects
# years/ports. (data/dependency.json)
DEPENDENCY_VERSION_RANGES: dict[str, tuple[float, float]] = {
    name: (lo, hi) for name, (lo, hi) in load_dict("dependency.json", "version_ranges").items()
}


def is_plausible_version(name: str, version_number: str) -> bool:
    """Whether ``version_number`` is a plausible version for the dependency.

    Plausibility is checked on the major component against the declared range
    ``[lo, hi)`` (decided 2026-08-27). A year, port, count or permission value
    near the name is not a version and must not drive a verdict.
    """
    lo, hi = DEPENDENCY_VERSION_RANGES.get(name, (0.0, 100.0))
    parts = [p for p in re.split(r"[^0-9]+", version_number) if p]
    if not parts:
        return False
    try:
        major = int(parts[0])
    except ValueError:
        return False
    return lo <= major < hi


def normalize_dependency_name(name: str) -> str:
    """Canonicalize a dependency mention (§7.1).

    Lowercase, fold ``_`` and ``.`` to ``-``, then map known synonyms. Applied
    to both doc mentions and manifest names so grouping and matching compare
    canonical forms.
    """
    folded = name.strip().lower().replace("_", "-").replace(".", "-")
    return DEPENDENCY_SYNONYMS.get(folded, folded)
