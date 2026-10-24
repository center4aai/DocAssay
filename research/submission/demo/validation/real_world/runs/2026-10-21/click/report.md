repo: click
docs=36 claims=1269 referents=255 evidence=1430
code_verdicts: {'REFUTED': 3, 'NEI': 136, 'SUPPORTED': 137}  coverage=0.51  resolved=140

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 19 items in 5 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 3
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 3 of 3):
  1. PATH_EXISTS hello.py docs/entry-points.md:34-34
     tier: bare
     raw: Contents of ``hello.py``:
     cited by 10 claims
  2. PATH_EXISTS app.py docs/standalone-apps.md:45-45
     tier: bare
     raw: Where ``app.py`` contains a Click command:
     cited by 2 claims
  3. PATH_EXISTS __main__.py docs/standalone-apps.md:96-96
     tier: bare
     raw: ``python -m <package>``, so a ``__main__.py`` file **must** exist in the

