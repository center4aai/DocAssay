"""Structure inventory harvested from the analyzed repository.

The PATH_EXISTS predicate's evidence source is the project's own file and
directory listing. The listing is complete by construction, which
is what makes the structure world CLOSED: a claim about a path that is not in
the listing is REFUTED. Files and directories share one inventory; directory
keys keep a trailing slash (``docs/``) so they never collide with file keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from docassay.evidence.git import git_tracked_files, tracked_dir_prefixes
from docassay.vocabularies.structure import SKIPPED_DIRS, normalize_path


@dataclass(frozen=True, slots=True)
class PathEvidence:
    """One path in the project tree (a file or a directory)."""

    evidence_id: str
    path: str
    kind: str
    domain: str = ""
    line_start: int | None = None
    line_end: int | None = None
    snippet: str = ""
    # The path exactly as it appears in the tree (original case). ``path`` is
    # normalized (lowercased) for grouping; case-fidelity resolution compares
    # the claim's original-case token against this.
    raw_path: str = ""

    @property
    def object(self) -> str:
        """The normalized referent key that groups evidence with claims."""
        return self.path

    @property
    def source_file(self) -> str:
        """Provenance: the path itself is the fact's location."""
        return self.path


def build_structure_inventory(project_root: Path, kind: str) -> list[PathEvidence]:
    """Every ``kind`` path in the project tree, ``"file"``/``"dir"``/``"both"``.

    When the tree is a git checkout, the file set is the tracked snapshot
    (``git ls-files``) — untracked files and build scratch never enter the
    CLOSED world, and ``SKIPPED_DIRS`` is NOT applied (a tracked ``doc/build/``
    is a real path docs may reference. For a git-less tree the
    working-tree walk is used with only ``SKIPPED_DIRS`` pruned — hidden files
    and dot-directories (``.github/``, ``.gitignore``) are real paths that docs
    reference, so they stay in the listing that makes the structure world
    CLOSED.
    """
    tracked = git_tracked_files(project_root)
    if tracked is not None:
        return _evidence_from_tracked(tracked, kind)

    evidence: list[PathEvidence] = []
    for dirpath, dirnames, filenames in Path(project_root).walk():
        dirnames[:] = sorted(d for d in dirnames if d not in SKIPPED_DIRS)
        rel_dir = dirpath.relative_to(project_root)
        base = "" if rel_dir == Path(".") else rel_dir.as_posix() + "/"
        if kind in ("dir", "both"):
            if base:
                evidence.append(_dir_evidence(base))
            for dirname in sorted(dirnames):
                evidence.append(_dir_evidence(base + dirname + "/"))
        if kind in ("file", "both"):
            for filename in sorted(filenames):
                rel = base + filename
                evidence.append(
                    PathEvidence(
                        evidence_id=f"file:{rel}",
                        path=normalize_path(rel),
                        raw_path=rel,
                        kind="file",
                        line_start=1,
                        line_end=1,
                    )
                )
    return evidence


def _evidence_from_tracked(tracked: frozenset[str], kind: str) -> list[PathEvidence]:
    """Listing derived from ``git ls-files``: files + implied directories."""
    evidence: list[PathEvidence] = []
    if kind in ("dir", "both"):
        for dirkey in sorted(tracked_dir_prefixes(tracked)):
            evidence.append(_dir_evidence(dirkey))
    if kind in ("file", "both"):
        for rel in sorted(tracked):
            evidence.append(
                PathEvidence(
                    evidence_id=f"file:{rel}",
                    path=normalize_path(rel),
                    raw_path=rel,
                    kind="file",
                    line_start=1,
                    line_end=1,
                )
            )
    return evidence


def _dir_evidence(rel: str) -> PathEvidence:
    return PathEvidence(
        evidence_id=f"dir:{rel}", path=normalize_path(rel), raw_path=rel, kind="dir"
    )
