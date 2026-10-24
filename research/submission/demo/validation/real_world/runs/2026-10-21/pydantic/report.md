repo: pydantic
docs=96 claims=4252 referents=736 evidence=14620
code_verdicts: {'REFUTED': 6, 'SUPPORTED': 395, 'NEI': 384}  coverage=0.51  resolved=401

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 23 items in 6 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 2
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
    SYMBOL_EXISTS    TRUE_CANDIDATE  neg=0: 1
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 6 of 6):
  1. PATH_EXISTS a.py docs/concepts/forward_annotations.md:161-161
     tier: bare
     raw: Because `B` isn't available at runtime in `a.py`, the `A` model is left incomplete. In a parent module
  2. PATH_EXISTS pydantic.json docs/concepts/json_schema.md:615-615
     tier: bare
     raw: See the [API documentation][pydantic.json_schema.WithJsonSchema] for more details.
     cited by 22 claims
  3. SYMBOL_EXISTS pydantic_core._pydantic_core docs/integrations/aws_lambda.md:50-50
     tier: -
     raw: no module named `pydantic_core._pydantic_core`
  4. PATH_EXISTS llms.txt docs/integrations/llms.md:1-1
     tier: bare
     raw: The Pydantic documentation is available in the [llms.txt](https://llmstxt.org/) format.
     cited by 7 claims
  5. PATH_EXISTS mypy.ini docs/integrations/mypy.md:61-61
     tier: bare
     raw: === "`mypy.ini`"
  6. PATH_EXISTS flamegraph.svg pydantic-core/README.md:131-131
     tier: bare
     raw: The `flamegraph` command will produce an interactive SVG at `flamegraph.svg`.

