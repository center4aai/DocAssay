# Injector — identifier drift

**Defect.** A document names a class or function as current API, but the
definition of that class or function is renamed in the code. The document is left
unchanged, so it still uses the old name.

- **Artifact:** a class or function defined in the repository.
- **Direction:** change the code; leave the document unchanged.

## What to look for

Choose a statement that presents a class or function as a current, available API.
The document may name it in any natural way a reader would use — a bare name, a
qualified name, or a call form. Do not choose a name that is already described as
deprecated, historical, or illustrative.

The mutation renames a **definition** (a top-level class or function), not a
method or an attribute. Choose a top-level definition; renaming a method or an
attribute is a different change.

## The change

Rename the definition to a plausible new name of the same style. The old name
must be absent after the change and the new name present. The file must still
parse. The document line must still use the **old** name.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "identifier-drift",
  "direction": "code_side",
  "file": "<source file that defines the symbol>",
  "old": "<the name as the document writes it>",
  "new": "<a plausible new name>",
  "symbol": "<bare symbol name>",
  "target": "<the exact name text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the change falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-API statement>"
}
```

If no natural current-API statement exists, emit:

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
