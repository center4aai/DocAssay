# Claim scope of the documentation-assertion verifier

> **Status: normative, active (2026-10-13).** This document is the contract that
> `protocol.md` requires before any scoring run. It states, for every drift type,
> whether the tool commits to detecting it. It is **declared before scoring** and
> is **never derived from what the engine happened to do** (`protocol.md:35-37`).

## 1. Status and purpose

The tool (`src/docassay/`) is a deterministic, symbolic verifier. It extracts
claims from natural-language documentation, adjudicates each claim against a
code-derived fact inventory, and emits `SUPPORTED / REFUTED / NEI` per assertion
(`protocol.md:20-24`; `core/pipeline.py:427-566`). It is **not** an open-world
benchmark: it is a conformance test against the contract declared here.

This document pairs with `../validation/protocol.md`:

- `protocol.md` defines **how** detection is measured (injection, verification,
  finding diff) and fixes the three reporting buckets (`protocol.md:26-41`);
- `SCOPE.md` (this file) fixes **what** the tool commits to detecting, so the
  recall denominator is declared, not inferred.

Every claim below is traceable to code with `file:line`. Where the code does not
settle a question, the entry says **not determined by code** rather than guessing.

### 1.1 The three buckets (kept separate everywhere)

| bucket | definition | role |
|---|---|---|
| **IN SCOPE** | drift type backed by an implemented predicate in `ALL_PREDICATES` | the recall denominator |
| **CATALOG IN-SCOPE, NOT IMPLEMENTED** | drift type the **evaluation taxonomy** marks scope `in` (`normalization.json`) but with **no** predicate | reported as a gap; never in the denominator |
| **OUT OF SCOPE** | drift type neither predicate-backed nor in the taxonomy's scope-`in` list | the expressiveness boundary |

An **implemented predicate** means one of the six `Predicate` instances in
`predicates/__init__.py:20-27` (`ALL_PREDICATES`). Detection happens at the
predicate layer.

**What the tool itself declares.** The tool's own surface (`README.md:13-39`,
"What works today") lists exactly the six predicates above and does **not**
claim the catalog's other in-scope classes. `README.md:41-42` names further
predicate groups (config, CLI, infra, license/OS) as "being added" — a
roadmap, not a current commitment. The middle bucket therefore reflects the
**evaluation taxonomy's** scope-`in` list (`normalization.json:7-20`), which is
the benchmark's error taxonomy, **not** a claim made by the tool. This is the
distinction that matters: the tool is not penalised for a drift type it never
committed to, and the gap is reported rather than scored.

The distinction between a **non-claim** (gate drop) and an `NEI` is normative
(`predicates/base.py:73-85`): a `GateResult(ok=False)` mention "never enters the
verdict layer", forms no referent/assertion, and is recorded only in
`AnalysisResult.gated_claims` (`core/pipeline.py:500-516`). An `NEI` is a real
verdict on a formed claim.

### 1.2 NEI taxonomy

`NEI` is a **first-class outcome**, not a dump for classes the tool does not
implement. It is emitted only after a claim has been formed, and it always
carries a **layer** (where adjudication stopped) and a verbatim **reason**
(`predicates/base.py:28-50`):

| layer | what stopped adjudication | representative reasons |
|---|---|---|
| `CLAIM_GATE` | the mention is not a current-state claim about this project's artifact (genre / subject / construction / form), or the claim does not fix a referent | `"unresolved bare name"`, `"historical mention"`, `"instruction"`, `"example"`, `"dynamic surface"` |
| `WORLD` | the claim is formed, but the closed world for that fact is not complete — absence is ignorance, not contradiction | `"foreign top segment"`, `"top not in project packages"`, `"negation with no evidence"`, `"inventory incomplete"` |
| `DECIDABILITY` | the claim is genuine and current-state, but the evidence cannot decide it | `"version range undecidable"`, `"declared but no version spec"`, `"negated non-single-pin version"` |

**`NEI` is not `none`.** `NEI` means a claim was formed and the tool
**abstained** from adjudicating it: the claim exists, is attributable to a
referent and a document line, and is reported with its layer and reason.
`none` is the reporting-side outcome for a mention that never became a claim — a
`GateResult(ok=False)` drop, or no anchor at all. Such a mention never enters
the verdict layer and is recorded only in `AnalysisResult.gated_claims`
(`predicates/base.py:73-85`, `core/pipeline.py:500-516`). A `none` is an
extraction question; an `NEI` is not.

---

## 2. Predicate inventory

Six predicates are registered (`predicates/__init__.py:20-27`). The `world` and
each `Predicate(...)` definition are cited. "Unit" is the referent key the
predicate groups claims and evidence by (the benchmark's `unit` field in
`normalization.json` is a **different axis** — repo/method/behavior — and is not
the predicate unit). The `Predicate` dataclass (`predicates/base.py:88-106`) has
no `unit` field: the exact name of the predicate "unit" is **not determined by
code**, so each row's unit is read off that predicate's evidence `object` property
(e.g. `evidence/manifests.py:73-76`, `evidence/listing.py:35-38`,
`evidence/symbols.py:81-84`, `evidence/project.py:97-100`,
`evidence/infra.py:38-41`).

| predicate | `world` | unit (referent) | artifact type adjudicated | `Predicate(...)` definition |
|---|---|---|---|---|
| `DEPENDENCY` | `closed-over-manifest` | normalized package name | declared dependency + version constraint | `predicates/dependency.py:570-581` |
| `PATH_EXISTS` | `closed-over-listing` | normalized path (dir key keeps `/`) | file / directory path in the tracked listing | `predicates/listing.py:435-443` |
| `SYMBOL_EXISTS` | `closed-over-project` | qualified, case-folded symbol name | Python module/class/function/method/field/reexport | `predicates/structure.py:513-522` |
| `LICENSE` | `closed-over-field-and-file` | canonical license name | license manifest field + `LICENSE`-file detection | `predicates/crossdoc.py:177-186` |
| `HAS_DOCKERFILE` | `closed-over-listing` | constant `"dockerfile"` | `Dockerfile*` paths | `predicates/infra.py:289-297` |
| `HAS_CI_WORKFLOW` | `closed-over-listing` | constant `"ci_workflow"` | CI config files/dirs | `predicates/infra.py:299-307` |

World constants: `predicates/dependency.py:47`, `predicates/listing.py:64`,
`predicates/structure.py:57`, `predicates/crossdoc.py:31`, `predicates/infra.py:27`.

Two orthogonal flags shape each world (`predicates/base.py:10-16,100-106`):

- `domain_scoped_evidence` — evidence is per manifest-bearing directory
  (monorepo). Set for `DEPENDENCY` (`dependency.py:578`); the whole-tree worlds
  (`PATH_EXISTS`, `SYMBOL_EXISTS`, `LICENSE`, the two infra predicates) leave it
  `False` and match the merged inventory (`core/pipeline.py:579-592`).
- `world_holds` — when false, every assertion of that predicate abstains with
  `NEI/WORLD "inventory incomplete"` (`core/pipeline.py:613-622`). Overridden for
  `SYMBOL_EXISTS` → `has_project_python` (`structure.py:521`), `LICENSE` →
  `has_license_inventory` (`crossdoc.py:200`); the default is `True`
  (`base.py:100`).

Anchor-first is the extraction rule for **all** predicates: the vocabulary is the
only selector and no trigger word gates extraction (`predicates/dependency.py:1-7`).

---

## 3. Per-predicate scope entry

### 3.1 `DEPENDENCY` — external dependency / version drift

**Anchor.** A controlled allowlist: the fixed `data/dependency.json:names` set
(2 959 surface forms, `vocabularies/dependency.py:33`) plus, at runtime, every
dependency the tool itself harvests from the project's manifests
(`extend_with_declared=True`, `anchor_evidence` excludes lock files;
`dependency.py:578-580`, `core/pipeline.py:487-497`). Matching is a maximal
`[A-Za-z0-9_-]+` run equal (case-insensitively) to an anchored name
(`vocabularies/dependency.py:95-122`). Name normalization folds `_`/`.` to `-`
and applies `synonyms` (`dependency.py:156-164`). URL spans are removed before
anchoring (`dependency.py:71-79`).

**World / why decidable.** `closed-over-manifest` (`dependency.py:9-21,47`). The
manifests (`pyproject.toml`, `setup.cfg`, `setup.py`, `requirements*.txt`) are
complete by construction for what they declare (`evidence/manifests.py:79-103`);
the world closes over the project's **declared** dependencies only. Lock files
(`uv.lock`, `poetry.lock`) never close presence and never extend the anchor set;
they only refine a version (`evidence/manifests.py:31-40,522-557`). Manifests in
non-authoritative directories (deeper than two levels, or under
`manifest_non_code_dirs`) are ignored (`evidence/manifests.py:168-180`).

**Verdict rules** (`dependency.py:440-532`):
- `SUPPORTED` — declared dependency with no version claim (`:504-505`); or a
  version claim whose manifest constraint is not contradicted (`:526-527`,
  `markers/version.py:261-312`); or a negated single-pin version lying outside
  the manifest's allowed set (`:567`).
- `REFUTED` — a version claim the manifest constraint excludes (`:532`); a
  negated single-pin version lying inside the allowed set (`:564`).
- `NEI` — enumerated reasons (verbatim) and layers:
  - `WORLD "negation with no evidence"` (`:479`);
  - `CLAIM_GATE "hypothetical negation"` (`:481`);
  - `CLAIM_GATE "optionality phrasing"` (`:483`, only when all declared evidence
    is optional);
  - `CLAIM_GATE "negated versionless mention"` (`:493`);
  - `CLAIM_GATE "negated non-requirement mention"` (`:495`);
  - `WORLD "undeclared (open by transitivity)"` (`:502`);
  - `DECIDABILITY "declared but no version spec"` (`:509`);
  - `DECIDABILITY "version range undecidable"` (`:529`);
  - `CLAIM_GATE "non-requirement mention"` (`:531`);
  - `DECIDABILITY "negated non-single-pin version"` (`:548`);
  - `DECIDABILITY "negated version, no spec"` (`:551`);
  - `DECIDABILITY "negated version undecidable"` (`:566`).
- Window-level downgrades that make a version mention *not a requirement* (fed as
  flags, not gates): `locator`, `conditional`, `perf`, `python_context`
  (`dependency.py` → `claim_flags`, `:367-378`).

**Non-claims (gate drops) rather than NEI** (`dependency.py:381-407`, verbatim
reasons): `"historical mention"`, `"test-env mention"`, `"hypothetical negation"`,
`"optionality phrasing"`, `"key = value fragment"`, `"quoted requirement string"`,
`"install instruction"`. Locator/conditional stay in the verdict layer (they can
carry legitimate feature-gate requirements).

### 3.2 `PATH_EXISTS` — stale file/directory path

**Anchor.** Backtick-quoted path-shaped tokens, trailing-slash directory tokens,
`the \`X\` directory` noun phrases, **Markdown link/image targets**
(`[label](docs/guide.md)`), and unresolved bare `name.ext` filenames
(`listing.py:66-78,109-140,166-249`). The anchor is syntactic, not a closed
allowlist (`vocabularies/structure.py:1-8`).

**Not anchored (forms no claim).** A bare **directory-qualified** path in prose
(`docs/guide.md`, no backticks) and a Markdown link whose first segment is a
hostname (`example.com/page.html`) are not anchored at extraction or abstain at
the verdict gate (`top-level directory absent from repository`). A bare
`name.ext` without a directory *is* anchored but refutes only under a reference
frame — otherwise it abstains (`unreferenced bare filename`).

**World / why decidable.** `closed-over-listing` (`listing.py:11-19,64`): the
tracked file+directory inventory is complete by construction
(`evidence/listing.py:46-106`; git snapshot via `git ls-files`,
`evidence/git.py:24-63`), so a claim about an absent path is refutable.

**Verdict rules** (`listing.py:307-428`):
- `SUPPORTED` — claim resolves to an inventory key (`:362-365`, with a
  `case differs: …` hint from `base.py:127-154`); or, for a bare name, a basename
  match (`:366-370`).
- `REFUTED` — negative claim with evidence (`:361`); positive claim with no
  evidence after all gates (`:428`).
- `NEI` — verbatim reasons:
  - `WORLD "negation with no evidence"` (`:360`);
  - `CLAIM_GATE` gate reason via `mention_gate_reason` (`:371-381`):
    `"historical mention"`, `"instruction"`, `"example"`, `"user runtime config"`,
    `"reader's own file"`, `"generated file"` (`base.py:111-119`);
  - `CLAIM_GATE "extensionless slash anchor"` (`:382-383`);
  - `CLAIM_GATE "placeholder path"` (`:384-385`);
  - `CLAIM_GATE "external software artifact"` (`:386-387`);
  - `CLAIM_GATE "generated artifact"` (`:388-389`);
  - `CLAIM_GATE "filename fragment pattern"` (`:390-391`);
  - `CLAIM_GATE "hidden/tool entry"` (`:392-396`);
  - `CLAIM_GATE "reader-space :file: example file"` (`:397-403`);
  - `CLAIM_GATE "top-level directory absent from repository"` (`:405-416`);
  - `CLAIM_GATE "extensionless bare name"` (`:417-421`);
  - `CLAIM_GATE "unreferenced bare filename"` (`:422-427`).

**Non-claims (gate drops)** (`listing.py:275-298`): `"historical mention"`,
`"instructional mention"`, `"exemplary mention"`, `"user/runtime-config mention"`,
`"placeholder path"`, `"extensionless slash anchor"`.

### 3.3 `SYMBOL_EXISTS` — stale code symbol (and removed referent)

**Anchor.** Code-shaped backtick tokens: dotted names, calls (`name()`,
`obj.method()`), and noun-gated mentions (`the \`parse\` function`, `the \`limit\`
field`) (`structure.py:61-74,225-249`). Call syntax and nouns are anchor forms;
the referent is a symbol, not a symbol kind (`structure.py:3-8`). `_is_usable_symbol`
filters path tokens, Sphinx roles, extensions, config/chart windows and
placeholder segments (`structure.py:140-168`).

**World / why decidable.** `closed-over-project` (`structure.py:10-17,57`): the
Python AST inventory is complete for the project's own tree
(`evidence/symbols.py:1-9,87-92`), guarded by `has_project_python`
(`evidence/symbols.py:95-102`). Only a **qualified** (dotted) claim refutes; bare
single-segment mentions abstain (`structure.py:10-17`).

**Verdict rules** (`structure.py:306-414`):
- `SUPPORTED` — resolved dotted claim (`:375-385`, with case hint); a bare name
  with last-segment candidates (`:387-393`).
- `REFUTED` — negative claim with evidence (`:371-374`); a capitalized last
  segment resolving only to a lowercase module (`:376-383`, `did you mean` hint);
  an unresolved dotted claim under a project-owned top (`:414`).
- `NEI` — verbatim reasons:
  - `CLAIM_GATE "non-symbol mention"` (RST anchor / plugin entry point, `:353-356`);
  - `WORLD "foreign top segment"` (`:358-369`);
  - `WORLD "negation with no evidence"` (`:371-373`);
  - `CLAIM_GATE "unresolved bare name"` (`:387-394`, §3.3.1);
  - `WORLD "top not in project packages"` (`:396-399`);
  - `CLAIM_GATE` gate reason via `mention_gate_reason` (`:400-404`):
    `"historical mention"`, `"instruction"`, `"example"`;
  - `CLAIM_GATE "cython/generated surface"` (`:405-406`);
  - `CLAIM_GATE "dynamic surface"` (`:407-408`);
  - `CLAIM_GATE "last segment is a domain name ending (.{last})"` (`:409-413`).

**Non-claims (gate drops)** (`structure.py:269-292`): `"historical mention"`,
`"instructional mention"`, `"exemplary mention"`.

**Removed referent.** A *removed* top-level symbol the docs still reference by a
qualified name is an unresolved dotted claim under a project-owned top →
`REFUTED` (`structure.py:414`). This is the mechanism behind
`removed-referent-drift` (see §5 and the discrepancy note). Detection requires a
**qualified** reference; a bare mention abstains (`:394`, §3.3.1).

### 3.3.1 Bare-name policy

`SYMBOL_EXISTS` refutes **only** a qualified name whose top segment is a
project-owned package and whose symbol is absent from the AST inventory
(`structure.py:358-369,396-414`). Qualification is what ties the claim to this
project: a dotted name starting with a project package is a claim about the
project's own tree, and the AST inventory is complete for that tree.

A **bare** single-segment name is never refuted, in any anchor form — call
(`serve()`), noun-gated (``the `parse` function``, ``the `limit` field``), or
plain (`parse`). If it resolves to a last-segment candidate it is `SUPPORTED`
(`structure.py:387-393`); if it does not, it is `NEI` with layer `CLAIM_GATE` and
reason `"unresolved bare name"` (`structure.py:387-394`). A bare name may denote
a parameter, a builtin, an external symbol, an attribute, or an ordinary word;
it does not by itself establish that the claim is about this project, so absence
from the project AST inventory is not evidence that the claim is false. The
abstention is **deliberate**: the claim is formed and the tool declines to
adjudicate it. It is not a failed refutation and must not be scored as a miss.

| claim form | example | outcome | recorded reason |
|---|---|---|---|
| qualified, project-owned top, absent from AST | `mypkg.parse` | `REFUTED` | — |
| qualified, project-owned top, present | `mypkg.parse_document` | `SUPPORTED` | — |
| qualified, foreign top | `numpy.array` | `NEI` | `WORLD "foreign top segment"` |
| bare call, unresolved | `serve()` | `NEI` | `CLAIM_GATE "unresolved bare name"` |
| bare noun-gated, unresolved | ``the `parse` function`` | `NEI` | `CLAIM_GATE "unresolved bare name"` |
| bare word, unresolved | `parse` | `NEI` | `CLAIM_GATE "unresolved bare name"` |
| bare word, last-segment candidate present | `parse` | `SUPPORTED` | — |
| no code-shaped anchor | ordinary prose | `none` (no claim formed) | gate drop / no anchor |

### 3.3.2 Section-qualified name

A **section-qualified name** is a bare member token that the document itself
ties to a project-owned module. It is a claim form in its own right; it is not a
bare name and it is not a general licence to qualify names.

A bare token `T` on line `L` is section-qualified to module `M` if and only if
all of the following hold.

1. **Project-owned qualifier.** `M` is a Python module in the project's own
   tree, and its top segment is a top-level package/module of the project (as
   declared by the project's packages), not an external dependency, stdlib
   module, domain word, or file that does not map to a module. If `M` is not
   in the project's module inventory, no qualification occurs.
2. **Document-supplied context.** `M` is supplied by one of:
   - `heading`: a heading names `M` as a module, and the token is in that
     heading's section;
   - `table`: a cell in the same table row names `M` in a module position (a
     header labelled module/package/namespace, or a cell that resolves to `M`
     and is not the symbol cell), and another cell contains `T` as a member
     token;
   - `prose`: the same sentence or clause names `M` as a module (`the M module`,
     `M module`, `in M`, `from M`, `M provides/declares/exposes/contains/
     defines`), and `T` is the only code-shaped bare member token;
   - `list`: a list item under a `heading` context naming `M`, or a list item
     whose lead-in names `M` as a module;
   - `path_prose`: a path token resolves to exactly one project-owned `.py`
     module `M`, the path is explicitly presented as a module/source file
     (`the M module`, `in M`, `M provides`), and `T` is the only code-shaped
     bare member token on the line. A path to a data file, asset, template,
     directory, or non-`.py` file is not a module qualifier.
3. **Heading reset.** A heading that names a project module sets context `M` at
   its level. A code-shaped member/signature subheading of a module heading
   inherits `M` and does not change it (it is the target line, not a new
   module). A heading that is neither a module nor a code-shaped member (for
   example `Notes`, `Installation`, `Parsing`) clears `M`. A heading of the
   same or higher level than the module heading clears `M` unless it itself
   names a module. A fenced code block is not a context and does not inherit or
   set `M`.
4. **One-token guard.** Exactly one code-shaped bare member token `T` is on the
   line. If two or more candidate bare tokens are present, no token is
   qualified (`context_ambiguous`). A path, a call with a receiver other than
   `M`, a dotted name, a builtin, a keyword, a placeholder, a dunder, an
   environment variable, or a CLI flag is not a member token.
5. **Gap guard.** In `prose`, `path_prose`, or `list`, if a usage verb from
   {`uses`, `calls`, `invokes`, `wraps`, `delegates to`, `is used by`,
   `depends on`} stands between the `M` reference and `T`, the token is not
   qualified: the sentence asserts a use relation, not membership. If `M` is
   explicitly a module reference (`the M module`) and the verb is from
   {`provides`, `declares`, `exposes`, `contains`, `defines`, `documents`,
   `includes`}, qualification is allowed.
6. **Precedence.** If more than one context applies on one line: same-line
   explicit module reference (`prose`/`path_prose`) > table row > innermost
   module heading. If the winning context gives `M1` and another applicable
   context gives a different project module `M2`, no qualification occurs
   (`context_conflict`). If both give the same `M`, qualification proceeds.
7. **Resolution.** The claim is `M.T`, with `claim_form =
   section_qualified`, `context_source` as recorded, `context_module = M`, and
   `context_line` = the line that supplied `M`. It is `REFUTED` only if `M` is
   project-owned and `M.T` is absent from the project AST inventory. It is
   `SUPPORTED` if `M.T` exists. If `M` is not in the project inventory, no
   claim is formed (or the existing `NEI "top not in project packages"`). A
   bare token with no context remains bare and is never `REFUTED`.
8. **No chaining.** A section-qualified name is not used to qualify a second
   token on the line, and it does not cross into another document.
9. **Recorded context.** Every claim records `claim_form` (`qualified` or
   `section_qualified`), `context_source`, `context_module`, and
   `context_line`. A `section_qualified` claim with `context_module = null` is
   a defect and is reported.

A bare call (`T()`) under a module context is section-qualified to `M.T`; when
qualification occurs, `claim_form` is `section_qualified`, not `bare_call`. A
call with an explicit receiver other than `M` is not qualified.

A document may write a dotted name directly. That is `qualified`, not
`section_qualified`, even if a heading also names the module.

### 3.4 `LICENSE` — declared-license mismatch

**Anchor.** A closed allowlist of license names (`data/project.json:license_names`,
`crossdoc.py:54-61`) **inside a license-context window** (`licensed under`, `the …
license`; `license_context_words`, `crossdoc.py:44-52,63-121`). A bare `apache`
mention without a version is skipped (project names, `crossdoc.py:9-11,95`).

**World / why decidable.** `closed-over-field-and-file` (`crossdoc.py:30-31`): the
manifest `license` field plus `LICENSE`-file detection (`evidence/project.py:289-411`);
canonicalization folds clauses and versions (`evidence/project.py:102-152`). World
guard `has_license_inventory` (`crossdoc.py:200`, `evidence/project.py:484-488`).

**Verdict rules** (`crossdoc.py:151-186`):
- `SUPPORTED` — canonical license present (family match supported,
  `:139-148,178-179`);
- `REFUTED` — negative claim with evidence (`:174-176`); a different license is
  declared (`:184-185`);
- `NEI` — verbatim reasons:
  - `WORLD "negation with no evidence"` (`:177`);
  - `CLAIM_GATE "third-party attribution"` (`:180-181`);
  - `CLAIM_GATE "historical mention"` (`:182-183`);
  - `WORLD "no license inventory"` (`:186`).

**Non-claims (gate drops)** (`crossdoc.py:132-135`): `"historical mention"`.

### 3.5 `HAS_DOCKERFILE` — claimed Dockerfile

**Anchor.** The `Dockerfile` name, but **only** in an assertive sense — an
existence/possession verb or a repo location (`_DOCKERFILE_ASSERT_RE`,
`infra.py:37-43,121-149`). A how-to mention of the *user's* Dockerfile never
anchors.

**World / why decidable.** `closed-over-listing` (`infra.py:27`): the listing is
complete, so absence of a `Dockerfile*` path refutes (`evidence/infra.py:49-92`).

**Verdict rules** (`infra.py:224-264`): `SUPPORTED` evidence (`:242-243`);
`REFUTED` negative+evidence (`:238-240`) or positive with no evidence and no
downgrade (`:246`); `NEI` reasons `WORLD "negation with no evidence"` (`:241`)
and `CLAIM_GATE` gate reason (`:244-245`): `"historical mention"`,
`"instruction"`, `"example"`.

**Non-claims (gate drops)** (`infra.py:203-215`): `"historical mention"`,
`"instructional mention"`, `"exemplary mention"`.

### 3.6 `HAS_CI_WORKFLOW` — claimed CI workflow

**Anchor.** CI product names plus bare `ci`/`ci/cd`/`continuous integration`
(`data/project.json:ci_names`, `infra.py:45-62`). Multi-word product names anchor
on their own; bare `ci` and single-word tools need a CI context word
(`infra.py:51-62,152-183`).

**World / why decidable.** `closed-over-listing` (`infra.py:27`); CI config files
and directories form a closed allowlist (`data/project.json:ci_config_files`,
`ci_config_dirs`; `evidence/infra.py:87-92`).

**Verdict rules** (`infra.py:267-282`, delegate to `_presence_match`): identical
to §3.5 with referent `"ci_workflow"`. `NEI` reasons:
`WORLD "negation with no evidence"` (`:241`) and `CLAIM_GATE` gate reason
(`:244-245`): `"historical mention"`, `"instruction"`, `"example"`. Gate drops:
`"historical mention"`, `"instructional mention"`, `"exemplary mention"`
(`infra.py:203-215`).

---

## 4. Corpus / document scope conditions

Only a document that passes **all** of the following can contribute claims.

**File type.** Scanned extensions are `.md` and `.rst` only
(`data/pipeline.json:2-5`, `core/pipeline.py:29,375,400`).

**File set.** In a git checkout the document set is the tracked snapshot
(`git ls-files`), **without** the `SKIPPED_DIRS` filter, so tracked `doc/build/`
and `sites/` are scanned (`core/pipeline.py:346-391`, `evidence/git.py:1-14,24-52`).
Git-less trees fall back to a working-tree walk with `SKIPPED_DIRS` and dot-dirs
pruned (`core/pipeline.py:392-416`).

**Excluded documents.**
- Change-history stems and path markers (`changelog`, `changes`, `history`,
  `release-notes`, `upgrading`, `java-sdk/`, `/adr/`, …; `data/pipeline.json:6-20`,
  `core/pipeline.py:120-171`).
- Release-notes genre detected from a **top-level** heading (`# Release Notes`,
  `What's New`, `Changelog`, `News`); a section-level `## News` does not exclude a
  README (`core/pipeline.py:216-239,388-390`).
- Non-English documents (`core/pipeline.py:385-387`) — see below.
- Proposal/plan/announcement documents are still **extracted**, but a `REFUTED`
  grounded only in them is downgraded to `NEI` (`core/pipeline.py:174-213,522-528,
  637-668`, reason `"refutation grounded only in plan/proposal documents"`).

**English-only filter** (`is_english_document`, `core/pipeline.py:88-117`). The
body is the first 20 000 chars after stripping HTML comments, code fences, inline
code and URLs (`_strip_code_and_comments`, `:78-85`). Two layers:
1. non-Latin script ratio: `non_latin / letters > 0.02` → not English (`:104-107`);
2. lowercase diacritic ratio: `lower_diacritics / lower_letters > 0.008`
   (`_DIACRITIC_RATIO`, `:73-75,108-116`); capitalized words are ignored so
   accented proper nouns do not trip the gate.

An English check with no letters returns `True` (`:102-103`).

**Fenced code and tables** (`core/windows.py:137-243`). A line beginning
` ``` ` or `~~~` is dropped as a window boundary (`:156`). For most predicates
inline backticks are stripped (`:174-176`); `PATH_EXISTS` and `SYMBOL_EXISTS`
use `iter_windows_preserve_code`, which keeps backticks (`:228-235`). A Markdown
table emits one `"<header> <cell>"` window per data row only when the block has a
header + separator row; lone table rows are dropped (`:115-134,162-171`).

**Per-domain inventory (monorepos).** `DomainIndex` maps each file to the
deepest manifest-bearing ancestor directory; the root is the `""` domain
(`core/domains.py:36-69`). A `domain_scoped_evidence` predicate (`DEPENDENCY`)
adjudicates a sub-project claim against that domain's own manifest; a
root-domain (`""`) claim describes the whole repository and sees the union of
every manifest (`core/pipeline.py:579-592`, `predicates/dependency.py:17-20`).
Whole-tree predicates always match the merged inventory.

---

## 5. Drift-type conformance table

Canonical classes and their `unit`/`scope`/`artifact_class` are from
`injected_gold/normalization.json`. The predicate column is the bridge to the
engine: it is the code-correct answer, cross-checked against
`injected_gold/scripts/coverage.py:35-49` (`ARTIFACT_TO_PREDICATE`) and
the retired deterministic-operator registry (not shipped). The **"backed by a predicate"** half of
each bucket is a code fact, cited in the predicate column; the **"catalog
in-scope"** half follows the evaluation taxonomy's `scope: in` classes
(`normalization.json:7-20`) — the benchmark's taxonomy, not a declaration made by
the tool (see §1.1).

### 5.1 Repo-level in-scope classes (scope `in`, unit `repo`)

| canonical_class | unit/scope | predicate (or none) | bucket | note |
|---|---|---|---|---|
| `external-dependency-drift` | repo / in | `DEPENDENCY` | **IN** | version-break operator `refuted`; a removal (undeclared) abstains |
| `path-location-drift` | repo / in | `PATH_EXISTS` | **IN** | operator `path.code_rename` → `refuted` |
| `identifier-drift` | repo / in | `SYMBOL_EXISTS` | **IN** | rename operator `refuted` |
| `removed-referent-drift` | repo / in | `SYMBOL_EXISTS` | **IN** | deleted qualified symbol → unresolved dotted claim (`structure.py:414`). `coverage.py` maps `referent` → `SYMBOL_EXISTS` (corrected; see §5.4) |
| `license-drift` | repo / in | `LICENSE` | **IN** | declared-license mismatch; conformance-template injector (§3.4) |
| `dockerfile-drift` | repo / in | `HAS_DOCKERFILE` | **IN** | claimed Dockerfile absent; conformance-template injector (§3.5) |
| `ci-workflow-drift` | repo / in | `HAS_CI_WORKFLOW` | **IN** | claimed CI workflow absent; conformance-template injector (§3.6) |
| `config-key-drift` | repo / in | none | catalog in-scope, not implemented | no predicate for env-var / feature-flag keys |
| `api-endpoint-drift` | repo / in | none | catalog in-scope, not implemented | no predicate for HTTP route strings |
| `type-drift` | repo / in | none | catalog in-scope, not implemented | no predicate for type annotations |
| `schema-field-drift` | repo / in | none | catalog in-scope, not implemented | no predicate for schema field keys |
| `membership-drift` | repo / in | none | catalog in-scope, not implemented | no declared enum-membership predicate |
| `missing-documentation` | repo / in | none | catalog in-scope, not implemented | omission; operator is `completeness_gap` (no claim to refute) |
| `invalid-example-instruction` | repo / in | none | catalog in-scope, not implemented | command/example change; no predicate |
| `cross-document-drift` | repo / in | none | catalog in-scope, not implemented | no cross-document predicate |
| `translation-drift` | repo / in | none | catalog in-scope, not implemented | localized copies are filtered by the English-only gate; no predicate |
| `value-drift` | repo / in | none | catalog in-scope, not implemented | project-version pins are not adjudicated (version numbers routinely match dependency versions and arbitrary literals) |

**Count (normative).** Of the 17 repo-level in-scope canonical classes,
**7 are IN SCOPE** and **10 are CATALOG IN-SCOPE, NOT IMPLEMENTED**. None of these 17 is
out of scope by the benchmark overlay.

### 5.2 Out-of-scope classes (scope `out`, `candidate`, `control`)

All rows below are **OUT OF SCOPE** for the claim vocabulary. The `unit`/`scope`
column is from `normalization.json`; the class lists match
`injected_gold/boundary.json`.

| canonical_class | unit/scope | predicate (or none) | bucket | note |
|---|---|---|---|---|
| `behavior-drift` | behavior / out | none | OUT | semantics/behavior; not claimed |
| `signature-drift` | behavior / out | none | OUT | not claimed |
| `constraint-drift` | method / out | none | OUT | not claimed |
| `security-drift` | behavior / out | none | OUT | not claimed |
| `exception-contract-drift` | method / out | none | OUT | not claimed |
| `null-semantics-drift` | method / out | none | OUT | not claimed |
| `format-encoding-drift` | method / out | none | OUT | not claimed |
| `polarity-order-drift` | method / out | none | OUT | not claimed |
| `lifecycle-contract-drift` | method / out | none | OUT | not claimed |
| `return-value-semantics-drift` | method / out | none | OUT | not claimed |
| `parameter-mismatch` | behavior / out | none | OUT | not claimed |
| `unused-parameter` | method / out | none | OUT | not claimed |
| `copy-edit-drift` | repo / out | none | OUT | typo/grammar; not claimed |
| `presentation-format` | doc / out | none | OUT | not claimed |
| `documentation-process` | process / out | none | OUT | not claimed |
| `documentation-tooling` | tool / out | none | OUT | not claimed |
| `data-quality` | data / out | none | OUT | not claimed |
| `control-repair-failure` | repair / out | none | OUT | not claimed |
| `error-message-drift` | repo / candidate | none | OUT (candidate, unconfirmed) | `boundary.json:candidate_unconfirmed` |
| `control-pre-existing` | repo / control | none | OUT (control) | control class, not a drift type |
| `control-misinterpreted` | repo / control | none | OUT (control) | control class |
| `control-illustrative` | repo / control | none | OUT (control) | control class |
| `control-benign-equivalence` | repo / control | none | OUT (control) | control class |
| `control-incorrect-external` | repo / control | none | OUT (control) | control class |
| `rubric-correctness` | rubric / control | none | OUT (control) | rubric dimension, not a drift type |
| `rubric-up-to-date` | rubric / control | none | OUT (control) | rubric dimension |
| `rubric-completeness` | rubric / control | none | OUT (control) | rubric dimension |
| `axis-commit-induced` | rubric / control | none | OUT (control) | rubric axis |

### 5.3 Bucket summary

- **Repo-level scope-`in` classes:** 17 total → **7 IN SCOPE**, **10 CATALOG
  IN-SCOPE, NOT IMPLEMENTED**, **0 OUT**.
- **All canonical classes:** 45 total → 7 IN, 10 catalog-in-scope-not-implemented,
  28 OUT (18 scope-`out`, 1 candidate, 9 control).

### 5.4 Coverage measurement (corrected)

`injected_gold/scripts/coverage.py` and `injected_gold/README.md` §5 report the
post-freeze expressiveness measurement. They previously reported **4/14
expressible**, with `artifact_class` `referent` mapped to `None`, i.e. missing
`removed-referent-drift`. That was a defect in the measurement map, not a scope
fact: the only operator for it, `referent.code_delete` (`operators.json:70-82`),
deletes a referenced top-level symbol and declares `expected_outcome: "refuted"`;
a deleted qualified symbol is an unresolved dotted claim under a project-owned top
and is `REFUTED` by `SYMBOL_EXISTS` (`predicates/structure.py:414`). The map was
corrected (`coverage.py:42`, `referent → SYMBOL_EXISTS`) and now reports **7/17
expressible**: path, identifier, removed-referent, dependency, license,
dockerfile, ci_workflow — the same seven classes this document marks IN SCOPE.
`value-drift` and `cross-document-drift` are reported as non-expressible gaps
(no predicate).

---

## 6. Not claimed

The tool does **not** commit to any of the following.

1. **Behavior/semantics and prose quality.** Anything whose ground truth is
   runtime behaviour, prose quality or presentation rather than a code-derived
   fact: `behavior-drift`, `signature-drift`, `constraint-drift`, `security-drift`,
   `exception-contract-drift`, `null-semantics-drift`, `format-encoding-drift`,
   `polarity-order-drift`, `lifecycle-contract-drift`,
   `return-value-semantics-drift`, `parameter-mismatch`, `unused-parameter`,
   `copy-edit-drift` (`boundary.json:out_of_scope_repo_expr`).
2. **Doc/process/tool/data classes.** `presentation-format`,
   `documentation-process`, `documentation-tooling`, `data-quality`,
   `control-repair-failure` (`boundary.json:out_of_scope_doc_process_data`).
3. **Candidate class.** `error-message-drift` is unconfirmed and is not claimed
   (`boundary.json:candidate_unconfirmed`).
4. **Controls and rubric axes.** The nine `control-*` / `rubric-*` /
   `axis-commit-induced` classes are validation controls, not drift types
   (`boundary.json:control_classes`).
5. **The 10 repo-level canonical classes with no predicate** (§5.1):
   `config-key-drift`, `api-endpoint-drift`, `type-drift`, `schema-field-drift`,
   `membership-drift`, `missing-documentation`, `invalid-example-instruction`,
   `cross-document-drift`, `translation-drift`, `value-drift`. They are not
   adjudicated by the current predicate vocabulary.
6. **Lock-file-derived presence.** A package present only in `uv.lock` /
   `poetry.lock` is never treated as a declared dependency
   (`evidence/manifests.py:31-40`; `NEI "undeclared (open by transitivity)"`,
   `predicates/dependency.py:502`).
7. **Bare-name refutation.** Bare (unqualified) symbol or unreferenced bare
   filename mentions are never refuted (`predicates/structure.py:387-394`,
   `predicates/listing.py:422-427`). For symbols this is the deliberate
   abstention of §3.3.1 (`NEI "unresolved bare name"`), not a miss.

---

## 7. Provenance appendix

**§2 predicate inventory.** `predicates/__init__.py:20-28`;
`predicates/dependency.py:47,570-581`; `predicates/listing.py:64,435-443`;
`predicates/structure.py:57,513-522`; `predicates/crossdoc.py:47,49,644-665`;
`predicates/infra.py:27,289-307`; `predicates/base.py:10-16,88-106`;
`core/pipeline.py:487-497,579-592,613-622`.

**§3.1 `DEPENDENCY`.** `predicates/dependency.py:1-7,9-21,47,71-79,82-121,
367-407,440-532,570-581`; `vocabularies/dependency.py:33,95-122,156-164`;
`data/dependency.json`; `evidence/manifests.py:31-40,79-103,168-180,522-557`;
`markers/version.py:261-312`.

**§3.2 `PATH_EXISTS`.** `predicates/listing.py:11-19,64,66-140,166-249,275-298,
307-428`; `evidence/listing.py:46-106`; `evidence/git.py:24-63`;
`vocabularies/structure.py:1-8,25-36,88-103`; `predicates/base.py:111-119,127-154`.

**§3.3 `SYMBOL_EXISTS`.** `predicates/structure.py:3-17,57,61-74,140-168,225-249,
269-292,306-414,513-522`; `evidence/symbols.py:1-9,87-102,833-849`;
`vocabularies/structure.py:506-592`.

**§3.4 `LICENSE`.** `predicates/crossdoc.py:1-11,30-31,44-61,63-121,124-186,200`;
`data/project.json:license_names,license_context_words`; `evidence/project.py:102-152,
289-411,484-488`.

**§3.5–3.6 `HAS_DOCKERFILE` / `HAS_CI_WORKFLOW`.** `predicates/infra.py:27,37-92,
121-183,203-215,224-307`; `data/project.json:ci_names,ci_context_words,
ci_config_files,ci_config_dirs`; `evidence/infra.py:19-92`.

**§4 corpus/document scope.** `data/pipeline.json:2-20`; `core/pipeline.py:29,
78-117,120-171,174-239,346-416,500-528,637-668`; `core/windows.py:115-134,137-243`;
`core/domains.py:36-69`; `evidence/git.py:1-14,24-63`.

**§5 conformance table.** `injected_gold/normalization.json`;
`injected_gold/scripts/coverage.py:32-49,82-126`;
the retired deterministic-operator registry, entries 26-307 (not shipped);
`injected_gold/boundary.json`;
`injected_gold/README.md:96-104`.

**§6 not claimed.** `injected_gold/boundary.json`;
the retired deterministic-operator registry, entries 6-11 (not shipped);
`evidence/manifests.py:31-40`;
`predicates/dependency.py:502`; `predicates/structure.py:387-394`;
`predicates/listing.py:422-427`.
