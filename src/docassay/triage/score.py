"""Finding-quality score: a transparent, deterministic ranking of candidates.

The score orders REFUTED findings so a human reviews the most likely true
doc↔code contradictions first. It is a weighted sum of signals from a fixed
table (no learned weights, no LLM); the breakdown is exposed so every point is
auditable. Findings classified as systematic noise get a penalty and land below
the candidates.
"""

from __future__ import annotations

from docassay.triage import taxonomy
from docassay.triage.signals import FindingSignals

# Signal weights (transparent table). Max positive contribution:
# world_closed(3) + not_negative(2) + doc_authority(<=3) + versioned(2)
# + refuting_evidence(1) + corroborated(1) + anchored(1) = 13.
_WEIGHTS: dict[str, int] = {
    "world_closed": 3,
    "not_negative": 2,
    "versioned": 2,
    "refuting_evidence": 1,
    "corroborated": 1,
    "anchored": 1,
}
_SYSTEMATIC_PENALTY = 6
_MAX_RAW = 13


def score_finding(signals: FindingSignals, error_class: str) -> tuple[float, dict[str, int]]:
    """Score a finding in ``[0, 1]`` plus the raw weighted breakdown.

    ``error_class`` is the classifier output; systematic-noise classes are
    penalized. ``corroborated`` rewards an assertion backed by several claims
    (2+ within the same assertion), which is corroboration, not noise.
    ``anchored`` rewards a path whose first segment exists in the repository —
    the reviewer's tier-1 findings are 21% strict precise vs 4% for bare names
    , so the tier belongs in the ranking key.
    """
    breakdown: dict[str, int] = {}
    if signals.world_closed:
        breakdown["world_closed"] = _WEIGHTS["world_closed"]
    if not signals.is_negative:
        breakdown["not_negative"] = _WEIGHTS["not_negative"]
    if signals.versioned:
        breakdown["versioned"] = _WEIGHTS["versioned"]
    if signals.refuting_evidence:
        breakdown["refuting_evidence"] = _WEIGHTS["refuting_evidence"]
    if signals.occurrences >= 2:
        breakdown["corroborated"] = _WEIGHTS["corroborated"]
    if signals.finding_level == "anchored":
        breakdown["anchored"] = _WEIGHTS["anchored"]
    breakdown["doc_authority"] = taxonomy.DOC_AUTHORITY.get(signals.doc_class, 1)

    raw = sum(breakdown.values())
    if error_class in taxonomy.SYSTEMATIC_NOISE:
        raw -= _SYSTEMATIC_PENALTY
        breakdown["noise_penalty"] = -_SYSTEMATIC_PENALTY

    score = max(0.0, min(1.0, raw / _MAX_RAW))
    return score, breakdown
