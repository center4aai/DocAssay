"""Git-tracked file listing.

The structure and documentation inventories are "closed over the tracked
repository snapshot": when the tree is a git checkout, the authoritative file
set is ``git ls-files``, not an os.walk over the working tree. A working-tree
walk picks up untracked files (the tool's own ``.docassay_cache/``, build
scratch) and — worse — applies the ``SKIPPED_DIRS`` union to the *documentation*
walk, which dropped real docs under ``doc/build/`` (sqlalchemy) and ``sites/``
(paramiko).

So: with ``.git`` present, the file set is the tracked set; ``SKIPPED_DIRS``
remains only as the guard for git-less trees (where a walk cannot be filtered
to a snapshot and the gitignore-union is the only protection).
"""

from __future__ import annotations

import functools
import subprocess
from pathlib import Path


@functools.lru_cache(maxsize=64)
def _git_tracked(root: Path) -> tuple[str, ...] | None:
    """Every tracked file path (POSIX, relative) under ``root``, or ``None``.

    ``None`` when the directory is not a git checkout (no ``.git``) or git is
    unavailable — the caller then falls back to the working-tree walk.
    """
    if not (root / ".git").exists():
        return None
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return tuple(p for p in out.stdout.decode("utf-8", errors="replace").split("\0") if p)


def git_tracked_files(project_root: Path) -> frozenset[str] | None:
    """Tracked file paths under ``project_root`` as a frozenset, or ``None``."""
    tracked = _git_tracked(Path(project_root))
    if tracked is None:
        return None
    return frozenset(tracked)


def tracked_dir_prefixes(tracked: frozenset[str]) -> frozenset[str]:
    """Every directory implied by a tracked file set (trailing ``/`` keys)."""
    dirs: set[str] = set()
    for rel in tracked:
        head = rel
        while "/" in head:
            head, _, _tail = head.rpartition("/")
            dirs.add(head + "/")
    return frozenset(dirs)


@functools.lru_cache(maxsize=64)
def _tracked_dir_prefixes(root: Path) -> frozenset[str] | None:
    tracked = git_tracked_files(root)
    if tracked is None:
        return None
    return tracked_dir_prefixes(tracked)


def clear_listing_cache() -> None:
    """Forget cached listings, so the next analysis reads the checkout afresh.

    The listing is cached per root for the many walks of one analysis; a
    long-lived process (the web UI) re-analyzes a clone updated in place under
    the same root and must not reuse the previous snapshot.
    """
    _git_tracked.cache_clear()
    _tracked_dir_prefixes.cache_clear()


def tracked_subdirs(project_root: Path, dirpath: Path, dirnames: list[str]) -> list[str] | None:
    """The subdirectories to descend into, when ``project_root`` is a git tree.

    With ``.git`` present the authoritative walk set is the tracked snapshot:
    a directory holding no tracked file is pruned (it is build scratch or the
    tool's own cache), while real tracked source under a gitignore-named
    directory (``src/poetry/utils/env/``) is kept. Returns ``None`` for a
    git-less tree, where the caller falls back to the ``SKIPPED_DIRS`` union.
    Hidden directories are always pruned.
    """
    prefixes = _tracked_dir_prefixes(Path(project_root))
    if prefixes is None:
        return None
    root = Path(project_root)
    kept: list[str] = []
    for name in dirnames:
        if name.startswith("."):
            continue
        rel = (dirpath / name).relative_to(root).as_posix() + "/"
        if rel in prefixes:
            kept.append(name)
    return sorted(kept)
