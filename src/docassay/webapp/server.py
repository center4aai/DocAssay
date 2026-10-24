"""FastAPI app serving analysis bundles over HTTP (web extra).

Every repository is exposed as a JSON bundle produced by the core CLI export
(Mode A): the frontend consumes bundles as data. Repositories come from three
sources:

- **path** — ``POST /api/repos/analyze`` with a local directory;
- **upload** — ``POST /api/repos/upload`` with a zip archive;
- **clone** — ``POST /api/repos/clone`` with a git URL, downloaded into the
  server-owned ``workdir/repos/clones/`` tree;
- **corpus** — directories discovered under ``corpus_dir`` (default
  ``./test_repos``), listed as available before they are analyzed.

Bundles are cached in a server-side workdir (never inside the analyzed tree, so
the PATH_EXISTS listing is not polluted). The provenance viewer reads source
files through ``/api/repos/{id}/file`` which is confined to the repo root.
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import logging
import os
import re
import secrets
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles

from docassay.core.bundle import TOOL_VERSION, to_bundle, to_markdown
from docassay.core.pipeline import analyze_repository, find_project_root
from docassay.evidence.git import clear_listing_cache
from docassay.evidence.symbols import symbols_cached
from docassay.webapp.zip_safe import UnsafeArchiveError, extract_zip

log = logging.getLogger("docassay.webapp")

_MAX_UPLOAD_BYTES = 150 * 1024 * 1024
_MAX_FILE_LINES = 500
_CLONE_TIMEOUT_S = 600


def _emit_progress(
    kind: str,
    message: str,
    percent: int | None = None,
    duration_ms: int | None = None,
) -> None:
    """Stream one progress frame to the connected SSE client.

    Assigned to a thread-local sink by ``_analyze_stream``; when the request is
    not a streamed analysis the sink is a no-op, so progress is simply dropped.
    ``percent`` (0-100) is optional and only set by coarse-grained stages such
    as the git clone, letting the frontend render a bar. ``duration_ms`` is set
    on the synthetic ``timing`` frames that close a phase (clone / extract /
    analyze) so the frontend can show how long each phase took.
    """
    sink = getattr(_STATE, "sink", None)
    if sink is not None:
        sink(kind, message, percent, duration_ms)


def _noop_progress(*_args: object, **_kwargs: object) -> None:
    """Progress sink used when a non-streamed request runs a prelude."""


class _StreamState(threading.local):
    sink: Callable[..., None] | None = None


_STATE = _StreamState()


class CloneError(ValueError):
    """A repository URL could not be validated or cloned."""


def _validate_git_url(raw: str) -> str | None:
    """Return an error message for a bad git URL, or ``None`` if it is acceptable.

    Accepts only ``https://`` URLs: ``ssh://``, ``git://``, ``http://``,
    ``file://``, scp-style ``user@host:path`` forms, plain local paths and
    empty strings are rejected. ``git`` itself is additionally restricted to
    the https transport (``_GIT_HTTPS_ONLY``), so a redirect or a submodule
    cannot switch protocols.
    """
    url = raw.strip()
    if not url:
        return "repository URL is required"
    if "://" not in url:
        return "repository URL must start with https://"
    scheme, rest = url.split("://", 1)
    if scheme.lower() != "https":
        return f"unsupported URL scheme: {scheme.lower()!r} (only https is accepted)"
    if not rest or rest.startswith("/"):
        return "invalid repository URL"
    return None


# Every git network command the server runs is limited to https.
_GIT_HTTPS_ONLY = ("-c", "protocol.allow=never", "-c", "protocol.https.allow=always")


# Approximate mapping of git's clone phases onto one 0-100 bar. Git reports
# progress per phase, each restarting at 0%, so the receiving phase — which
# dominates wall-clock for a link download — is given the widest band.
_CLONE_PHASE_BANDS: dict[str, tuple[int, int]] = {
    "enumerating objects": (0, 2),
    "counting objects": (2, 5),
    "compressing objects": (5, 10),
    "receiving objects": (10, 90),
    "resolving deltas": (90, 100),
}
_CLONE_PHASE_RE = re.compile(
    r"(?P<phase>Enumerating objects|Counting objects|Compressing objects|"
    r"Receiving objects|Resolving deltas):\s+(?P<pct>\d+)%"
)


def _clone_progress(line: str, on_progress: Callable[..., None], state: dict) -> None:
    """Map one line of ``git clone --progress`` stderr onto an overall percent."""
    match = _CLONE_PHASE_RE.search(line.removeprefix("remote: ").strip())
    if match is None:
        return
    phase = match.group("phase").lower()
    lo, hi = _CLONE_PHASE_BANDS.get(phase, (0, 100))
    overall = int(lo + (hi - lo) * int(match.group("pct")) / 100)
    if overall <= state["percent"]:
        return
    state["percent"] = overall
    on_progress("clone", f"{phase} {match.group('pct')}%", percent=overall)


def _run_git_clone(
    url: str, dest: Path, on_progress: Callable[..., None], *, depth: int | None
) -> None:
    """Run ``git clone``, reading stderr incrementally to stream phase progress.

    ``git`` writes progress to stderr and separates updates with ``\\r`` when
    stderr is not a tty, so raw chunks are split on both ``\\r`` and ``\\n``
    instead of using line-buffered reads (which would stall until EOF).
    """
    args = ["git", *_GIT_HTTPS_ONLY, "clone", "--progress"]
    if depth is not None:
        args += ["--depth", str(depth)]
    args += ["--", url, str(dest)]
    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        bufsize=0,
    )
    assert proc.stderr is not None
    state = {"percent": -1}
    buf = ""
    deadline = time.monotonic() + _CLONE_TIMEOUT_S
    while True:
        chunk = proc.stderr.read(512)
        if not chunk:
            break
        if time.monotonic() > deadline:
            proc.kill()
            proc.wait()
            raise CloneError(f"git clone timed out after {_CLONE_TIMEOUT_S}s")
        buf += chunk.decode("utf-8", "replace")
        *lines, buf = re.split(r"[\r\n]", buf)
        for line in lines:
            if line:
                _clone_progress(line, on_progress, state)
    proc.wait()
    if proc.returncode != 0:
        raise CloneError(f"git clone exited with status {proc.returncode}")


def _clone_repository(url: str, dest: Path, on_progress: Callable[..., None] | None = None) -> None:
    """Clone ``url`` into ``dest`` (shallow, full clone as fallback)."""
    error = _validate_git_url(url)
    if error is not None:
        raise CloneError(error)
    emit = on_progress or _noop_progress
    dest.mkdir(parents=True, exist_ok=True)
    try:
        try:
            _run_git_clone(url, dest, emit, depth=1)
        except CloneError:
            # A shallow clone fails for some servers; retry as a full clone.
            shutil.rmtree(dest, ignore_errors=True)
            dest.mkdir(parents=True, exist_ok=True)
            _run_git_clone(url, dest, emit, depth=None)
    except (CloneError, subprocess.SubprocessError, OSError) as exc:
        shutil.rmtree(dest, ignore_errors=True)
        raise CloneError(f"could not clone {url!r}: {exc}") from exc


def _run_git(*args: str, cwd: Path | None = None) -> None:
    """Run one git command, raising ``CloneError`` with its stderr on failure."""
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_CLONE_TIMEOUT_S,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise CloneError(f"git failed: {detail[:400]}")


def _refresh_clone_repository(
    url: str, dest: Path, on_progress: Callable[..., None] | None = None
) -> None:
    """Update an existing clone in place instead of downloading it again.

    ``git fetch --depth 1`` pulls only the new commits and ``reset --hard``
    moves the worktree to the fetched head, so re-analyzing a URL already in the
    workdir costs a delta download rather than a fresh full clone. A failed
    refresh (offline, force-pushed history) is non-fatal: the existing tree is
    kept and analyzed as-is.
    """
    emit = on_progress or _noop_progress
    emit("cmd", f"git fetch --depth 1 origin ({dest.name})")
    try:
        _run_git(*_GIT_HTTPS_ONLY, "fetch", "--depth", "1", "origin", cwd=dest)
        _run_git("reset", "--hard", "FETCH_HEAD", cwd=dest)
    except (CloneError, subprocess.SubprocessError, OSError) as exc:
        emit("info", f"refresh skipped, using the existing checkout: {exc}")
        return
    emit("ok", "existing clone refreshed from origin")


def _normalize_repo_url(url: str) -> str:
    """Canonical form used to recognize the same remote across clone requests.

    Drops a trailing ``/`` and ``.git`` and case-folds, so
    ``https://github.com/pandas-dev/pandas.git`` and ``.../pandas`` match. It is
    deliberately scheme-agnostic only for the common forms; ssh/https spellings
    of one repository are treated as distinct (they may point at different
    forks) rather than risking a wrong reuse.
    """
    text = url.strip()
    if text.lower().endswith(".git"):
        text = text[:-4]
    return text.rstrip("/").lower()


def _dir_size(path: Path) -> int:
    """Total size in bytes of a directory tree (0 when unreadable)."""
    total = 0
    for item in path.rglob("*"):
        try:
            if item.is_file():
                total += item.stat().st_size
        except OSError:
            continue
    return total


def _slug(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return slug or "repo"


def _repo_id(name: str, root: Path) -> str:
    digest = hashlib.sha1(str(root.resolve()).encode()).hexdigest()[:10]
    return f"{_slug(name)}-{digest}"


# The three id shapes the server mints: ``_repo_id`` (``<slug>-<10 hex>``),
# uploads (``<slug>-up<8 hex>``) and clones (``<slug>-cl<8 hex>``). Anything
# else in a URL path is rejected before it can name a file.
_REPO_ID_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*-(?:[0-9a-f]{10}|(?:up|cl)[0-9a-f]{8})")


def is_valid_repo_id(repo_id: str) -> bool:
    """Whether ``repo_id`` has one of the shapes the server mints."""
    return bool(_REPO_ID_RE.fullmatch(repo_id))


class RepoStore:
    """Manifests + cached bundles + uploads under one workdir."""

    def __init__(self, workdir: Path):
        self.workdir = workdir
        self.repos_dir = workdir / "repos"
        self.bundles_dir = workdir / "bundles"
        self.logs_dir = workdir / "logs"
        self.uploads_dir = workdir / "uploads"
        self.clones_dir = self.repos_dir / "clones"
        self._active: dict[str, int] = {}
        self._active_lock = threading.Lock()
        for d in (
            self.repos_dir,
            self.bundles_dir,
            self.logs_dir,
            self.uploads_dir,
            self.clones_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _inside(directory: Path, name: str) -> Path:
        """``directory / name``, refusing a name that is not a server id."""
        if not is_valid_repo_id(name):
            raise ValueError(f"invalid repository id: {name!r}")
        path = directory / name
        if path.resolve().parent != directory.resolve():
            raise ValueError(f"repository id escapes its directory: {name!r}")
        return path

    def manifest_path(self, repo_id: str) -> Path:
        return self._inside(self.repos_dir, repo_id).with_name(f"{repo_id}.json")

    def bundle_path(self, repo_id: str) -> Path:
        return self._inside(self.bundles_dir, repo_id).with_name(f"{repo_id}.json")

    def log_path(self, repo_id: str) -> Path:
        return self._inside(self.logs_dir, repo_id).with_name(f"{repo_id}.json")

    def upload_dir(self, repo_id: str) -> Path:
        return self._inside(self.uploads_dir, repo_id)

    def clone_dir(self, repo_id: str) -> Path:
        return self._inside(self.clones_dir, repo_id)

    # Ids whose clone/upload/analysis is still running: their source tree has
    # no manifest yet, so ``prune_sources`` must not treat it as an orphan.
    def mark_active(self, repo_id: str) -> None:
        with self._active_lock:
            self._active[repo_id] = self._active.get(repo_id, 0) + 1

    def release_active(self, repo_id: str) -> None:
        with self._active_lock:
            count = self._active.get(repo_id, 0) - 1
            if count > 0:
                self._active[repo_id] = count
            else:
                self._active.pop(repo_id, None)

    def active_ids(self) -> frozenset[str]:
        with self._active_lock:
            return frozenset(self._active)

    def load_manifest(self, repo_id: str) -> dict | None:
        path = self.manifest_path(repo_id)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def save_manifest(self, manifest: dict) -> None:
        self.manifest_path(manifest["id"]).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def save_bundle(self, repo_id: str, bundle: dict) -> None:
        self.bundle_path(repo_id).write_text(
            json.dumps(bundle, ensure_ascii=False), encoding="utf-8"
        )

    def load_bundle(self, repo_id: str) -> dict | None:
        path = self.bundle_path(repo_id)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def save_log(self, repo_id: str, lines: list[dict]) -> None:
        """Persist the run's progress log beside the bundle.

        The log is what the web "View logs" button reopens. It is stored
        separately from the bundle (not embedded) so a cached bundle stays
        small, and it survives cache hits, navigation and page reloads.
        """
        self.log_path(repo_id).write_text(
            json.dumps({"lines": lines}, ensure_ascii=False), encoding="utf-8"
        )

    def load_log(self, repo_id: str) -> list[dict] | None:
        path = self.log_path(repo_id)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        lines = data.get("lines") if isinstance(data, dict) else None
        return lines if isinstance(lines, list) else None

    def root_for(self, repo_id: str) -> Path | None:
        manifest = self.load_manifest(repo_id)
        if manifest is None:
            return None
        root = Path(manifest["root"])
        return root if root.is_dir() else None

    def list_manifests(self) -> list[dict]:
        out = []
        for path in sorted(self.repos_dir.glob("*.json")):
            if not is_valid_repo_id(path.stem):
                continue
            manifest = self.load_manifest(path.stem)
            if manifest is not None:
                out.append(manifest)
        return out

    def delete_repo(self, repo_id: str) -> bool:
        """Remove one analysis; upload sources are removed, others kept.

        Returns ``True`` when an analysis was removed. For ``path``/``corpus``
        repositories the source tree is the caller's checkout and is never
        deleted — only the manifest and the cached bundle go away (corpus
        entries reappear as "available"). For ``upload`` repositories the
        extracted tree under ``uploads/`` is a server-owned copy and is removed.
        For ``clone`` repositories the cloned tree under ``repos/clones/`` is a
        server-owned copy and is removed too.
        """
        manifest = self.load_manifest(repo_id)
        removed = False
        if manifest is not None:
            self.manifest_path(repo_id).unlink(missing_ok=True)
            removed = True
            if manifest.get("kind") == "upload":
                shutil.rmtree(self.upload_dir(repo_id), ignore_errors=True)
            elif manifest.get("kind") == "clone":
                shutil.rmtree(self.clone_dir(repo_id), ignore_errors=True)
        self.bundle_path(repo_id).unlink(missing_ok=True)
        self.log_path(repo_id).unlink(missing_ok=True)
        return removed

    def clear_bundles(self) -> int:
        """Drop every cached bundle; manifests stay, repos are re-analyzed on open."""
        removed = 0
        for path in self.bundles_dir.glob("*.json"):
            path.unlink(missing_ok=True)
            removed += 1
        for path in self.logs_dir.glob("*.json"):
            path.unlink(missing_ok=True)
        return removed

    def clear_symbol_caches(self) -> int:
        """Remove the AST inventory cache for analyzed roots.

        Each analyzed repository has a user-cache symbol file keyed by a hash of
        its resolved root (written by ``evidence.symbols``, never inside the
        tree; clearing it forces a fresh AST parse on the next
        analysis. The web workdir itself is never touched.
        """
        from docassay.evidence.symbols import cache_file

        removed = 0
        for manifest in self.list_manifests():
            path = cache_file(Path(manifest["root"]))
            if path.is_file():
                path.unlink(missing_ok=True)
                removed += 1
        return removed

    def find_clone_by_url(self, url: str) -> dict | None:
        """The newest existing clone of ``url``, or ``None``.

        Re-cloning a URL already in the workdir reuses this manifest instead of
        minting a new id and downloading a second copy (REPORT: duplicated
        clones). The newest manifest wins when several already exist.
        """
        target = _normalize_repo_url(url)
        best: dict | None = None
        best_mtime = -1.0
        for manifest in self.list_manifests():
            if manifest.get("kind") != "clone" or not manifest.get("source_url"):
                continue
            if _normalize_repo_url(str(manifest["source_url"])) != target:
                continue
            if not Path(manifest["root"]).is_dir():
                continue
            try:
                mtime = self.manifest_path(manifest["id"]).stat().st_mtime
            except OSError:
                mtime = 0.0
            if mtime > best_mtime:
                best, best_mtime = manifest, mtime
        return best

    def _remove_repo_tree(self, manifest: dict) -> int:
        """Delete one repo's dir/bundle/log; return the bytes it occupied."""
        repo_id = manifest["id"]
        freed = 0
        if manifest.get("kind") == "clone":
            tree = self.clone_dir(repo_id)
        elif manifest.get("kind") == "upload":
            tree = self.upload_dir(repo_id)
        else:
            tree = None
        if tree is not None and tree.is_dir():
            freed += _dir_size(tree)
            shutil.rmtree(tree, ignore_errors=True)
        bundle = self.bundle_path(repo_id)
        if bundle.is_file():
            freed += bundle.stat().st_size
            bundle.unlink(missing_ok=True)
        self.log_path(repo_id).unlink(missing_ok=True)
        self.manifest_path(repo_id).unlink(missing_ok=True)
        return freed

    def prune_sources(self) -> dict:
        """Remove source trees (and their caches) that no manifest references.

        Orphan clones/uploads appear when a clone is interrupted mid-flight or a
        manifest is removed out of band; without this sweep they sit in the
        workdir forever. Corpus/path sources are the caller's own checkouts and
        are never touched.
        """
        manifest_ids = {m["id"] for m in self.list_manifests()} | self.active_ids()
        removed_dirs = 0
        freed = 0
        for directory in (self.clones_dir, self.uploads_dir):
            if not directory.is_dir():
                continue
            for child in directory.iterdir():
                if child.is_dir() and child.name not in manifest_ids:
                    freed += _dir_size(child)
                    shutil.rmtree(child, ignore_errors=True)
                    removed_dirs += 1
        removed_bundles = 0
        for path in list(self.bundles_dir.glob("*.json")):
            if path.stem not in manifest_ids:
                freed += path.stat().st_size
                path.unlink(missing_ok=True)
                removed_bundles += 1
        removed_logs = 0
        for path in list(self.logs_dir.glob("*.json")):
            if path.stem not in manifest_ids:
                freed += path.stat().st_size
                path.unlink(missing_ok=True)
                removed_logs += 1
        return {
            "removed_dirs": removed_dirs,
            "removed_bundles": removed_bundles,
            "removed_logs": removed_logs,
            "freed_bytes": freed,
        }

    def prune_duplicate_clones(self) -> dict:
        """Delete all but the newest clone of each remote URL.

        Repeated "Clone & analyze" of one URL used to leave a full tree, bundle
        and manifest behind every time. This keeps the most recently written
        manifest per normalized URL and removes the older duplicates.
        """
        groups: dict[str, list[dict]] = {}
        active = self.active_ids()
        for manifest in self.list_manifests():
            if manifest.get("kind") != "clone" or not manifest.get("source_url"):
                continue
            if manifest["id"] in active:
                continue
            key = _normalize_repo_url(str(manifest["source_url"]))
            groups.setdefault(key, []).append(manifest)
        removed: list[str] = []
        freed = 0
        for items in groups.values():
            if len(items) < 2:
                continue
            items.sort(
                key=lambda m: (
                    self.manifest_path(m["id"]).stat().st_mtime
                    if self.manifest_path(m["id"]).is_file()
                    else 0.0
                ),
                reverse=True,
            )
            for stale in items[1:]:
                freed += self._remove_repo_tree(stale)
                removed.append(stale["id"])
        return {"removed": sorted(removed), "freed_bytes": freed}


def host_header_values(host: str, port: int, extra: list[str]) -> list[str]:
    """``Host`` header values the server answers when bound to ``host:port``.

    Loopback binds answer the loopback names; any other bind answers its own
    address and the ``--allowed-host`` values. A value without a port also
    admits ``value:port``. The value ``*`` disables the check entirely, for a
    container published on an arbitrary host port; it is never implied.
    """
    names = ["127.0.0.1", "localhost", "[::1]"] if _is_loopback_host(host) else []
    if not _is_loopback_host(host) and host not in ("0.0.0.0", "::"):
        names.append(f"[{host}]" if ":" in host else host)
    for value in extra:
        value = value.strip().lower()
        if value == "*":
            return ["*"]
        if value:
            names.append(value)
    out: list[str] = []
    for name in names:
        out.append(name)
        if not re.search(r":\d+$", name):
            out.append(f"{name}:{port}")
    return out


def _is_loopback_host(host: str) -> bool:
    """Whether ``host`` binds a loopback-only interface.

    ``0.0.0.0`` binds every interface and is reachable from the network, so it
    does NOT count as localhost — local path analysis is disabled on it.
    """
    return host in ("127.0.0.1", "localhost", "::1")


@dataclass(frozen=True, slots=True)
class _AppContext:
    """Immutable settings and storage shared by every route handler."""

    store: RepoStore
    corpus_dir: Path
    allow_root: tuple[Path, ...]
    allow_local_paths: bool
    session_token: str
    host_set: frozenset[str] | None


def _path_allowed(ctx: _AppContext, path: Path) -> bool:
    """Whether a local path may be analyzed by the ``path`` endpoint."""
    resolved = path.resolve()
    if ctx.allow_root:
        return any(resolved.is_relative_to(root.resolve()) for root in ctx.allow_root)
    return ctx.allow_local_paths


def _root_allowed(ctx: _AppContext, root: Path, kind: str) -> bool:
    """Whether a repository root is currently admissible for analysis.

    Server-owned trees (upload/clone/corpus) are always admissible; a
    caller-supplied ``path`` root must pass ``_path_allowed``.
    """
    if kind != "path":
        return True
    return _path_allowed(ctx, root)


def _discover_corpus(ctx: _AppContext) -> list[dict]:
    if not ctx.corpus_dir.is_dir():
        return []
    found: list[dict] = []
    for child in sorted(ctx.corpus_dir.iterdir()):
        if not child.is_dir():
            continue
        root = child / "source"
        root = root if root.is_dir() else child
        name = root.parent.name if root.name == "source" else root.name
        found.append({"id": _repo_id(name, root), "name": name, "root": str(root)})
    return found


def _manifest_record(store: RepoStore, manifest: dict) -> dict:
    bundle = store.load_bundle(manifest["id"])
    return {
        "id": manifest["id"],
        "name": manifest["name"],
        "kind": manifest.get("kind", "path"),
        "source": manifest["root"],
        "url": manifest.get("source_url"),
        "analyzed": bundle is not None,
        "analyzed_at": bundle["meta"]["created"] if bundle else None,
        "meta": bundle["meta"] if bundle else None,
    }


def _check_id(repo_id: str) -> None:
    if not is_valid_repo_id(repo_id):
        raise HTTPException(400, f"invalid repository id: {repo_id!r}")


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _analyze_and_store(
    ctx: _AppContext,
    root: Path,
    name: str,
    kind: str,
    repo_id: str | None = None,
    source_url: str | None = None,
    *,
    stream: bool = False,
    log_lines: list[dict] | None = None,
) -> tuple[dict, dict]:
    if not _root_allowed(ctx, root, kind):
        raise HTTPException(
            403,
            "local path analysis is disabled for this server; "
            "use --allow-root to enable specific roots",
        )
    # Collect the run's progress lines even when nobody is streaming: the
    # web "View logs" button reopens this log on a later (possibly cached)
    # visit. A pre-seeded ``log_lines`` lets the caller prepend prelude
    # frames (e.g. the git clone) that run before the pipeline.
    captured: list[dict] = log_lines if log_lines is not None else []

    def capture(
        kind: str,
        message: str,
        percent: int | None = None,
        duration_ms: int | None = None,
    ) -> None:
        frame: dict = {"kind": kind, "message": message}
        if percent is not None:
            frame["percent"] = percent
        if duration_ms is not None:
            frame["duration_ms"] = duration_ms
        captured.append(frame)
        if stream:
            _emit_progress(kind, message, percent, duration_ms)

    analyze_start = time.perf_counter()
    try:
        result = analyze_repository(root, progress=capture)
    finally:
        # A long-lived server must not keep the inventories and listings of
        # past analyses alive (the next analysis rebuilds what it needs).
        symbols_cached.cache_clear()
        clear_listing_cache()
    # Phase timing frame: the frontend renders it as "Analyze — n s". It is
    # appended before save_log so it persists with the rest of the run log.
    capture(
        "timing",
        "analyze",
        duration_ms=round((time.perf_counter() - analyze_start) * 1000),
    )
    if repo_id is None:
        repo_id = _repo_id(name, root)
    store = ctx.store
    bundle = to_bundle(result, project_name=name)
    store.save_bundle(repo_id, bundle)
    store.save_log(repo_id, captured)
    manifest: dict = {
        "id": repo_id,
        "name": name,
        "kind": kind,
        "root": str(root.resolve()),
    }
    if source_url:
        manifest["source_url"] = source_url
    store.save_manifest(manifest)
    log.info(
        "analyzed %s (id=%s root=%s): %d claims, %d referents, %d evidence, bundle %d bytes",
        name,
        repo_id,
        root,
        len(result.claims),
        len(result.referents),
        len(result.evidence),
        len(json.dumps(bundle)),
    )
    info = {"id": repo_id, "name": name, "kind": kind, "meta": bundle["meta"]}
    if source_url:
        info["url"] = source_url
    return info, bundle


def _analyze_stream(
    ctx: _AppContext,
    root: Path | None,
    name: str,
    kind: str,
    repo_id: str | None,
    source_url: str | None,
    *,
    done_key: str = "repo",
    prelude: Callable[[Callable[..., None]], Path | None] | None = None,
    seed_log: list[dict] | None = None,
    active_id: str | None = None,
) -> StreamingResponse:
    """SSE feed: emit real pipeline progress, then the result payload.

    The analysis runs in a daemon worker thread; every progress callback is
    enqueued as an SSE ``data`` frame and drained by ``gen``. ``prelude``
    runs first in the same thread (e.g. the git clone) and may return the
    resolved project root. Errors are surfaced as ``{"event":"error"}``.
    ``seed_log`` pre-populates the run log with frames produced before the
    stream existed (e.g. upload extraction timing); they are both persisted
    and re-emitted to the live stream.
    """
    import queue

    q: queue.Queue[str | None] = queue.Queue()
    # Prelude frames (the git clone) are emitted before the pipeline runs, so
    # they are captured here and handed to ``_analyze_and_store`` as the
    # already-seeded log the pipeline then appends to.
    captured: list[dict] = list(seed_log) if seed_log else []

    def on_progress(
        kind: str,
        message: str,
        percent: int | None = None,
        duration_ms: int | None = None,
    ) -> None:
        frame: dict = {"event": "progress", "kind": kind, "message": message}
        if percent is not None:
            frame["percent"] = percent
        if duration_ms is not None:
            frame["duration_ms"] = duration_ms
        q.put(_sse(frame))

    def prelude_progress(
        kind: str,
        message: str,
        percent: int | None = None,
        duration_ms: int | None = None,
    ) -> None:
        frame: dict = {"kind": kind, "message": message}
        if percent is not None:
            frame["percent"] = percent
        if duration_ms is not None:
            frame["duration_ms"] = duration_ms
        captured.append(frame)
        on_progress(kind, message, percent, duration_ms)

    def run() -> None:
        try:
            for frame in captured:
                on_progress(
                    frame["kind"],
                    frame["message"],
                    frame.get("percent"),
                    frame.get("duration_ms"),
                )
            resolved_root = root
            if prelude is not None:
                resolved_root = prelude(prelude_progress) or root
            if resolved_root is None:
                raise HTTPException(404, "repository root missing")
            _STATE.sink = on_progress
            try:
                info, bundle = _analyze_and_store(
                    ctx,
                    resolved_root,
                    name,
                    kind,
                    repo_id,
                    source_url,
                    stream=True,
                    log_lines=captured,
                )
            finally:
                _STATE.sink = None
            payload = {"bundle": bundle} if done_key == "bundle" else {"repo": info}
            q.put(_sse({"event": "done", **payload}))
        except HTTPException as exc:
            q.put(_sse({"event": "error", "error": exc.detail}))
        except Exception as exc:  # noqa: BLE001 - surface to the SSE client
            log.exception("streamed analysis failed")
            q.put(_sse({"event": "error", "error": str(exc)}))
        finally:
            if active_id is not None:
                ctx.store.release_active(active_id)
            q.put(None)

    threading.Thread(target=run, daemon=True).start()

    def gen():
        while True:
            item = q.get()
            if item is None:
                break
            yield item

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _bundle(ctx: _AppContext, repo_id: str) -> dict:
    store = ctx.store
    bundle = store.load_bundle(repo_id)
    if bundle is not None:
        log.info(
            "bundle %s: served from cache (%d referents)",
            repo_id,
            len(bundle.get("referents", [])),
        )
        return bundle
    manifest = store.load_manifest(repo_id)
    if manifest is not None:
        root = Path(manifest["root"])
        if not root.is_dir():
            raise HTTPException(404, f"repository tree missing: {root}")
        log.info("bundle %s: cache miss, re-analyzing %s", repo_id, root)
        _, bundle = _analyze_and_store(
            ctx, root, manifest["name"], manifest.get("kind", "path"), repo_id=repo_id
        )
        return bundle
    # Corpus candidate: listed on the home page, analyzed on demand.
    for candidate in _discover_corpus(ctx):
        if candidate["id"] == repo_id:
            log.info("bundle %s: corpus candidate, analyzing %s", repo_id, candidate["root"])
            _, bundle = _analyze_and_store(
                ctx, Path(candidate["root"]), candidate["name"], "corpus"
            )
            return bundle
    raise HTTPException(404, f"unknown repository: {repo_id}")


def _install_middleware(
    app: FastAPI, *, session_token: str, host_set: frozenset[str] | None
) -> None:
    @app.middleware("http")
    async def _require_session_token(request: Request, call_next):
        # No CORS headers are emitted (same-origin only), and the token is not
        # embedded in any served page, so no other origin can obtain it. Every
        # /api request needs it.
        if request.url.path.startswith("/api/"):
            if request.headers.get("x-session-token", "") != session_token:
                return JSONResponse(
                    {"detail": "missing or invalid session token"},
                    status_code=401,
                )
        return await call_next(request)

    @app.middleware("http")
    async def _require_known_host(request: Request, call_next):
        # A request whose Host header names another site (DNS rebinding) is
        # refused before any route runs. ``*`` is an explicit opt-out for a
        # container published on an arbitrary host port.
        if host_set is not None and "*" not in host_set:
            host = request.headers.get("host", "").lower()
            if host not in host_set:
                return JSONResponse({"detail": "host not allowed"}, status_code=400)
        return await call_next(request)

    @app.middleware("http")
    async def _log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        size = response.headers.get("content-length", "?")
        log.info(
            "%s %s -> %s (%.0fms, %s bytes)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            size,
        )
        return response


def _register_meta_routes(app: FastAPI, ctx: _AppContext) -> None:
    @app.post("/api/client-error")
    def client_error(payload: dict) -> dict:
        page = payload.get("page", "?")
        message = payload.get("message", "?")
        stack = (payload.get("stack") or "").strip()
        log.warning("CLIENT ERROR [%s]: %s\n%s", page, message, stack)
        return {"ok": True}

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "tool_version": TOOL_VERSION}

    @app.get("/health")
    def health_probe() -> dict:
        """Unauthenticated liveness probe for containers and monitors."""
        return {"status": "ok"}

    @app.get("/api/repos")
    def list_repos() -> dict:
        by_id: dict[str, dict] = {}
        for manifest in ctx.store.list_manifests():
            by_id[manifest["id"]] = _manifest_record(ctx.store, manifest)
        for candidate in _discover_corpus(ctx):
            by_id.setdefault(
                candidate["id"],
                {
                    **candidate,
                    "kind": "corpus",
                    "analyzed": False,
                    "analyzed_at": None,
                    "meta": None,
                },
            )
        repos = sorted(by_id.values(), key=lambda r: r["name"].lower())
        return {
            "repos": repos,
            "corpus_dir": str(ctx.corpus_dir),
            "workdir": str(ctx.store.workdir),
        }


def _register_ingest_routes(app: FastAPI, ctx: _AppContext) -> None:
    @app.post("/api/repos/analyze", response_model=None)
    def analyze_path(payload: dict, stream: bool = False) -> dict | StreamingResponse:
        raw = payload.get("path")
        if not isinstance(raw, str) or not raw.strip():
            raise HTTPException(400, "field 'path' is required")
        path = Path(raw).expanduser()
        if not path.is_dir():
            raise HTTPException(404, f"not a directory: {path}")
        root = find_project_root(path)
        if not _root_allowed(ctx, root, "path"):
            raise HTTPException(
                403,
                "local path analysis is disabled for this server; "
                "use --allow-root to enable specific roots",
            )
        name = root.name
        log.info("analyze request: path=%s resolved_root=%s", path, root)
        if stream:
            return _analyze_stream(ctx, root, name, "path", None, None)
        info, _ = _analyze_and_store(ctx, root, name, "path")
        return info

    @app.post("/api/repos/upload", response_model=None)
    async def upload_repo(file: UploadFile, stream: bool = False) -> dict | StreamingResponse:
        name = Path(file.filename or "repo.zip").stem or "repo"
        data = await file.read()
        if not data:
            raise HTTPException(400, "empty upload")
        if len(data) > _MAX_UPLOAD_BYTES:
            raise HTTPException(413, "upload too large")
        repo_id = f"{_slug(name)}-up{secrets.token_hex(4)}"
        dest = ctx.store.upload_dir(repo_id)
        tmp_zip = ctx.store.workdir / f"{repo_id}.zip"
        ctx.store.mark_active(repo_id)
        streaming = False
        try:
            tmp_zip.write_bytes(data)
            extract_start = time.perf_counter()
            try:
                extract_zip(tmp_zip, dest)
            except UnsafeArchiveError as exc:
                raise HTTPException(400, str(exc)) from exc
            except Exception as exc:
                raise HTTPException(400, f"invalid zip: {exc}") from exc
            finally:
                tmp_zip.unlink(missing_ok=True)
            extract_ms = round((time.perf_counter() - extract_start) * 1000)
            root = find_project_root(dest)
            log.info("upload %s: extracted to %s, root=%s", name, dest, root)
            if stream:
                response = _analyze_stream(
                    ctx,
                    root,
                    name,
                    "upload",
                    repo_id,
                    None,
                    seed_log=[{"kind": "timing", "message": "extract", "duration_ms": extract_ms}],
                    active_id=repo_id,
                )
                streaming = True
                return response
            info, _ = _analyze_and_store(ctx, root, name, "upload", repo_id)
            return info
        finally:
            if not streaming:
                ctx.store.release_active(repo_id)

    @app.post("/api/repos/clone", response_model=None)
    def clone_repo(payload: dict, stream: bool = False) -> dict | StreamingResponse:
        raw = payload.get("url")
        if not isinstance(raw, str) or not raw.strip():
            raise HTTPException(400, "field 'url' is required")
        url = raw.strip()
        error = _validate_git_url(url)
        if error is not None:
            raise HTTPException(400, error)
        base = Path(url).name
        if base.lower().endswith(".git"):
            base = base[:-4]
        name = _slug(base) or "repo"

        # Re-cloning a URL already in the workdir refreshes that checkout under
        # its existing id instead of downloading and analyzing a second copy.
        existing = ctx.store.find_clone_by_url(url)
        if existing is not None:
            repo_id = existing["id"]
            dest = ctx.store.clone_dir(repo_id)

            def prelude(on_progress: Callable[..., None]) -> Path:
                on_progress("info", f"reusing existing clone: {dest.name}")
                clone_start = time.perf_counter()
                _refresh_clone_repository(url, dest, on_progress)
                on_progress(
                    "timing",
                    "clone",
                    duration_ms=round((time.perf_counter() - clone_start) * 1000),
                )
                root = find_project_root(dest)
                log.info("clone %s: refreshed %s, root=%s", name, dest, root)
                return root

        else:
            repo_id = f"{name}-cl{secrets.token_hex(4)}"
            dest = ctx.store.clone_dir(repo_id)

            def prelude(on_progress: Callable[..., None]) -> Path:
                on_progress("cmd", f"git clone --depth 1 {url}")
                clone_start = time.perf_counter()
                try:
                    _clone_repository(url, dest, on_progress)
                except CloneError as exc:
                    raise HTTPException(400, str(exc)) from exc
                on_progress(
                    "timing",
                    "clone",
                    duration_ms=round((time.perf_counter() - clone_start) * 1000),
                )
                root = find_project_root(dest)
                on_progress("ok", f"clone complete: {root}")
                log.info("clone %s: cloned to %s, root=%s", name, dest, root)
                return root

        ctx.store.mark_active(repo_id)
        if stream:
            return _analyze_stream(
                ctx, None, name, "clone", repo_id, url, prelude=prelude, active_id=repo_id
            )
        try:
            prelude(_noop_progress)
            root = find_project_root(dest)
            info, _ = _analyze_and_store(ctx, root, name, "clone", repo_id, source_url=url)
            return info
        finally:
            ctx.store.release_active(repo_id)


def _register_repo_routes(app: FastAPI, ctx: _AppContext) -> None:
    @app.get("/api/repos/{repo_id}/bundle")
    def get_bundle(repo_id: str) -> dict:
        _check_id(repo_id)
        return _bundle(ctx, repo_id)

    @app.get("/api/repos/{repo_id}/log")
    def get_log(repo_id: str) -> dict:
        """Reopen a completed run's progress log.

        Returns ``{"lines": []}`` for legacy bundles analyzed before logs were
        persisted, so the frontend can simply hide the logs affordance.
        """
        _check_id(repo_id)
        return {"lines": ctx.store.load_log(repo_id) or []}

    @app.get("/api/repos/{repo_id}/bundle/stream", response_model=None)
    def get_bundle_stream(repo_id: str) -> StreamingResponse:
        """SSE variant of the bundle: cached bundles arrive instantly, cache
        misses stream the re-analysis pipeline progress first."""
        _check_id(repo_id)
        bundle = ctx.store.load_bundle(repo_id)
        if bundle is not None:

            def cached():
                yield _sse({"event": "done", "bundle": bundle})

            return StreamingResponse(
                cached(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )
        manifest = ctx.store.load_manifest(repo_id)
        if manifest is not None:
            root = Path(manifest["root"])
            if not root.is_dir():
                raise HTTPException(404, f"repository tree missing: {root}")
            log.info("bundle %s: cache miss, re-analyzing %s", repo_id, root)
            return _analyze_stream(
                ctx,
                root,
                manifest["name"],
                manifest.get("kind", "path"),
                repo_id,
                None,
                done_key="bundle",
            )
        for candidate in _discover_corpus(ctx):
            if candidate["id"] == repo_id:
                log.info("bundle %s: corpus candidate, analyzing %s", repo_id, candidate["root"])
                return _analyze_stream(
                    ctx,
                    Path(candidate["root"]),
                    candidate["name"],
                    "corpus",
                    repo_id,
                    None,
                    done_key="bundle",
                )
        raise HTTPException(404, f"unknown repository: {repo_id}")

    @app.get("/api/repos/{repo_id}/export.md")
    def get_markdown(repo_id: str) -> PlainTextResponse:
        _check_id(repo_id)
        return PlainTextResponse(to_markdown(_bundle(ctx, repo_id)))

    @app.delete("/api/repos/{repo_id}")
    def delete_repo(repo_id: str) -> dict:
        """Remove one analysis (manifest + cached bundle; upload source too)."""
        _check_id(repo_id)
        if not ctx.store.delete_repo(repo_id):
            raise HTTPException(404, f"unknown repository: {repo_id}")
        log.info("deleted analysis %s", repo_id)
        return {"ok": True}

    @app.get("/api/repos/{repo_id}/file")
    def get_file(repo_id: str, path: str, start: int = 1, end: int = 0) -> dict:
        _check_id(repo_id)
        manifest = ctx.store.load_manifest(repo_id)
        root = ctx.store.root_for(repo_id)
        if manifest is None or root is None:
            raise HTTPException(404, f"unknown repository: {repo_id}")
        if not _root_allowed(ctx, root, manifest.get("kind", "path")):
            raise HTTPException(403, "repository root is not allowed for local path access")
        target = (root / path).resolve()
        if not target.is_relative_to(root.resolve()):
            raise HTTPException(400, "path escapes repository root")
        if not target.is_file():
            raise HTTPException(404, f"no such file: {path}")
        try:
            lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            raise HTTPException(500, f"cannot read file: {exc}") from exc
        if end <= 0:
            end = min(start + _MAX_FILE_LINES - 1, len(lines))
        start = max(1, start)
        end = min(max(start, end), len(lines))
        return {
            "path": path,
            "start": start,
            "end": end,
            "lines": [
                {"n": n, "text": text} for n, text in enumerate(lines, 1) if start <= n <= end
            ],
        }


def _register_maintenance_routes(app: FastAPI, ctx: _AppContext) -> None:
    @app.post("/api/repos/clear-cache")
    def clear_cache() -> dict:
        """Drop cached bundles and the AST inventory caches in analyzed roots."""
        bundles = ctx.store.clear_bundles()
        symbol_caches = ctx.store.clear_symbol_caches()
        log.info("cleared cache: %d bundles, %d symbol caches", bundles, symbol_caches)
        return {"ok": True, "cleared_bundles": bundles, "cleared_symbol_caches": symbol_caches}

    @app.post("/api/repos/prune-sources")
    def prune_sources() -> dict:
        """Delete orphaned clone/upload trees (and caches) with no manifest."""
        report = ctx.store.prune_sources()
        log.info("pruned sources: %s", report)
        return {"ok": True, **report}

    @app.post("/api/repos/prune-duplicates")
    def prune_duplicates() -> dict:
        """Delete every clone but the newest one per remote URL."""
        report = ctx.store.prune_duplicate_clones()
        log.info("pruned duplicate clones: %s", report)
        return {"ok": True, **report}


def _is_loopback_client(request: Request) -> bool:
    """True when the request originates on this machine (the local browser)."""
    host = request.client.host if request.client else ""
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return host == "localhost"
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    return addr.is_loopback


def _is_loopback_host_header(value: str) -> bool:
    """True for ``localhost`` / loopback-IP Host headers, with or without a port.

    Containers publish the UI on ``localhost:<host-port>`` but the connection
    arrives from the Docker bridge gateway, so ``request.client`` is not
    loopback. The Host header is the only signal that the browser is local.
    """
    host = value.strip().lower()
    if host.startswith("["):
        host = host[1 : host.find("]")] if "]" in host else host
    elif host.count(":") == 1:
        host = host.rsplit(":", 1)[0]
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return host == "localhost"
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    return addr.is_loopback


def _mount_static(
    app: FastAPI, static_dir: Path | None, *, allow_bare_index: bool = False
) -> None:
    if static_dir is None or not static_dir.is_dir():
        return

    @app.get("/", include_in_schema=False)
    def _index(request: Request, token: str | None = None):
        index = static_dir / "index.html"
        if not index.is_file():
            raise HTTPException(404, "index.html missing; run: cd web && npm run build")
        expected = app.state.session_token
        host_is_local = allow_bare_index and _is_loopback_host_header(
            request.headers.get("host", "")
        )
        if expected and token != expected and (_is_loopback_client(request) or host_is_local):
            # A bare http://127.0.0.1:8000/ (a bookmark, a new tab, or a reload
            # after the server restarted with a new token) carries no token and
            # would 401 on every API call. On loopback, hand the browser the
            # address printed at startup; remote clients still need that URL.
            # ``allow_bare_index`` extends the same courtesy to a container
            # browser whose connection arrives from the Docker bridge gateway
            # but whose Host header is still localhost/127.0.0.1.
            return RedirectResponse(
                f"/?token={expected}",
                status_code=307,
                headers={"Cache-Control": "no-store"},
            )
        html = index.read_text(encoding="utf-8")
        return HTMLResponse(
            html,
            headers={"Cache-Control": "no-cache"},
        )

    app.mount("/", StaticFiles(directory=static_dir, html=True), name="web")


def create_app(
    *,
    workdir: Path,
    corpus_dir: Path | None = None,
    static_dir: Path | None = None,
    allow_root: list[Path] | None = None,
    allow_local_paths: bool = True,
    allowed_hosts: list[str] | None = None,
    allow_bare_index: bool = False,
) -> FastAPI:
    """Build the app.

    ``allowed_hosts`` lists the ``Host`` header values the server answers
    (``run`` always passes them); ``None`` disables the check for embedding
    and tests.
    """
    # Session token (B4): every API request must carry it. It is never embedded
    # in a served page: ``run`` prints the start address ``/?token=...``, the
    # frontend moves the token from the address bar into session storage, and a
    # loopback ``GET /`` without (or with a stale) token is redirected to that
    # address instead of rendering a page that cannot call the API.
    ctx = _AppContext(
        store=RepoStore(workdir),
        corpus_dir=corpus_dir if corpus_dir is not None else Path("test_repos"),
        allow_root=tuple(allow_root or []),
        allow_local_paths=allow_local_paths,
        session_token=secrets.token_urlsafe(32),
        host_set=(
            frozenset(h.lower() for h in allowed_hosts) if allowed_hosts is not None else None
        ),
    )
    app = FastAPI(title="DocAssay", version=TOOL_VERSION)
    app.state.session_token = ctx.session_token
    _install_middleware(app, session_token=ctx.session_token, host_set=ctx.host_set)
    _register_meta_routes(app, ctx)
    _register_ingest_routes(app, ctx)
    _register_repo_routes(app, ctx)
    _register_maintenance_routes(app, ctx)
    _mount_static(app, static_dir, allow_bare_index=allow_bare_index)
    return app


def run(
    host: str = "127.0.0.1",
    port: int | None = None,
    workdir: Path | None = None,
    corpus: Path | None = None,
    static: Path | None = None,
    allow_root: list[Path] | None = None,
    allowed_hosts: list[str] | None = None,
    public_url: str | None = None,
    allow_bare_index: bool = False,
) -> int:
    """Launch uvicorn with the web app (requires the ``[web]`` extra).

    ``port`` falls back to ``$DOCASSAY_PORT`` and then to 8000. ``public_url``
    (or ``$DOCASSAY_PUBLIC_URL``) is only what the startup line prints; it is
    how a container that maps a different host port announces the right address.
    """
    import uvicorn

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    if port is None:
        raw_port = os.environ.get("DOCASSAY_PORT", "8000")
        try:
            port = int(raw_port)
        except ValueError as exc:
            raise SystemExit(f"invalid DOCASSAY_PORT: {raw_port!r}") from exc
    if not 1 <= port <= 65535:
        raise SystemExit(f"port out of range: {port}")
    public_url = public_url or os.environ.get("DOCASSAY_PUBLIC_URL") or None

    default_workdir = Path.home() / ".local" / "share" / "docassay" / "web"
    default_static = Path(__file__).resolve().parents[3] / "web" / "dist"
    app = create_app(
        workdir=workdir or default_workdir,
        corpus_dir=corpus,
        static_dir=static or default_static,
        allow_root=allow_root,
        allow_local_paths=_is_loopback_host(host),
        allowed_hosts=host_header_values(host, port, allowed_hosts or []),
        allow_bare_index=allow_bare_index,
    )
    if host not in ("127.0.0.1", "localhost", "::1"):
        if not allow_root:
            log.warning(
                "binding non-loopback host %r with no --allow-root: "
                "local path analysis is disabled",
                host,
            )
        else:
            log.warning(
                "binding non-loopback host %r: local path analysis limited to --allow-root roots",
                host,
            )
    shown = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    shown = f"[{shown}]" if ":" in shown else shown
    base = (public_url or f"http://{shown}:{port}").rstrip("/")
    print(f"open: {base}/?token={app.state.session_token}", flush=True)
    log.info("serving API + static %s at http://%s:%s", static or default_static, shown, port)
    uvicorn.run(app, host=host, port=port)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docassay web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="bind port (default: $DOCASSAY_PORT or 8000)",
    )
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--corpus", type=Path, default=None)
    parser.add_argument("--static", type=Path, default=None)
    parser.add_argument(
        "--public-url",
        default=None,
        help="address to print for the UI when the host port differs "
        "(default: $DOCASSAY_PUBLIC_URL)",
    )
    parser.add_argument(
        "--allow-bare-index",
        action="store_true",
        help="redirect a loopback Host (localhost/127.0.0.1) to ?token= even when "
        "the connection arrives from a bridge (used by the demo container)",
    )
    parser.add_argument(
        "--allow-root",
        type=Path,
        action="append",
        default=None,
        help="allow local path analysis only under this root (repeatable)",
    )
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=None,
        help="extra Host header to answer; \"*\" disables the check (repeatable)",
    )
    args = parser.parse_args(argv)
    return run(
        host=args.host,
        port=args.port,
        workdir=args.workdir,
        corpus=args.corpus,
        static=args.static,
        allow_root=args.allow_root,
        allowed_hosts=args.allowed_host,
        public_url=args.public_url,
        allow_bare_index=args.allow_bare_index,
    )


if __name__ == "__main__":
    raise SystemExit(main())
