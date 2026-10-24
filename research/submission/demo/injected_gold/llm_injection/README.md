# LLM injection — source-grounded few-shot injector

> Status: **draft, active (2026-10-13).** This subtree implements the
> **injection** step of the operative tool-validation protocol
> (`../../validation/protocol.md` §2, §4.2): manufacture known defects whose
> *distribution* is grounded in real, human-triaged incidents, then let the
> engine-free harness verify them. It does **not** run the engine, apply
> mutations, or score; those stages live in `../scripts/` and are unchanged.

## Why a separate subtree

The deterministic operator registry (now archived under
the private deterministic-operator archive (not shipped)) was a set of
**deterministic, hand-written** target selections. `protocol.md` §4.2 replaces it
as the *headline* injection source with an LLM injector that receives
**few-shot exemplars from real bugs** and produces an *analogous* defect. This
subtree holds the two artifacts that step needs — an **exemplar bank** and
**injector prompts**. The surviving mechanics (the mutation grammar and the
engine-free oracle) live in `../engine/`; the injector's output schema is
field-compatible with `../engine/oracle.py:verify_entry`.

## Layout

```
llm_injection/
  README.md
  exemplars/
    rules.json     # FROZEN deterministic keyword ruleset (class assignment)
    bank.json      # generated bank (do not edit by hand)
    bank.md        # human-readable rendering
    evidence/      # extracted before/after evidence per triaged exemplar (committed)
    cache/         # raw fetched .patch files (gitignored, regenerable)
  prompts/
    injector.system.md        # shared contract (constraints, process, self-check)
    class.<drift>.md ×  5     # per-class definition + output skeleton + placeholders
    output.schema.json        # JSON Schema for the injector's mutation object
  scripts/
    build_exemplar_bank.py    # stdlib-only, deterministic bank builder (+ --check)
    fetch_exemplar_evidence.py# one-time network step: commit_url -> before/after
    llm_inject.py             # runner: prepare -> run injector -> finalize
```

## Bank provenance and pooling rule

Sources (all local, read-only):

| pool | source | kind | role |
|---|---|---|---|
| `triaged` | `other_instruments/readu/data/analysis/READU_tp.md` | human-triaged true positives | **primary bank** |
| `triaged` | `exemplars/sources/curated_triaged.json` | manually commit-verified real incidents | **top-up for thin classes** |
| `raw` | `other_instruments/readu/data/dataset/*.json` → `potential_readme_bug_scenarios` | LLM-derived hypotheses | **separate, labelled pool** |
| `controls` | `other_instruments/readu/data/analysis/READU_fp.md` | human-triaged false positives | negative exemplars |

Per `protocol.md` §2 the `raw` (LLM hypothesis) pool is **never mixed into** the
primary `triaged` bank; `bank.json` keeps them in separate arrays under each
class. The curated layer is also triaged: each row cites a public commit whose
parent tree already carried the renamed identifier, and
the document line was repaired in that commit. It is never populated from
`readu_raw`. CASCADE's method-level `inco` labels are almost entirely **out of scope**
for the four predicate-backed classes and are not harvested here (they remain the
boundary layer in `../catalog_external.json` and `../operators/boundary.json`).

Each exemplar records `{id, pool, label, repo, commit_url, location, quote,
matched_rule, evidence}`; curated triaged rows and controls additionally carry
`triage_note`. `commit_url` is bank provenance only and is **never rendered into
the injector prompt**.

## Offline evidence enrichment

`protocol.md` §4.2 wants few-shot exemplars that anchor target selection. The
READU sources store only a prose alert + `location`, no diffs. So a **one-time
network step**, `scripts/fetch_exemplar_evidence.py`, fetches each triaged
exemplar's `<commit_url>.patch`, parses the unified diff into per-file hunks,
matches the files against the alert's `location`, and writes an extracted
evidence JSON under `exemplars/evidence/` (committed). The bank builder embeds it;
**the injector only ever reads the local bank and never touches the network**
(enforced by `injector.system.md` constraint 8).

- Raw patches are cached under `exemplars/cache/` (gitignored, regenerable).
- Each evidence file: `{status, commit_sha, patch_sha256, locations, files:[{path,
  side: doc|code, removed, added, hunks, truncated, matched_location}]}`. No
  timestamps (deterministic).
- Coverage today: 49/49 triaged exemplars enriched; 41 matched the alert
  `location`, 8 fall back to a capped diffstat (the patch touched other files).
- Anonymous GitHub allows ~60 requests/hour; set `GITHUB_TOKEN` for larger runs.
  `--offline` rebuilds evidence from cache; `--resume` continues after a rate limit.

In the prompt each example is rendered **diff-only**, with one header line and no
URL, no alert prose:

```
### example 1
docs/cloud.md (doc)
  - # Turbo
  + # Cloud
```

## Class assignment (frozen rules)

`exemplars/rules.json` is a **frozen, engine-free** ruleset that assigns each
incident to one of the four in-scope canonical classes by ordered keyword
precedence (`path-location-drift` → `external-dependency-drift` →
`removed-referent-drift` → `identifier-drift`). It decides **class membership
only**; it never judges whether an incident is a real defect and never reads
`src/docassay/`. To change assignment, edit `rules.json` and regenerate.

The current ruleset is version `2026-10-20`. It adds an explicit `none_of` guard
to `path-location-drift` (so `code renamed it to ...` reaches the identifier
class) and a present-tense `renames it to` pattern to `identifier-drift`. This
moves two real READU field-rename incidents into `identifier-drift` (one from
`unclassified`, one from `path-location-drift`); the raw pool is unchanged.

### Coverage caveat (read this)

Deterministic keyword assignment over READU still yields a **thin, noisy**
per-class bank, and the real-incident distribution does not line up 1:1 with our
narrow predicates:

- `identifier-drift` is topped up by four real symbol-rename fixes;
  the two reclassified READU rows are field/DTO renames, so the class is broader
  than the injector's top-level class/function target rule.
- `external-dependency-drift` inherits READU's broader external-resource theme
  (registries, URLs, minimum tool versions), which is wider than a declared
  manifest entry.
- CASCADE contributes effectively nothing in scope.

The exemplars therefore anchor **which kind of artifact tends to drift** (target
selection), not phrasing and not a 1:1 class match — exactly the role
`protocol.md` §4.2 assigns them.

## Prompt contract

A fully assembled prompt is four blocks **in this order**:

1. `injector.system.md` — the invariants: one drift type per injection; analogy
   not imitation; a structured mutation against a **named** artifact;
   mechanically checkable (`old` before, `new` after, file still parses); in scope
   only; **no tool awareness** (told the defect, never the detector); **no
   network**.
2. `class.<drift>.md` — the class definition, target-selection rules, and the
   required output skeleton (with the harness dispatch `kind` pre-filled).
3. the **target repository** (inventory + document excerpts).
4. the **examples** (few-shot, last — closest to generation): bare
   `before → after` excerpts.

The class file's placeholders:

| placeholder | filled with |
|---|---|
| `{{REPO_INVENTORY}}` | engine-free structural inventory of the target corpus repo |
| `{{DOC_EXCERPTS}}` | the documents the engine's corpus scope would scan |
| `{{EXEMPLARS}}` | the class's triaged exemplars as diff-only excerpts (URL/prose stripped; exemplars without evidence are omitted) |

The injector emits **one** JSON object matching `prompts/output.schema.json`, or
`{"injectable": false, "reason": "…"}`.

## Authorship / style-leak guard

`protocol.md` §4.2 requires the injector to use a **different model/prompt
family** from the author of the clean corpus documents. The synthetic corpus docs
are written by the `repo-docwriter` subagent (`.opencode/agents/repo-docwriter.md`);
the injector is a separate agent (`repo-injector`) and the injection run must use a
different model family. Keep mutated text minimal so the prose voice does not
change.

## Regeneration

```bash
B=research/submission/demo/injected_gold/llm_injection
# 1) one-time network step (triaged exemplars -> exemplars/evidence/)
PYTHONPATH=src uv run python $B/scripts/fetch_exemplar_evidence.py            # triaged
PYTHONPATH=src uv run python $B/scripts/fetch_exemplar_evidence.py --offline  # cache only
# 2) offline, deterministic bank build
PYTHONPATH=src uv run python $B/scripts/build_exemplar_bank.py
PYTHONPATH=src uv run python $B/scripts/build_exemplar_bank.py --check
```

`--check` fails if `bank.json`/`bank.md` are stale, if the sources or embedded
evidence changed under the frozen ruleset, or if a target class has no exemplar.

## Runner (autonomous, offline)

`scripts/llm_inject.py` runs the three stages (or all at once):

```bash
B=research/submission/demo/injected_gold/llm_injection
RUN=$B/runs/llm-demo
# assemble prompts + plan (one sample, one seed)
PYTHONPATH=src uv run python $B/scripts/llm_inject.py prepare \
    --repos quillpad --seed 1 --out $RUN
# drive the injector (one call per bundle; model family different from the doc author)
PYTHONPATH=src uv run python $B/scripts/llm_inject.py run \
    --model <provider/model> --out $RUN
# validate + apply + verify + freeze manifest + provenance
PYTHONPATH=src uv run python $B/scripts/llm_inject.py finalize --out $RUN
```

Scaled arm: `--seeds` and `--samples` widen the plan (different exemplar draws
and target samples per `(repo, class)`):

```bash
RUN=$B/runs/scaled-2026-10-19
PYTHONPATH=src uv run python $B/scripts/llm_inject.py prepare \
    --repos quillpad,tidecast,ledgerly,parcelroute \
    --seeds 1,2,3 --samples 1 --out $RUN
PYTHONPATH=src uv run python $B/scripts/llm_inject.py run \
    --model <provider/model> --out $RUN
PYTHONPATH=src uv run python $B/scripts/llm_inject.py finalize --out $RUN
PYTHONPATH=src uv run python $B/scripts/score_injections.py \
    --manifest $RUN/manifest.jsonl --snapshots $RUN/snapshots --out $RUN --seed 1
```

- **prepare** builds, per `(repo, class, seed, sample)`, a four-block prompt into
  `injector_input/` plus `plan.json`. Engine-free (the inventory and excerpts come
  from `_corpus`, never `src/docassay`).
- **run** invokes `opencode run --agent repo-injector --format json`, parses the
  assistant's one JSON object (NDJSON), and writes it to `injector_output/`.
  `--dry-run` skips the model calls. Model can also come from `$INJECTOR_MODEL`.
- **finalize** validates each proposal (`kind`/`drift_type`/required fields),
  resolves the artifact on disk, applies it to a git-less snapshot with the
  frozen applier (`engine.grammar.apply_mutation`), proves it with the engine-free
  oracle (`engine.oracle.verify_entry`), and writes `manifest.jsonl`
  (field-compatible with `score_injections.py`) + `provenance.json` (injector
  model, prompt sha256, seed, exemplar ids, verifier result). It also writes
  `__baseline` snapshots so `score_injections.py` can run unchanged.

Scoring stays separate (engine invoked only here):

```bash
PYTHONPATH=src uv run python $B/scripts/score_injections.py \
    --manifest $RUN/manifest.jsonl --snapshots $RUN/snapshots --out $RUN --seed 1
```

### Run (`runs/llm-demo`, 4 synthetic repos × 1 sample × 4 classes)

16 injections prepared, 16/16 valid proposals, **16/16 verified** by the oracle;
engine recall **0.875** (14/16):

| class | refuted/injected | note |
|---|---|---|
| `path-location-drift` | 4/4 | |
| `identifier-drift` | 4/4 | |
| `removed-referent-drift` | 3/4 | one `none` |
| `external-dependency-drift` | 3/4 | one `none` |

Snapshots/claims are gitignored and regenerable.

### Scaled run (`runs/scaled-2026-10-19`, 4 repos × 4 classes × seeds {1,2,3})

The run yields 48 bundles → **41 verified** by the oracle and overall recall
**37/41 = 0.902**.

| class | refuted/injected | recall [95% CI] |
|---|---|---|
| `path-location-drift` | 12 → 12 | 1.000 [0.76, 1.00] |
| `identifier-drift` | 11 → 10 | 0.909 [0.62, 0.98] |
| `external-dependency-drift` | 9 → 8 | 0.889 [0.57, 0.98] |
| `removed-referent-drift` | 9 → 7 | 0.778 [0.45, 0.94] |
| **overall** | **41 → 37** | **0.902** |

Two fixes moved these numbers:

- `path-location-drift` was **7/12**: the misses referenced `docs/*.md` as **bare
  prose paths**, which `PATH_EXISTS` did not anchor. The extractor now anchors
  **Markdown link/image targets** (`listing.py`); the corpus no longer relies on
  a doc-side backtick rule.

Remaining weak class: `removed-referent-drift` (7/9; 2 `none`).

### Stage A sensitivity run (`runs/stage-a-2026-10-20`)

The checker-shaped corpus above is the development set. Stage A regenerated the
documents without extractor-aware rules and removed the extractor-derived target
rules. On the active four-class scope the result is **18/32 refuted (0.5625),
10/32 NEI (0.3125), 4/32 none (0.125)**; end-to-end **18/48 = 0.375**. The
symbol classes are mostly deliberate `NEI` abstentions on bare names, not
"0/5 detection". Baseline `0 REFUTED` is a diagnostic, not an acceptance gate.
Full report, metrics, and evidence: `runs/stage-a-2026-10-20/`.

### Stage B held-out natural corpus (`runs/stage-b-2026-10-20`)

Stage B is a **new, frozen, independently audited** natural corpus (6 repos,
3 domains) that was not used to build the tool or the bank. It uses the four
active classes, one mutation per snapshot, and 18 engine-free controls. The
final run is **72/72 verified**: **35/72 refuted (0.486)**, **7/72 NEI**, and
**30/72 none**; controls are **18/18 clean** (0 false positives, but 13
supported, 1 NEI, 4 not extracted). Path is 18/18; external dependency 14/18;
identifier 1/18; removed-referent 2/18. The baseline has 0 `REFUTED` claims.
Independent annotation is a gap: the blind 90-row sheet is ready, but there are no
independent labels or IAA yet. Full report: `runs/stage-b-2026-10-20/report.md`; metrics:
`runs/stage-b-2026-10-20/metrics.md`; freeze:
`runs/stage-b-2026-10-20/corpus_freeze.json`. Post-B engine work (bare-name
policy unchanged): `runs/stage-b-2026-10-20/ENGINE_FOLLOWUPS.md`; the real
refutation fixes are +4 (35 → 39/72), while the rest moves `none` to
`NEI`/`SUPPORTED`.

## Deferred

Growing the `raw` pool and widening the corpus. The output schema and manifest
are already field-compatible so these slot in without changing the prompts.
