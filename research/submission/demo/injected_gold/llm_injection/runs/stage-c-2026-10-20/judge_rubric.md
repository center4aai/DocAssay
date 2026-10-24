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
