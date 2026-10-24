# Documentation consistency audit

Audit the repository at:

`{{REPO_DIR}}`

Read `spec.json`, `pyproject.toml`, the source tree, and all Markdown documents.
Check the factual statements the documents make about the project.

## What to check

1. Version: any version stated in the docs matches `project.version`,
   `pyproject.toml`, and the package `__version__`.
2. Dependencies: any dependency named in the docs is declared in
   `pyproject.toml`, and any version requirement stated in the docs matches the
   declared constraint.
3. Paths and files: any file or directory the docs say exists actually exists.
4. Symbols: any class, function, method, or attribute the docs describe actually
   exists in the source with that name.
5. Configuration keys, routes, schema fields, and constants: any mentioned value
   exists in the source.
6. Commands and examples: commands shown in the docs are plausible for this
   repository; do not flag a missing test suite or a missing entry point unless
   the docs claim it exists.

Do **not** require the docs to mention every symbol, dependency, or
configuration key. Omission is fine. Only report statements that are false,
unsupported, or misleading.

Do **not** modify any file. Do not run any external analysis or verification
tool. Use only reading and searching.

## Output

If the repository is consistent, reply with exactly:

`CONSISTENT`

Otherwise, list each problem as:

`file:line — the offending statement — why it is wrong`

most severe first. Do not fix anything.
