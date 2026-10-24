"""Analyze a repository and print the verdict summary.

Usage::

    docassay analyze <repo_root>
    docassay analyze --format sarif --output docassay.sarif --fail-on refuted <repo_root>
    PYTHONPATH=src python -m docassay.core.analyze_repo <repo_root>
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from docassay.core.pipeline import analyze_repository, exclusion_progress


def analyze(
    root: Path,
    *,
    fmt: str = "text",
    output: Path | None = None,
    fail_on: str = "none",
) -> int:
    """Analyze ``root``; exit 1 when ``fail_on == "refuted"`` and a claim is refuted.

    ``fmt="sarif"`` writes a SARIF 2.1.0 log (to ``output`` or stdout) instead
    of the text summary.
    """
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    result = analyze_repository(root, progress=exclusion_progress)
    refuted = sum(1 for r in result.referents for a in r.assertions if a.code_verdict == "REFUTED")
    exit_code = 1 if fail_on == "refuted" and refuted else 0
    if fmt == "sarif":
        from docassay.core.sarif import to_sarif

        text = json.dumps(to_sarif(result, scan_root=root), ensure_ascii=False, indent=2)
        if output is not None:
            output.write_text(text + "\n", encoding="utf-8")
            print(f"wrote {output} ({refuted} refuted claim(s))", file=sys.stderr)
        else:
            print(text)
        return exit_code
    verdicts: Counter[str] = Counter()
    for referent in result.referents:
        for assertion in referent.assertions:
            verdicts[assertion.code_verdict or "?none"] += 1

    resolved = verdicts["SUPPORTED"] + verdicts["REFUTED"]
    total = sum(verdicts.values())
    precision_note = ""
    if resolved:
        precision_note = f"  resolved={resolved} coverage={resolved / max(total, 1):.2f}"
    print(
        f"docs={result.scanned_documents} claims={len(result.claims)} "
        f"referents={len(result.referents)} evidence={len(result.evidence)}"
    )
    print(f"code_verdicts: {dict(verdicts)}")
    if precision_note:
        print(precision_note)
    for referent in sorted(result.referents, key=lambda r: r.object):
        for assertion in referent.assertions:
            if assertion.code_verdict in {"SUPPORTED", "REFUTED"}:
                print(
                    f"  {assertion.code_verdict:>9}  {referent.object:12} "
                    f"ver={assertion.context.version or '-':10}"
                )
    if output is not None:
        print("--output applies to --format sarif only", file=sys.stderr)
    return exit_code


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <repo_root>", file=sys.stderr)
        return 2
    return analyze(Path(argv[1]))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
