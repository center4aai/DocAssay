repo: sqlalchemy
docs=155 claims=7498 referents=753 evidence=53742
code_verdicts: {'REFUTED': 4, 'SUPPORTED': 246, 'NEI': 569}  coverage=0.31  resolved=250

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 20 items in 6 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 1
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 3
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 4 of 4):
  1. SYMBOL_EXISTS setup.entry_points README.dialects.rst:108-108
     tier: -
     raw: is similar to the ``entry_points`` directive we placed in our ``setup.py``.
  2. SYMBOL_EXISTS sqlalchemy.dialects.postgresql.pgdialect doc/build/core/connections.rst:1301-1301
     tier: -
     raw: ``sqlalchemy.dialects.postgresql.PGDialect`` must still explicitly include this
  3. PATH_EXISTS thread.lock doc/build/errors.rst:217-217
     tier: bare
     raw: The :class:`_pool.QueuePool` pool class uses a ``thread.Lock`` object internally
  4. SYMBOL_EXISTS sqlalchemy.dialects.postgresql.pgcompiler doc/build/errors.rst:568-568
     tier: -
     raw: ``sqlalchemy.dialects.postgresql.PGCompiler``.  The guidance below is

