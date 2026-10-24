# Prompt provenance — Stage C vs Stage B

Frozen at S0. Hashes are in `scope_engine_freeze.json`.

## docwriter.md — newly authored

The Stage C docwriter prompt is **not** copied from Stage B. The diff against
`runs/stage-b-2026-10-20/prompts_natural/docwriter.md` is:

| change | permitted by §3.1 | note |
|---|---|---|
| document list is parameterised (`{{TASK_DOC}}`, `{{REFERENCE_DOC}}`) | yes — run identifier | Stage B hard-coded `docs/guide.md` + `docs/api.md` |
| genre instruction placeholders (`{{TASK_GENRE_INSTRUCTION}}`, `{{REFERENCE_GENRE_INSTRUCTION}}`) | yes — genre instruction | filled per repo from `corpus_design.json` |
| removed the fixed three-file wording | yes | Stage C assigns document roles, not a fixed guide/api pair |
| removed "inline code for identifiers, and Markdown links for other documents" | yes — removal of presentation guidance | the forbidden-phrase list in §2.3 |
| removed "Do not tailor the prose to any particular analysis or verification tool" | yes | replaced by "Write for a human maintainer and user" (no tool vocabulary) |
| truth rules and style otherwise unchanged | — | |

The prompt contains none of the forbidden phrases listed in plan §2.3
("organise per module", "module heading", "table of symbols", "group by
module", any instruction to use qualified names/dotted names/backticks/links/
version constraints, any mention of resolution, qualification, the engine,
predicates, claims, or `SCOPE.md`).

## injector.system.md and class.*.md — copied verbatim

Byte-identical to `runs/stage-b-2026-10-20/prompts_natural/`. The only permitted
difference in §5.2 is the schema `$id`; it is changed in
`output.schema.json` (`stage-b/output.schema.json` → `stage-c/output.schema.json`).

## auditor.md — Stage B copy plus two additions

- a "Genre assignment (separate, blind)" section;
- the rubric is supplied as `genre_rubric.md` (new file).

## genre_rubric.md — new

The frozen six-genre rubric used by the blind auditor. It does not contain a
planned assignment and does not mention the engine, predicates, or this plan.
