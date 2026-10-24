repo: mkdocs
docs=36 claims=1189 referents=268 evidence=2447
code_verdicts: {'REFUTED': 14, 'NEI': 159, 'SUPPORTED': 114}  coverage=0.45  resolved=128

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 23 items in 7 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 1
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 14 of 14):
  1. PATH_EXISTS foo.md docs/dev-guide/themes.md:434-434
     tier: bare
     raw: page `foo.md` would be `/bar/foo/`.
     cited by 3 claims
  2. PATH_EXISTS search/search.html docs/dev-guide/themes.md:747-747
     tier: unanchored
     raw: search page via a template located at `search/search.html`.
     cited by 2 claims
  3. PATH_EXISTS search/search_index.json docs/dev-guide/themes.md:771-771
     tier: unanchored
     raw: The search index is written to a JSON file at `search/search_index.json` in the
  4. PATH_EXISTS mkdocs/search_index.json docs/getting-started.md:161-161
     tier: anchored
     raw: even have a `sitemap.xml` file and `mkdocs/search_index.json`.
  5. PATH_EXISTS x.html docs/user-guide/configuration.md:686-686
     tier: bare
     raw: no additional `X` directory is created, and the file is simply stored as `X.html`.
  6. PATH_EXISTS foo.py docs/user-guide/configuration.md:876-876
     tier: bare
     raw: > If a hook file has a file `foo.py` adjacent to it, it can use the normal Python syntax `import foo` to access its functions.
  7. PATH_EXISTS base.yml docs/user-guide/configuration.md:1184-1184
     tier: bare
     raw: parent file `base.yml` and deep merge the two. This would result in MkDocs
     cited by 2 claims
  8. PATH_EXISTS somelib.js docs/user-guide/customizing-your-theme.md:193-193
     tier: bare
     raw: template. As `somelib.js` is a JavaScript library, it would logically go in the
     cited by 2 claims
  9. PATH_EXISTS win_add2path.py docs/user-guide/installation.md:97-97
     tier: bare
     raw: > `Tools`, then `Scripts` folder, and run the `win_add2path.py` file by double
     cited by 2 claims
  10. PATH_EXISTS docs/about.md docs/user-guide/writing-your-docs.md:120-120
     tier: anchored
     raw: `docs/about.md`.
  11. PATH_EXISTS docs/user-guide/license.md docs/user-guide/writing-your-docs.md:207-207
     tier: anchored
     raw: Please see the [project license](license.md) for further details.
  12. PATH_EXISTS docs/user-guide/about.md docs/user-guide/writing-your-docs.md:233-233
     tier: anchored
     raw: Please see the [project license](about.md#license) for further details.
  13. PATH_EXISTS docs/user-guide/img/screenshot.png docs/user-guide/writing-your-docs.md:330-330
     tier: anchored
     raw: ![Screenshot](img/screenshot.png)
  14. DEPENDENCY markdown docs/user-guide/writing-your-docs.md:384-384
     tier: -
     raw: A level 1 Markdown header on the first line of the document body.
     evidence: markdown:pyproject.toml:==3.3.6, markdown:pyproject.toml:>=3.3.6, markdown:requirements/requirements-docs.txt:==3.5.1

