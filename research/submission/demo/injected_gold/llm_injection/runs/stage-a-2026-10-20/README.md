# Stage A — natural corpus / decontaminated injector

This directory is the committed record of Stage A: the sensitivity experiment
run after the checker-shaped synthetic corpus produced the 0.925 headline. It
contains the analysis and evidence, not the large transient snapshots/claims
(those remain in `/tmp/docassay-stage-a` and are regenerable).

## Read this first

- **`report.md`** — the full Stage A report: design, results, three-outcome
  analysis, baseline/circularity discussion, caveats.
- **`metrics-active-4class.md`** — the compact active-scope metrics table.
- **`removal-report.md`** — what was removed after Stage A (`VERSION` predicate,
  `doc_drift`), file-level changes, verification.
- **`baseline_evidence.md`** — real-repo baseline REFUTED counts and examples
  showing why a 0-REFUTED acceptance gate is circular.
- **`entries.json`** — per-injection table (repo, class, target, reaction,
  claim form).
- **`corpus_freeze.json`** — hashes of the natural corpus and clean prompts.
- **`prompts_natural/`** — the clean docwriter/injector prompts used in Stage A.

## Headline

Active four-class scope (path, external-dependency, identifier,
removed-referent):

- **18/32 refuted** (0.5625), **10/32 NEI** (0.3125), **4/32 none** (0.125);
- end-to-end refutation **18/48 = 0.375**;
- per class: path 10/0/0, external 7/0/2, identifier 1/6/1,
  removed-referent 0/4/1.

`NEI` is a deliberate abstention, not a miss. The symbol classes are limited
because natural docs use bare names, and `SYMBOL_EXISTS` refutes only qualified
project-owned names; see `report.md` §5–§6 and `SCOPE.md` §3.3.1.

## Provenance

| item | value |
|---|---|
| branches | `demo` (no new branch) |
| docwriter | `claude-haiku-5-5`, natural prompt (`prompts_natural/docwriter.md`) |
| injector | `deepseek-v4.1-flash` |
| corpus | 4 synthetic repos (`quillpad`, `tidecast`, `ledgerly`, `parcelroute`) |
| run data | `/tmp/docassay-stage-a` (transient; not committed) |
| Stage A date | 2026-10-20 |

## Caveats

- Same tool-shaped specs and same exemplar bank as the earlier arm; only the
  docwriter contract, injector target rules, and baseline gate were changed.
- No external claim annotation: “verified” is on-disk mutation validity.
- The audit is LLM-based, model-based.
- No controls; precision is not measured in this arm.
- Baseline 0 REFUTED on this corpus is not evidence of real-world precision.
