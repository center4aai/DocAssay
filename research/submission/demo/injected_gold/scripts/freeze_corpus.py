"""Freeze the Stage B natural corpus (SHA-256, prompts, agents, model IDs).

The freeze is taken **before** any injector or scoring run.  It records:

- the SHA-256 of every corpus file (source, ``pyproject.toml``, ``spec.json``,
  docs, example data), excluding caches and VCS metadata;
- the SHA-256 of every prompt in the run's ``prompts_natural/`` directory;
- the SHA-256 of the agent prompt files that drove the LLM roles;
- the exact model IDs and a SHA-256 of each ID string;
- an aggregate SHA-256 over the sorted ``path:hash`` lines.

``--verify`` recomputes the same values from the recorded paths and exits
non-zero on any difference.  It is the guard against editing a frozen corpus
after looking at a tool result.

Run::

    PYTHONPATH=src uv run python .../scripts/freeze_corpus.py \
        --out .../runs/stage-b-2026-10-20/corpus_freeze.json

    PYTHONPATH=src uv run python .../scripts/freeze_corpus.py \
        --verify --freeze .../runs/stage-b-2026-10-20/corpus_freeze.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INJECTED_GOLD = SCRIPTS.parent
ARTIFACT = INJECTED_GOLD.parent
REPO_ROOT = ARTIFACT.parents[2]
DEFAULT_REPOS_DIR = INJECTED_GOLD / "synthetic-natural"
DEFAULT_AGENTS_DIR = REPO_ROOT / ".opencode" / "agents"
DEFAULT_PROMPTS_DIR = (
    INJECTED_GOLD / "llm_injection" / "runs" / "stage-b-2026-10-20" / "prompts_natural"
)
DEFAULT_MODELS = {
    "architect": "opencode-go/claude-haiku-5-5",
    "docwriter": "opencode-go/claude-haiku-5-5",
    "auditor": "opencode-go/qwen3.8-flash",
    "injector": "opencode-go/deepseek-v4.1-flash",
    "adjudicator": "opencode-go/qwen3.8-flash",
}
AGENT_FILES = (
    "repo-architect.md",
    "repo-docwriter.md",
    "repo-auditor.md",
    "repo-injector.md",
)
SKIP_DIRS = frozenset(
    {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv"}
)
SKIP_SUFFIXES = (".pyc", ".pyo", ".egg-info")
SKIP_NAMES = frozenset({".DS_Store"})


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
        if path.name in SKIP_NAMES:
            continue
        if any(path.name.endswith(suffix) for suffix in SKIP_SUFFIXES):
            continue
        yield path


def _hash_tree(root: Path, key_prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if not root.is_dir():
        return out
    for path in _iter_files(root):
        rel = path.relative_to(root).as_posix()
        out[f"{key_prefix}{rel}"] = _sha256(path)
    return out


def _aggregate(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(f"{rel}:{files[rel]}\n".encode())
    return h.hexdigest()


def _git(*args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _models(arg_models: dict[str, str]) -> dict[str, dict[str, str]]:
    return {
        role: {"id": model_id, "sha256": hashlib.sha256(model_id.encode("utf-8")).hexdigest()}
        for role, model_id in sorted(arg_models.items())
    }


def build(
    repos_dir: Path,
    prompts_dir: Path,
    agents_dir: Path,
    models: dict[str, str],
    corpus_name: str = "synthetic-natural-stage-b-2026-10-20",
    extra_paths: tuple[Path, ...] = (),
) -> dict:
    repos = sorted(p.name for p in repos_dir.iterdir() if p.is_dir()) if repos_dir.is_dir() else []
    files: dict[str, str] = {}
    specs: dict[str, str] = {}
    for repo in repos:
        root = repos_dir / repo
        for path in _iter_files(root):
            rel = path.relative_to(repos_dir).as_posix()
            files[rel] = _sha256(path)
        spec = root / "spec.json"
        if spec.is_file():
            specs[repo] = _sha256(spec)
    prompts = _hash_tree(prompts_dir)
    agents: dict[str, str] = {}
    if agents_dir.is_dir():
        for name in AGENT_FILES:
            path = agents_dir / name
            if path.is_file():
                agents[name] = _sha256(path)
    extra: dict[str, str] = {}
    for path in extra_paths:
        if path.is_file():
            extra[_rel(path)] = _sha256(path)
    return {
        "corpus": corpus_name,
        "frozen_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "branch": _git("branch", "--show-current"),
        "git_commit": _git("rev-parse", "HEAD"),
        "paths": {
            "repos_dir": _rel(repos_dir),
            "prompts_dir": _rel(prompts_dir),
            "agents_dir": _rel(agents_dir),
        },
        "repos": repos,
        "files": dict(sorted(files.items())),
        "specs": dict(sorted(specs.items())),
        "prompts": dict(sorted(prompts.items())),
        "agents": dict(sorted(agents.items())),
        "extra": dict(sorted(extra.items())),
        "models": _models(models),
        "aggregate_sha256": _aggregate(files),
        "extra_aggregate_sha256": _aggregate(extra),
        "note": (
            "Frozen before any injector or scoring run. Baseline findings are "
            "diagnostic, not acceptance criteria; do not edit the corpus to change "
            "them. Verify with --verify."
        ),
    }


def verify(freeze_path: Path) -> int:
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    paths = frozen["paths"]
    repos_dir = REPO_ROOT / paths["repos_dir"]
    prompts_dir = REPO_ROOT / paths["prompts_dir"]
    agents_dir = REPO_ROOT / paths["agents_dir"]
    models = {role: info["id"] for role, info in frozen["models"].items()}
    extra_paths = tuple(REPO_ROOT / rel for rel in frozen.get("extra", {}))
    current = build(
        repos_dir, prompts_dir, agents_dir, models,
        corpus_name=frozen.get("corpus", ""), extra_paths=extra_paths,
    )

    problems: list[str] = []
    for section in ("files", "specs", "prompts", "agents", "extra"):
        old, new = frozen.get(section, {}), current.get(section, {})
        for key in sorted(set(old) | set(new)):
            if old.get(key) != new.get(key):
                problems.append(f"{section}: {key} changed or missing")
    if frozen.get("aggregate_sha256") != current.get("aggregate_sha256"):
        problems.append("aggregate_sha256 changed")
    if frozen.get("extra_aggregate_sha256") != current.get("extra_aggregate_sha256"):
        problems.append("extra_aggregate_sha256 changed")
    if frozen.get("models") != current.get("models"):
        problems.append("models changed")

    if problems:
        print("FREEZE VERIFY FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"FREEZE VERIFY OK: {freeze_path} ({len(frozen.get('files', {}))} corpus files)")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repos-dir", default=str(DEFAULT_REPOS_DIR))
    ap.add_argument("--prompts-dir", default=str(DEFAULT_PROMPTS_DIR))
    ap.add_argument("--agents-dir", default=str(DEFAULT_AGENTS_DIR))
    ap.add_argument("--out", default="", help="write the freeze JSON here")
    ap.add_argument("--verify", action="store_true", help="verify an existing freeze")
    ap.add_argument("--freeze", default="", help="freeze JSON to verify")
    ap.add_argument("--corpus-name", default="synthetic-natural-stage-b-2026-10-20")
    ap.add_argument(
        "--extra",
        action="append",
        default=[],
        help="additional frozen artifact (repeatable): taxonomy, design, audit, controls, reports",
    )
    for role, model_id in DEFAULT_MODELS.items():
        ap.add_argument(f"--model-{role}", default=model_id)
    args = ap.parse_args(argv)

    if args.verify:
        if not args.freeze:
            ap.error("--verify needs --freeze")
        return verify(Path(args.freeze))

    if not args.out:
        ap.error("--out is required unless --verify is used")
    models = {role: getattr(args, f"model_{role}") for role in DEFAULT_MODELS}
    payload = build(
        Path(args.repos_dir),
        Path(args.prompts_dir),
        Path(args.agents_dir),
        models,
        corpus_name=args.corpus_name,
        extra_paths=tuple(Path(p) for p in args.extra),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"froze {len(payload['files'])} files, {len(payload['prompts'])} prompts, "
        f"{len(payload['agents'])} agents -> {out}"
    )
    print(f"  aggregate_sha256: {payload['aggregate_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
