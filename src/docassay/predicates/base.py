"""The predicate plugin contract (§3, §4, §6).

A ``Predicate`` bundles everything needed to analyze one claim predicate: how
to extract claims from a document (``scan``), how to harvest the code-side
evidence inventory (``harvest``), how to adjudicate one claim against that
inventory (``match``), and which window-level downgrade signals exist
(``flags``). The pipeline is generic over the plugin list — adding a predicate
is writing a module and registering one ``Predicate`` instance.

``domain_scoped_evidence`` marks predicates whose evidence world is per-domain:
each manifest-bearing directory is its own CLOSED inventory (the DEPENDENCY
world). Whole-tree worlds (the listing, the project AST) leave it ``False`` and
match against the merged inventory. ``extend_with_declared`` marks predicates
whose scan anchor set is extended at runtime with the project's own harvested
declarations (DEPENDENCY): any dependency the tool harvests becomes anchorable.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from docassay.core.models import PredicateClaim


class Verdict(NamedTuple):
    """A per-claim code verdict with its epistemic reason (3-layer model).

    Three orthogonal layers drive a ``NEI`` (the three-layer verdict model):

    - ``WORLD`` — inventory not complete for this fact (OPEN world / ``world_holds``
      false): absence is ignorance, not contradiction.
    - ``DECIDABILITY`` — the claim is genuine and current-state, but the evidence
      cannot decide it (undecidable version range, wildcard, over-spec pin).
    - ``CLAIM_GATE`` — the mention is not a current-state claim at all (genre /
      subject / construction / form). Phase 2 moves these into a ``gate()`` that
      prevents claim formation; for now they surface here as a forward-looking
      reason.

    ``layer`` is empty for ``SUPPORTED``/``REFUTED``; ``reason`` may carry a
    hint for them (``did you mean: …``, ``case differs: …``).
    """

    outcome: str
    supporting: tuple[str, ...] = ()
    refuting: tuple[str, ...] = ()
    layer: str = ""
    reason: str = ""


def _default_evidence_sources(items: list) -> tuple[str, ...]:
    return tuple(sorted({getattr(i, "source_file", "") for i in items} - {""}))


@dataclass(frozen=True)
class GateResult:
    """Whether a scan-produced mention is a current-state claim at all.

    ``ok=False`` marks the mention a non-claim by construction (genre /
    construction / form, the three-layer verdict model Phase 2): it never
    enters the verdict layer — like the §1 non-extraction exclusions, it does
    not produce a NEI verdict and does not form a referent/assertion.
    ``reason`` is the human-readable gate signal (e.g. "historical mention").
    """

    ok: bool = True
    reason: str = ""


@dataclass(frozen=True)
class Predicate:
    """One adjudicated claim predicate: extraction + evidence + matching."""

    name: str
    world: str
    scan: Callable[..., list[PredicateClaim]]
    harvest: Callable[[Path], list]
    match: Callable[..., Verdict]
    flags: Callable[[PredicateClaim], dict[str, bool]] = lambda claim: {}
    gate: Callable[[PredicateClaim], GateResult] = lambda claim: GateResult()
    evidence_sources: Callable[[list], tuple[str, ...]] = _default_evidence_sources
    world_holds: Callable[[Path], bool] = lambda project_root: True
    domain_scoped_evidence: bool = False
    extend_with_declared: bool = False
    # When ``extend_with_declared`` is set, only evidence for which this returns
    # ``True`` extends the scan anchor vocabulary. Used to keep transitive
    # evidence (lock-file resolved packages) out of the anchor set.
    anchor_evidence: Callable[[object], bool] = lambda item: True


# Literal CLAIM_GATE reasons for the per-mention downgrade flags, in priority
# order: the reason names the cue that fired, not a generic label.
_MENTION_FLAG_REASONS: tuple[tuple[str, str], ...] = (
    ("historical", "historical mention"),
    ("instructional", "instruction"),
    ("exemplary", "example"),
    ("user_config", "user runtime config"),
    ("reader_space", "reader's own file"),
    ("reader_file", "reader's own file"),
    ("generated", "generated file"),
)


def mention_gate_reason(**flags: bool) -> str:
    """The reason for the first downgrade flag that is set, or ``""``."""
    return next((reason for name, reason in _MENTION_FLAG_REASONS if flags.get(name)), "")


def case_hint(claimed: str, actual_spellings: list[str], separators: str = "/.") -> str:
    """``"case differs: <tree spelling>"`` when a match holds only case-insensitively.

    ``claimed`` is the document's spelling; ``actual_spellings`` are the
    original-case names of the matched inventory entries. The claim may be a
    segment-aligned suffix of an entry (``Guide.md`` of ``docs/Guide.md``). No
    hint when any entry matches with the exact case.
    """
    claim = claimed.strip().strip("`'\"").removesuffix("()").strip("/")
    if not claim:
        return ""
    folded = claim.lower()
    differing = ""
    for spelling in actual_spellings:
        actual = spelling.strip("/")
        if not actual.lower().endswith(folded):
            continue
        head = actual[: len(actual) - len(claim)]
        if head and head[-1] not in separators:
            continue
        if actual.endswith(claim):
            return ""
        if actual == actual.lower() and claim != folded:
            # A lowercased inventory key (a re-export alias) is not the tree's
            # spelling; it cannot tell the reader anything.
            continue
        differing = differing or actual
    return f"case differs: {differing}" if differing else ""
