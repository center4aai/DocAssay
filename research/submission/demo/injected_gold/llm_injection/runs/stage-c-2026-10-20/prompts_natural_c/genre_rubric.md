# Genre rubric — independent auditor (Stage C, frozen at S0)

Assign each of the two non-README documents exactly one genre from this rubric.
You are **blind** to any planned assignment. Read the whole document and choose
the genre that best describes what the document is for. Do not rewrite it.

| genre | what the document is for |
|---|---|
| `tutorial` | teaches a new user to complete one small, realistic task step by step |
| `how-to` | solves one concrete problem that a user who already knows the basics has |
| `reference` | looks up the public interface and states exact names, signatures, and behavior |
| `explanation` | explains the concepts, design, and reasons behind how the project works |
| `cookbook` | collects several short, self-contained recipes for common tasks |
| `module map` | explains what each part of the project is for and how the parts relate |

Rules:

1. Judge the **content and purpose**, not the layout. Headings, tables, lists,
   and code blocks do not decide the genre.
2. A document may include examples in any genre; examples alone do not make it a
   cookbook.
3. If two genres fit, choose the one that describes the document's main purpose.
4. If the document is a changelog, release notes, roadmap, or proposal, report
   `forbidden` instead of a genre.
5. Give a one-sentence rationale for each assignment.

Return JSON only:

```json
{"repos": {"<repo>": {"task_document": "<genre>",
                      "reference_document": "<genre>",
                      "rationale": "<one sentence>"}}}
```
