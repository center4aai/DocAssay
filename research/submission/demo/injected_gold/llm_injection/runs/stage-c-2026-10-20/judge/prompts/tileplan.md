# Judge rubric — Stage C (frozen at S0)

Two independent adjudicators read the tool's baseline→injected reaction diff for
one bundle and decide the **reaction**, never whether the injection is a real
defect (the injector's verifier does that).

## Inputs

- the frozen `manifest.jsonl` entry for the bundle (`target`, `old`, `new`,
  `symbol`, `doc_path`, `line`, `class`);
- the baseline claim dump and the injected claim dump for the same snapshot.

Judges do not see the other judge's verdict, the metrics, or the annotation
sheet.

## Decision order

1. **`refuted`** — a *new* claim in the injected tree, whose referent is the
   injected artifact, returns `REFUTED`. "New" means the same
   `(doc_path, line, predicate, referent)` is absent from the baseline or its
   verdict changed to `REFUTED`.
2. **`nei`** — no new same-artifact `REFUTED`, and at least one same-artifact
   claim is formed and returns `NEI`. Record the layer and the verbatim reason.
3. **`none`** — no same-artifact `REFUTED` and no same-artifact `NEI`. Sub-flag
   in this order:
   - `supported`: a same-artifact claim is formed and returns `SUPPORTED`;
   - `other_referent`: a claim covers the recorded target line at a different
     referent;
   - `no_claim`: neither.

## Artifact matching

- **path** — normalized inventory path equality.
- **dependency** — normalized package name (`_`/`.` → `-`, case-folded) plus the
  requirement relation.
- **identifier / removed-referent** — project-qualified name equality. A bare
  mention elsewhere with the same last segment is not the same artifact. A
  section-qualified `M.T` is the same artifact as the injected `M.T`.

## Target-line and cross-mention

Record, independently of the artifact outcome:

- `target_line_status`: `refuted` if a new same-artifact `REFUTED` exists on the
  recorded `doc_path` and line; else `nei` if a same-artifact claim on that line
  abstains; else `none` with the same sub-flags.
- `attribution`: `target_line` (only on-line), `other_mention` (only elsewhere),
  `both`.

Detection is **not** bound to the recorded line: a refutation found anywhere in
the diff is credited, but the target-line status is reported separately. Do not
credit a finding at an unrelated referent.

## Disagreement

The deterministic diff judge and the LLM judge are compared per bundle. Report
agreement. Resolve disagreements manually against the two claim dumps and log
the resolution; never silently pick one.


## Items

{"repo": "tileplan__identifier-drift__s1_0", "tool_diff": {"new_refuted": [{"source": "docs/api.md", "line": 62, "predicate": "SYMBOL_EXISTS", "object": "tileplan.extent.merge_extents", "reason": ""}], "new_nei": [{"source": "docs/usage.md", "line": 28, "predicate": "SYMBOL_EXISTS", "object": "merge_extents", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "tileplan__identifier-drift__s1_0::0", "repo": "tileplan__identifier-drift__s1_0", "op_id": "llm.identifier-drift", "canonical_class": "identifier-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "tileplan.extent.merge_extents", "new": "merge_extentsInjected", "doc_path": "README.md", "target": "merge_extents"}}]}
{"repo": "tileplan__identifier-drift__s2_0", "tool_diff": {"new_refuted": [{"source": "docs/api.md", "line": 77, "predicate": "SYMBOL_EXISTS", "object": "tileplan.zoom.closest_zoom", "reason": ""}], "new_nei": [], "new_supported": []}, "items": [{"id": "tileplan__identifier-drift__s2_0::0", "repo": "tileplan__identifier-drift__s2_0", "op_id": "llm.identifier-drift", "canonical_class": "identifier-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "tileplan.zoom.closest_zoom", "new": "closest_zoomInjected", "doc_path": "docs/api.md", "target": "closest_zoom"}}]}
{"repo": "tileplan__identifier-drift__s3_0", "tool_diff": {"new_refuted": [{"source": "docs/api.md", "line": 62, "predicate": "SYMBOL_EXISTS", "object": "tileplan.extent.merge_extents", "reason": ""}], "new_nei": [{"source": "docs/usage.md", "line": 28, "predicate": "SYMBOL_EXISTS", "object": "merge_extents", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "tileplan__identifier-drift__s3_0::0", "repo": "tileplan__identifier-drift__s3_0", "op_id": "llm.identifier-drift", "canonical_class": "identifier-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "tileplan.extent.merge_extents", "new": "merge_extentsInjected", "doc_path": "README.md", "target": "merge_extents"}}]}
{"repo": "tileplan__path-location-drift__s1_0", "tool_diff": {"new_refuted": [], "new_nei": [], "new_supported": []}, "items": [{"id": "tileplan__path-location-drift__s1_0::0", "repo": "tileplan__path-location-drift__s1_0", "op_id": "llm.path-location-drift", "canonical_class": "path-location-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "examples/bay_area.geojson", "new": "examples/bay_area_view.geojson", "doc_path": "README.md", "target": "examples/bay_area.geojson"}}]}
{"repo": "tileplan__path-location-drift__s2_0", "tool_diff": {"new_refuted": [], "new_nei": [], "new_supported": []}, "items": [{"id": "tileplan__path-location-drift__s2_0::0", "repo": "tileplan__path-location-drift__s2_0", "op_id": "llm.path-location-drift", "canonical_class": "path-location-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "examples/bay_area.geojson", "new": "examples/bay_area_view.geojson", "doc_path": "README.md", "target": "examples/bay_area.geojson"}}]}
{"repo": "tileplan__path-location-drift__s3_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 109, "predicate": "PATH_EXISTS", "object": "docs/usage.md", "reason": ""}], "new_nei": [{"source": "docs/walkthrough.md", "line": 38, "predicate": "DEPENDENCY", "object": "build", "reason": "undeclared (open by transitivity)"}, {"source": "docs/walkthrough.md", "line": 60, "predicate": "DEPENDENCY", "object": "build", "reason": "undeclared (open by transitivity)"}, {"source": "docs/walkthrough.md", "line": 137, "predicate": "DEPENDENCY", "object": "build", "reason": "undeclared (open by transitivity)"}, {"source": "docs/walkthrough.md", "line": 4, "predicate": "DEPENDENCY", "object": "constantly", "reason": "undeclared (open by transitivity)"}, {"source": "docs/walkthrough.md", "line": 63, "predicate": "DEPENDENCY", "object": "construct", "reason": "undeclared (open by transitivity)"}, {"source": "docs/walkthrough.md", "line": 28, "predicate": "SYMBOL_EXISTS", "object": "featurecollection", "reason": "unresolved bare name"}], "new_supported": [{"source": "docs/walkthrough.md", "line": 145, "predicate": "PATH_EXISTS", "object": "api.md", "reason": ""}, {"source": "docs/walkthrough.md", "line": 145, "predicate": "PATH_EXISTS", "object": "docs/api.md", "reason": ""}, {"source": "docs/walkthrough.md", "line": 144, "predicate": "PATH_EXISTS", "object": "readme.md", "reason": ""}, {"source": "docs/walkthrough.md", "line": 95, "predicate": "SYMBOL_EXISTS", "object": "descendants", "reason": ""}, {"source": "docs/walkthrough.md", "line": 11, "predicate": "SYMBOL_EXISTS", "object": "extent", "reason": ""}, {"source": "docs/walkthrough.md", "line": 13, "predicate": "SYMBOL_EXISTS", "object": "extent", "reason": ""}, {"source": "docs/walkthrough.md", "line": 112, "predicate": "SYMBOL_EXISTS", "object": "from_quadkey", "reason": ""}, {"source": "docs/walkthrough.md", "line": 28, "predicate": "SYMBOL_EXISTS", "object": "merge_extents", "reason": ""}, {"source": "docs/walkthrough.md", "line": 97, "predicate": "SYMBOL_EXISTS", "object": "parent", "reason": ""}, {"source": "docs/walkthrough.md", "line": 26, "predicate": "SYMBOL_EXISTS", "object": "tile_extent", "reason": ""}, {"source": "docs/walkthrough.md", "line": 127, "predicate": "SYMBOL_EXISTS", "object": "tile_from_lonlat", "reason": ""}, {"source": "docs/walkthrough.md", "line": 118, "predicate": "SYMBOL_EXISTS", "object": "tileplan.coords", "reason": ""}, {"source": "docs/walkthrough.md", "line": 111, "predicate": "SYMBOL_EXISTS", "object": "to_quadkey", "reason": ""}]}, "items": [{"id": "tileplan__path-location-drift__s3_0::0", "repo": "tileplan__path-location-drift__s3_0", "op_id": "llm.path-location-drift", "canonical_class": "path-location-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "docs/usage.md", "new": "docs/walkthrough.md", "doc_path": "README.md", "target": "docs/usage.md"}}]}
{"repo": "tileplan__removed-referent-drift__s1_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 96, "predicate": "SYMBOL_EXISTS", "object": "tileplan.cover.coveroptions", "reason": ""}, {"source": "docs/api.md", "line": 114, "predicate": "SYMBOL_EXISTS", "object": "tileplan.cover.coveroptions", "reason": ""}], "new_nei": [{"source": "docs/api.md", "line": 116, "predicate": "SYMBOL_EXISTS", "object": "coveroptions", "reason": "unresolved bare name"}, {"source": "docs/api.md", "line": 128, "predicate": "SYMBOL_EXISTS", "object": "coveroptions", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "tileplan__removed-referent-drift__s1_0::0", "repo": "tileplan__removed-referent-drift__s1_0", "op_id": "llm.removed-referent-drift", "canonical_class": "removed-referent-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "tileplan.cover.CoverOptions", "new": null, "doc_path": "docs/api.md", "target": "CoverOptions"}}]}
{"repo": "tileplan__removed-referent-drift__s2_0", "tool_diff": {"new_refuted": [{"source": "docs/api.md", "line": 108, "predicate": "SYMBOL_EXISTS", "object": "tileplan.quadkey.from_quadkey", "reason": ""}], "new_nei": [{"source": "docs/usage.md", "line": 112, "predicate": "SYMBOL_EXISTS", "object": "from_quadkey", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "tileplan__removed-referent-drift__s2_0::0", "repo": "tileplan__removed-referent-drift__s2_0", "op_id": "llm.removed-referent-drift", "canonical_class": "removed-referent-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "tileplan.quadkey.from_quadkey", "new": null, "doc_path": "docs/api.md", "target": "from_quadkey"}}]}
{"repo": "tileplan__removed-referent-drift__s3_0", "tool_diff": {"new_refuted": [{"source": "docs/api.md", "line": 108, "predicate": "SYMBOL_EXISTS", "object": "tileplan.quadkey.from_quadkey", "reason": ""}], "new_nei": [{"source": "docs/usage.md", "line": 112, "predicate": "SYMBOL_EXISTS", "object": "from_quadkey", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "tileplan__removed-referent-drift__s3_0::0", "repo": "tileplan__removed-referent-drift__s3_0", "op_id": "llm.removed-referent-drift", "canonical_class": "removed-referent-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "tileplan.quadkey.from_quadkey", "new": null, "doc_path": "docs/api.md", "target": "from_quadkey()"}}]}

Return ONLY a JSON object of the form {"verdicts":[{"id":"...","reaction":"refuted|nei|none","reason":"..."}]} covering every item id exactly once. Do not add commentary.