# Injector — `external-dependency-drift` (code-side declared-dependency drift)

**Defect.** A dependency **declared in the project manifest** is changed so it no
longer satisfies the version requirement a document states — or is removed while
the document still mentions it. The documentation and the manifest disagree.

- **Artifact:** a declared dependency and its version constraint.
- **Direction:** mutate the **manifest**; the document is left unchanged.
- **Dispatch kind:** `dependency_version_break` (primary, produces a refutable
  claim). `dependency_remove` is the secondary, doc-drift form.

## What the exemplars anchor

Choose a target the same *way* the real incidents do: a dependency the
documentation presents as a current requirement together with a version
constraint, and that the manifest declares. Ignore the exemplars' specific
ecosystems and packages; take only the *pattern* (a stated constraint vs. a
declared one).

> Scope note. The declared dependency must appear in the project's own manifest
> (`pyproject.toml`, `setup.cfg`, `setup.py`, `requirements*.txt`). A package that
> is only present transitively, or only mentioned as an external tool, is **not**
> in scope — do not target it.

## Target-selection rules

1. The dependency must be **declared** in the repository inventory below (name + constraint).
2. A document line must name the dependency and, ideally, state a constraint
   (e.g. `` `click` (`>=8.1`) ``). Report that line and the constraint token.
3. Prefer a dependency whose documented constraint is a simple bound you can
   contradict.

## Required mutation (primary)

Change the manifest constraint for that dependency to a clearly non-overlapping
bound (e.g. `>=999`). The new constraint must be parseable and must not intersect
the constraint stated on the document line.

### Secondary form (only if no documented constraint exists)

Remove the dependency from the manifest while the document still names it. Set
`kind` to `dependency_remove` and record `old` as the dependency name.

## Output skeleton (fill and emit as JSON only)

```json
{
  "injectable": true,
  "drift_type": "external-dependency-drift",
  "artifact_class": "dependency",
  "direction": "code_side",
  "kind": "dependency_version_break",
  "file": "<manifest file>",
  "old": "<existing constraint, e.g. >=8.1>",
  "new": ">=999",
  "symbol": "<normalized dependency name>",
  "target": "<dependency token as written in the doc line>",
  "doc_path": "<document file>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the claim the document makes that the change falsifies>",
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
