# Removal report — VERSION predicate and doc_drift

**Date:** 2026-10-20  
**Branch:** `demo` (no new branch)  
**Scope:** active project only. Frozen legacy (the private legacy archive (not shipped),
the private archive (not shipped)) and the frozen external catalog
(`injected_gold/catalog_external.json`) were not edited.

## 1. What was removed and why

### VERSION

The `VERSION` predicate was removed completely:

- no `version_predicate`, `version_scan`, `version_flags`, `version_gate`,
  `match_version`, `VERSION_WORLD`, or `VERSION_PREDICATE`;
- no `VersionEvidence` / `build_version_inventory` / project-version inventory;
- no `project_metadata()["versions"]`;
- no `version_bump` mutation kind, oracle check, or LLM class mapping;
- no `value-drift` injection class, prompt, schema entry, or active scorer
  support.

Reason: project-version detection is brittle on ordinary repositories. Version
literals are routinely ambiguous with dependency versions, tool versions, API
versions, years, ports, and arbitrary numbers. The predicate had a narrow useful
case and a large false-refutation surface. Stage A also showed the opposite
failure mode on natural docs (under-extraction), which is additional evidence
that the predicate is not a reliable contract.

### doc_drift

The referent-level cross-document consistency feature was removed completely:

- no `DocConsistency`, `DOC_DRIFT`, `doc_consistency`, or `doc_conflicts`;
- no `_cross_document_consistency`, `_pair_conflicts`, `constraints_overlap`;
- no `DOC_DRIFT` sections in bundles, dumps, analyze output, triage reports, or
  aggregate tables;
- no `doc_drift` bucket or `doc_conflict` reaction in the injection scorer or
  judge rubric.

Reason: it was a separate capability that was not part of the predicate-backed
conformance denominator, added output-schema surface, and made the tool claim
more than the validation protocol measured. Removing it makes the claim scope
match the six predicates the tool actually commits to.

## 2. New scope

| item | before | after |
|---|---:|---:|
| registered predicates | 7 | **6** |
| active LLM injection classes | 5 | **4** |
| expressible repo-level canonical classes | 8/17 | **7/17** |
| predicate names | DEPENDENCY, PATH_EXISTS, SYMBOL_EXISTS, VERSION, LICENSE, HAS_DOCKERFILE, HAS_CI_WORKFLOW | DEPENDENCY, PATH_EXISTS, SYMBOL_EXISTS, LICENSE, HAS_DOCKERFILE, HAS_CI_WORKFLOW |
| active injection classes | path, identifier, removed-referent, external-dependency, value | path, identifier, removed-referent, external-dependency |

`value-drift` and `cross-document-drift` remain in the frozen external taxonomy
and are reported by `coverage.py` as **catalog in-scope, not implemented**
gaps. They are no longer tool capabilities, no longer in the injection
denominator, and no longer in `SCOPE.md`'s IN-SCOPE table.

## 3. File-level changes

Core tool (`src/docassay/`):

- `predicates/__init__.py` — removed `version_predicate`; six predicates remain.
- `predicates/crossdoc.py` — removed the VERSION block and helpers; the module
  now contains only LICENSE.
- `core/pipeline.py`, `core/sarif.py` — removed `VERSION` action/rule text.
- `core/models.py` — removed `DocConsistency`, `doc_consistency`,
  `doc_conflicts`.
- `core/assertions.py` — removed cross-document consistency; assertion
  clustering remains.
- `core/bundle.py`, `core/dump_claims.py`, `core/analyze_repo.py` — removed
  doc-drift fields/counters/sections.
- `triage/findings.py`, `triage/aggregate.py`, `triage/report.py` — removed
  `doc_consistency` / `doc_drift`.
- `api.py`, `mcp_server.py` — removed project-version metadata; metadata now
  covers license, dependencies, Docker/CI.
- `evidence/project.py` — removed version evidence/inventory; license and
  manifest helpers remain.
- `markers/version.py` — removed `constraints_overlap`; version-context
  utilities used by DEPENDENCY remain.
- `data/project.json`, `tests/data/vocabulary_manifest.json` — removed
  VERSION-only vocabulary/config entries.

Tests:

- `test_crossdoc.py` — VERSION scan/match/pipeline and version-inventory tests
  removed; LICENSE tests remain.
- `test_dependency.py` — DOC_DRIFT tests removed; assertion-split tests remain.
- `test_bundle.py` — added regression tests asserting no doc-drift fields in
  bundles/dumps/markdown.
- `test_triage.py`, `test_abstention_rules.py`, `test_api.py`,
  `test_mcp_server.py` — updated for six predicates and no version metadata.
- The remaining `doc_consistency` / `VERSION` strings in tests are **negative
  regression assertions** (absence checks), not feature code.

Active research tree (`research/submission/demo/`):

- `validation/SCOPE.md` — six predicates; VERSION section removed;
  `value-drift` / `cross-document-drift` are catalog gaps; no doc_drift claim.
- `validation/protocol.md` — reactions are `refuted / nei / none`; no
  `doc_drift` bucket or `doc_conflict`.
- `validation/retrospective.md` — current counts updated; historical value
  mention removed.
- `injected_gold/README.md`, `llm_injection/README.md` — four active classes,
  7/17 expressible, updated run numbers.
- `injected_gold/scripts/coverage.py` — `value` maps to no predicate;
  `validate_catalog.py` — VERSION removed from fallback predicates.
- `injected_gold/engine/grammar.py`, `engine/oracle.py` — `version_bump`
  removed.
- `injected_gold/scripts/_corpus.py` — project-version inventory removed.
- `injected_gold/llm_injection/scripts/llm_inject.py` — four classes; no
  value/version mapping.
- `injected_gold/llm_injection/prompts/class.value.md` — deleted.
- `injected_gold/llm_injection/prompts/output.schema.json` — `value-drift`
  removed.
- `injected_gold/llm_injection/exemplars/rules.json` — value class removed;
  bank rebuilt with four classes.
- `injected_gold/llm_injection/exemplars/sources/curated_triaged.json` —
  value incidents removed; value evidence files deleted.
- `injected_gold/scripts/score_injections.py`, `judge_batches.py`,
  `judge_diff.py`, `judge_apply.py` — no `doc_drift` bucket, `doc_conflict`
  reaction, or value support.
- `README.md` — no VERSION bullet or DOC_DRIFT description.

## 4. Metric impact

Stage A data, before/after removing the value class:

| run | before | after |
|---|---:|---:|
| Stage A verified-only | 21/44 = **0.477** | 18/32 = **0.5625** |
| Stage A end-to-end (all attempts) | 21/60 = **0.350** | 18/48 = **0.375** |
| Old checker-shaped corpus | 49/53 = **0.925** | 37/41 = **0.902** |

The aggregate refutation rate **rises** after removal because the weakest class
is removed. This is a denominator change, not a capability improvement. The
per-class numbers are the meaningful comparison:

- path-location: 10 refuted / 0 NEI / 0 none
- external-dependency: 7 refuted / 0 NEI / 2 none
- identifier: 1 refuted / 6 NEI / 1 none
- removed-referent: 0 refuted / 4 NEI / 1 none
- active total: **18 refuted / 10 NEI / 4 none** (32 verified)

`NEI` is a deliberate abstention, not a miss; the symbol classes are mostly
abstentions under the bare-name policy, not “0/5 detection”.

`doc_drift` had zero entries in the LLM run, so its removal does not change
recall. It changes the output schema and the tool’s claim scope.

## 5. Verification

Commands run from the repository root:

```bash
uv run pytest -q
uv run ruff check src/

B=research/submission/demo/injected_gold
PYTHONPATH=src uv run python $B/scripts/validate_catalog.py
PYTHONPATH=src uv run python $B/scripts/validate_scope.py
PYTHONPATH=src uv run python $B/scripts/coverage.py
PYTHONPATH=src uv run python $B/engine/oracle.py --selftest
PYTHONPATH=src uv run python $B/llm_injection/scripts/build_exemplar_bank.py --check
```

Results:

- `pytest`: **589 passed, 11 xfailed**.
- `ruff`: **All checks passed**.
- `validate_catalog.py`: **CATALOG OK** (82 external entries, 45 canonical
  classes, 0 ours).
- `validate_scope.py`: **SCOPE OK** (28 boundary classes, 17 repo in-scope).
- `coverage.py`: **7/17 expressible**; `value-drift` and
  `cross-document-drift` are non-expressible gaps.
- `oracle --selftest`: **SELFTEST OK**.
- `build_exemplar_bank.py --check`: **EXEMPLAR BANK CHECK OK**; four classes,
  40 triaged / 713 raw / 81 controls.

A smoke `dump_claims` run on a temporary repo produced no `VERSION`,
`doc_consistency`, `doc_conflicts`, or `DOC_DRIFT` keys.

The baseline workflow is no longer an acceptance gate: `generate_synthetic.py
baseline-report` runs the engine once, prints baseline findings, and always
exits 0 on a successful engine run. `check` is a deprecated alias with the same
diagnostic behavior. Baseline findings are recorded and adjudicated, never used
to edit docs or select a corpus. This removes the second circularity loop: on
held-out real repos the baseline has tens of REFUTED claims (bitsandbytes 34,
fastapi 62, pydantic 29), several of them false positives; a 0-REFUTED gate
would have hidden them.

## 6. Residual mentions in frozen/historical data

These are intentionally retained and are not active tool code:

- `injected_gold/catalog_external.json` and `normalization.json` still contain
  `value-drift` and `cross-document-drift` as **external taxonomy** rows. They
  are frozen/independent catalog data and are reported as gaps by
  `coverage.py`.
- Historical run directories under `injected_gold/llm_injection/runs/` retain
  old `value-drift` manifests and `doc_drift` fields. They are frozen run
  artifacts, not produced by the current pipeline.
- the private legacy archive (not shipped) and the private archive (not shipped) may contain old
  references; they are read-only legacy.

No active code path emits or consumes VERSION claims or doc-drift fields.

## 7. Bottom line

The tool now has **six predicates** and **four real-incident injection classes**.
`VERSION` and `doc_drift` are gone from the active implementation, tests, active
docs, prompts, scorer, and injection grammar. The only remaining mentions are
external catalog data, frozen historical runs, and negative regression tests
that assert the fields stay absent.
