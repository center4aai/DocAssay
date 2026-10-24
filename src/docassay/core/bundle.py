"""JSON bundle + Markdown export of an analysis result (stdlib only).

The bundle is the machine-readable contract between the CLI (Mode A) and the
web viewer (Mode B): one self-contained JSON document per repository with the
full referent → assertion → claim hierarchy, evidence provenance, and the
triage findings. ``to_markdown`` renders the same data as a human-readable
report, and ``to_bundle``/``to_markdown`` accept a bundle dict so a stored
bundle can be re-rendered without re-running the analysis.
"""

from __future__ import annotations

import dataclasses
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from docassay.core.pipeline import AnalysisResult, analyze_repository
from docassay.predicates import ALL_PREDICATES
from docassay.triage.aggregate import aggregate_findings, render_aggregate
from docassay.triage.findings import collect_findings, document_order

try:
    from importlib.metadata import version as _metadata_version

    TOOL_VERSION: str = _metadata_version("docassay")
except Exception:  # pragma: no cover - package not installed (PYTHONPATH dev run)
    TOOL_VERSION = "0.1.0"


def _iso_today() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _get(item: Any, name: str, default: Any = None) -> Any:
    return getattr(item, name, default)


def _context_dict(context: Any) -> dict:
    return {
        "version": context.version,
        "platform": sorted(context.platform),
        "polarity": sorted(context.polarity),
        "restriction": sorted(context.restriction),
        "time": sorted(context.time),
        "arch": sorted(context.arch),
    }


def _claim_dict(claim: Any) -> dict:
    return {
        "claim_id": claim.claim_id,
        "source": claim.source,
        "predicate_type": claim.predicate_type,
        "object": claim.object,
        "domain": claim.domain,
        "raw_context": claim.raw_context,
        "context": _context_dict(claim.context),
        "negative": claim.is_negative,
        "extraction_source": claim.extraction_source,
        "anchor_type": claim.anchor_type,
        "line_start": claim.line_start,
        "line_end": claim.line_end,
    }


def _assertion_dict(assertion: Any) -> dict:
    return {
        "context": _context_dict(assertion.context),
        "code_verdict": assertion.code_verdict,
        "code_verdict_layer": assertion.code_verdict_layer,
        "code_verdict_reason": assertion.code_verdict_reason,
        "is_code_verifiable": assertion.is_code_verifiable,
        "code_conflicts": list(assertion.code_conflicts),
        "evidence_sources": list(assertion.evidence_sources),
        "supporting_evidence": list(assertion.supporting_evidence),
        "refuting_evidence": list(assertion.refuting_evidence),
        "claims": [_claim_dict(c) for c in assertion.claims],
    }


def _referent_dict(referent: Any) -> dict:
    return {
        "predicate_type": referent.predicate_type,
        "object": referent.object,
        "domain": referent.domain,
        "assertions": [_assertion_dict(a) for a in referent.assertions],
    }


def _evidence_record(item: Any) -> dict:
    """Uniform provenance record for any evidence type.

    Symbol evidence carries ``kind``, dependency evidence ``source_type``, and
    ``source_file`` may be a declared field or a computed property (the listing
    evidence's source is the path itself).
    """
    if dataclasses.is_dataclass(item):
        data = {f.name: getattr(item, f.name) for f in dataclasses.fields(item)}
    else:
        data = dict(_get(item, "__dict__", {}) or {})
    source_file = data.get("source_file")
    if source_file is None:
        source_file = _get(item, "source_file")
    return {
        "source_file": source_file,
        "domain": data.get("domain") or "",
        "line_start": data.get("line_start"),
        "line_end": data.get("line_end"),
        "kind": data.get("kind") or data.get("source_type"),
        "snippet": data.get("snippet") or "",
    }


def _findings(result: AnalysisResult, project_name: str) -> list[dict]:
    """Triage findings as plain dicts (empty when custom predicates are used)."""
    known = {p.name for p in ALL_PREDICATES}
    if not all(a.predicate_type in known for r in result.referents for a in r.assertions):
        return []
    return [
        f.to_dict(include_score=False)
        for f in document_order(collect_findings(result, project_name))
    ]


def to_bundle(result: AnalysisResult, project_name: str = "") -> dict:
    """The JSON contract for one analyzed repository."""
    if not project_name:
        project_name = Path(result.project_root).name
    verdicts: Counter[str] = Counter()
    for referent in result.referents:
        for assertion in referent.assertions:
            verdicts[assertion.code_verdict or "?none"] += 1
    resolved = verdicts["SUPPORTED"] + verdicts["REFUTED"]
    total = max(sum(verdicts.values()), 1)
    return {
        "meta": {
            "repo": project_name,
            "project_root": result.project_root,
            "scanned_documents": result.scanned_documents,
            "created": _iso_today(),
            "tool_version": TOOL_VERSION,
            "claims": len(result.claims),
            "referents": len(result.referents),
            "evidence": len(result.evidence),
            "verdicts": dict(verdicts),
            "resolved": resolved,
            "coverage": round(resolved / total, 3),
        },
        "referents": [_referent_dict(r) for r in result.referents],
        "evidence": {e.evidence_id: _evidence_record(e) for e in result.evidence},
        "findings": _findings(result, project_name),
    }


def _fmt_counts(counts: dict) -> str:
    return " ".join(f"{k}={v}" for k, v in sorted(counts.items()))


def _ctx_line(context: dict) -> str:
    parts = []
    if context["version"]:
        parts.append(f"version={context['version']}")
    for marker in ("platform", "polarity", "restriction", "time", "arch"):
        values = context[marker]
        if values:
            parts.append(f"{marker}={'/'.join(values)}")
    return (" | " + " ".join(parts)) if parts else ""


def _finding_loc(finding: dict) -> str:
    if finding.get("primary_line_start") is not None:
        return (
            f"{finding['primary_source']}:{finding['primary_line_start']}"
            f"-{finding['primary_line_end']}"
        )
    return finding.get("primary_source") or ""


def _claim_loc(claim: dict) -> str:
    if claim.get("line_start") is not None:
        return f"{claim['source']}:{claim['line_start']}-{claim['line_end']}"
    return claim["source"]


def _evidence_loc(rec: dict, eid: str) -> str:
    source = rec.get("source_file") or eid
    start = rec.get("line_start")
    end = rec.get("line_end")
    if start is not None:
        return f"{source}:{start}-{end or start}"
    return source


def to_markdown(bundle: dict) -> str:
    """Render a bundle as a readable Markdown report."""
    meta = bundle["meta"]
    lines = [f"# {meta['repo']}", ""]
    lines.append(
        f"docs={meta['scanned_documents']} claims={meta['claims']} "
        f"referents={meta['referents']} evidence={meta['evidence']}"
    )
    lines.append(f"resolved={meta['resolved']} coverage={meta['coverage']}")
    lines.append(f"code_verdicts: {_fmt_counts(meta['verdicts'])}")
    lines.append("")

    findings = bundle["findings"]
    refuted = [f for f in findings if f.get("verdict") == "REFUTED"]
    if refuted:
        lines.append(f"## Findings (REFUTED, document order, {len(refuted)})")
        lines.append("")
        for finding in refuted:
            lines.append(
                f"- **{finding['predicate']}** {finding['object']} {_finding_loc(finding)}"
            )
            if finding.get("raw_context"):
                lines.append(f"  - raw: {finding['raw_context'][:150]}")
            if finding.get("refuting_evidence"):
                lines.append(f"  - evidence: {', '.join(finding['refuting_evidence'])}")
        lines.append("")

    lines.append("## Assertions")
    lines.append("")
    for ref in bundle["referents"]:
        title = f"### {ref['predicate_type']} {ref['object']}"
        if ref["domain"]:
            title += f" [{ref['domain']}]"
        lines.append(title)
        for assertion in ref["assertions"]:
            lines.append(
                f"- verdict **{assertion['code_verdict']}**{_ctx_line(assertion['context'])}"
            )
            if assertion["evidence_sources"]:
                lines.append(f"  - evidence sources: {', '.join(assertion['evidence_sources'])}")
            for eid in assertion["supporting_evidence"] + assertion["refuting_evidence"]:
                rec = bundle["evidence"].get(eid, {})
                loc = _evidence_loc(rec, eid)
                snippet = rec.get("snippet") or ""
                if snippet:
                    lines.append(f"  - evidence {loc}: `{snippet}`")
                else:
                    lines.append(f"  - evidence {loc}")
            for claim in assertion["claims"]:
                neg = " [NEG]" if claim["negative"] else ""
                lines.append(
                    f"  - `{claim['claim_id']}` {_claim_loc(claim)}{neg}: "
                    f"{claim['raw_context'][:200]}"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


def write_bundle(repo_root: Path, output: Path) -> int:
    """``docassay export <root> <out.json>``."""
    if not repo_root.is_dir():
        print(f"not a directory: {repo_root}", file=sys.stderr)
        return 2
    result = analyze_repository(repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(to_bundle(result), indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"wrote {output} ({result.scanned_documents} docs, "
        f"{len(result.claims)} claims, {len(result.referents)} referents)"
    )
    return 0


def write_markdown(repo_root: Path, output: Path) -> int:
    """``docassay export-md <root> <out.md>``."""
    if not repo_root.is_dir():
        print(f"not a directory: {repo_root}", file=sys.stderr)
        return 2
    result = analyze_repository(repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(to_markdown(to_bundle(result)), encoding="utf-8")
    print(f"wrote {output} ({result.scanned_documents} docs, {len(result.claims)} claims)")
    return 0


def corpus_markdown(repo_dir: Path, output: Path | None) -> int:
    """``docassay corpus-md [--dir D] [output]`` (default: ./test_repos).

    Walks the corpus (each entry may be wrapped in a ``source/`` directory,
    mirroring the internal corpus runner), collects findings across
    repositories and renders the aggregate tables. With no ``output`` the
    report is printed to stdout.
    """
    if not repo_dir.is_dir():
        print(f"not a directory: {repo_dir}", file=sys.stderr)
        return 2
    all_items: list = []
    for child in sorted(repo_dir.iterdir()):
        if not child.is_dir():
            continue
        root = child / "source"
        root = root if root.is_dir() else child
        name = root.parent.name if root.name == "source" else root.name
        result = analyze_repository(root)
        all_items.extend(collect_findings(result, project_name=name))
    agg = aggregate_findings(all_items)
    text = render_aggregate(agg)
    if output is None:
        print(text)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"wrote {output} ({len(all_items)} resolved items, {agg['repositories']} repos)")
    return 0
