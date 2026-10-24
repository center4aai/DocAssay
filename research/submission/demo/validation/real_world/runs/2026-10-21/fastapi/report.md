repo: fastapi
docs=187 claims=5385 referents=633 evidence=15581
code_verdicts: {'REFUTED': 23, 'NEI': 334, 'SUPPORTED': 349}  coverage=0.53  resolved=372

PRECISION (stratified measurement): top-K=1000 sample/stratum=5
  review requested: 27 items in 8 strata
    DEPENDENCY       SUPPORTED       neg=0: 5
    DEPENDENCY       TRUE_CANDIDATE  neg=0: 4
    HAS_CI_WORKFLOW  SUPPORTED       neg=0: 1
    LICENSE          SUPPORTED       neg=0: 1
    PATH_EXISTS      SUPPORTED       neg=0: 5
    PATH_EXISTS      SYSTEMATIC      neg=0: 1
    PATH_EXISTS      TRUE_CANDIDATE  neg=0: 5
    SYMBOL_EXISTS    SUPPORTED       neg=0: 5
  run `docassay consolidate <review.jsonl>` after labelling

FINDINGS (REFUTED, document order, first 23 of 23):
  1. PATH_EXISTS traefik.toml docs/en/docs/advanced/behind-a-proxy.md:231-231
     tier: bare
     raw: Then create a file `traefik.toml` with:
     cited by 2 claims
  2. PATH_EXISTS routes.toml docs/en/docs/advanced/behind-a-proxy.md:243-243
     tier: bare
     raw: This tells Traefik to listen on port 9999 and to use another file `routes.toml`.
     cited by 3 claims
  3. PATH_EXISTS log.txt docs/en/docs/advanced/events.md:121-121
     tier: bare
     raw: Here, the `shutdown` event handler function will write a text line `"Application shutdown"` to a file `log.txt`.
     cited by 2 claims
  4. PATH_EXISTS openapi.json docs/en/docs/advanced/generate-clients.md:152-152
     tier: bare
     raw: We could download the OpenAPI JSON to a file `openapi.json` and then we could **remove that prefixed tag** with a script like this:
     cited by 3 claims
  5. DEPENDENCY starlette docs/en/docs/advanced/templates.md:38-38
     tier: -
     raw: Before FastAPI 0.108.0, Starlette 0.29.0, the name was the first parameter.
     evidence: starlette:pyproject.toml:>=0.46.0
  6. DEPENDENCY pydantic docs/en/docs/deployment/versions.md:92-92
     tier: -
     raw: pydantic>=2.7.0,<3.0.0
     evidence: pydantic:pyproject.toml:>=2.9.0, pydantic:pyproject.toml:>=2.9.0,<3.0.0
  7. PATH_EXISTS swagger-ui-bundle.js docs/en/docs/how-to/custom-docs-ui-assets.md:96-96
     tier: bare
     raw: [`swagger-ui-bundle.js`](https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js)
     cited by 2 claims
  8. PATH_EXISTS swagger-ui.css docs/en/docs/how-to/custom-docs-ui-assets.md:97-97
     tier: bare
     raw: [`swagger-ui.css`](https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css)
     cited by 2 claims
  9. PATH_EXISTS redoc.standalone.js docs/en/docs/how-to/custom-docs-ui-assets.md:101-101
     tier: bare
     raw: [`redoc.standalone.js`](https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js)
  10. PATH_EXISTS app/internal/ docs/en/docs/tutorial/bigger-applications.md:52-52
     tier: unanchored
     raw: There's also a subdirectory `app/internal/` with another file `__init__.py`, so it's another "Python subpackage": `app.internal`.
  11. PATH_EXISTS app/routers/items.py docs/en/docs/tutorial/bigger-applications.md:204-204
     tier: unanchored
     raw: This code lives in the module `app.routers.items`, the file `app/routers/items.py`.
     cited by 7 claims
  12. PATH_EXISTS app/dependencies.py docs/en/docs/tutorial/bigger-applications.md:206-206
     tier: unanchored
     raw: And we need to get the dependency function from the module `app.dependencies`, the file `app/dependencies.py`.
     cited by 4 claims
  13. PATH_EXISTS app/routers/dependencies.py docs/en/docs/tutorial/bigger-applications.md:229-229
     tier: unanchored
     raw: find the module `dependencies` (an imaginary file at `app/routers/dependencies.py`)...
  14. PATH_EXISTS app/routers/users.py docs/en/docs/tutorial/bigger-applications.md:315-315
     tier: unanchored
     raw: As the files `app/routers/users.py` and `app/routers/items.py` are submodules that are part of the same Python package `app`, we can use a single dot 
     cited by 5 claims
  15. PATH_EXISTS app/routers/ docs/en/docs/tutorial/bigger-applications.md:328-328
     tier: unanchored
     raw: look for the subpackage `routers` (the directory at `app/routers/`)...
     cited by 3 claims
  16. PATH_EXISTS app/internal/admin.py docs/en/docs/tutorial/bigger-applications.md:430-430
     tier: unanchored
     raw: That way, the original `APIRouter` will stay unmodified, so we can still share that same `app/internal/admin.py` file with other projects in the organ
     cited by 3 claims
  17. PATH_EXISTS 404.html docs/en/docs/tutorial/frontend.md:75-75
     tier: bare
     raw: In this case, **FastAPI** won't serve `index.html` for missing frontend paths. It will return the `404.html` file instead.
     cited by 4 claims
  18. DEPENDENCY python docs/en/docs/tutorial/testing.md:181-181
     tier: -
     raw: platform linux -- Python 3.6.9, pytest-5.3.5, py-1.8.1, pluggy-0.13.1
     evidence: python:pyproject.toml:>=3.10
  19. DEPENDENCY python scripts/general-llm-prompt.md:172-172
     tier: -
     raw: //// tab | Python 3.8+ non-Annotated
     evidence: python:pyproject.toml:>=3.10
     cited by 2 claims
  20. PATH_EXISTS scripts/help-fastapi.md scripts/general-llm-prompt.md:307-307
     tier: anchored
     raw: [Pull Requests erzeugen](help-fastapi.md#create-a-pull-request){.internal-link target=_blank}
  21. PATH_EXISTS scripts/body-multiple-params.md scripts/general-llm-prompt.md:319-319
     tier: anchored
     raw: [Body - Multiple Parameters: Singular values in body](body-multiple-params.md#singular-values-in-body){.internal-link target=_blank}
     cited by 3 claims
  22. PATH_EXISTS scripts/tests/test_translation_fixer/test_complex_doc/data/project-generation.md scripts/tests/test_translation_fixer/test_complex_doc/data/en_doc.md:196-196
     tier: anchored
     raw: This is a link with attributes: [**FastAPI** Project Generators](project-generation.md){.internal-link target=_blank}
     cited by 2 claims
  23. PATH_EXISTS scripts/tests/test_translation_fixer/test_markdown_links/data/project-generation.md scripts/tests/test_translation_fixer/test_markdown_links/data/en_doc.md:7-7
     tier: anchored
     raw: Two links here: [How to](https://fastapi.tiangolo.com/how-to/) and [Project Generators](project-generation.md){.internal-link target=_blank}.

