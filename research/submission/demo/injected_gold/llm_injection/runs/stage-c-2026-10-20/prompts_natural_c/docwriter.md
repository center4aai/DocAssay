# Documentation writer — Stage C natural corpus

You are writing the documentation for one small open-source-style Python
project. Work only inside this repository directory:

`{{REPO_DIR}}`

Read `spec.json`, `pyproject.toml`, and the source tree first. The spec and the
source are the source of truth.

## What to write

Write exactly these three files (create directories as needed):

- `README.md` — what the project is for, how to install it, a short quickstart,
  and the main concepts.
- `{{TASK_DOC}}` — {{TASK_GENRE_INSTRUCTION}}
- `{{REFERENCE_DOC}}` — {{REFERENCE_GENRE_INSTRUCTION}}

Write like a maintainer writing for human readers. A normal project does not
document every symbol, every dependency, or every internal detail. Omit things
that do not matter to a user. It is fine if the three documents overlap a little.

Cover only what the project actually has. A library may have no HTTP routes, no
schema fields, no configuration keys, and no enum values; do not invent them,
and do not add a section just because a documentation template might have one.

## Truth rules

- Only mention files, paths, symbols, dependencies, versions, configuration keys,
  routes, schema fields, and constants that actually exist in this repository.
- Spell names exactly as they appear in the spec or source.
- The project version you state, if you state one, must be the version in
  `pyproject.toml` / the package `__version__`.
- Do not invent features, commands, or examples that the code does not support.
- The generated source is deliberately small; its function bodies may return
  `None`. Describe the API surface accurately and do not claim runtime behavior
  the code does not implement.
- Do not modify source files, `pyproject.toml`, `spec.json`, or any other file
  besides the three documents above.

## Style

- Write ordinary Markdown the way a maintainer naturally would.
- Use whatever phrasing feels natural. Do not follow a fixed template for the
  version line, symbol references, or file references.
- Write in English, present tense, for a reader who wants to use the project.
- Write for a human maintainer and user.

## Output

Create the three Markdown files in the repository directory above. When done,
reply with the list of files you wrote and one sentence about each.
