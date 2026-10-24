# Injector — external-dependency drift

**Defect.** A document presents a third-party dependency as a current
requirement, but the project manifest is changed so that the declared dependency
no longer satisfies the documented requirement, or the dependency is removed
while the document still names it.

- **Artifact:** a dependency declared in the project manifest.
- **Direction:** change the manifest; leave the document unchanged.

## What to look for

Choose a statement that presents a dependency as a current requirement. If the
document states a version requirement, use the constraint form of the mutation.
If it only names the dependency as something the project uses, use the removal
form.

The dependency must be declared in the project's own manifest
(`pyproject.toml`, `setup.cfg`, `setup.py`, or `requirements*.txt`), because the
mutation edits that manifest.

## The change

- **Constraint form:** change the manifest constraint to a clearly
  non-overlapping bound (for example `>=999`). The new constraint must be
  parseable and must not intersect the requirement stated in the document.
- **Removal form:** remove the dependency from the manifest while the document
  still names it. Use this form only when the document does not state a
  constraint.

The document line must still name the dependency.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "external-dependency-drift",
  "direction": "code_side",
  "file": "<manifest file>",
  "old": "<the existing constraint, or the dependency name for removal>",
  "new": "<the new constraint, or null for removal>",
  "symbol": "<normalized dependency name>",
  "target": "<the exact dependency text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the change falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-requirement statement>"
}
```

If no natural current-requirement statement exists, emit:

```json
{"injectable": false, "reason": "<short reason>"}
```

## Repository inventory

{{REPO_INVENTORY}}

## Document excerpts

{{DOC_EXCERPTS}}

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

{{EXEMPLARS}}
