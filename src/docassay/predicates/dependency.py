"""The DEPENDENCY predicate: extraction and matching.

Extraction is anchor-first over the controlled allowlist; every dictionary hit
in a window is one claim anchor, and the context markers are cut around it. No
trigger words gate extraction — the vocabulary is the only selector. Matching is
binary against the harvested manifest inventory with not-contradiction version
semantics.

World (decided 2026-08-27, methodology §3.4): **closed over the
manifest inventory.** The manifest (``pyproject.toml`` / ``requirements*.txt``)
is complete by construction for the dependencies it declares, so a claim about a
declared dependency is fully adjudicated (presence → SUPPORTED, negation →
REFUTED, version → checked). A claim about a dependency the manifest does NOT
declare stays NEI: absence never refutes (transitive/conditional dependencies,
prose mentions of ecosystem names).

In a monorepo the inventory is **per-domain**: a sub-project claim
adjudicates against its own manifest-bearing directory only, so two sub-projects
never contaminate each other's verdicts. A root-domain claim (``""``) describes
the whole repository and adjudicates against the union of every manifest.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from docassay.core.models import Context, PredicateClaim
from docassay.core.windows import anchor_line_text, iter_windows, line_at
from docassay.data import load_list, regex_alternation
from docassay.evidence.manifests import (
    LOCK_SOURCE_TYPES,
    DependencyEvidence,
    build_dependency_inventory,
)
from docassay.markers.context import EXIST_VERBS, extract_contexts
from docassay.markers.version import constraint_satisfied, parse_constraint
from docassay.predicates.base import GateResult, Predicate, Verdict
from docassay.vocabularies.dependency import (
    allowlist_for,
    dependency_anchors,
    normalize_dependency_name,
)
from docassay.vocabularies.markers import NEGATION_WORDS, perf_re

DEPENDENCY_PREDICATE = "DEPENDENCY"
DEPENDENCY_WORLD = "closed-over-manifest"

# A dependency name that appears inside a URL is a link/hostname, not a claim
# about a project dependency (``www.python.org``, ``github.com/celery/celery``).
# The anchor allowlist's word boundary is ``[a-z0-9_-]``, so ``.`` in a URL
# does not stop a hostname segment from anchoring. The TLD is the full IANA root
# zone (data/structure.json ``host_tlds``), but a bare ``name.tld`` is only
# treated as a URL when the surrounding shape is unambiguous — a scheme, a
# ``www.`` host, an e-mail, a ≥2-dot domain (``pandas.pydata.org``) or a
# single-dot domain with a path (``github.com/celery``). A single-dot bare
# ``requests.py``/``python.org`` stays an ordinary token, so dotted *code*
# identifiers (``numpy.random``) and real dependency mentions are not suppressed.
_URL_TLDS = regex_alternation(load_list("structure.json", "host_tlds"))
_PATH = r"(?:/[^\s<>()\[\]\"']*)?"
_DOMAIN = r"[a-z0-9][a-z0-9-]*"
_URL_SPAN_RE = re.compile(
    r"https?://[^\s<>()\[\]\"']+|"
    r"(?<![\w.])www\.[^\s<>()\[\]\"']+|"
    r"[a-zA-Z0-9._%+-]+@" + _DOMAIN + r"(?:\." + _DOMAIN + r")*\.(?:" + _URL_TLDS + r")|"
    r"(?<![\w.])(?:" + _DOMAIN + r"\.){2,}(?:" + _URL_TLDS + r")(?![a-z0-9-])" + _PATH + r"|"
    r"(?<![\w.])" + _DOMAIN + r"\.(?:" + _URL_TLDS + r")(?![a-z0-9-])/[^\s<>()\[\]\"']*"
)


def _non_url_anchors(
    window: str, anchors: list[tuple[int, int, str]]
) -> list[tuple[int, int, str]]:
    """Anchors whose position is not inside a URL span (``www.python.org``)."""
    spans = _URL_SPAN_RE.finditer(window)
    url_spans = [(m.start(), m.end()) for m in spans]
    if not url_spans:
        return anchors
    return [a for a in anchors if not any(s <= a[0] < e for s, e in url_spans)]


def scan_document(
    text: str,
    source: str,
    *,
    extra_names: frozenset[str] = frozenset(),
) -> list[PredicateClaim]:
    """Anchor-first scan of one document → DEPENDENCY claims.

    ``extra_names`` are the project's own manifest-declared dependencies (the
    runtime extension of the fixed allowlist), so a dependency the tool harvests
    is always anchorable.
    """
    allowlist = allowlist_for(frozenset(extra_names))
    claims: list[PredicateClaim] = []
    # One claim per ``(line, object)`` still, but the first mention does not
    # always own the context: "NumPy (numpy>=1.24)" anchors ``NumPy`` first
    # (versionless) and ``numpy>=1.24`` second (versioned). Keeping the first
    # claim unconditionally lost the version and made the injected manifest
    # invisible (Stage B E1). The map points at the claim's slot so a later
    # versioned occurrence can replace a versionless one.
    claim_slots: dict[tuple[str, str], int] = {}

    for line_idx, (window, line_start, _line_end, line_map) in enumerate(iter_windows(text)):
        anchors = _non_url_anchors(window, dependency_anchors(window, allowlist))
        if not anchors:
            continue
        contexts = extract_contexts(window, anchors, line_map=line_map)
        for start, end, token in anchors:
            object_name = normalize_dependency_name(token)
            dedupe_key = (anchor_line_text(window, line_map, start), object_name)
            claim = PredicateClaim(
                claim_id=f"{source}:{line_idx}:{start}",
                source=source,
                predicate_type=DEPENDENCY_PREDICATE,
                object=object_name,
                raw_context=anchor_line_text(window, line_map, start),
                context=contexts[start],
                line_start=line_at(line_map, start, line_start),
                line_end=line_at(line_map, end - 1, line_start),
            )
            slot = claim_slots.get(dedupe_key)
            if slot is None:
                claim_slots[dedupe_key] = len(claims)
                claims.append(claim)
            elif claims[slot].context.version is None and claim.context.version is not None:
                # Same line, same object: prefer the versioned occurrence. A
                # genuinely versionless repeat keeps the first claim.
                claims[slot] = claim
    return claims


def _evidence_ids(items: Iterable[DependencyEvidence]) -> tuple[str, ...]:
    return tuple(e.evidence_id for e in items)


# Past/change markers that make a version mention a historical reference rather
# than a current requirement ("since Celery 4.0", "will be removed in 2.3",
# "As of Airflow 2.7.0"). Refuting such a claim would be a false finding.
# (data/dependency.json)
_PAST_TIME: frozenset[str] = load_list("dependency.json", "past_time")

# Time words that are historical only NEXT TO a version or a date ("since 2.0",
# "until v3", "before 2024") — "after installing", "blocks until interrupted"
# and "time series" are not historical references.
_CONTEXTUAL_TIME: frozenset[str] = frozenset({"after", "as of", "before", "since", "until"})
_ALWAYS_HISTORICAL_TIME: frozenset[str] = frozenset(
    w for w in _PAST_TIME if w not in _CONTEXTUAL_TIME
)
_VERSION_OR_DATE_NEAR = re.compile(
    r"\b(?:after|as\s+of|before|since|until)\s+(?:the\s+)?(?:version\s+)?"
    r"(?:v?\d+(?:\.\d+){0,3}|\d{4})\b",
    re.IGNORECASE,
)

_HISTORICAL_PHRASE_RE = re.compile(
    r"(?:\b(?:"
    + regex_alternation(load_list("dependency.json", "historical_phrases"), escape=False)
    + r")\b|deprecat)",
    re.IGNORECASE,
)

# Migration/upgrade/compatibility framing (E6): a version in "migrate from v1
# to v2", "compatibility with 0.7.x" or "API differences between 0.7 and 0.10"
# describes a relation between releases, not the project's current requirement.
# The flag downgrades a would-be version REFUTED to NEI; it never suppresses a
# claim. (data/dependency.json)
_COMPATIBILITY_PHRASE_RE = re.compile(
    r"\b(?:"
    + regex_alternation(load_list("dependency.json", "compatibility_phrases"), escape=False)
    + r")\b",
    re.IGNORECASE,
)

# "Starting from ``joblib >= 0.14``, joblib will ..." is a change note, not a
# requirement. Both a following version and a change/feature cue are required,
# so "starting from scratch" and a bare "starting from" stay inert.
_STARTING_FROM_RE = re.compile(
    r"\bstarting\s+(?:from|with)\b[^\n]{0,80}?\bv?\d+(?:\.\d+){1,3}\b",
    re.IGNORECASE,
)
_CHANGE_CUE_RE = re.compile(
    r"\b(?:chang\w*|support\w*|available|defaults?|requires?|required|uses?|used|"
    r"introduc\w*|deprecat\w*|removed?|no\s+longer|will|can|is|are)\b",
    re.IGNORECASE,
)

# A versioned *release* as the subject of a past-tense state verb
# ("Scikit-learn 0.23 required Python 3.6", "FastAPI 0.126.0 dropped support")
# is release history, not a present requirement. The same-object guard in
# ``is_historical_version`` keeps a current "requests 2.0 required ..." live.
_RELEASE_HISTORY_RE = re.compile(
    r"\b(?P<name>[a-z0-9][a-z0-9._+-]*)\s+(?:version\s+)?"
    r"v?(?P<version>\d+(?:\.\d+){1,3})\s+"
    r"(?:required|supported|had|was|were|used|included|shipped|introduced|"
    r"added|dropped|removed|deprecated|changed|needed)\b",
    re.IGNORECASE,
)
_CLAIM_VERSION_NUM_RE = re.compile(r"^(?:==|>=|<=|>|<|~=|\^|!=)?\s*v?([0-9]+(?:\.[0-9]+)*)")

# Test-environment / benchmark contexts: a version mention describes the CI or
# benchmark environment ("tested under PyTorch 2.4+", "benchmark on 2.3.1+cu121"),
# not a current requirement. English-only (multilingual markers deferred).
# (data/dependency.json)
_TEST_ENV_RE = re.compile(
    "(?:"
    + regex_alternation(load_list("dependency.json", "test_env_patterns"), escape=False)
    + ")",
    re.IGNORECASE,
)

# A version bound introduced by a framing word ("With Celery <5.4", "SDPA is
# used by default for torch>=2.1.1") describes a feature condition, not a
# project requirement. Upper bounds are decisive; ``>=``/``>``/pins need a
# feature phrase nearby. (data/dependency.json)
_CONDITIONAL_INTRO_RE = re.compile(
    r"\b(with|for|when|if)\s+[a-z0-9][a-z0-9._-]*\s*(>=|<=|>|<|==|~=|\^|!=)?\s*v?([0-9]+(?:\.[0-9]+){0,3})\b",
    re.IGNORECASE,
)
_FEATURE_PHRASE_RE = re.compile(
    r"\b(?:"
    + regex_alternation(load_list("dependency.json", "feature_phrases"), escape=False)
    + r")\b",
    re.IGNORECASE,
)

# Requirement/compatibility verbs that keep an "in <dep> <version>" locator a
# live requirement claim ("In Python 3.10, the code requires X") rather than a
# descriptive topic locator ("in Django 1.4", "In Celery 5.0, tasks were...").
# (data/dependency.json)
_REQUIREMENT_VERBS: frozenset[str] = EXIST_VERBS | load_list(
    "dependency.json", "requirement_verb_extra"
)

_IN_LOCATOR_RE = re.compile(
    r"\bin\s+([a-z0-9][a-z0-9._-]*)\s*(?:==)?\s*v?([0-9]+(?:\.[0-9]+){0,3})\b",
    re.IGNORECASE,
)

_OPTIONALITY_NEED_RE = re.compile(
    r"\b(?:no|not|without)\s+[a-z0-9][a-z0-9._-]*\s+(?:needed|required|necessary|mandatory)\b",
    re.IGNORECASE,
)
_HYPOTHETICAL_RE = re.compile(r"(?:^\s*|[.;,]\s+)if\b", re.IGNORECASE)

# Configuration-fragment windows: a TOML/pyproject assignment
# (``pytest = "^8.0.0"``, ``dev = ["pytest (>=7.1.2,<8.0.0)"]``) or a quoted
# PEP 508 requirement literal (``"pytest (>=8.0.0,<9.0.0)",``) shows the
# configuration a *reader* would write, not a claim about the project's own
# requirements. Such a window is a non-claim (CLAIM_GATE), not a REFUTED.
_CONFIG_ASSIGNMENT_RE = re.compile(
    r"(?:^|[\s\[,])[\"']?[a-z0-9][a-z0-9._-]*[\"']?\s*=\s*[\"'\[{]",
    re.IGNORECASE,
)
_QUOTED_REQUIREMENT_RE = re.compile(
    r"[\"'][a-z0-9][a-z0-9._-]*\s*(?:\(|>=|<=|==|~=|\^|>|<)",
    re.IGNORECASE,
)

# Install instructions: "pip install ruff>=0.4.8",
# "You should install ruff". The mention tells the reader how to install a
# package; it is not a claim about the project's manifest.
_INSTALL_INSTRUCTION_RE = re.compile(
    r"\byou\s+(?:should|must|can|may|need\s+to|might\s+want\s+to|will\s+need\s+to)?\s*install\b"
    r"|\b(?:pip3?|conda|mamba|pipenv|python\s+-m\s+pip)\s+install\b"
    r"|\b(?:poetry|uv)\s+(?:add|remove|cache)\b"
    r"|\bpipx\s+(?:install|run)\b"
    r"|\bpyenv\s+(?:local|install|global)\b",
    re.IGNORECASE,
)

# Language-version *context* mentions of Python: "on Python 3.6", "as of
# Python 3.8", "supports Python 3.9", "compatible with Python 3.5", "if using
# Python 2" describe language behaviour, a language version or a target, not a
# project requirement ("requires Python X" stays a live version claim). The
# pattern is deliberately narrow: bare "with Python"/"tested with Python" and
# requirement verbs are not included, so real version-drift findings ("Rich
# requires Python 3.8", "tested with Python 3.10-3.12") keep REFUTING.
_PYTHON_CONTEXT_RE = re.compile(
    r"\b(?:on|for|as of|since|until|before|like|in|under|within|up to|related to)"
    r"\s+(?:a\s+)?python\b"
    r"|\bwith\s+(?:a|an)\s+python\b"
    r"|\bpython\s+[0-9][0-9.]*\+?\s+natively\s+supports\b"
    r"|\bpython\s+[0-9][0-9.]*\+?\s+introduces\b"
    r"|\bpython\s+[0-9][0-9.]*\+?\s+(?:is|was|are|were)\s+no\s+longer\b"
    r"|\bpython\s+[0-9][0-9.]*\+?\s+was\b"
    r"|\b(?:supports?|supporting|supported)\s+(?:the\s+)?python\b"
    r"|\brepresent(?:s|ing|ed)?\s+(?:the\s+)?python\b"
    r"|\b(?:drop|dropping|drops?)\s+(?:the\s+)?python\b"
    r"|\bno\s+longer\s+supports?\s+(?:python\b|this\s+version\b)"
    r"|\bcompatible\s+with\s+(?:any\s+)?python\b"
    r"|\bif\s+using\s+python\b"
    r"|\busing\s+python\s+[0-9]"
    r"|\ball\s+python\s+[0-9]"
    r"|\b(?:introduced|dropped|removed)\s+(?:in|on)\s+python\b",
    re.IGNORECASE,
)


def is_historical(claim: PredicateClaim) -> bool:
    """Whether a claim describes a past/change state, not a current requirement."""
    if claim.context.time & _ALWAYS_HISTORICAL_TIME:
        return True
    if claim.context.time & _CONTEXTUAL_TIME:
        # "since"/"until"/"before"/"after"/"as of" are historical only when a
        # version or a date follows ("since 2.0", "until v3", "before 2024");
        # "after installing", "blocks until interrupted" stay current-state.
        if _VERSION_OR_DATE_NEAR.search(claim.raw_context):
            return True
    return bool(_HISTORICAL_PHRASE_RE.search(claim.raw_context))


def is_compatibility_context(claim: PredicateClaim) -> bool:
    """Whether a versioned mention is migration/compatibility prose (E6).

    "migrate from v1 to v2", "compatibility with 0.7.x", "API differences
    between 0.7 and 0.10", "prior to version 0.16" and "starting from joblib
    >= 0.14, ... will ..." describe a relation between releases or a change
    note. The mention may be true or false, but it is not the project's current
    requirement, so a would-be version contradiction must not REFUTE.
    """
    if claim.context.version is None:
        return False
    low = claim.raw_context
    if _COMPATIBILITY_PHRASE_RE.search(low):
        return True
    return bool(_STARTING_FROM_RE.search(low) and _CHANGE_CUE_RE.search(low))


def is_historical_version(claim: PredicateClaim) -> bool:
    """Whether a versioned release is the subject of a past-tense state verb.

    "Scikit-learn 0.23 required Python 3.6—3.8." reports what an old release
    required, not what the project requires now. The same-object/same-version
    guard keeps a live "requests 2.0 required ..." from being downgraded.
    """
    if claim.context.version is None:
        return False
    match = _RELEASE_HISTORY_RE.search(claim.raw_context)
    if match is None:
        return False
    claimed = _CLAIM_VERSION_NUM_RE.match(claim.context.version)
    subject = normalize_dependency_name(match.group("name"))
    if subject == claim.object and claimed is not None:
        return match.group("version") != claimed.group(1)
    return True


def is_test_env(claim: PredicateClaim) -> bool:
    """Whether a version mention describes a test/benchmark environment."""
    if claim.context.version is None:
        return False
    return bool(_TEST_ENV_RE.search(claim.raw_context))


def is_descriptive_locator(claim: PredicateClaim) -> bool:
    """Whether an ``in <dep> <version>`` mention is a topic locator, not a claim.

    "in Django 1.4", "In Celery 5.0, tasks were defined" locate a discussion in
    a version. A requirement/compatibility verb anywhere in the window keeps the
    mention a live claim ("In Python 3.10, the code requires X").
    """
    version = claim.context.version
    if not version:
        return False
    m = re.match(r"^(?:==|>=|<=|>|<|~=|\^|!=)?\s*v?([0-9]+(?:\.[0-9]+)*)", version)
    if not m:
        return False
    num = m.group(1)
    for loc in _IN_LOCATOR_RE.finditer(claim.raw_context.lower()):
        if loc.group(2) != num:
            continue
        if normalize_dependency_name(loc.group(1)) != claim.object:
            continue
        if _REQUIREMENT_VERBS.intersection(_window_tokens(claim.raw_context)):
            return False
        return True
    return False


def is_conditional(claim: PredicateClaim) -> bool:
    """Whether a version bound is a feature-gate condition, not a requirement."""
    version = claim.context.version
    if not version:
        return False
    m = re.match(r"^(?:==|>=|<=|>|<|~=|\^|!=)?\s*v?([0-9]+(?:\.[0-9]+)*)", version)
    if not m:
        return False
    num = m.group(1)
    low = claim.raw_context.lower()
    intro = _CONDITIONAL_INTRO_RE.search(low)
    if not intro or intro.group(3) != num:
        return False
    intro_op = intro.group(2) or "=="
    if intro_op in ("<", "<="):
        return True
    return intro_op in (">", ">=") and bool(_FEATURE_PHRASE_RE.search(low))


def is_hypothetical(claim: PredicateClaim) -> bool:
    """Whether a negation sits in a hypothetical: "If you have not installed X"."""
    return bool(_HYPOTHETICAL_RE.search(claim.raw_context))


def config_fragment_reason(claim: PredicateClaim) -> str:
    """The literal kind of configuration fragment in the window, or ``""``."""
    if _CONFIG_ASSIGNMENT_RE.search(claim.raw_context):
        return "key = value fragment"
    if _QUOTED_REQUIREMENT_RE.search(claim.raw_context):
        return "quoted requirement string"
    return ""


def is_install_instruction(claim: PredicateClaim) -> bool:
    """Whether the claim window is an install instruction, not a claim."""
    return bool(_INSTALL_INSTRUCTION_RE.search(claim.raw_context))


def is_python_context(claim: PredicateClaim) -> bool:
    """Whether a ``python`` version mention is language context, not a requirement.

    Requires a version and the ``python`` object; see ``_PYTHON_CONTEXT_RE``.
    """
    if claim.object != "python" or claim.context.version is None:
        return False
    return bool(_PYTHON_CONTEXT_RE.search(claim.raw_context))


def is_optionality_phrasing(claim: PredicateClaim) -> bool:
    """Whether a negation is phrased as optionality: "no X needed / not required"."""
    return bool(_OPTIONALITY_NEED_RE.search(claim.raw_context.lower()))


def is_perf_note(claim: PredicateClaim) -> bool:
    """Whether a version mention is a performance note, not a requirement.

    "faster with PyTorch 2.9 or later", "less memory with X <version>" describe
    a performance property of a version, not a project requirement. A version
    must be attached (a bare "faster installs" without a version does not touch
    the dependency claim).
    """
    return claim.context.version is not None and bool(perf_re().search(claim.raw_context))


def claim_flags(claim: PredicateClaim) -> dict[str, bool]:
    """All window-level downgrade signals of one claim (fed to match_dependency)."""
    return {
        "historical": is_historical(claim),
        "test_env": is_test_env(claim),
        "locator": is_descriptive_locator(claim),
        "conditional": is_conditional(claim),
        "hypothetical": is_hypothetical(claim),
        "optionality": is_optionality_phrasing(claim),
        "perf": is_perf_note(claim),
        "python_context": is_python_context(claim),
        "compatibility": is_compatibility_context(claim),
        "historical_version": is_historical_version(claim),
    }


def dependency_gate(claim: PredicateClaim) -> GateResult:
    """Whether a scan-produced DEPENDENCY mention is a current-state claim.

    Non-claims by construction (Phase 2, surgical): historical, test-env,
    hypothetical and optionality mentions, configuration fragments and install
    instructions. Locator/conditional stay in the verdict layer as
    downgrades (they can carry legitimate feature-gate requirements). A
    *versionless negation* ("X does not support Y", "does not use X") stays in
    the verdict layer too: it can be a genuine usage claim and the inventory's
    absence cannot settle it — match returns a conservative NEI.
    """
    if is_historical(claim):
        return GateResult(False, "historical mention")
    if is_test_env(claim):
        return GateResult(False, "test-env mention")
    if is_hypothetical(claim) and claim.is_negative:
        # "If you have not installed X" is a hypothetical only when the mention
        # is actually negated; an unconditional leading "if" ("if the package
        # is installed, ...") is a condition, not a non-claim.
        return GateResult(False, "hypothetical negation")
    if is_optionality_phrasing(claim):
        return GateResult(False, "optionality phrasing")
    if fragment := config_fragment_reason(claim):
        return GateResult(False, fragment)
    if is_install_instruction(claim):
        return GateResult(False, "install instruction")
    return GateResult()


_WINDOW_TOKEN_RE = re.compile(r"[a-z][a-z0-9]*")


def _window_tokens(text: str) -> frozenset[str]:
    return frozenset(_WINDOW_TOKEN_RE.findall(text.lower()))


def _is_single_pin(version: str) -> bool:
    parsed = parse_constraint(version)
    return parsed is not None and len(parsed) == 1 and parsed[0][0] == "=="


def _declared_evidence(evidence: list[DependencyEvidence]) -> list[DependencyEvidence]:
    """Manifest-declared evidence, excluding lock-file (transitive) evidence."""
    return [e for e in evidence if e.source_type not in LOCK_SOURCE_TYPES]


def _version_evidence(evidence: list[DependencyEvidence]) -> list[DependencyEvidence]:
    """Evidence that can carry a version for comparison.

    The declared manifest constraint is authoritative; a lock-file resolved
    version is consulted only when the manifest declares the dependency without
    a version.
    """
    declared = [e for e in _declared_evidence(evidence) if e.version_spec.strip()]
    if declared:
        return declared
    return [e for e in evidence if e.source_type in LOCK_SOURCE_TYPES and e.version_spec.strip()]


def match_dependency(
    object: str,
    context: Context,
    evidence_by_name: dict[str, list[DependencyEvidence]],
    *,
    historical: bool = False,
    test_env: bool = False,
    locator: bool = False,
    conditional: bool = False,
    hypothetical: bool = False,
    optionality: bool = False,
    perf: bool = False,
    python_context: bool = False,
    compatibility: bool = False,
    historical_version: bool = False,
) -> Verdict:
    """Match one claim's context against the inventory.

    Returns a ``Verdict`` (outcome, supporting/refuting evidence ids, layer,
    reason). See `Verdict` for the layer semantics (WORLD / DECIDABILITY /
    CLAIM_GATE).
    Verdict follows the §6.1 table with ``DEPENDENCY_WORLD``: a claim about a
    declared dependency is closed (presence → SUPPORTED, negation → REFUTED,
    version → not-contradiction check); a claim about an undeclared dependency
    is NEI. Undecidable version questions (no manifest version, wildcards,
    ``!=`` exclusions) are NEI, as are historical version references
    (``historical=True`` downgrades a would-be version REFUTED to NEI). The
    same downgrade applies to test-environment, topic-locator, conditional
    (feature-gate), performance-note ("faster with X 2.9+") and
    migration/compatibility ("migrate from v1", "API differences between",
    "starting from X >= 0.14") mentions. A hypothetical negation ("if you have
    not installed X") or an optionality phrasing ("no X needed") against an
    optional-only dependency is NEI, not REFUTED.
    """
    evidence = evidence_by_name.get(object, [])
    declared = _declared_evidence(evidence)
    negative = bool(context.polarity & NEGATION_WORDS)
    non_requirement = (
        historical
        or test_env
        or locator
        or conditional
        or perf
        or python_context
        or compatibility
        or historical_version
    )

    if negative:
        if not declared:
            # P1 conservative: absence does not confirm a negation in CLOSED.
            return Verdict("NEI", layer="WORLD", reason="negation with no evidence")
        if hypothetical:
            return Verdict("NEI", layer="CLAIM_GATE", reason="hypothetical negation")
        if optionality and all(e.source_type.startswith("optional") for e in declared):
            return Verdict("NEI", layer="CLAIM_GATE", reason="optionality phrasing")
        if context.version is None:
            # A negated mention without a version is a feature/limitation or
            # availability statement ("X does not support Y", "without X",
            # "X is not installed", "do not use X.foo"), not an adjudicable
            # claim that the project uses X. The manifest declaring X does not
            # mean X is used (dependencies are often optional/conditional), so
            # absence-of-usage cannot be closed-world REFUTED (measured
            # 2026-09-07: all 12 versionless negated DEPENDENCY REFUTED on the
            # train corpus were false; decision-record ws4-negation).
            return Verdict("NEI", layer="CLAIM_GATE", reason="negated versionless mention")
        if non_requirement:
            return Verdict("NEI", layer="CLAIM_GATE", reason="negated non-requirement mention")
        return _match_negated_version(object, context, evidence)

    if not declared:
        # D1: undeclared dependency — OPEN-by-transitivity, never REFUTED. A
        # package present only in a lock file is transitive, not declared, and
        # does not close the world either.
        return Verdict("NEI", layer="WORLD", reason="undeclared (open by transitivity)")

    if context.version is None:
        return Verdict("SUPPORTED", _evidence_ids(declared))

    version_items = _version_evidence(evidence)
    if not version_items:
        return Verdict("NEI", layer="DECIDABILITY", reason="declared but no version spec")

    supporting: list[DependencyEvidence] = []
    refuting: list[DependencyEvidence] = []
    undecidable = False
    for evidence_item in version_items:
        eq = constraint_satisfied(context.version, evidence_item.version_spec.strip())
        if eq is True:
            supporting.append(evidence_item)
        elif eq is False and evidence_item.source_type not in LOCK_SOURCE_TYPES:
            # A resolved lock pin may confirm a doc version claim but never
            # contradict it: the declared manifest constraint is the contract,
            # the lock only records one resolution.
            refuting.append(evidence_item)
        else:
            undecidable = True

    if supporting:
        return Verdict("SUPPORTED", _evidence_ids(supporting), _evidence_ids(refuting))
    if undecidable:
        return Verdict("NEI", layer="DECIDABILITY", reason="version range undecidable")
    if non_requirement:
        if compatibility:
            reason = "compatibility mention"
        elif historical_version:
            reason = "historical version mention"
        else:
            reason = "non-requirement mention"
        return Verdict("NEI", layer="CLAIM_GATE", reason=reason)
    return Verdict("REFUTED", (), _evidence_ids(refuting))


def _match_negated_version(
    object: str,
    context: Context,
    evidence: list[DependencyEvidence],
) -> Verdict:
    """A negated versioned claim: ``<dep> <version> is not supported``.

    The doc excludes a specific version. If that version lies inside the
    manifest's allowed set, the doc excludes something the code supports →
    REFUTED. Outside the set, doc and code agree → SUPPORTED. Undecidable
    (range negation, wildcard manifest) → NEI.
    """
    if not _is_single_pin(context.version):
        return Verdict("NEI", layer="DECIDABILITY", reason="negated non-single-pin version")
    version_items = _version_evidence(evidence)
    if not version_items:
        return Verdict("NEI", layer="DECIDABILITY", reason="negated version, no spec")
    supporting: list[DependencyEvidence] = []
    refuting: list[DependencyEvidence] = []
    undecidable = False
    for evidence_item in version_items:
        eq = constraint_satisfied(context.version, evidence_item.version_spec.strip())
        if eq is True:
            refuting.append(evidence_item)
        elif eq is False and evidence_item.source_type not in LOCK_SOURCE_TYPES:
            supporting.append(evidence_item)
        else:
            undecidable = True
    if refuting:
        return Verdict("REFUTED", (), _evidence_ids(refuting))
    if undecidable:
        return Verdict("NEI", layer="DECIDABILITY", reason="negated version undecidable")
    return Verdict("SUPPORTED", _evidence_ids(supporting))


dependency_predicate = Predicate(
    name=DEPENDENCY_PREDICATE,
    world=DEPENDENCY_WORLD,
    scan=scan_document,
    harvest=build_dependency_inventory,
    match=match_dependency,
    flags=claim_flags,
    gate=dependency_gate,
    domain_scoped_evidence=True,
    extend_with_declared=True,
    anchor_evidence=lambda item: getattr(item, "source_type", "") not in LOCK_SOURCE_TYPES,
)
