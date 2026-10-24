"""Deterministic per-finding signal extraction (triage input).

A finding is a resolved assertion (the REFUTED ones are the findings of
interest). For each finding we compute a signal vector that the classifier and
the scorer consume. Every signal is a pure deterministic function of the
assertion's claims (their ``raw_context``, ``object``, ``context`` markers), the
predicate world, and the document class — no LLM, no stored state
(methodology §6.3).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from docassay.core.models import Assertion, PredicateClaim
from docassay.predicates.base import Predicate
from docassay.vocabularies.markers import NEGATION_WORDS, perf_re

# --- document classification -------------------------------------------------

_DIRECTIVE_STEMS = frozenset(
    {
        "contributing",
        "hacking",
        "development",
        "developing",
        "agents",
        "code_of_conduct",
        "maintainers",
        "maintaining",
    }
)


def classify_document(source: str) -> str:
    """Authority class of the document a finding was extracted from.

    Priority: README > DIRECTIVE > BENCHMARK > TEST > TUTORIAL > DOCS > OTHER.
    """
    low = source.lower()
    stem = Path(low).stem
    if stem.startswith("readme") or low == "readme":
        return "README"
    if stem in _DIRECTIVE_STEMS:
        return "DIRECTIVE"
    if "benchmark" in low or "/benchmarks" in low:
        return "BENCHMARK"
    if re.search(r"(^|/)tests?/", low) or "/test" in low:
        return "TEST"
    if "tutorial" in low or "example" in low or "/examples" in low:
        return "TUTORIAL"
    if re.search(r"(^|/)docs?(/|$)", low):
        return "DOCS"
    return "OTHER"


# --- discriminative error-class regexes -------------------------------------

# "the <thing> does not support/require/use <object>" — the subject is a third
# party (a runtime, library or model), not the project itself.
_FOREIGN_SUBJECT_ARTICLE_RE = re.compile(
    r"\b(?:the|a|an)\s+[a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,3}\s+"
    r"(?:does\s+not|do\s+not|doesn't|don't|never)\s+"
    r"(?:support|require|need|use|work|install|ship|include)\w*\b",
    re.IGNORECASE,
)

# "<Named> only supports <object> ... and below" — a capability statement about a
# third-party tool ("Django-Celery only supports Celery 4.0 and below").
_SUBJECT_ONLY_SUPPORT_RE = re.compile(
    r"\b[A-Z][a-zA-Z0-9_-]*(?:\s+[a-z0-9][a-z0-9_-]*){0,2}\s+"
    r"only\s+support(?:s|ed)?\b",
    re.IGNORECASE,
)

# "<Named> does not support <object>" — third-party subject, object is the
# negated thing ("Snowpark does not support Python 3.12"). Excluded when the
# subject is the project itself (passed in as ``project_name``) or the object.
_SUBJECT_NAMED_NEG_RE = re.compile(
    r"\b([A-Z][a-zA-Z0-9_-]*(?:\s+[a-z0-9][a-z0-9_-]*){0,2})\s+"
    r"(?:does\s+not|do\s+not|doesn't|don't)\s+"
    r"(?:support|require|need|use|work|install)\w*\b",
    re.IGNORECASE,
)

# Capability statements: "there is built-in support", "provides support for",
# "built-in/native support".
_CAPABILITY_RE = re.compile(
    r"\b(?:there\s+is|there's|provides?|offers?|includes?)\s+"
    r"(?:a|an|built-in|native\s+)?(?:built-in\s+|native\s+)?support\b|"
    r"\b(?:built-in|native)\s+support\b|"
    r"\bsupport\s+for\b",
    re.IGNORECASE,
)

# Performance notes ("faster/slower/less memory ... with X <version> or later").

# Configuration/server-side resolution ("resolves to", "maps to", "the default",
# "es_compat_with", "config option").
_CONFIG_RE = re.compile(
    r"\b(?:resolves?\s+to|maps?\s+to|defaults?\s+to|the\s+default|"
    r"config(?:uration)?\s+(?:option|value|field|setting)|environment\s+variable|"
    r"env\s+var|setting\b|compat\w*)\b",
    re.IGNORECASE,
)

# A dotted identifier with >=2 dots and no slash is a module reference, not a
# repo path (``airflow.providers.common.sql``).
_MODULE_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+){2,}$", re.IGNORECASE)

# Runtime/example namespaces in documentation: runtime store directories with a
# value (``variables/<name>``, ``<app>/connections/<name>``), ALL_CAPS
# bucket-like prefixes (``BUCKET_1_SRC``), config/secret/env prefixes, hidden
# cache dirs. The store-noun branch needs a *value* segment after the store
# (and no trailing slash): a bare directory claim (``deployments/templates/``)
# stays a candidate.
_RUNTIME_PREFIX_RE = re.compile(
    r"^(?:(?:[^/]+/)?(?:variables|connections|dags|pools|xcom|sensors|schedules|slots|secrets)/[^/]+$|"
    r"[A-Z0-9]+_[A-Z0-9_]*/|"
    r"(?:vars?|config|settings?|secret|secrets)[/_.-]|"
    r"\.[a-z0-9_-]*cache|\.env)",
    re.IGNORECASE,
)
_RUNTIME_CONTEXT_RE = re.compile(
    r"\b(?:the\s+default\s+value\s+is|the\s+default\s+is|default\s+value)\b",
    re.IGNORECASE,
)

# Template artifacts and template-generated documents.
_TEMPLATE_EXT_RE = re.compile(r"\.(?:jinja2?|tmpl|template|tpl|j2|in)$", re.IGNORECASE)
_TEMPLATE_DOC_RE = re.compile(r"(?:/templates?/|_template)", re.IGNORECASE)

# External link targets read as paths. The predicate layer rejects host prefixes
# with >=2 dots (``jakewheat.github.io/sql-overview``); a single-dot domain with
# a path is a residual (``modern-sql.com/standard``). Both are link targets, not
# repo paths. A single-dot prefix alone is kept out (``tests.data/`` can be a
# real directory); it needs a slash path AND an RST/markdown link marker.
_EXTERNAL_HOST_RE = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+\.[a-z]{2,}", re.IGNORECASE)
_EXTERNAL_SINGLE_DOT_RE = re.compile(r"^[a-z0-9-]+\.[a-z]{2,}/", re.IGNORECASE)
_LINK_MARKER_RE = re.compile(r"`[^`]*`_|\[[^\]]*\]\(|<https?://", re.IGNORECASE)

# Structure predicate whose object is a path-shaped token.
_STRUCTURE_PREDICATES = frozenset({"PATH_EXISTS"})

# A relative Markdown link target ("[docs](path)", "[tutorial](tutorial.md)")
# is an author-controlled reference: a stale one is a first-tier finding even
# when the path's first segment does not exist in the listing.
_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]*)\)", re.IGNORECASE)


def finding_level(
    predicate: str,
    object: str,
    raw_context: str,
    top_levels: frozenset[str],
) -> str:
    """Finding tier: anchored vs bare vs unanchored.

    Level 1 ("anchored"): the claimed path's first segment exists in the
    repository listing, or it is a relative Markdown link target. Level 2:
    bare names and paths whose first segment is absent. The reviewer's labelled
    data shows 21% strict / 29% lenient precision on level 1 vs 4% on level 2,
    so the tier is the ranking key for the triage report.
    """
    if predicate != "PATH_EXISTS":
        return "-"
    m = _MD_LINK_RE.search(raw_context)
    if m and not re.match(r"(?i)(/|https?://)", m.group(1)):
        return "anchored"
    obj = object.rstrip("/")
    if "/" not in obj:
        return "bare"
    head = obj.split("/", 1)[0]
    return "anchored" if head in top_levels else "unanchored"


@dataclass(frozen=True, slots=True)
class FindingSignals:
    """Deterministic signal vector of one resolved assertion."""

    predicate: str
    world_closed: bool
    is_negative: bool
    versioned: bool
    doc_class: str
    downgrade: frozenset[str]
    foreign_subject: bool
    capability: bool
    perf_note: bool
    config_value: bool
    module_relative: bool
    runtime_namespace: bool
    template_path: bool
    external_reference: bool
    finding_level: str
    occurrences: int
    refuting_evidence: tuple[str, ...]
    supporting_evidence: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "predicate": self.predicate,
            "world_closed": self.world_closed,
            "is_negative": self.is_negative,
            "versioned": self.versioned,
            "doc_class": self.doc_class,
            "downgrade": sorted(self.downgrade),
            "foreign_subject": self.foreign_subject,
            "capability": self.capability,
            "perf_note": self.perf_note,
            "config_value": self.config_value,
            "module_relative": self.module_relative,
            "runtime_namespace": self.runtime_namespace,
            "template_path": self.template_path,
            "external_reference": self.external_reference,
            "finding_level": self.finding_level,
            "occurrences": self.occurrences,
        }


def primary_claim(assertion: Assertion) -> PredicateClaim:
    """The claim a REFUTED finding should be reviewed by.

    For a REFUTED assertion the refuting claim(s) are listed in
    ``code_conflicts``; the first one is the finding's primary evidence. For any
    other verdict the first claim (deterministic ``claim_id`` order) is used.
    """
    if assertion.code_conflicts:
        conflict_ids = set(assertion.code_conflicts)
        for claim in assertion.claims:
            if claim.claim_id in conflict_ids:
                return claim
    return assertion.claims[0]


def compute_signals(
    assertion: Assertion,
    predicate: Predicate,
    project_name: str = "",
    top_levels: frozenset[str] = frozenset(),
) -> FindingSignals:
    """Compute the signal vector of one resolved assertion (§see module doc)."""
    claim = primary_claim(assertion)
    context = claim.context
    is_negative = bool(context.polarity & NEGATION_WORDS)
    low = claim.raw_context.lower()
    object_low = claim.object.lower()

    foreign_subject = _detect_foreign_subject(claim, is_negative, object_low, project_name)
    versioned = context.version is not None
    perf_note = bool(versioned and perf_re().search(low))
    capability = bool(_CAPABILITY_RE.search(low))

    downgrade = _downgrade_flags(claim, predicate)
    module_relative = claim.predicate_type in _STRUCTURE_PREDICATES and bool(
        _MODULE_RE.match(claim.object)
    )
    runtime_namespace = claim.predicate_type in _STRUCTURE_PREDICATES and bool(
        _RUNTIME_PREFIX_RE.match(claim.object) or _RUNTIME_CONTEXT_RE.search(low)
    )
    template_path = claim.predicate_type in _STRUCTURE_PREDICATES and bool(
        _TEMPLATE_EXT_RE.search(claim.object) or _TEMPLATE_DOC_RE.search(claim.source)
    )
    external_reference = claim.predicate_type in _STRUCTURE_PREDICATES and bool(
        _EXTERNAL_HOST_RE.match(claim.object)
        or (
            _EXTERNAL_SINGLE_DOT_RE.match(claim.object)
            and _LINK_MARKER_RE.search(claim.raw_context)
        )
    )
    config_value = bool(_CONFIG_RE.search(low))
    level = finding_level(claim.predicate_type, claim.object, claim.raw_context, top_levels)

    return FindingSignals(
        predicate=claim.predicate_type,
        world_closed="closed" in predicate.world,
        is_negative=is_negative,
        versioned=versioned,
        doc_class=classify_document(claim.source),
        downgrade=downgrade,
        foreign_subject=foreign_subject,
        capability=capability,
        perf_note=perf_note,
        config_value=config_value,
        module_relative=module_relative,
        runtime_namespace=runtime_namespace,
        template_path=template_path,
        external_reference=external_reference,
        finding_level=level,
        occurrences=len(assertion.claims),
        refuting_evidence=assertion.refuting_evidence,
        supporting_evidence=assertion.supporting_evidence,
    )


def _detect_foreign_subject(
    claim: PredicateClaim,
    is_negative: bool,
    object_low: str,
    project_name: str,
) -> bool:
    """Whether a negation/claim is asserted about a third-party subject.

    Three patterns cover the observed audit cases:

    - "the <thing> does not require <object>" — article-introduced subject;
    - "<Named> only supports <object>" — capability statement about another tool;
    - "<Named> does not support <object>" — named subject negating the object.

    The subject must not be the project itself (``project_name``) nor the claim
    object, otherwise the claim is about the documented referent and stays a
    candidate.
    """
    if _FOREIGN_SUBJECT_ARTICLE_RE.search(claim.raw_context):
        return True
    if _SUBJECT_ONLY_SUPPORT_RE.search(claim.raw_context):
        subject = _subject_of_only_support(claim.raw_context)
        if subject and subject != claim.object and subject.lower() != project_name.lower():
            return True
        return bool(is_negative and _SUBJECT_ONLY_SUPPORT_RE.search(claim.raw_context))
    if is_negative:
        for m in _SUBJECT_NAMED_NEG_RE.finditer(claim.raw_context):
            subject = m.group(1)
            if subject.lower() == object_low:
                continue
            if subject.lower() == project_name.lower():
                continue
            return True
    return False


def _subject_of_only_support(raw_context: str) -> str | None:
    m = _SUBJECT_ONLY_SUPPORT_RE.search(raw_context)
    if not m:
        return None
    return m.group(0).split(" only ")[0].strip()


def _downgrade_flags(claim: PredicateClaim, predicate: Predicate) -> frozenset[str]:
    """The predicate's own window-level downgrade signals for the claim.

    A REFUTED finding's primary claim should carry none (they downgrade to NEI),
    but they are recorded for robustness and for NEI-side analysis.
    """
    try:
        flags = predicate.flags(claim)
    except TypeError:
        return frozenset()
    return frozenset(name for name, value in flags.items() if value is True)
