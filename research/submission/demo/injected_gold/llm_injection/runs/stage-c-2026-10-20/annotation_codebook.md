# Stage C annotation codebook (frozen at S0)

**Status:** normative for Stage C. Written at S0, before any corpus generation or
engine run. Hashed in `scope_engine_freeze.json`. Annotators read this document
and nothing else about the tool.

Stage C labels are engine-only plus the LLM arm at sign-off (OPEN-C9). This codebook is
frozen now so that annotation can start without changing the corpus, the sheet,
or the labels later. Until independent annotation is completed, the run is
**provisional engine-only** (plan §7.6).

## 1. What the annotator sees and does not see

The sheet gives, per row: repository, class, document role, genre, document path,
line number, the line text, the mention text, whether the row is a target line, a
cross-mention, or a control, the mutation `old → new`, the symbol where
applicable, the injector's own description of the claim, and (for controls) the
control family.

The annotator does **not** see: the tool's verdict, layer, reason, reaction,
metrics, claim dumps, `entries.json`, `bootstrap.json`, other annotators' labels,
or any Stage B report.

The annotator may read the frozen repository tree (documents, source,
`pyproject.toml`, `spec.json`). The tree is the authority.

**The injector's description is not ground truth.** It is one model's statement
of what it changed. Judge the line against the frozen tree.

## 2. Fields and decision order

Fill every field for every row. `n/a` is a value; do not leave a cell blank.

### 2.1 `claim_type` — is the line a current-state claim?

Decide in this order:

1. **`not_a_claim`** — the line does not assert anything about this project's
   current artifacts: headings, prose about motivation, an instruction to the
   reader, a question, a placeholder, a comment about the document itself.
2. **`historical`** — the line refers to a past, removed, deprecated, superseded,
   future, or planned state ("before 2.0", "will be removed", "used to",
   "migrate from", "legacy").
3. **`illustrative`** — the line is an example, a sample output, a fenced code
   block, a command transcript, or a hypothetical ("for example, if you call …").
4. **`conditional`** — the statement holds only under a stated condition
   ("on Windows", "if you use X", "when the optional extra is installed") and the
   condition is not established by the repository.
5. **`current_claim`** — otherwise. This includes ordinary present-tense
   statements, tables of current artifacts, and reference headings that name a
   current member.

Tie-break: a reference heading (`### name`) is `current_claim` when the
document's section describes the current API; it is `not_a_claim` when it is a
table of contents, a changelog entry, or a link index.

### 2.2 `claim_form` — what form does the mention take?

Only for `current_claim`; otherwise `not_a_claim`.

1. **`path`** — the mention is a file or directory path (inline code, link
   target, or a bare path-shaped token).
2. **`dependency`** — the mention is a package/dependency name, with or without
   a version constraint, in a sentence about installation or requirements.
3. **`qualified`** — the document itself writes a dotted name whose top segment
   is a project-owned package/module (`morpheme.lexicon.lookup`).
4. **`section_qualified`** — the document writes a **bare** member token, and a
   module context supplied by the document itself (heading, table row, prose
   lead-in, list lead-in, or `.py` path presented as a module) ties it to a
   project-owned module. The module is not written next to the token.
5. **`bare_call`** — a bare name followed by `()` with no project module context.
6. **`bare`** — any other single-segment code-shaped name.

Decision order matters: `path` and `dependency` are checked before symbol forms;
`qualified` before `section_qualified`; a bare call under a module context is
`section_qualified` (plan §9.1, last paragraph).

If the line contains two or more code-shaped bare member tokens, none of them is
`section_qualified`: use `bare`/`bare_call`, and record `context_source = none`
unless a module context is explicitly written for the specific token.

### 2.3 `context_source` — where did the module context come from?

Only meaningful for `section_qualified`; otherwise `none`.

- `heading` — a heading names the module and the token is inside its section.
- `table` — a cell in the same table row names the module in a module position.
- `prose` — the same sentence or clause names the module as a module
  (`the M module`, `in M`, `from M`, `M provides/declares/…`).
- `list` — a list item under a module heading, or a list lead-in that names the
  module.
- `path_prose` — a `.py` path presented as a module (`the M module`,
  `M provides`) resolves to exactly one project module.
- `none` — no document-supplied module context.

A non-module context (`Parsing`, `helpers`, `utilities`, a domain word) is
`none`, even when it looks like a section. This is the family-B trap: it is not
a module.

### 2.4 `defect_is_real` — is the injected defect really in the frozen tree?

Controls are `n/a`.

- **`yes`** — the line's current claim is contradicted by the frozen tree (the
  path/symbol/dependency is absent or the constraint is violated).
- **`no`** — the line is true in the frozen tree, or the change does not touch
  the claim the line makes.
- **`n/a`** — `claim_type != current_claim`.

Judge only the artifact the row is about. A line may be stale for an unrelated
reason; that is not this defect.

### 2.5 `nei_reason_applies` — would abstention be legitimate?

- **`yes`** — the claim is genuinely undecidable from the repository (bare name
  with no project qualifier, a removed dependency that could be transitive, an
  external/foreign symbol, a dynamic surface).
- **`no`** — the repository does decide it, and silence is a miss.
- **`n/a`** — the row is not an abstention candidate.

### 2.6 `none_claim_not_extracted` — is "no claim" the right reaction?

- **`yes`** — the line supplies no current-state claim about the injected
  artifact (per §2.1), so forming no claim is correct.
- **`no`** — the line does make a claim, so the tool should have formed one.
- **`n/a`** — not a `none` case.

### 2.7 `control_false_positive` — only for control rows

- **`yes`** — the control statement is true in the frozen tree and a refutation
  of it would be a tool error.
- **`no`** — the control statement is actually false (a corpus defect).
- **`n/a`** — not a control.

### 2.8 `same_artifact` — only for cross-mention rows

- **`yes`** — the target line and the other mention denote the same artifact
  (same normalized path, same dependency name, or the same project-qualified
  symbol).
- **`no`** — same spelling but a different artifact (e.g. another module's
  symbol, an external type, a build artifact).
- **`unsure`** — the document and tree do not settle it.

## 3. Tie-breaks

- Prefer the narrowest form: `qualified` over `section_qualified` when the
  module is written next to the token; `section_qualified` over `bare` only when
  a module context exists.
- A mention in a table cell inherits the row's module cell, never a module from
  a neighbouring row.
- A fenced code block is never a claim and never supplies context.
- A pluralized token (`MArray`s) is an external type mention, not a member of the
  surrounding module.
- A dunder, builtin, keyword, CLI flag, environment variable, or placeholder is
  not a member token.
- When two readings are possible and the tree does not disambiguate, use
  `unsure` (for `same_artifact`) or `n/a` (for fields with an `n/a` value); do
  not guess.

## 4. Agreement

With two annotators: Cohen's κ on `claim_type`, `claim_form`, `context_source`,
`defect_is_real`, `nei_reason_applies`, `none_claim_not_extracted`,
`control_false_positive`, and `same_artifact`, plus percent agreement. Target
κ ≥ 0.60; report the observed value, whatever it is. Do not drop a field for low
κ.

With one annotator: report n = 1, no κ, and label the independent arm **provisional**.

No LLM label is ever presented as an independent label. The engine-free classifier's
labels are reported separately as a comparison, never substituted for independent
labels.
