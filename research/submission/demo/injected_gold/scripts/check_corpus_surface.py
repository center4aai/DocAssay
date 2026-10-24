"""Engine-free spec-surface check for the Stage C corpus (§2.4, §3.4).

Checks, per repository: required spec keys, forbidden evaluation-shaped
surfaces (``endpoints``, ``schema_fields``, ``enum_members``), ``config_keys``
only where the frozen design allows them, exactly three documents matching the
design, and the optional-surface counts. It never imports ``docassay`` and
never rejects a repository on engine output.

Run::

    PYTHONPATH=src uv run python .../scripts/check_corpus_surface.py \
        --corpus-dir .../synthetic-natural-c \
        --design .../runs/stage-c-2026-10-20/corpus_design.json \
        --out .../runs/stage-c-2026-10-20/surface_report.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_KEYS = ("project", "dependencies", "modules", "docs")
FORBIDDEN_KEYS = ("endpoints", "schema_fields", "enum_members")
OPTIONAL_KEYS = ("config_keys", "example_commands", "paths", "data_files")


def check_repo(root: Path, design: dict) -> dict:
    spec_path = root / "spec.json"
    violations: list[str] = []
    if not spec_path.is_file():
        return {"repo": root.name, "ok": False, "violations": ["missing spec.json"]}
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"repo": root.name, "ok": False, "violations": [f"invalid spec.json: {exc}"]}
    for key in REQUIRED_KEYS:
        if key not in spec:
            violations.append(f"missing required key: {key}")
    for key in FORBIDDEN_KEYS:
        if spec.get(key):
            violations.append(f"forbidden surface present: {key}")
    if spec.get("config_keys") and not design.get("config_keys_allowed"):
        violations.append("config_keys present but not allowed for this repo")
    docs = [d.get("path") for d in spec.get("docs", []) if isinstance(d, dict)]
    expected = ["README.md", design["task_document"]["path"], design["reference_document"]["path"]]
    if sorted(docs) != sorted(expected):
        violations.append(f"docs {docs} != expected {expected}")
    for path in expected:
        if not (root / path).is_file():
            violations.append(f"document not materialised: {path}")
    counts = {key: len(spec.get(key) or []) for key in OPTIONAL_KEYS}
    return {
        "repo": root.name,
        "ok": not violations,
        "violations": violations,
        "optional_surface_counts": counts,
        "module_count": len(spec.get("modules", [])),
        "dependency_count": len(spec.get("dependencies", [])),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    corpus = Path(args.corpus_dir)
    design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    reports = []
    for entry in design["repos"]:
        root = corpus / entry["name"]
        reports.append(check_repo(root, entry))
    ok = all(report["ok"] for report in reports)
    payload = {"ok": ok, "repos": reports}
    text = json.dumps(payload, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
