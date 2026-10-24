# Confirmed documentation drift (REAL_DRIFT)

## celery

- **PATH_EXISTS** `docs/configuration.rst` — CONTRIBUTING.rst:1202 (conf 0.95, class DIRECTIVE)  
  CONTRIBUTING.rst still points contributors at docs/configuration.rst, deleted in 2016; line was rewritten 2019, after the move.  
  evidence: ls docs/configuration.rst -> No such file; git log -- docs/configuration.rst -> 86dc8f20a 'Docs: Moves configuration reference to userguide' (2016-07-09); git blame -L 1202 CONTRIBUTING.rst -> d48c347a09 (2019-10-30)  
  history: 2016-07-09 Docs: Moves configuration reference to userguide 
- **PATH_EXISTS** `docs/include/introduction.txt` — CONTRIBUTING.rst:1467 (conf 0.93, class DIRECTIVE)  
  Typo: directory is docs/includes/ (plural); contributing guide tells maintainers to bump version in a nonexistent file.  
  evidence: docs/include absent; docs/includes/introduction.txt exists and .bumpversion.cfg lists 'docs/includes/introduction.txt'; CONTRIBUTING.rst:1467 says docs/include  
  history:   
- **SYMBOL_EXISTS** `celery.result.baseasyncresult` — docs/internals/app-overview.rst:185 (conf 0.92, class DOCS)  
  BaseAsyncResult was removed in Celery 4.0 and renamed ResultBase; the map still names it as current API.  
  evidence: grep '^class ' celery/result.py -> ResultBase/AsyncResult/...; docs/history/whatsnew-4.0.rst:2148 'Removed ``BaseAsyncResult``'  
  history:   
- **SYMBOL_EXISTS** `celery.worker.workercontroller` — docs/internals/app-overview.rst:189 (conf 0.92, class DOCS)  
  WorkerController was renamed WorkController; the map uses the pre-3.0 name.  
  evidence: cat celery/worker/__init__.py -> 'from .worker import WorkController', "__all__ = ('WorkController',)"; rg WorkerController celery/ -> none  
  history:   
- **PATH_EXISTS** `requirements/doc.txt` — requirements/README.rst:35 (conf 0.9, class README)  
  Index lists requirements/doc.txt but only requirements/docs.txt exists; every other listed file exists.  
  evidence: ls requirements: docs.txt YES, doc.txt no; README.rst:35 'Extra requirements required to build the Sphinx documentation'  
  history:   
- **SYMBOL_EXISTS** `celery.pidbox.broadcastconsumer` — docs/internals/app-overview.rst:196 (conf 0.88, class DOCS)  
  celery/pidbox.py no longer exists and BroadcastConsumer was renamed; pidbox now lives under celery.worker.pidbox.  
  evidence: ls celery/pidbox.py -> No such file; grep '^class ' celery/worker/pidbox.py -> Pidbox, gPidbox  
  history:   
- **SYMBOL_EXISTS** `celery.pidbox.broadcastpublisher` — docs/internals/app-overview.rst:195 (conf 0.88, class DOCS)  
  Module celery/pidbox.py is gone; BroadcastPublisher was replaced by Pidbox/gPidbox in celery.worker.pidbox.  
  evidence: ls celery/pidbox.py -> absent; grep '^class ' celery/worker/pidbox.py -> Pidbox, gPidbox; docs hit only app-overview.rst  
  history:   
- **SYMBOL_EXISTS** `celery.bin.amqp.amqpadmin` — docs/internals/app-overview.rst:209 (conf 0.87, class DOCS)  
  AMQPAdmin was renamed; bin/amqp.py now defines only AMQPContext, so the architecture map lists a dead class.  
  evidence: grep '^class ' celery/bin/amqp.py -> 'class AMQPContext:'; grep -rn AMQPAdmin celery/ docs/ -> only app-overview.rst:209  
  history:   
- **SYMBOL_EXISTS** `celery.bin.beat.beatcommand` — docs/internals/app-overview.rst:211 (conf 0.85, class DOCS)  
  CLI commands became click functions; bin/beat.py has only def beat(), no BeatCommand class.  
  evidence: grep -n 'class |^def ' celery/bin/beat.py -> 'def beat(ctx, detach=...)'; rg BeatCommand celery/ -> docs only  
  history:   
- **SYMBOL_EXISTS** `celery.bin.events.evcommand` — docs/internals/app-overview.rst:199 (conf 0.85, class DOCS)  
  bin/events.py now defines a click function events(); EvCommand no longer exists.  
  evidence: grep -n 'class |^def ' celery/bin/events.py -> _run_evdump/_run_evcam/_run_evtop/def events(...); no EvCommand  
  history:   
- **SYMBOL_EXISTS** `celery.bin.worker.workercommand` — docs/internals/app-overview.rst:187 (conf 0.85, class DOCS)  
  WorkerCommand removed when the CLI moved to click; bin/worker.py defines only option types plus def worker().  
  evidence: grep -n 'class |^def ' celery/bin/worker.py -> CeleryBeat/WorkersPool/Hostname/Autoscale, def worker(...)  
  history:   
- **SYMBOL_EXISTS** `celery.worker.control.controldispatch` — docs/internals/app-overview.rst:193 (conf 0.85, class DOCS)  
  ControlDispatch no longer exists; control is a module whose public API is only Panel.  
  evidence: grep -n '^class |__all__' celery/worker/control.py -> "__all__ = ('Panel',)", class Panel; rg ControlDispatch celery/ -> docs only  
  history:   
- **SYMBOL_EXISTS** `celery.result.tasksetresult` — docs/internals/app-overview.rst:182 (conf 0.8, class DOCS)  
  TaskSetResult no longer exists in celery.result; task sets were replaced by group/ResultSet.  
  evidence: grep '^class ' celery/result.py -> ResultBase, AsyncResult, ResultSet, GroupResult, EagerResult; TaskSetResult only in app-overview.rst  
  history:   
- **SYMBOL_EXISTS** `celery.task.sets.taskset` — docs/internals/app-overview.rst:180 (conf 0.8, class DOCS)  
  App dependency tree names celery.task.sets.TaskSet, but the celery/task package was deleted; only a DB model class TaskSet remains.  
  evidence: ls celery/task -> No such file; grep -rn 'class TaskSet' celery/ -> celery/backends/database/models.py:101 only  
  history:   
- **SYMBOL_EXISTS** `celery.worker.control.registry.panel` — docs/internals/app-overview.rst:194 (conf 0.6, class DOCS)  
  Panel still exists but only as celery.worker.control.Panel; the documented registry submodule was collapsed into a single module.  
  evidence: ls celery/worker -> control.py (no control/ package); grep '^class ' celery/worker/control.py -> class Panel(UserDict)  
  history:   

## dbt-core

- **PATH_EXISTS** `.gitattributes` — crates/proto-rust/README.md:53 (conf 0.9, class README)  
  README instructs readers that .gitattributes marks generated files, but no .gitattributes is tracked anywhere at HEAD.  
  evidence: git ls-tree -r HEAD | grep -c gitattributes -> 0; find . -name .gitattributes -> none; git log --diff-filter=D shows 8290fe08c 'Project import generated by Copybara.' deleting it.  
  history: 2026-06-01 Project import generated by Copybara. 
- **SYMBOL_EXISTS** `dbt.nodes.depends_on_macros` — crates/dbt-docs-server/API-CONTRACTS.md:2339 (conf 0.74, class OTHER)  
  Doc lists dbt.nodes among tables carrying depends_on_macros, but nodes has no such column at HEAD; the stated inverse scan is impossible.  
  evidence: NodeRow (parquet.rs:1714-1789) and node_cols! (info_schema/schema.rs:16-78) omit depends_on_macros; only macros/exposures/metrics/saved_queries/semantic_models/unit_tests declare it.  
  history: 2018-12-14 Split dbt into core and plugins 
- **PATH_EXISTS** `crates/dbt-docs-server/src/handlers/models.rs` — crates/dbt-docs-server/API-CONTRACTS.md:6195 (conf 0.72, class OTHER)  
  Doc calls handlers/models.rs the structural template; file deleted 2026-08-12 when docs server became a static DuckDB-WASM site. No handlers dir at HEAD.  
  evidence: ls crates/dbt-docs-server/src/handlers -> not found; git log --diff-filter=DR -> 'D crates/dbt-docs-server/src/handlers/models.rs' at 447e19b1e; src/lib.rs says 'There is no API'; API-CONTRACTS.md last edited 2026-09-09.  
  history: 2026-08-13 feat(dbt-docs-server): generate docs v2 as a static site queried by DuckDB-WASM 

## fastapi

- **DEPENDENCY** `pydantic` — docs/en/docs/deployment/versions.md:92 (conf 0.7, class DOCS)  
  Current versions doc says pydantic 'any version above 1.0.0' and shows pin >=2.7.0, but the package requires >=2.9.0; following it yields an unsatisfiable install.  
  evidence: sed -n 75,110p docs/en/docs/deployment/versions.md (pydantic>=2.7.0,<3.0.0) vs pyproject.toml L46 'pydantic>=2.9.0', L168 '>=2.9.0,<3.0.0'  
  history:   

## httpx

- **SYMBOL_EXISTS** `httpx.mounts` — docs/advanced/transports.md:178 (conf 0.68, class DOCS)  
  Current transports guide example builds a client with httpx.Mounts, but no such public class exists in httpx at HEAD.  
  evidence: rg -n Mounts httpx/ -> no hits; docs/advanced/transports.md:178,190 use httpx.Mounts({...}); mounts are passed as a plain dict to Client(mounts=...)  
  history:   

## pip

- **PATH_EXISTS** `build_env.py` — docs/html/development/architecture/anatomy.rst:69 (conf 0.6, class DOCS)  
  anatomy.rst lists pip/_internal/build_env.py as current layout; it is now the build_env/ package.  
  evidence: git log src/pip/_internal/build_env.py: removed in c8651d86d 'Split build environment module'; repo has build_env/ dir.  
  history:   
- **PATH_EXISTS** `pep425tags.py` — docs/html/development/architecture/anatomy.rst:86 (conf 0.5, class DOCS)  
  Layout doc still lists pep425tags.py; module was renamed years ago, so the described anatomy is stale.  
  evidence: git log src/pip/_internal/pep425tags.py -> 'Move pep425tags -> utils.compatibility_tags'; no such file at HEAD.  
  history:   

## pytest

- **SYMBOL_EXISTS** `_pytest.pdb` — doc/en/reference/reference.rst:796 (conf 0.9, class DOCS)  
  reference.rst tells contributors to read _pytest.pdb, renamed to _pytest/debugging.py in 2016; no pdb module exists at HEAD.  
  evidence: ls src/_pytest -> debugging.py, no pdb.py; git log --diff-filter=R -- _pytest/pdb.py -> 05b5554ca 'Renamed pytest pdb to debugging'; file still edited 2026-10-09  
  history: 2016-06-25 Renamed pytest pdb to debugging which conflicts with python pdb. Combining multiple imports the "import pdb" imports the pytest module as opposed to the python debugger. 

## ruff

- **PATH_EXISTS** `crates/ruff_linter/src/flake8_unused_arguments/settings.rs` — CONTRIBUTING.md:398 (conf 0.9, class DIRECTIVE)  
  CONTRIBUTING points to a plugin settings file but omits the rules/ directory; path is wrong at HEAD.  
  evidence: find: actual file crates/ruff_linter/src/rules/flake8_unused_arguments/settings.rs; no non-rules copy.  
  history:   

## sqlfluff

- **PATH_EXISTS** `plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles.yml` — CONTRIBUTING.md:308 (conf 0.93, class DIRECTIVE)  
  Contributors are pointed at a fixtures path that no longer exists; the file moved into a profiles_yml/ subdirectory in 2022, a year before this line was written.  
  evidence: find -> .../test/fixtures/dbt/profiles_yml/profiles.yml only, no fixtures/dbt/profiles.yml; git log -- plugins/.../dbt/profiles.yml -> 286a5268 'Fix connection issue in dbt 1.0.0' (2022); blame -L 308 -> 032814847 (2023-03-13)  
  history: 2022-01-07 Fix connection issue in dbt 1.0.0 (#2230) 
- **PATH_EXISTS** `aliasing.yml` — test/AGENTS.md:447 (conf 0.62, class DIRECTIVE)  
  AGENTS.md claims per-category rule test YAMLs; directory holds per-rule files (AL01.yml...), never aliasing.yml.  
  evidence: ls test/fixtures/rules/std_rule_cases -> AL01.yml, AL02.yml, CP01.yml, ... plus README.md (94 files); find -name 'aliasing*' empty; section added by #7261.  
  history:   
- **PATH_EXISTS** `capitalisation.yml` — test/AGENTS.md:449 (conf 0.62, class DIRECTIVE)  
  Documented category YAML absent; CP rule tests live in CP01.yml-style files.  
  evidence: ls test/fixtures/rules/std_rule_cases -> CP01.yml, CP02.yml, ...; no capitalisation.yml at HEAD or in history.  
  history:   
- **PATH_EXISTS** `convention.yml` — test/AGENTS.md:450 (conf 0.62, class DIRECTIVE)  
  Documented category YAML absent; CV rule tests live in CV01.yml-style files.  
  evidence: ls test/fixtures/rules/std_rule_cases -> CV01.yml..CV13.yml; no convention.yml; find -name 'convention*' empty.  
  history:   
- **PATH_EXISTS** `layout.yml` — test/AGENTS.md:448 (conf 0.62, class DIRECTIVE)  
  Documented category YAML does not exist; rule tests are per-rule files like LT01.yml.  
  evidence: ls test/fixtures/rules/std_rule_cases shows LT01.yml etc., no layout.yml; loader globs std_rule_cases/*.yml individually.  
  history:   
- **PATH_EXISTS** `references.yml` — test/AGENTS.md:452 (conf 0.62, class DIRECTIVE)  
  Documented category YAML absent; RF rule tests live in RF01.yml-style files.  
  evidence: ls test/fixtures/rules/std_rule_cases -> RF01.yml, RF02.yml, ...; no references.yml at HEAD or in history.  
  history:   
- **PATH_EXISTS** `structure.yml` — test/AGENTS.md:451 (conf 0.62, class DIRECTIVE)  
  Documented category YAML absent; ST rule tests live in ST01.yml-style files.  
  evidence: ls test/fixtures/rules/std_rule_cases -> ST01.yml, ST02.yml, ...; no structure.yml; per-rule layout since the split of rule YAMLs.  
  history:   
- **PATH_EXISTS** `grammar.rs` — sqlfluffrs/sqlfluffrs_dialects/README.md:20 (conf 0.6, class README)  
  Generator emits mod.rs/matcher.rs/parser.rs only; GrammarTables now lives in parser.rs, so grammar.rs is a stale name.  
  evidence: utils/rustify.py:76 builds dialect/<name>/{mod,matcher,parser}.rs; build_parsers.py emits GrammarTables into parser.rs; no grammar.rs generated or gitignored anywhere.  
  history:   
