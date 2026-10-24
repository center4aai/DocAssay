"""Cross-repository aggregation of triage items.

Combines per-repository triage items into the paper's human-unit tables: a
per-predicate verdict matrix, a per-predicate noise-budget (REFUTED by predicted
class), and corpus totals. Precision pooling across repositories is handled by
``adjudicate.consolidate`` on the merged review files, not here.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from docassay.triage.findings import Finding


def aggregate_findings(items: list[Finding]) -> dict:
    """Aggregate triage items from one or more repositories."""
    by_pred: dict[str, Counter[str]] = defaultdict(Counter)
    classes_by_pred: dict[str, Counter[str]] = defaultdict(Counter)
    repos: set[str] = set()
    resolved = 0
    refuted = 0
    for item in items:
        repos.add(item.repo)
        if item.is_resolved:
            resolved += 1
        if item.is_finding:
            refuted += 1
            classes_by_pred[item.predicate][item.predicted_class] += 1
        by_pred[item.predicate][item.verdict or "NEI"] += 1

    table = {
        pred: {
            "SUPPORTED": counts["SUPPORTED"],
            "REFUTED": counts["REFUTED"],
            "NEI": counts["NEI"],
        }
        for pred, counts in sorted(by_pred.items())
    }
    classes = {pred: dict(counts) for pred, counts in sorted(classes_by_pred.items())}
    return {
        "repositories": len(repos),
        "resolved": resolved,
        "refuted": refuted,
        "by_predicate": table,
        "refuted_by_class": classes,
    }


def render_aggregate(agg: dict) -> str:
    """Render the cross-repository aggregate as Markdown."""
    lines: list[str] = []
    lines.append("# Triage aggregate")
    lines.append("")
    lines.append(
        f"repositories={agg['repositories']} resolved={agg['resolved']} "
        f"refuted={agg['refuted']}"
    )
    lines.append("")
    lines.append("## Verdicts by predicate")
    lines.append("")
    lines.append("| predicate | SUPPORTED | REFUTED | NEI |")
    lines.append("|---|---|---|---|")
    for pred, counts in agg["by_predicate"].items():
        lines.append(f"| {pred} | {counts['SUPPORTED']} | {counts['REFUTED']} | {counts['NEI']} |")
    lines.append("")
    lines.append("## REFUTED by predicted class")
    lines.append("")
    lines.append("| predicate | class | count |")
    lines.append("|---|---|---|")
    for pred, classes in agg["refuted_by_class"].items():
        for cls, n in sorted(classes.items(), key=lambda kv: -kv[1]):
            lines.append(f"| {pred} | {cls} | {n} |")
    return "\n".join(lines) + "\n"
