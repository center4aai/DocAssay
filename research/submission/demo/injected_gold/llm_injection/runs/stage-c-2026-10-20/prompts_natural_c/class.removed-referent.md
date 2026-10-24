# Injector — removed-referent drift

**Defect.** A document names a class or function as current API, but that
definition is deleted from the code. The document is left unchanged, so it names
something that no longer exists.

- **Artifact:** a class or function defined in the repository.
- **Direction:** change the code; leave the document unchanged.

## What to look for

Choose a statement that presents a class or function as current, available API.
Do not choose a name that is already described as deprecated, historical, or
illustrative.

The mutation removes a **definition** (a top-level class or function), not a
method or an attribute. Prefer a definition that is not imported or called
elsewhere, so the rest of the tree still parses after the removal.

## The change

Delete the definition as a whole block. The old name must be absent after the
change and the file must still parse. The document line must still name the
**deleted** symbol.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "removed-referent-drift",
  "direction": "code_side",
  "file": "<source file that defines the symbol>",
  "old": "<the name as the document writes it>",
  "new": null,
  "symbol": "<bare symbol name>",
  "target": "<the exact name text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the removal falsifies>",
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
