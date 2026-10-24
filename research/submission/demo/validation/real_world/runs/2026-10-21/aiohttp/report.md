repo: aiohttp
docs=152 claims=2354 referents=439 evidence=5081
code_verdicts: {'REFUTED': 15, 'NEI': 222, 'SUPPORTED': 241}  coverage=0.54  resolved=256

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 27 items in 9 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 2
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      SYSTEMATIC      neg=0: 2
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 1
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 15 of 15):
  1. PATH_EXISTS 1234.feature.1.rst AGENTS.md:40-40
     tier: bare
     raw: Multiple fragments same category: `1234.feature.rst`, `1234.feature.1.rst`.
  2. PATH_EXISTS 1234.feature.rst AGENTS.md:40-40
     tier: bare
     raw: Multiple fragments same category: `1234.feature.rst`, `1234.feature.1.rst`.
  3. PATH_EXISTS reader_c.py CHANGES/12573.contrib.rst:5-5
     tier: bare
     raw: ``reader_py.py`` / ``reader_c.py`` split and the vendored ``llhttp``
     cited by 2 claims
  4. PATH_EXISTS changes/6045.doc.1.rst CHANGES/README.rst:85-85
     tier: anchored
     raw: File :file:`CHANGES/6045.doc.1.rst`:
  5. PATH_EXISTS changes/8074.bugfix.rst CHANGES/README.rst:91-91
     tier: anchored
     raw: File :file:`CHANGES/8074.bugfix.rst`:
  6. PATH_EXISTS changes/4594.feature.rst CHANGES/README.rst:104-104
     tier: anchored
     raw: File :file:`CHANGES/4594.feature.rst`:
  7. SYMBOL_EXISTS aiohttp.cookiejar.multipartwriter THREAT_MODEL.md:35-35
     tier: -
     raw: Entry points `aiohttp.MultipartReader`/`MultipartWriter`, `aiohttp.CookieJar`, `aiohttp.TraceConfig`, `aiohttp.resolver.AsyncResolver`
  8. PATH_EXISTS vendor/llhttp/ THREAT_MODEL.md:182-182
     tier: anchored
     raw: `vendor/llhttp/` — vendored upstream parser, version `9.3.1` (see
  9. PATH_EXISTS vendor/llhttp/package.json THREAT_MODEL.md:183-183
     tier: anchored
     raw: `vendor/llhttp/package.json`). Generated via `make generate-llhttp`.
     cited by 2 claims
  10. PATH_EXISTS reader_c.pyx THREAT_MODEL.md:482-482
     tier: bare
     raw: `reader.py` / `reader_c.pyx` / `reader_c.py` / `reader_py.py` — frame
  11. DEPENDENCY aiodns docs/client_reference.rst:1304-1304
     tier: -
     raw: default (asynchronous if `aiodns>=1.1` is installed).
     evidence: aiodns:pyproject.toml:>= 3.3.0, aiodns:requirements/base-ft.txt:==4.0.4, aiodns:requirements/base.txt:==4.0.4, aiodns:requirements/constraints.txt:==4.0.4, aiodns:requirements/dev.txt:==4.0.4, aiodns:requirements/lint.txt:==4.0.4, aiodns:requirements/pyproject.toml:>= 3.3.0, aiodns:requirements/runtime-deps.txt:==4.0.4, aiodns:requirements/test-ft.txt:==4.0.4, aiodns:requirements/test-mobile.txt:==4.0.4, aiodns:requirements/test.txt:==4.0.4
  12. PATH_EXISTS security.md docs/contributing-admins.rst:87-87
     tier: bare
     raw: Vulnerability reports arrive through the organization's ``SECURITY.md``
  13. DEPENDENCY gunicorn docs/deployment.rst:289-289
     tier: -
     raw: [2017-03-11 18:27:21 +0000] [1249] [INFO] Starting gunicorn 19.7.1
     evidence: gunicorn:requirements/base-ft.txt:==26.2.0, gunicorn:requirements/base.txt:==26.2.0, gunicorn:requirements/constraints.txt:==26.2.0, gunicorn:requirements/dev.txt:==26.2.0, gunicorn:requirements/test-ft.txt:==26.2.0, gunicorn:requirements/test-mobile.txt:==26.2.0, gunicorn:requirements/test.txt:==26.2.0
  14. PATH_EXISTS mod.py docs/faq.rst:431-431
     tier: bare
     raw: Consider the following code from ``mod.py``::
     cited by 2 claims
  15. PATH_EXISTS main.py docs/faq.rst:447-447
     tier: bare
     raw: ``main.py``::

