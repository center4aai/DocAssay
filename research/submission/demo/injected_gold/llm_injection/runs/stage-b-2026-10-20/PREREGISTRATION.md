# Stage B — preregistration

**Date:** 2026-10-20
**Branch:** `demo` (no new branch)
**Status:** written **before** corpus generation, before prompt finalization, and
before any engine or injector run.
**Run directory:** `research/submission/demo/injected_gold/llm_injection/runs/stage-b-2026-10-20/`

This file is the preregistration for Stage B, a **held-out natural-corpus**
evaluation of the current documentation verifier. Stage B is designed **after**
Stage A (`../stage-a-2026-10-20/`) but uses a **new corpus**, a **new
documentation writer contract**, a **new injector contract**, and **controls**.
It is not used to tune prompts, specs, or tool code.

---

## 1. Question

Stage A showed that the checker-shaped 0.925 headline was substantially a
property of benchmark construction: on natural documents, with no extractor
preconditions in the docwriter or injector prompts, active four-class
refutation was **18/32 (0.5625)**, with **10/32 NEI** and **4/32 none**.

Stage B asks the next question:

> On a **new, frozen, independently audited natural corpus** that was never used
> to build the tool or the exemplar bank, what does the **current** tool do on
> the four active injection classes, with a transparent three-outcome report,
> controls, and a held-out corpus?

Stage B evaluates the tool **as-is**. It does not test VERSION, doc drift,
value drift, cross-document drift, or any class outside the active four.

---

## 2. Hypotheses (directional; not used for tuning)

These are predictions, not acceptance criteria. They are fixed before the
corpus is generated.

- **H1 (paths).** `path-location-drift` refutation will be the strongest class:
  natural Markdown links and inline-code paths are still anchored, and a path is
  often mentioned in more than one document. Predicted refutation ≥ 0.60.
- **H2 (symbols).** `identifier-drift` and `removed-referent-drift` will show
  many deliberate `NEI` abstentions under the bare-name policy (`SCOPE.md`
  §3.3.1). Predicted refutation ≤ 0.40 for each; abstention ≥ 0.40 for each;
  qualified claims will refute more often than bare calls or bare names.
- **H3 (dependencies).** `external-dependency-drift` will be moderate.
  Constraint-form injections should refute more often than removal-form
  injections, because the current `DEPENDENCY` predicate abstains on an
  undeclared dependency (`NEI "undeclared (open by transitivity)"`). Predicted
  refutation 0.30–0.75 overall.
- **H4 (baseline).** At least one of the six frozen baselines will contain a
  `REFUTED` finding, and at least one baseline finding will be adjudicated a
  tool false positive. A 0-`REFUTED` baseline is not an acceptance criterion.
- **H5 (controls).** Consistent-present controls will mostly stay clean, but
  precision is not assumed to be 1.0. Predicted control precision ≥ 0.85.
- **H6 (generator).** Declines and generator failures will occur. Predicted
  end-to-end verified fraction ≥ 0.70. If it is lower, that is reported as a
  corpus/injector result and is **not** repaired by tuning on Stage B.

---

## 3. Metrics and estimands

Every planned bundle has exactly one injector outcome. Every **verified**
injection has exactly one tool outcome read from the tool's reaction to the
target claim:

| outcome | definition |
|---|---|
| `refuted` | the target claim is formed and `REFUTED` against a closed inventory |
| `nei` | the target claim is formed and the predicate abstains (`NEI`), with layer and verbatim reason |
| `none` | no claim formed, a claim formed at a different referent, or a formed target claim wrongly `SUPPORTED` (sub-flagged) |

Reported metrics, per class and per claim form, with raw counts:

- **Refutation rate** = `refuted / verified`.
- **Abstention rate** = `nei / verified`.
- **Extraction-miss rate** = `none / verified`.
- **End-to-end refutation** = `refuted / planned bundles` (72), so declines and
  generator failures are in the denominator and are not hidden.
- **Verified fraction** = `verified / planned bundles`.
- **Decline rate** and **generator-failure rate**, separately.
- **Controls precision** = clean controls / controls, with the `NEI` / `none`
  split of the non-refuted controls reported alongside; every control
  refutation is listed as a false positive.
- **Baseline findings**: every baseline `REFUTED` claim, adjudicated as
  `true_doc_bug`, `tool_false_positive`, or `undetermined`.
- **Unattributed findings** on injected trees as a precision proxy.
- **Cluster-aware 95% CI**: bootstrap by **repository** (6 clusters, 10,000
  replicates, fixed seed), not Wilson on 72 allegedly independent injections.

`NEI` is not a miss and is never folded into the refutation numerator or the
extraction-miss rate. `refuted + nei + none = verified` for every class.

No single aggregate score is reported as the headline.

---

## 4. Corpus: six repos, three domains

The corpus is **new** (`synthetic-natural/`) and does not reuse the four
dev/regression repos (`quillpad`, `tidecast`, `ledgerly`, `parcelroute`).

| repo | domain | natural project |
|---|---|---|
| `gaugekit` | environmental data | stream-gauge CSV loading and summary statistics |
| `gridwatch` | energy/utility data | smart-meter interval parsing and tariff calculation |
| `plotline` | creative/visual | SVG chart primitives (scales, marks, canvas) |
| `palette` | creative/visual | color palette generation and contrast checks |
| `sheetmusic` | music | chord/progression parsing and transposition |
| `recipecard` | everyday/consumer | recipe scaling and shopping-list generation |

**Domains:** environmental/energy data (2), creative/visual (2), music/everyday
(2). Three domains total.

**Why these are not tool-shaped.** They are ordinary small libraries/CLIs, not
API-service checklists. The corpus is designed from what the software does, not
from a list of surfaces. There is no mandated HTTP route table, schema-field
list, enum-member list, config-key inventory, or example-command inventory.
Those surfaces are **optional** in the spec schema and are included only when
the project naturally has them. Omissions in the docs are allowed. The
documentation is written for a human reader, with no fixed template for version
lines, symbol references, path references, or dependency mentions.

**Pre-registered backups.** If a primary repo fails twice at spec generation or
doc generation, it is replaced by a backup and the substitution is recorded:
`beaconlog` (structured logging for CLIs) or `unitwise` (unit conversion).
Backups are not used to replace a repo because of anything the tool says.

---

## 5. Active classes and claim forms

Four active classes only:

1. `path-location-drift` — a current location is renamed/moved; the doc still
   points at the old location.
2. `identifier-drift` — a current class/function definition is renamed; the doc
   still names the old symbol.
3. `removed-referent-drift` — a current class/function definition is deleted;
   the doc still names it.
4. `external-dependency-drift` — a current dependency requirement is broken
   (constraint no longer intersects the documented requirement) or the
   dependency is removed from the manifest; the doc still states it.

No `VERSION`, no `doc_drift`, no `value-drift`, no
`cross-document-drift` injection.

Claim forms recorded by the scorer: `path`, `dependency`, `qualified`,
`bare_call`, `bare`.

The `SYMBOL_EXISTS` bare-name policy is **kept**. Stage B evaluates the current
tool; bare-name abstention is a deliberate `NEI`, not a miss. Tool fixes are a
separate development cycle **after** B.

---

## 6. Corpus acceptance criteria (independent audit, not the engine)

A repo is accepted into the frozen corpus only if:

1. `spec.json` validates under `generate_synthetic.py spec-validate`.
2. Deterministic materialization produces a parseable Python tree and
   `pyproject.toml`.
3. The three documents exist, are English, and are not a changelog, release
   notes, or roadmap.
4. An **independent auditor** (`repo-auditor`, model family different from the
   docwriter) checks every factual statement in the docs against the spec and
   source and reports `CONSISTENT` after fixes.
5. Only **factual** errors are fixed. Style, omissions, and non-factual prose
   are not changed. Every fix is recorded with `file:line`, the statement, the
   correction, and the audit finding.
6. The engine is **not** used to accept, reject, select, or repair a repo.

The engine may run **after** freeze as a diagnostic. Its findings are recorded,
never used to edit the corpus.

---

## 7. Annotation protocol and IAA

Target: **two independent annotators**, blind to the tool's verdicts.
Every verified injection and every control is annotated (not a subsample unless
the sheet is too large; if subsampled, the sampling rule is recorded).

Annotation fields per row:

- `claim_type`: `current_claim` / `historical` / `illustrative` / `conditional`
  / `not_a_claim`
- `claim_form`: `qualified` / `bare_call` / `bare` / `path` / `dependency`
- `defect_is_real`: `yes` / `no`
- `nei_reason_applies`: `yes` / `no` / `n/a` (for `NEI` outcomes)
- `none_claim_not_extracted`: `yes` / `no` / `n/a` (for `none` outcomes)
- `control_false_positive`: `yes` / `no` / `n/a` (for controls)
- `annotator_id`, `notes`

The annotation sheet contains the doc line, the target claim, and the mutation
(`old` → `new`) but **no tool verdict, layer, reason, or reaction**.

IAA: Cohen's κ on `defect_is_real` and on `claim_type`, plus the miss stream
(`none_claim_not_extracted`), the abstention stream (`nei_reason_applies`), and
the control stream (`control_false_positive`). Target κ ≥ 0.60; the observed κ
is reported whatever it is. If only one annotator is available, no IAA is
claimed. If independent annotation is not available, the sheet and instructions are
produced and the lack of independent labels is reported as a **blocker**; LLM labels
are never presented as independent labels.

**Current status:** independent annotation is not included.
Stage B reports no independent labels and no IAA.

---

## 8. Controls

- **Consistent-present (required):** a current-state doc claim about an artifact
  that exists and is consistent with the spec/source (a live path, a declared
  dependency, a qualified symbol that resolves, a license/Docker/CI claim that
  is true). Expected: **not refuted**.
- **Consistent-absent (optional):** a current-state doc claim that an artifact
  is absent, where it is in fact absent (e.g. "no Dockerfile is shipped").
  Expected: **not refuted**. If no natural consistent-absent statement exists,
  the arm reports zero and does not invent one.

Controls are selected **engine-free**, from the docs and the structural
inventory, before scoring. They are not selected from the tool's claims. A
control refutation is a false positive regardless of rate.

Controls cover the four active classes; where a capability predicate
(`LICENSE`, `HAS_DOCKERFILE`, `HAS_CI_WORKFLOW`) has a naturally true claim,
an opportunistic control is added and reported separately. They are not pooled
into the four-class refutation denominator.

---

## 9. Stop rules

**Corpus generation.**
- Two attempts per primary repo. If both fail, use a pre-registered backup and
  record the substitution and reason.
- Do not select or repair a repo on the basis of engine output.
- Do not edit docs after freeze.

**Injector.**
- One attempt per bundle. No retry of a substantive decline
  (`injectable:false`) or a substantive generator failure; retrying would bias
  the sample.
- One retry is allowed only for an **infrastructure** failure (timeout, no JSON
  because the runner failed). If the retry also fails, it is a generator
  failure.
- If the injector model is unavailable for most bundles, stop and report; do
  not silently substitute a different model family.
- Declines and failures are counted in the end-to-end denominator.

**Freeze.**
- The corpus, specs, prompts, and model IDs are hashed into
  `corpus_freeze.json` before any injector or scoring run.
- `freeze_corpus.py --verify` must pass before scoring.
- If a corpus file changes after freeze, the run is invalid. A repair is a new
  corpus version with a new freeze, and both versions are reported.

---

## 10. Freeze and provenance

`corpus_freeze.json` records:

- SHA-256 of every corpus file (source, `pyproject.toml`, `spec.json`, docs,
  example data), excluding `__pycache__`, `.pyc`, `.DS_Store`, and `.git`;
- an aggregate SHA-256 over the sorted `path:hash` lines;
- SHA-256 of every docwriter, auditor, injector-system, per-class, and output
  schema prompt;
- SHA-256 of the agent prompt files;
- exact model IDs and a SHA-256 of each ID string;
- freeze timestamp, branch, and git commit;
- a note that baseline findings are diagnostic, not acceptance criteria.

`provenance.json` records, per bundle: repo, class, seed, snapshot ID, prompt
SHA-256, model ID, exemplar IDs, verifier result, and status
(`verified` / `declined` / `invalid` / `unresolved` / `verify_failed` /
`conflict` / `apply_failed` / `timeout` / `no_output`).

---

## 11. What Stage B does not establish

- It is **not** an open-world benchmark. It tests only the declared six
  predicates and the four active injection classes.
- It is **not** an independent reference unless independent annotation is completed.
- It is **not** a population estimate for real repositories or organic defects.
  Six small synthetic repos are not a random sample of open-source projects.
- It is **not** a test of behavior/semantics, prose quality, or the ten
  catalog-in-scope classes with no predicate.
- It is **not** a measure of the injector's realism; the injector is a benchmark
  construction tool, and its outputs are verified mechanically.
- It is **not** a precision estimate beyond the controls.
- It is **not** a paired comparison with Stage A; the corpora differ.

---

## 12. Hold-out statement

Stage B is **held out**. The corpus is generated and frozen **before** the tool
is run. The tool, prompts, specs, and analysis scripts are **not** tuned on
Stage B after seeing its results. Any tool limitation found is reported and
fixed only in a **later** development cycle, not here.

---

## 13. Recorded deviation: auditor model (2026-10-20)

The planned independent auditor was `opencode-go/gpt-6-luna` (OpenAI family).
It is unavailable in this environment (`Country, region, or territory not
supported`). `opencode-go/gemini-4-argon-contributor` was blocked by workspace
privacy settings (`trains on request data`), and `opencode-go/grok-4.7`
returned `Endpoint is unavailable`. The audit therefore uses
**`opencode-go/qwen3.8-flash`** (Alibaba/Qwen family), which is a different
model family from the Claude docwriter and therefore satisfies the independence
requirement. This substitution was made **before the corpus freeze** and
**before any engine or injector run**; it is an infrastructure substitution,
not a result-driven change. It is recorded in `audit/audit.json` and in
`corpus_freeze.json`.

---

## Appendix A — planned design

- 6 repos × 4 classes × 3 seeds = **72 bundles**.
- One mutation per snapshot: each bundle gets its own git-less baseline and
  injected snapshot (`<repo>__<class>__s<seed>_<sample>`).
- Docwriter: `opencode-go/claude-haiku-5-5` (Claude family).
- Injector: `opencode-go/deepseek-v4.1-flash` (DeepSeek family; different from
  the docwriter).
- Auditor / baseline adjudicator: `opencode-go/qwen3.8-flash` (Alibaba/Qwen
  family; different from the docwriter). The planned GPT-6 Luna auditor was
  region-blocked; see §13.
- Architect: `opencode-go/claude-haiku-5-5`.
- Corpus: `research/submission/demo/injected_gold/synthetic-natural/`.
- Run artifacts: this directory.
