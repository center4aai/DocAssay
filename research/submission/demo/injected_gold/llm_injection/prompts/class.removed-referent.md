# Injector — `removed-referent-drift` (code-side symbol removal)

**Defect.** A top-level symbol that a document references by a qualified (dotted)
name is **deleted** from the code, so the referenced element no longer exists. The
document still names it.

- **Artifact:** a code referent (module/class/function/method).
- **Direction:** mutate the **code**; the document is left unchanged.
- **Dispatch kind:** `symbol_delete` (harness removes the definition).

## What the exemplars anchor

Choose a target the same *way* the real incidents do: a symbol a document treats
as a current, available API and that has no remaining legitimate role, referenced
by a **qualified** name. This is the removal counterpart of `identifier-drift`:
the referent is gone, not renamed.

## Target-selection rules

1. The symbol must be a **top-level** class or function in the repository inventory below.
2. The document must reference it by a **qualified (dotted)** name on the line you
   report. A bare, unqualified mention does not qualify.
3. Prefer a symbol that is not imported or called elsewhere in the project, so
   removing it leaves the tree parseable and self-consistent apart from the
   now-stale documentation.
4. Do not target a `Class.attribute` or `module.CONSTANT`.

## Required mutation

Delete the symbol's definition (whole block). The old qualified name must be
absent from the tree after the change; the file must still parse. The document
line still names the **deleted** symbol.

## Output skeleton (fill and emit as JSON only)

```json
{
  "injectable": true,
  "drift_type": "removed-referent-drift",
  "artifact_class": "referent",
  "direction": "code_side",
  "kind": "symbol_delete",
  "file": "<source file defining the symbol>",
  "old": "<qualified name as referenced, e.g. pkg.Thing>",
  "new": null,
  "symbol": "<bare symbol name>",
  "target": "<token as written in the doc line>",
  "doc_path": "<document file>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the claim the document makes that the removal falsifies>",
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
