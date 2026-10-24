"""Engine-free genre and document-shape acceptance check (§3.4).

Verifies: exactly three English Markdown documents, the planned document roles,
no changelog / release-notes / roadmap / proposal genre, and — when the
independent auditor's blind genre assignment is available — that the assigned
genre matches the planned genre. A mismatch is reported; it is never repaired
by the engine or by editing a document to change a claim form.

The auditor's assignment file is JSON:

    {"repos": {"contourkit": {"task_document": "tutorial",
                              "reference_document": "reference",
                              "rationale": "..."}}}

Run::

    PYTHONPATH=src uv run python .../scripts/check_genres.py \
        --corpus-dir .../synthetic-natural-c \
        --design .../runs/stage-c-2026-10-20/corpus_design.json \
        --audit .../runs/stage-c-2026-10-20/audit/genre.json \
        --out .../runs/stage-c-2026-10-20/genre_report.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FORBIDDEN_GENRES = ("changelog", "release notes", "release-notes", "roadmap", "proposal")
STOPWORDS = frozenset(
    "the a an and or of to in for on with is are was were this that these those "
    "it its as by from at be can will not you your we our".split()
)


def _english_ratio(text: str) -> float:
    words = re.findall(r"[A-Za-z]{2,}", text)
    if not words:
        return 0.0
    return len(words) / max(1, len(text.split()))


def _looks_english(text: str) -> bool:
    words = [w.lower() for w in re.findall(r"[A-Za-z]{2,}", text)]
    if len(words) < 20:
        return True
    hits = sum(1 for word in words if word in STOPWORDS)
    return hits / len(words) >= 0.15


def check_repo(root: Path, entry: dict, audit: dict) -> dict:
    violations: list[str] = []
    docs = {
        "readme": root / "README.md",
        "task_document": root / entry["task_document"]["path"],
        "reference_document": root / entry["reference_document"]["path"],
    }
    markdown = sorted(p for p in root.rglob("*.md"))
    if len(markdown) != 3:
        violations.append(f"expected 3 Markdown documents, found {len(markdown)}")
    for role, path in docs.items():
        if not path.is_file():
            violations.append(f"missing {role}: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not _looks_english(text):
            violations.append(f"{path.name}: not English-like")
        title = " ".join(re.findall(r"^#+\s+(.*)$", text, re.MULTILINE)).lower()
        name = path.name.lower()
        if any(marker in title or marker in name for marker in FORBIDDEN_GENRES):
            violations.append(f"{path.name}: forbidden document genre")
    assigned = (audit.get("repos", {}) or {}).get(entry["name"])
    genre_check = {"status": "pending" if not assigned else "checked"}
    if assigned:
        for role in ("task_document", "reference_document"):
            planned = entry[role]["genre"]
            got = assigned.get(role)
            if got != planned:
                violations.append(f"{role}: assigned genre {got!r} != planned {planned!r}")
    return {"repo": entry["name"], "ok": not violations,
            "violations": violations, "genre_check": genre_check}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--audit", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    corpus = Path(args.corpus_dir)
    design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    audit = json.loads(Path(args.audit).read_text(encoding="utf-8")) if args.audit else {}
    reports = [check_repo(corpus / entry["name"], entry, audit) for entry in design["repos"]]
    ok = all(report["ok"] for report in reports) and bool(audit)
    payload = {"ok": ok, "genre_assignment": "checked" if audit else "pending",
               "repos": reports}
    text = json.dumps(payload, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
