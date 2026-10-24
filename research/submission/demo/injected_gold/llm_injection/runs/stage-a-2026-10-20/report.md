# Stage A — natural corpus / decontaminated injector

**Date:** 2026-10-20  
**Status:** completed (3 seeds)  
**Transient workspace (not committed):** `/tmp/docassay-stage-a`  
**Committed report artifacts:** this directory (`report.md`, `removal-report.md`,
`baseline_evidence.md`, `entries.json`, `corpus_freeze.json`, `prompts_natural/`)
**No branch was created; the repository was not modified.**

## 1. Question

The current headline number is **0.925** (49/53) on the checker-shaped synthetic
corpus. How much of it survives when:

- the documents are written **without knowledge of the extractor**;
- the injector is **not given extractor preconditions** (no “unique basename”,
  “dotted form”, “word version”, “declared manifest dependency” rules);
- the corpus is **frozen before the tool runs** and baseline findings are not
  used to edit documents?

Stage A is a controlled ablation: same 4 specs, same deterministic code, same
exemplar bank; only the docwriter contract, the injector contract, and the
baseline-gate/freeze procedure change.

## 2. Design

| Layer | Current pipeline | Stage A |
|---|---|---|
| specs | 4 synthetic projects | same 4 specs, unchanged |
| code | deterministic materialization | same code, unchanged |
| docs | `repo-docwriter` with checker-aware rules | natural docwriter, no checker/scanner/anchor/claim rules |
| baseline gate | `generate_synthetic.py check` requires 0 REFUTED | no engine gate; freeze first, record baseline findings |
| injector | class prompts with extractor preconditions and `kind`/`artifact_class` | natural class prompts; harness infers kind |
| exemplar bank | triaged README/CASCADE bank | same bank (control variable) |
| freeze | after verification | before any injector/engine run |
| run size | 4 repos × 5 classes × 3 seeds | 4 repos × 5 classes × 3 seeds = 60 bundles |

## 3. Corpus

- 4 repos: `quillpad`, `tidecast`, `ledgerly`, `parcelroute`.
- Same `spec.json` and same materialized Python tree as the current corpus.
- Documentation regenerated from scratch by `claude-haiku-5-5` using a natural
  writer prompt: README + configuration guide + API reference, ordinary
  Markdown, omissions allowed, no prescribed phrasing.
- No `check` gate was used. The corpus was hashed into
  `corpus_freeze.json` (copied here) **before** any injector or engine run.
- Baseline `REFUTED` on all four repos: **0**. Findings were recorded, not used
  to edit the documents.
- An LLM audit found behavior-level mismatches (the code is a placeholder, while
  the docs describe intended behavior). These are outside the five injected
  artifact classes and were **not** edited. In-scope claims (path, symbol,
  version, dependency) are consistent.

Natural-document properties relevant to the experiment:

- version statements are embedded in prose: `This is version 0.1.0. …`,
  `The current release is version 0.4.1.`, `Version: 0.3.1`;
- symbols are often bare names (`load_settings()`, `open_store`, `serve()`), not
  package-qualified dotted names;
- paths appear as Markdown links and inline code;
- dependencies appear in prose (`uvicorn (0.29 or newer)`).

## 4. Injector and verification

- 60/60 bundles produced valid JSON proposals.
- **44/60 verified** by the engine-free oracle (73.3%).
- **16/60 generator failures** (26.7%):
  - 10 `unresolved` — the proposed symbol could not be resolved to a definition
    in the repository;
  - 3 `verify_failed` — the mutation applied but the on-disk check failed
    (mostly malformed dependency constraints);
  - 3 `conflict` — the same file/line was already used by another injection in
    the same snapshot.
- No external claim annotation in Stage A. “Verified” means the mutation exists on
  disk and the target token is still on the document line; it does not
  independently prove that the line is a current-state claim.

Generator failures by class:

| class | verified | generator failures |
|---|---:|---:|
| path-location | 10 | 2 |
| external-dependency | 9 | 3 |
| identifier | 8 | 4 |
| removed-referent | 5 | 7 |
| value | 12 | 0 |
| **total** | **44** | **16** |

## 5. Results

Stage A was run before `VERSION`/`doc_drift` removal. The active four-class
numbers below exclude the historical `value-drift` entries; value is reported
separately as historical.

### Overall (active four classes)

Every verified injection has exactly one outcome. `NEI` is a claim that was
formed and deliberately abstained; `none` is no claim formed at all. The old
“detected / verified” metric counted both `NEI` and `none` as misses, which is
why it reported 0/5 for removed-referent.

| outcome | count | rate | 95% CI |
|---|---:|---:|---|
| refuted | 18/32 | **0.5625** | [0.393, 0.718] |
| NEI (claim formed, abstained) | 10/32 | **0.3125** | [0.180, 0.486] |
| none (no claim formed) | 4/32 | **0.125** | [0.050, 0.281] |
| all attempts (end-to-end refutation) | 18/48 | 0.375 | [0.252, 0.516] |

Per seed (active four classes):

| seed | verified | refuted | NEI | none |
|---|---:|---:|---:|---:|
| 1 | 11 | 6 | 3 | 2 |
| 2–3 | 21 | 12 | 7 | 2 |

### Per class (active four classes)

| class | verified | refuted | NEI | none | refutation | abstention | extraction miss |
|---|---:|---:|---:|---:|---:|---:|---:|
| path-location-drift | 10 | 10 | 0 | 0 | **1.000** | 0.000 | 0.000 |
| external-dependency-drift | 9 | 7 | 0 | 2 | **0.778** | 0.000 | 0.222 |
| identifier-drift | 8 | 1 | 6 | 1 | **0.125** | 0.750 | 0.125 |
| removed-referent-drift | 5 | 0 | 4 | 1 | **0.000** | 0.800 | 0.200 |
| **total** | **32** | **18** | **10** | **4** | **0.5625** | **0.3125** | **0.125** |

### Outcome by claim form

| claim form | verified | refuted | NEI | none |
|---|---:|---:|---:|---:|
| path | 10 | 10 | 0 | 0 |
| dependency | 9 | 7 | 0 | 2 |
| qualified symbol | 1 | 1 | 0 | 0 |
| bare call (`name()`) | 9 | 0 | 9 | 0 |
| bare symbol | 3 | 0 | 1 | 2 |
| **total** | **32** | **18** | **10** | **4** |

The table is the point: **qualified symbol references refute; bare symbol
references abstain.** The old 0/5 for removed-referent was not five failed
refutations — it was 4 deliberate NEI abstentions and 1 no-claim extraction.

Historical value-drift (removed from active scope): 12 verified, 3 refuted,
9 none under the old VERSION predicate. It is excluded from the active totals.

There are 44 historical verified entries but only 28 distinct
`(repo, class, target)` combinations; the three seeds often select the same
natural target. The active four-class subset has 32 entries.

## 6. What drives the drop

### 6.1 Historical: value drift (class removed) — natural phrasing was not extracted

This class was removed from the active scope after Stage A; it is kept here as
history. Of 12 verified value injections, 3 were refuted and 9 produced no claim.
The only detected value injections are the parcelroute cases, and even there the
refutation comes from `docs/api.md`, not from the README line the injector
selected. The other three repositories produced **no version claim** on any
version line:

- quillpad: `The current project version is 0.1.0. The package layout …`
- tidecast: `The current release is version 0.4.1.`
- ledgerly: `This is version 0.4.2. The package is early …`

The old corpus used a standalone line `The current project version is X.` and
scored 12/12. The natural version statement is either embedded in a longer
sentence or phrased differently, and the VERSION gate forms no claim. This is a
direct replication of the old failure mode: the previous fix changed the corpus
to the phrasing the scanner accepts, rather than recording the scanner's
limitation.

### 6.2 Identifier drift: 1 refuted, 6 NEI, 1 none — bare names abstain

The dominant outcome is `NEI` with reason `unresolved bare name`:

- `load_settings()` (quillpad) → `SYMBOL_EXISTS load_settings` NEI
- `open_store` (quillpad) → NEI
- `parse_forecast()` (tidecast) → NEI
- `serve()` (tidecast) → NEI
- `build_router()` (parcelroute) → NEI

Natural documentation uses bare names. The tool forms a `SYMBOL_EXISTS` claim
but cannot resolve the bare name to a qualified symbol after the rename, so it
**deliberately abstains**. It does not claim that the symbol is absent: a bare
name may be a parameter, builtin, external symbol, attribute, or an ordinary
word. The old prompt explicitly required a **dotted or call form**; that rule
was doing the work. The one refuted case used a qualified name
(`ledgerly.cli.main`). The one `none` is a separate extraction issue, not an
abstention.

This is not “1/8 detection”. It is: **1 closed-world refutation, 6 correct
abstentions under the bare-name policy, 1 extraction miss.**

### 6.3 Removed-referent drift: 0 refuted, 4 NEI, 1 none — same bare-name policy

Four of five verified injections produce `NEI` (`unresolved bare name`); one
produces no claim on the line. The old prompt required a **qualified (dotted)**
name, which again was the extractor precondition. Natural bare names do not
reach a refutable claim. The correct report is **0 refuted, 4 abstained, 1
extraction miss** — not “0/5”.

`NEI` is a first-class outcome here, not a dump for unsupported classes. The
claim was formed and the tool said: under the current scope, a bare name does not
prove that the artifact belongs to this project.

### 6.4 Path-location drift: 10/10 — survives decontamination

Natural Markdown links and inline-code paths are still anchored, and the injected
path is usually mentioned in more than one document, so a refutation can come
from a different mention. This is the one class whose recall survives the
decontamination. It is also the class where the extractor was extended to
Markdown links (`listing.py`, commit `d0497f1`) and where the old corpus was
changed to use backticks. The 10/10 is therefore credible for the current
extractor, but it is not evidence that the old checker-shaped corpus was
uncontaminated.

### 6.5 External dependency: 7/9 — two genuine constraint misses

Two verified injections remain `SUPPORTED` after the manifest constraint is set
to `>=999`:

- `uvicorn` (parcelroute, seed 1): manifest `uvicorn>=999`, doc says
  `uvicorn (0.29 or newer)`; the claim stays SUPPORTED.
- `pydantic` (parcelroute, seed 2): manifest `pydantic>=999`; the claim stays
  SUPPORTED.

These look like genuine tool limitations in constraint comparison, not
doc-phrasing artifacts.

### 6.6 Generator failures matter

16/60 natural proposals could not be turned into verified injections. Most are
unresolved symbols (the model chooses a bare name that does not resolve to a
unique definition) and malformed constraint values. Under the protocol these
are generator defects and are dropped from the denominator. The active
four-class end-to-end rate is **18/48 = 0.375**; the historical five-class
end-to-end rate was 21/60 = 0.350. The harness/applier is tuned to the
checker-shaped corpus more than the injector prompts were.

### 6.7 Baseline before injection: 0 REFUTED is not evidence of precision

Stage A’s baseline had **0 REFUTED** on all four synthetic repos. That is not a
precision result: the docs are simple and derived from the spec, and the
behavior-level mismatches found by the independent audit are outside the
predicate vocabulary. On real held-out repos, archived baseline dumps show tens
of REFUTED claims:

| repo | claims | REFUTED baseline | share |
|---|---:|---:|---:|
| bitsandbytes | 2821 | 34 | 1.2% |
| fastapi | 4265 | 62 | 1.5% |
| pydantic | 3294 | 29 | 0.9% |

Several look like false positives: `Python >= 3.9` as a project dependency,
migration-guide mentions of Pydantic v1/v2, an external `llms.txt` badge, and
`flamegraph.svg` as a command output. These are recorded in
`baseline_evidence.md` in this directory.

**This is the second circularity loop.** A workflow that requires `0 REFUTED`
before accepting a repository (`generate_synthetic.py check`) uses the tool
under test as the judge of its own corpus. It can pass either by selecting repos
the engine already agrees with, or by editing docs until the findings disappear.
Both hide baseline false positives and make precision look perfect by
construction. Stage A did not use the gate, but the active pipeline still had it.

The non-circular procedure is: independent audit → freeze → run the engine once
on the baseline → record findings → adjudicate each as a true doc bug or a tool
false positive → never edit the corpus to erase a finding. `check` is now a
diagnostic (`baseline-report`), not an acceptance gate.

## 7. Comparison with the current headline

| run | refuted / verified | refutation rate |
|---|---:|---:|
| current, pre-fix value | 32/53 | 0.604 |
| current, after value fix | 44/53 | 0.830 |
| current, after path fix (headline) | 49/53 | **0.925** |
| **Stage A, active four classes** | **18/32** | **0.5625** |
| Stage A, historical five classes | 21/44 | 0.477 |
| Stage A, active four classes, all attempts | 18/48 | 0.375 |

The Stage A denominator is different (32 active verified entries, 4 repos,
3 seeds), so the difference is not a paired comparison. But the direction is unambiguous:
after removing the checker-aware docwriter rules and the extractor-derived target
rules, recall falls by roughly half. The old 0.925 was substantially a property
of the benchmark construction, not a general capability estimate.

## 8. Validity caveats

1. **Same tool-shaped specs.** The specs still enumerate surfaces the old
   pipeline needed; only the docs and injector rules were decontaminated.
2. **Same noisy exemplar bank.** The bank was rebuilt to four classes
   (`path 12`, `external 11`, `removed 9`, `identifier 8` triaged), but it is
   still thin and noisy. The prompt rules, not the exemplars, still drive much
   of the target choice.
3. **No external claim annotation.** “Verified” is on-disk mutation validity, not
   claim validity. An independent stream is still needed.
4. **Audit is LLM-based.** The docwriter and the first auditor used the same
   model family; a second audit with a different family returned `CONSISTENT`
   on two repos and timed out on two. This is model-based audit.
5. **Generator failures excluded from the headline denominator.** The protocol
   treats them as generator defects; the active end-to-end rate is
   **18/48 = 0.375**, reported alongside.
6. **Detection is not bound to the selected line.** Path and external cases can
   be detected through another document mention. This is allowed by the protocol
   but inflates class refutation relative to “did the tool refute this exact
   line?”
7. **No controls, no precision.** The LLM arm has no consistent-present/absent
   controls; precision is not measured.
8. **Small sample and clustering.** 4 repos, 32 active verified entries;
   the Wilson CIs are optimistic because targets cluster within repos and seeds.

## 9. Interpretation

Stage A says the current 0.925 is **not** a robust estimate of the tool's recall
on natural documentation. The picture that emerges:

- **paths:** strong (10 refuted / 0 NEI / 0 none), including natural Markdown
  links and inline code;
- **declared dependencies:** moderate (7 refuted / 0 NEI / 2 none), with genuine
  constraint-comparison misses;
- **symbol references:** qualified references refute (1/1); bare references
  abstain by policy (9 bare calls → 9 NEI; 3 bare → 1 NEI + 2 none). This is not
  “0/5 detection”; it is a deliberate closed-world boundary;
- **natural version statements:** removed from active scope; historically 3/12
  refuted, 9/12 no claim.

This is exactly the pattern the old target-selection rules were hiding: the old
prompt told the injector to use qualified names, a version-scoped phrase, and a
backticked path, and the old corpus was rewritten to satisfy those same
preconditions.

## 10. What to do next (B)

1. **Independent claim annotation** for every injected line (blind to the tool), with
   IAA on a sample. Without it, “verified” remains a generator claim.
2. **New held-out corpus** with new specs written without tool-shaped surface
   requirements, and docs written by a different model family.
3. **Fix the applier for symbol renames/deletes**: rename/remove references too,
   or reject targets whose old name remains in the tree. Many identifier/removed
   proposals are otherwise clean at the definition but leave references.
4. **Claim-aware verifier and stage attribution**: distinguish `not_a_claim`,
   `claim_gate`, `extraction`, `referent`, and `evidence`; report every miss.
5. **Controls and precision**: consistent-present/absent targets, no
   tool-conditioned baseline edits.
6. **Independent judges**: do not share `obj_match` between scorer and
   deterministic judge; run the LLM judge and independent miss/control stream.
7. **Report both denominators**: verified-only recall and end-to-end rate
   (including generator failures).

## 11. Artifacts

- Report: `report.md` (this file)
- Removal report: `removal-report.md`
- Baseline evidence: `baseline_evidence.md`
- Entry-level table: `entries.json`
- Corpus freeze: `corpus_freeze.json`
- Clean prompts: `prompts_natural/`
- Transient run workspace (not committed): `/tmp/docassay-stage-a/corpus/`,
  `/tmp/docassay-stage-a/runs/stage-a-s1/`,
  `/tmp/docassay-stage-a/runs/stage-a-s23/`
- Metrics: `metrics.md` / `metrics.json` in each transient run directory.

Reproduction sketch:

```bash
ROOT=.
W=/tmp/docassay-stage-a

# corpus generation (docwriter) and freeze are in the run log;
# injector + verify:
PYTHONPATH=src uv run python "$W/llm_inject_stage_a.py" prepare \
  --repos quillpad,tidecast,ledgerly,parcelroute --seeds 2,3 --out "$W/runs/stage-a-s23"
PYTHONPATH=src uv run python "$W/llm_inject_stage_a.py" run \
  --model opencode-go/deepseek-v4.1-flash --agent repo-injector --out "$W/runs/stage-a-s23"
PYTHONPATH=src uv run python "$W/llm_inject_stage_a.py" finalize --out "$W/runs/stage-a-s23"

# score:
PYTHONPATH=src uv run python \
  research/submission/demo/injected_gold/scripts/score_injections.py \
  --manifest "$W/runs/stage-a-s23/manifest.jsonl" \
  --snapshots "$W/runs/stage-a-s23/snapshots" \
  --out "$W/runs/stage-a-s23" --seed 1
```

## 12. Bottom line

On the active four-class scope, Stage A is **18/32 refuted (0.5625), 10/32 NEI
(0.3125), 4/32 none (0.125)**; end-to-end refutation is **18/48 = 0.375**. The
historical five-class figure was 21/44 = 0.477, which counted both NEI and none
as “not detected”.

The drop from 0.925 is not noise: it is concentrated exactly where the old
prompt encoded extractor preconditions — natural version phrasing, bare symbol
names, and qualified referents. Path refutation survives; dependency refutation
is moderate; symbol refutation is limited because bare names deliberately
abstain. The 0-REFUTED baseline gate is a second circularity loop, not evidence
of precision.

This is a strong argument that Stage B is necessary before the 0.925 number can
be used as a headline claim.

## 13. Follow-up (2026-10-20): VERSION and doc_drift removed

After Stage A, the `VERSION` predicate and the referent-level `doc_drift` /
`DOC_DRIFT` feature were removed from the active project:

- registered predicates: **7 → 6**;
- active LLM injection classes: **5 → 4** (no `value-drift`);
- expressible repo-level classes: **8/17 → 7/17**;
- `value-drift` and `cross-document-drift` remain external-catalog gaps, not
  tool capabilities.

Metric impact is a denominator change, not a capability improvement:

| run | before | after |
|---|---:|---:|
| Stage A verified-only | 21/44 = 0.477 | 18/32 = 0.5625 |
| Stage A end-to-end | 21/60 = 0.350 | 18/48 = 0.375 |
| Old checker-shaped corpus | 49/53 = 0.925 | 37/41 = 0.902 |

The aggregate rises because the weakest class is removed. Per-class numbers are
the meaningful comparison: path 10 refuted / 0 NEI / 0 none; external 7/0/2;
identifier 1/6/1; removed-referent 0/4/1. The symbol classes are not “0/5
detection”: most are deliberate NEI abstentions under the bare-name policy.

Verification: `pytest` 589 passed / 11 xfailed; `ruff` clean; catalog, scope,
coverage, oracle selftest, and exemplar-bank check all pass. Full file-level
detail is in `removal-report.md` in this directory.
