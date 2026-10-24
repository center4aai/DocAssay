"""Integrity invariants of the controlled vocabularies (data/*.json).

These tests freeze the *shape* of the vocabularies so a manual edit that
breaks an invariant (duplicate, unsorted, a synonym pointing nowhere, a version
range for an unknown name) fails loudly. The compositions themselves are
frozen under ``src/docassay/tests/data/vocabulary_manifest.json``; this
module only guards the invariants, not the exact word list.
"""

from __future__ import annotations

import re

from docassay.data import load, load_dict, load_list
from docassay.vocabularies.dependency import normalize_dependency_name

_REGEX_META = re.compile(r"[\\*()\[\]]")


def _all_word_lists() -> list[tuple[str, str, frozenset[str]]]:
    """Every (file, key, value) whose value is a word pool (list of strings)."""
    out: list[tuple[str, str, frozenset[str]]] = []
    for fname in ("dependency.json", "markers.json", "structure.json", "pipeline.json"):
        data = load(fname)
        for key, value in data.items():
            if isinstance(value, list) and value and all(isinstance(v, str) for v in value):
                out.append((fname, key, frozenset(value)))
    return out


def test_no_duplicates_in_any_word_list() -> None:
    for fname, key, _pool in _all_word_lists():
        items = list(load(fname).get(key, []))
        assert len(items) == len(set(items)), f"{fname}.{key} has duplicates"


def test_word_lists_are_sorted() -> None:
    for fname, key, _pool in _all_word_lists():
        items = [str(v) for v in load(fname).get(key, [])]
        # Regex phrase tables (e.g. ``historical_phrases``) carry their own
        # metacharacters; their order is irrelevant (``regex_alternation`` sorts
        # longest-first at compile time). Only plain word lists must be sorted.
        if any(_REGEX_META.search(w) for w in items):
            continue
        assert items == sorted(items), f"{fname}.{key} is not sorted"


def test_no_whitespace_or_capitalization_in_word_lists() -> None:
    # ``pipeline.manifest_names`` are filenames whose capitalization is
    # significant (``Pipfile``, ``requirements.txt``); skip the case check.
    for fname, key, pool in _all_word_lists():
        if (fname, key) == ("pipeline.json", "manifest_names"):
            continue
        for word in pool:
            assert word == word.strip(), f"{fname}.{key} has padding in {word!r}"
            assert word == word.lower(), f"{fname}.{key} has uppercase {word!r}"


def test_synonyms_normalize_to_reachable_targets() -> None:
    names = set(load_list("dependency.json", "names"))
    canonical_names = {n.lower().replace("_", "-") for n in names}
    synonyms = load_dict("dependency.json", "synonyms")
    for alias, target in synonyms.items():
        # Every alias must be anchorable: its canonical form is in names.
        assert alias.lower().replace("_", "-") in canonical_names, f"alias {alias!r} not in names"
        # Every target is the canonical form the alias normalizes to.
        assert normalize_dependency_name(alias) == target, (
            f"{alias!r} normalizes to {normalize_dependency_name(alias)!r}, not {target!r}"
        )


def test_version_ranges_keys_are_canonical_names() -> None:
    names = {n.lower().replace("_", "-") for n in load_list("dependency.json", "names")}
    ranges = load_dict("dependency.json", "version_ranges")
    for name in ranges:
        assert name in names, f"version range for unknown name {name!r}"


def test_version_ranges_are_valid_intervals() -> None:
    ranges = load_dict("dependency.json", "version_ranges")
    for name, (lo, hi) in ranges.items():
        assert lo >= 0, f"{name}: negative lower bound {lo}"
        assert lo < hi, f"{name}: interval {lo}..{hi} is empty"
        # Datestamp-major packages (certifi 2026.x, pytz 2026.x) legitimately
        # have a large upper bound; only a non-numeric/inverted range is wrong.
        assert isinstance(lo, (int, float)) and isinstance(hi, (int, float))


def test_python_builtins_are_lowercase_and_sorted() -> None:
    builtins = load_list("structure.json", "python_builtins")
    assert builtins == frozenset(sorted(builtins))
    assert all(b == b.lower() for b in builtins)


def test_host_tlds_are_lowercase_without_dots() -> None:
    tlds = load_list("structure.json", "host_tlds")
    assert all(t == t.lower() and "." not in t and t.isalnum() for t in tlds)


def test_host_tlds_match_iana_snapshot() -> None:
    """Golden spec §6.7 / freeze-guard: ``host_tlds`` is exactly the committed
    IANA root-zone snapshot (alnum TLDs, lowercase; IDN ``xn--`` excluded)."""
    from pathlib import Path

    snapshot = Path(__file__).resolve().parent / "data" / "iana_tlds_2026-09-06.txt"
    lines = [
        line.strip().lower()
        for line in snapshot.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    expected = frozenset(sorted(t for t in lines if t.isalnum()))
    assert load_list("structure.json", "host_tlds") == expected
    assert len(expected) > 1000  # full root zone, not a hand-picked subset


def test_dependency_names_have_anchorable_characters() -> None:
    names = load_list("dependency.json", "names")
    for name in names:
        assert any(c.isalpha() for c in name)
        assert all(c.isalnum() or c in "+_.-" for c in name), f"bad char in {name!r}"


def test_manifest_counts_match_provenance() -> None:
    """Counts recorded in vocabulary_manifest.json match the data files."""
    import json
    from pathlib import Path

    manifest = json.loads(
        (Path(__file__).resolve().parent / "data" / "vocabulary_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    for fname, tables in manifest.items():
        if fname in ("generated", "note", "frozen_sha256_prefix", "code_pools"):
            continue
        data = load(f"{fname}.json")
        for table, meta in tables.items():
            actual = len(data.get(table, []))
            assert actual == meta["count"], (
                f"{fname}.{table}: manifest says {meta['count']}, data has {actual}"
            )


def _manifest() -> dict:
    import json
    from pathlib import Path

    return json.loads(
        (Path(__file__).resolve().parent / "data" / "vocabulary_manifest.json").read_text(
            encoding="utf-8"
        )
    )


def test_frozen_hashes_match_data() -> None:
    """``frozen_sha256_prefix`` freezes every data file; a drift fails loudly.

    The hashes were stale before 2026-09-14 (dependency/markers changed in
    Phases 1/4 without a refresh); the guard is now enforced.
    """
    import hashlib
    from pathlib import Path

    data_dir = Path(__file__).resolve().parents[1] / "data"
    for fname, prefix in _manifest()["frozen_sha256_prefix"].items():
        actual = hashlib.sha256((data_dir / fname).read_bytes()).hexdigest()[:16]
        assert actual == prefix, f"{fname}: frozen {prefix}, actual {actual}"


def test_code_pools_have_provenance() -> None:
    """Every verdict-shaping code pool carries file/source/rule/status."""
    pools = _manifest()["code_pools"]
    for name, meta in pools.items():
        if name == "note":
            continue
        for field in ("file", "source", "rule", "status"):
            assert meta.get(field), f"code_pool {name} missing {field}"
        assert meta["status"] in {"external", "calibration"}, name


# --- Golden-spec cross-table invariants ------------------------------------


def test_version_suffix_order_keys_match_pep440() -> None:
    order = load_dict("markers.json", "version_suffix_order")
    # Keys must match the hard-coded regex in markers/version.py and PEP 440.
    assert set(order) == {"dev", "a", "b", "rc", "", "post"}
    assert list(order) == ["dev", "a", "b", "rc", "", "post"]


def test_eq_prefix_only_is_shared_with_exclusion() -> None:
    eq = set(load_list("markers.json", "eq_prefixes"))
    excl = set(load_list("markers.json", "exclusion_words"))
    assert eq & excl == {"only"}


def test_historical_time_is_subset_of_past_time() -> None:
    pt = set(load_list("dependency.json", "past_time"))
    ht = set(load_list("markers.json", "historical_time"))
    assert ht <= pt, sorted(ht - pt)


def test_time_words_cover_downgrade_pools() -> None:
    """Golden spec §6.1-6.2: downgrade pools must be reachable via ``time_words``.

    ``context.time`` is filled from the ``time_words`` regex, so every member of
    ``past_time``/``historical_time`` must also be in ``time_words`` or the
    downgrade flag silently never fires. ``until`` was adopted 2026-09-06
    (minimal-change gate, decision-record); the invariant is now strict.
    """
    tw = set(load_list("markers.json", "time_words"))
    pt = set(load_list("dependency.json", "past_time"))
    ht = set(load_list("markers.json", "historical_time"))
    assert (pt | ht) <= tw, sorted((pt | ht) - tw)


# Golden spec §2.5: the closed change-of-state participle class (WordNet/VerbNet)
# behind ``historical_verb_forms`` — the same class documented for the T2
# ``historical_phrases`` harvest (§1.5). Freeze-guard: if the data pool drifts
# from the regenerator's class, the flag surface changes without a decision.
_CHANGE_STATE_PARTICIPLES = (
    "split off",
    "exposed",
    "moved",
    "renamed",
    "merged",
    "relocated",
    "extracted",
    "deleted",
    "dropped",
)


def test_historical_verb_forms_match_past_copula_class() -> None:
    """Golden spec §2.6: ``historical_verb_forms`` is exactly the past copula
    (``was``/``were``) × the change-of-state participle class."""
    forms = set(load_list("markers.json", "historical_verb_forms"))
    expected = {f"{c} {p}" for c in ("was", "were") for p in _CHANGE_STATE_PARTICIPLES}
    assert forms == expected, sorted(expected - forms) + sorted(forms - expected)


def test_unambiguous_ci_syncs_with_multiword_ci_names() -> None:
    """Golden spec §6.5: ``_UNAMBIGUOUS_CI`` in ``predicates/infra.py`` is the
    multi-word subset of ``ci_names`` (only multi-word products anchor alone;
    single-word names need a CI-context word). A drift would silently gate (or
    un-gate) a product. ``travis ci`` was missing until 2026-09-07 (WS7) —
    the sync is now an enforced invariant."""
    import docassay.predicates.infra as infra

    multi = {n for n in load_list("project.json", "ci_names") if " " in n}
    assert multi == set(infra._UNAMBIGUOUS_CI), (
        f"_UNAMBIGUOUS_CI drift: data multi-word {sorted(multi)}, "
        f"code has {sorted(infra._UNAMBIGUOUS_CI)}"
    )
