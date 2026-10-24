# Stage C — preregistration: held-out natural corpus after the E1–E6 engine changes

**Date:** 2026-10-20
**Branch:** `demo`
**Status:** plan for sign-off. No Stage C corpus, prompt, injection, engine run,
or score exists at the time of writing. This file is normative once signed; it is
not a report. Every placeholder below is a plan, not a result.
**Run directory:** `research/submission/demo/injected_gold/llm_injection/runs/stage-c-<signoff-date>/`
(the date is fixed at sign-off; the placeholder is not a result).
**Corpus directory:** `research/submission/demo/injected_gold/synthetic-natural-c/`
**Normative parents:** `validation/protocol.md` and `validation/SCOPE.md`, as
amended by **OPEN-C1** and **OPEN-C11** before sign-off. The frozen Stage B
prompts and exemplar bank are *inputs*, not parents.

---

## 0. Prior numbers are not the Stage C baseline

> **Stage B's `35/72` is not the Stage C baseline. The post-hoc `68/72`,
> `72/72` credited, and `63/72` target-line trials are not the Stage C
> expectation, baseline, or headline.**
>
> - `35/72 (0.486)` refuted, `7/72` `NEI`, `30/72` `none` is Stage B's result on
>   the **Stage B corpus** under the **pre-E1/E2** engine
>   (`runs/stage-b-2026-10-20/report.md` §6). Stage C uses a different corpus,
>   different domains, different document genres, and a different engine commit.
> - The post-hoc trial on the frozen Stage B snapshots reached `68/72 (0.944)`;
>   after adding E1/E2 it reached `72/72` credited and `63/72` target-line
>   (`regression-context-qualification/README.md`,
>   `regression-trial-plus-e1e2/README.md`). It was measured on the same corpus
>   that motivated the change. **9/68** (and later **9/72**) refutations were
>   credited through a non-target mention.
> - The trial's per-class `18/18` identifier and `18/18` removed-referent rows,
>   and its claim-form `32/32` bare and `3/3` bare-call rows, are properties of
>   that post-hoc fixture. They are **not** Stage C targets, quotas, or
>   expectations.
> - `39/72 (0.542)` (E1/E2 arithmetic on the Stage B targets) is also not a
>   Stage C baseline; it is a projection on a different corpus.
> - Stage C reports **no delta against any of these numbers**. A Stage C value
>   near `0.944` is not confirmation of the trial. A Stage C value below
>   `0.486` is not a regression, because the corpus and engine differ. No
>   headline table may carry a "vs Stage B" column. Historical context may
>   appear only in a clearly labelled appendix, never in the result.

---

## 1. Question, scope arms, and hypotheses

Stage B measured the pre-fix engine on a natural corpus and located the failure
modes that became E1–E6 and the section-qualification trial. Stage C asks the
**held-out** question that Stage B could not:

> After the engine changes (E1, E2, E3/E4/E5, E6, and the adopted scope decision
> on section-qualified names), on a **new** natural corpus in **new domains**,
> with **new documentation genres**, **new dependency phrasings**, and **new
> module-context patterns**, what does the tool do on the four active classes —
> with the bare-name policy, controls, and credited versus target-line
> detection reported separately?

Stage C is a conformance test, not a benchmark race. It evaluates the tool
**as frozen at sign-off**. It is not used to tune prompts, specs, corpora, or
tool code.

### 1.1 Scope arms (C1 is blocking)

The plan pre-registers **two mutually exclusive arms**. Exactly one is executed.
The arm is fixed at S0, before any spec or document is generated. It is not
chosen after seeing corpus or engine output.

| arm | `SCOPE.md` | engine symbol form | A4/B controls | symbol-class reporting |
|---|---|---|---|---|
| **C-ext** | §3.3.2 *section-qualified name* adopted verbatim from §9.1 | bare member may become `section_qualified` when the document supplies a project-owned module; bare without context stays bare | applicable | `section_qualified` is a reported claim form; target-line and credited rates both reported |
| **C-base** | §3.3.2 **not** adopted; bare-name policy unchanged | only a document-written dotted `qualified` name is refutable; no context inference | **n/a** | symbol classes reported as **policy-limited**; no claim that the tool detects bare symbol drift |

Both arms share the four active classes, the corpus design, the injector
contract, the controls that remain applicable, and the scoring definitions.
`section_qualified` is a valid `claim_form` value only in C-ext; in C-base it may
appear only as `n/a` in a caption, never as a measured cell.

**OPEN-C1 is a hard abort condition.** No Stage C run begins until the arm is
chosen and `SCOPE.md` is amended (C-ext) or explicitly reaffirmed (C-base).

### 1.2 What Stage C adds beyond Stage B

| axis | Stage B | Stage C |
|---|---|---|
| domains | environmental/energy, creative/visual, music/everyday | geospatial, language/text, instrument/hardware |
| document genres | one fixed document set (README + one guide + one API page), not a genre taxonomy | pre-assigned genres from one frozen six-genre taxonomy; README is a document role, not a genre |
| dependency phrasings | whatever occurred, reported only in aggregate | pre-registered phrasing inventory, reported per phrasing (not selected for) |
| module-context patterns | incidental | frozen `context_source` taxonomy (heading / table / prose / list / path prose / none), reported per source |
| engine | pre-E1/E2/E6; bare never refuted | E1+E2+E3+E6 in both arms; C-ext adds E4/E5 and §3.3.2 |
| controls | 18 consistent-present | conditional on C1: C-ext A1–A4 + B + optional C; C-base A1–A3 + optional C |
| attribution | target line vs other mention, post hoc | pre-registered co-primary: credited and target-line, with a crosstab |
| annotation | blocked; no independent labels | at least one non-author annotator required; two for IAA; blind sheet with target-line and cross-mention rows |
| baseline | 0 `REFUTED`; adjudication not exercised | adjudication pre-registered whether or not findings occur |

### 1.3 Hypotheses (directional; fixed before generation; not acceptance criteria)

- **H1 (transfer).** Rates will vary by class, genre, and context source. Stage C
  makes **no prediction about a comparison with Stage B** and no claim that a
  class ordering will reproduce. The result is reported descriptively.
- **H2 (paths).** `path-location-drift` refutation remains high across the
  pre-assigned genres. Prose path mentions without backticks or link syntax
  produce more `NEI`/`none` than backticked paths and Markdown links.
- **H3 (dependency).** Constraint-break injections refute more often than
  dependency-removal injections; removal is expected `NEI`
  (`"undeclared (open by transitivity)"`) by policy. The E1 shape (display name
  and constraint on one line), the E2 shape (disjoint lower/upper bounds), and
  the E6 migration/compatibility gate are reported by shape, not in aggregate.
  Table-row, extras, and environment-marker phrasings produce more
  `NEI`/`none` than the plain name-plus-constraint forms.
- **H4 (symbols).** Uncontextualised bare names are **never** `REFUTED` — this is
  policy compliance, not a prediction. Among symbol claims, the predicted
  refutation order is `qualified` ≳ `section_qualified` > `bare_call` > `bare`,
  with `section_qualified` measured only in C-ext. In C-base, symbol rates are
  expected to be low and are reported as policy-limited, not as engine failure.
- **H5 (attribution).** Credited refutation is greater than or equal to
  target-line refutation by construction. The gap is larger in C-ext than in
  C-base, because qualification creates additional refutable mentions away from
  the target line. A credited-only symbol rate is not evidence that target-line
  claims are detected.
- **H6 (controls).** Specificity on consistent-present controls is high but is
  not assumed to be 1.0. In C-ext the non-module context traps (family B) are the
  most likely source of a new false positive. Any control refutation is listed
  individually.
- **H7 (generator and baseline).** Declines, unresolved proposals, and generator
  failures occur and are counted, never retried for substance. Baseline
  `REFUTED` findings may be nonzero on richer documents; the adjudication
  procedure is pre-registered and no 0-`REFUTED` assumption is made.
- **H8 (E6).** Removing the migration/compatibility/historical version-prose
  false positives does not remove a genuine current-state dependency
  refutation; E1 shapes still refute. This is checked by the frozen unit tests
  and by the Stage C baseline/control counts, not by a new real-repo audit.

---

## 2. Frozen taxonomy and corpus design

### 2.1 One taxonomy file

`injected_gold/llm_injection/runs/stage-c-<date>/taxonomy.json` is the **single**
source of truth for every categorical field. It is hashed in
`scope_engine_freeze.json` (§4.1). No second genre list, claim-form list, or
context list may exist in a prompt, a spec, or a report.

The taxonomy has separate, orthogonal dimensions:

| dimension | values |
|---|---|
| `genre` (non-README documents only) | `tutorial`, `how-to`, `reference`, `explanation`, `cookbook`, `module map` |
| `target_document` | `readme`, `task_document`, `reference_document` |
| `claim_form` | `path`, `dependency`, `qualified`, `section_qualified`, `bare_call`, `bare`, `not_a_claim` |
| `context_source` | `heading`, `table`, `prose`, `list`, `path_prose`, `none` |
| `dependency_phrasing` | `name_only`, `display_plus_constraint`, `inline_backticked`, `table_row`, `extras`, `environment_marker`, `multi_in_sentence`, `range`, `install_command` |
| `dependency_form` | `constraint_break`, `removal` |
| `outcome` | `refuted`, `nei`, `none` |
| `none_sub` (artifact level) | `no_claim`, `other_referent`, `supported` |
| `target_line_status` | `refuted`, `nei`, `none` |
| `attribution` | `target_line`, `other_mention`, `both` |
| `bundle_status` | `verified`, `declined`, `invalid`, `verify_failed`, `apply_failed`, `timeout`, `no_output`, `unresolved`, `conflict` |

`genre` is **not** assigned to `README.md`; README is `target_document=readme`
and `genre=n/a`. This removes the previous inconsistent genre lists.

### 2.2 Six repos, three new domains

| repo | domain | natural project |
|---|---|---|
| `contourkit` | geospatial / terrain | elevation raster sampling, contour polylines, simplification |
| `tileplan` | geospatial / mapping | slippy-map tile coordinates, extents, zoom arithmetic |
| `morpheme` | language / text | morphological segmentation and lemma lookup for a small language pack |
| `bibscan` | language / scholarly text | BibTeX/CSL parsing and citation formatting |
| `serialscope` | instrument / lab hardware | serial-line framing and decoding for lab instruments |
| `sensorbus` | instrument / lab hardware | sensor reading aggregation, calibration, unit conversion |

Three domains, two repos each. **None** overlaps Stage B's domains
(environmental/energy, creative/visual, music/everyday), the dev/regression
repos (`quillpad`, `tidecast`, `ledgerly`, `parcelroute`), or the repos named in
the trial's differential (`fastapi`, `pydantic`, `celery`, `prefect`,
`scikit-learn`).

**Pre-registered backups** (used only after two generation failures, never
because of anything the engine says): `heightgrid` (geospatial), `tokenfold`
(text), `pulsecount` (hardware). A substitution is recorded with the failed
attempt, the reason, and the pre-freeze timestamp.

### 2.3 Three documents per repo, genre-only guidance

Every repo has exactly three tracked English Markdown documents:

1. `README.md` — install, what the project is for, a short quickstart
   (`target_document=readme`, `genre=n/a`).
2. one task-oriented document (`target_document=task_document`);
3. one reference or explanation document (`target_document=reference_document`).

Genres for documents 2 and 3 are fixed before generation:

| repo | `task_document` genre | `reference_document` genre |
|---|---|---|
| `contourkit` | `tutorial` | `reference` |
| `tileplan` | `how-to` | `reference` |
| `morpheme` | `explanation` | `reference` |
| `bibscan` | `cookbook` | `reference` |
| `serialscope` | `tutorial` | `module map` |
| `sensorbus` | `how-to` | `explanation` |

The corpus spans all six genres. Genres exist to span ordinary documentation
practice, not to exercise a predicate. The assignment is fixed before generation
for genre coverage only; no genre is chosen to create a `context_source`. If a
genre naturally yields no module context, that is a result.

`module map` is a **content genre** (what the document covers), not a layout
instruction; the docwriter may write it as prose and is given no heading, table,
or list template. `README` is a document role, not a genre.

**Genre-only instruction.** The docwriter receives the genre name and the normal
role contract. It is **not** told how to present names, modules, paths, tables,
lists, or dependencies. A genre name such as `module map` is permitted; what is
forbidden is a presentation template. In particular, the Stage C docwriter
prompt must not contain any of the following, and the prompt diff (§3.1) is
checked for them:

- "organise per module", "one section per module", "module heading";
- "module/symbol table", "table of symbols", "columns: module, symbol";
- "annotated list under module headings", "list the members under each module";
- "include a heading for each module", "group by module";
- any instruction to use qualified names, dotted names, backticks, Markdown
  links, version constraints, or a particular dependency phrasing;
- any mention of resolution, qualification, the engine, predicates, claims, or
  `SCOPE.md`.

The injector is likewise not steered toward any form (§5.1).

**Pre-registered backup genres** (used only after two generation failures, never
because of engine output):

| repo | backup for `task_document` | backup for `reference_document` |
|---|---|---|
| `contourkit` | `how-to` | `explanation` |
| `tileplan` | `tutorial` | `explanation` |
| `morpheme` | `reference` | `explanation` |
| `bibscan` | `how-to` | `reference` |
| `serialscope` | `how-to` | `reference` |
| `sensorbus` | `tutorial` | `module map` |

The actual `context_source` distribution is **measured after generation**, never
targeted. The report includes a descriptive Stage B-vs-Stage C style audit
(Appendix A2): document length, heading depth, table count, list count, backtick
density, and `context_source` shares. That audit is not a baseline comparison
and never appears in the headline.

### 2.4 Required versus optional spec surfaces

The `spec.json` schema is **unchanged from Stage B**. No new spec field is added
for evaluation purposes.

- **Required:** `project`, `dependencies`, `modules`, `docs`.
- **Optional:** `paths`, `data_files`.
- **Optional and not incentivised:** `config_keys`, `endpoints`,
  `schema_fields`, `enum_members`, `example_commands`.

Rules:

1. `endpoints`, `schema_fields`, and `enum_members` **must not** be declared by
   any Stage C spec. They are the clearest route back to a tool-shaped corpus.
2. `config_keys` may appear only in `serialscope`/`sensorbus` where a device
   configuration genuinely exists, and only if the architect would have written
   it without an evaluation in mind.
3. `example_commands` and `paths`/`data_files` may appear where natural
   (e.g. a data file the CLI reads); their presence is not a selection
   criterion.
4. The genre assignment, phrasing inventory, and context taxonomy live in
   `taxonomy.json` and `corpus_design.json` (both created at S0 and hashed in
   `scope_engine_freeze.json`; copied into `corpus_freeze.json`), **not** in
   `spec.json`, so neither the materializer nor the docwriter is shaped by the
   evaluation.

An engine-free `check_corpus_surface.py` enforces rule 1 and records the optional
surface counts as a corpus property. It never selects or rejects a repo.

### 2.5 Sampling: 4 classes × 6 repos × 3 seeds = 72 primary bundles

- Active classes: `path-location-drift`, `identifier-drift`,
  `removed-referent-drift`, `external-dependency-drift`.
- Seeds `1,2,3` are **independent injector draws**, not replicates of a fixed
  target.
- Each bundle is an independent git-less baseline/injected pair named
  `<repo>__<class>__s<seed>_<sample>`.
- **One mutation per snapshot.** No class or seed shares a snapshot.
- The 72 primary bundles are **`code_side` only**. `doc_side` is a separate
  exploratory arm and is never pooled (§5.5).
- If two seeds select the same target, both are kept. Retrying for diversity
  would bias the sample. The resulting **seed collapse** is measured and
  reported (§8.9).

### 2.6 Reporting axes fixed before generation (not selection criteria)

Recorded so no post-hoc subgroup is invented:

- `target_document` (`readme` / `task_document` / `reference_document`) and
  `genre` (`n/a` for README);
- `dependency_phrasing` from the frozen inventory;
- `context_source` and `claim_form` from the frozen taxonomy, assigned by the
  engine-free classifier (§7.2) and confirmed by annotation where available.

No target, document, or repo is chosen because a pattern is present.

### 2.7 Contamination and exclusion rules

A Stage C repo is rejected before freeze if any of the following holds:

1. It reuses a Stage A/B spec, source file, document paragraph, or repo name.
2. Any Stage C document shares a **12-token shingle** with any Stage A/B or
   dev-corpus document. This is the minimum check, not the only one.
3. **Expanded contamination checks** (engine-free) also run and are reported:
   - normalized-paragraph hash (whitespace/punctuation-folded);
   - 8-token shingle Jaccard and longest common token substring ≥ 25 tokens;
   - heading-sequence fingerprint (levels + normalized text);
   - source-code line hash against every Stage A/B and dev-corpus source file;
   - project name, top-level package, class/function name, and dependency
     requirement-string collisions;
   - document filename + line-count + word-count fingerprint.
   Any hit is reviewed by the auditor and either removed or documented in
   `contamination_report.json`. The 12-token check alone is not sufficient
   evidence of independence.
4. Any document contains tool vocabulary (`docassay`, predicate names,
   `REFUTED`, `SUPPORTED`, `NEI`, `drift`, `claim`) in a way that suggests the
   document was written for a checker.
5. The repo was used to develop E1–E6 or the section-qualification rule.

---

## 3. Generation and independent audit (no engine gate)

### 3.1 Roles, blindness, and model families

| role | writes | family constraint | sees |
|---|---|---|---|
| `repo-architect` | `spec.json` per repo | may share a family with the docwriter; **not** the injector | project description only; not this plan, `SCOPE.md`, predicates, or Stage B material |
| `repo-docwriter` | the three documents | **different family from the Stage B docwriter (Anthropic/Claude)**, and different from the injector | spec + materialised source + genre name only |
| `repo-auditor` | read-only audit report; never edits docs | **different family from architect and every docwriter family**; not the injector | spec, source, documents; not the engine, this plan, `SCOPE.md`, or Stage B material |
| `repo-injector` | one mutation proposal per bundle | different family from **every docwriter family used**; blind to the tool | frozen docs/source/spec + the Stage B exemplar bank, nothing else |
| reaction judges | LLM judge + deterministic diff judge | judge may share a family with the auditor; **not** the injector or docwriter | tool diff only |
| baseline adjudicator | baseline finding labels | independent of the engine; independent preferred | baseline finding + spec/source/docs |
| annotators | blind labels | see §7 | read-only corpus + spec/source |

**Model-family default.** Stage B's docwriter was
`opencode-go/claude-haiku-5-5` (Anthropic/Claude). Stage C defaults to a
docwriter from a **different family** from Stage B, and different from the
injector family. If no different family is available, a **pre-registered 3/3
split** is allowed: three repos use a non-Anthropic family, three use the
Stage B Anthropic family; the assignment is fixed at S0, before any document is
written, and never mixed within a repo. If neither a different family nor a
pre-registered split is available at S0, **C3 blocks sign-off**.

**New/diffed docwriter prompt.** The Stage C docwriter prompt is newly authored,
not copied verbatim from Stage B. It is diffed against
`runs/stage-b-2026-10-20/prompts_natural/docwriter.md` before the freeze.
Permitted differences: the genre instruction, the run/schema identifiers, and
removal of any presentation guidance. Every other difference is listed in the
deviations log with a justification that it does not shape target selection.
The diff and both hashes are frozen.

**Blindness.** The architect, docwriter, auditor, and injector run in sessions
with **no access** to the Stage B corpus, Stage B report, Stage B metrics, the
post-hoc regression directories, this plan, `SCOPE.md`, the predicates, or any
engine output. The run operator may know the design but must not paste Stage B
documents, results, or plan text into those sessions or into their prompts, and
must not retrieve `runs/stage-b-*` or `synthetic-natural/` into their context.
A blind-role attestation is recorded per role in `provenance.json`.

**Accurate independence statement.** Using a different docwriter family (or a
pre-registered split) removes **direct model-family sharing** with Stage B. It
does **not** establish independence from shared training corpora, shared
documentation conventions, or the shared genre taxonomy. It is not evidence that
the section-qualification rule is independent of generator style, and it does
not license a generalisation claim.

### 3.2 Procedure

1. **S0 first.** Choose C1 and C11 (§1.1, §8.8); amend `SCOPE.md` and
   `protocol.md`; freeze the engine and analysis artefacts in
   `scope_engine_freeze.json` (§4.1); run `freeze_scope_engine.py --verify`
   **before S1**. No spec may be written before this passes.
2. **Architect** writes one `spec.json` per repo from the project description.
3. **Materialise deterministically** with
   `generate_synthetic.py spec-validate` and `materialize`. Re-materialise to a
   temporary directory and require an empty diff.
4. **Docwriter** writes the three documents from `spec.json` and the
   materialised source, under the assigned **genre-only** instruction.
5. **Engine-free shape check:** three `.md` files, English, not a changelog /
   release-notes / roadmap / proposal, no tool vocabulary, expanded
   contamination checks (§2.7), spec-surface check.
6. **Auditor** reads spec, source, and documents, statement by statement, and
   returns `CONSISTENT` or a list of findings `{file:line, statement,
   correction, reason}`. The auditor is read-only.
7. **Docwriter applies factual corrections only.** The auditor re-audits.
   Maximum two rounds; a repo still not `CONSISTENT` after two rounds fails and
   is replaced by a pre-registered backup (repo and genre backups).
8. Record every fix in `audit/audit.json`: before/after file hash, line,
   statement before, statement after, audit finding, and — **for any fix that
   touches a target line, a control line, or a line that the classifier labels
   as a claim** — `before_claim_form`, `after_claim_form`,
   `before_context_source`, `after_context_source`. A correction must be
   factual; it may not be made to change a claim form or context. If a factual
   correction changes the form, that is recorded and the line is re-classified
   on the final text. Annotation and control sheets are built only from the
   final audited text.
9. **No engine run at any point in steps 1–8.** No `baseline-report`, no
   `check`, no `score`, no tool import.

### 3.3 Audit rules

- Fix **factual** errors only: a statement contradicted by the spec or the
  materialised source.
- Do not fix style, tone, omissions, or non-factual prose. Do not add claims.
- If a statement is ambiguous, mark it `UNDETERMINED` and leave it. Such a line
  is excluded from controls.
- The auditor must not use the engine, the predicates, `SCOPE.md`, or this plan.
- The audit is LLM-based unless an external auditor is available. It is reported as
  an independence-by-family audit, **not** as independent annotation.
- An audit correction that changes a line's claim form or context is recorded
  **before/after**; it is never silently re-labelled.
- If an audit correction invalidates a pre-registered control candidate, the
  control is **re-selected from the final text**, not edited, and the drop
  reason is recorded.

### 3.4 Engine-free spec-surface and genre acceptance checks

Two engine-free checks are frozen at S0 and run before corpus freeze:

1. **Spec-surface check** (`check_corpus_surface.py`): required fields present;
   forbidden fields absent; `config_keys` only in the two hardware repos;
   optional surfaces recorded with counts; each `docs` entry corresponds to an
   actual document role. It does not select or reject a repo.
2. **Genre acceptance check** (`check_genres.py` + the independent auditor):
   the auditor assigns each document 2/3 a genre from the frozen six-genre
   taxonomy using a frozen rubric, blind to the planned assignment. Acceptance
   requires assigned genre = planned genre. A mismatch is recorded; the repo may
   be regenerated (two attempts) or use the pre-registered backup genre. The
   check never requires a presentation form (no module headings, no tables) and
   never uses the engine.

A repo that fails either check is replaced by a pre-registered backup or
regenerated; the reason is recorded. Neither check may be used to choose a
corpus that makes the engine look better.

### 3.5 No engine gate

`generate_synthetic.py check` and `baseline-report` are diagnostics. A corpus is
never selected, rejected, or repaired on the basis of engine output. A 0-`REFUTED`
baseline is neither required nor treated as evidence of precision
(`protocol.md` §4.1).

---

## 4. Freeze and provenance

There are **two freeze files**. They cover different windows and are verified at
different points.

### 4.1 `scope_engine_freeze.json` (S0, before any spec)

Written and verified **before S1**. It records SHA-256 for:

- **scope and protocol:** `validation/SCOPE.md` (with the C1 amendment if
  C-ext), `validation/protocol.md` (with the C11 amendment), and this file;
- **engine code:** `git rev-parse HEAD`, empty `git status --porcelain`, and
  SHA-256 of every `src/docassay/**/*.py`, plus an aggregate;
- **engine data and vocabulary:** `src/docassay/data/**/*.json`,
  `src/docassay/vocabularies/**/*.py` (and any equivalent data directory),
  plus an aggregate;
- **tool environment:** `pyproject.toml`, `uv.lock`, `.python-version` if
  present, and the exact `python --version` string;
- **engine-free verifier and materialiser:** `engine/oracle.py`,
  `engine/grammar.py`, `scripts/generate_synthetic.py`, `scripts/_corpus.py`;
- **injector harness:** `llm_injection/scripts/llm_inject.py` and the judge
  scripts;
- **freeze tooling:** `scripts/freeze_corpus.py` and the **new**
  `scripts/freeze_scope_engine.py`, created as part of S0 before the S0 freeze
  (self-hash recorded at build);
- **prompts:** docwriter, auditor, injector system, four class prompts, output
  schema, and the four agent prompt files (`repo-architect`, `repo-docwriter`,
  `repo-auditor`, `repo-injector`); the Stage C docwriter prompt diff;
- **model IDs:** the exact ID string and a SHA-256 of each string for every
  role, plus the C3 family/split assignment;
- **annotation materials:** `annotation_codebook.md` and the engine-free
  claim-form/context classifier `classify_claim_context.py`;
- **corpus design:** `taxonomy.json` and `corpus_design.json` (genre
  assignment, phrasing inventory, context taxonomy);
- **analysis code:** `score_injections.py`, the Stage C metrics script, the
  bootstrap script, `build_controls.py`, `build_annotation_sheet.py`, the
  control-selection config, the judge rubric, the spec-surface and genre
  checkers, the contamination checker, and the bootstrap seed;
- an aggregate SHA-256 over the sorted `path:hash` lines, the freeze timestamp,
  branch, and commit.

The Stage C docwriter prompt is **newly authored** and diffed (§3.1); the
injector prompt is diffed against Stage B with only the schema `$id` permitted to
differ (§5.2). Both diffs are frozen.

### 4.2 `corpus_freeze.json` (S4, before injection)

`freeze_corpus.py` records SHA-256 for:

- every corpus file: source, `pyproject.toml`, `spec.json`, the three documents,
  example data — excluding `__pycache__`, `.pyc`, `.DS_Store`, `.git`;
- `taxonomy.json`, `corpus_design.json` (genre assignment, phrasing inventory,
  context taxonomy);
- `audit/audit.json` (including before/after claim form and context for touched
  lines);
- `controls.jsonl` for the applicable C1 arm, plus `control_config.json`;
- the contamination report and the genre/spec-surface acceptance reports;
- an aggregate SHA-256 over the sorted `path:hash` lines, the freeze timestamp,
  branch, and commit.

### 4.3 Verification points

All of the following must pass, in order:

1. `freeze_scope_engine.py --verify` **immediately before S1** (before any
   spec is written). A mismatch aborts; no spec is generated.
2. `freeze_scope_engine.py --verify` immediately before the injector run.
3. `freeze_corpus.py --verify` immediately before the injector run.
4. `freeze_scope_engine.py --verify` **and** `freeze_corpus.py --verify`
   immediately before scoring.
5. **`freeze_scope_engine.py --verify` and `freeze_corpus.py --verify` again
   immediately after scoring**, and the post-score result is recorded in the
   report (T1). A post-score mismatch invalidates the run even if the score
   completed.

There is no override. A missing verification record is a failed verification.

Commands (paths and flags fixed at S0):

```bash
B=research/submission/demo/injected_gold
RUN=$B/llm_injection/runs/stage-c-<signoff-date>
PYTHONPATH=src uv run python $B/scripts/freeze_scope_engine.py \
    --verify --freeze $RUN/scope_engine_freeze.json
PYTHONPATH=src uv run python $B/scripts/freeze_corpus.py \
    --verify --freeze $RUN/corpus_freeze.json
```

### 4.4 No post-freeze edits

Any change to an S0 artefact (§4.1) before the corpus freeze is a **new
version** of the scope/engine freeze and a **deviation**, recorded before the
affected corpus is generated. The new freeze is verified, and any generation
that used the old S0 artefact is redone. Any change after the corpus freeze
invalidates the run. A repair is a **new corpus/engine version** (`stage-c-v2`) with a new
freeze and a full re-run; both versions are reported. "Fix and continue" is
forbidden.

### 4.5 Provenance per bundle

`provenance.json` records per bundle: repo, class, seed, snapshot IDs, prompt
SHA-256, model ID and family, exemplar IDs, verifier result, target
document/line, `aux_edits`, and status (`verified`, `declined`, `invalid`,
`unresolved`, `verify_failed`, `conflict`, `apply_failed`, `timeout`,
`no_output`). It also records the blind-role attestation (§3.1).

---

## 5. Injections

### 5.1 Contract

Stage C reuses the Stage B **natural injector contract** verbatim, subject to a
hash-equality check (§5.2). Constraints:

1. **Natural prompt.** The injector picks a current-state statement a maintainer
   would make and a real artifact that exists. It chooses the target and the
   change the way a maintainer would.
2. **No extractor preconditions.** The prompt must not mention qualification,
   module headings, tables, Markdown links, backticks, version constraints,
   mention counts, "the checker", or any property that would make a mention
   easier to extract. No sentence may be added to improve extraction.
3. **No `kind`, no `artifact_class`, no `claim_form`.** The model emits only
   `injectable`, `drift_type`, `direction`, `file`, `old`, `new`, `symbol`,
   `target`, `doc_path`, `doc_line_text`, `target_claim`, `exemplar_ids`,
   `rationale`. The harness infers kind and artifact class. The model never
   emits a line number or an expected verdict.
4. **`injectable: false` is a valid outcome.** A substantive decline is not
   retried and is counted in the end-to-end denominator.
5. **One artifact per snapshot.** "Artifact" is the class-specific referent
   defined in §5.4, not the number of touched files. Mechanical auxiliary edits
   are allowed only as specified there; a proposal that changes a second
   artifact, a second document, or a second class is `invalid`.
6. **Forbidden:** `VERSION` (project version pins), value drift,
   cross-document drift, document-vs-document edits, behaviour/semantics,
   config keys, endpoints, schema fields, enum members,
   invalid-example-instruction, license, Dockerfile, and CI workflow. Capability
   classes appear only as optional controls.
7. The artifact must exist before the mutation and be absent or contradicted
   after it. The document line must exist verbatim before the mutation and the
   target token must be on it.
8. **Primary bundles are `code_side`.** The harness requires
   `direction=code_side` for the primary 72; this is a harness constraint, not a
   prompt change, a form steer, or an extractor precondition. A `doc_side`
   proposal is `invalid` for the primary 72 and is not replaced; `doc_side` may
   run only as the separate exploratory arm in §5.5.

The injector may choose a bare name, a qualified name, a call, a path, or a
dependency name. It is **not** steered toward any form.

### 5.2 Prompt provenance and anti-drift check

Before the freeze, the Stage C injector prompts are diffed against
`runs/stage-b-2026-10-20/prompts_natural/`. Permitted differences: the schema
`$id`, and nothing else. Any other difference is listed in the deviations log
with a justification that it does not shape target selection. The hash of every
Stage C prompt is frozen.

### 5.3 Exemplar bank

The Stage B bank is frozen and reused unchanged. No Stage A, B, or C incident is
added to it. No new exemplar is written for Stage C. The injector sees only the
bank entries for the requested class, and `exemplar_ids` is recorded per bundle.

### 5.4 Single-artifact rule, auxiliary edits, and class-specific verification

"One mutation per snapshot" is enforced at the **referent** level. A rename or
deletion may require mechanical edits so that the tree still parses; those edits
are recorded as `aux_edits` and are not additional artifacts.

| class | artifact identity | allowed mutation | allowed `aux_edits` | verifier checks |
|---|---|---|---|---|
| `path-location-drift` | one tracked path (file or directory) | rename or move the path | rewrite imports/references to the old path; nothing else | old path absent; new path present; exactly one path referent changed; every aux edit is a mechanical reference update; docs unchanged; tree parses |
| `identifier-drift` | one top-level class/function | rename the definition | rewrite internal references/call sites to the new name | old qualified name absent; new name present; AST diff is a rename mapping only; no other public symbol added/removed; docs unchanged |
| `removed-referent-drift` | one top-level class/function | delete the definition | remove or rewrite internal references/imports | old qualified name absent; no new public symbol; tree parses/imports; docs unchanged |
| `external-dependency-drift` | one manifest requirement | break the constraint or remove the requirement | none | exactly one dependency entry changed; old requirement satisfied before; not satisfied (or absent) after; docs unchanged |
| `doc_side` path (exploratory) | one document path token | substitute one token | none | old path exists; new path absent; exactly one token changed; code unchanged |

Class-specific verification also checks that the mutation does not introduce a
second drift type: no symbol rename in a path injection, no manifest edit in a
symbol injection, no document edit in any primary injection, and no change to
`spec.json`. A failure is `verify_failed` with a reason; it is counted in the
end-to-end denominator and dropped from the verified numerator. This replaces
the earlier "the diff touches exactly one file and one token" wording, which
conflicted with rename call sites.

### 5.5 Direction: `doc_side` is a separate exploratory arm

The primary 72 bundles are `code_side` only. `doc_side` path injections are
**not** pooled with them and do not enter the 72 denominator. If resources
permit, a separate exploratory arm is pre-registered in a short addendum
**before it is generated**; it uses the same repos and seeds, reports its own
denominator, and is labelled exploratory. A `doc_side` injection edits the claim
rather than the artifact and is never used to support a claim about code-side
detection.

**OPEN-C7:** whether the exploratory arm runs at all. Default: **not run**;
`doc_side` is `n/a` in the result.

---

## 6. Controls

Controls are selected **engine-free**, from the frozen documents plus the
structural inventory and the spec, **before any engine run**, and are evaluated
on the six **clean** baselines (not on injected trees). Both the C-ext and
C-base pattern sets are pre-registered in `control_config.json`; only the set
applicable to the C1 arm is evaluated.

### 6.1 Families (conditional on C1)

**C-ext (section qualification adopted):**

| family | required | definition | expected |
|---|---:|---|---|
| A1 consistent-present, path | 6 | a current-state path claim that exists in the baseline | not `REFUTED` |
| A2 consistent-present, dependency | 6 | a current-state dependency claim that the manifest satisfies | not `REFUTED` |
| A3 consistent-present, qualified symbol | 6 | a document-written dotted symbol claim that resolves | not `REFUTED` |
| A4 consistent-present, section-qualified symbol | 6 | a bare symbol under a document-supplied project module context whose qualified name resolves | not `REFUTED` |
| B non-module context trap | 6 | a bare symbol under a heading/cell/prose context that **looks** like module context but is not a project module path (e.g. a "Parsing" heading, a "parsing helpers" column label), and the symbol exists somewhere in the project | not `REFUTED` |
| C consistent-absent (optional) | ≤6 | a true current-state absence claim ("no Dockerfile is shipped"; "the package does not depend on pandas") | not `REFUTED`; `NEI` expected for absence |

**C-base (no section qualification):**

| family | required | definition | expected |
|---|---:|---|---|
| A1 consistent-present, path | 6 | as above | not `REFUTED` |
| A2 consistent-present, dependency | 6 | as above | not `REFUTED` |
| A3 consistent-present, qualified symbol | 6 | as above | not `REFUTED` |
| A4 | **n/a** | not applicable: no section-qualified form exists | — |
| B | **n/a** | not applicable: no qualification; a non-module trap is not a distinct control | — |
| C consistent-absent (optional) | ≤6 | as above | not `REFUTED` |

Family A is one control per repo per applicable family: **24 required in C-ext**
(A1–A4), **18 required in C-base** (A1–A3). Family B is one per repo in C-ext:
**6 required**. Family C is opportunistic: zero is a valid count and is reported
as `n/a`, never as `0/0` or `100%`.

### 6.2 Selection, drop, and shortfall

For each family, candidates are document lines matching the fixed patterns in
Appendix B. The selector takes candidates in a fixed document order (README,
then `task_document`, then `reference_document` by filename) with a per-repo
offset derived from a fixed seed, and records the line, the referent, the truth
check, and every rejected candidate. The selector script, config, and seed are
hashed at freeze.

A candidate is **dropped** (not replaced by a fabricated control) if:

- the truth check fails (the artifact does not exist / the manifest does not
  satisfy it / the qualified name does not resolve);
- the line is not a current-state claim (`historical`, `illustrative`,
  `conditional`, `not_a_claim`);
- the line is `UNDETERMINED` after audit;
- the candidate does not match the family definition (e.g. A4 has no module
  context, or B's context is actually a project module);
- a factual audit fix removed the line.

Per-family reporting: `required`, `evaluated`, `dropped` (with reasons),
`shortfall = required - evaluated`, and `not_applicable` where C1 makes the
family n/a. A shortfall is a corpus result, not a reason to relax the family.
Controls are never selected from the tool's claims, findings, or output.

### 6.3 Reporting: specificity, precision, extraction, false positives

These are four different quantities and are reported separately for the primary
set (A + B in C-ext; A in C-base) and for C:

1. **Specificity / non-refutation over all evaluated controls:**
   `1 - refuted / evaluated`. This is the primary control estimand. Every
   control is in the denominator whether or not the tool extracted it. If
   `evaluated = 0`, the family is `n/a`.
2. **Precision over extracted controls only:**
   `1 - refuted / extracted`. A control is **extracted** if the tool formed at
   least one claim on the control's document line whose source token is the
   control's target token, regardless of the referent the engine assigned; a
   control with no claim on that line/token is **not extracted** and is
   **excluded from the precision denominator**. `referent_matched` (the claim's
   referent equals the control's expected referent) is reported separately. A
   non-extracted control is never counted as evidence of precision. If
   `extracted = 0`, precision is `n/a`.
3. **Extraction rate:** `extracted / evaluated`, per family, with the
   `SUPPORTED` / `NEI` / `none` split of the non-refuted controls and the
   `referent_matched` count.
4. **Individual false positives:** every control refutation is listed with
   repo, document, line, referent, family, `claim_form`, and `context_source`.
   A control refutation is a new `REFUTED` finding on the control's document
   line whose source token is the control's target token, **regardless of the
   referent the engine assigned**. This is required for family B: a wrong
   qualification to a non-module referent is the trap, and counting only
   same-referent refutations would miss it. It is a false positive regardless
   of rate, unless adjudication shows the control line was actually false (a
   corpus defect; reported and handled as a deviation, not silently removed).

A single control refutation blocks a "0 false positives" claim but does **not**
invalidate the run; it is reported and adjudicated. Controls never enter the
four-class refutation denominator. Capability controls (`LICENSE`,
`HAS_DOCKERFILE`, `HAS_CI_WORKFLOW`), if naturally true, are reported as a
separate opportunistic arm (**OPEN-C8**) and never pooled.

---

## 7. Independent annotation

### 7.1 Annotators, blindness, and the one-annotator rule

- **At least one non-author annotator is required** for any externally confirmed
  label. An author of this plan, of the corpus generation (architect, docwriter,
  auditor), or of the engine is not an annotator. If the only available
  annotator is an author, the independent arm does not run.
- **Two independent annotators** are required for the final,
  independently validated result and for IAA. With **one** non-author annotator, Stage C
  may publish a **provisional** report with externally confirmed labels but **no
  IAA**, and the final independently validated claim stays blocked. With zero, see
  §7.6.
- Annotators are blind to every tool verdict, layer, reason, reaction, metric,
  claim dump, and to each other's labels. They have **read-only** access to the
  frozen corpus, spec, and source; no engine; no write access; no Stage B
  report, metrics, or regression directory; no `entries.json`, `claims/`, or
  `bootstrap.json`.
- The sheet is generated mechanically from the frozen manifest and controls. It
  contains no entry IDs that encode outcome, no sort order that groups by
  outcome, and no tool field.

### 7.2 Frozen codebook and engine-free classifier

- `annotation_codebook.md` (frozen at S0) defines every field, the decision
  order, examples, and tie-breaks. It is the normative annotation text.
- `classify_claim_context.py` (frozen at S0) is an **engine-free**,
  deterministic classifier that assigns `claim_form`, distinguishes
  `section_qualified` from `qualified`, and assigns `context_source` from the
  frozen text using the §9.1 rules. It does not import `docassay` and does
  not read tool output. It has a self-check and is hashed.
- The classifier supplies the scoring labels for T4/T5; independent labels are
  compared to it (agreement), never replaced by it. The classifier is not shown
  to annotators before they label, to avoid anchoring.
- If the classifier and an annotator disagree, both labels are reported; no
  silent relabelling.

### 7.3 Sheet fields and framing

Per row: `repo`, `class`, `target_document`, `genre`, `doc_path`, `line`,
`target` text, `mention_text`, `mention_role` (`target_line` / `other_mention` /
`control`), mutation `old → new`, `symbol` where applicable, `target_claim`
(the injector's stated claim, explicitly labelled **"injector's description,
not ground truth"**), `control` family (`none` for injections), and
`artifact_identity` in normalized form. Blank fields for the annotator:

- `claim_type`: `current_claim` / `historical` / `illustrative` / `conditional`
  / `not_a_claim`;
- `claim_form`: `path` / `dependency` / `qualified` / `section_qualified` /
  `bare_call` / `bare` / `not_a_claim`;
- `context_source`: `heading` / `table` / `prose` / `list` / `path_prose` /
  `none`;
- `defect_is_real`: `yes` / `no` / `n/a` (controls);
- `nei_reason_applies`: `yes` / `no` / `n/a`;
- `none_claim_not_extracted`: `yes` / `no` / `n/a`;
- `control_false_positive`: `yes` / `no` / `n/a`;
- `same_artifact` for cross-mention rows (`yes` / `no` / `unsure`);
- `annotator_id`, `notes`.

**Target-claim framing.** The sheet includes `target_claim` only as the
injector's description. Annotators judge `defect_is_real` themselves against the
frozen tree and the document line; they are told not to trust `target_claim` and
not to infer a verdict from it.

**Cross-mention rows.** For every injected artifact, the sheet contains one row
for the recorded target line and one row for **each other document mention** of
the same artifact that the frozen scorer could credit. Rows are shuffled without
saying which is the target. This makes the cross-mention split auditable rather
than post-hoc.

**Coverage.** Every verified injection and every applicable control is
annotated. No subsampling, even if the sheet exceeds 120 rows. A control that
was dropped or n/a is not a row.

### 7.4 Secondary, non-blind sheets

Two secondary sheets are prepared and clearly labelled as **not** the primary
independent labels: the first contributes agreement statistics for its own fields, and
the second is never used for IAA.

1. **Cross-mention attribution sheet (blind to attribution).** For every
   credited refutation, the target line and the crediting mention(s) are
   presented in random order without saying which one the tool used. The
   annotator answers `same_artifact` (`yes`/`no`/`unsure`),
   `both_current_claims` (`yes`/`no`/`partial`), and `notes`. A cross-mention
   refutation is credited in the final table only if `same_artifact` is `yes`;
   raw and externally confirmed counts are both reported.
2. **Wrong-support sheet (verdict-visible).** For the `none`/`supported`
   sub-case, the target claim and the mutated artifact are shown and the
   annotator answers whether the claim is false in the frozen tree and whether
   `SUPPORTED` is wrong. This sheet is not blind and is never used for IAA.

### 7.5 Agreement

Cohen's κ on `claim_type`, `claim_form`, `context_source`, `defect_is_real`,
and each stream field (`nei_reason_applies`, `none_claim_not_extracted`,
`control_false_positive`), plus the cross-mention fields. Report percent
agreement alongside κ, because κ is unstable on skewed fields (almost all
`defect_is_real = yes`). Target **κ ≥ 0.60**; report the observed value whatever
it is. No field is dropped for low κ. Disagreements are adjudicated by a third
reader or by consensus and the resolution is logged.

With **one** annotator: report n = 1, no κ, and label the independent arm
**provisional**. With two: report IAA.

### 7.6 Blocker rule and no LLM gold

If no non-author independent annotator is available, Stage C may publish only a
**provisional engine-only report**, labelled provisional, with no independent labels and
no external confirmation. If one non-author annotator is available, it may publish
a **provisional externally confirmed report** with no IAA. The final Stage C result,
and any claim that detection is independently validated, is **blocked** until two
annotators complete the sheet. LLM labels are never presented as independent labels,
and a low κ is reported, not replaced. **OPEN-C9.**

---

## 8. Scoring

### 8.1 Outcomes at the injected-artifact level

Every **verified** injection gets exactly **one artifact-level outcome**. This
replaces the earlier target-line-only definition, which conflicted with
cross-mention credit.

Let `A` be the injected artifact identity (class-specific; §8.2). Let `F` be the
set of **new** findings in the baseline→injected difference: a finding is new if
its `(doc_path, line, predicate, referent)` is absent from the baseline, or its
verdict changed to `REFUTED`/`NEI` in the injected tree. A **same-artifact
finding** is a new finding whose referent matches `A`.

A **same-artifact claim** is any claim in the injected run whose referent matches
`A`, pre-existing or new; `pre_existing` is recorded. Only a **new** `REFUTED`
finding counts for `refuted`; `nei` and `supported` are read from same-artifact
claims in the injected run.

| artifact outcome | definition |
|---|---|
| `refuted` | at least one new same-artifact finding is `REFUTED` |
| `nei` | no same-artifact `REFUTED`, and at least one same-artifact claim is formed and abstains (`NEI`), with layer and verbatim reason |
| `none` | no same-artifact `REFUTED` and no same-artifact `NEI` |

`none` is sub-flagged in this priority order:

- `supported`: a same-artifact claim is formed and wrongly returned `SUPPORTED`;
- `other_referent`: no same-artifact claim, but a claim covers the recorded
  target line at a different referent;
- `no_claim`: no same-artifact claim and no claim on the target line.

`refuted + nei + none = verified` for every class. The old sentence "`none` = a
claim at a different referent" is now only the `other_referent` sub-flag; it is
not the whole `none` category.

**Target-line status is recorded independently** for every injection:

| target-line status | definition |
|---|---|
| `refuted` | a new same-artifact `REFUTED` finding on the recorded `doc_path` and line |
| `nei` | no target-line `REFUTED`, but a same-artifact claim on the target line abstains |
| `none` | otherwise; sub-flagged `supported` / `other_referent` / `no_claim` as above |

Target-line status uses the priority `refuted > nei > none`. This yields the
crosstab in T10. An artifact can be `refuted` at the artifact
level while its target line is `none` — that is a cross-mention credit, not a
target-line detection.

**Attribution** is mutually exclusive:

- `target_line` — a `REFUTED` same-artifact finding exists on the recorded line,
  and no other-mention `REFUTED` exists;
- `other_mention` — no target-line `REFUTED`, but at least one same-artifact
  `REFUTED` elsewhere;
- `both` — target-line and other-mention `REFUTED` findings both exist.

For the target-line rate, `target_line` and `both` count as target-line; for the
off-target share, only `other_mention` is off-target.

### 8.2 Artifact matching per class

Credit requires the **same artifact**, not a same-named word:

- **path:** normalized inventory path equality (case-folded where the inventory
  is case-insensitive). A bare filename elsewhere is credited only if it
  resolves unambiguously to the same old path.
- **dependency:** normalized package name (fold `_`/`.` to `-`, case-fold), plus
  the relevant requirement relation.
- **identifier / removed-referent:** qualified project-owned name equality. An
  other mention is credited only if the document supplies a project-owned
  qualifier that resolves to the injected symbol; a bare mention elsewhere with
  the same last segment is **not** enough. In C-ext, a `section_qualified`
  mention of `M.T` is the same artifact as the injected `M.T`.
- **doc_side path (exploratory):** the replaced token's old path identity.

A finding at an unrelated referent is never credited.

### 8.3 Estimands: credited versus target-line

Three rates, always reported with raw counts:

- **Credited refutation rate** `R_credit = |{i: outcome = refuted}| / verified`.
  This is the protocol-level recall (`protocol.md` §4.4: a refutation found
  anywhere in the diff).
- **Target-line refutation rate**
  `R_target = |{i: target_line_status = refuted}| / verified`.
- **End-to-end refutation** `R_end = |{i: outcome = refuted}| / 72`.

Per-class **primary estimand** is fixed before scoring:

| classes | primary | co-reported |
|---|---|---|
| `path-location-drift`, `external-dependency-drift` | `R_credit` | `R_target` |
| `identifier-drift`, `removed-referent-drift` | `R_target` | `R_credit` (protocol recall) |
| overall (T2) | **no single headline** | both `R_credit` and `R_target`, side by side |

No class headline is reported without both columns for the symbol classes. A
credited-only symbol rate is not evidence that target-line claims are detected.

### 8.4 Rates, denominators, and end-to-end statuses

- Refutation rate = `refuted / verified`; abstention rate = `nei / verified`;
  extraction-miss rate = `none / verified`. This is the generic outcome table;
  per-class primary rates are fixed in §8.3. Report raw counts next to every
  rate. `NEI` is never folded into the miss column or the refutation numerator.
- **End-to-end:** `R_end = refuted / 72`, with `verified / 72`, decline rate,
  unresolved rate, conflict rate, and generator-failure rate reported
  separately.

A bundle that is not verified is **not** `none`. It is a `bundle_status` and
stays in the 72 denominator:

| status | meaning | retry |
|---|---|---|
| `declined` | substantive `injectable:false` | no |
| `invalid` | multi-artifact, forbidden class, unsuitable target, or `doc_side` in primary | no |
| `verify_failed` | oracle rejects the applied mutation | no |
| `apply_failed` | patch cannot be applied | no |
| `timeout` | infrastructure timeout | one infrastructure retry |
| `no_output` | runner produced no JSON | one infrastructure retry |
| `unresolved` | valid response but no usable target claim/artifact after parsing | no |
| `conflict` | proposal conflicts with the frozen tree or another artifact | no |

`unresolved` and `conflict` are generator/harness outcomes, never tool
outcomes. A class with fewer than 12 verified injections is reported as
**underpowered**; its rates are shown but not treated as a class estimate. If
overall `verified < 48`, the run is reported as a **corpus/injector failure**
and no class or headline claim is made.

### 8.5 Per-class, per-form, per-genre, per-document tables

Report:

- class × artifact outcome, with `R_credit` and `R_target`;
- `claim_form` × outcome;
- `context_source` × outcome, with target-line / cross-mention split;
- `genre` × outcome;
- `target_document` × outcome;
- `dependency_phrasing` and `dependency_form` × outcome;
- per-repo × outcome.

Cells with zero entries are shown as `0` and labelled, not dropped. `genre` is
`n/a` for README.

Claim forms for Stage C: `path`, `dependency`, `qualified`, `section_qualified`,
`bare_call`, `bare`. `section_qualified` is a measured cell only in C-ext.
Dependency form: `constraint_break` / `removal`.

### 8.6 Controls

Report as specified in §6.3: specificity over all evaluated controls, precision
over extracted controls, extraction rate, per-family n/drop/shortfall, and the
individual FP list. A single control refutation blocks a "0 false positives"
claim but does not invalidate the run. C = 0 is `n/a`.

### 8.7 Baseline findings

Run the engine once on the six clean baselines and record every `REFUTED` claim.
Adjudicate each as `true_doc_bug`, `tool_false_positive`, or `undetermined`:

- the adjudicator is independent of the engine and does not use engine output as
  evidence (independent preferred; an independent-family LLM may assist, with independent
  spot-checks and reported agreement);
- do **not** edit the corpus to remove a finding; a repair is a new version with
  a new freeze;
- report both counts, plus unattributed findings on the injected trees as a
  precision proxy.

A control refutation at a verified-true statement is a baseline
`tool_false_positive` by construction; the two views are cross-referenced.

### 8.8 Uncertainty: repo-cluster bootstrap, no Wilson

- Primary interval: **percentile bootstrap by repository** (6 clusters, 10,000
  replicates, fixed seed), for `R_credit` and `R_target`, overall and per class.
- Report the **leave-one-repo-out** minimum and maximum as a robustness check
  for both rates.
- **No Wilson interval is reported anywhere**, including controls. Wilson
  assumes independent Bernoulli trials, and the 72 entries are not independent:
  seeds repeat targets within a repo, and Stage B's distinct-target counts were
  6/8/15/14 (`runs/stage-b-2026-10-20/report.md` §6.8).
- With six clusters, per-class bootstrap values move in multiples of 3 and
  `0/18` or `18/18` intervals are degenerate. Report them as degenerate, not as
  certainty.
- Controls are reported as counts and an FP list, not as an interval.

**C11 is a sign-off blocker, not an optional deviation.** `protocol.md` §5
currently requires a Wilson 95% CI for the refutation rate. Before sign-off,
`protocol.md` §5 is amended to the following (or Stage C does not start):

> **Refutation rate** — `refuted / N`, with a repository-cluster percentile
> bootstrap 95% interval (6 clusters, 10,000 replicates, fixed seed) and a
> leave-one-repo-out range. Wilson is not used: the entries are not independent
> Bernoulli trials because seeds repeat targets within a repository. With six
> clusters the interval is descriptive and may be degenerate. The sentence
> making Wilson the only per-class CI is removed; both `R_credit` and
> `R_target` carry the bootstrap interval.

The amended `protocol.md` is hashed in `scope_engine_freeze.json`. If it is not
amended, the plan and the normative protocol disagree and the run is aborted;
Stage C does not "supersede" the protocol by itself.

### 8.9 Effective sample size

Report per class: entries, distinct `(repo, artifact)` pairs, number of seeds that
collapsed onto an existing target, and the per-target outcome table. The
per-target table is a sensitivity analysis, not the headline. Symbol classes are
expected to collapse; do not treat 18 entries as 18 independent claims.

### 8.10 Judges

Per `protocol.md` §4.5, two independent adjudicators of the tool's **reaction**:
an LLM judge with a frozen rubric (hashed at S0) and a deterministic diff judge.
Report agreement; resolve disagreements manually and log them. Judges never
decide whether an injection is a real defect.

### 8.11 Pre-registered table list

The Stage C report must contain these tables; no metric outside this list may
become the headline:

| id | table |
|---|---|
| T1 | freeze and provenance status (scope/engine and corpus hashes; pre- and post-score verification) |
| T2 | overall three outcomes, `R_credit`, `R_target`, repo-cluster CI |
| T3 | class × outcome (counts, rates), credited and target-line; primary estimand per §8.3 |
| T4 | `claim_form` × outcome |
| T5 | `context_source` × outcome, with target-line / cross-mention split |
| T6 | `genre` × outcome |
| T7 | `target_document` × outcome and per-repo × outcome |
| T8 | `dependency_phrasing` and `dependency_form` × outcome |
| T9 | end-to-end statuses: planned / verified / declined / invalid / verify_failed / apply_failed / timeout / no_output / unresolved / conflict / refuted |
| T10 | credited × target-line crosstab (counts), per class; shows `refuted`/`none` cells caused by cross-mention credit |
| T11 | controls: specificity, precision over extracted, extraction rate, per-family n/drop/shortfall, FP list |
| T12 | baseline findings and adjudication |
| T13 | effective sample size and seed collapse |
| T14 | annotation coverage, κ, and stream agreement (n = 1 or 2) |
| T15 | deviations log |

Exploratory analyses are allowed but are labelled exploratory and cannot replace
a T-table. Appendix A2 (style audit) is descriptive and not a result table.

---

## 9. The section-qualified scope (C-ext) and engine reporting

### 9.1 Normative text for `SCOPE.md` §3.3.2 (frozen verbatim at S0)

This block is the **exact** text inserted into `SCOPE.md` if C1 = C-ext. It is
hashed as part of `SCOPE.md`. If any word of the adopted rule differs from this
block, the freeze records the difference as a deviation.

> **§3.3.2 Section-qualified name**
>
> A **section-qualified name** is a bare member token that the document itself
> ties to a project-owned module. It is a claim form in its own right; it is not
> a bare name and it is not a general licence to qualify names.
>
> A bare token `T` on line `L` is section-qualified to module `M` if and only if
> all of the following hold.
>
> 1. **Project-owned qualifier.** `M` is a Python module in the project's own
>    tree, and its top segment is a top-level package/module of the project (as
>    declared by the project's packages), not an external dependency, stdlib
>    module, domain word, or file that does not map to a module. If `M` is not
>    in the project's module inventory, no qualification occurs.
> 2. **Document-supplied context.** `M` is supplied by one of:
>    - `heading`: a heading names `M` as a module, and the token is in that
>      heading's section;
>    - `table`: a cell in the same table row names `M` in a module position
>      (a header labelled module/package/namespace, or a cell that resolves to
>      `M` and is not the symbol cell), and another cell contains `T` as a
>      member token;
>    - `prose`: the same sentence or clause names `M` as a module (`the M
>      module`, `M module`, `in M`, `from M`, `M provides/declares/exposes/
>      contains/defines`), and `T` is the only code-shaped bare member token;
>    - `list`: a list item under a `heading` context naming `M`, or a list item
>      whose lead-in names `M` as a module;
>    - `path_prose`: a path token resolves to exactly one project-owned `.py`
>      module `M`, the path is explicitly presented as a module/source file
>      (`the M module`, `in M`, `M provides`), and `T` is the only code-shaped
>      bare member token on the line. A path to a data file, asset, template,
>      directory, or non-`.py` file is not a module qualifier.
> 3. **Heading reset.** A heading that names a project module sets context `M`
>    at its level. A code-shaped member/signature subheading of a module heading
>    inherits `M` and does not change it (it is the target line, not a new
>    module). A heading that is neither a module nor a code-shaped member (for
>    example `Notes`, `Installation`, `Parsing`) clears `M`. A heading of the
>    same or higher level than the module heading clears `M` unless it itself
>    names a module. A fenced code block is not a context and does not inherit
>    or set `M`.
> 4. **One-token guard.** Exactly one code-shaped bare member token `T` is on
>    the line. If two or more candidate bare tokens are present, no token is
>    qualified (`context_ambiguous`). A path, a call with a receiver other than
>    `M`, a dotted name, a builtin, a keyword, a placeholder, a dunder, an
>    environment variable, or a CLI flag is not a member token.
> 5. **Gap guard.** In `prose`, `path_prose`, or `list`, if a usage verb from
>    {`uses`, `calls`, `invokes`, `wraps`, `delegates to`, `is used by`,
>    `depends on`} stands between the `M` reference and `T`, the token is not
>    qualified: the sentence asserts a use relation, not membership. If `M` is
>    explicitly a module reference (`the M module`) and the verb is from
>    {`provides`, `declares`, `exposes`, `contains`, `defines`, `documents`,
>    `includes`}, qualification is allowed.
> 6. **Precedence.** If more than one context applies on one line:
>    same-line explicit module reference (`prose`/`path_prose`) > table row >
>    innermost module heading. If the winning context gives `M1` and another
>    applicable context gives a different project module `M2`, no qualification
>    occurs (`context_conflict`). If both give the same `M`, qualification
>    proceeds.
> 7. **Resolution.** The claim is `M.T`, with `claim_form =
>    section_qualified`, `context_source` as recorded, `context_module = M`, and
>    `context_line` = the line that supplied `M`. It is `REFUTED` only if `M` is
>    project-owned and `M.T` is absent from the project AST inventory. It is
>    `SUPPORTED` if `M.T` exists. If `M` is not in the project inventory, no
>    claim is formed (or the existing `NEI "top not in project packages"`). A
>    bare token with no context remains bare and is never `REFUTED`.
> 8. **No chaining.** A section-qualified name is not used to qualify a second
>    token on the line, and it does not cross into another document.
> 9. **Recorded context.** Every claim records `claim_form` (`qualified` or
>    `section_qualified`), `context_source`, `context_module`, and
>    `context_line`. A `section_qualified` claim with `context_module = null` is
>    a defect and is reported.
>
> A bare call (`T()`) under a module context is section-qualified to `M.T`; when
> qualification occurs, `claim_form` is `section_qualified`, not `bare_call`.
> A call with an explicit receiver other than `M` is not qualified.
>
> A document may write a dotted name directly. That is `qualified`, not
> `section_qualified`, even if a heading also names the module.

### 9.2 Boundary cases (normative)

| case | outcome |
|---|---|
| heading `## contourkit.grid`, then `### sample()` | `section_qualified` to `contourkit.grid`, `context_source=heading` |
| `## Notes` under a module heading | clears the module; a bare name below is `bare` |
| heading `### class Canvas` under `## plotline.canvas` | member heading; inherits `plotline.canvas`; `Canvas` may be section-qualified |
| two bare member tokens on one line | no qualification; `context_ambiguous` |
| `The M module uses parse` | no qualification (usage-verb gap) |
| `The M module provides parse` | qualification allowed |
| table row `\| Canvas \| plotline.canvas \| ... \|` | `section_qualified` if the module cell is in a module position |
| code fence containing `parse` | no claim; fences are not context |
| `palette/harmony.py provides generate_palette` | `section_qualified` via `path_prose` only if the path maps to a project `.py` module and is presented as a module |
| `docs/guide.md provides ...` | no qualification: data/document path, not a module |
| `numpy.array` | `qualified`, foreign top; `NEI "foreign top segment"` |
| `morpheme.lexicon.lookup` written directly | `qualified`, not `section_qualified` |
| module heading and same-line prose name different project modules | `context_conflict`; no qualification |
| module heading names an external package | no qualification; bare remains bare |
| `T` is a builtin/keyword/dunder/placeholder | no qualification |
| `M.T` exists in another module only | `section_qualified` to `M`; `M.T` is absent from `M` → `REFUTED` (the symbol exists elsewhere, but not in `M`) |

### 9.3 C-base definition

If C1 = C-base:

- `SCOPE.md` §3.3.2 is not adopted; the bare-name policy of §3.3.1 is unchanged.
- A bare name is never `REFUTED`; only a document-written dotted `qualified`
  name whose top is project-owned is refutable.
- `section_qualified` is not a produced claim form; the classifier reports it as
  `n/a`; `context_source` is recorded descriptively only.
- A4 and B controls are `n/a`.
- Symbol-class rates are reported as **policy-limited**: a low rate is the
  declared bare-name policy at work, not a hidden engine miss. The report must
  say this in the same sentence as the symbol rate.

### 9.4 Bare-name policy compliance

Report the number of targets with **no** module context, their outcomes, and the
count of `REFUTED` among them. Under `SCOPE.md` §3.3.1 that count must be
**zero**. A bare refutation is a policy violation and is reported as an engine
defect, never as a detection success. Report `NEI "unresolved bare name"` counts
separately from extraction misses. In C-ext, a bare target that the document
supplies no module for is still bare; the qualification rule never applies
retroactively.

### 9.5 E1/E2/E3/E4/E5/E6 reporting

The engine composition is fixed per arm at S0 and hashed:

| item | C-base | C-ext | expected direction |
|---|---|---|---|
| E1 duplicate versioned dependency mention | included with E6 | included with E6 | `SUPPORTED` → `REFUTED` for the E1 shape |
| E2 disjoint constraint intervals | included | included | `SUPPORTED` → `REFUTED` for the E2 shape |
| E3 kind-aware bare candidate | included | included | `SUPPORTED` → `NEI`; no refutation gain |
| E4 heading anchoring of bare names | excluded | included | `none` → `NEI`/`SUPPORTED`; enables §3.3.2 |
| E5 same-line referent preference | excluded | included | `none` → `NEI`/`SUPPORTED`; no refutation gain alone |
| E6 migration/compatibility/historical version gate | included with E1 | included with E1 | prevents E1 false positives on historical prose |
| §3.3.2 section-qualified name | not adopted | adopted | `bare`/`none` → `section_qualified` where context exists |

**E6 is a precondition for E1.** The post-hoc real-repo audit found E1 amplifies
pre-existing migration/compatibility false positives (5 clear FPs in
`regression-trial-plus-e1e2/README.md`). If E6 is not implemented, unit-tested,
and hash-frozen at S0, **E1 is not included**; the composition without E1 is
recorded in `scope_engine_freeze.json` and dependency version-break claims are
reported as a known engine limitation. **OPEN-C12** must be resolved at S0; it
is blocking for any run that claims E1.

Report dependency injections by shape, not only in aggregate:

| shape | expected |
|---|---|
| duplicate display name + constraint on one line (`NumPy (numpy>=1.24)`) | the versioned occurrence owns the claim; refutes when the manifest no longer intersects |
| disjoint lower/upper bounds (`>=8.1` vs `<8.1`) | refutes when intervals are disjoint |
| plain name + constraint | refutes when the manifest excludes the claimed version |
| dependency removal | `NEI "undeclared (open by transitivity)"` by policy, not a miss |
| extras / markers / table rows / ranges | report outcome per phrasing; `NEI` is a legitimate result |
| migration/compatibility/historical version prose | E6 gate; not a current-state requirement; report any residual FP |

The report must state whether each E1/E2 shape refuted on Stage C, with counts,
and whether the fixes produced any **new baseline or control false positive** on
dependency claims. A single refuting case is not evidence that a fix "works";
the counts are the evidence. `NEI` on removal form is not counted as a miss or a
refutation.

### 9.6 Cross-mention inflation risk

Section qualification makes off-target mentions refutable, and
`protocol.md` §4.4 credits a refutation found anywhere in the diff. Stage C must
therefore report, for every class and every context pattern:

- the credited refutation rate `R_credit`;
- the target-line refutation rate `R_target`;
- the off-target share `(R_credit - R_target) / R_credit`, reported as `n/a`
  when `R_credit = 0`;
- the externally confirmed off-target share after the cross-mention sheet; if no
  annotator is available, the raw share only, labelled provisional.

If a class's credited rate materially exceeds its target-line rate, the report
must say so in the same sentence as the rate. A class whose credited
refutations are mostly cross-mention is **not** evidence that target-line claims
are detected. No aggregate that hides this split may be used as the headline.
The Stage B trial's `9/68` off-target share is the reason this is a required
column, not an optional caveat.

---

## 10. Acceptance criteria and stop rules

### 10.1 Corpus acceptance (independent audit, not the engine)

A repo enters the frozen corpus only if all hold:

1. `spec.json` validates under `generate_synthetic.py spec-validate`.
2. Deterministic materialisation produces a parseable Python tree and
   `pyproject.toml`; re-materialisation has an empty diff.
3. Exactly three documents exist, are English, and are not changelog,
   release-notes, roadmap, or proposal documents.
4. The engine-free shape check passes: tool vocabulary, expanded contamination
   checks, file extensions, document count, spec surface.
5. The genre acceptance check passes: the independent auditor's blind genre
   assignment matches the planned genre, or a pre-registered backup genre is
   used with the substitution recorded.
6. The independent auditor reports `CONSISTENT` after factual fixes, with a
   complete fix log (including before/after claim form and context for touched
   lines) and no more than two audit rounds.
7. The engine was not used at any point in acceptance.

Two attempts per primary repo; then a pre-registered repo backup and/or backup
genre, with the substitution and reason recorded. A repo is never replaced
because of engine output.

### 10.2 Freeze

- `scope_engine_freeze.json` exists and `--verify` passes **before S1**, before
  the injector run, and before scoring.
- `corpus_freeze.json` exists and `--verify` passes before the injector run and
  before scoring.
- **Both freeze verifications pass again after scoring**, and the post-score
  record is in T1.
- The engine tree is clean at the recorded commit and its hash matches; the
  engine data/vocabulary, tool environment, oracle, materialiser, injector
  harness, freeze tools, prompts, model IDs, codebook, classifier, judge rubric,
  control config, and analysis scripts match their frozen hashes.
- A mismatch aborts; there is no override.

### 10.3 Injector

- One attempt per bundle.
- One retry only for an **infrastructure** failure (timeout, runner failure, no
  JSON due to the runner). A second failure is a generator failure.
- A substantive `injectable:false` decline, `unresolved`, or `conflict` is not
  retried.
- If the injector model is unavailable for more than 10% of bundles, stop and
  report; do not silently substitute a model family.
- Declines and failures stay in the end-to-end denominator.

### 10.4 Scoring

- The engine is invoked only at scoring time, once per baseline and once per
  injected snapshot, on the frozen inputs. No re-runs to obtain a better result.
  A crash may be re-run only with identical inputs, and the crash is logged.
- All 72 planned bundles are scored or assigned a `bundle_status`. No post-hoc
  exclusion of a class, repo, seed, or bundle.
- All T-tables are produced, even when empty or `n/a`.

### 10.5 Analysis and tuning prohibitions

- Only the pre-registered tables and estimands are headline-eligible.
- No Wilson interval; no single aggregate score as the headline; no
  `0-REFUTED` gate; no dropping controls; no changing the denominator after
  seeing results; no substituting specificity for precision or vice versa.
- After the freeze, **no** edits to the corpus, documents, specs, prompts, agent
  prompts, exemplar bank, engine, engine data, or analysis code. A change is a
  new version with a new freeze and a full re-run.
- Stage C is **not** used to tune prompts, specs, or tool code. Any limitation
  found is reported and fixed in a later development cycle (Stage D), on a
  different corpus.

### 10.6 Independent annotation

- At least one **non-author** annotator is required for a externally confirmed arm.
- Two independent annotators are required for the final result and IAA.
- One non-author annotator: provisional externally confirmed report, no IAA, final
  claim blocked.
- Zero non-author annotators: provisional engine-only report, no independent labels,
  final claim blocked. **OPEN-C9.**

### 10.7 Abort conditions

Abort and report (do not improvise):

1. **OPEN-C1** is unresolved at sign-off (no scope arm).
2. **OPEN-C11** is unresolved: `protocol.md` §5 still requires Wilson at
   sign-off.
3. `scope_engine_freeze.json` verification fails before S1, before injection, or
   before scoring.
4. An S0 artefact changed after `scope_engine_freeze.json` was written without a
   new version/deviation.
5. `corpus_freeze.json` verification fails.
6. The engine tree is dirty or its hash differs at scoring time.
7. The auditor is unavailable, or a repo cannot be made `CONSISTENT` after two
   rounds and no backup remains.
8. The injector is unavailable beyond the 10% threshold, or overall
   `verified < 48`.
9. Contamination is found after freeze (a shared shingle, a reused document, a
   tool-vocabulary leak).
10. A document or spec changes after freeze.
11. A control was selected from engine output or fabricated to fill a family.
12. The annotation sheet contains a tool verdict, layer, reason, or reaction.
13. **OPEN-C12** is unresolved and the run claims E1 (E6 missing).
14. A control false positive is found to be a corpus error rather than a tool
    error and the corpus is not re-versioned.

A missing non-author annotator is **not** an abort of the run; it blocks the
final independently validated claim and forces the provisional label (§7.6).

---

## 11. What Stage C does not establish

1. **Not an open-world benchmark.** It tests six predicates and four active
   injection classes. `VERSION`, value drift, and cross-document drift are not
   tested.
2. **Not a population estimate.** Six small synthetic repos in three domains are
   not a random sample of open-source projects. Two repos per domain cannot
   support a domain-level claim.
3. **Not organic-defect precision.** The defects are injected and mechanically
   verified; the real-world drift distribution is not measured.
4. **Not an independent reference** unless two independent annotators complete the sheet; with
   one, it is provisional and has no IAA.
5. **Not a measure of injector realism.** The injector is a construction tool.
6. **Not behaviour or semantics.** Signatures, runtime behaviour, security, and
   prose quality are out of scope.
7. **Not the ten catalog-in-scope classes with no predicate**, and not the
   capability classes beyond opportunistic controls.
8. **Not a paired comparison with Stage B.** Corpora, genres, engine, and scope
   differ; no delta is estimable. No "vs Stage B" column is reported.
9. **Not evidence that the section-qualification rule is generator-independent
   or generalises beyond these genres.** Using a different docwriter family (or a
   pre-registered 3/3 split) removes direct model-family sharing with Stage B,
   but model families share training corpora and documentation conventions, and
   the corpus is generated under this plan's own fixed genre taxonomy. Stage C
   cannot separate the rule from the generator's style, and it does not license
   a generalisation claim.
10. **Not a precision estimate beyond the controls.** Baseline findings and
    control false positives are reported, but the corpus is not a random sample
    of clean documentation.
11. **Not a stable symbol-class estimate.** Seed collapse within a repo may leave
    few distinct targets; the per-target table is a sensitivity analysis, not a
    class estimate.

---

## 12. Sequencing and rough timeline

| step | working time | output | gate |
|---|---|---|---|
| S0 scope, protocol, engine freeze | 1 d | `SCOPE.md` amendment (or C-base reaffirmation), `protocol.md` §5 amendment, engine commit, `taxonomy.json`, `corpus_design.json`, `annotation_codebook.md`, classifier, `control_config.json`, prompts, model IDs, `scope_engine_freeze.json` | **C1 and C11 resolved**; C2 composition fixed; C3 family/split fixed; C12 E6 status fixed; `freeze_scope_engine.py --verify` passes **before S1** |
| S1 specs | 1 d | six `spec.json`, validated and materialised | deterministic re-materialisation diff empty |
| S2 docs | 1 d | three documents per repo | three docs, correct genre, genre-only prompt, English |
| S3 audit and fixes | 1–2 d | `audit/audit.json`, `CONSISTENT` for 6/6 | independent auditor, ≤2 rounds, factual fixes only, before/after claim form/context |
| S4 corpus checks, controls, freeze | 0.5 d | `corpus_design.json`, applicable `controls.jsonl`, contamination report, `corpus_freeze.json` (including the S0 `taxonomy.json`) | `--verify` passes; controls engine-free; shortfalls recorded |
| S5 injections | 1 d | 72 proposals, `manifest.jsonl`, `provenance.json` | oracle verifies; one artifact per snapshot; `aux_edits` recorded |
| S6 scoring and judges | 1 d | claim dumps, `entries.json`, judge agreement | both freezes re-verified **before and after** scoring |
| S7 metrics and baseline adjudication | 0.5 d | T1–T13, `bootstrap.json`, `baseline_findings.json` | all planned bundles statused |
| S8 annotation sheets | 0.5 d | blind sheet with target-line and cross-mention rows, wrong-support sheet | sheets contain no verdict |
| S9 independent annotation | 1–2 calendar weeks | labels, κ (n = 2) or provisional (n = 1) | at least one non-author annotator |
| S10 final report | 1 d | `report.md`, `metrics.md`, deviation log | post-score freeze re-verify; T14–T15 present |

Rough total: **7–8 working days** of generation, injection, and scoring, plus
**1–2 calendar weeks** of annotation lead time. The timeline is not a result and
may slip without changing the estimands.

---

## 13. Open decisions

| id | decision | default if unresolved at sign-off | blocking? | effect |
|---|---|---|---|---|
| **C1** | Adopt `section-qualified name` into `SCOPE.md` §3.3.2 (C-ext), or run the policy-preserving C-base engine? | **blocks start**; no Stage C run begins until decided | **yes** | determines whether symbol-class rates are scope-limited or measured under the extension; determines A4/B controls and the `section_qualified` form |
| **C2** | Engine composition: E3 included; E4/E5 included only in C-ext? | E1+E2+E3+E6 in C-base; E1+E2+E3+E4+E5+E6 + §3.3.2 in C-ext | **yes at S0** (no freeze without a composition) | E3 converts false `SUPPORTED` to `NEI`; E4/E5 change `none` to `NEI`/`SUPPORTED` and enable C-ext |
| **C3** | Docwriter family: different from Stage B, or a pre-registered 3/3 split? | different family; fallback 3/3 split fixed at S0 | **yes if neither is available** | removes direct model-family sharing; a split confounds corpus with model and is reported |
| **C4** | Domain set: 3 domains × 2 repos (proposed) or 2 × 3? | 3 × 2 | no | affects domain spread versus within-domain depth |
| **C5** | Control families and denominators | conditional per §6.1; C-ext A1–A4+B, C-base A1–A3; C separate | no | sets the specificity and precision denominators |
| **C6** | Force seeds 1–3 onto the three documents, or allow free choice? | free choice, report distribution | no | forcing raises genre coverage but biases toward documents with more mentions |
| **C7** | Run a separate `doc_side` path-injection exploratory arm? | **no**; `doc_side` is `n/a` | no | adds a claim-edit mechanism; never pooled with the 72 |
| **C8** | Add opportunistic capability controls (`LICENSE`, `HAS_DOCKERFILE`, `HAS_CI_WORKFLOW`) where a naturally true claim exists? | yes, separate arm only | no | adds precision evidence outside the four active classes |
| **C9** | Can at least one non-author annotator be recruited? Two? | one = provisional/no IAA; zero = engine-only provisional; final blocked | **yes for a final external claim** | determines whether Stage C can claim external validation |
| **C10** | If C1 is rejected, does Stage C proceed on C-base? | yes, with symbol classes reported as policy-limited | no | avoids an engine change after seeing corpus results |
| **C11** | Amend `protocol.md` §5 to replace Wilson with the repo-cluster bootstrap? | **blocks sign-off**; the protocol is amended before the freeze or Stage C does not start | **yes** | keeps the normative protocol and the plan consistent |
| **C12** | Is E6 implemented, unit-tested, and frozen? | if **no**, E1 is excluded and the composition is recorded; if E1 is claimed, S0 blocks | **yes for an E1 claim** | E1 without E6 amplifies migration/compatibility false positives |

---

## 14. Deviations log

Every deviation from this plan is recorded here before the affected result is
reported, with: date, section, what changed, why, whether it happened before or
after the scope/engine freeze and the corpus freeze, before or after scoring, and
the expected effect on the estimand.

| date | section | deviation | reason | stage (pre/post freeze, pre/post scoring) | effect |
|---|---|---|---|---|---|
| | | | | | |

---

## Appendix A — design summary

- **Corpus:** 6 new repos, 3 new domains (geospatial, language/text,
  instrument/hardware), 3 documents each, one frozen six-genre taxonomy
  (`tutorial`, `how-to`, `reference`, `explanation`, `cookbook`, `module map`).
- **Sample:** 4 active classes × 6 repos × 3 seeds = **72 planned primary
  bundles**; `code_side` only; one artifact per snapshot; `doc_side` separate
  and off by default.
- **Controls:** conditional on C1. C-ext: 24 consistent-present (A1–A4) + 6
  non-module traps (B) + up to 6 optional consistent-absent (C). C-base: 18
  consistent-present (A1–A3) + optional C; A4/B n/a. Selected engine-free;
  evaluated on clean baselines; shortfalls and drops recorded.
- **Injection:** natural contract reused verbatim; no extractor preconditions;
  no `kind`/`artifact_class`; declines allowed; one artifact per snapshot with
  recorded `aux_edits`; no `VERSION`, value, or cross-document drift.
- **Freeze:** two files. `scope_engine_freeze.json` at S0 covers `SCOPE.md`,
  the amended `protocol.md`, engine code/data/vocabulary, tool environment,
  prompts, model IDs, oracle, materialiser, injector harness, freeze tools,
  codebook, classifier, judge rubric, control config, and analysis code.
  `corpus_freeze.json` at S4 covers the corpus, taxonomy, audit, controls, and
  checks. Both verify before S1/injection/scoring and **again after scoring**.
- **Annotation:** at least one non-author annotator required; two for IAA and the
  final claim; blind sheet with target-line and cross-mention rows; frozen
  codebook and engine-free classifier; κ target ≥ 0.60, reported whatever it is.
- **Scoring:** artifact-level `refuted`/`nei`/`none`, with `none` sub-flags;
  credited and target-line rates co-primary with a fixed per-class primary;
  end-to-end statuses including declines, unresolved, conflict, timeout, and
  no-output; controls reported as specificity over all evaluated controls and
  precision over extracted controls, separately; repo-cluster bootstrap (no
  Wilson); credited versus target-line split.
- **Headline:** no single number; no delta against Stage B's `35/72`, the
  post-hoc `68/72`, `72/72`, `63/72`, or the trial's per-class `18/18` and
  claim-form `32/32` rows.

### Appendix A2 — descriptive style audit (not a result)

After freeze, report for Stage C (and, descriptively, Stage B):

| field | Stage B (descriptive mapping) | Stage C |
|---|---|---|
| documents / repos / words | recorded | recorded |
| heading depth distribution | recorded | recorded |
| tables per document | recorded | recorded |
| list items per document | recorded | recorded |
| inline-backtick density | recorded | recorded |
| `context_source` shares | mapped descriptively, not scored | measured |
| `target_document` shares | mapped descriptively, not scored | measured |

The audit is used only to describe the corpus and to check that genre-only
guidance did not silently become presentation guidance. It is never a baseline
comparison, never a like-for-like taxonomy comparison, and never a headline.

---

## Appendix B — control-selection config (pre-registered)

`control_config.json` contains both C-ext and C-base pattern sets, a fixed seed
(`20261020`), and the drop rules. It is hashed at S0. The selector never imports
`docassay`.

**Selection order.** Documents in the order `README.md`, `task_document`,
`reference_document` (by filename); candidates are shuffled with
`random.Random(seed + zlib.crc32((repo + family).encode()))`; take the first candidate that
passes the truth check and the current-state check. Record the candidate index,
the line, the referent, and every rejected candidate with its reason.

**Patterns.**

| family | candidate pattern (engine-free) | truth check |
|---|---|---|
| A1 path | inline-code path or Markdown link target, not negated, not in a fence | token resolves to a tracked path in the baseline |
| A2 dependency | line names a declared dependency, with or without a version constraint, not historical/conditional | the dependency is declared, and any claimed constraint is satisfied |
| A3 qualified symbol | inline-code dotted name with a project-owned top, not negated, not in a fence | the qualified name resolves in the AST inventory |
| A4 section-qualified symbol | inline-code bare member under a `heading`/`table`/`prose`/`list`/`path_prose` module context per §9.1, exactly one candidate token | the qualified name resolves in the AST inventory |
| B non-module trap | inline-code bare symbol under a heading/column/prose context that is not a project module (e.g. `Parsing`, `helpers`, `utilities`), exactly one candidate token | the symbol exists somewhere in the project; the context does **not** resolve to a project module |
| C consistent-absent | current-state absence statement (`no`, `not`, `does not ship/include/depend`, `without`) about an artifact | the artifact is truly absent; `NEI` expected |

**Drop reasons:** `no_candidate`, `truth_check_failed`, `not_current`,
`undetermined`, `context_absent`, `context_is_module` (B), `ambiguous`,
`audit_changed_line`. A dropped control is reported, never replaced by a
fabricated one. A family with zero evaluated controls is `n/a`; a family with
fewer than the required count is a **shortfall**, reported with reasons.

**C-ext vs C-base applicability.** The C-ext set is evaluated only if C1 =
C-ext. The C-base set is evaluated only if C1 = C-base. The non-applicable set
is recorded as `not_applicable_scope`, not as zero.

---

## Sign-off

| role | name | date | confirms |
|---|---|---|---|
| author | | | plan complete |
| scope owner | | | C1 decided; `SCOPE.md` amended (C-ext) or reaffirmed (C-base) |
| protocol owner | | | C11 resolved; `protocol.md` §5 amended to the repo-cluster bootstrap before sign-off |
| engine owner | | | engine commit frozen; E1/E2/E3/E6 (and E4/E5 in C-ext) included as per C2/C12; E6 gate present if E1 is claimed |
| corpus owner | | | genre-only docwriter prompt; no presentation guidance; blindness attestation |
| annotation owner | | | at least one non-author annotator, or provisional status accepted; two for the final claim |

---

## Amendment A1 — headline estimand (2026-10-21, post-score, disclosed)

**Status:** recorded after the Stage C corpus was frozen, the snapshots were
scored, and the raw outcomes (`refuted 50 / nei 15 / none 4`) were fixed. It
changes **no** raw count, outcome, entry, or snapshot. It changes only which
derived rate is the headline.

**What changed.** §8.3 of this plan, and `protocol.md` §5 as first written,
treated credited detection (`R_credit`) and target-line attribution (`R_target`)
as co-primary. `protocol.md` §5.1 (amendment A1) now defines the headline
estimand as **detection of the drift**, `R_detect = REFUTED or NEI` on the
injected artifact, with `R_credit`, `NEI`, `none` and `R_target` reported as the
decomposition and the attribution diagnostic.

**Why.** The tool's declared goal is catching documentation drift, not
maximising closed-world refutations. A same-artifact `NEI` is an explicit,
inspectable reaction that names the artifact and its reason; it is not silence
and not a wrong `SUPPORTED`. Counting it as a miss understated what the tool
actually did. The operator made this decision on 2026-10-21 after seeing the
outcome split, and it is disclosed as a **post-score estimand change** in
`deviations.md` (entry of 2026-10-21) and in `report.md` T15.

**What did not change.** The four-class denominator (69 verified of 72 planned),
every per-class outcome, the controls (24 evaluated, 0 refuted), the baseline
(0 `REFUTED`), the judges, and the LLM annotation arm. No number in T3–T14 moved.

**Conservative sensitivity.** Because `NEI` enters `R_detect`, the report also
carries `R_detect` restricted to abstentions judged legitimate (8/15), i.e.
`58/69 = 0.841` next to `65/69 = 0.942`. Both are reported; neither is hidden.
The attribution number `R_target = 39/69 = 0.565` is reported as a diagnostic and
is not a miss count.
