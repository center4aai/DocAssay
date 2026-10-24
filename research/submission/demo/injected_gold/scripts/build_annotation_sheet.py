"""Build the blind annotation sheet for Stage B.

Every verified injection and every control gets one row.  The row contains the
document line, the target claim, and the mutation (``old`` -> ``new``), but **no
tool verdict, layer, reason, or reaction**.  The annotation fields are blank for
independent annotators.

Run::

    PYTHONPATH=src uv run python .../scripts/build_annotation_sheet.py \
        --run .../runs/stage-b-2026-10-20
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INJECTED_GOLD = SCRIPTS.parent
NATURAL = INJECTED_GOLD / "synthetic-natural"

BLANK_FIELDS = (
    "claim_type",
    "claim_form",
    "context_source",
    "defect_is_real",
    "nei_reason_applies",
    "none_claim_not_extracted",
    "control_false_positive",
    "same_artifact",
    "annotator_id",
    "notes",
)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _doc_line(repo: str, doc_path: str, line: int | None, corpus_dir: Path | None = None) -> str:
    if not repo or not doc_path or not line:
        return ""
    path = (corpus_dir or NATURAL) / repo / doc_path
    if not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1]
    return ""


def _mention_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def build_stage_c(run: Path, corpus_dir: Path, seed: int) -> tuple[list[dict], list[dict]]:
    """Stage C blind sheet + a separate key (role is never shown to annotators)."""
    manifest = _read_jsonl(run / "manifest.jsonl")
    controls = _read_jsonl(run / "controls.jsonl")
    entries = json.loads((run / "entries.json").read_text(encoding="utf-8")) \
        if (run / "entries.json").is_file() else []
    by_snapshot = {e["snapshot_id"]: e for e in entries if e.get("control") == "none"}
    rows: list[dict] = []
    key: list[dict] = []

    def add(row: dict, role: str, target_entry: dict) -> None:
        rows.append(row)
        key.append({"mention_id": row["mention_id"], "mention_role": role,
                    "repo_name": row["repo_name"], "class": row["class"],
                    "doc_path": row["doc_path"], "line": row["line"],
                    "target": row["target"], "snapshot_id": row.get("snapshot_id")})

    for entry in manifest:
        repo = entry.get("repo_name") or entry.get("repo", "").split("__", 1)[0]
        meta = {
            "repo_name": repo,
            "class": entry.get("canonical_class"),
            "target_document": entry.get("target_document", "n/a"),
            "genre": entry.get("genre", "n/a"),
            "target": entry.get("target"),
            "old": entry.get("old"),
            "new": entry.get("new"),
            "symbol": entry.get("symbol"),
            "target_claim": entry.get("target_claim", ""),
            "control": entry.get("control", "none"),
            "artifact_identity": str(entry.get("old") or entry.get("target") or "").strip().lower(),
            "snapshot_id": entry.get("snapshot_id"),
        }
        doc_path, line = entry.get("doc_path"), entry.get("line")
        identity = f"{entry.get('snapshot_id')}::{doc_path}::{line}"
        row = {
            "mention_id": _mention_id(identity + "::target"),
            **meta,
            "doc_path": doc_path,
            "line": line,
            "doc_line_text": _doc_line(repo, doc_path, line, corpus_dir),
            "mention_text": str(entry.get("target") or ""),
            "is_control": False,
        }
        for field in BLANK_FIELDS:
            row[field] = ""
        add(row, "target_line", entry)
        seen = {(doc_path, line)}
        for match in (by_snapshot.get(entry.get("snapshot_id"), {}) or {}).get("matched", []):
            loc = (match.get("source"), match.get("line_start"))
            if loc in seen:
                continue
            seen.add(loc)
            cross = {
                "mention_id": _mention_id(identity + f"::cross::{loc}"),
                **meta,
                "doc_path": loc[0],
                "line": loc[1],
                "doc_line_text": _doc_line(repo, loc[0], loc[1], corpus_dir),
                "mention_text": str(match.get("object") or ""),
                "is_control": False,
            }
            for field in BLANK_FIELDS:
                cross[field] = ""
            add(cross, "other_mention", entry)

    for entry in controls:
        repo = entry.get("repo_name") or entry.get("repo", "").split("__", 1)[0]
        doc_path, line = entry.get("doc_path"), entry.get("line")
        row = {
            "mention_id": _mention_id(
                f"{entry.get('repo')}::{doc_path}::{line}::control::{entry.get('control')}"
            ),
            "snapshot_id": entry.get("repo"),
            "repo_name": repo,
            "class": entry.get("canonical_class"),
            "target_document": entry.get("target_document", "n/a"),
            "genre": entry.get("genre", "n/a"),
            "target": entry.get("target"),
            "old": entry.get("old"),
            "new": entry.get("new"),
            "symbol": entry.get("symbol"),
            "target_claim": "",
            "control": entry.get("control", "n/a"),
            "control_family": entry.get("family"),
            "artifact_identity": str(entry.get("target") or "").strip().lower(),
            "doc_path": doc_path,
            "line": line,
            "doc_line_text": _doc_line(repo, doc_path, line, corpus_dir),
            "mention_text": str(entry.get("target") or ""),
            "is_control": True,
        }
        for field in BLANK_FIELDS:
            row[field] = ""
        rows.append(row)
        key.append({"mention_id": row["mention_id"], "mention_role": "control",
                    "repo_name": repo, "class": row["class"],
                    "doc_path": doc_path, "line": line, "target": row["target"],
                    "snapshot_id": row["snapshot_id"]})

    random.Random(seed).shuffle(rows)
    return rows, key


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--stage-c", action="store_true")
    ap.add_argument("--corpus-dir", default="")
    ap.add_argument("--seed", type=int, default=20261020)
    args = ap.parse_args(argv)

    run = Path(args.run)
    if args.stage_c:
        corpus = (
            Path(args.corpus_dir) if args.corpus_dir
            else run.parent.parent / "synthetic-natural-c"
        )
        rows, key = build_stage_c(run, corpus, args.seed)
        out = Path(args.out) if args.out else run / "annotation_sheet.jsonl"
        out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                       encoding="utf-8")
        (run / "annotation_sheet_key.jsonl").write_text(
            "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in key), encoding="utf-8"
        )
        print(f"wrote {len(rows)} blind Stage C rows -> {out}")
        print("wrote annotation_sheet_key.jsonl (analysis only; not shown to annotators)")
        return 0

    manifest = _read_jsonl(run / "manifest.jsonl")
    controls = _read_jsonl(run / "controls.jsonl")
    rows: list[dict] = []
    for entry in manifest + controls:
        is_control = entry.get("control", "none") != "none"
        row = {
            "row_id": f"{entry.get('snapshot_id', entry.get('repo', ''))}::"
            f"{entry.get('canonical_class', '')}::{entry.get('target', '')}",
            "entry_id": f"{entry.get('repo_name', '')}::{entry.get('canonical_class', '')}::"
            f"{entry.get('target', '')}",
            "repo_name": entry.get("repo_name", entry.get("repo", "").split("__", 1)[0]),
            "seed": entry.get("seed", 0),
            "class": entry.get("canonical_class"),
            "control": entry.get("control", "none"),
            "kind": entry.get("kind"),
            "mutation_form": entry.get("form", "n/a"),
            "doc_path": entry.get("doc_path"),
            "line": entry.get("line"),
            "doc_line_text": _doc_line(
                entry.get("repo_name", entry.get("repo", "").split("__", 1)[0]),
                entry.get("doc_path"),
                entry.get("line"),
            ),
            "target": entry.get("target"),
            "old": entry.get("old"),
            "new": entry.get("new"),
            "symbol": entry.get("symbol"),
            "target_claim": entry.get("target_claim", ""),
            "rationale": entry.get("rationale", ""),
            "is_control": is_control,
        }
        for field in BLANK_FIELDS:
            row[field] = ""
        rows.append(row)

    out = Path(args.out) if args.out else run / "annotation_sheet.jsonl"
    out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    print(f"wrote {len(rows)} annotation rows -> {out}")
    print(f"  injections: {sum(1 for r in rows if not r['is_control'])}")
    print(f"  controls:   {sum(1 for r in rows if r['is_control'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
