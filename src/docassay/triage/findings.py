"""Collect triage items (findings) from an analysis result.

One triage item per assertion: the resolved verdict plus its signal vector,
predicted error class and score. REFUTED items are the findings; SUPPORTED and
NEI items exist so the precision estimator can stratify over the whole resolved
population.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from docassay.core.pipeline import AnalysisResult
from docassay.predicates import ALL_PREDICATES
from docassay.triage import taxonomy
from docassay.triage.classifier import classify
from docassay.triage.score import score_finding
from docassay.triage.signals import compute_signals, primary_claim


@dataclass(frozen=True, slots=True)
class Finding:
    """One assertion with its triage metadata."""

    finding_id: str
    repo: str
    predicate: str
    object: str
    domain: str
    verdict: str | None
    predicted_class: str
    score: float
    score_breakdown: dict[str, int]
    signals: dict = field(default_factory=dict)
    finding_level: str = ""
    primary_source: str = ""
    primary_claim_id: str = ""
    primary_line_start: int | None = None
    primary_line_end: int | None = None
    raw_context: str = ""
    refuting_evidence: tuple[str, ...] = ()
    supporting_evidence: tuple[str, ...] = ()
    occurrences: int = 0
    code_verdict_layer: str = ""
    code_verdict_reason: str = ""

    @property
    def is_finding(self) -> bool:
        return self.verdict == "REFUTED"

    @property
    def is_resolved(self) -> bool:
        return self.verdict in {"SUPPORTED", "REFUTED"}

    def to_dict(self, *, include_score: bool = True) -> dict:
        """Plain record. ``include_score=False`` drops the triage score and
        predicted class: they do not rank true findings (precision@resolved by
        score bucket is non-monotone), so user-facing outputs omit them and
        list findings in document order; the research JSONL keeps them."""
        record = {
            "finding_id": self.finding_id,
            "repo": self.repo,
            "predicate": self.predicate,
            "object": self.object,
            "domain": self.domain,
            "verdict": self.verdict,
            "predicted_class": self.predicted_class,
            "score": round(self.score, 3),
            "score_breakdown": self.score_breakdown,
            "signals": self.signals,
            "finding_level": self.finding_level,
            "primary_source": self.primary_source,
            "primary_claim_id": self.primary_claim_id,
            "primary_line_start": self.primary_line_start,
            "primary_line_end": self.primary_line_end,
            "raw_context": self.raw_context,
            "refuting_evidence": list(self.refuting_evidence),
            "supporting_evidence": list(self.supporting_evidence),
            "occurrences": self.occurrences,
            "code_verdict_layer": self.code_verdict_layer,
            "code_verdict_reason": self.code_verdict_reason,
        }
        if not include_score:
            for key in ("predicted_class", "score", "score_breakdown"):
                record.pop(key)
        return record


def document_order(items: list[Finding]) -> list[Finding]:
    """REFUTED first, each group by document and line (no score ranking)."""
    return sorted(
        items,
        key=lambda f: (
            f.verdict != "REFUTED",
            f.primary_source,
            f.primary_line_start or 0,
            f.finding_id,
        ),
    )


def collect_findings(result: AnalysisResult, project_name: str = "") -> list[Finding]:
    """Build one triage item per assertion (deterministic, ``claim_id`` order)."""
    by_name = {plugin.name: plugin for plugin in ALL_PREDICATES}
    if not project_name:
        project_name = Path(result.project_root).name
    # First segments of every listed path — the "anchored" tier key.
    top_levels = frozenset(
        e.object.rstrip("/").split("/", 1)[0]
        for e in result.evidence
        if getattr(e, "object", "").count("/") >= 0 and "/" in getattr(e, "object", "")
    )
    items: list[Finding] = []
    for referent in result.referents:
        for assertion in referent.assertions:
            plugin = by_name.get(assertion.predicate_type)
            signals_obj = compute_signals(assertion, plugin, project_name, top_levels)
            verdict = assertion.code_verdict
            if verdict == "REFUTED":
                error_class = classify(signals_obj)
            elif verdict == "SUPPORTED":
                error_class = taxonomy.SUPPORTED
            else:
                error_class = taxonomy.ABSTAINED
            score, breakdown = score_finding(signals_obj, error_class)
            claim = primary_claim(assertion)
            items.append(
                Finding(
                    finding_id=f"{assertion.predicate_type}|{assertion.object}|{assertion.domain}",
                    repo=project_name,
                    predicate=assertion.predicate_type,
                    object=assertion.object,
                    domain=assertion.domain,
                    verdict=verdict,
                    predicted_class=error_class,
                    score=score,
                    score_breakdown=breakdown,
                    signals=signals_obj.to_dict(),
                    finding_level=signals_obj.finding_level,
                    primary_source=claim.source,
                    primary_claim_id=claim.claim_id,
                    primary_line_start=claim.line_start,
                    primary_line_end=claim.line_end,
                    raw_context=claim.raw_context,
                    refuting_evidence=assertion.refuting_evidence,
                    supporting_evidence=assertion.supporting_evidence,
                    occurrences=signals_obj.occurrences,
                    code_verdict_layer=assertion.code_verdict_layer,
                    code_verdict_reason=assertion.code_verdict_reason,
                )
            )
    items.sort(key=lambda f: (f.verdict != "REFUTED", -f.score, f.finding_id))
    return items


def findings_jsonl(items: list[Finding], output: Path) -> None:
    """Write the triage items to JSONL (one record per assertion)."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        for item in items:
            f.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")
