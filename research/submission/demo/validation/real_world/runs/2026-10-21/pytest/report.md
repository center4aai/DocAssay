repo: pytest
docs=257 claims=10550 referents=723 evidence=9248
code_verdicts: {'REFUTED': 22, 'SUPPORTED': 198, 'NEI': 888}  coverage=0.20  resolved=220

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 31 items in 9 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 3
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      SYSTEMATIC      neg=0: 1
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 5
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 22 of 22):
  1. PATH_EXISTS changelog/2574.bugfix.rst CONTRIBUTING.rst:299-299
     tier: anchored
     raw: #. Write a ``changelog`` entry: ``changelog/2574.bugfix.rst``, use issue id number
  2. PATH_EXISTS pyconvert_unittest.py doc/en/adopt.rst:55-55
     tier: bare
     raw: changing to native assert_ statements (pycmd_ has a script to help with that, ``pyconvert_unittest.py``)
  3. SYMBOL_EXISTS py.path.local doc/en/deprecations.rst:489-489
     tier: -
     raw: In order to support the transition from ``py.path.local`` to :mod:`pathlib`,
     cited by 13 claims
  4. SYMBOL_EXISTS pytest._fillfuncargs doc/en/deprecations.rst:1037-1037
     tier: -
     raw: The ``pytest._fillfuncargs`` function
  5. SYMBOL_EXISTS py.io.terminalwriter doc/en/deprecations.rst:1097-1097
     tier: -
     raw: with ``py.io.TerminalWriter``.
  6. PATH_EXISTS test_three.py doc/en/example/customdirectory.rst:57-57
     tier: bare
     raw: Notice how ``test_three.py`` was not executed, because it is not listed in the manifest.
  7. PATH_EXISTS test_server.py doc/en/example/markers.rst:231-231
     tier: bare
     raw: (``test_server.py``, ``TestClass``);
     cited by 12 claims
  8. DEPENDENCY python doc/en/example/pythoncollection.rst:272-272
     tier: -
     raw: platform linux2 -- Python 2.7.10, pytest-2.9.1, py-1.4.31, pluggy-0.3.1
     evidence: python:pyproject.toml:>=3.10
  9. SYMBOL_EXISTS conftest.db doc/en/example/simple.rst:774-774
     tier: -
     raw: also define a ``db`` fixture in that sister directory's ``conftest.py`` file.
  10. PATH_EXISTS samplefile.ini doc/en/how-to/unittest.rst:193-193
     tier: bare
     raw: pre-initialized ``samplefile.ini``.  Our ``initdir`` fixture itself uses
     cited by 3 claims
  11. SYMBOL_EXISTS pkg.testing doc/en/how-to/usage.rst:102-102
     tier: -
     raw: This will import ``pkg.testing`` and use its filesystem location to find and run tests from.
  12. PATH_EXISTS newhooks.py doc/en/how-to/writing_hook_functions.rst:216-216
     tier: bare
     raw: For a real world example, see `newhooks.py`_ from `xdist <https://github.com/pytest-dev/pytest-xdist>`_.
     cited by 2 claims
  13. SYMBOL_EXISTS conftest.pytest_my_hook doc/en/how-to/writing_hook_functions.rst:236-236
     tier: -
     raw: now simply define the function ``pytest_my_hook`` with the correct signature in their ``conftest.py``.
  14. SYMBOL_EXISTS conftest.pythonpath doc/en/how-to/writing_plugins.rst:102-102
     tier: -
     raw: ``conftest.py`` files as well on your ``PYTHONPATH`` or ``sys.path``.
  15. PATH_EXISTS plugin.py doc/en/how-to/writing_plugins.rst:230-230
     tier: bare
     raw: module inside a package is imported.  This way ``plugin.py`` can still
  16. PATH_EXISTS tests/subpackage/test_subpackage.py doc/en/reference/fixtures.rst:208-208
     tier: unanchored
     raw: ``innermost`` fixture defined in ``tests/subpackage/test_subpackage.py``, but
  17. PATH_EXISTS tests/test_top.py doc/en/reference/fixtures.rst:209-209
     tier: unanchored
     raw: the one defined in ``tests/test_top.py`` would be unavailable to it because it
  18. DEPENDENCY coverage doc/en/reference/plugin_list.rst:1894-1894
     tier: -
     raw: :pypi:pytest-supercov                                  Pytest plugin for measuring explicit test-file to source-file coverage                         
     evidence: coverage:pyproject.toml:>=7.5
  19. SYMBOL_EXISTS _pytest.pdb doc/en/reference/reference.rst:796-796
     tier: -
     raw: in ``_pytest.pdb`` which interacts with ``_pytest.capture``
  20. PATH_EXISTS tests/test_testament.py doc/en/reference/reference.rst:1423-1423
     tier: unanchored
     raw: In this scenario, with the default options, pytest will collect the class `Testament` from `tests/test_testament.py` because it starts with `Test`, ev
  21. SYMBOL_EXISTS logging.log doc/en/reference/reference.rst:1903-1903
     tier: -
     raw: calls to ``logging.log()`` to specify auto-indentation behavior for
  22. DEPENDENCY pytest-xdist doc/en/reference/reference.rst:2429-2429
     tier: -
     raw: required_plugins = pytest-django>=3.0.0,<4.0.0 pytest-html pytest-xdist>=1.0.0
     evidence: pytest-xdist:pyproject.toml:>=3.5

