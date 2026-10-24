"""Validate the two-layer injection catalog and its independence invariants.

Layers
------
- ``catalog_external.json`` (layer ``external``): harvested from external
  instruments/papers; one row per ``(source, source_label)``; no de-duplication.
- ``catalog_ours.json`` (layer ``ours``): incidents from our own runs and real
  bug reports, added after the external layer is frozen.

Checks
------
- structural: unique ids, sources resolve, enums valid, evidence present;
- external layer is frozen;
- ``canonical_class`` resolves against ``normalization.json``;
- ``ours`` entries carry provenance (run/bug_report) and are not derived from the
  engine;
- the engine's predicate vocabulary does not appear as a JSON key or as an
  ``artifact_class`` (selection must not come from the engine).

Run::

    PYTHONPATH=src uv run python \
        research/submission/demo/injected_gold/scripts/validate_catalog.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ARTIFACT = SCRIPTS.parents[1]
sys.path.insert(0, str(ARTIFACT / "scripts"))
from _paths import INJECTED_GOLD, REPO_ROOT  # noqa: E402

EXTERNAL = INJECTED_GOLD / "catalog_external.json"
OURS = INJECTED_GOLD / "catalog_ours.json"
NORMALIZATION = INJECTED_GOLD / "normalization.json"

UNITS = {"repo", "method", "behavior", "doc", "process", "tool", "data", "repair", "rubric"}
SCOPES = {"in", "out", "control", "candidate"}

FALLBACK_PREDICATES = (
    "DEPENDENCY",
    "PATH_EXISTS",
    "SYMBOL_EXISTS",
    "LICENSE",
    "HAS_DOCKERFILE",
    "HAS_CI_WORKFLOW",
)


def predicate_names() -> tuple[str, ...]:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    try:
        from docassay.api import PREDICATE_NAMES  # noqa: PLC0415

        return tuple(PREDICATE_NAMES)
    except Exception:  # noqa: BLE001
        return FALLBACK_PREDICATES


def validate_entries(entries, sources, canon, errors, layer):
    seen: set[str] = set()
    for e in entries:
        eid = e.get("id")
        if not eid:
            errors.append(f"{layer}: entry without id")
            continue
        if eid in seen:
            errors.append(f"{layer}: duplicate id {eid!r}")
        seen.add(eid)
        if e.get("source") not in sources:
            errors.append(f"{layer}:{eid}: unknown source {e.get('source')!r}")
        if e.get("unit") not in UNITS:
            errors.append(f"{layer}:{eid}: bad unit {e.get('unit')!r}")
        if e.get("scope") not in SCOPES:
            errors.append(f"{layer}:{eid}: bad scope {e.get('scope')!r}")
        cc = e.get("canonical_class")
        if cc is not None and cc not in canon:
            errors.append(f"{layer}:{eid}: canonical_class {cc!r} not in normalization")
        ev = e.get("evidence")
        if not isinstance(ev, dict) or not ev.get("artifact"):
            errors.append(f"{layer}:{eid}: missing evidence.artifact")
    return seen


def main() -> int:
    errors: list[str] = []
    external = json.loads(EXTERNAL.read_text(encoding="utf-8"))
    ours = json.loads(OURS.read_text(encoding="utf-8"))
    norm = json.loads(NORMALIZATION.read_text(encoding="utf-8"))
    canon = norm.get("canonical_classes", {})

    if external.get("layer") != "external":
        errors.append("catalog_external: layer != external")
    if external.get("frozen") is not True:
        errors.append("catalog_external: not frozen")

    sources = external.get("sources", {})
    for sid, src in sources.items():
        if not src.get("ref"):
            errors.append(f"source {sid!r} has no ref")

    validate_entries(external.get("entries", []), sources, canon, errors, "external")

    # ours layer: provenance required, engine-derived selection forbidden.
    for e in ours.get("entries", []):
        eid = e.get("id")
        if not e.get("provenance"):
            errors.append(f"ours:{eid}: missing provenance")
        if e.get("origin") != "ours":
            errors.append(f"ours:{eid}: origin must be 'ours'")

    # Independence invariant: engine predicate names must not be used as keys or
    # artifact classes anywhere in either catalog. Natural-language mentions in
    # prose are allowed.
    pred_set = set(predicate_names())
    reserved = {"predicate", "target_predicate", "maps_to", "expected_predicate"}
    bad_keys: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in pred_set or k in reserved:
                    bad_keys.append(k)
                if k == "artifact_class" and v in pred_set:
                    bad_keys.append(f"artifact_class={v}")
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(external)
    walk(ours)
    for k in sorted(set(map(str, bad_keys))):
        errors.append(f"engine predicate leaked into catalog: {k!r}")

    if errors:
        print("CATALOG INVALID")
        for err in errors:
            print(f"  - {err}")
        return 1

    ext = external.get("entries", [])
    in_scope = [e for e in ext if e.get("scope") == "in"]
    out_scope = [e for e in ext if e.get("scope") == "out"]
    controls = [e for e in ext if e.get("scope") == "control"]
    candidates = [e for e in ext if e.get("scope") == "candidate"]
    print("CATALOG OK")
    print(f"  external version : {external.get('version')} (frozen={external.get('frozen')})")
    print(f"  sources          : {len(sources)}")
    print(f"  external entries : {len(ext)} "
          f"({len(in_scope)} in, {len(out_scope)} out, {len(controls)} control, "
          f"{len(candidates)} candidate)")
    print(f"  canonical classes: {len(canon)}")
    print(f"  ours entries     : {len(ours.get('entries', []))} (append-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
