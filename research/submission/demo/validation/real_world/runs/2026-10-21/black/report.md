repo: black
docs=32 claims=859 referents=177 evidence=2884
code_verdicts: {'REFUTED': 3, 'SUPPORTED': 76, 'NEI': 118}  coverage=0.40  resolved=79

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 20 items in 7 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 2
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 1
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 3 of 3):
  1. PATH_EXISTS .preview.pr-comment.md docs/contributing/gauging_changes.md:54-54
     tier: bare
     raw: `.preview.pr-comment.md` and `.stable.pr-comment.md` (if triggered by a PR)
  2. PATH_EXISTS .stable.pr-comment.md docs/contributing/gauging_changes.md:54-54
     tier: bare
     raw: `.preview.pr-comment.md` and `.stable.pr-comment.md` (if triggered by a PR)
  3. SYMBOL_EXISTS scripts.make_width_table.wcwidth docs/contributing/release_process.md:73-73
     tier: -
     raw: Bump `wcwidth` to the latest version and run `scripts/make_width_table.py`

