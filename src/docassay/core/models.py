"""Internal typed models for the method-v2 claim/assertion layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from docassay.vocabularies.markers import NEGATION_WORDS

CodeVerdict = Literal["SUPPORTED", "REFUTED", "NEI"]


@dataclass(frozen=True, slots=True)
class Context:
    """Structured context of a claim: the filled context markers.

    Markers follow the pool in §5.1; which markers a predicate uses is fixed in
    §5.2. An empty field means the marker was not found in the window — by §5.3
    an empty field is *not* a contradiction with a filled one.
    """

    version: str | None = None
    platform: frozenset[str] = frozenset()
    polarity: frozenset[str] = frozenset()
    restriction: frozenset[str] = frozenset()
    time: frozenset[str] = frozenset()
    arch: frozenset[str] = frozenset()

    def merged(self, other: Context) -> Context:
        """Union of two compatible contexts (both filled → must agree).

        Callers guarantee compatibility (no filled marker differs); this helper
        keeps the invariant that the union is lossless.
        """
        return Context(
            version=self.version if self.version is not None else other.version,
            platform=self.platform | other.platform,
            polarity=self.polarity | other.polarity,
            restriction=self.restriction | other.restriction,
            time=self.time | other.time,
            arch=self.arch | other.arch,
        )

    def conflicts_with(self, other: Context) -> bool:
        """§5.3 equality: false iff some marker is filled with different values.

        An empty field never contradicts a filled one.
        """
        if self.version is not None and other.version is not None and self.version != other.version:
            return True
        for marker in ("platform", "polarity", "restriction", "time", "arch"):
            a = getattr(self, marker)
            b = getattr(other, marker)
            if a and b and a != b:
                return True
        return False


@dataclass(frozen=True, slots=True)
class PredicateClaim:
    """An atomic claim: one predicate + one object + context."""

    claim_id: str
    source: str
    predicate_type: str
    object: str
    raw_context: str
    context: Context
    domain: str = ""
    extraction_source: Literal["regex", "llm"] = "regex"
    anchor_type: str = ""
    line_start: int | None = None
    line_end: int | None = None
    # The anchor token exactly as written in the document (original case), for
    # case-fidelity resolution. Empty when the predicate does
    # not care about case (dependency, version, license, infra).
    raw_object: str = ""

    @property
    def is_negative(self) -> bool:
        """Negation is fixed by the `polarity` context marker (§5.1, §6.1).

        `restriction` words ("only", "except", …) qualify the referent without
        negating it and never make a claim negative.
        """
        return bool(self.context.polarity & NEGATION_WORDS)


@dataclass(frozen=True, slots=True)
class Assertion:
    """A context-cluster inside one referent; the unit of code verdict (§2, §6).

    All claims of a referent ``(predicate_type, object, domain)`` whose filled
    context markers agree (§5.3) cluster into one assertion, so an assertion is
    identified by the referent key plus its merged context. The doc↔code verdict
    lives here.
    """

    predicate_type: str
    object: str
    domain: str
    claims: tuple[PredicateClaim, ...]
    context: Context
    evidence_sources: tuple[str, ...] = ()
    is_code_verifiable: bool = True
    code_verdict: CodeVerdict | None = None
    # Epistemic reason behind a NEI verdict (3-layer model): WORLD /
    # DECIDABILITY / CLAIM_GATE, with a free-text reason. Empty for
    # SUPPORTED/REFUTED and for non-NEI outcomes.
    code_verdict_layer: str = ""
    code_verdict_reason: str = ""
    code_conflicts: tuple[str, ...] = ()
    supporting_evidence: tuple[str, ...] = ()
    refuting_evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReferentResult:
    """All claims sharing one referent key.

    The referent key is ``(predicate_type, object, domain)``; the assertions are
    the context-clusters of those claims.
    """

    predicate_type: str
    object: str
    domain: str
    assertions: tuple[Assertion, ...]
