# Synthetic corpus (2026-10)

A four-repo, **uncontaminated** evaluation corpus for the injected-gold pipeline
(README §9). The smoke/sweep runs use `test_repos/validation_repos`
(`pydantic`, `fastapi`, `bitsandbytes`) — material the engine and its tests were
built on. These repos are generated from scratch and audited independently
against spec and source, so their docs and code agree by construction: every
injected defect is the only difference, and controls are exact.

| repo | theme | manifest | docs | surfaces |
|---|---|---|---|---|
| `quillpad` | local note-taking library (CLI, route table, YAML store) | 1 | 3 | all coverable |
| `tidecast` | weather-forecast cache (CLI, route table, JSON store) | 1 | 3 | all coverable |
| `ledgerly` | double-entry bookkeeping (CLI, route table, CSV store) | 1 | 3 | all coverable |
| `parcelroute` | parcel routing (CLI, route table, TOML store) | 1 | 3 | all coverable |

Each repo is a small flat-layout Python project: `<pkg>/{models,store,…}.py`,
`pyproject.toml`, `README.md`, `docs/{configuration,api}.md`, and an example data
file. The **spec** (`spec.json`) is the single source of truth; the corpus is
generated from it.

## How it is generated

The LLM roles are pre-created OpenCode subagents (`.opencode/agents/`):

- `repo-architect` — writes `spec.json` (project topology, symbols, surfaces).
- `repo-docwriter` — writes `README.md` + `docs/*.md` from the same spec.
- `repo-coder` — writes the source tree from the spec (used in the mode-B pilot).
- `repo-auditor` — read-only consistency audit.

The **deterministic** parts live in `../scripts/generate_synthetic.py`
(`spec-validate`, `materialize`, `baseline-report`). In the locked mode (**A**)
the code is materialized deterministically from the spec; only the prose is
agent-written.

### Regeneration

```bash
B=research/submission/demo/injected_gold
for r in quillpad tidecast ledgerly parcelroute; do
  PYTHONPATH=src uv run python $B/scripts/generate_synthetic.py spec-validate --spec $B/synthetic/$r/spec.json
  PYTHONPATH=src uv run python $B/scripts/generate_synthetic.py materialize  --spec $B/synthetic/$r/spec.json --out $B/synthetic/$r
  # then have the `repo-docwriter` subagent write the docs for $B/synthetic/$r,
  # and the `repo-auditor` subagent audit them against spec + source
  # once the repo is frozen and audited, record the baseline diagnostic:
  PYTHONPATH=src uv run python $B/scripts/generate_synthetic.py baseline-report --repo $B/synthetic/$r
done
```

**`baseline-report` is a diagnostic, not an acceptance gate.** The rule is:

1. Freeze the corpus (spec, code, docs) after the independent audit.
2. Run the baseline diagnostic once and **record** its findings as they are.
3. Do **not** edit docs, swap repos, or otherwise "repair" the corpus to make
   findings disappear. That would tune the corpus to the tool under test and
   hide its baseline false positives.
4. Acceptance is the independent audit (`repo-auditor`: every factual statement
   checked against spec and source), not the engine's verdict counts.

The recorded baseline is the reference point for the per-injection diff: a
finding that appears only after an injection is attributable to that injection;
a finding already present at baseline is reported as a baseline finding, not
silently removed. Target reachability is likewise not gated here — the LLM
injector proposes a target or declines with `injectable: false`.

### Historical full run (deterministic operators, archived)

The deterministic sweep is retired; its code (`inject.py`, `verify_operators.py`)
and its run live under
the private deterministic-operator archive (not shipped). The current headline run is
the LLM injector (`../llm_injection/`), scored by the same `score_injections.py`.

```bash
# (archived) deterministic sweep
# RUN=<private deterministic-operator run: synthetic-2026-10-12>
# PYTHONPATH=src uv run python $B/engine/oracle.py --manifest $RUN/manifest.jsonl --snapshots /tmp/synth-snap
# PYTHONPATH=src uv run python $B/scripts/score_injections.py --manifest $RUN/manifest.jsonl --snapshots /tmp/synth-snap --out $RUN --seed 1
```

## Pilot: how mode A was chosen

The pilot repo (`quillpad`) was built twice and compared on the same independent
audit and on the recorded baseline diagnostic:

| | **mode A** — deterministic code + doc-writer | **mode B** — code-agent + doc-writer |
|---|---|---|
| baseline REFUTED (recorded) | 0 | 0 |
| classes covered | 13/14 | 13/14 |
| code reproducible | yes | no |
| agents used | 1 | 2 |

Both were audited as consistent; mode A was locked because the code is
reproducible (a benchmark corpus should not drift between regenerations) and
coverage is identical. The REFUTED row is a recorded observation, not a pass
criterion.

## First run (archived: `deterministic-operators/runs/synthetic-2026-10-12`)

157 injected entries, 157/157 verified by the stdlib oracle.

- refuted recall **0.697** [0.527, 0.826] (23/33)
- control precision **1.000** [0.904, 1.0] (36/36 clean)
- doc-drift classes 4/84, completeness gap 0/4, external-dependency and value
  0/4 — the classes with no predicate abstain, as the coverage analysis predicts.

## Known limitations

- **`translation-drift` is unreachable**: `_corpus.iter_doc_texts(english_only=True)`
  filters localized copies out of the sampled document set, while
  `_sample_translation` looks for them there. Recorded, not fixed here.
- **`control.dependency.consistent_absent` is unreachable**: its filter requires a
  token that is simultaneously `shape == "symbol"` and free of `.`/`()`.
- The generator materializes a dedicated definition-free module for any literal
  surface (`config.py`, `routes.py`, `constants.py`, `fields.py`) that the spec
  does not already provide, so a `path_rename` never collides with the symbol
  operators.

## Pipeline bugs the corpus surfaced (deterministic pipeline, archived)

Building the corpus exposed five defects in the injection pipeline, all fixed:

1. `_corpus._collect_defs` labelled every top-level function `method`, so
   functions were excluded from the symbol operators.
2. `_corpus.is_translation_path` read the `.md` extension as a language code,
   dropping `README.md` from the injection corpus entirely.
3. `inject._type_candidates` did not strip `()`, so call-form return types never
   matched.
4. `inject._literal_candidates` let the config-key mode accept snake_case (and
   the schema-field mode accept UPPER_SNAKE), so the two stole each other's
   targets.
5. `inject.resolve_repo` rejected a repo directory that had `pyproject.toml` but
   no top-level `*.py`.
6. `inject.py` used the raw `--repos` string as the snapshot id, so an absolute
   path made `snapshots / "<abs>/repo__baseline"` escape the snapshot directory
   and write next to the repository. It now uses the repository's basename.

## Historical corpus fix (2026-10-19) — doc-side part revoked

> **Superseded.** The doc-side change recorded here (backticking `docs/*.md`
> references, and a `repo-docwriter` rule requiring it) is revoked. Editing
> documentation so that an extractor forms a claim is tuning the corpus to the
> tool under test. The doc-writer prompt now gives no formatting requirement of
> that kind, and baseline findings are recorded rather than repaired.

What happened: `quillpad` and `parcelroute` listed their guides as bare prose
paths (`- docs/configuration.md describes …`); the `PATH_EXISTS` extractor
anchors backtick-quoted paths but not a bare `dir/name.ext`, so those references
formed no claim and the `path-location-drift` injections scored 0/2 there. At
the time this was "fixed" on both sides — by backticking the references in the
READMEs **and** by teaching the extractor to anchor **Markdown link/image
targets** (`listing.py`). Only the extractor change stands: closing a real
markdown-link extraction gap is a tool improvement, independent of any corpus.
The resulting `path-location-drift` recall of 12/12 is a property of that
extractor version measured on this corpus, not evidence that the corpus was
required to be REFUTED-free.
