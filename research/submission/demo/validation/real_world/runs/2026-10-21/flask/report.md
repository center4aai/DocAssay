repo: flask
docs=80 claims=2212 referents=301 evidence=1155
code_verdicts: {'REFUTED': 12, 'NEI': 229, 'SUPPORTED': 95}  coverage=0.32  resolved=107

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 25 items in 7 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 5
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 3
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 1
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 12 of 12):
  1. PATH_EXISTS flask.json docs/api.rst:228-228
     tier: bare
     raw: :attr:`flask.Flask.json`. The functions provided by ``flask.json`` will
     cited by 2 claims
  2. PATH_EXISTS app.json docs/api.rst:229-229
     tier: bare
     raw: use methods on ``app.json`` if an app context is active.
     cited by 2 claims
  3. DEPENDENCY python docs/cli.rst:141-141
     tier: -
     raw: Python 3.10.0 (default, Oct 27 2021, 06:59:51) [GCC 11.1.0] on linux
     evidence: python:pyproject.toml:>=3.11
  4. SYMBOL_EXISTS flask.commands docs/cli.rst:447-447
     tier: -
     raw: Flask will automatically load commands specified in the ``flask.commands``
  5. DEPENDENCY werkzeug docs/testing.rst:101-101
     tier: -
     raw: bytes returned by the view. If you want to use text, Werkzeug 2.1
     evidence: werkzeug:pyproject.toml:>=3.1.0
  6. PATH_EXISTS response.json docs/testing.rst:158-158
     tier: bare
     raw: Similarly, if the response contains JSON data, the ``response.json``
     cited by 4 claims
  7. DEPENDENCY click docs/tutorial/install.rst:75-75
     tier: -
     raw: click          6.7
     evidence: click:pyproject.toml:>=8.1.3
  8. DEPENDENCY itsdangerous docs/tutorial/install.rst:78-78
     tier: -
     raw: itsdangerous   0.24
     evidence: itsdangerous:pyproject.toml:>=2.2.0
  9. DEPENDENCY jinja2 docs/tutorial/install.rst:79-79
     tier: -
     raw: Jinja2         2.10
     evidence: jinja2:pyproject.toml:>=3.1.2
  10. DEPENDENCY markupsafe docs/tutorial/install.rst:80-80
     tier: -
     raw: MarkupSafe     1.0
     evidence: markupsafe:pyproject.toml:>=2.1.1
  11. DEPENDENCY werkzeug docs/tutorial/install.rst:82-82
     tier: -
     raw: Werkzeug       0.14.1
     evidence: werkzeug:pyproject.toml:>=3.1.0
  12. DEPENDENCY python docs/tutorial/tests.rst:514-514
     tier: -
     raw: platform linux -- Python 3.6.4, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
     evidence: python:pyproject.toml:>=3.11

