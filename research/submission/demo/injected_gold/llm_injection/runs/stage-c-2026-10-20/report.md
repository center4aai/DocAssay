# Stage C — report (provisional, engine-only)

**Date:** 2026-10-21
**Arm:** C-ext (section-qualified name adopted, `SCOPE.md` §3.3.2)
**Corpus:** `synthetic-natural-c/` v2 (6 repos, 3 new domains, 18 documents)
**Engine:** `src/docassay`; scored at tree `21ac874c…` (commit `9a212cf` + the
S0/S5 engine-free fixes recorded in `deviations.md`), final at tree
`bc6af4f…` after the identifier update and the demo-surface re-freeze (`postscore_note`)
**Status:** **provisional**. Labels are engine-only plus a supplementary
three-model LLM annotation arm that labels the blind sheet. The arm is
confirmation only; no IAA is claimed. This report carries engine-only labels
plus the LLM arm.

> **KPI (operator decision, 2026-10-21):** the tool has **caught** a defect if it
> produces a same-artifact `REFUTED` **anywhere** in the baseline→injected diff,
> **or** a same-artifact `NEI`. `NEI` is an explicit abstention with a mention,
> not silence, and counts as caught. `none` (no claim / wrong `SUPPORTED` /
> other referent) is a miss. `R_detect` is the headline; `R_credit` is
> `REFUTED`-only and `R_target` is attribution. This is a disclosed post-score
> change from the plan's co-primary rule; raw counts are unchanged.

> No delta against Stage B is reported. Stage B's `35/72`, the post-hoc
> `68/72`, `72/72`, and `63/72` are properties of a different corpus and engine
> and are not Stage C baselines.

## T1 — freeze and provenance

| item | value |
|---|---|
| scope/engine freeze | `scope_engine_freeze.json`; scored aggregate `043f45af2a8d…`, final `6b124f6a…` (131 files, `postscore_note`) |
| engine tree | scored `21ac874c78f80ccdfa597dea824d4ff37f098f92`; final `bc6af4f78d83440a20f69215767488a3f49f300a` |
| corpus freeze | `corpus_freeze.json`, `synthetic-natural-stage-c-2026-10-20-v2`, aggregate `5cbfa8893d1b…`, 78 files |
| model IDs | architect/docwriter `opencode-go/gpt-6-luna`; auditor `opencode-go/gemini-4-argon-contributor`; injector `opencode-go/deepseek-v4.1-flash`; adjudicator `opencode-go/qwen3.8-flash` |
| verification | scope + corpus `--verify` passed before S1, before injection, before scoring, after scoring, and after the final re-freeze |
| deviations | 16 entries, `deviations.md` (S0 agent-prompt correction, contamination-check correction and shingle removal, corpus-freeze extension, metrics/scorer/judge fixes, corpus link repair → v2, post-score KPI change, identifier update re-freeze, demo-surface re-freeze) |

## T2 — overall

| verified | detected (REFUTED+NEI) | R_detect (KPI) [95% CI] | REFUTED (R_credit) | NEI | none | R_target (attribution) [95% CI] |
|---|---|---|---|---|---|---|
| 69 | **65** | **0.942** [0.873, 0.986] | 50 (0.725) | 15 | 4 | 0.565 [0.476, 0.639] |

Repo-cluster bootstrap, 6 clusters, 10,000 replicates, seed 20261020; no Wilson.

**What the 4 misses are:** all are `path-location-drift` with `no_claim` — the
path token has an extension outside the engine's extension list
(`.asc`, `.geojson`, `.bib`) and is gated before a claim is formed. Nothing else
is `none`.

**Attribution:** of the 50 `REFUTED`, 11 are other-mention-only, 12 both, 27
target-line-only. Under the KPI all 50 are caught; `R_target = 0.565` only says
how often the recorded line carried the refutation.

## T3 — class × outcome

| class | verified | detected | R_detect (KPI) | REFUTED | NEI | none | R_target (attribution) |
|---|---:|---:|---:|---:|---:|---:|---:|
| path-location-drift | 18 | 14 | **0.778** | 14 | 0 | 4 | 0.778 |
| external-dependency-drift | 15 | 15 | **1.000** | 15 | 0 | 0 | 1.000 |
| identifier-drift | 18 | 18 | **1.000** | 9 | 9 | 0 | 0.111 |
| removed-referent-drift | 18 | 18 | **1.000** | 12 | 6 | 0 | 0.444 |

Every class is scored on `R_detect`. `NEI` counts as caught: the tool formed a
claim about the injected artifact and explicitly abstained (`"unresolved bare
name"`); it did not silently support the statement. The identifier and
removed-referent classes therefore reach 1.000 under the KPI, split between
refutation and explicit abstention; their `R_target` values are attribution
notes, not misses.

## T4 — claim form × outcome

| claim_form | n | refuted | NEI | none | R_credit | R_target | other-mention |
|---|---:|---:|---:|---:|---:|---:|---:|
| path | 20 | 15 | 1 | 4 | 0.750 | 0.700 | 1 |
| dependency | 15 | 15 | 0 | 0 | 1.000 | 1.000 | 0 |
| section_qualified | 16 | 11 | 5 | 0 | 0.688 | 0.500 | 3 |
| bare | 14 | 5 | 9 | 0 | 0.357 | 0.143 | 3 |
| bare_call | 4 | 4 | 0 | 0 | 1.000 | **0.000** | 4 |

`bare_call` is caught 4/4 through another mention; `bare` is caught 14/14
(5 `REFUTED` + 9 `NEI`); `section_qualified` is caught 16/16. `R_target` only
records which of those were refuted on the recorded line.

## T5 — context source × outcome

| context_source | n | refuted | NEI | none | R_credit | R_target | other-mention |
|---|---:|---:|---:|---:|---:|---:|---:|
| heading | 10 | 6 | 4 | 0 | 0.600 | 0.500 | 1 |
| list | 4 | 3 | 1 | 0 | 0.750 | 0.500 | 1 |
| prose | 2 | 2 | 0 | 0 | 1.000 | 0.500 | 1 |
| none | 53 | 39 | 10 | 4 | 0.736 | 0.585 | 8 |

## T6 — genre × outcome

| genre | n | refuted | NEI | none | R_credit | R_target |
|---|---:|---:|---:|---:|---:|---:|
| n/a (README) | 41 | 33 | 5 | 3 | 0.805 | 0.683 |
| reference | 16 | 11 | 5 | 0 | 0.688 | 0.562 |
| explanation | 6 | 3 | 3 | 0 | 0.500 | 0.000 |
| module map | 3 | 2 | 1 | 0 | 0.667 | 0.667 |
| tutorial | 1 | 1 | 0 | 0 | 1.000 | 0.000 |
| how-to | 1 | 0 | 1 | 0 | 0.000 | 0.000 |
| cookbook | 1 | 0 | 0 | 1 | 0.000 | 0.000 |

## T7 — target document and repo

| target_document | n | refuted | NEI | none | R_credit | R_target |
|---|---:|---:|---:|---:|---:|---:|
| readme | 41 | 33 | 5 | 3 | 0.805 | 0.683 |
| reference_document | 22 | 13 | 9 | 0 | 0.591 | 0.500 |
| task_document | 6 | 4 | 1 | 1 | 0.667 | 0.000 |

| repo | verified | refuted | NEI | none | R_credit | R_target |
|---|---:|---:|---:|---:|---:|---:|
| bibscan | 12 | 8 | 3 | 1 | 0.667 | 0.667 |
| contourkit | 12 | 6 | 5 | 1 | 0.500 | 0.417 |
| morpheme | 12 | 12 | 0 | 0 | 1.000 | 0.667 |
| sensorbus | 12 | 6 | 6 | 0 | 0.500 | 0.500 |
| serialscope | 12 | 11 | 1 | 0 | 0.917 | 0.667 |
| tileplan | 9 | 7 | 0 | 2 | 0.778 | 0.444 |

## T8 — dependency phrasing and form

| value | n | refuted | NEI | none | R_credit | R_target |
|---|---:|---:|---:|---:|---:|---:|
| inline_backticked / constraint_break | 15 | 15 | 0 | 0 | 1.000 | 1.000 |
| n/a (other classes) | 54 | 35 | 15 | 4 | 0.648 | 0.444 |

Only the `inline_backticked` phrasing and `constraint_break` form occur in the
verified set; the other pre-registered phrasings have no entries. All three
`verify_failed` bundles are tileplan dependency breaks: tileplan is stdlib-only,
so there is no manifest requirement to break.

## T9 — end-to-end statuses

| planned | verified | declined | invalid | verify_failed | apply_failed | timeout | no_output | unresolved | conflict | refuted |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 72 | 69 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 50 |

`verified/72 = 0.958`. External-dependency is 15/18; the three failures are
counted in the denominator and not replaced.

## T10 — credited detection × target-line attribution

| class | credited refuted (KPI) | target-line refuted (attribution) | other-mention-only | both |
|---|---:|---:|---:|---:|
| path-location-drift | 14 | 14 | 0 | 7 |
| external-dependency-drift | 15 | 15 | 0 | 3 |
| identifier-drift | 9 | 2 | 7 | 1 |
| removed-referent-drift | 12 | 8 | 4 | 1 |

## T11 — controls

| family | required | evaluated | dropped | shortfall | extracted | refuted | specificity | precision (extracted) | extraction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1 path | 6 | 6 | 0 | 0 | 6 | 0 | 1.000 | 1.000 | 1.000 |
| A2 dependency | 6 | 5 | 0 | 1 | 5 | 0 | 1.000 | 1.000 | 1.000 |
| A3 qualified symbol | 6 | 3 | 0 | 3 | 3 | 0 | 1.000 | 1.000 | 1.000 |
| A4 section-qualified symbol | 6 | 5 | 0 | 1 | 5 | 0 | 1.000 | 1.000 | 1.000 |
| B non-module trap | 6 | 5 | 0 | 1 | 1 | 0 | 1.000 | 1.000 | **0.200** |
| C consistent-absent | 0 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

24/24 evaluated controls are clean; 0 control refutations. The shortfalls are
corpus properties: tileplan has no dependency (A2) and no trap (B);
morpheme/sensorbus/serialscope have no document-written dotted symbol (A3);
sensorbus has no section-qualified control (A4). Family B is rarely extracted
(1/5), so its precision is a single-control result, not evidence of broad
precision.

## T12 — baseline findings

**0** `REFUTED` claims on the six clean baselines after the v2 corpus repair.
The one pre-repair baseline finding was a broken relative link in
`contourkit/docs/walkthrough.md:254` (`docs/api.md` from inside `docs/`); it was
repaired and the corpus was re-frozen as v2. No baseline adjudication is
outstanding.

## T13 — effective sample size

| class | entries | distinct (repo, artifact) | collapsed targets | collapsed entries |
|---|---:|---:|---:|---:|
| path-location-drift | 18 | 11 | 6 | 13 |
| external-dependency-drift | 15 | 7 | 5 | 13 |
| identifier-drift | 18 | 13 | 5 | 10 |
| removed-referent-drift | 18 | 15 | 3 | 6 |

The 69 entries are not 69 independent claims; the per-target table is a
sensitivity analysis, not the headline.

## T14 — LLM annotation arm (supplementary)

Three LLM annotators
(`claude-haiku-5-5`, `glm-5.3-flash`, `qwen3.8-flash`) labelled the blind
132-row sheet (69 target + 39 cross-mention + 24 controls). The sheet contains
no tool verdict, layer, reason, or metric. The arm is supplementary confirmation only.

| field | Fleiss κ | % agreement |
|---|---:|---:|
| `claim_type` | 1.000 | 1.000 |
| `claim_form` | 0.987 | 0.985 |
| `context_source` | 0.905 | 0.932 |
| `defect_is_real` | 1.000 | 1.000 |
| `none_claim_not_extracted` | 1.000 | 1.000 |
| `control_false_positive` | 1.000 | 1.000 |
| `nei_reason_applies` | **0.489** | 0.674 |
| `same_artifact` | n/a | n/a (not in this sheet) |

KPI checks (majority label):

| check | count |
|---|---:|
| non-control rows judged a real defect | 105/105 current claims (3 fenced rows `n/a`) |
| controls judged true (so refuting them would be wrong) | 24/24 |
| `none` rows judged "a claim should have been formed" (miss) | 4/4 |
| NEI judged a **legitimate** abstention | **8/15** |
| NEI judged **not** legitimate | **7/15** |

The 7 contested NEI are not a random split: all have a module context the
engine could have used but did not section-qualify —
`bibscan/docs/api.md:19` table row under `bibscan.names`, `bibscan/docs/api.md:117`
heading under `## bibscan.names`, `contourkit/docs/api.md:152` heading under
`## contourkit.geometry`, `sensorbus/docs/concepts.md:74` (`units.py exposes
convert`), `serialscope/docs/structure.md:74` list item under
`serialscope/errors.py`. The remaining 8 NEI are bare names with no project
qualifier, where abstention is legitimate.

**Sensitivity.** Under the operator KPI (REFUTED + every NEI) detection is
**65/69 = 0.942**. Counting only the LLM-validated NEI gives **58/69 = 0.841**
(50 REFUTED + 8 legitimate NEI). The difference is exactly the 7 avoidable
abstentions above. The operator KPI stands; this sensitivity is reported, not
used to change it.

## T15a — judges (supplementary)

| judge | refuted | NEI | none | agreement on refuted/non-refuted |
|---|---:|---:|---:|---:|
| deterministic diff judge | 50 | 15 | 4 | 1.000 (69/69) |
| LLM judge (`qwen3.8-flash`, frozen rubric) | 50 | 11 | 8 | 1.000 (69/69) |

Both judges agree on the refuted/non-refuted decision for all 69 bundles; they
split the non-refuted cases differently (scorer 15 NEI/4 none; LLM 11 NEI/8
none). No manual resolution changed a refuted decision.

## T15 — deviations

See `deviations.md`. The material ones:

- corpus link repair after the S4 freeze → `v2`, fresh snapshots and re-score;
- control evaluation restricted to the control's own line (§6.3);
- analysis-script fixes before the reported result (metrics status, baseline
  filter, dependency artifact in the judge, Stage C control ids);
- **post-score KPI change:** credited detection (`R_credit`) is the headline for
  every class; target-line is attribution. This is a disclosed post-hoc estimand
  change, recorded on 2026-10-21.

## Interpretation (descriptive only)

- Under the KPI the tool catches **65/69 = 0.942** (95% CI 0.873–0.986):
  50 `REFUTED` and 15 explicit `NEI` abstentions.
- Path and dependency detection transfer well to the new domains: dependency
  1.000, path 0.778. The four path misses are a single mechanical gap — the
  extension list does not include `.asc`, `.geojson`, or `.bib`, so the claim is
  gated before adjudication.
- Both symbol classes reach **1.000** under the KPI: identifier 9 `REFUTED` +
  9 `NEI`, removed-referent 12 `REFUTED` + 6 `NEI`. The `NEI` cases are explicit
  `"unresolved bare name"` abstentions on the injected artifact, not silent
  support; they count as caught by operator policy. Off-line refutations also
  count.
- The section-qualified form is measurable in C-ext (16 entries, 16 caught,
  8 refuted on the recorded line). Bare and bare-call mentions are caught
  through another mention or an explicit abstention.
- Controls are clean but thin: 24 evaluated, with shortfalls and a B extraction
  rate of 0.2.
- The corpus is small and the verified set is 69, not 72. No generalisation
  beyond these six repositories is claimed.

## What this does not establish

No external validation, no IAA, no population estimate, no comparison with Stage B,
no claim about classes outside the four active ones, no claim that the recorded
line was the one that caught the defect (`R_target` is attribution), no claim
that an `NEI` is a refutation of the defect (it counts as caught by operator
policy because it explicitly surfaces the artifact), and no claim that the eight
real-repo false `REFUTED` claims found before S0 are fixed (they were accepted
as-is by the operator decision recorded in `README.md`).
