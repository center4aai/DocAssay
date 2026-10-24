"""Attribute every REFUTED finding to the git history that explains it.

For each REFUTED claim we ask the repository's own history whether the artifact
ever existed and, if it did, which commit removed or renamed it. This turns a
bare "path is absent" verdict into an auditable chain:

    docs/CONTRIBUTING.rst:1180 cites docs/configuration.rst
    -> file existed until commit abc123 (2025-11-03, "move docs/")
    -> the citing line was last edited in commit def456 (2021-06-01)

Classes:

    EXISTED_AND_DELETED   the artifact existed, then a commit deleted it
    EXISTED_AND_RENAMED   the artifact existed, then a commit renamed/moved it
    NEVER_EXISTED         no commit ever contained it (example/tutorial path)
    PRESENT_NOW           it is in the tree (the predicate's own mismatch)
    CASE_VARIANT          present with different letter case (normalization bug)
    UNKNOWN               history lookup not conclusive (symbols, deps)

Usage::

    PYTHONPATH=src uv run python .../real_world/scripts/attribute_staleness.py
    PYTHONPATH=src uv run python .../real_world/scripts/attribute_staleness.py --only celery
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REAL_WORLD = SCRIPTS.parent
REPOS_DIR = REAL_WORLD / "repos"
RUNS = REAL_WORLD / "runs"

_COMMIT_RE = re.compile(r"^@@([0-9a-f]{7,40})\|([^|]*)\|(.*)$")


def git(repo: Path, *args: str, timeout: int = 120) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=False, timeout=timeout
    )
    return proc.stdout if proc.returncode == 0 else ""


def load_findings(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def head_files(repo: Path) -> dict[str, str]:
    """Lower-cased path -> real path for every tracked file at HEAD."""
    files = git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    return {f.lower(): f for f in files if f}


def path_events(repo: Path, path: str) -> list[dict]:
    """Deletion/rename events for ``path``, newest first."""
    out = git(
        repo,
        "log",
        "--all",
        "-M",
        "--diff-filter=DR",
        "--name-status",
        "--format=@@%H|%cI|%s",
        "--",
        path,
    )
    events: list[dict] = []
    current: dict | None = None
    for line in out.splitlines():
        m = _COMMIT_RE.match(line)
        if m:
            current = {"sha": m.group(1), "date": m.group(2), "subject": m.group(3)}
            continue
        if current is None or not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("D") and parts[-1].rstrip("/") == path.rstrip("/"):
            events.append({**current, "kind": "deleted", "target": None})
        elif status.startswith("R") and len(parts) >= 3 and parts[1] == path:
            events.append({**current, "kind": "renamed", "target": parts[2]})
    return events


def blame_line(repo: Path, source: str, line: int) -> dict | None:
    out = git(repo, "blame", "-L", f"{line},{line}", "--porcelain", "--", source, timeout=180)
    if not out:
        return None
    first = out.splitlines()[0] if out else ""
    parts = first.split()
    if len(parts) < 2:
        return None
    sha = parts[0]
    meta = {"sha": sha}
    for entry in out.splitlines()[1:]:
        if entry.startswith("author-time "):
            meta["author_time"] = int(entry.split()[1])
        elif entry.startswith("committer-time "):
            meta["commit_time"] = int(entry.split()[1])
        elif entry.startswith("summary "):
            meta["subject"] = entry[len("summary ") :]
    meta["date"] = date.fromtimestamp(meta.get("commit_time", 0)).isoformat()
    return meta


def attribute_path(repo: Path, finding: dict, files_lower: dict[str, str]) -> dict:
    raw = finding["object"]
    path = raw.rstrip("/")
    if not path:
        return {"status": "UNKNOWN", "detail": "empty path"}
    if path in files_lower.values():
        return {"status": "PRESENT_NOW"}
    variant = files_lower.get(path.lower())
    if variant is not None:
        return {"status": "CASE_VARIANT", "case_variant": variant}

    events = path_events(repo, path)
    if not events:
        return {"status": "NEVER_EXISTED"}
    newest = events[0]
    return {
        "status": "EXISTED_AND_DELETED" if newest["kind"] == "deleted" else "EXISTED_AND_RENAMED",
        "removed_at": newest["sha"],
        "removed_date": newest["date"],
        "removed_subject": newest["subject"],
        "renamed_to": newest.get("target"),
        "events": len(events),
    }


def module_candidates(dotted: str) -> list[str]:
    parts = dotted.split(".")
    out = []
    for i in range(len(parts), 0, -1):
        base = "/".join(parts[:i])
        out.extend([f"{base}.py", f"{base}/__init__.py"])
    return out


def attribute_symbol(repo: Path, finding: dict, files_lower: dict[str, str]) -> dict:
    dotted = finding["object"]
    candidates = module_candidates(dotted)
    present = [c for c in candidates if c.lower() in files_lower]
    if present:
        module = present[0]  # deepest (longest dotted prefix) existing module
        symbol = dotted.split(".")[-1]
        text = (repo / module).read_text(encoding="utf-8", errors="ignore")
        if re.search(rf"(^|[^A-Za-z0-9_]){re.escape(symbol)}([^A-Za-z0-9_]|$)", text):
            return {"status": "PRESENT_NOW", "module": module}
        # The module survives but the symbol does not. A pickaxe (``git log
        # -S``) needs blob content and is prohibitively slow on a lazy clone,
        # so record the last commit that touched the module instead: triage
        # digs deeper on the shortlist with a targeted pickaxe.
        scope = module.rsplit("/", 1)[0] if module.endswith("__init__.py") else module
        last = git(repo, "log", "--all", "-1", "--format=@@%H|%cI|%s", "--", scope)
        record = {"status": "MODULE_PRESENT", "module": module}
        m = _COMMIT_RE.match(last.strip())
        if m:
            record["module_last_change"] = {
                "sha": m.group(1),
                "date": m.group(2),
                "subject": m.group(3),
            }
        return record
    # The module is gone: find the commit that deleted the deepest candidate.
    for cand in candidates:
        events = path_events(repo, cand)
        if events:
            newest = events[0]
            return {
                "status": "EXISTED_AND_DELETED"
                if newest["kind"] == "deleted"
                else "EXISTED_AND_RENAMED",
                "module": cand,
                "removed_at": newest["sha"],
                "removed_date": newest["date"],
                "removed_subject": newest["subject"],
                "renamed_to": newest.get("target"),
            }
    return {"status": "NEVER_EXISTED"}


def attribute(repo: Path, finding: dict, files_lower: dict[str, str]) -> dict:
    pred = finding["predicate"]
    if pred == "PATH_EXISTS":
        return attribute_path(repo, finding, files_lower)
    if pred == "SYMBOL_EXISTS":
        return attribute_symbol(repo, finding, files_lower)
    if pred == "DEPENDENCY":
        return attribute_dependency(repo, finding)
    return {"status": "UNKNOWN", "detail": f"no attributor for {pred}"}


_MANIFESTS = ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "tox.ini")


def attribute_dependency(repo: Path, finding: dict) -> dict:
    name = finding["object"].strip().lower()
    declaring = [m for m in _MANIFESTS if (repo / m).exists()]
    if declaring:
        for manifest in declaring:
            text = (repo / manifest).read_text(encoding="utf-8", errors="ignore").lower()
            if re.search(rf"(^|[^a-z0-9_.-]){re.escape(name)}([^a-z0-9_.-]|$)", text):
                return {"status": "PRESENT_NOW", "module": manifest}
    for manifest in declaring:
        out = git(
            repo, "log", "--all", "-i", "-S", name, "--format=@@%H|%cI|%s", "--", manifest
        )
        for line in out.splitlines():
            m = _COMMIT_RE.match(line)
            if m:
                return {
                    "status": "EXISTED_AND_DELETED",
                    "module": manifest,
                    "removed_at": m.group(1),
                    "removed_date": m.group(2),
                    "removed_subject": m.group(3),
                }
    return {"status": "NEVER_EXISTED"}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--only", default="")
    args = parser.parse_args(argv)

    run_dir = RUNS / args.date
    only = {n.strip() for n in args.only.split(",") if n.strip()}

    totals: dict[str, int] = defaultdict(int)
    for findings_path in sorted(run_dir.glob("*/findings.jsonl")):
        name = findings_path.parent.name
        if only and name not in only:
            continue
        repo = REPOS_DIR / name
        findings = [f for f in load_findings(findings_path) if f["verdict"] == "REFUTED"]
        files_lower = head_files(repo)
        rows = []
        for finding in findings:
            result = {"finding_id": finding["finding_id"], **finding}
            result["staleness"] = attribute(repo, finding, files_lower)
            st = result["staleness"]["status"]
            if st in {"EXISTED_AND_DELETED", "EXISTED_AND_RENAMED"}:
                blame = blame_line(repo, finding["primary_source"], finding["primary_line_start"])
                if blame:
                    result["staleness"]["claim_line"] = blame
            totals[st] += 1
            rows.append(result)
        out = findings_path.parent / "staleness.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        local = defaultdict(int)
        for row in rows:
            local[row["staleness"]["status"]] += 1
        print(f"{name:12s} {len(rows):4d} refuted  {dict(sorted(local.items()))}")

    print("\ncorpus totals:", dict(sorted(totals.items())))
    (run_dir / "staleness_totals.json").write_text(
        json.dumps(dict(sorted(totals.items())), indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
