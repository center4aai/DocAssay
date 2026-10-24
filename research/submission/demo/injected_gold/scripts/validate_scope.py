"""Validate the expressiveness boundary against normalization.json.

Replaces the boundary half of the retired ``validate_operators.py`` (the registry
half went with the deterministic operators). Mechanical guard:

- every class in ``boundary.json`` exists in ``normalization.json`` and is **not**
  repo-level in-scope (an in-scope class may never be filed as out of scope).

Run::

    PYTHONPATH=src uv run python .../scripts/validate_scope.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INJECTED_GOLD = SCRIPTS.parent
BOUNDARY = INJECTED_GOLD / "boundary.json"
NORMALIZATION = INJECTED_GOLD / "normalization.json"

BOUNDARY_GROUPS = (
    "out_of_scope_repo_expr",
    "out_of_scope_doc_process_data",
    "candidate_unconfirmed",
    "control_classes",
)


def main() -> int:
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    canon = json.loads(NORMALIZATION.read_text(encoding="utf-8"))["canonical_classes"]

    errors: list[str] = []
    in_scope_or_unknown: list[str] = []
    boundary_classes: list[str] = []

    for group in BOUNDARY_GROUPS:
        for name in boundary.get(group, []):
            boundary_classes.append(name)
            meta = canon.get(name)
            if meta is None:
                errors.append(f"boundary: {name!r} not in normalization")
            elif meta.get("unit") == "repo" and meta.get("scope") == "in":
                in_scope_or_unknown.append(name)
    if in_scope_or_unknown:
        errors.append(f"boundary lists in-scope repo classes: {in_scope_or_unknown}")

    repo_in_scope = {
        name
        for name, meta in canon.items()
        if meta.get("unit") == "repo" and meta.get("scope") == "in"
    }

    if errors:
        print("SCOPE INVALID")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("SCOPE OK")
    print(f"  boundary classes   : {len(boundary_classes)}")
    print(f"  repo in-scope classes: {len(repo_in_scope)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
