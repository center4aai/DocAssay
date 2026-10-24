repo: httpx
docs=25 claims=1023 referents=217 evidence=1828
code_verdicts: {'REFUTED': 1, 'SUPPORTED': 110, 'NEI': 113}  coverage=0.50  resolved=111

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 18 items in 6 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 1
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 1 of 1):
  1. SYMBOL_EXISTS httpx.mounts docs/advanced/transports.md:178-178
     tier: -
     raw: Or this example, which uses a custom transport and `httpx.Mounts` to always redirect `http://` requests.

