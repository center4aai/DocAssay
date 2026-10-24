"""SARIF 2.1.0 export of refuted claims (pipeline integration).

One SARIF result per refuting documentation claim: ``ruleId`` is the predicate,
the location is the claim's document line, and the message names the refuted
object plus the refuting inventory lines (or the absence from the inventory).
Only ``REFUTED`` verdicts are reported: ``SUPPORTED`` needs no action and
``NEI`` is an explicit abstention, not a finding.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.bundle import TOOL_VERSION
from docassay.core.pipeline import AnalysisResult

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"

_RULE_TEXT = {
    "PATH_EXISTS": "Documented path does not exist in the repository",
    "SYMBOL_EXISTS": "Documented code symbol does not exist in the project",
    "DEPENDENCY": "Documented dependency or version contradicts the manifest",
    "LICENSE": "Documented license contradicts the repository license",
    "HAS_DOCKERFILE": "Documented Dockerfile claim contradicts the repository",
    "HAS_CI_WORKFLOW": "Documented CI workflow claim contradicts the repository",
}


def _uri_prefix(project_root: str, scan_root: Path | None) -> str:
    """Prefix turning project-relative paths into scan-root-relative URIs."""
    if scan_root is None:
        return ""
    try:
        rel = Path(project_root).resolve().relative_to(scan_root.resolve())
    except ValueError:
        return ""
    text = rel.as_posix()
    return "" if text in ("", ".") else text + "/"


def _region(line_start: int | None, line_end: int | None) -> dict:
    region: dict = {"startLine": line_start or 1}
    if line_end and line_start and line_end > line_start:
        region["endLine"] = line_end
    return region


def refuted_findings(result: AnalysisResult) -> list[dict]:
    """Every refuting claim as a plain record (predicate, object, location, evidence)."""
    evidence_by_id = {getattr(e, "evidence_id", ""): e for e in result.evidence}
    findings: list[dict] = []
    for referent in result.referents:
        for assertion in referent.assertions:
            if assertion.code_verdict != "REFUTED":
                continue
            conflicts = set(assertion.code_conflicts)
            refuting = [
                evidence_by_id[eid] for eid in assertion.refuting_evidence if eid in evidence_by_id
            ]
            for claim in assertion.claims:
                if conflicts and claim.claim_id not in conflicts:
                    continue
                findings.append(
                    {
                        "predicate": referent.predicate_type,
                        "object": referent.object,
                        "source": claim.source,
                        "line_start": claim.line_start,
                        "line_end": claim.line_end,
                        "hint": assertion.code_verdict_reason,
                        "evidence": [
                            (
                                getattr(e, "source_file", "") or "",
                                getattr(e, "line_start", None),
                            )
                            for e in refuting
                        ],
                    }
                )
    findings.sort(key=lambda f: (f["source"], f["line_start"] or 0, f["predicate"], f["object"]))
    return findings


def _message(finding: dict) -> str:
    text = f"{finding['predicate']} `{finding['object']}` is refuted by the repository"
    if finding["evidence"]:
        lines = ", ".join(
            f"{path}:{line}" if line else path for path, line in finding["evidence"] if path
        )
        text += f" (evidence: {lines})" if lines else ""
    else:
        text += " (absent from the repository inventory)"
    if finding["hint"]:
        text += f"; hint: {finding['hint']}"
    return text + "."


def to_sarif(result: AnalysisResult, scan_root: Path | None = None) -> dict:
    """The SARIF 2.1.0 log for one analysis."""
    prefix = _uri_prefix(result.project_root, scan_root)
    findings = refuted_findings(result)
    rule_ids = sorted({f["predicate"] for f in findings})
    rules = [
        {
            "id": rule_id,
            "shortDescription": {"text": _RULE_TEXT.get(rule_id, f"{rule_id} claim refuted")},
            "defaultConfiguration": {"level": "warning"},
        }
        for rule_id in rule_ids
    ]
    results = []
    for finding in findings:
        entry: dict = {
            "ruleId": finding["predicate"],
            "ruleIndex": rule_ids.index(finding["predicate"]),
            "level": "warning",
            "message": {"text": _message(finding)},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": prefix + finding["source"]},
                        "region": _region(finding["line_start"], finding["line_end"]),
                    }
                }
            ],
        }
        related = [
            {
                "id": i,
                "physicalLocation": {
                    "artifactLocation": {"uri": prefix + path},
                    "region": _region(line, line),
                },
            }
            for i, (path, line) in enumerate(finding["evidence"])
            if path and line
        ]
        if related:
            entry["relatedLocations"] = related
        results.append(entry)
    return {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "DocAssay",
                        "version": TOOL_VERSION,
                        "rules": rules,
                    }
                },
                "columnKind": "unicodeCodePoints",
                "results": results,
            }
        ],
    }
