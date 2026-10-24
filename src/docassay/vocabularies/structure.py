"""The structure-predicate vocabulary.

Path-shaped anchors are not a closed allowlist like DEPENDENCY: any backtick
token that looks like a file or directory path can anchor a claim, and the
CLOSED world turns a missing path into a finding. This module only carries the
shared *shape* helpers — the anchor regexes themselves live in each predicate
module.
"""

from __future__ import annotations

import posixpath
import re
from collections import OrderedDict

from docassay.data import load_list, regex_alternation

# File extensions that make a backtick token a plausible PATH_EXISTS anchor,
# and common extensionless file names docs reference by name. Both live in
# ``data/structure.json``.
FILE_EXTENSIONS: frozenset[str] = load_list("structure.json", "file_extensions")
BARE_FILE_NAMES: frozenset[str] = load_list("structure.json", "bare_file_names")


def normalize_path(path: str) -> str:
    """Canonicalize a path mention for grouping and matching (§7.1).

    Lowercase, strip a leading ``./``, collapse double slashes, and keep a
    trailing ``/`` for directory mentions so file and directory referents do
    not collide.
    """
    p = path.strip().replace("\\", "/").lower()
    while p.startswith("./"):
        p = p[2:]
    p = p.replace("//", "/")
    return p


# Sphinx cross-reference roles. A backtick token inside ``:ref:`x```,
# ``:func:`x```, ``:doc:`x```, ... is an API/doc cross-reference, not a file
# reference.
# External-package roles (``:pypi:`, ``:pip:`) point at PyPI, not the project.
_SPHINX_ROLE_RE = re.compile(
    r":(?:abbr|attr|class|classmethod|citation|code|data|dfn|doc|envvar|exc|"
    r"func|keyword|meth|mod|obj|property|ref|staticmethod|term|user|"
    r"pypi|pip|issue|pr|commit|gh|"
    r"py:attr|py:class|py:func|py:meth|py:mod):\s*[`]*$",
    re.IGNORECASE,
)


def is_sphinx_role_anchor(window: str, start: int) -> bool:
    """Whether the anchor at ``start`` sits inside a Sphinx cross-reference."""
    return bool(_SPHINX_ROLE_RE.search(window[:start]))


# Build/deploy output directories, deploy artifact files and git/CI reference
# tokens (data/structure.json): generated output and repository-navigation
# tokens are not CLOSED-world findings against the source tree.
_BUILD_ARTIFACT_DIRS: frozenset[str] = load_list("structure.json", "build_artifact_dirs")
_DEPLOY_ARTIFACT_FILES: frozenset[str] = load_list("structure.json", "deploy_artifact_files")
_GIT_REF_LEADING: frozenset[str] = load_list("structure.json", "git_ref_leading")

# An external host ("jakewheat.github.io/sql-overview") — a link target, not a
# project path. Requires a dot-domain TLD in the part before the first slash.
# The TLD is the full IANA root zone (data/structure.json ``host_tlds``), so
# dotted *code* identifiers (``numpy.random``, ``requests.py``) are never
# mistaken for domains — ``random``/``py`` are not TLDs.
_EXTERNAL_HOST_RE = re.compile(
    r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+\.(?:"
    + regex_alternation(load_list("structure.json", "host_tlds"))
    + r")$",
    re.IGNORECASE,
)

# A DOI (``10.1001/jama.295.3.306``) — a citation, not a project path.
_DOI_RE = re.compile(r"^10\.\d{4,}/")

# A purely numeric leading path segment (``2023/``, ``1/b.``) with no file
# extension is a year, fraction, argument or count, not a file reference.
_NUMERIC_SEGMENT_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")


def _has_file_extension(token: str) -> bool:
    return token.lower().endswith(tuple(sorted(FILE_EXTENSIONS, key=len, reverse=True)))


def is_extensionless_slash_path(path: str) -> bool:
    """Whether a slash-carrying *file* mention has no reliable file suffix.

    An extensionless slash token (``gzip/bz2``, ``apache/airflow``,
    ``try/except``) is often an enumeration of variants or an identifier, not a
    project file — the CLOSED world cannot safely refute it. Trailing-slash
    directories stay reliable anchors, as do tokens whose final segment ends in
    a known extension or is a known bare-file name (``dbt/dockerfile``).
    """
    if path.endswith("/"):
        return False  # a trailing-slash token is a directory mention
    stripped = path.rstrip("/")
    if "/" not in stripped:
        return False
    last = stripped.rsplit("/", 1)[-1].lower()
    return not _has_file_extension(last) and last not in BARE_FILE_NAMES


# Placeholder segments in documentation paths ("version-x.x.x/",
# "docs/<version>/", "install/${VERSION}/"): a concrete directory cannot be
# resolved, so the CLOSED world must abstain instead of refuting. Version
# placeholders are the dotted-x shapes (``x.x.x`` / ``X.X.X``); the others are
# explicit templating braces.
_PLACEHOLDER_RE = re.compile(r"(?:\bx\.x\.x\b|[<{]\$?[A-Za-z0-9_.-]+[}>])", re.IGNORECASE)


def is_placeholder_path(path: str) -> bool:
    """Whether a path mention contains an explicit placeholder segment.

    Template placeholders ("version-x.x.x/", "docs/<version>/",
    "install/${VERSION}/") are not concrete repository paths, so their absence
    from the listing must not be a CLOSED-world finding (conservative
    abstention). Works on the normalized object key, directories
    included (trailing slash is irrelevant to the segment scan).
    """
    return bool(_PLACEHOLDER_RE.search(path))


def _is_math_fraction(token: str) -> bool:
    """Whether a single-slash token is a math/fraction form (``1/x``, ``f_s/2``).

    A path with exactly one ``/`` whose segments are single characters or pure
    numbers (and no file extension) is a formula, not a repository path.
    """
    if token.count("/") != 1:
        return False
    if _has_file_extension(token):
        return False
    left, right = token.split("/")
    segments = (left, right)
    if any(_NUMERIC_SEGMENT_RE.fullmatch(seg) for seg in segments):
        return True
    return all(len(seg) <= 2 for seg in segments)


def is_rejectable_path(token: str) -> bool:
    """Whether a path-shaped token is not a claim about the project tree.

    Rejects ``/``-absolute and ``~`` paths (docs-site URLs, user-home
    examples), build/deploy output directories (``_build/``, ``docs/build/``,
    ``site/``), deploy artifact files (``versions.json``), external hosts
    (``jakewheat.github.io/sql-overview``), DOIs, math fractions (``1/x``),
    numeric-leading non-extension tokens and git/CI references (``origin/main``,
    ``refs/tags/v``, ``actions/cache``). A filename that merely ends in a
    build-dir word (``build.rs``, ``dist.py``) is not affected.
    """
    if token.startswith(("/", "~")):
        return True
    if "//" in token:
        return True  # integer division (``M//2``) or a URL — not a project path
    if token.startswith("../"):
        return True  # relative navigation escaping the tree root
    if token.strip("./") == "":
        return True  # ``.`` / ``./`` / ``..`` — navigation, not a file
    if token.lower() in _DEPLOY_ARTIFACT_FILES:
        return True
    host, sep, _rest = token.partition("/")
    if sep and _EXTERNAL_HOST_RE.match(host):
        return True
    if _DOI_RE.match(token):
        return True
    if _is_math_fraction(token):
        return True
    leading = token.split("/", 1)[0]
    if _NUMERIC_SEGMENT_RE.fullmatch(leading) and not _has_file_extension(token):
        return True
    if token.lower().split("/", 1)[0] in _GIT_REF_LEADING:
        return True
    segments = token.lower().split("/")
    return any(seg in _BUILD_ARTIFACT_DIRS for seg in segments)


# Runtime/instance configuration artifacts. A config-artifact mention (``.env``,
# ``*.cfg``, ``*.ini``, ``*.conf``, ``*_config.py``) that is *absent* from the
# tree is usually the application's runtime configuration (read by the daemon
# from the deployment environment), not a repo file. Two conditions keep this a
# conservative, project-agnostic rule: the object must be a config-shaped
# artifact, and the mention must sit in a configuring window ("set X in
# ``airflow.cfg``", "configure the ``values.yaml``"). A bare mention of a
# dev-tool config that normally lives in the repo (``pytest.ini``, ``tox.ini``)
# or a code path ending in ``config.py`` stays a claim. (data/structure.json)
USER_CONFIG_FILES: frozenset[str] = load_list("structure.json", "user_config_files")
_USER_CONFIG_SUFFIXES: tuple[str, ...] = tuple(
    sorted(load_list("structure.json", "user_config_suffixes"), key=len, reverse=True)
)

_CONFIG_FRAMING_RE = re.compile(
    r"\[\s*[a-z0-9_]+\s*\]|"  # INI section marker: ``[core]``, ``[sentry]``
    r"\b(?:configured?|configur(?:able|ation|ational)|config(?:s)?[_\s-]?file|"
    r"setting[s]?|set\b|section[s]?|option[s]?|parameter[s]?|default[s]?|"
    r"override[s]?|custom\b|change\b|registered?\s+(?:in|via|under)|"
    r"environment\s+variables?|env\s*var|verify|review|edit|populate|"
    r"seed(?:s|ed|ing)?|mount(?:s|ed|ing)?|cop(?:y|ied|ying)\b|"
    r"read[s]?\s+(?:from|in))\b",
    re.IGNORECASE,
)


def is_user_config_mention(object_name: str, raw_context: str) -> bool:
    """Whether an absent config-artifact mention is a runtime configuration."""
    base = object_name.rstrip("/").rsplit("/", 1)[-1].lower()
    if base in USER_CONFIG_FILES:
        return True
    if not base.endswith(_USER_CONFIG_SUFFIXES):
        return False
    return bool(_CONFIG_FRAMING_RE.search(raw_context))


# Reader-space cues: second-person addresses, tutorial captions, "will be
# saved/written/created", "Let's say", "Here's", "e.g." — the mention lives in
# the *reader's* project space (a tutorial's `app.py`, a config the user would
# write), not the analyzed repository. A would-be REFUTED path with such a cue
# is not a stale-repo-path finding (; measured on the reviewer's
# labels: removes 29 USR + 6 OUT + 3 HOLE false REFUTED, loses 0 TP/TPw).
# ``:caption:`` is a directive option; ``:file:`` is deliberately NOT a cue —
# it is a Sphinx cross-reference role that *marks a file path claim*
# (``:file:`requirements/default.txt```), so gating it by cue would hide real
# stale-path findings (measured: mutation recall on ``requirements/*.txt``).
# (data/markers.json has the generative/exemplary pools; this is a fixed
# syntactic class, kept inline like the report's proposal_effect.py CUE.)
_READER_SPACE_CUE_RE = re.compile(
    r"\b(?:your|you|you'll|you're|let's|here's|suppose|say you have|"
    r"for example|will be (?:saved|written|created|generated|stored)|e\.g)\b"
    r"|:caption:",
    re.IGNORECASE,
)


def is_reader_space_mention(raw_context: str) -> bool:
    """Whether a claim window addresses the reader or captions an example."""
    return bool(_READER_SPACE_CUE_RE.search(raw_context))


# Reader-project file names: tool configs, package-manager manifests and
# tutorial placeholders that live in the *reader's* project, not the analyzed
# repository (``.cz.toml``, ``pytest.toml``, ``Cargo.toml``, ``launch.json``,
# ``myproject``). A mention of such a bare name that is *absent* from the tree
# is not a stale-repo-path finding — the file is the reader's own. Slash-carrying
# paths (``py-polars/cargo.toml``) stay adjudicated: they claim a repo-relative
# location. (data/structure.json)
READER_FILE_NAMES: frozenset[str] = load_list("structure.json", "reader_file_names")


def is_reader_file_name(object_name: str) -> bool:
    """Whether a bare path mention names a reader-project file/config."""
    return "/" not in object_name.rstrip("/") and object_name.rstrip("/") in READER_FILE_NAMES


# Third-party software artifacts referenced by bare name (C headers of the
# CPython/C stdlib, web-server configs, external tool scripts). A bare mention
# that is absent from the tree is a reference to foreign software, not a
# stale-repo-path finding (data/structure.json).
EXTERNAL_SOFTWARE_FILES: frozenset[str] = load_list("structure.json", "external_software_files")


def is_external_software_name(object_name: str) -> bool:
    """Whether a bare path mention names a third-party software artifact."""
    return "/" not in object_name.rstrip("/") and object_name.rstrip("/") in EXTERNAL_SOFTWARE_FILES


# Build/runtime generated artifacts. A ``<name>module.c`` filename is
# f2py/swig wrapper output (``fib1module.c``, ``blahmodule.c``), generated from
# a signature file, not a hand-written source. The rule is a pattern, not a
# per-project allowlist: generated names are project-specific, so enumerating
# them would memorise the tuning corpus.
_GENERATED_MODULE_C_RE = re.compile(r"^[a-z0-9_]+module\.c$", re.IGNORECASE)


def is_generated_artifact_name(object_name: str) -> bool:
    """Whether a bare path mention names a generated artifact."""
    return bool(_GENERATED_MODULE_C_RE.match(object_name.rstrip("/").lower()))


# Runtime/tooling hidden directories (``.venv/``, ``.git/``, ``.tox/``): the
# gitignore-derived ``skipped_dirs`` pool plus the VCS dirs it may not carry.
# A doc mention of one is runtime state, not a stale repo path. Real tracked
# dot dirs (``.github``, ``.cargo``, ``.config``) are not in the pool and stay
# adjudicated.
SKIPPED_DIRS: frozenset[str] = load_list("structure.json", "skipped_dirs")
_EXTRA_TOOL_DOT_DIRS: frozenset[str] = frozenset({".bzr", ".hg"})


def is_hidden_tool_dir(object_name: str) -> bool:
    """Whether a path mention's head is a runtime/tooling hidden directory."""
    head = object_name.rstrip("/").split("/", 1)[0].lower()
    return head.startswith(".") and (head in SKIPPED_DIRS or head in _EXTRA_TOOL_DOT_DIRS)


# A window describing build/runtime *output* ("generated by f2py", "will
# generate", "the generated header") — the mention is a produced artifact, not a
# current-state source file.
_GENERATED_MENTION_RE = re.compile(
    r"\b(?:generated\s+by|the\s+generated|to\s+generate|will\s+generate)\b",
    re.IGNORECASE,
)


def is_generated_mention(raw_context: str) -> bool:
    """Whether a window describes a generated/runtime artifact."""
    return bool(_GENERATED_MENTION_RE.search(raw_context))


# A dot-prefixed fragment token ("``.feature.rst``", "``.breaking.rst``") is a
# filename *pattern* for changelog/towncrier snippets, not a concrete file.
_DOT_FRAGMENT_RE = re.compile(r"^\.[a-z0-9_-]+\.(?:rst|md|txt|markdown)$", re.IGNORECASE)


def is_dot_fragment_name(object_name: str) -> bool:
    """Whether a path mention is a dot-prefixed filename pattern."""
    return bool(_DOT_FRAGMENT_RE.match(object_name.rstrip("/")))


# Conventional placeholder names in paths (foo/bar/baz/sample/example/mymodule,
# plus the tutorial xxx/yyy test placeholders and ``my*`` reader-project names).
_PLACEHOLDER_SEGMENTS: frozenset[str] = load_list("structure.json", "placeholder_segments")
_PLACEHOLDER_EXTRAS: frozenset[str] = frozenset({"xxx", "yyy"})
# Real ``my*`` names that must never be treated as reader placeholders.
_MY_PREFIX_DENY: frozenset[str] = frozenset({"mysql", "mypy", "mypyc", "mypy_extensions"})


def has_placeholder_segment(path: str) -> bool:
    """Whether a path carries a conventional placeholder segment/name.

    A path whose directory segments (or file stem) use placeholder words
    (``foo/bar/tests/test_foo.py``, ``numpy/xxx/tests/test_yyy.py``,
    ``src/mypkg/``, ``my_extension.pyx``) is a tutorial template, not a
    concrete repository path. Only ever consulted for *absent* paths, so a real
    ``mypackage/`` directory (which would resolve) is unaffected.
    """
    stripped = path.rstrip("/")
    for seg in stripped.split("/"):
        low = seg.lower()
        if low in _PLACEHOLDER_SEGMENTS or low in _PLACEHOLDER_EXTRAS:
            return True
        stem = low.rsplit(".", 1)[0]
        if stem not in _MY_PREFIX_DENY and re.fullmatch(r"my[a-z0-9_]+", stem):
            return True
        if any(tok in _PLACEHOLDER_EXTRAS for tok in stem.replace("-", "_").split("_")):
            return True
    return False


def _basename(path: str) -> str:
    stripped = path.rstrip("/")
    return stripped.rsplit("/", 1)[-1]


# Per-evidence-dict derived indexes. Indexed caches are bounded LRU (the
# pipeline allocates a fresh inventory dict per analysis run, so an unbounded
# module-level dict would pin every analyzed inventory for the web process's
# lifetime). Entries are identity-guarded so ``id`` reuse across runs can never
# serve a stale index.
_INDEX_CACHE_MAX = 16


def _index_cache_lookup(cache: OrderedDict, marker: int, value: object):
    hit = cache.get(marker)
    if hit is not None and hit[0] is value:
        cache.move_to_end(marker)
        return hit[1]
    return None


def _index_cache_store(cache: OrderedDict, marker: int, value: object, index) -> None:
    cache[marker] = (value, index)
    cache.move_to_end(marker)
    while len(cache) > _INDEX_CACHE_MAX:
        cache.popitem(last=False)


# Basename → inventory keys, cached per evidence dict.
_BASENAME_INDEX_CACHE: OrderedDict[int, tuple[object, dict[str, list[str]]]] = OrderedDict()


def _basename_index(evidence_by_name) -> dict[str, list[str]]:
    marker = id(evidence_by_name)
    cached = _index_cache_lookup(_BASENAME_INDEX_CACHE, marker, evidence_by_name)
    if cached is not None:
        return cached
    index: dict[str, list[str]] = {}
    for key in evidence_by_name:
        index.setdefault(_basename(key), []).append(key)
    _index_cache_store(_BASENAME_INDEX_CACHE, marker, evidence_by_name, index)
    return index


# Last-segment → symbol keys, cached per evidence dict (identity-guarded like
# the basename index). ``a.b.c`` maps its final segment ``c`` to the full key.
# Both ``resolve_symbol_key`` and the SYMBOL_EXISTS match layer scan only the
# keys sharing the claimed last segment instead of the whole inventory.
_SYMBOL_INDEX_CACHE: OrderedDict[int, tuple[object, dict[str, list[str]]]] = OrderedDict()


def _symbol_index(evidence_by_name) -> dict[str, list[str]]:
    marker = id(evidence_by_name)
    cached = _index_cache_lookup(_SYMBOL_INDEX_CACHE, marker, evidence_by_name)
    if cached is not None:
        return cached
    index: dict[str, list[str]] = {}
    for key in evidence_by_name:
        index.setdefault(key.rsplit(".", 1)[-1], []).append(key)
    _index_cache_store(_SYMBOL_INDEX_CACHE, marker, evidence_by_name, index)
    return index


def last_segment_candidates(base: str, evidence_by_name) -> list[str]:
    """Inventory keys whose last dotted segment is ``base``."""
    return _symbol_index(evidence_by_name).get(base, [])


# Top-level package segments (``a.b.c`` → ``a``), cached per evidence dict. The
# SYMBOL_EXISTS match layer rebuilds this set for every dotted claim that
# reaches the CLOSED-world decision; hoisting it into a bounded identity-guarded
# cache turns an O(inventory) set build per claim into one build per dict.
_TOP_LEVEL_CACHE: OrderedDict[int, tuple[object, frozenset[str]]] = OrderedDict()


def top_level_packages(evidence_by_name) -> frozenset[str]:
    marker = id(evidence_by_name)
    cached = _index_cache_lookup(_TOP_LEVEL_CACHE, marker, evidence_by_name)
    if cached is not None:
        return cached
    tops = frozenset(k.split(".")[0] for k in evidence_by_name)
    _index_cache_store(_TOP_LEVEL_CACHE, marker, evidence_by_name, tops)
    return tops


# Directory path segments (every segment of every inventory key, file leaf
# excluded), cached per evidence dict. The PATH_EXISTS match layer uses this to
# decide whether a missing slash path is *anchored*: if its first segment is not
# any directory of the listing (top-level or nested — document-relative and
# suffix resolution anchor claims to nested dirs, e.g. ``proj/celery.py`` →
# ``examples/django/proj/celery.py``), the mention cannot be a stale reference
# into the project tree (it names a directory that never existed / belongs to
# the reader), so the CLOSED world abstains instead of refuting it. Same cache
# discipline as ``top_level_packages``.
_DIRECTORY_SEGMENTS_CACHE: OrderedDict[int, tuple[object, frozenset[str]]] = OrderedDict()


def directory_segments(evidence_by_name) -> frozenset[str]:
    """Every directory segment of every inventory key (file leaf excluded)."""
    marker = id(evidence_by_name)
    cached = _index_cache_lookup(_DIRECTORY_SEGMENTS_CACHE, marker, evidence_by_name)
    if cached is not None:
        return cached
    segments: set[str] = set()
    for key in evidence_by_name:
        if "/" not in key:
            continue
        parts = key.rstrip("/").split("/")
        dirs = parts if key.endswith("/") else parts[:-1]
        segments.update(dirs)
    _index_cache_store(_DIRECTORY_SEGMENTS_CACHE, marker, evidence_by_name, frozenset(segments))
    return frozenset(segments)


def resolve_evidence_key(object: str, source: str, evidence_by_name) -> str | None:
    """Resolve a claimed path to an inventory key (or ``None``).

    A bare name is resolved against the referencing document's directory first,
    then the repo root; a slash-carrying *file* path against the repo root
    first, then the document's directory, then by **path suffix** — the claimed
    path is resolved when it is a segment-aligned suffix of an inventory key
    (``flaskr/db.py`` → the unique ``examples/tutorial/flaskr/db.py``,
    ``parser/frame.rs`` → ``sqlfluffrs/…/parser/frame.rs``). The old unique-
    basename fallback for slash paths is gone: it confirmed stale references
    against a same-named file in a different directory (``src/old/utils.py`` →
    ``src/new/utils.py``). Trailing-slash directory mentions
    keep the basename-unique fallback (a bare directory name is a true
    existence claim).
    """
    base = _basename(object)
    doc_rel = posixpath.normpath(posixpath.join(posixpath.dirname(source), object))
    if object.endswith("/") and not doc_rel.endswith("/"):
        doc_rel += "/"  # normpath strips the trailing slash; a dir key needs it back
    if "/" not in object.rstrip("/"):
        if doc_rel in evidence_by_name:
            return doc_rel
        if object in evidence_by_name:
            return object
        matches = _basename_index(evidence_by_name).get(base, ())
        return matches[0] if len(matches) == 1 else None
    if object in evidence_by_name:
        return object
    if doc_rel in evidence_by_name:
        return doc_rel
    suffix = "/" + object
    for key in sorted(basename_candidates(object, evidence_by_name)):
        if key.endswith(suffix):
            return key
    return None


def basename_candidates(path: str, evidence_by_name) -> list[str]:
    """Inventory keys sharing ``path``'s basename (may be empty)."""
    return _basename_index(evidence_by_name).get(_basename(path), [])


def normalize_symbol(name: str) -> str:
    """Canonicalize a symbol mention for grouping and matching.

    Lowercase and fold backslashes to dots; both the doc mention and the
    harvested symbol key are normalized so grouping compares canonical forms.
    """
    return name.strip().lower().replace("\\", ".")


def resolve_symbol_key(object: str, evidence_by_name) -> str | None:
    """Resolve a claimed symbol to an inventory key (or ``None``).

    A dotted claim of **three or more segments** resolves only by an exact
    name, by the claimed name being a suffix of a key, or by its tail *after
    the top-level package* being a suffix of a key whose top matches —
    ``transformers.logging.critical`` → ``transformers.utils.logging.critical``
    (tail ``logging.critical``). The last-segment fallback is removed for these
    claims: it confirmed unrelated symbols through a shared final segment
    (``numpy.array_api.Array`` → ``numpy.f2py.symbolic.op.array``,
    ``scrapy.contrib.itemparser.parsers.Join`` →
    ``scrapy.crawler.crawlerrunner.join``).

    Shorter claims (one or two segments) keep the full resolution: exact,
    suffix, then a last-segment match scored by shared leading prefix — this is
    what resolves re-exported and nested symbols (``basehook.get_connection`` →
    ``airflow.hooks.base.basehook.get_connection``, ``pkg.mark.x`` →
    ``_pkg.mark.x``). A *dotted* claim whose last segment matches several keys
    picks the one sharing the longest leading prefix
    (``scipy.stats.bernoulli`` → ``scipy.stats._discrete_distns.bernoulli``,
    not ``scipy.special._basic.bernoulli``), then the shallowest candidate. A
    bare name stays unresolved when ambiguous — the match layer enumerates all
    last-segment matches for it.
    """
    if object.count(".") < 2:
        return _resolve_symbol_key_simple(object, evidence_by_name)
    if object in evidence_by_name:
        return object
    top, tail = object.split(".", 1)
    base = object.rsplit(".", 1)[-1]
    pool = last_segment_candidates(base, evidence_by_name)
    exact_suffix = sorted(k for k in pool if k.endswith("." + object))
    if exact_suffix:
        return exact_suffix[0]
    same_top = sorted(k for k in pool if k.split(".", 1)[0] == top and k.endswith("." + tail))
    return same_top[0] if same_top else None


def _resolve_symbol_key_simple(object: str, evidence_by_name) -> str | None:
    """Resolution for one- and two-segment claims (see ``resolve_symbol_key``)."""
    if object in evidence_by_name:
        return object
    suffix = "." + object
    base = object.rsplit(".", 1)[-1]
    # Only keys sharing the claimed last segment can match, so index by it
    # instead of scanning the whole inventory.
    pool = last_segment_candidates(base, evidence_by_name)
    suffix_matches = [key for key in pool if key.endswith(suffix)]
    base_matches = pool
    if "." not in object:
        if len(suffix_matches) == 1:
            return suffix_matches[0]
        return base_matches[0] if len(base_matches) == 1 else None
    pool = suffix_matches if suffix_matches else base_matches
    return _best_segment_match(object, pool)


def _best_segment_match(object: str, candidates: list[str]) -> str | None:
    """The candidate whose dotted path best matches the claimed one.

    Prefer the longest shared leading-segment prefix, then the shallowest
    candidate, then lexicographic order for determinism. ``None`` when nothing
    matches.
    """
    if not candidates:
        return None
    obj_parts = object.split(".")

    def score(key: str) -> tuple[int, int, str]:
        cand_parts = key.split(".")
        shared = 0
        for a, b in zip(obj_parts, cand_parts, strict=False):
            if a != b:
                break
            shared += 1
        return (shared, -len(cand_parts), key)

    return sorted(candidates, key=score)[-1]


# Python builtins that docs mention as bare calls (``issubclass()``,
# ``sorted()``, ``str()``) but that are not project symbols. A bare claim about
# one is not a CLOSED-world finding against the project tree.
# (data/structure.json)
PYTHON_BUILTINS: frozenset[str] = load_list("structure.json", "python_builtins")


def is_builtin_symbol(name: str) -> bool:
    """Whether a bare symbol mention is a Python builtin (not a project symbol)."""
    return name in PYTHON_BUILTINS
