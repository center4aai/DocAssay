# Third-Party Notices

DocAssay (`docassay`) has **no runtime dependencies**: the verification engine
uses only the Python standard library.

## Attribution scope for this repository

- The software in `src/` does not vendor or copy third-party source code.
- Development tooling (`pytest`, `ruff`, `uv`) is installed separately and is
  governed by its own licenses.
- The web UI no longer loads external fonts or other third-party assets at
  runtime.

## Data and fixtures

- **IANA root-zone TLD snapshot** — `src/docassay/tests/data/iana_tlds_2026-09-06.txt`
  is a dated snapshot of the IANA root zone database
  (<https://www.iana.org/domains/root/db>), used only by a vocabulary-integrity
  test. The snapshot is factual registry data; the IANA terms of use apply.
- **Dependency vocabulary** — `src/docassay/data/dependency.json` is derived
  from public PyPI package metadata (distribution names and latest versions,
  snapshot 2026-09-05). Package names are not copyrightable; no package source
  is included.
- **Research exemplars** — the research artifact contains short quotations and
  patch excerpts from public commits in third-party repositories, used as
  research examples for the injection study. Each evidence record and the
  curated-source README name the source repository and commit URL. Those
  excerpts remain under the source repository's license; they are research data,
  not part of the MIT-licensed software.
- **Synthetic corpora** in the research artifact were generated for this study
  and are licensed CC BY 4.0
  (`DATA-LICENSE.md` in the research artifact) unless a file says otherwise.
