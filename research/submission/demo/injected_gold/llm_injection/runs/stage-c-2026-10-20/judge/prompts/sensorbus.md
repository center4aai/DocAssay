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

{"repo": "sensorbus__external-dependency-drift__s1_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 42, "predicate": "DEPENDENCY", "object": "numpy", "reason": ""}], "new_nei": [], "new_supported": []}, "items": [{"id": "sensorbus__external-dependency-drift__s1_0::0", "repo": "sensorbus__external-dependency-drift__s1_0", "op_id": "llm.external-dependency-drift", "canonical_class": "external-dependency-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "numpy", "new": ">=999", "doc_path": "README.md", "target": "numpy>=1.24"}}]}
{"repo": "sensorbus__external-dependency-drift__s2_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 42, "predicate": "DEPENDENCY", "object": "numpy", "reason": ""}], "new_nei": [], "new_supported": []}, "items": [{"id": "sensorbus__external-dependency-drift__s2_0::0", "repo": "sensorbus__external-dependency-drift__s2_0", "op_id": "llm.external-dependency-drift", "canonical_class": "external-dependency-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "numpy", "new": ">=999", "doc_path": "README.md", "target": "numpy>=1.24"}}]}
{"repo": "sensorbus__external-dependency-drift__s3_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 42, "predicate": "DEPENDENCY", "object": "numpy", "reason": ""}], "new_nei": [], "new_supported": []}, "items": [{"id": "sensorbus__external-dependency-drift__s3_0::0", "repo": "sensorbus__external-dependency-drift__s3_0", "op_id": "llm.external-dependency-drift", "canonical_class": "external-dependency-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "numpy", "new": ">=999", "doc_path": "README.md", "target": "numpy>=1.24"}}]}
{"repo": "sensorbus__identifier-drift__s1_0", "tool_diff": {"new_refuted": [], "new_nei": [{"source": "docs/usage.md", "line": 43, "predicate": "SYMBOL_EXISTS", "object": "calibrationcurve", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "sensorbus__identifier-drift__s1_0::0", "repo": "sensorbus__identifier-drift__s1_0", "op_id": "llm.identifier-drift", "canonical_class": "identifier-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "sensorbus.calibration.CalibrationCurve", "new": "CalibrationCurveInjected", "doc_path": "README.md", "target": "CalibrationCurve"}}]}
{"repo": "sensorbus__identifier-drift__s2_0", "tool_diff": {"new_refuted": [], "new_nei": [{"source": "docs/concepts.md", "line": 88, "predicate": "SYMBOL_EXISTS", "object": "convert", "reason": "unresolved bare name"}, {"source": "docs/usage.md", "line": 146, "predicate": "SYMBOL_EXISTS", "object": "convert", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "sensorbus__identifier-drift__s2_0::0", "repo": "sensorbus__identifier-drift__s2_0", "op_id": "llm.identifier-drift", "canonical_class": "identifier-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "sensorbus.units.convert", "new": "convertInjected", "doc_path": "docs/concepts.md", "target": "convert"}}]}
{"repo": "sensorbus__identifier-drift__s3_0", "tool_diff": {"new_refuted": [], "new_nei": [{"source": "README.md", "line": 21, "predicate": "SYMBOL_EXISTS", "object": "list_devices", "reason": "unresolved bare name"}, {"source": "docs/concepts.md", "line": 115, "predicate": "SYMBOL_EXISTS", "object": "list_devices", "reason": "unresolved bare name"}, {"source": "docs/usage.md", "line": 21, "predicate": "SYMBOL_EXISTS", "object": "list_devices", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "sensorbus__identifier-drift__s3_0::0", "repo": "sensorbus__identifier-drift__s3_0", "op_id": "llm.identifier-drift", "canonical_class": "identifier-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "sensorbus.devices.list_devices", "new": "list_devicesInjected", "doc_path": "docs/concepts.md", "target": "list_devices"}}]}
{"repo": "sensorbus__path-location-drift__s1_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 72, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}, {"source": "docs/concepts.md", "line": 57, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}, {"source": "docs/usage.md", "line": 45, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}], "new_nei": [], "new_supported": []}, "items": [{"id": "sensorbus__path-location-drift__s1_0::0", "repo": "sensorbus__path-location-drift__s1_0", "op_id": "llm.path-location-drift", "canonical_class": "path-location-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "examples/curve_nitrate.csv", "new": "examples/nitrate_calibration.csv", "doc_path": "README.md", "target": "examples/curve_nitrate.csv"}}]}
{"repo": "sensorbus__path-location-drift__s2_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 72, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}, {"source": "docs/concepts.md", "line": 57, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}, {"source": "docs/usage.md", "line": 45, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}], "new_nei": [], "new_supported": []}, "items": [{"id": "sensorbus__path-location-drift__s2_0::0", "repo": "sensorbus__path-location-drift__s2_0", "op_id": "llm.path-location-drift", "canonical_class": "path-location-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "examples/curve_nitrate.csv", "new": "examples/nitrate_calibration.csv", "doc_path": "README.md", "target": "examples/curve_nitrate.csv"}}]}
{"repo": "sensorbus__path-location-drift__s3_0", "tool_diff": {"new_refuted": [{"source": "README.md", "line": 72, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}, {"source": "docs/concepts.md", "line": 57, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}, {"source": "docs/usage.md", "line": 45, "predicate": "PATH_EXISTS", "object": "examples/curve_nitrate.csv", "reason": ""}], "new_nei": [], "new_supported": []}, "items": [{"id": "sensorbus__path-location-drift__s3_0::0", "repo": "sensorbus__path-location-drift__s3_0", "op_id": "llm.path-location-drift", "canonical_class": "path-location-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "examples/curve_nitrate.csv", "new": "examples/curve_nitrate_01.csv", "doc_path": "README.md", "target": "examples/curve_nitrate.csv"}}]}
{"repo": "sensorbus__removed-referent-drift__s1_0", "tool_diff": {"new_refuted": [], "new_nei": [{"source": "docs/concepts.md", "line": 114, "predicate": "SYMBOL_EXISTS", "object": "serialdevice", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "sensorbus__removed-referent-drift__s1_0::0", "repo": "sensorbus__removed-referent-drift__s1_0", "op_id": "llm.removed-referent-drift", "canonical_class": "removed-referent-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "sensorbus.devices.SerialDevice", "new": null, "doc_path": "docs/usage.md", "target": "SerialDevice"}}]}
{"repo": "sensorbus__removed-referent-drift__s2_0", "tool_diff": {"new_refuted": [], "new_nei": [{"source": "docs/concepts.md", "line": 114, "predicate": "SYMBOL_EXISTS", "object": "serialdevice", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "sensorbus__removed-referent-drift__s2_0::0", "repo": "sensorbus__removed-referent-drift__s2_0", "op_id": "llm.removed-referent-drift", "canonical_class": "removed-referent-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "sensorbus.devices.SerialDevice", "new": null, "doc_path": "README.md", "target": "SerialDevice"}}]}
{"repo": "sensorbus__removed-referent-drift__s3_0", "tool_diff": {"new_refuted": [], "new_nei": [{"source": "README.md", "line": 21, "predicate": "SYMBOL_EXISTS", "object": "list_devices", "reason": "unresolved bare name"}, {"source": "docs/concepts.md", "line": 115, "predicate": "SYMBOL_EXISTS", "object": "list_devices", "reason": "unresolved bare name"}, {"source": "docs/usage.md", "line": 21, "predicate": "SYMBOL_EXISTS", "object": "list_devices", "reason": "unresolved bare name"}], "new_supported": []}, "items": [{"id": "sensorbus__removed-referent-drift__s3_0::0", "repo": "sensorbus__removed-referent-drift__s3_0", "op_id": "llm.removed-referent-drift", "canonical_class": "removed-referent-drift", "expected_outcome": "refuted", "control": "none", "injection": {"direction": null, "artifact": "sensorbus.devices.list_devices", "new": null, "doc_path": "docs/concepts.md", "target": "list_devices"}}]}

Return ONLY a JSON object of the form {"verdicts":[{"id":"...","reaction":"refuted|nei|none","reason":"..."}]} covering every item id exactly once. Do not add commentary.