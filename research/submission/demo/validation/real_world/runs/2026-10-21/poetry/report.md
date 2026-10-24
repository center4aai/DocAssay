repo: poetry
docs=45 claims=1732 referents=194 evidence=7589
code_verdicts: {'REFUTED': 1, 'NEI': 151, 'SUPPORTED': 74}  coverage=0.33  resolved=75

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 18 items in 6 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 1
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 1 of 1):
  1. DEPENDENCY python docs/managing-environments.md:130-130
     tier: -
     raw: Python:         3.7.1
     evidence: python:pyproject.toml:>=3.10,<4.0

