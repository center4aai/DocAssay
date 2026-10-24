"""Per-repository triage report: top findings + noise budget + measurement plan.

Replaces the raw resolved-assertion dump (hundreds of lines per large repo) with
a three-part surface: the top-K highest-score findings a human should review, a
noise budget that explains the REFUTED remainder by predicted error class, and
the stratified measurement request whose labels produce the precision estimate.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from docassay.core.pipeline import AnalysisResult
from docassay.triage.findings import Finding, collect_findings, document_order
from docassay.triage.sampling import build_strata, sample_from_strata


def _verdict_counts(items: list[Finding]) -> Counter[str]:
    return Counter(item.verdict or "?none" for item in items)


def _claim_line(item: Finding) -> str:
    # ``primary_claim_id`` is ``{source}:{window}:{offset}``; use the recorded
    # source directly so the window index never leaks into the path.
    return item.primary_source


def render_report(
    result: AnalysisResult,
    project_name: str = "",
    *,
    top_k: int = 15,
    sample_per_stratum: int = 5,
    seed: int = 0,
) -> str:
    """Render the triage report for one repository."""
    items = collect_findings(result, project_name)
    verdicts = _verdict_counts(items)
    resolved = verdicts["SUPPORTED"] + verdicts["REFUTED"]
    total = sum(verdicts.values())
    coverage = resolved / max(total, 1)
    findings = [f for f in items if f.is_finding]

    strata = build_strata(items)
    sample = sample_from_strata(strata, sample_per_stratum, seed)
    sample_items = [f for group in sample.values() for f in group]
    sample_items.sort(key=lambda f: f.finding_id)

    lines: list[str] = []
    lines.append(f"repo: {items[0].repo if items else project_name}")
    lines.append(
        f"docs={result.scanned_documents} claims={len(result.claims)} "
        f"referents={len(result.referents)} evidence={len(result.evidence)}"
    )
    lines.append(f"code_verdicts: {dict(verdicts)}  coverage={coverage:.2f}  resolved={resolved}")
    lines.append("")

    # Measurement plan (precision is estimated after adjudication).
    lines.append(
        f"PRECISION (stratified measurement): top-K={top_k} sample/stratum={sample_per_stratum}"
    )
    lines.append(f"  review requested: {len(sample_items)} items in {len(sample)} strata")
    for key in sorted(sample):
        n = len(sample[key])
        lines.append(f"    {key[0]:16} {key[1]:15} neg={int(key[2])}: {n}")
    lines.append("  run `docassay consolidate <review.jsonl>` after labelling")
    lines.append("")

    # Findings in document order: the triage score does not rank true findings
    # (precision@resolved by score bucket is non-monotone), so none is shown.
    ranked = document_order(findings)
    lines.append(
        f"FINDINGS (REFUTED, document order, first {min(top_k, len(ranked))} of {len(findings)}):"
    )
    for i, f in enumerate(ranked[:top_k], 1):
        loc = (
            f"{_claim_line(f)}:{f.primary_line_start}-{f.primary_line_end}"
            if f.primary_line_start is not None
            else _claim_line(f)
        )
        lines.append(f"  {i}. {f.predicate} {f.object} {loc}")
        if f.finding_level:
            lines.append(f"     tier: {f.finding_level}")
        if f.raw_context:
            lines.append(f"     raw: {f.raw_context[:150]}")
        if f.refuting_evidence:
            lines.append(f"     evidence: {', '.join(f.refuting_evidence)}")
        if f.occurrences > 1:
            lines.append(f"     cited by {f.occurrences} claims")
    lines.append("")
    return "\n".join(lines) + "\n"


def write_findings(items: list[Finding], output: Path) -> None:
    """Write all triage items to JSONL (one record per assertion)."""
    from docassay.triage.findings import findings_jsonl

    findings_jsonl(items, output)
