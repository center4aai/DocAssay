"""Dump all claims (with assertion verdicts) of a repository to JSONL.

Usage::

    docassay dump <repo_root> <output.jsonl>
    PYTHONPATH=src python -m docassay.core.dump_claims <repo_root> <output.jsonl>

One record per claim: the extracted context markers, the raw window, and the
verdict of the assertion the claim belongs to (code verdict + evidence).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from docassay.core.pipeline import analyze_repository, exclusion_progress


def _record(claim, assertion, evidence_by_id: dict) -> dict:
    def provenance(items):
        out: dict[str, dict] = {}
        for eid in items:
            item = evidence_by_id.get(eid)
            if item is None:
                continue
            out[eid] = {
                "source_file": getattr(item, "source_file", None),
                "line_start": getattr(item, "line_start", None),
                "line_end": getattr(item, "line_end", None),
                "snippet": getattr(item, "snippet", ""),
            }
        return out

    return {
        "claim_id": claim.claim_id,
        "predicate": claim.predicate_type,
        "object": claim.object,
        "domain": claim.domain,
        "source": claim.source,
        "raw_context": claim.raw_context,
        "extraction_source": claim.extraction_source,
        "line_start": claim.line_start,
        "line_end": claim.line_end,
        "context": {
            "version": claim.context.version,
            "platform": sorted(claim.context.platform),
            "polarity": sorted(claim.context.polarity),
            "restriction": sorted(claim.context.restriction),
            "time": sorted(claim.context.time),
            "arch": sorted(claim.context.arch),
        },
        "negative": claim.is_negative,
        "assertion_context_version": assertion.context.version,
        "code_verdict": assertion.code_verdict,
        "code_verdict_layer": assertion.code_verdict_layer,
        "code_verdict_reason": assertion.code_verdict_reason,
        "code_conflicts": list(assertion.code_conflicts),
        "supporting_evidence": list(assertion.supporting_evidence),
        "refuting_evidence": list(assertion.refuting_evidence),
        "evidence": {
            **provenance(assertion.supporting_evidence),
            **provenance(assertion.refuting_evidence),
        },
    }


def dump(repo_root: Path, output: Path) -> int:
    if not repo_root.is_dir():
        print(f"not a directory: {repo_root}", file=sys.stderr)
        return 2

    result = analyze_repository(repo_root, progress=exclusion_progress)
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence_by_id = {e.evidence_id: e for e in result.evidence}
    with output.open("w", encoding="utf-8", newline="") as f:
        for referent in result.referents:
            for assertion in referent.assertions:
                for claim in assertion.claims:
                    f.write(
                        json.dumps(
                            _record(claim, assertion, evidence_by_id),
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

    verdicts: Counter[str] = Counter()
    for referent in result.referents:
        for assertion in referent.assertions:
            verdicts[assertion.code_verdict or "?none"] += 1
    resolved = verdicts["SUPPORTED"] + verdicts["REFUTED"]
    total = sum(verdicts.values())
    print(f"wrote {len(result.claims)} claims to {output}")
    print(f"code_verdicts: {dict(verdicts)}")
    if resolved:
        print(f"resolved={resolved} coverage={resolved / max(total, 1):.2f}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <repo_root> <output.jsonl>", file=sys.stderr)
        return 2
    return dump(Path(argv[1]), Path(argv[2]))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
