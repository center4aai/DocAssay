# Injector — `path-location-drift` (code-side path drift)

**Defect.** A repository file or directory that a document references **by path**
is renamed or moved, so the path the documentation names no longer exists in the
tree. The document still points at the old location.

- **Artifact:** a file path (never a symbol).
- **Direction:** mutate the **code/tree**; the document is left unchanged and
  becomes stale.
- **Dispatch kind:** `path_rename` (harness applies `rename` on disk).

## What the exemplars anchor

Choose a target the same *way* the real incidents do: a path a document treats as
a current, existing location (a linked file, a config example, a module path in a
command), not a path that is already described as historical or illustrative.

## Target-selection rules

1. The path must be a **file** that actually exists in the repository inventory below.
2. It must be named in a document line in the excerpts below (the `doc_path` and
   `doc_line_text` you report).
3. Prefer a file with a **unique basename** so the mention resolves unambiguously.
4. Do not target a document that is itself excluded from analysis (changelogs,
   release notes, translations); pick a README- or guide-like document.

## Required mutation

Rename the file to a minimal, plausible new name (e.g. append `_v2`, change a
word), keeping the same extension and directory unless the incident pattern is a
move. The old path must be gone and the new path present after the change. The
named document line still contains the **old** path token.

Report `target` as the exact path token as written on the doc line.

## Output skeleton (fill and emit as JSON only)

```json
{
  "injectable": true,
  "drift_type": "path-location-drift",
  "artifact_class": "path",
  "direction": "code_side",
  "kind": "path_rename",
  "file": "<old path, relative>",
  "old": "<old path, relative>",
  "new": "<new path, relative>",
  "target": "<path token as written in the doc line>",
  "doc_path": "<document file>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the claim the document makes that the rename falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one or two sentences: which exemplar pattern you followed>"
}
```

## Repository inventory

{{REPO_INVENTORY}}

## Document excerpts

{{DOC_EXCERPTS}}

## Examples (few-shot)

Real, human-triaged instances of this drift type, rendered as bare excerpts
(`before → after`) under a `<file> (doc|code)` header. No URLs, no commentary.
Use them to choose *what kind of artifact* to target — never to copy wording.

{{EXEMPLARS}}
