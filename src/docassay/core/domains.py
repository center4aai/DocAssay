"""Domain detection: which sub-project/part of a repository a file belongs to.

A monorepo has multiple authoritative manifests;
each manifest-bearing directory is a domain. Claims and evidence are stamped
with the domain of their file location and never mix across domains in one
referent. A file's domain is the deepest manifest-bearing directory that is an
ancestor of the file; the project root is the ``""`` (root/global) domain.

The same manifest walk that harvests the DEPENDENCY inventory feeds the index,
so a manifest that is authoritative for evidence is authoritative for the
domain mapping, and vice versa.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from pathlib import Path

from docassay.evidence.manifests import iter_manifest_files
from docassay.vocabularies.structure import normalize_path

ROOT_DOMAIN = ""


@dataclass(frozen=True, slots=True)
class DomainIndex:
    """Repository-relative manifest directories → file-to-domain mapping.

    ``manifest_dirs`` holds the normalized relative paths of every directory
    containing an authoritative manifest (the root directory is ``""``).
    """

    manifest_dirs: tuple[str, ...]

    @classmethod
    def build(cls, project_root: Path) -> DomainIndex:
        """Collect the manifest-bearing directories of ``project_root``."""
        dirs: set[str] = set()
        for _path, rel in iter_manifest_files(project_root):
            dirs.add(normalize_path(posixpath.dirname(rel)))
        ordered = sorted((d for d in dirs if d != ROOT_DOMAIN), key=len, reverse=True)
        ordered.append(ROOT_DOMAIN)
        return cls(manifest_dirs=tuple(ordered))

    @property
    def is_single_domain(self) -> bool:
        """Whether every file maps to the root domain (single-project repo)."""
        return len(self.manifest_dirs) <= 1

    def domain_for(self, rel: str) -> str:
        """The domain label of a repository-relative path (root → ``""``).

        The path is normalized before matching (the listing evidence stores
        normalized paths), and a directory match requires a ``/`` boundary so
        ``providers/amazonaws/…`` never matches the ``providers/amazon``
        domain. The deepest match wins; files outside every manifest directory
        (root-level docs of a monorepo without a root manifest) stay in the
        root domain.
        """
        normalized = normalize_path(rel)
        best = ROOT_DOMAIN
        for domain in self.manifest_dirs:
            if domain == ROOT_DOMAIN:
                continue
            if normalized == domain or normalized.startswith(domain + "/"):
                if len(domain) > len(best):
                    best = domain
        return best
