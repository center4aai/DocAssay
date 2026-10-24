# Retrospective — annotation and validation methods tried for the tool validation

> Status: **active, 2026-10-19.** Companion to `protocol.md` (how detection is
> measured) and `SCOPE.md` (what the tool commits to detecting). This document
> records **what was tried, what it produced, and why it was kept or rejected**,
> so a reader does not have to reconstruct the dead ends from git history.
>
> Rejected artifacts are kept in the private archive; this artifact ships only
> the evidence used by the reported results.

The through-line: a gold standard for this tool needs an **objective
denominator**. Verdict labels over a sample drawn *from the tool's own findings*
cannot measure recall, and "all claims in a text window" has no ground truth.
Every method below is judged on three things: **objective denominator**,
**independence** (no tool / author feedback into the labels), and
**reproducibility**.

---

## 1. Methods tried, and their outcome

| # | method | design | headline result | verdict |
|---|---|---|---|---|
| 1 | AI-proxy calibration (archived) | two LLM annotators on a tool-drawn sample | Cohen's κ = **0.629** (< 0.7) | **rejected** — model-based; below target |
| 2 | Document-sampled L1 gold (Task E) | 4 repos × 20 text windows = 80, protocol-free L1 verdicts | committed metrics report **all zeros** | **rejected** — no denominator, metrics inconsistent with sheets |
| 3 | LLM-as-annotator / judge arms | qwen3.8-27b annotation arms (private archive) | strong deference and over-refutation on non-claims | **rejected as annotation**; kept as judge diagnostic |
| 4 | Injection-based conformance | inject known defects; recall = detected / injected | deterministic operators 0.697; LLM few-shot injector 20/20 verified, recall 0.70 | **adopted** |

---

## 2. What each method actually measured

### 2.1 AI-proxy calibration (rejected)

Two language models labelled a sample drawn from the tool's own findings;
agreement was κ = 0.629, below the 0.7 target. Rejected because it uses model labels and because the sample is tool-conditioned. Kept only as history.

### 2.2 Document-sampled L1 gold — Task E (rejected)

Designed to avoid a tool-conditioned sample: sample **fixed text windows**
(20 lines, chosen by position, independent of the tool), have annotators
enumerate checkable claims and give a **protocol-free** L1 verdict
(`agree / disagree / cant-tell / not-about-repo`), and compare to the tool only
afterwards. Frame: 4 single-project repos × 20 windows = 80.

Outcome:

- The annotate sheets **are populated** (per sheet: 41–82 seven-predicate claims,
  48–83 verdicts across the 4 repos).
- But the committed `runs/E_metrics.{md,json}` report **0 external claims, 0 matches,
  recall 0, Jaccard A/B = 1.000** for every repo — i.e. they were computed on
  **empty** sheets and never regenerated. The committed metrics contradict the
  committed sheets.
- There is **no committed IAA / κ computation** anywhere on these sheets, and no
  script that produced them, so the **annotator identity is not fixed** (the
  machine-precise notes suggest an LLM, not two annotators).

Rejected: the method still has **no objective denominator** ("all claims in a
window" is not ground truth), and in this implementation it is not even
internally reproducible. Archived.

> Note on the stated reason. The pivot documents claim the document-sampled gold
> had a **negative inter-annotator κ** (`protocol.md`, `injected_gold/README.md`).
> No committed computation in the tree shows this; the stored metrics are zeros.
> The rejection stands on the denominator argument regardless — but the specific
> κ number is **not currently reproducible** and should not be cited without one.

### 2.3 LLM-as-annotator / judge arms (rejected as annotation)

A separate LLM-as-annotator experiment was rejected: the arms showed strong
**deference** (copying the tool verdict on most answered cases) and
**over-refutation** on non-claims, so an LLM is not a substitute for an
independent annotator. It is retained **only** as a judge / verification
diagnostic (see §4, checker B).

### 2.4 Injection-based conformance (adopted)

Supplies the missing **denominator** by manufacturing known defects:
recall = injected defects the tool refutes / injected defects, with a consistent
control for precision. Pipeline: apply → **engine-free oracle** → run tool →
finding diff → score → adjudicate.

- **Deterministic operators (v1, historical).** A hand-written registry of 20
  operators over 14 in-scope canonical classes. On the synthetic corpus: 157
  injections, 157/157 verified, **refuted recall 0.697** [0.527, 0.826],
  control precision **1.000** (36/36); sweep (fastapi/pydantic/bitsandbytes)
  recall 0.765. The **target selection** in this arm is derived from the engine's
  anchor vocabulary — the circularity the protocol forbids.
- **LLM few-shot injector (current headline).** An injector receives few-shot
  examples — real, human-triaged READU incidents with `before → after` evidence
  extracted from their **real commit patches** — and proposes an **analogous**
  defect (target selection grounded in the incident distribution, not the tool's
  vocabulary). Demo run (`runs/llm-demo`, 4 synthetic repos × 4 active classes):
  **16/16 verified**, engine recall **0.875** (path 4/4, identifier 4/4,
  removed-referent 3/4, external-dependency 3/4).

Adopted. The deterministic registry's role is retained only as the **mutation
grammar** (see §5), not as the headline injection source.

- **Conformance templates (capability predicates).** `LICENSE`,
  `HAS_DOCKERFILE` and `HAS_CI_WORKFLOW` are declared by the tool but had no
  external-catalog rows. Because their referent is fixed by the predicate, they
  are injected as **constructed** cases (`conformance/run.py`, `origin:
  conformance`), reported as a separate arm. Demo: 9 cases, 9/9 verified,
  refuted recall 3/3, controls 5/6 clean (one `license` mention falsely
  refuted). This **closes the predicate-coverage gap**: all six registered
  predicates now have an injection evaluator — four real-incident classes plus
  three conformance classes.

---

## 3. What carries forward

1. **Engine-free oracle** (`engine/oracle.py:verify_entry`) — proves an injection
   on disk without importing the tool.
2. **Deterministic scorer + judges** (`score_injections.py`, `judge_diff.py`,
   `judge_batches.py`/`judge_apply.py`).
3. **Synthetic corpus** (`injected_gold/synthetic/`) — clean by construction, so
   the finding diff is attributable to injections and controls are exact.
4. **Injection protocol + scope** (`protocol.md`, `SCOPE.md`) — pre-declared
   before any scoring run.

---

## 4. The two checkers (architecture)

There are two distinct validations, on opposite sides of the tool run:

| | checker A — injection validity | checker B — detection |
|---|---|---|
| **question** | does the injected defect really exist on disk, and which claim does it invalidate? | did the tool react to that artifact, and how? |
| **when** | **before** the tool runs | after the tool runs |
| **who** | `engine/oracle.py:verify_entry` (engine-free, stdlib, per `kind`) | `score_injections.py` (finding-diff match) + judges |
| **output** | `{old present before / new after, file parses, artifact absent/renamed, target claim}` | reaction `refuted / nei / doc_conflict / none` per injected artifact |
| **why it matters** | a generator defect is dropped **before scoring**, so a miss cannot be confused with a bad injection | recall = `refuted / injected`; the stage attribution says *where* a miss happened |

Checker B is **not** a per-operator answer-checker: it scans the whole
baseline→injected finding diff for a new claim whose referent matches the
injected artifact. Adjudication of the reaction is done by **two independent
judges** (an LLM judge and our own deterministic diff judge), whose agreement is
reported; disagreements are resolved manually.

---

## 5. Residual dependence on the hand-written operators

The LLM path does **not** use the operator **registry**. The dependency is on the
mutation **grammar**, which is shared code:

| layer | what it is | used by LLM path? |
|---|---|---|
| operator registry (archived) | 20 hand-written **target-selection presets** (class → kind + required surface) | **no** — only the retired `inject.py main()` |
| `kind` enum (`path_rename`, `symbol_rename`, `symbol_delete`, `dependency_version_break`, …) | the **mutation grammar** | **yes** — fixed per class (`CLASS_TO_KIND`) |
| `engine/grammar.py:apply_mutation` / `resources` | the generic applier, keyed by `kind` | **yes** |
| `engine/oracle.py:_CHECKS` | the engine-free oracle, keyed by `kind` | **yes** |

So:

- The LLM chooses **which artifact and what content** to drift (grounded in real
  incidents). It does **not** choose the **kind** of mutation: that is pre-filled
  per class by the harness.
- Archiving the registry removes the circular **target selection** but does
  **not** remove the grammar dependency — the grammar now lives in
  `engine/grammar.py` and `engine/oracle.py`.
- **Honest residual constraint:** the 5 kinds line up 1:1 with the 5
  predicate-expressible classes, so the injectable taxonomy is bounded by the
  tool's declared scope. This is intended for a conformance test (scope is
  pre-declared in `SCOPE.md`), but it means the gain in defensibility comes from
  **target selection and the real-incident distribution**, not from the taxonomy.
  State this explicitly; do not present the injection set as open-ended.

---

## 6. Open weaknesses to close before finalizing the artifact

1. **Thin few-shot bank per class.** Triaged exemplars: path-location 13,
   external-dependency 11, removed-referent 9, **identifier 2, value 1**. The
   large LLM-hypothesis `raw` pool (818) is deliberately **not** used in the
   prompt. Value/identifier need more real-incident exemplars.
2. **Style-leak guard.** The injector must use a different model/prompt family
   from the corpus doc author. The demo injector was an LLM
   (`opencode-go/deepseek-v4.1-flash`); the doc author (`repo-docwriter`) model
   is not yet pinned in the run provenance — fix this before the scaled run.
3. **Scope/taxonomy coupling** (§5) — declared and by design, but must be stated.
4. **Archive weight.** The archived Task E claims dumps are large
   (`fastapi` 126 MB, `pandas` 199 MB); they are renames (no new git objects),
   but consider pruning if size matters.
