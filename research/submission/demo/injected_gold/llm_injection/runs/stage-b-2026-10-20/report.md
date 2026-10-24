# Stage B — held-out natural-corpus evaluation of the documentation verifier

**Date:** 2026-10-20
**Branch:** `demo` (no new branch)
**Status:** complete; no independent labels or IAA are claimed.
**Run directory:** `research/submission/demo/injected_gold/llm_injection/runs/stage-b-2026-10-20/`

Stage B is a held-out evaluation of the **current** tool on a new, frozen,
independently audited natural corpus. It was not used to tune prompts, specs, or
tool code. The corpus, prompts, and model IDs were frozen before any engine or
injector run.

---

## 1. Question

Stage A showed that the checker-shaped 0.925 headline was substantially a
property of benchmark construction: on natural documents, with no extractor
preconditions in the docwriter or injector prompts, active four-class
refutation was 18/32 (0.5625), with 10/32 `NEI` and 4/32 `none`.

Stage B asks: on a **new** natural corpus that was never used to build the tool
or the exemplar bank, what does the **current** tool do on the four active
injection classes, with a transparent three-outcome report, controls, and a
held-out corpus?

The tool is evaluated as-is. Bare-name abstention under `SYMBOL_EXISTS` is
deliberate (`SCOPE.md` §3.3.1); tool fixes are a separate development cycle
after B.

---

## 2. What was frozen and when

`corpus_freeze.json` was written at **2026-10-20T10:46:11+00:00** (branch
`demo`), before any injector or scoring run, and re-verified after scoring:

- **71 corpus files** (source, `pyproject.toml`, `spec.json`, docs, example
  data), excluding `__pycache__`, `.pyc`, `.DS_Store`, and `.git`;
- **8 prompts** (`docwriter`, `auditor`, `injector.system`, four class prompts,
  `output.schema.json`);
- **4 agent prompt files** (`repo-architect`, `repo-docwriter`, `repo-auditor`,
  `repo-injector`);
- exact model IDs and a SHA-256 of each ID string;
- an aggregate SHA-256 over the sorted `path:hash` lines:
  `0a739f4ef52b62db0041b8ff36fde5ac22be00b50fea1fc1f9ff5c11e713ca41`.

`freeze_corpus.py --verify` passed after the scoring run, confirming that no
corpus file, spec, prompt, agent prompt, or model ID changed after the freeze.
Per-prompt SHA-256 values are in `corpus_freeze.json` (`prompts`), and the
per-bundle prompt hash, seed, and exemplar IDs are in `provenance.json`.

### Models

| role | model | family |
|---|---|---|
| architect | `opencode-go/claude-haiku-5-5` | Anthropic / Claude |
| docwriter | `opencode-go/claude-haiku-5-5` | Anthropic / Claude |
| auditor | `opencode-go/qwen3.8-flash` | Alibaba / Qwen |
| injector | `opencode-go/deepseek-v4.1-flash` | DeepSeek |

The docwriter and injector are different families. The auditor is a third
family, independent of the docwriter. The preregistered auditor was GPT-6 Luna;
it was unavailable in this environment (`Country, region, or territory not
supported`). Gemini-4 was blocked by workspace privacy settings, and Grok-4.7
returned an endpoint error. Qwen3.8 Flash was substituted **before the freeze**
and **before any engine or injector run**; the substitution is recorded in
`PREREGISTRATION.md` §13 and `audit/audit.json`.

---

## 3. Corpus design

### 3.1 Six repos, three domains

| repo | domain | natural project |
|---|---|---|
| `gaugekit` | environmental data | stream-gauge CSV loading and summary statistics |
| `gridwatch` | energy/utility data | smart-meter interval parsing and tariff calculation |
| `plotline` | creative/visual | SVG chart primitives (scales, marks, canvas) |
| `palette` | creative/visual | color palette generation and contrast checks |
| `sheetmusic` | music | chord/progression parsing and transposition |
| `recipecard` | everyday/consumer | recipe scaling and shopping-list generation |

Domains: environmental/energy data (2), creative/visual (2), music/everyday (2).

### 3.2 Why the corpus is not tool-shaped

The repos are ordinary small libraries/CLIs, not API-service checklists. The
spec schema was changed for Stage B so that `config_keys`, `endpoints`,
`schema_fields`, `enum_members`, `example_commands`, `paths`, and `data_files`
are **optional**; only `project`, `dependencies`, `modules`, and `docs` are
required. None of the six specs declares `config_keys`, `endpoints`,
`schema_fields`, or `enum_members`. The docs are ordinary install/quickstart/
guide/API-reference prose, with no fixed template for version lines, symbol
references, path references, or dependency mentions. The injector never sees
the tool, its predicates, or its output.

### 3.3 Active classes and claim forms

Four classes only:

1. `path-location-drift` — a current location is renamed/moved; the doc still
   points at the old location.
2. `identifier-drift` — a current class/function definition is renamed; the doc
   still names the old symbol.
3. `removed-referent-drift` — a current class/function definition is deleted;
   the doc still names it.
4. `external-dependency-drift` — a current dependency requirement is broken in
   the manifest; the doc still states it.

No `VERSION`, `doc_drift`, `value-drift`, or `cross-document-drift` injection.

Claim forms: `path`, `dependency`, `qualified`, `bare_call`, `bare`.

### 3.4 One mutation per snapshot

Each of the 72 bundles gets an independent git-less baseline/injected pair:
`<repo>__<class>__s<seed>_<sample>`. No class or seed shares a snapshot.

---

## 4. Corpus generation and independent audit

Each repo was generated by `repo-architect` (Claude), materialized
deterministically from `spec.json`, documented by `repo-docwriter` (Claude), and
audited read-only by `repo-auditor` (Qwen3.8 Flash), which compared every
factual statement in the docs against the spec and source. The engine was not
used at any point in acceptance.

**Result:** 6/6 repos audited `CONSISTENT`. `recipecard` initially had three
factual errors about a non-existent top-level re-export; the fixes were:

| file | finding | fix |
|---|---|---|
| `README.md:59` | `from recipecard import ...` | import from `recipecard.loader`, `recipecard.scaling`, `recipecard.shopping` |
| `docs/guide.md:57` | claimed re-export from the top-level package | removed the re-export claim |
| `docs/api.md:3` | claimed package-level imports | only per-module imports |

After the fixes, `recipecard` re-audited `CONSISTENT`. The full trail is in
`audit/audit.json`.

The audit is LLM-based, model-based. It is independent of the docwriter by model
family, but it is not a substitute for independent corpus annotation.

---

## 5. Injector run

- **72/72 bundles** produced valid JSON proposals with `injectable: true`.
- **0 declines.**
- **72/72 verified** by the engine-free oracle after two pre-scoring harness
  fixes (below).
- Exact injector model: `opencode-go/deepseek-v4.1-flash`.
- Per-bundle prompt SHA-256, seed, exemplar IDs, model, and verifier result are
  in `provenance.json`; the verified entries are in `manifest.jsonl`.

### 5.1 Pre-scoring harness fixes (not prompt/spec/tool tuning)

The first finalize pass produced 55/72 verified. All 17 failures were
`external-dependency-drift` constraint proposals. The model wrote the **full
requirement** (`click>=999`, `numpy>=999`, `PyYAML>=999`) while the applier
expects the constraint (`>=999`) and prefixes the dependency name itself. This
is a harness parsing mismatch, not a generator defect: the proposals name a real
manifest dependency and are semantically valid.

A second pass normalized the requirement and produced 70/72; the two remaining
failures were `PyYAML` proposals rejected because the oracle's doc-line check
was case-sensitive (`pyyaml` vs `PyYAML`). A case-insensitive oracle check
produced **72/72**.

| pass | verified | verify_failed | dependency verified |
|---|---:|---:|---:|
| pre-fix | 55 | 17 | 1/18 |
| after requirement normalization | 70 | 2 | 16/18 |
| after case-insensitive oracle check | **72** | **0** | **18/18** |

No injector output was regenerated; no prompt, spec, or tool code was changed.
The raw model value is preserved as `new_raw` in the manifest. The fixes were
made **before scoring**, so no tool result influenced them. Full detail:
`HARNESS_FIX.md`.

---

## 6. Scoring

The engine was run once on the frozen corpus: baseline and injected snapshots
for 72 injections plus 6 clean control snapshots. `score_injections.py` cached
the claim dumps; `stage_b_metrics.py` computed the three outcomes, the `none`
sub-flags, controls, end-to-end denominators, and the repo-cluster bootstrap.
The `baseline-report` smoke on `gaugekit` is a separate diagnostic requested by
the verification checklist; it is not the scoring run and no metric below uses
it.

### 6.1 Overall (verified injections)

| outcome | count | rate | repo-cluster 95% CI |
|---|---:|---:|---|
| refuted | 35/72 | **0.486** | [0.375, 0.611] |
| NEI (claim formed, abstained) | 7/72 | 0.097 | [0.042, 0.167] |
| none (no refutation/abstention) | 30/72 | 0.417 | [0.278, 0.569] |

`refuted + NEI + none = 72`. `NEI` is not a miss. `none` is decomposed below.

### 6.2 Per class

| class | n | refuted | NEI | none | refutation | abstention | extraction miss |
|---|---:|---:|---:|---:|---:|---:|---:|
| `path-location-drift` | 18 | 18 | 0 | 0 | **1.000** | 0.000 | 0.000 |
| `external-dependency-drift` | 18 | 14 | 0 | 4 | **0.778** | 0.000 | 0.222 |
| `identifier-drift` | 18 | 1 | 1 | 16 | **0.056** | 0.056 | 0.889 |
| `removed-referent-drift` | 18 | 2 | 6 | 10 | **0.111** | 0.333 | 0.556 |

Repo-cluster 95% CIs: path 1.000 [1.000, 1.000]; external 0.778 [0.444, 1.000];
identifier 0.056 [0.000, 0.167]; removed-referent 0.111 [0.000, 0.333]. Six
clusters; the intervals are wide and should be read as descriptive.

### 6.3 `none` is not one thing

| `none` subtype | count | meaning |
|---|---:|---|
| `no_claim` | 16 | no claim covers the target line |
| `other_referent` | 8 | a claim covers the line, but its object is a different referent |
| `supported` | 6 | a target claim is formed and wrongly returned `SUPPORTED` |

By class:

| class | no_claim | other_referent | supported |
|---|---:|---:|---:|
| `path-location-drift` | 0 | 0 | 0 |
| `external-dependency-drift` | 0 | 0 | 4 |
| `identifier-drift` | 9 | 6 | 1 |
| `removed-referent-drift` | 7 | 2 | 1 |

The six `supported` cases are:

- **external dependency (4):** three `gaugekit` `numpy>=1.24` cases and one
  `sheetmusic` `click>=8.1` case. The three `gaugekit` cases are a
  **version-extraction** gap: the line `NumPy (numpy>=1.24)` produces a
  `DEPENDENCY numpy` claim with `context.version = null`, so the `>=999`
  mutation is invisible. The `sheetmusic` case is a **disjoint-interval**
  comparison bug: `>=8.1` against `<8.1` is returned `SUPPORTED`. Neither is a
  miss of the dependency mention itself, but they are different engine
  limitations.
- **plotline `Canvas` (2):** the class `Canvas` was renamed to `CanvasInjected`,
  but the module `plotline.canvas` still exists. The bare name `Canvas`
  case-folds to the module name `canvas`, so the tool finds a last-segment
  candidate and returns `SUPPORTED`. This is a false support under the
  bare-name policy: the supporting referent is the module, not the class.

### 6.4 Per claim form

| claim form | n | refuted | NEI | none | refutation |
|---|---:|---:|---:|---:|---:|
| `path` | 18 | 18 | 0 | 0 | **1.000** |
| `dependency` | 18 | 14 | 0 | 4 | **0.778** |
| `qualified` | 1 | 1 | 0 | 0 | **1.000** |
| `bare` | 32 | 2 | 7 | 23 | **0.062** |
| `bare_call` | 3 | 0 | 0 | 3 | **0.000** |

The table is the point: path and dependency claims refute; bare symbol
references mostly do not. The `bare` row is not "32 missed refutations": 7 are
deliberate `NEI` abstentions, 13 are no-claim, 8 are another referent, and 2
are a wrong `SUPPORTED` (the two plotline `Canvas` cases). The three
`bare_call` entries are all no-claim.

### 6.5 End-to-end

Because the two pre-scoring harness defects were fixed and all 72 raw proposals
were valid, the final end-to-end denominator is the same as the verified
denominator:

| class | planned | refuted | NEI | none | end-to-end refutation |
|---|---:|---:|---:|---:|---:|
| `path-location-drift` | 18 | 18 | 0 | 0 | **1.000** |
| `external-dependency-drift` | 18 | 14 | 0 | 4 | **0.778** |
| `identifier-drift` | 18 | 1 | 1 | 16 | **0.056** |
| `removed-referent-drift` | 18 | 2 | 6 | 10 | **0.111** |
| **all** | **72** | **35** | **7** | **30** | **0.486** |

The pre-fix finalize counts are reported in §5.1 so the harness history is not
hidden. The final run has 0 declines and 0 generator failures.

### 6.6 Controls

18 engine-free consistent-present controls (path/dependency/symbol × 6 repos).
A control refutation is a false positive.

| class | n | clean | refuted (FP) | NEI | none | precision |
|---|---:|---:|---:|---:|---:|---:|
| `path-location-drift` | 6 | 6 | 0 | 1 | 5 | **1.000** |
| `external-dependency-drift` | 6 | 6 | 0 | 0 | 6 | **1.000** |
| `identifier-drift` | 6 | 6 | 0 | 0 | 6 | **1.000** |
| **all** | **18** | **18** | **0** | **1** | **17** | **1.000** |

The non-refuted controls are not 17 extraction misses: **13** formed a
`SUPPORTED` claim, **1** was `NEI`, **2** had no claim, and **2** had another
referent. Precision is therefore 1.0 with 0 false positives, but the evidence is
limited: four controls were not extracted, and the controls are constructed
rather than sampled from natural defect-free claims.

### 6.7 Detection is not bound to the recorded line

29/35 refutations matched a finding on the recorded target line; **6/35** were
found through another document mention, which the protocol allows. The clearest
case: the `gridwatch` identifier target `read_json` (`docs/api.md:27`) and the
removed-referent target `read_json` (`docs/api.md:27`) are refuted through the
qualified mention `gridwatch.readers.read_json` at `docs/guide.md:36`. All three
symbol refutations in the corpus are the same `read_json` symbol; the symbol
classes are therefore much less independent than their 18-entry denominators
suggest.

### 6.8 Effective sample size

The 72 entries are not 72 independent claims:

| class | entries | distinct `(repo, target)` |
|---|---:|---:|
| `path-location-drift` | 18 | **6** |
| `external-dependency-drift` | 18 | **8** |
| `identifier-drift` | 18 | **15** |
| `removed-referent-drift` | 18 | **14** |

The three seeds often select the same natural target. The headline CI resamples
the six repositories, not the 72 entries, precisely because the entries cluster.
Even the repo-cluster bootstrap does not capture the within-repo concentration
of the `read_json` refutations; this is a caveat, not a correction.

---

## 7. Baseline findings

The frozen baselines contain **0 `REFUTED`** claims across all six repos:

| repo | claims | SUPPORTED | NEI | REFUTED |
|---|---:|---:|---:|---:|
| `gaugekit` | 34 | 24 | 10 | 0 |
| `gridwatch` | 49 | 37 | 12 | 0 |
| `plotline` | 45 | 31 | 14 | 0 |
| `palette` | 50 | 32 | 18 | 0 |
| `sheetmusic` | 41 | 28 | 13 | 0 |
| `recipecard` | 41 | 30 | 11 | 0 |
| **all** | **260** | **182** | **78** | **0** |

There were no baseline findings to adjudicate as true documentation bugs or tool
false positives. `baseline_findings.json` is empty; `baseline_summary.json`
records the counts. The recorded adjudicator model (Qwen3.8 Flash) was therefore
not exercised.

**A 0-`REFUTED` baseline is not evidence of real-world precision.** These docs
were written to be accurate against a spec and a deliberately small source tree,
and the engine was not used to accept or repair them. Stage A's
`baseline_evidence.md` shows tens of baseline `REFUTED` claims on real repos,
several of them false positives. Stage B does not overturn that; it simply has
no baseline findings to adjudicate.

---

## 8. Independent annotation and IAA

**Status: no independent annotation.** Stage B claims **no independent labels**
and computes **no IAA**. No model labels have been substituted for independent
labels.

The blind sheet `annotation_sheet.jsonl` has **90 rows** (72 verified injections
+ 18 controls). It contains the doc line, target, mutation (`old` → `new`),
symbol, and target claim, but **no tool verdict, layer, reason, or reaction**.
It was generated mechanically from the frozen manifest and controls; because it
contains no tool output, the annotators remain blind even though the file was
written after the scoring pass. `ANNOTATION.md` defines the fields, the
miss/abstention/control streams, and the IAA target (Cohen's κ ≥ 0.60, reported
whatever it is). When two annotators are
available, the sheet is ready for them; until then this section remains a
blocker, not a result.

---

## 9. What Stage B does not establish

1. **No independent labels.** The annotation sheet is blank. The corpus audit is
   model-based.
2. **Not an open-world benchmark.** It tests only the six declared predicates
   and the four active injection classes. `VERSION`, doc drift, value drift, and
   cross-document drift are not tested.
3. **Not behavior/semantics.** The docs are checked against a small structural
   inventory; behavior, signatures, security, and prose quality are out of
   scope.
4. **Not a population estimate.** Six synthetic repos in three domains are not a
   random sample of open-source projects.
5. **Not a measure of the injector's realism.** The injector is a construction
   tool; its outputs were verified mechanically, not judged as realistic bug
   reports.
6. **Not a precision estimate beyond the controls.** The 18 controls show 0
   false positives, but 4 were not extracted and they are constructed.
7. **Not a paired comparison with Stage A.** The corpus, doc style, and class
   mix differ. The direction is consistent, but the numbers are not paired.
8. **Not a basis for tuning.** Any tool limitation found here is reported and
   left for a later development cycle. Stage B was not used to change prompts,
   specs, or tool code.

---

## 10. Comparison with Stage A (descriptive only)

| | Stage A | Stage B |
|---|---|---|
| corpus | 4 dev repos, same specs | 6 new repos, natural specs |
| docs | natural prompt | natural prompt |
| bundles | 48 active | 72 |
| verified | 32/48 | 72/72 after harness fixes |
| refuted | 18/32 = 0.5625 | 35/72 = 0.486 |
| NEI | 10/32 = 0.3125 | 7/72 = 0.097 |
| none | 4/32 = 0.125 | 30/72 = 0.417 |
| controls | none | 18, 0 false positives |

The composition changed: Stage A's symbol misses were mostly **abstentions** on
bare calls (`NEI "unresolved bare name"`); Stage B's symbol misses are mostly
**no claim at all** on bare names in API headings, plus a few refutations through
a qualified mention. That is a different natural-document style, not a paired
improvement or regression. Path remains strong; dependency is moderate; symbol
refutation is limited by the bare-name policy and by extraction.

### 10.1 Post-B engine follow-ups

The prioritized post-B engine work is in **`ENGINE_FOLLOWUPS.md`**. It keeps the
bare-name policy unchanged. The only real refutation bugs are E1 (a duplicate
dependency mention loses the versioned occurrence: 3 `gaugekit` cases) and E2
(disjoint constraint intervals: 1 `sheetmusic` case); fixing both gives
**39/72 (0.542)**. E3 removes 2 false `SUPPORTED` by a same-name module
(`Canvas`), converting them to `NEI`, not `REFUTED`. E4/E5 **bare anchoring**
improves extraction and attribution (`none` → `NEI`/`SUPPORTED`) but does not
raise refutation.

A **post-hoc trial** of a stronger variant — qualify the bare name with the
document's own module heading/table/prose context — reached **68/72 (0.944)**
on the frozen snapshots, with 0 baseline/control false positives. With the E1/E2
dependency fixes it reaches **72/72 credited**, **63/72 target-line**. That is a
**claim-scope extension** (`section-qualified name`), not the Stage B headline,
and 9/72 refutations come from another mention. The real-repo precision audit
found the symbol rule nearly dormant (no visible trial-specific false
positives, but low power) and E1 amplifying pre-existing migration/
compatibility false positives; E6 (implemented) gates those prose contexts and
drops the targeted real-repo FPs (fastapi 75→55, prefect 7→6, sklearn 30→26)
without changing Stage B. See `regression-context-qualification/README.md`,
`regression-trial-plus-e1e2/README.md`, and
`regression-trial-e1e2-e6/README.md`; adoption requires a `SCOPE.md` decision
and a new held-out evaluation.

---

## 11. Reproduction

```bash
ROOT=.
B=$ROOT/research/submission/demo/injected_gold
RUN=$B/llm_injection/runs/stage-b-2026-10-20

# corpus (already generated and frozen; do not edit after freeze)
for r in gaugekit gridwatch plotline palette sheetmusic recipecard; do
  PYTHONPATH=src uv run python $B/scripts/generate_synthetic.py spec-validate \
      --spec $B/synthetic-natural/$r/spec.json
  PYTHONPATH=src uv run python $B/scripts/generate_synthetic.py materialize \
      --spec $B/synthetic-natural/$r/spec.json --out $B/synthetic-natural/$r
done

# freeze verification
PYTHONPATH=src uv run python $B/scripts/freeze_corpus.py --verify \
    --freeze $RUN/corpus_freeze.json

# injector (already run; snapshots/provenance are regenerable)
PYTHONPATH=src uv run python $B/llm_injection/scripts/llm_inject.py prepare \
    --repos gaugekit,gridwatch,plotline,palette,sheetmusic,recipecard \
    --seeds 1,2,3 --samples 1 --prompts $RUN/prompts_natural --out $RUN
PYTHONPATH=src uv run python $B/llm_injection/scripts/llm_inject.py run \
    --model opencode-go/deepseek-v4.1-flash --out $RUN
PYTHONPATH=src uv run python $B/llm_injection/scripts/llm_inject.py finalize --out $RUN

# scoring (engine invoked here and only here)
cat $RUN/manifest.jsonl $RUN/controls.jsonl > $RUN/scoring_manifest.jsonl
PYTHONPATH=src uv run python $B/scripts/score_injections.py \
    --manifest $RUN/scoring_manifest.jsonl --snapshots $RUN/snapshots \
    --out $RUN --seed 1
PYTHONPATH=src uv run python $B/scripts/stage_b_metrics.py --run $RUN

# annotation sheet
PYTHONPATH=src uv run python $B/scripts/build_annotation_sheet.py --run $RUN
```

---

## 12. Bottom line

On a new, frozen, independently audited natural corpus, the current tool
refutes **35/72 (0.486)** verified active-class injections, with **7/72 NEI**
and **30/72 none**. Path-location drift is fully refuted (18/18); external
dependency is moderate (14/18, with 3 version-extraction false supports and 1
disjoint-interval false support); identifier and removed-referent are weak
(1/18 and 2/18), mostly because natural API references are bare names that are
often not extracted at all, not because the tool abstains.

Controls show **0 false positives in 18**, but 13 controls were `SUPPORTED`, 1
was `NEI`, and 4 were not extracted, so precision evidence is limited. The
baseline has 0 `REFUTED` claims; that is a clean-by-construction corpus, not a
real-world precision result.

The remaining blocker is independent annotation: the blind 90-row sheet is ready, but
there are no independent labels and no IAA yet. Stage B was held out and was not used to
tune prompts, specs, or tool code.
