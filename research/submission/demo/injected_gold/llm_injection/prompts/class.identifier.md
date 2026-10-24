# Injector — `identifier-drift` (code-side symbol rename)

**Defect.** The **definition** of a code symbol that a document references by its
qualified (dotted) name is renamed, so the documented identifier no longer
resolves in the project's code. The document still names the old identifier.

- **Artifact:** a code symbol (module/class/function/method/field).
- **Direction:** mutate the **code**; the document is left unchanged.
- **Dispatch kind:** `symbol_rename` (harness renames the definition and the
  references it can parse).

## What the exemplars anchor

Choose a target the same *way* the real incidents do: a symbol a document names as
a current API (a class, a function, a field), referenced by a **qualified or
call-form** token, not a bare ambiguous word and not an attribute/constant.

## Target-selection rules

1. The symbol must be a **top-level** class or function defined in
   the repository inventory below, with a unique name in the project.
2. The document must reference it by a **dotted or call form** (e.g.
   `pkg.Thing`, `load_note()`), on the line you report.
3. Avoid names that also occur as ordinary English words in the document; the
   reference must be to the code symbol.
4. Do not target a `Class.attribute` or `module.CONSTANT` token — a plain
   attribute or constant is not a resolvable symbol.

## Required mutation

Rename the definition to a minimal plausible new name (e.g. append `Renamed`),
keeping the same spelling style. The old qualified name must be absent and the new
name present after the change; the file must still parse. The document line still
names the **old** symbol.

## Output skeleton (fill and emit as JSON only)

```json
{
  "injectable": true,
  "drift_type": "identifier-drift",
  "artifact_class": "identifier",
  "direction": "code_side",
  "kind": "symbol_rename",
  "file": "<source file defining the symbol>",
  "old": "<qualified name as referenced, e.g. pkg.Thing>",
  "new": "<new qualified name>",
  "symbol": "<bare symbol name>",
  "target": "<token as written in the doc line>",
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
