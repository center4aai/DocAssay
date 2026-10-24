# Stage B — post-evaluation engine follow-ups

**Date:** 2026-10-20
**Status:** proposal for a **separate development cycle after Stage B**.
**Scope:** the engine (`src/docassay/`), not the corpus, prompts, or injector.
**Policy constraint:** the bare-name policy stays as it is. A bare (unqualified)
symbol is **never** `REFUTED`; an unresolved bare name is `NEI`
(`SCOPE.md` §3.3.1). Nothing below changes that rule.

---

## 1. Why this document exists

Stage B found **35/72 refuted, 7/72 NEI, 30/72 none** on the four active
classes. The low overall number is not uniform:

| group | refuted | rate |
|---|---:|---:|
| path + external dependency | 32/36 | 0.889 |
| identifier + removed-referent | 3/36 | 0.083 |

The symbol classes are weak for several reasons: two real **refutation** bugs
(E1, E2), one real **false-support** bug (E3), and two extraction/attribution
gaps (E4, E5). This document separates:

1. **real engine limitations** that can be fixed without changing the
   bare-name policy;
2. **deliberate policy / non-goals** that must not be "fixed";
3. **analysis/harness limitations** that are not engine work.

The expected gain from fixing the real refutation bugs is **+4 refutations**
(35 → 39/72, 0.486 → 0.542). That is the honest ceiling under the current
bare-name policy. The rest of the gap is policy (bare names deliberately
abstain) and extraction (which moves `none` → `NEI`/`SUPPORTED`, not
`REFUTED`). If a higher symbol-class refutation rate is the goal, the only
routes are a policy change (bare names refutable) or a corpus change (qualified
names); both are outside this scope.

---

## 2. Evidence from Stage B

The exact cases that motivate each item:

| case | class | observed | why it matters |
|---|---|---|---|
| `gaugekit` `numpy>=1.24` × 3 seeds | external | doc says `numpy>=1.24`; manifest `>=999`; tool `SUPPORTED` | version claim is never attached (`context.version = null`) |
| `sheetmusic` `click>=8.1` (seed 3) | external | doc says `click>=8.1`; manifest `<8.1`; tool `SUPPORTED` | disjoint intervals not detected |
| `plotline` `Canvas` × 2 | identifier / removed | class renamed to `CanvasInjected`; module `plotline.canvas` remains; tool `SUPPORTED` | bare name resolves to a module, not the class |
| `gaugekit` `### \`Reading\``, `### \`monthly_means() -> dict[str, float]\`` | identifier / removed | no claim on the line (`no_claim`) | plain bare names in API headings are not anchored |
| `sheetmusic` `parse_chord`, `palette` `generate_palette` | identifier | engine claims `SYMBOL_EXISTS sheetmusic.parser` / `PATH_EXISTS palette/harmony.py`, not the target | module/path claims shadow the bare symbol |

The baseline is clean (0 `REFUTED` in 260 claims), so these are injected-defect
reactions, not pre-existing findings.

---

## 3. Triage

### 3.1 Real engine limitations (fix)

| id | limitation | Stage B cases | expected effect | policy impact |
|---|---|---|---:|---|
| **E1** | A duplicate dependency mention on one line loses the versioned occurrence: the first, versionless anchor wins dedupe, so `context.version` is null. | 3 (`gaugekit` `numpy`) | +3 refuted | none |
| **E2** | `constraint_satisfied` does not detect disjoint intervals when one side is lower-bound-only and the other upper-bound-only (`>=8.1` vs `<8.1`). | 1 (`sheetmusic` `click`) | +1 refuted | none |
| **E3** | A bare capitalized symbol resolves to a **module** of the same folded name (`Canvas` → `canvas`), producing a false `SUPPORTED`. | 2 (`plotline` `Canvas`) | 2 `SUPPORTED` → `NEI` (not `REFUTED`) | none: bare names still never refute |
| **E4** | Plain bare names in API-reference headings are not anchored at all (`### \`Reading\``). | 16 `no_claim`, plus 8 `other_referent` | `none` → `NEI`/`SUPPORTED`; **no refutation gain** | none: claim formation only, no bare refutation |
| **E5** | Same-line referent selection prefers a module/path claim over the bare symbol claim. | 8 `other_referent` | mostly resolves after E3/E4 | none |
| **E6** | E1's correct version extraction turns migration/compatibility/historical prose into refutations on real repos. | 5 clear FPs + 1 arguable on the real-repo audit | 0 refuted (precision fix); implemented | none: gate the prose, keep E1 |

**P0:** E1, E2. **P1:** E3. **P2:** E4, E5 (policy-preserving, no refutation
gain).

### 3.2 Deliberate policy / non-goals (do not "fix")

- **Bare names never refute.** A bare name may be a parameter, builtin,
  external symbol, attribute, or ordinary word. Unresolved bare names stay
  `NEI "unresolved bare name"`. This is the main reason identifier/removed
  refutation is low.
- **Undeclared/removed dependency → `NEI`** (`"undeclared (open by
  transitivity)"`). The world closes over declared manifest dependencies;
  a removed dependency could be transitive. Do not turn this into a refutation
  without a separate contract decision.
- **No VERSION, doc drift, value drift, or cross-document drift.** These remain
  removed/out of scope.
- **No new predicates.** The six-predicate contract is unchanged.
- **No prompt/spec/corpus tuning.** Stage B is held out; fixes are developed on
  the dev set and tested against Stage B only as a post-hoc regression.
- **No 0-`REFUTED` acceptance gate.**

### 3.3 Analysis/harness limitations (not engine work)

- Detection is not bound to the recorded line: 6/35 refutations came from
  another mention. This is allowed by the protocol; report attribution rather
  than change the engine.
- 72 entries are not 72 independent claims: distinct targets are 6 (path),
  8 (external), 15 (identifier), 14 (removed-referent). Keep repo-cluster
  bootstrap and add per-target reporting.
- Controls: 18/18 clean but 13 `SUPPORTED`, 1 `NEI`, 4 not extracted. Report
  the subtype split; do not treat 1.0 precision as broad evidence.
- Independent labels are not included; no IAA is claimed.

---

## 4. Detailed work items

### E1 (P0) — preserve the versioned duplicate on the same line

**Status:** implemented 2026-10-20 (`predicates/dependency.py`), with 15 new
tests; see §5.2.

**Symptom.** `gaugekit` line 9:

```
gaugekit depends on NumPy (numpy>=1.24). From a checkout of the repository:
```

The tool emits one `DEPENDENCY numpy` claim at the **first** mention (`NumPy`,
position 20) with `context.version = null`. The version-bearing second mention
(`numpy>=1.24`, position 27) is deduplicated away by
`predicates/dependency.py::scan_document`, whose dedupe key is
`(anchor_line_text, object_name)`. The verdict is then `SUPPORTED` for a
versionless dependency, so the `>=999` mutation is invisible.

**Root cause.** The dedupe key ignores the version/context. The first mention
wins regardless of which occurrence carries the version.

**Proposed change.** Deduplicate by `(line, object, context.version)` or merge
the contexts of same-object anchors on a line, preferring the occurrence that
carries a version. Do not create two claims; one claim with the version.

**Tests.**
- `NumPy (numpy>=1.24)` → one `DEPENDENCY numpy` claim with
  `context.version == ">=1.24"`.
- `requests (requests>=2.0)` and `Django (django>=4.2)` → same.
- Baseline `numpy>=1.24` vs manifest `>=1.24` → `SUPPORTED`.
- Injected `numpy>=1.24` vs manifest `>=999` → `REFUTED`.
- A versionless repeated mention (`numpy is used; numpy is fast`) stays
  versionless and does not invent a version.
- No change to a single-mention requirement (`numpy>=1.24` on its own).

**Acceptance.** The 3 Stage B `gaugekit` cases become `REFUTED`; the gaugekit
baseline remains 0 `REFUTED`; no new false positives on the dev set.

---

### E2 (P0) — detect disjoint intervals in `constraint_satisfied`

**Status:** implemented 2026-10-20 (`markers/version.py`); see §5.2.

**Symptom.** `sheetmusic` seed 3: doc `click>=8.1`, manifest `click<8.1`.
The intervals are disjoint, but `constraint_satisfied(">=8.1", "<8.1")`
returns `True`, so the verdict is `SUPPORTED`.

**Root cause.** `markers/version.py::constraint_satisfied` compares
lower-bound-to-lower-bound and upper-bound-to-upper-bound only. A
lower-bound-only claim against an upper-bound-only manifest falls through to
`True` (line ~261-312).

**Proposed change.** Compute the claim and manifest intervals
(`_version_interval` already exists) and check intersection first:

- empty intersection → `False` (`REFUTED`);
- non-empty, claim stricter than manifest → `None` (`NEI`, existing
  "understatement" semantics);
- non-empty, manifest stricter / equal → `True`;
- include `!=` exclusions in the interval: an excluded value that is the only
  manifest point makes the intersection empty;
- keep the existing pin/list and bare-major rules.

**Tests.**
- `>=8.1` vs `<8.1` → `False`.
- `>8.1` vs `<=8.1` → `False`.
- `>=8.1` vs `<9` → `True` (intersection non-empty).
- `>=8.1` vs `>=999` → `False`.
- `==8.1` vs `<8.1` → `False`.
- `~=8.1` (expands to `>=8.1,<9.0`) vs `<8.1` → `False`.
- `!=8.1` vs `==8.1` → `False`.
- Existing baseline `click>=8.1` vs `>=8.1` → `SUPPORTED`.
- Do not turn an upper-bound-only doc claim (`<4`) into a refutation; keep the
  existing `NEI`.

**Acceptance.** The `sheetmusic` `click` case becomes `REFUTED`; no new
`REFUTED` on the six Stage B baselines; all existing version tests pass.

---

### E3 (P1) — kind-aware bare candidate resolution

**Symptom.** `plotline` class `Canvas` renamed to `CanvasInjected`; the module
`plotline.canvas` remains. The doc line `### \`class Canvas\`` / `- a
\`Canvas\` ...` produces `SYMBOL_EXISTS canvas SUPPORTED`. The bare name
case-folds to the module and is treated as resolved.

**Root cause.** `vocabularies/structure.py::last_segment_candidates` indexes
**all** evidence kinds, including `KIND_MODULE` (`evidence/symbols.py`). A
capitalized bare class name can therefore resolve to a lowercase module.

**Proposed change.** Make bare candidate resolution kind-aware:

- a capitalized bare name prefers `class`/`function` candidates; a
  module-only candidate is not a valid resolution for a class-shaped name;
- a lowercase bare name may resolve to module/function;
- if no kind-compatible candidate exists, return `NEI "unresolved bare name"`;
- **never** return `REFUTED` for a bare name.

This is policy-preserving: it changes `SUPPORTED` → `NEI`, not `REFUTED`.

**Tests.**
- class `Canvas` + module `canvas`, bare `Canvas` → `NEI`, not `SUPPORTED`;
  bare `canvas` → `SUPPORTED`.
- class `Foo` + function `foo`: bare `Foo` → class candidate; bare `foo` →
  function candidate.
- qualified `plotline.Canvas` after rename → `REFUTED` (unchanged).
- bare `Canvas` after rename → `NEI`, never `REFUTED`.
- Existing bare-name tests in `test_structure.py` / `test_abstention_rules.py`
  stay green.

**Acceptance.** The 2 Stage B `Canvas` cases become `NEI`; overall refutation
does not change; no new `REFUTED`.

---

### E4 (P2) — anchor bare names in API-reference headings (optional, policy-preserving)

**Symptom.** 16 Stage B entries have `none/no_claim`. Typical lines:

```
### `Reading`
### `monthly_means() -> dict[str, float]`
```

No call, no dot, no noun-gated mention, so `symbol_exists_scan` forms no claim.
The tool silently says nothing rather than abstaining.

**Root cause.** `predicates/structure.py::symbol_exists_scan` anchors
`_CALL_RE`, `_DOTTED_RE`, `_NOUN_AFTER_RE`, `_NOUN_BEFORE_RE` only. A plain
backticked bare name in a heading is not an anchor.

**Proposed change.** Add an API-reference heading anchor for a code-shaped
backticked token on a heading line (`#`..`######`), plus the existing call form.
Form a claim; the verdict remains the current bare-name policy: `SUPPORTED` if
a kind-compatible candidate exists, otherwise `NEI "unresolved bare name"`.
**No bare refutation.**

**Tests.**
- `### \`Reading\`` → a `SYMBOL_EXISTS Reading` claim; `NEI` or `SUPPORTED`,
  never `REFUTED`.
- `### \`monthly_means() -> dict[str, float]\`` → claim on `monthly_means`.
- `#### \`Class.method()\`` → claim; qualified behavior unchanged.
- Non-code headings (`## Installation`, `## Notes`) → no claim.
- Fenced code blocks and paths → no new symbol claim.
- No new `REFUTED` on the six baselines.

**Acceptance.** The 16 `no_claim` cases become `NEI`/`SUPPORTED`; refutation
is unchanged; no new false positives. This is a transparency fix, not a
refutation fix. If the team wants "bare names completely untouched", defer
E4; the cost is that these misses stay invisible as `none`.

---

### E5 (P2) — same-line referent preference (mostly resolved by E3/E4)

**Symptom.** 8 entries are `other_referent`: the line produces a module/path
claim (`SYMBOL_EXISTS sheetmusic.parser`, `PATH_EXISTS palette/harmony.py`) but
not the target bare symbol. The target is not adjudicated.

**Root cause.** The scanner anchors the dotted module and the path; the bare
function name in the same line is not an anchor (E4). After E4, both claims
exist. If both cover the line, the report can attribute the target to the
symbol claim.

**Proposed change.** Prefer a symbol claim over a module/path claim for the
target when both cover the same line and the target is a symbol. Do not
suppress the module/path claim from the output; only the target attribution
changes. This is primarily a reporting/selection rule; implement only after
E4.

**Tests.**
- `sheetmusic` `parse_chord` line: claims for both `sheetmusic.parser` and
  `parse_chord`; target attribution selects `parse_chord`.
- `palette` `generate_palette` line: claims for the path and the symbol; the
  target selects the symbol.
- No change to path/dependency targets.

**Acceptance.** The 8 `other_referent` cases become `NEI`/`SUPPORTED` for the
target; refutation unchanged; no new false positives.

---

## 5. Expected impact (honest ceiling)

Starting from Stage B (`35 refuted / 7 NEI / 30 none`). Rows through E3 are
the **bug-fix path**; the last row is the **post-hoc trial variant**
(module-context qualification), which supersedes E3 for the `Canvas` cases and
is an alternative path, not a cumulative row.

| change | refuted | NEI | none | note |
|---|---:|---:|---:|---|
| Stage B | 35 | 7 | 30 | — |
| + E1 | 38 | 7 | 27 | 3 `gaugekit` `numpy` cases |
| + E2 | **39** | 7 | 26 | 1 `sheetmusic` `click` case |
| + E3 | 39 | **9** | 24 | 2 `Canvas` `SUPPORTED`→`NEI` |
| + E4/E5 bare anchoring only | 39 | up to 33 | 0 | `none`→`NEI`/`SUPPORTED`; no refutation gain |
| + E4/E5 with **module-context qualification** (trial) | **68** | 0 | 4 | post-hoc trial; 4 external E1/E2 remain; 9/68 off-line |

**Bare anchoring only** tops out at **39/72 (0.542)** plus E1/E2. That is not
the whole story: a stronger variant — **qualify the anchored bare name with the
document's own module context** — was trialed and reached **68/72 (0.944)**.
It is a claim-scope extension, not a pure bug fix; see §5.1 and
`regression-context-qualification/README.md`.

If the goal is a higher symbol-class refutation rate, the options are:

- **policy change:** make bare names refutable (rejected: bare names stay as
  is);
- **section-qualified names:** qualify a bare name with a project module from
  the document's heading/table/prose context (trialed: 68/72; requires a
  `SCOPE.md` decision);
- **corpus change:** inject qualified names (rejected for Stage B: that is
  benchmark tuning; a future corpus could pre-register it, but it would measure
  a different claim scope).

### 5.1 Trial result (2026-10-20)

A post-hoc trial implemented **module-context qualification + trigger-word
anchoring** in `SYMBOL_EXISTS` and re-ran the frozen Stage B snapshots:

| outcome | Stage B | trial |
|---|---:|---:|
| refuted | 35/72 = 0.486 | **68/72 = 0.944** |
| NEI | 7/72 | 0 |
| none | 30/72 | 4 (external E1/E2) |

Per class: path 18/18; external 14/18; identifier **18/18**; removed-referent
**18/18**. Controls: 18/18 clean, 16 `SUPPORTED`, 1 `NEI`, 1 other referent.
Baseline: 0 `REFUTED` (claims rose, e.g. gaugekit 34→58, but no baseline
finding). Full suite: 611 passed, 11 xfailed; ruff clean; catalog/scope/coverage/
oracle/bank/freeze pass.

**Caveats.** 59/68 refutations match the recorded target line; **9/68** come
from another qualified mention (e.g. `gaugekit monthly_means` at
`docs/guide.md:45` via `docs/api.md:44`). So 18/18 symbol refutation does **not**
mean every target line was refuted. The rule is a **section-qualified name**
extension: it must be written into `SCOPE.md` if adopted, and "bare names as
is" must then mean "bare **without** module context". The four remaining
external cases are E1/E2, not addressed by this rule.

### 5.2 E1/E2 implemented, and the real-repo precision audit

E1 and E2 were implemented on 2026-10-20 (`predicates/dependency.py`,
`markers/version.py`, 15 new tests). A full post-hoc regression of the trial +
E1/E2 gives:

| outcome | Stage B | trial | trial + E1/E2 |
|---|---:|---:|---:|
| refuted (credited) | 35/72 | 68/72 | **72/72** |
| target-line refuted | 29/72 | 59/72 | **63/72** |
| NEI | 7 | 0 | 0 |
| none | 30 | 4 | 0 |

Controls 18/18 clean; baseline 0 `REFUTED`. The 9 remaining cross-mention
refutations are the same symbol at another doc line. Details:
`regression-trial-plus-e1e2/README.md`.

**Precision audit on real repos** (fastapi, pydantic, celery, prefect,
scikit-learn; 22,527 claims, 179 `REFUTED`):

- **Symbol rule:** 10 module-qualified claims emitted; **0** were `REFUTED`.
  The rule is nearly dormant on these repos. One mis-attribution
  (`prefect.cli.prefect`, the console command) abstained via the
  dynamic-surface guard; without that guard it would be a false `REFUTED`.
  Low-power evidence: no visible trial-specific FP, but not a clean bill of
  health.
- **E1:** +6 refuted claims on the sample, of which **5 are clear false
  positives** (fastapi migration-guide Pydantic v1/v2 prose, prefect `whenever`
  compatibility ranges, sklearn historical `scipy 0.16`); 1 is arguable
  stale-advice drift. E1 also removes 2 pre-existing FPs (duplicate Mermaid
  graph lines). E1 amplifies a **pre-existing** migration/compatibility FP
  family; it does not create a new claim form.
- **E2:** 0 verdict changes on the sample; no real-repo disjoint-interval case
  surfaced.

**E6 (implemented 2026-10-20):** a precision gate for migration/compatibility/
historical version prose. Migration/upgrade guide paths are excluded; the
phrases `migrate from`, `compatibility`, `compatible with`, `API differences
between`, `starting from` + version + change cue, `prior to version`, `before
version`, and historical release constructions return `NEI "compatibility
mention"` / `NEI "historical version mention"` instead of `REFUTED`. Keep E1;
gate the prose.

Targeted real-repo re-runs after E6: **fastapi 75 → 55** (migration guide
excluded + stale `deployment/versions.md`), **prefect 7 → 6** (`whenever`
ranges), **scikit-learn 30 → 26** (`joblib`/`scipy`/historical Python notes).
No `SUPPORTED`→`NEI` changes; Stage B remains **72/72 credited, 63/72
target-line**, controls 18/18, baseline 0. The remaining real-repo `REFUTED`
claims are pre-existing FP families (path examples, prose "CI",
`pydantic.json_schema` split, migration-guide mentions outside the excluded
paths), not the symbol trial.

---

## 6. Test and regression plan

1. **Unit tests** for E1/E2 in `markers/version.py` / `test_dependency.py`:
   duplicate mention ownership, disjoint intervals, `~=`, `!=`, open bounds,
   pre-releases, multiple specifiers, environment markers.
2. **Unit tests** for E3 in `test_structure.py` / `test_abstention_rules.py`:
   class-vs-module, function-vs-module, qualified unchanged, bare never
   `REFUTED`.
3. **Unit tests** for E4/E5 in `test_structure.py`: heading anchors, code
   fences, non-code headings, same-line symbol preference.
4. **Full suite:** `uv run pytest -q` (currently 589 passed, 11 xfailed).
5. **Lint:** `uv run ruff check src/`.
6. **Research checks:** catalog, scope, coverage, oracle selftest, exemplar
   bank.
7. **Stage B regression:** re-run the Stage B scoring on the frozen manifest /
   snapshots **without editing the corpus**. Report the delta. This is a
   post-hoc regression, not a new headline; a new held-out corpus is required
   for a new headline.
8. **Baseline guard:** the six Stage B baselines must stay 0 `REFUTED`. Any new
   baseline refutation blocks the change.

---

## 7. Sequencing and guardrails

1. E1 + E2 (P0) in one change; small, testable, +4 refutations.
2. E3 (P1) separately; policy-preserving `SUPPORTED`→`NEI`.
3. Decide on E4/E5 (P2) explicitly. Bare anchoring alone improves transparency
   but **does not** increase refutation; if "bare names untouched" is strict,
   skip it. The **module-context qualification** variant (trialed: 68/72) is a
   claim-scope extension and needs an explicit `SCOPE.md` decision before
   adoption.
4. Do not change prompts, specs, or the Stage B corpus.
5. Do not use the Stage B result to select fixes; use the dev corpus and unit
   tests. Stage B is a post-hoc regression.
6. Do not reintroduce VERSION/doc drift/value/cross-doc.
7. Do not add a 0-`REFUTED` gate.

---

## 8. Bottom line

- The real fixable refutation bugs are **E1** (duplicate dependency mention
  loses the version) and **E2** (disjoint constraint intervals). They are
  implemented and account for **4/72** false `SUPPORTED` cases.
- **E3** removes 2 false `SUPPORTED` by a same-name module; it converts them to
  `NEI`, not `REFUTED` (the trial supersedes it by qualifying `Canvas` and
  refuting it).
- **E4/E5 bare anchoring** makes 24 silent `none` cases visible as
  `NEI`/`SUPPORTED`; alone it does not raise refutation.
- **E4/E5 with module-context qualification** (the trial) reaches **68/72
  (0.944)** on the frozen Stage B snapshots, with 0 baseline/control false
  positives, but 9/68 refutations come from another mention. This is a
  claim-scope extension (`section-qualified name`), not a pure bug fix.
- **Trial + E1/E2** reaches **72/72 credited**, **63/72 target-line**, controls
  18/18, baseline 0. This is post-hoc, not a new held-out result.
- **E6** is implemented: E1's correct version extraction amplified migration/
  compatibility prose false positives on real repos (5 clear FPs in the audit);
  the gate removes the targeted FPs (fastapi 75→55, prefect 7→6, sklearn 30→26)
  without changing Stage B (72/72, 63/72 target-line).
- Without the section-qualified extension, the realistic post-fix refutation is
  **39/72 (0.542)**. With it, the post-hoc result is **72/72**; Stage C is
  needed for a new held-out headline.
