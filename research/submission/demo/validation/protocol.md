# Tool validation protocol — injection-based conformance testing

> Status: **draft, active**. This is the operative validation protocol for the
> demo artifact. It supersedes the document-sampled (Task E) gold
> and the annotation-protocol line: those measured extraction agreement between
> annotators and had no objective denominator (negative inter-annotator κ). This
> protocol supplies the missing denominator by injecting known defects and
> measuring whether the tool *should* have caught them.

The tool's **claim scope** (which drift types and under which conditions the
tool commits to detecting) is a separate, normative document, `SCOPE.md`. It is
declared before any scoring run and is never derived from engine behaviour.
Nothing here is scored against classes outside that scope.

---

## 1. What is being tested

The tool is a deterministic symbolic verifier: it extracts claims from
documentation, adjudicates them against a code-derived fact inventory, and emits
a verdict (`SUPPORTED / REFUTED / NEI`) per claim. The validation question is
**conformance**: for each drift type the tool declares it detects, does it detect
injected instances of that type?

This is a **conformance test against a declared contract**, not an open-world
benchmark. Three buckets, kept separate everywhere in reporting:

| bucket | definition | role |
|---|---|---|
| **in scope** | drift type backed by an implemented predicate (declared in `SCOPE.md`) | the recall denominator |
| **catalog in-scope, not implemented** | drift type the evaluation taxonomy lists as in-scope but with no predicate | reported separately as a gap (never in the denominator, never hidden) |
| **out of scope** | drift type neither predicate-backed nor in the taxonomy's in-scope list | reported as the expressiveness boundary |

The scope must be written **before** any scoring run and never derived from
what the engine happened to do. That is the single guard that separates a
conformance test from self-serving evaluation.

This protocol deliberately does **not** test operators that the tool, by
construction, does not aim to catch.

---

## 2. Where defects come from

Defects are **manufactured** (injected), but their *distribution* is grounded in
real reported bugs:

- A **few-shot exemplar bank** built from human-triaged real incidents
  (`readu` TP themes, `CASCADE` `inco` labels). LLM-derived hypotheses
  (`readu_raw` scenarios) are a separate, clearly labelled pool and are not
  mixed into the primary bank.
- An **injector model** receives exemplars for one in-scope drift type and
  introduces an analogous defect into a repository.
- The source instruments (READU / CASCADE / DocChecker) are **detectors over
  natural commits**; none of them implements a mutation generator. The injector
  is new, so its outputs must be verified, not trusted.

Anchoring injection in the real-incident distribution (not in the tool's
vocabulary) is what keeps the target universe from collapsing onto targets the
tool is already known to see.

### 2.1 Conformance templates (predicate-defined referents)

For the three **capability predicates** whose referent is fixed by the predicate
itself, the target is **not a choice**: `HAS_DOCKERFILE` always refers to a
`Dockerfile`, `HAS_CI_WORKFLOW` to a CI config, `LICENSE` to a declared license.
These are injected as **conformance templates**
(`injected_gold/conformance/`), a separate provenance arm (`origin:
"conformance"`), and are **never** pooled with the real-incident bank or with
`catalog_ours.json`. A template is admissible **only** while the referent is
predicate-defined; for prose drift (path / symbol / dependency) a template would
reintroduce the circularity guard 2 forbids, and is inadmissible.

---

## 3. Objects

| object | description |
|---|---|
| **corpus repo** | a small, uncontaminated repository (agent-generated, or an organic repo not used to build the tool or the exemplar bank) |
| **injection** | one structured defect: `{repo, drift_type, direction, target artifact, doc_path, old, new, target_claim}`, plus the mutation patch |
| **manifest** | the frozen list of verified injections for a run |
| **verifier** | the deterministic, engine-free program that proves an injection exists on disk and reports the claim it invalidates |
| **finding diff** | new tool findings on the injected tree vs the baseline tree |

---

## 4. Pipeline

### 4.1 Corpus

Repositories must be **uncontaminated**: not containing the tool's own test
material and, for the primary run, not the repositories whose commits built the
exemplar bank.

**Baseline consistency is established independently of the tool.** An
independent audit — a manual reading, or a specified check that does not call the
engine — establishes that the baseline documentation is consistent with the code
and records any known-inconsistent statements. Only then is the corpus **frozen**
(snapshot + manifest). The engine is not the authority on whether its own
baseline is clean.

After the freeze, run the engine **once** on the baseline and **record** every
baseline `REFUTED` finding. Baseline findings are data, not noise:

- Do **not** edit the corpus to make baseline findings disappear. A repair is a
  new corpus version with a new freeze, and the finding is reported against both
  versions.
- **Adjudicate** each baseline finding as either a **true documentation bug**
  (pre-existing, not attributable to any injection) or a **tool false positive**,
  and report both counts. The first is a real finding the tool got right; the
  second is the tool's precision cost on clean text.
- The finding diff in §4.4 is computed against the frozen baseline *including*
  its recorded findings, so an injection is credited only for a **new** finding
  at the injected artifact.

`generate_synthetic.py check` is a **diagnostic** only — a sanity check on corpus
generation and inventory shape. It is never an acceptance gate, and a corpus is
not selected, rejected or repaired on the basis of its output.

**Why a 0-`REFUTED` acceptance gate is circular.** Requiring the baseline to
produce zero refutations makes the tool under test the judge of its own corpus.
A repository can pass either by being selected because the engine already agrees
with it, or by being repaired until the engine's findings vanish; both use the
engine's output as ground truth. Such a gate also hides the evidence precision
needs: baseline false positives are "repaired" out of existence instead of being
reported, so precision on clean text looks perfect by construction. A clean
synthetic baseline is therefore **not** evidence of real-world precision — it
shows only that the engine is self-consistent on text generated to match its own
vocabulary. Baseline findings are reported, never gated.

### 4.2 Injection (LLM, few-shot, in-scope only)

One drift type per injection. The injector receives a small set of real-bug
exemplars for that type and must produce an **analogous** defect — the exemplars
anchor **target selection** (what kind of artifact tends to drift), not only
phrasing. Constraints on the injector:

- It never sees the tool, its predicates, its vocabulary, or its output.
- It emits a **structured mutation** against a **named artifact** so the defect
  stays mechanically verifiable. Free prose edits are not admissible: if the
  artifact cannot be named, the injection cannot be verified and does not enter
  the manifest.
- It does not use the same model/prompt family that wrote the corpus docs
  (avoid a style leak between the author of the "clean" text and the injector).
- It targets only drift types in **scope** (section 1). Out-of-scope and
  declared-but-unimplemented types are not injected for the headline number.

### 4.3 Deterministic verification

`verify` proves each injection on disk **without importing the tool**, and
emits the **claim** the defect invalidates:

1. the mutation is applied exactly as recorded (`old` present before, `new`
   after; file parses);
2. the defect is real for the drift type (e.g. the old path is absent from the
   tree, the old symbol is absent from the AST inventory, the manifest constraint
   no longer intersects the documented one);
3. the **target claim**: the doc line + referent the tool is expected to refute.

An injection that fails verification is dropped before scoring (it is a
generator defect, not a tool miss). The verifier is deliberately
**claim-level**: "file changed" is not sufficient, because a miss can then not be
distinguished from a claim that was never extracted.

### 4.4 Tool run and finding diff

Run the tool on the baseline and injected trees. Detection is **not** bound to
the recorded line: for each injection, scan the whole baseline→injected finding
diff for a new claim whose referent matches the injected artifact, and record
**how the target claim was handled**: `refuted`, `nei` (claim formed, abstained)
or `none` (no claim formed). **Refutation rate** on a class = injected artifacts
the tool refuted / injected artifacts; `nei` and `none` are separate reported
outcomes and are never folded into that numerator or denominator (§5).

### 4.5 Adjudication

Two independent adjudicators of *how the tool reacted*:

- an **LLM judge** given the per-repo tool diff and a rubric;
- a **deterministic diff judge** (no LLM) over the same diff.

Report their agreement; disagreements are resolved manually and recorded. The
judge adjudicates the tool's **reaction**, never whether the injection is a
real defect — that is the verifier's and the annotator's job.

### 4.6 Independent annotation

Independent annotation is targeted, not total:

- **Miss stream:** every injection with outcome `none` (defect verified, no
  target claim formed). The annotator confirms the defect is real and that the
  claim was genuinely never extracted.
- **Abstention stream:** every injection with outcome `nei` (claim formed, tool
  abstained). The annotator confirms the abstention reason applies — for
  example, that a bare name really is unresolvable — and that it is not a
  disguised miss. Abstentions are reported as abstentions, never as misses.
- **Control stream:** a sample of injections the tool **did** refute, to catch
  false refutations (precision). Annotation is **blind** to the tool's verdict.
- Report inter-annotator agreement on all three streams (addresses the negative-κ
  problem of the document-sampled gold directly).

### 4.7 Freeze

LLM injection is non-deterministic. After verification the **manifest is
frozen**; all scoring is a replay of the frozen manifest plus the frozen
snapshots. Provenance per injection: injector model, prompt hash, seed, exemplar
ids, verifier result, independent verdict.

---

## 5. Metrics

Every verified injection is assigned exactly one of three outcomes, read from the
tool's reaction to the **target claim**:

| outcome | definition |
|---|---|
| `refuted` | the target claim is formed and `REFUTED` against a closed inventory — a closed-world finding |
| `nei` | the target claim is formed and the predicate abstains (`NEI`), with layer (`CLAIM_GATE` / `WORLD` / `DECIDABILITY`) and verbatim reason recorded |
| `none` | no refutation or abstention was produced for the target claim: no claim formed (gate drop, no anchor), a claim formed at a different referent, or a formed target claim wrongly returned `SUPPORTED` (sub-flagged) |

The outcomes partition the verified injections of a class:
`refuted + nei + none = N`. The `SUPPORTED` sub-case is called out explicitly: a
target claim that is formed and comes back `SUPPORTED` is a wrong-verdict miss,
not an abstention. It is carried in `none` so it cannot be mistaken for a
refutation, tagged `supported`, attributed to `evidence` / `referent` (never
`extraction`), and its count is reported next to the extraction-miss count.

### 5.1 Headline estimand: detection of the drift (amendment A1, 2026-10-21)

The tool's operational goal is **catching documentation drift**, not maximising
the count of closed-world `REFUTED` verdicts. A drift is **detected** when the
tool produces a same-artifact `REFUTED` finding anywhere in the
baseline→injected diff, **or** a same-artifact `NEI` — an explicit abstention
that names the injected artifact, with a layer and a verbatim reason. An `NEI`
is a deliberate, inspectable reaction: the tool surfaced the artifact and said
why it will not decide, instead of silently supporting the statement. Silence,
a claim at another referent, and a wrongly `SUPPORTED` claim are not detection.

- **Detection rate (`R_detect`)** — `detected / N`, the headline: the fraction
  of injected drifts the tool caught in any inspectable way.
- **Refutation rate (`R_credit`)** — `refuted / N`: the subset decided by a
  closed-world `REFUTED`. Reported next to `R_detect` as the
  **decomposition**, never instead of it.
- **Abstention rate** — `nei / N`, reported with the layer and verbatim reason.
- **Extraction-miss rate** — `none / N`, reported with the `none` sub-flag
  (`supported` / `other_referent` / `no_claim`).

`R_detect = R_credit + nei/N` by construction; `refuted + nei + none = N`. Raw
counts are reported next to every rate, and every table that quotes `R_detect`
quotes its decomposition in the same row. `R_detect` carries a repository-cluster
percentile bootstrap 95% interval (6 clusters, 10,000 replicates, fixed seed);
Wilson is not used because entries are not independent Bernoulli trials (seeds
repeat targets within a repository), and with six clusters the interval is
descriptive and may be degenerate.

**Attribution is diagnostic, not a metric of success.** `R_target` — how often
the recorded target line itself carried the reaction — is reported for every
class with the credited/target-line crosstab. A drift may be caught through
another mention of the same artifact; that is detection of the artifact, not of
the sentence, and the two are never conflated.

**`NEI` is not a miss and not a zero**, and a high abstention rate does not make
a class accurate: it marks a class where the predicate frequently declines to
decide, and the reasons are reported. Because `NEI` enters `R_detect`, every run
that headlines `R_detect` also reports a **conservative sensitivity bound** in
which only abstentions confirmed as legitimate (by annotation, or by an
engine-free avoidability check) count as detected. Both numbers are reported.

- **Per-outcome stage attribution.** For `refuted`, the stage is the closed
  world that supplied the evidence; for `nei`, the recorded layer
  (`claim_gate` / `world` / `decidability`) and reason; for `none`,
  `claim_gate` / `extraction` / `referent` / `no_predicate` (the last only for
  declared-but-unimplemented). `R_detect` alone is not the result; *where* each
  outcome occurs is, and the `R_credit` / `NEI` / `none` split is reported with
  every detection rate.
- **Precision** on controls (consistent-present and consistent-absent targets):
  fraction of controls the tool does not refute, with the `nei` / `none` split
  of the non-refuted controls reported alongside. A control refutation is a
  false positive regardless of rate.
- **Baseline findings** (§4.1): true-bug and false-positive counts adjudicated
  independently, reported separately from injected refutation.
- **Unattributed findings** on the injected tree as a precision proxy.
- **Agreement**: LLM judge vs deterministic judge; independent labels vs verifier.
- **Boundary report**: out-of-scope and declared-but-unimplemented classes, with
  their injection counts, kept out of the headline.

---

## 6. Circularity and contamination guards

1. Scope is normative and pre-declared; the denominator is never inferred from
   tool behaviour.
2. Injection targets come from a real-incident exemplar distribution, not from
   the tool's anchor vocabulary.
3. The verifier and the claim inventory used for injection are engine-free
   (standard library only); "verified" must not presuppose tool-visibility.
4. The tool is invoked only at scoring time.
5. Corpus repos are uncontaminated; the injector is a different model/prompt
   family from the doc author.
6. Declared-but-unimplemented classes are reported, never silently dropped.
7. Constructed **conformance templates** are admissible only for a
   predicate-defined (constant/listing) referent, carry `origin: "conformance"`,
   and are reported as a **separate arm** — never pooled into the real-incident
   recall denominator without that label.

---

## 7. Open items

- `SCOPE.md`: normative and active — the detected drift types and conditions
  (six predicates; bare-name policy in §3.3.1).
- Verifier coverage per in-scope type (deterministic vs manual-only).
- Exemplar-bank selection and pooling (`readu` TP / `CASCADE` vs `readu_raw`).
- Sampling size and CI targets; number of corpus repos.
- Whether organic repositories (natural-defect slice) are added as a second,
  independent validation arm.
