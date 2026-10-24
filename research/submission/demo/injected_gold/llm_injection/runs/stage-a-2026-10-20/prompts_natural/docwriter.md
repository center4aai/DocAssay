# Documentation writer — natural corpus

You are writing the documentation for one small open-source-style Python project.
Work only inside this repository directory:

`{{REPO_DIR}}`

Read `spec.json`, `pyproject.toml`, and the source tree first. The spec and the
source are the source of truth.

## What to write

Write these three files (create `docs/` if needed):

- `README.md` — what the project is for, how to install it, a short quickstart,
  and the main concepts.
- `docs/configuration.md` — configuration and environment variables that a user
  would actually need.
- `docs/api.md` — the public API a user would actually call, with short examples
  where useful.

Write like a maintainer writing for human readers. A normal project does not
document every symbol, every dependency, or every internal detail. Omit things
that do not matter to a user. It is fine if the three documents overlap a little.

## Truth rules

- Only mention files, paths, symbols, dependencies, versions, configuration keys,
  routes, schema fields, and constants that actually exist in this repository.
- Spell names exactly as they appear in the spec or source.
- The project version you state, if you state one, must be the version in
  `pyproject.toml` / the package `__version__`.
- Do not invent features, commands, or examples that the code does not support.
- Do not modify source files, `pyproject.toml`, or `spec.json`.

## Style

- Use ordinary Markdown: headings, short paragraphs, bullet lists, fenced code
  blocks, inline code for identifiers, and Markdown links for other documents.
- Use whatever phrasing feels natural. Do not follow a fixed template for the
  version line, symbol references, or file references.
- Write in English, present tense, for a reader who wants to use the project.
- Do not tailor the prose to any particular analysis or verification tool. Write
  for a human maintainer and user.

## Output

Create the three Markdown files in the repository directory above. When done,
reply with the list of files you wrote and one sentence about each.
