"""Post-freeze expressiveness coverage of the external catalog.

The external catalog is frozen first; only then do we ask which canonical
repo-level artifact classes map onto the engine's predicate vocabulary. The
out-of-scope classes and unmapped artifact classes are reported as an
expressiveness boundary. The ``ours`` layer (catalog_ours.json) is reported
separately and never mixed into the external numbers.

Run::

    PYTHONPATH=src uv run python \
        research/submission/demo/injected_gold/scripts/coverage.py [--json OUT]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ARTIFACT = SCRIPTS.parents[1]
sys.path.insert(0, str(ARTIFACT / "scripts"))
from _paths import INJECTED_GOLD, REPO_ROOT  # noqa: E402

EXTERNAL = INJECTED_GOLD / "catalog_external.json"
OURS = INJECTED_GOLD / "catalog_ours.json"
NORMALIZATION = INJECTED_GOLD / "normalization.json"

# artifact_class -> predicate the engine could emit (the measurement). Values not
# listed (endpoint, schema_field, membership, omission, example, cross_doc,
# config_key, type, value) have no direct predicate in the current vocabulary.
#
# ``referent`` maps to SYMBOL_EXISTS: a removed top-level symbol the docs still
# reference by a qualified name is an unresolved dotted claim under a project-owned
# top and is REFUTED (predicates/structure.py:414). See ../validation/SCOPE.md §5.4.
ARTIFACT_TO_PREDICATE: dict[str, str | None] = {
    "path": "PATH_EXISTS",
    "identifier": "SYMBOL_EXISTS",
    "referent": "SYMBOL_EXISTS",
    "dependency": "DEPENDENCY",
    "value": None,
    "license": "LICENSE",
    "dockerfile": "HAS_DOCKERFILE",
    "ci_workflow": "HAS_CI_WORKFLOW",
    "config_key": None,
    "endpoint": None,
    "type": None,
    "schema_field": None,
    "membership": None,
    "omission": None,
    "example": None,
    "cross_doc": None,
}


def predicate_names() -> tuple[str, ...]:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    try:
        from docassay.api import PREDICATE_NAMES  # noqa: PLC0415

        return tuple(PREDICATE_NAMES)
    except Exception:  # noqa: BLE001
        return ()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="", help="write the coverage report as JSON")
    args = ap.parse_args()

    external = json.loads(EXTERNAL.read_text(encoding="utf-8"))
    ours = json.loads(OURS.read_text(encoding="utf-8"))
    norm = json.loads(NORMALIZATION.read_text(encoding="utf-8"))
    canon = norm["canonical_classes"]

    if external.get("frozen") is not True:
        print("refusing to report coverage: external catalog is not frozen")
        return 1

    preds = predicate_names()
    unknown = {
        c: p for c, p in ARTIFACT_TO_PREDICATE.items()
        if p is not None and preds and p not in preds
    }

    repo_classes = {
        name for name, meta in canon.items()
        if meta.get("unit") == "repo" and meta.get("scope") == "in"
    }
    out_classes = {n for n, m in canon.items() if m.get("scope") == "out"}
    control_classes = {n for n, m in canon.items() if m.get("scope") == "control"}
    candidate_classes = {n for n, m in canon.items() if m.get("scope") == "candidate"}

    counts: dict[str, int] = defaultdict(int)
    for e in external.get("entries", []):
        if e.get("canonical_class"):
            counts[e["canonical_class"]] += 1

    rows = []
    for name in sorted(repo_classes):
        meta = canon[name]
        art = meta.get("artifact_class")
        rows.append({
            "canonical_class": name,
            "artifact_class": art,
            "predicate": ARTIFACT_TO_PREDICATE.get(art) or "-",
            "entries": counts.get(name, 0),
        })
    expressible = [r for r in rows if r["predicate"] != "-"]

    print("Post-freeze expressiveness coverage (external layer)")
    print(f"  engine predicates : {', '.join(preds) if preds else '(unavailable)'}")
    if unknown:
        print(f"  WARNING unknown predicate names : {unknown}")
    print()
    print(f"  {'canonical_class':26} {'artifact_class':14} {'predicate':16} entries")
    print(f"  {'-'*26} {'-'*14} {'-'*16} {'-'*7}")
    for r in rows:
        print(f"  {r['canonical_class']:26} {str(r['artifact_class']):14} "
              f"{r['predicate']:16} {r['entries']}")
    print()
    print(f"  repo-level in-scope classes       : {len(rows)}")
    print(f"  expressible by a predicate        : {len(expressible)}/{len(rows)}")
    print("  unmapped repo-level classes       : "
          + ", ".join(r['canonical_class'] for r in rows if r['predicate'] == '-'))
    print(f"  out-of-scope canonical classes    : {len(out_classes)}")
    print(f"  control canonical classes         : {len(control_classes)}")
    present_candidates = sorted(candidate_classes & set(counts)) or '(none present)'
    print(f"  candidate (unconfirmed) classes   : {present_candidates}")
    print(f"  ours layer entries (separate)     : {len(ours.get('entries', []))}")

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {
                    "predicates": list(preds),
                    "unknown_predicates": unknown,
                    "repo_level_in_scope": rows,
                    "expressible": len(expressible),
                    "total_repo_classes": len(rows),
                    "out_of_scope_classes": sorted(out_classes),
                    "control_classes": sorted(control_classes),
                    "candidate_classes_present": sorted(candidate_classes & set(counts)),
                    "ours_entries": len(ours.get("entries", [])),
                },
                indent=2, ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
