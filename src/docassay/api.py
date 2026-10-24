"""Deterministic fact-inventory API: DocAssay as an agent's source of truth.

A thin, transport-independent surface over the analysis pipeline
(``core/pipeline.py``). It exposes what an external agent needs:

- ``build_inventory`` -- the deterministic fact inventory of a repository
  (dependencies, paths, symbols, license, infra) with provenance;
- ``verify_claim`` -- one free-form claim string against that inventory, with a
  ``SUPPORTED`` / ``REFUTED`` / ``NEI`` verdict, the abstention layer and the
  evidence lines;
- ``Oracle`` -- a lazy holder that builds the inventory once and answers
  repeated ``list_facts`` / ``lookup`` / ``verify_claim`` calls.

The verdict path is deterministic and LLM-free, exactly as in the CLI and web
UI: this module adds a query surface, not new verdict logic.
"""

from __future__ import annotations

import dataclasses
from collections import Counter
from pathlib import Path
from typing import Any

from docassay.core.domains import DomainIndex
from docassay.core.pipeline import (
    analyze_repository,
    find_project_root,
    stamp_domain,
)
from docassay.predicates import ALL_PREDICATES

# The predicate names the inventory is built from, in registration order.
PREDICATE_NAMES: tuple[str, ...] = tuple(p.name for p in ALL_PREDICATES)

# Synthetic document name used to adjudicate a single agent-supplied claim. It
# is never written to disk; the pipeline only needs a stable ``source`` label.
_AGENT_DOC = "agent_claim.md"

_FACT_FIELDS = frozenset(
    {
        "evidence_id",
        "object",
        "source_file",
        "line_start",
        "line_end",
        "kind",
        "source_type",
        "snippet",
        "domain",
    }
)


def _jsonable(value: Any) -> Any:
    """Coerce a value to something ``json.dumps`` can serialize."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return str(value)


def _fields(item: Any) -> dict[str, Any]:
    if dataclasses.is_dataclass(item):
        return {f.name: getattr(item, f.name) for f in dataclasses.fields(item)}
    return dict(getattr(item, "__dict__", {}) or {})


@dataclasses.dataclass(frozen=True, slots=True)
class Fact:
    """One deterministic fact of the inventory, with source provenance."""

    predicate: str
    object: str
    domain: str
    evidence_id: str
    source_file: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    kind: str | None = None
    snippet: str = ""
    detail: dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "predicate": self.predicate,
            "object": self.object,
            "domain": self.domain,
            "evidence_id": self.evidence_id,
            "source_file": self.source_file,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "kind": self.kind,
            "snippet": self.snippet,
            "detail": self.detail,
        }


def _fact_from_evidence(predicate: str, item: Any) -> Fact:
    data = _fields(item)
    source_file = data.get("source_file")
    if source_file is None:
        source_file = getattr(item, "source_file", None)
    detail = {k: _jsonable(v) for k, v in data.items() if k not in _FACT_FIELDS}
    return Fact(
        predicate=predicate,
        object=str(data.get("object") or getattr(item, "object", "")),
        domain=str(data.get("domain") or ""),
        evidence_id=str(data.get("evidence_id") or getattr(item, "evidence_id", "")),
        source_file=source_file,
        line_start=data.get("line_start"),
        line_end=data.get("line_end"),
        kind=data.get("kind") or data.get("source_type"),
        snippet=str(data.get("snippet") or ""),
        detail=detail,
    )


def _name_matches(needle: str, name: str) -> bool:
    """Whether a bare ``needle`` names ``name`` (exact, segment or basename)."""
    if not name:
        return False
    if name == needle:
        return True
    if name.endswith("." + needle):
        return True
    return "/" in name and name.rsplit("/", 1)[-1] == needle


@dataclasses.dataclass(frozen=True, slots=True)
class Inventory:
    """The complete fact inventory of one repository."""

    project_root: str
    facts: tuple[Fact, ...]

    @property
    def predicates(self) -> tuple[str, ...]:
        return tuple(sorted({f.predicate for f in self.facts}))

    def for_predicate(self, predicate: str) -> tuple[Fact, ...]:
        wanted = predicate.upper()
        return tuple(f for f in self.facts if f.predicate == wanted)

    def lookup(self, predicate: str, name: str) -> tuple[Fact, ...]:
        """Case-insensitive lookup of a referent by object / declared name.

        A bare name also matches a qualified or nested referent (``Klass``
        matches ``mod.Klass``; ``mod.py`` matches ``src/mod.py``).
        """
        wanted = predicate.upper()
        needle = name.strip().strip("`'\"").lower()
        if not needle:
            return ()
        hits: list[Fact] = []
        for fact in self.facts:
            if fact.predicate != wanted:
                continue
            names = {fact.object.lower(), str(fact.detail.get("qualified_name", "")).lower()}
            names.update(
                str(fact.detail.get(key, "")).lower()
                for key in ("name", "package_name", "raw_path", "path")
            )
            if any(_name_matches(needle, n) for n in names):
                hits.append(fact)
        return tuple(hits)

    def counts(self) -> dict[str, int]:
        counter = Counter(f.predicate for f in self.facts)
        return {name: counter.get(name, 0) for name in PREDICATE_NAMES}

    def metadata(self) -> dict[str, Any]:
        """Project-level ground truth: license, dependencies, infra."""
        return {
            "project_root": self.project_root,
            "fact_counts": self.counts(),
            "licenses": sorted({str(f.object) for f in self.for_predicate("LICENSE")}),
            "dependencies": sorted(
                {
                    str(f.detail.get("package_name") or f.object)
                    for f in self.for_predicate("DEPENDENCY")
                }
            ),
            "has_dockerfile": bool(self.for_predicate("HAS_DOCKERFILE")),
            "has_ci_workflow": bool(self.for_predicate("HAS_CI_WORKFLOW")),
        }


def build_inventory(repo_root: str | Path) -> Inventory:
    """Harvest the deterministic fact inventory of a repository."""
    root = find_project_root(Path(repo_root))
    domains = DomainIndex.build(root)
    facts: list[Fact] = []
    for plugin in ALL_PREDICATES:
        for item in plugin.harvest(root):
            stamped, _domain = stamp_domain(item, domains.domain_for)
            facts.append(_fact_from_evidence(plugin.name, stamped))
    return Inventory(project_root=str(root), facts=tuple(facts))


@dataclasses.dataclass(frozen=True, slots=True)
class ClaimVerdict:
    """The verdict for one referent of an agent-supplied claim."""

    predicate: str
    object: str
    domain: str
    verdict: str
    layer: str
    reason: str
    negative: bool
    supporting: tuple[str, ...]
    refuting: tuple[str, ...]
    evidence: tuple[Fact, ...]
    claims: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "predicate": self.predicate,
            "object": self.object,
            "domain": self.domain,
            "verdict": self.verdict,
            "layer": self.layer,
            "reason": self.reason,
            "negative": self.negative,
            "supporting": list(self.supporting),
            "refuting": list(self.refuting),
            "evidence": [f.to_dict() for f in self.evidence],
            "claims": list(self.claims),
        }


@dataclasses.dataclass(frozen=True, slots=True)
class VerifyResult:
    """The result of verifying one free-form claim string.

    ``status`` is the aggregate over every referent the extractor found:
    ``NO_CLAIM`` when nothing matched (the vocabulary did not recognize the
    text as a checkable claim), ``REFUTED`` if any referent is refuted,
    ``SUPPORTED`` if all are supported, otherwise ``NEI``.
    """

    claim: str
    status: str
    verdicts: tuple[ClaimVerdict, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "status": self.status,
            "verdicts": [v.to_dict() for v in self.verdicts],
        }


def _claim_record(claim: Any) -> dict[str, Any]:
    return {
        "source": claim.source,
        "line_start": claim.line_start,
        "line_end": claim.line_end,
        "raw_context": claim.raw_context,
        "object": claim.object,
        "negative": claim.is_negative,
    }


def _aggregate_status(verdicts: tuple[ClaimVerdict, ...]) -> str:
    if not verdicts:
        return "NO_CLAIM"
    outcomes = {v.verdict for v in verdicts}
    if "REFUTED" in outcomes:
        return "REFUTED"
    if outcomes <= {"SUPPORTED"}:
        return "SUPPORTED"
    return "NEI"


def verify_claim(repo_root: str | Path, text: str) -> VerifyResult:
    """Verify one free-form claim string against the repository inventory.

    The text is adjudicated through the same pipeline as a documentation file,
    using a synthetic document, so the verdict is identical to what the tool
    would report for the same sentence written in a README.
    """
    result = analyze_repository(Path(repo_root), documents=[(_AGENT_DOC, text)])
    evidence_by_id = {e.evidence_id: e for e in result.evidence}
    verdicts: list[ClaimVerdict] = []
    for referent in result.referents:
        for assertion in referent.assertions:
            if not assertion.claims:
                continue
            verdict = assertion.code_verdict or "NEI"
            evidence: list[Fact] = []
            for eid in assertion.supporting_evidence + assertion.refuting_evidence:
                item = evidence_by_id.get(eid)
                if item is not None:
                    evidence.append(_fact_from_evidence(referent.predicate_type, item))
            verdicts.append(
                ClaimVerdict(
                    predicate=referent.predicate_type,
                    object=referent.object,
                    domain=referent.domain,
                    verdict=verdict,
                    layer=assertion.code_verdict_layer,
                    reason=assertion.code_verdict_reason,
                    negative=any(c.is_negative for c in assertion.claims),
                    supporting=tuple(assertion.supporting_evidence),
                    refuting=tuple(assertion.refuting_evidence),
                    evidence=tuple(evidence),
                    claims=tuple(_claim_record(c) for c in assertion.claims),
                )
            )
    frozen = tuple(verdicts)
    return VerifyResult(claim=text, status=_aggregate_status(frozen), verdicts=frozen)


class Oracle:
    """A lazy, reusable source of truth over one repository.

    The inventory is built on first use and cached; ``refresh()`` (or
    ``refresh=True``) rebuilds it, e.g. after the working tree changes.
    """

    def __init__(self, repo_root: str | Path, *, refresh: bool = False) -> None:
        self.repo_root = Path(repo_root)
        self._builtin_refresh = refresh
        self._inventory: Inventory | None = None

    @property
    def inventory(self) -> Inventory:
        if self._inventory is None or self._builtin_refresh:
            self._inventory = build_inventory(self.repo_root)
        return self._inventory

    def refresh(self) -> Inventory:
        self._inventory = None
        return self.inventory

    def list_facts(self, predicate: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
        facts = (
            self.inventory.facts if predicate is None else self.inventory.for_predicate(predicate)
        )
        return [f.to_dict() for f in facts[: max(limit, 0)]]

    def lookup(self, predicate: str, name: str) -> list[dict[str, Any]]:
        return [f.to_dict() for f in self.inventory.lookup(predicate, name)]

    def verify_claim(self, claim: str) -> dict[str, Any]:
        return verify_claim(self.repo_root, claim).to_dict()

    def project_metadata(self) -> dict[str, Any]:
        return self.inventory.metadata()
