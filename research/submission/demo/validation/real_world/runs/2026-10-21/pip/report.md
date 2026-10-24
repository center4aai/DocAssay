repo: pip
docs=137 claims=3002 referents=329 evidence=16606
code_verdicts: {'REFUTED': 30, 'NEI': 216, 'SUPPORTED': 160}  coverage=0.47  resolved=190

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 31 items in 9 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 5
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    LICENSE          TRUE_CANDIDATE  neg=0: 3
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 1
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 30 of 30):
  1. DEPENDENCY sphinx docs/html/cli/pip_freeze.rst:56-56
     tier: -
     raw: Sphinx==1.2.2
     evidence: sphinx:pyproject.toml:~= 7.0
  2. DEPENDENCY setuptools docs/html/cli/pip_list.rst:74-74
     tier: -
     raw: setuptools 20.6.7  21.0.0 wheel
     evidence: setuptools:pyproject.toml:>= 70.1.0, <80
  3. DEPENDENCY setuptools docs/html/cli/pip_list.rst:161-161
     tier: -
     raw: setuptools       57.4.0
     evidence: setuptools:pyproject.toml:>= 70.1.0, <80
  4. DEPENDENCY python docs/html/cli/pip_show.rst:95-95
     tier: -
     raw: Programming Language :: Python :: 2
     evidence: python:pyproject.toml:>=3.10
     cited by 5 claims
  5. LICENSE bsd docs/html/cli/pip_show.rst:135-135
     tier: -
     raw: License :: OSI Approved :: BSD License
     cited by 8 claims
  6. PATH_EXISTS build_env.py docs/html/development/architecture/anatomy.rst:69-69
     tier: bare
     raw: ``build_env.py``
  7. PATH_EXISTS pep425tags.py docs/html/development/architecture/anatomy.rst:86-86
     tier: bare
     raw: ``pep425tags.py`` -- getting refactored into packaging.tags (a library on PyPI) which is external to pip (but vendored by pip).
  8. PATH_EXISTS news/nnnn.feature.rst docs/html/development/contributing.rst:94-94
     tier: anchored
     raw: ``news/NNNN.feature.rst`` and ``news/NNNN.removal.rst``).
  9. PATH_EXISTS news/nnnn.removal.rst docs/html/development/contributing.rst:94-94
     tier: anchored
     raw: ``news/NNNN.feature.rst`` and ``news/NNNN.removal.rst``).
  10. PATH_EXISTS get-pip.py docs/html/development/release-process.rst:156-156
     tier: bare
     raw: #. Regenerate the ``get-pip.py`` script in the `get-pip repository`_ (as
     cited by 8 claims
  11. PATH_EXISTS lib/ensurepip/__init__.py docs/html/development/release-process.rst:160-160
     tier: unanchored
     raw: adjusting the versions listed in ``Lib/ensurepip/__init__.py``.
  12. DEPENDENCY setuptools docs/html/reference/build-system.md:167-167
     tier: -
     raw: Setuptools 40.8.0 is the first version of setuptools that offers a
     evidence: setuptools:pyproject.toml:>= 70.1.0, <80
  13. PATH_EXISTS .dist-info/ docs/html/reference/inspect-report.md:43-43
     tier: bare
     raw: of the time this is the `.dist-info` directory. For legacy installs it is the
  14. PATH_EXISTS .egg-info/ docs/html/reference/inspect-report.md:44-44
     tier: bare
     raw: `.egg-info` directory.
  15. PATH_EXISTS direct_url.json docs/html/reference/inspect-report.md:55-55
     tier: bare
     raw: [`direct_url.json`](https://packaging.python.org/en/latest/specifications/direct-url)
     cited by 2 claims
  16. DEPENDENCY python docs/html/reference/inspect-report.md:95-95
     tier: -
     raw: "Programming Language :: Python :: 3.6",
     evidence: python:pyproject.toml:>=3.10
  17. DEPENDENCY python docs/html/reference/inspect-report.md:96-96
     tier: -
     raw: "Programming Language :: Python :: 3.7",
     evidence: python:pyproject.toml:>=3.10
  18. DEPENDENCY python docs/html/reference/inspect-report.md:97-97
     tier: -
     raw: "Programming Language :: Python :: 3.8",
     evidence: python:pyproject.toml:>=3.10
  19. DEPENDENCY python docs/html/reference/inspect-report.md:98-98
     tier: -
     raw: "Programming Language :: Python :: 3.9",
     evidence: python:pyproject.toml:>=3.10
  20. LICENSE apache-2.0 docs/html/reference/inspect-report.md:135-135
     tier: -
     raw: "license": "BSD-2-Clause or Apache-2.0",
  21. PATH_EXISTS pip.conf docs/html/topics/configuration.md:55-55
     tier: bare
     raw: : {file}`$VIRTUAL_ENV/pip.conf`. If no virtual environment is activated, `pip.conf` is loaded from the
  22. PATH_EXISTS pip.ini docs/html/topics/configuration.md:102-102
     tier: bare
     raw: : {file}`%VIRTUAL_ENV%\\pip.ini`, If no virtual environment is activated, `pip.ini` is loaded from
     cited by 3 claims
  23. PATH_EXISTS origin.json docs/html/topics/secure-installs.md:78-78
     tier: bare
     raw: These original hashes are obtained from a `origin.json` file stored in each cache entry.
  24. PATH_EXISTS build-constraints.txt docs/html/user_guide.rst:297-297
     tier: bare
     raw: Example build constraints file (``build-constraints.txt``):
     cited by 3 claims
  25. DEPENDENCY setuptools docs/html/user_guide.rst:302-302
     tier: -
     raw: setuptools>=45,<80
     evidence: setuptools:pyproject.toml:>= 70.1.0, <80
  26. DEPENDENCY python docs/html/user_guide.rst:1040-1040
     tier: -
     raw: With Python 2.6 came the `"user scheme" for installation
     evidence: python:pyproject.toml:>=3.10
  27. DEPENDENCY virtualenv docs/html/user_guide.rst:1107-1107
     tier: -
     raw: From within a `--system-site-packages virtualenv where SomePackage==0.3`
     evidence: virtualenv:pyproject.toml:>= 20.0.28
  28. DEPENDENCY virtualenv docs/html/user_guide.rst:1329-1329
     tier: -
     raw: `six==1.11, even though virtualenv==20.0.2` requires
     evidence: virtualenv:pyproject.toml:>= 20.0.28
  29. SYMBOL_EXISTS pip._vendor.simplejson src/pip/_vendor/README.rst:105-105
     tier: -
     raw: ``pip._vendor`` and to *not* load ``simplejson`` (all platforms) and
  30. LICENSE bsd src/pip/_vendor/idna/LICENSE.md:1-1
     tier: -
     raw: BSD 3-Clause License

