# Injected gold — external-first error catalog for the injection evaluation

> **Status:** the **external layer is frozen** (`catalog_external.json`). The
> `ours` layer (`catalog_ours.json`) is append-only and starts empty. The
> headline injection source is the **source-grounded few-shot LLM injector**
> (`llm_injection/`); the earlier deterministic operator pipeline (registry →
> inject → verify → score) is retired and archived under
> the private deterministic-operator archive (not shipped). What survives from it is
> the mutation **grammar** and the engine-free **oracle** (`engine/`). The three
> capability predicates (`LICENSE`, `HAS_DOCKERFILE`, `HAS_CI_WORKFLOW`) are
> covered by constructed **conformance templates** (`conformance/`), a separate
> provenance arm. The **operative tool-validation protocol** is
> `../validation/protocol.md`.
>
> External source artifacts referenced as `other_instruments/...` are local
> snapshots of public datasets used during construction; they are not shipped.
> The canonical source URLs and commit references are recorded in
> `catalog_external.json`.

## 1. Why this exists

The document-sampled gold cannot measure extraction **recall**: "all claims in a
window" has no objective denominator, and annotators (independent or LLM) do not
reproduce each other (negative Cohen's κ; loose-vs-strict agreement 0.14 in the
former extraction-eval line). Injection supplies the missing denominator: insert known
documentation↔repository inconsistencies, so recall = detected injected defects /
injected defects, with precision on a consistent control.

## 2. The circularity rule

A benchmark whose error types are read off `src/docassay/predicates/*` tests
exactly the engine's strengths. Therefore:

1. **External-first.** Every external entry cites a source artifact whose `kind`
   is not the engine (tool dataset, report, benchmark).
2. **Maximal, no de-duplication.** One row per `(source, source_label)`; original
   labels are kept **verbatim**; method/behavior/process/data rows are kept too
   (tagged by `unit`/`scope`), not dropped.
3. **Freeze, then measure.** `catalog_external.json:frozen = true`; predicate
   coverage is a post-freeze result (`scripts/coverage.py`), never a selection
   criterion.
4. **`ours` is separate and later.** Incidents from our own runs and real bug
   reports are appended to `catalog_ours.json` only after the external layer is
   frozen, and are never used to define it. Deriving classes from the engine's
   predicates is forbidden.

`scripts/validate_catalog.py` enforces (1), (3) and the independence invariant
mechanically.

## 3. Layers and files

```
injected_gold/
  catalog_external.json   # layer "external", FROZEN; entries with source_label + evidence
  catalog_ours.json       # layer "ours", append-only, empty seed
  normalization.json      # overlay: canonical_class -> unit/scope/artifact_class + aliases
  boundary.json           # out-of-scope classes (expressiveness limit; not operators)
  engine/
    grammar.py            # mutation kinds + applier (engine-free)
    oracle.py             # independent oracle (stdlib only) + --selftest
  README.md
  scripts/validate_catalog.py
  scripts/validate_scope.py    # boundary.json vs normalization.json
  scripts/coverage.py
  scripts/_corpus.py           # stdlib inventory + doc-token index (engine-free)
  scripts/score_injections.py  # run engine -> recall/precision/reactions (MPChecker)
  scripts/judge_batches.py     # build per-repo tool-diff batches for the judge agent
  scripts/judge_apply.py       # merge judge verdicts + agreement with the scorer
  scripts/judge_diff.py        # our own deterministic diff judge (no LLM) + agreement
  scripts/generate_synthetic.py
  synthetic/              # generated evaluation corpus (specs + repos)
  llm_injection/          # source-grounded few-shot injector (protocol §4.2)
    exemplars/            # rules.json (frozen) + generated bank.{json,md}
    prompts/              # injector.system.md + class.<drift>.md + output.schema.json
    scripts/              # build_exemplar_bank.py, fetch_exemplar_evidence.py, llm_inject.py
    runs/<date>/          # manifest.jsonl, provenance.json, metrics.{md,json}
  conformance/            # constructed templates for the capability predicates
    run.py                # license / dockerfile / ci_workflow (origin: conformance)
    runs/<date>/          # manifest.jsonl, provenance.json, metrics.{md,json}
```

Every external entry:

```
{id, source, source_label, canonical_class, unit, scope, definition,
 evidence: {artifact, ref, count, examples:[{commit_url|path, quote}]}}
```

- `source_label` — verbatim label from the source; `canonical_class` — normalized
  name from `normalization.json`.
- `unit ∈ {repo, method, behavior, doc, process, tool, data, repair, rubric}`.
- `scope ∈ {in, out, control, candidate}`.

## 4. Sources harvested

| source | what it contributes | status |
|---|---|---|
| `readu` (local) | 6 TP themes (244), 5 FP themes (81), repair themes, rubric (Correctness / Up-to-date-ness / Completeness; commit-induced vs pre-existing) | complete |
| `readu_raw` (local) | 4,336 prefilter `potential_readme_bug_scenarios` over 6,000 commits → config-key, api-endpoint, schema-field, UI-naming, path, membership, type, translation subclasses | complete |
| `cascade` (local) | 60 distinct method-level `notes` → exception-contract, null-semantics, format/encoding, polarity/order, lifecycle-contract + mapped classes | complete |
| `docchecker` (local) | binary Consistent/Inconsistent (no taxonomy) | complete |
| `mpc_2025` (arXiv 2411.11410) | 8 CDI patterns | complete |
| `docprism` (arXiv 2511.00215) | 7 true-positive + FP categories | complete |
| `vasperabench` (HF) | value_mismatch, signature_change, behavior_change, missing/extra_parameter, type_mismatch, security_change, config_mismatch + status classes | complete |
| `truth_benchmark` | 52 MATCH/LIE examples: wrong operators/constants, missing security, wrong sort/protocol, subtle traps | complete |
| `dca_bench` | cross-file/internal discrepancy, document-problem | partial (abstract/table) |
| `aghajani_2019` (2019) | 162-type taxonomy, 4 top categories (content-what / content-how / process / tool) | partial (top-level only) |
| `wen_2019` | code-comment inconsistency taxonomy | partial (top-level only) |
| `docer` | stale code-element reference (deleted/renamed) | partial (via READU driver) |
| `readme_auto_update` | README ↔ code change, single README | partial |

## 5. Post-freeze coverage (a result, not a filter)

`scripts/coverage.py` maps canonical repo-level artifact classes onto the engine's
predicate vocabulary. Current result: **17 repo-level in-scope classes, 7
expressible by a predicate** (path, identifier, removed-referent, dependency,
license, dockerfile, ci_workflow); the other 10 (api-endpoint, config-key,
cross-document, invalid-example, membership, missing-documentation, schema-field,
translation, type, value) have no predicate in the current vocabulary. The seven
expressible classes cover all six registered predicates. Out-of-scope and
control classes are reported separately; the `ours` layer is counted on its own.

## 6. The `ours` layer

Append-only. Allowed: (a) incidents from our own runs/audits with a
repo/doc/line reference;
(b) real reported bugs (maintainer confirmations, issue/PR). Forbidden: classes
derived from the engine's predicates or its advertised capabilities; hand-made
synthetic cases without a real incident. Each entry needs
`origin: "ours"` and a `provenance` object.

## 7. Evaluation protocol (mirrors MPChecker)

1. Apply a mutation to a repository; record it in `manifest.jsonl`.
2. Verify the mutation with `verify_without_tool` (independent oracle), then by
   manual audit.
3. Run the engine `dump_claims` on the baseline and the mutated snapshots.
4. Score per artifact class: recall on injected defects; precision on consistent
   controls; stage attribution for every miss (claim-gate / extraction / referent /
   evidence).
5. Report out-of-scope classes and the MPChecker / external held-out boundary
   separately as the expressiveness limit.

## 8. Commands

```bash
B=research/submission/demo/injected_gold

# Validate both layers and the independence invariants.
PYTHONPATH=src uv run python $B/scripts/validate_catalog.py

# Boundary (out-of-scope classes) against normalization.json.
PYTHONPATH=src uv run python $B/scripts/validate_scope.py

# Post-freeze expressiveness coverage (external vs ours).
PYTHONPATH=src uv run python $B/scripts/coverage.py

# Engine-free oracle unit tests.
PYTHONPATH=src uv run python $B/engine/oracle.py --selftest

# Verify a frozen manifest against its snapshots.
PYTHONPATH=src uv run python $B/engine/oracle.py \
    --manifest $B/llm_injection/runs/<date>/manifest.jsonl \
    --snapshots $B/llm_injection/runs/<date>/snapshots
```

The engine is invoked **only** by ``score_injections.py``. Snapshots are
git-less copies so that on-disk mutations are visible to the engine's CLOSED
world.

### Historical: deterministic operator sweep (archived)

The multi-repo/multi-seed sweep (`inject.py --seeds ...`) and its runs are
retired with the deterministic operators: code and runs are under
the private deterministic-operator archive (not shipped). The current headline run
is the LLM injector (§11). The scoring and judge notes below still apply.

```bash
# (archived) deterministic sweep, kept only as a reference for the retired arm
# RUN=<private deterministic-operator run: sweep-2026-10-12>
# PYTHONPATH=src uv run python $B/scripts/score_injections.py \
#     --manifest $RUN/manifest.jsonl --snapshots $B/snapshots --out $RUN --seed 1
```

``score_injections.py`` reports refuted recall (MPChecker scheme, with Wilson
95% CI), control precision, per-class stage attribution, ``completeness_gap``
separately, unattributed findings, any control false
refutes, and ``seed_diversity.{md,json}``.

**MPChecker scoring.** Detection is not bound to the recorded doc line: for each
injected artifact the scorer scans the whole baseline->injected finding diff for
a new claim whose object matches the artifact, and records **how** the tool
reacted (`refuted` finding, `nei` abstention, or `none`).
Recall = injected artifacts the tool refuted / injected artifacts.

**English-only injections.** Injections only target documents the engine's
English-only corpus scope scans: localized copies (`docs/<lang>/`,
`README.<lang>.md`) and non-English text are filtered out in
``_corpus.iter_doc_texts`` (mirroring the engine rule, standard library only).

**Judge agent.** ``judge_batches.py`` writes one tool-diff batch per repo plus
``judge/RUBRIC.md``; an independent agent adjudicates each batch ("did the tool
react, and how"), and ``judge_apply.py`` merges the verdicts and reports the
agreement with the deterministic scorer.

**Our own diff judge (no LLM).** ``judge_diff.py`` does the same adjudication
deterministically from the finding diff, considering both the stale artifact
(``old``) and the mutated value (``new``). On the sweep it agrees with the LLM
judge on the detected/not-detected decision for 196/196 items (100%) and on the
4-way reaction label for 95.9% (the rest is the ``nei``-vs-``none`` convention),
and reproduces the scorer's recall exactly.

## 9. Roadmap

- [x] Harvest external sources and freeze `catalog_external.json`.
- [x] Normalization overlay + validator + coverage.
- [x] Mutation grammar + engine-free oracle (`engine/`).
- [x] End-to-end pipeline (apply → verify → score) green (deterministic operators, archived).
- [x] Generate the small synthetic corpus (4 repos) and score it (deterministic operators, archived).
- [x] Source-grounded few-shot injector bank + prompts (`llm_injection/`, protocol §4.2).
- [x] LLM injector runner: prepare → `opencode run` → apply → `verify_entry` → freeze manifest.
- [ ] Scale the LLM-injection run across all synthetic repos / samples / seeds.
- [ ] Grow `catalog_ours.json` from real incidents/bug reports.
- [ ] External held-out boundary: MPChecker dataset + a natural fix-commit slice.

## 10. Synthetic corpus (2026-10)

The archived deterministic-operator run
(the private deterministic-operator run `synthetic-2026-10-12`, not shipped)
scored the pipeline on a four-repo **uncontaminated** corpus (`synthetic/`),
generated from a spec rather than harvested, so the baseline is clean by
construction and the controls are exact. Generator:
`scripts/generate_synthetic.py` (`spec-validate` / `materialize` / `check`); the
LLM roles are pre-created subagents in `.opencode/agents/`
(`repo-architect`, `repo-coder`, `repo-docwriter`, `repo-auditor`, `repo-injector`).
Details and regeneration commands are in `synthetic/README.md`.

That first run: 157 injected entries, 157/157 verified; refuted recall **0.697**
[0.527, 0.826]; control precision **1.000** [0.904, 1.0] (36/36).

## 11. LLM injection (source-grounded few-shot)

`llm_injection/` implements the **injection** step of the operative
`../validation/protocol.md` §2/§4.2: an LLM injector receives a small set of
**real, human-triaged incidents** (READU true positives) for one in-scope drift
type and manufactures an analogous defect. It holds a **frozen keyword ruleset**
(`exemplars/rules.json`), a generated **exemplar bank** (`exemplars/bank.json`
with the triaged primary bank and the LLM-hypothesis `readu_raw` pool kept
separate), and the **injector prompts** (`prompts/`). Triaged exemplars carry
concrete `before → after` **evidence** extracted once from their commit patches
(`scripts/fetch_exemplar_evidence.py`; raw patches cached and gitignored), so the
injector itself runs **offline**. The injector's output schema is field-compatible
with the engine-free oracle (`engine/oracle.py:verify_entry`).
See `llm_injection/README.md`, including the per-class coverage caveat.

The **runner** (`llm_injection/scripts/llm_inject.py`) drives `prepare → run →
finalize` end to end: it assembles the prompts, calls the `repo-injector`
subagent via `opencode run`, applies each proposal to a git-less snapshot, proves
it with the engine-free oracle, and freezes `manifest.jsonl` + `provenance.json`.
A four-repo run (`llm_injection/runs/llm-demo`, 16 injections) yielded 16/16
verified and engine recall 0.875. A **scaled run**
(`runs/scaled-2026-10-19`, 4 repos × 4 classes × seeds {1,2,3}; independent
snapshot per `(repo, seed)`) verified **41/48** and gives overall recall **0.902** — per-class
breakdown in `llm_injection/README.md`. Scoring reuses
`score_injections.py` unchanged.

The **Stage A sensitivity run** (`runs/stage-a-2026-10-20`) regenerated the docs
without extractor-aware rules and removed extractor-derived target rules. On the
active four-class scope it reports **18/32 refuted, 10/32 NEI, 4/32 none**; the
symbol classes are mostly deliberate abstentions on bare names, not “0/5
detection”. See `runs/stage-a-2026-10-20/README.md` and `report.md`.

The **Stage B held-out natural-corpus run** (`runs/stage-b-2026-10-20`) uses six
new repos in three domains, 72 bundles, one mutation per snapshot, and 18
engine-free controls. The final run is **72/72 verified: 35/72 refuted (0.486),
7/72 NEI, 30/72 none**; controls are **18/18 clean** (0 false positives, with 13
supported, 1 NEI, and 4 not extracted). Baseline is 0 `REFUTED`. Independent
annotation is not included; no independent labels or IAA are claimed. See
`runs/stage-b-2026-10-20/report.md`, `metrics.md`, and
`ENGINE_FOLLOWUPS.md` (post-B engine work; bare-name policy unchanged).

## 12. Conformance templates (capability predicates)

For `LICENSE`, `HAS_DOCKERFILE` and `HAS_CI_WORKFLOW` the referent is **fixed by
the predicate** (a declared license, a `Dockerfile`, a CI config), so there is no
circular *target* choice — a constructed case is a conformance test. They are
injected by `conformance/run.py` as a **separate provenance arm**
(`origin: "conformance"`), never mixed with the real-incident LLM bank or with
`catalog_ours.json`.

Three cases per predicate:

| case | expectation |
|---|---|
| `false-claim` | a recorded claim that the artifact exists, while it does not → `REFUTED` |
| `control-present` | the claim is true → must **not** be refuted (precision) |
| `mention` | an instruction / negative mention → must **not** be refuted (claim-gate/polarity) |

Demo run (`conformance/runs/demo`, 9 cases): 9/9 verified; refuted recall
**3/3** (1/1 per predicate); controls **5/6** clean — one control false refute on
`license` (a negated "not released under the MIT license" mention was refuted),
which the arm exists to surface. This closes the predicate-coverage gap: all
six registered predicates now have an injection evaluator (four real-incident
classes + three conformance classes).
