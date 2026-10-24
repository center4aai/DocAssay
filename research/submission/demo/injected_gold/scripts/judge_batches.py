"""Build per-repo "tool diff" batches for an LLM adjudicator (judge agent).

The deterministic scorer (``score_injections.py``) matches a new finding to an
injection by object heuristics. This harness hands the same question to an
independent judge agent: for each injected artifact, given the tool's
baseline->injected finding diff, decide **whether the tool reacted and how**.

It only *builds* the batches and the rubric; the judging itself is performed by
a spawned agent, and ``judge_apply.py`` merges the verdicts. The judge never
sees the deterministic verdict (no anchoring).

Run::

    PYTHONPATH=src uv run python .../scripts/judge_batches.py \
        --manifest .../runs/<run>/manifest.jsonl \
        --claims .../runs/<run>/claims --out .../runs/<run>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import score_injections as S  # noqa: E402

RUBRIC = """# Judge rubric — did the tool react to the injection, and how?

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
"""


def build(repo: str, entries: list[dict], claims_by: dict) -> dict:
    base = claims_by.get((repo, "baseline"), [])
    inj = claims_by.get((repo, "injected"), [])

    def slim(c: dict) -> dict:
        return {
            "source": c.get("source"),
            "line": c.get("line_start"),
            "predicate": c.get("predicate"),
            "object": c.get("object"),
            "reason": c.get("code_verdict_reason"),
        }

    def new_of(verdict: str) -> list[dict]:
        base_keys = S._keys(base, verdict)
        return [
            slim(c)
            for c in inj
            if c.get("code_verdict") == verdict and S._claim_key(c) not in base_keys
        ][:80]

    diff = {
        "new_refuted": new_of("REFUTED"),
        "new_nei": new_of("NEI"),
        "new_supported": new_of("SUPPORTED"),
    }

    items = []
    for i, e in enumerate(entries):
        items.append(
            {
                "id": f"{repo}::{i}",
                "repo": repo,
                "op_id": e["op_id"],
                "canonical_class": e["canonical_class"],
                "expected_outcome": e.get("expected_verdict"),
                "control": e.get("control", "none"),
                "injection": {
                    "direction": e.get("direction"),
                    "artifact": S._match_object(e),
                    "new": e.get("new"),
                    "doc_path": e.get("doc_path"),
                    "target": e.get("target"),
                },
            }
        )
    return {"repo": repo, "tool_diff": diff, "items": items}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--claims", required=True, help="directory of <repo>__<snap>.jsonl")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    manifest = [
        json.loads(line)
        for line in Path(args.manifest).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    claims_dir = Path(args.claims)
    repos = sorted({e["repo"] for e in manifest})
    claims_by = {}
    for repo in repos:
        for snap in ("baseline", "injected"):
            claims_by[(repo, snap)] = S.load_claims(claims_dir / f"{repo}__{snap}.jsonl")

    judge_dir = Path(args.out) / "judge"
    judge_dir.mkdir(parents=True, exist_ok=True)
    (judge_dir / "RUBRIC.md").write_text(RUBRIC, encoding="utf-8")

    for repo in repos:
        entries = [e for e in manifest if e["repo"] == repo]
        batch = build(repo, entries, claims_by)
        path = judge_dir / f"batch_{repo}.json"
        path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        n_ref = len(batch["tool_diff"]["new_refuted"])
        print(f"{repo}: {len(batch['items'])} items, new_refuted={n_ref} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
