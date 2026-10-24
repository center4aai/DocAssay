"""Triage CLI entry points: ``report``, ``review``, ``consolidate``.

``report`` runs the analysis and prints the triage report (top findings + noise
budget + measurement plan). ``review`` writes the review JSONL a human labels.
``consolidate`` merges review files into precision + confirmed-findings results.
"""

from __future__ import annotations

import sys
from pathlib import Path

from docassay.core.pipeline import analyze_repository
from docassay.triage.adjudicate import consolidate, render_consolidation, write_review
from docassay.triage.findings import collect_findings
from docassay.triage.report import render_report


def report(
    root: Path,
    *,
    top_k: int = 15,
    sample_per_stratum: int = 5,
    seed: int = 0,
    out_findings: Path | None = None,
    review_out: Path | None = None,
) -> int:
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    result = analyze_repository(root)
    print(render_report(result, top_k=top_k, sample_per_stratum=sample_per_stratum, seed=seed))
    items = collect_findings(result)
    if out_findings is not None:
        from docassay.triage.report import write_findings

        write_findings(items, out_findings)
        print(f"wrote {len(items)} triage items to {out_findings}")
    if review_out is not None:
        records = write_review(
            items, review_out, top_k=top_k, sample_per_stratum=sample_per_stratum, seed=seed
        )
        print(f"wrote review file with {len(records)} records to {review_out}")
    return 0


def review(
    root: Path,
    output: Path,
    *,
    top_k: int = 15,
    sample_per_stratum: int = 5,
    seed: int = 0,
) -> int:
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    result = analyze_repository(root)
    items = collect_findings(result)
    records = write_review(
        items, output, top_k=top_k, sample_per_stratum=sample_per_stratum, seed=seed
    )
    print(f"wrote review file with {len(records)} records to {output}")
    return 0


def run_consolidate(paths: list[Path], out: Path | None = None) -> int:
    if not paths:
        print("usage: consolidate <review.jsonl ...>", file=sys.stderr)
        return 2
    result = consolidate(paths)
    text = render_consolidation(result)
    print(text)
    if out is not None:
        out.write_text(text, encoding="utf-8")
        print(f"wrote consolidation to {out}")
    return 0
