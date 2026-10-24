"""The human adjudication loop: review labels -> precision + confirmed findings.

``write_review`` emits a JSONL file with one record per sampled or top-ranked
finding; a human fills ``confirm`` (true = the verdict is a real doc↔code
finding) and ``actual_class`` (the observed origin, from the same taxonomy).
``consolidate`` merges one or more review files, recomputes the stratified
precision estimate and the predicted-vs-actual confusion, and returns the
confirmed-findings list used for the paper's "N confirmed findings on M
repositories" human unit.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

from docassay.triage import sampling
from docassay.triage.findings import Finding
from docassay.triage.sampling import build_strata, sample_from_strata


def write_review(
    items: list[Finding],
    output: Path,
    *,
    top_k: int = 15,
    sample_per_stratum: int = 5,
    seed: int = 0,
) -> list[Finding]:
    """Write the review JSONL: top-K findings + the stratified sample.

    The record embeds every field a reviewer needs (raw context, evidence,
    predicted class, score) plus the stratum key and two label fields. A leading
    ``_meta`` record carries the population stratum sizes (and resolved counts)
    so ``consolidate`` can estimate precision over the full population, not just
    the reviewed items. Returns the records written (excluding the meta line).
    """
    strata = build_strata(items)
    sample = sample_from_strata(strata, sample_per_stratum, seed)
    sampled: set[str] = {f.finding_id for group in sample.values() for f in group}

    findings = [f for f in items if f.is_finding]
    ranked = sorted(findings, key=lambda f: (-f.score, f.finding_id))
    reviewed = ranked[:top_k] + [f for f in findings if f.finding_id in sampled]

    # De-duplicate (a finding can be both top-K and sampled) and keep a stable
    # order: top-K first (by score), then the sample.
    seen: set[str] = set()
    records: list[Finding] = []
    for f in reviewed:
        if f.finding_id in seen:
            continue
        seen.add(f.finding_id)
        records.append(f)

    meta = {
        "_meta": True,
        "stratum_sizes": [
            [key[0], key[1], key[2], len(group)] for key, group in sorted(strata.items())
        ],
        "resolved": sum(f.is_resolved for f in items),
        "total_items": len(items),
        "top_k": top_k,
        "sample_per_stratum": sample_per_stratum,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(meta, ensure_ascii=False) + "\n")
        for f in records:
            rec = f.to_dict()
            rec["stratum"] = list(sampling.stratum_key(f))
            rec["verdict_bucket"] = sampling.verdict_bucket(f)
            rec["in_top_k"] = f in ranked[:top_k]
            rec["confirm"] = None
            rec["actual_class"] = None
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return records


def read_review(path: Path) -> tuple[dict, list[dict]]:
    """Load a review file as ``(meta, records)`` (the ``_meta`` line is separate)."""
    meta: dict = {}
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("_meta"):
                meta = rec
            else:
                records.append(rec)
    return meta, records


def consolidate(review_paths: Iterable[Path]) -> dict:
    """Merge labelled review files into precision + confirmed-findings results.

    Returns a dict with ``precision`` (estimate, CI, reviewed/total counts),
    ``by_stratum``, ``confirmed`` (list of finding dicts), ``confusion``
    (predicted vs actual class counts) and ``by_repo``.
    """
    records: list[dict] = []
    stratum_sizes: dict[tuple, int] = defaultdict(int)
    resolved = 0
    for path in review_paths:
        meta, recs = read_review(path)
        records.extend(recs)
        for pred, bucket, neg, size in meta.get("stratum_sizes", []):
            stratum_sizes[(pred, bucket, neg)] += size
        resolved += int(meta.get("resolved", 0))
    labelled = [r for r in records if r.get("confirm") is not None]

    stratum_reviewed: dict[tuple, int] = defaultdict(int)
    stratum_correct: dict[tuple, int] = defaultdict(int)
    confirmed: list[dict] = []
    confusion: Counter[tuple[str, str]] = Counter()

    for r in labelled:
        key = tuple(r["stratum"])
        stratum_reviewed[key] += 1
        if r["confirm"] is True:
            stratum_correct[key] += 1
            confirmed.append(r)
        actual = r.get("actual_class")
        if actual:
            confusion[(r["predicted_class"], actual)] += 1

    estimate, ci, reviewed, total = sampling.stratified_estimate(
        stratum_sizes, stratum_reviewed, stratum_correct
    )

    by_repo: dict[str, Counter[str]] = defaultdict(Counter)
    for r in confirmed:
        by_repo[r["repo"]][r["predicate"]] += 1

    return {
        "precision": {
            "estimate": estimate,
            "ci": ci,
            "reviewed": reviewed,
            "resolved": resolved or total,
            "labelled": len(labelled),
        },
        "by_stratum": {
            ".".join(map(str, k)): {
                "size": stratum_sizes[k],
                "reviewed": stratum_reviewed[k],
                "correct": stratum_correct[k],
            }
            for k in sorted(stratum_sizes)
        },
        "confirmed": confirmed,
        "confusion": {f"{p} -> {a}": n for (p, a), n in sorted(confusion.items())},
        "by_repo": {repo: dict(counts) for repo, counts in sorted(by_repo.items())},
    }


def render_consolidation(result: dict) -> str:
    """Render the consolidation result as text (human-units summary)."""
    p = result["precision"]
    lines: list[str] = []
    lines.append("CONSOLIDATED ADJUDICATION")
    lines.append(
        f"  precision@resolved (stratified): {p['estimate']:.2f} "
        f"[{p['ci'][0]:.2f}, {p['ci'][1]:.2f}]  (reviewed {p['reviewed']} of {p['resolved']})"
    )
    confirmed = result["confirmed"]
    lines.append(f"  confirmed findings: {len(confirmed)}")
    for repo, counts in result["by_repo"].items():
        total = sum(counts.values())
        lines.append(
            f"    {repo}: {total} confirmed"
            + ("  (" + ", ".join(f"{p}={n}" for p, n in counts.items()) + ")" if counts else "")
        )
    if result["confusion"]:
        lines.append("  predicted -> actual:")
        for pair, n in result["confusion"].items():
            lines.append(f"    {pair}: {n}")
    return "\n".join(lines) + "\n"
