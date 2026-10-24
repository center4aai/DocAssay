"""Safe zip extraction for the upload endpoint.

Guards against zip-slip (paths escaping the destination), symlinks and
bombs (unbounded size / file count). Symlinks and macOS metadata entries are
skipped rather than rejected: a zip made on macOS from a checkout that contains
a virtualenv otherwise fails even though the actual sources are safe.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

_MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
_MAX_FILES = 10_000


class UnsafeArchiveError(ValueError):
    """The archive violates an extraction safety guard."""


def _is_metadata(name: str) -> bool:
    """macOS resource forks, Finder metadata and ``__MACOSX`` sidecars."""
    parts = Path(name.replace("\\", "/")).parts
    if not parts:
        return True
    return parts[0] == "__MACOSX" or parts[-1] == ".DS_Store" or parts[-1].startswith("._")


def _safe_target(dest: Path, name: str) -> Path:
    norm = name.replace("\\", "/")
    if norm.startswith("/") or norm.startswith("./") and norm != "./":
        raise UnsafeArchiveError(f"unsafe archive path: {name!r}")
    parts = Path(norm).parts
    if not parts or any(p in ("", "..") for p in parts):
        raise UnsafeArchiveError(f"unsafe archive path: {name!r}")
    dest_root = dest.resolve()
    target = dest.joinpath(*parts).resolve()
    if not target.is_relative_to(dest_root):
        raise UnsafeArchiveError(f"archive path escapes destination: {name!r}")
    return target


def extract_zip(zip_path: Path, dest: Path) -> None:
    """Extract ``zip_path`` into ``dest`` with safety guards."""
    dest.mkdir(parents=True, exist_ok=True)
    dest_root = dest.resolve()
    total = 0
    count = 0
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            if _is_metadata(info.filename):
                continue
            total += info.file_size
            count += 1
            if total > _MAX_UNCOMPRESSED_BYTES:
                raise UnsafeArchiveError("archive is too large")
            if count > _MAX_FILES:
                raise UnsafeArchiveError("archive contains too many files")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                # Never materialize a symlink (it could point outside the tree);
                # skip it so an otherwise valid checkout still uploads.
                continue
            if info.is_dir():
                continue
            target = _safe_target(dest, info.filename)
            if not target.is_relative_to(dest_root):
                raise UnsafeArchiveError("archive path escapes destination")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
