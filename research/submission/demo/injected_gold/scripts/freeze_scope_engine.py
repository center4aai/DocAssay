"""Freeze (and verify) the Stage C scope, engine, prompts, and analysis code (S0).

The Stage C preregistration requires a **scope/engine freeze before any spec is
written** (``validation/stage-c-plan.md`` §4.1). This file records SHA-256 for:

- scope and protocol: ``validation/SCOPE.md`` (with the C-ext §3.3.2 amendment),
  ``validation/protocol.md`` (with the C11 bootstrap amendment), and the plan;
- engine code: the ``src/docassay`` **git tree** object plus a SHA-256 of
  every ``.py`` file under it;
- engine data and vocabulary: ``data/**/*.json`` and ``vocabularies/**/*.py``;
- tool environment: ``pyproject.toml``, ``uv.lock``, ``.python-version`` if
  present, and the interpreter version string;
- engine-free verifier/materialiser: ``engine/oracle.py``, ``engine/grammar.py``,
  ``scripts/generate_synthetic.py``, ``scripts/_corpus.py``;
- injector harness and judges;
- freeze tooling (including this file);
- Stage C prompts (``runs/stage-c-<date>/prompts_natural_c/``);
- model IDs for every role, plus a SHA-256 of each ID string;
- annotation codebook and the engine-free classifier;
- corpus design: ``taxonomy.json`` and ``corpus_design.json``;
- analysis code: scorer, Stage C metrics, bootstrap, control selector,
  annotation-sheet builder, control config, judge rubric, checkers;
- an aggregate SHA-256 over sorted ``group/path:hash`` lines.

``--verify`` recomputes everything and exits non-zero on any difference. The
engine **tree** hash is the binding engine check: research-only commits may
advance ``HEAD`` after the freeze, but any change under ``src/docassay``
invalidates it. The recorded ``git_commit`` is provenance.

Run::

    PYTHONPATH=src uv run python .../scripts/freeze_scope_engine.py \
        --out .../runs/stage-c-2026-10-20/scope_engine_freeze.json

    PYTHONPATH=src uv run python .../scripts/freeze_scope_engine.py \
        --verify --freeze .../runs/stage-c-2026-10-20/scope_engine_freeze.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INJECTED_GOLD = SCRIPTS.parent
ARTIFACT = INJECTED_GOLD.parent
REPO_ROOT = ARTIFACT.parents[2]
RUN_DIR = INJECTED_GOLD / "llm_injection" / "runs" / "stage-c-2026-10-20"

SKIP_DIRS = frozenset({".git", "__pycache__", ".pytest_cache", ".mypy_cache",
                       ".ruff_cache", ".venv"})
SKIP_SUFFIXES = (".pyc", ".pyo")
SKIP_NAMES = frozenset({".DS_Store"})

GROUP_PATTERNS: dict[str, tuple[str, ...]] = {
    "scope_protocol": (
        "research/submission/demo/validation/SCOPE.md",
        "research/submission/demo/validation/protocol.md",
        "research/submission/demo/validation/stage-c-plan.md",
    ),
    "engine_code": ("src/docassay/**/*.py",),
    "engine_data": (
        "src/docassay/data/**/*.json",
        "src/docassay/vocabularies/**/*.py",
    ),
    "environment": (
        "pyproject.toml",
        "uv.lock",
        ".python-version",
    ),
    "engine_free": (
        "research/submission/demo/injected_gold/engine/*.py",
        "research/submission/demo/injected_gold/scripts/generate_synthetic.py",
        "research/submission/demo/injected_gold/scripts/_corpus.py",
    ),
    "injector_harness": (
        "research/submission/demo/injected_gold/llm_injection/scripts/*.py",
        "research/submission/demo/injected_gold/scripts/judge_*.py",
    ),
    "freeze_tooling": (
        "research/submission/demo/injected_gold/scripts/freeze_corpus.py",
        "research/submission/demo/injected_gold/scripts/freeze_scope_engine.py",
    ),
    "prompts": (
        "research/submission/demo/injected_gold/llm_injection/runs/"
        "stage-c-2026-10-20/prompts_natural_c/**/*",
    ),
    "annotation": (
        "research/submission/demo/injected_gold/llm_injection/runs/"
        "stage-c-2026-10-20/annotation_codebook.md",
        "research/submission/demo/injected_gold/llm_injection/runs/"
        "stage-c-2026-10-20/annotation_instructions.md",
        "research/submission/demo/injected_gold/scripts/classify_claim_context.py",
    ),
    "agents": (
        ".opencode/agents/repo-architect.md",
        ".opencode/agents/repo-docwriter.md",
        ".opencode/agents/repo-auditor.md",
        ".opencode/agents/repo-injector.md",
    ),
    "corpus_design": (
        "research/submission/demo/injected_gold/llm_injection/runs/"
        "stage-c-2026-10-20/taxonomy.json",
        "research/submission/demo/injected_gold/llm_injection/runs/"
        "stage-c-2026-10-20/corpus_design.json",
    ),
    "analysis": (
        "research/submission/demo/injected_gold/scripts/score_injections.py",
        "research/submission/demo/injected_gold/scripts/stage_c_metrics.py",
        "research/submission/demo/injected_gold/scripts/bootstrap_repo_cluster.py",
        "research/submission/demo/injected_gold/scripts/build_controls.py",
        "research/submission/demo/injected_gold/scripts/build_annotation_sheet.py",
        "research/submission/demo/injected_gold/scripts/annotation_agreement.py",
        "research/submission/demo/injected_gold/scripts/check_corpus_surface.py",
        "research/submission/demo/injected_gold/scripts/check_genres.py",
        "research/submission/demo/injected_gold/scripts/check_contamination.py",
        "research/submission/demo/injected_gold/llm_injection/runs/"
        "stage-c-2026-10-20/control_config.json",
        "research/submission/demo/injected_gold/llm_injection/runs/"
        "stage-c-2026-10-20/judge_rubric.md",
    ),
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def _iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_NAMES or path.name.endswith(SKIP_SUFFIXES):
            continue
        yield path


def _group_files(patterns: tuple[str, ...]) -> dict[str, str]:
    out: dict[str, str] = {}
    for pattern in patterns:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if path.is_file() and path.resolve().is_relative_to(REPO_ROOT):
                out[_rel(path)] = _sha256(path)
    return dict(sorted(out.items()))


def _git(*args: str) -> str | None:
    try:
        proc = subprocess.run(["git", *args], cwd=str(REPO_ROOT),
                              capture_output=True, text=True, check=False)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _models(run_dir: Path) -> dict[str, dict[str, str]]:
    design = json.loads((run_dir / "corpus_design.json").read_text(encoding="utf-8"))
    return {
        role: {"id": model_id,
               "sha256": hashlib.sha256(model_id.encode("utf-8")).hexdigest()}
        for role, model_id in sorted(design["models"].items())
    }


def _aggregate(groups: dict[str, dict[str, str]]) -> str:
    h = hashlib.sha256()
    for group in sorted(groups):
        for path in sorted(groups[group]):
            h.update(f"{group}/{path}:{groups[group][path]}\n".encode())
    return h.hexdigest()


def build(run_dir: Path) -> dict:
    groups = {name: _group_files(patterns) for name, patterns in GROUP_PATTERNS.items()}
    design = json.loads((run_dir / "corpus_design.json").read_text(encoding="utf-8"))
    return {
        "stage": "C",
        "arm": design["arm"],
        "frozen_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "branch": _git("branch", "--show-current"),
        "git_commit": _git("rev-parse", "HEAD"),
        "engine_tree_sha": _git("rev-parse", "HEAD:src/docassay"),
        "python_version": platform.python_version(),
        "files": groups,
        "counts": {name: len(files) for name, files in groups.items()},
        "models": _models(run_dir),
        "bootstrap_seed": design["seed"],
        "aggregate_sha256": _aggregate(groups),
        "verification_points": [
            "before S1",
            "before the injector run",
            "before scoring",
            "after scoring",
        ],
        "note": (
            "Scope/engine freeze taken before any Stage C spec is written. The "
            "engine tree hash is binding; research-only commits may advance HEAD. "
            "Verify with --verify at the four recorded points."
        ),
    }


def verify(freeze_path: Path) -> int:
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    current = build(RUN_DIR)
    problems: list[str] = []
    for group in sorted(set(frozen["files"]) | set(current["files"])):
        old, new = frozen["files"].get(group, {}), current["files"].get(group, {})
        for path in sorted(set(old) | set(new)):
            if old.get(path) != new.get(path):
                problems.append(f"{group}: {path} changed or missing")
    if frozen.get("aggregate_sha256") != current.get("aggregate_sha256"):
        problems.append("aggregate_sha256 changed")
    if frozen.get("models") != current.get("models"):
        problems.append("models changed")
    if frozen.get("engine_tree_sha") != current.get("engine_tree_sha"):
        problems.append("engine tree changed (src/docassay)")
    status = _git("status", "--porcelain", "--", "src", "pyproject.toml", "uv.lock")
    if status:
        problems.append("engine tree is dirty: " + status.replace("\n", "; "))

    if problems:
        print("SCOPE/ENGINE FREEZE VERIFY FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    total = sum(len(files) for files in frozen["files"].values())
    print(f"SCOPE/ENGINE FREEZE VERIFY OK: {freeze_path} "
          f"({total} files, engine tree {frozen.get('engine_tree_sha')})")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="", help="write the freeze JSON here")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--freeze", default="")
    ap.add_argument("--run", default=str(RUN_DIR))
    args = ap.parse_args(argv)
    run_dir = Path(args.run).resolve()
    if args.verify:
        freeze = Path(args.freeze or run_dir / "scope_engine_freeze.json")
        return verify(freeze)
    if not args.out:
        ap.error("--out is required unless --verify")
    data = build(run_dir)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    total = sum(len(files) for files in data["files"].values())
    print(f"WROTE {out} ({total} files, aggregate {data['aggregate_sha256'][:12]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
