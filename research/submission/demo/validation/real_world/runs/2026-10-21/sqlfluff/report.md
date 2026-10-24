repo: sqlfluff
docs=68 claims=2175 referents=502 evidence=20544
code_verdicts: {'REFUTED': 16, 'SUPPORTED': 267, 'NEI': 239}  coverage=0.54  resolved=283

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 28 items in 7 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 1
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 3
    LICENSE          SUPPORTED       neg=0: 4
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 16 of 16):
  1. PATH_EXISTS plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles.yml CONTRIBUTING.md:308-308
     tier: anchored
     raw: required connection parameters in `plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles.yml`.
  2. PATH_EXISTS pep8.ini docsv/configuration/index.md:13-13
     tier: bare
     raw: `pep8.ini`
  3. PATH_EXISTS integration.md docsv/development/shared-design-integration.md:8-8
     tier: bare
     raw: is the source of truth for it. Its own `INTEGRATION.md` is the contract; this
  4. PATH_EXISTS docsv/public/sqlfluff-design/ docsv/development/shared-design-integration.md:95-95
     tier: anchored
     raw: package's `static/sqlfluff-design/` directory into `docsv/public/sqlfluff-design/`,
  5. PATH_EXISTS sqlfluff-lrg.png docsv/development/shared-design-integration.md:236-236
     tier: bare
     raw: `sqlfluff-lrg.png` lockup where the main site's hero uses the wide one, which
  6. DEPENDENCY python docsv/guide/install.md:26-26
     tier: -
     raw: Python 3.9.1
     evidence: python:plugins/sqlfluff-plugin-example/pyproject.toml:>=3.10, python:pyproject.toml:>=3.10, python:sqlfluffrs/pyproject.toml:>=3.10
  7. PATH_EXISTS file_a.sql docsv/usage/pre-commit.md:75-75
     tier: bare
     raw: `file_a.sql` and `file_b.sql`, then the command which is called
     cited by 2 claims
  8. PATH_EXISTS file_b.sql docsv/usage/pre-commit.md:75-75
     tier: bare
     raw: `file_a.sql` and `file_b.sql`, then the command which is called
     cited by 2 claims
  9. PATH_EXISTS docsv/reference/cli/index.md docsv/usage/troubleshooting.md:116-116
     tier: anchored
     raw: [CLI](../reference/cli/index.md) directly. Often this can make debugging significantly
  10. PATH_EXISTS grammar.rs sqlfluffrs/sqlfluffrs_dialects/README.md:20-20
     tier: bare
     raw: `grammar.rs`** — `GrammarTables` struct with all parsing rules
  11. PATH_EXISTS aliasing.yml test/AGENTS.md:447-447
     tier: bare
     raw: `aliasing.yml`: Aliasing rules (AL*)
     cited by 2 claims
  12. PATH_EXISTS layout.yml test/AGENTS.md:448-448
     tier: bare
     raw: `layout.yml`: Layout rules (LT*)
     cited by 2 claims
  13. PATH_EXISTS capitalisation.yml test/AGENTS.md:449-449
     tier: bare
     raw: `capitalisation.yml`: Capitalisation rules (CP*)
  14. PATH_EXISTS convention.yml test/AGENTS.md:450-450
     tier: bare
     raw: `convention.yml`: Convention rules (CV*)
  15. PATH_EXISTS structure.yml test/AGENTS.md:451-451
     tier: bare
     raw: `structure.yml`: Structure rules (ST*)
  16. PATH_EXISTS references.yml test/AGENTS.md:452-452
     tier: bare
     raw: `references.yml`: Reference rules (RF*)

