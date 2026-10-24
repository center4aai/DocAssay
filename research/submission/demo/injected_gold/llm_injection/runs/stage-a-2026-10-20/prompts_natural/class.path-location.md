# Injector — path-location drift

**Defect.** A document points to a file or directory as a current location, but
that file or directory is renamed or moved. The document is left unchanged, so it
now points at a location that no longer exists.

- **Artifact:** a file or directory path.
- **Direction:** change the repository tree; leave the document unchanged.

## What to look for

Choose a statement that presents a location as current — for example, "the guide
is at …", "configuration lives in …", "the example data is in …", or a command
that names a path. Do not choose a path that the document explicitly describes as
historical, illustrative, or already gone.

## The change

Rename or move the file/directory to a plausible new name or location. Keep the
same kind of artifact (a file stays a file; a directory stays a directory). The
old path must be gone after the change and the new path must exist. The document
line must still contain the **old** path.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "path-location-drift",
  "direction": "code_side",
  "file": "<old path, relative to the repository>",
  "old": "<old path, relative to the repository>",
  "new": "<new path, relative to the repository>",
  "target": "<the exact path text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the change falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-location statement>"
}
```

If no natural current-location statement exists, emit:

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
