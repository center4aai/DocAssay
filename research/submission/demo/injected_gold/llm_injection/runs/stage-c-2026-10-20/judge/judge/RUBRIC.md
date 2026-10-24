# Judge rubric — did the tool react to the injection, and how?

You are an independent adjudicator for a documentation/repository inconsistency
benchmark. For each item you get:

- `injection`: what was changed. `artifact` is the value that became stale
  (the old symbol / path / dependency / target); `new` is what it became.
  `direction` is `code_side` (code changed, doc keeps the old mention) or
  `doc_side` (a doc mention was changed).
- `tool_diff`: the tool's findings on the injected tree that are NOT in the
  baseline, split into `new_refuted`, `new_nei`, `new_supported`. Each finding
  has `source` (doc file), `line`, `predicate`, `object`, `reason`.

Decide, WITHOUT looking at any line number of the injection, only from the
change itself and the tool's diff:

- `refuted` — a new finding whose `object` refers to the same artifact the
  injection invalidated (the tool flagged the stale reference). Near matches
  count (case, qualified vs bare, path suffix). Matching in ANY document counts.
- `nei` — a new finding about the artifact that ABSTAINED (verdict NEI): the
  tool noticed the mention but could not decide.
- `none` — no new finding concerns the injected artifact.

Return for EVERY item id a verdict object. Output STRICT JSON, no prose:

```json
{"verdicts": [
  {"id": "<item id>", "reaction": "refuted|nei|none",
   "matched": ["<source:line predicate object>", "..."],
   "confidence": "high|medium|low",
   "note": "<one short sentence explaining why>"}
]}
```
