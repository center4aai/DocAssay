"""Infrastructure inventory harvested from the analyzed repository.

The HAS_DOCKERFILE and HAS_CI_WORKFLOW predicates' evidence source is the
project's own file listing. The world is CLOSED over the listing:
a claim that a Dockerfile or a CI workflow exists is refuted by its absence.
Evidence is the concrete paths that satisfy each capability (``Dockerfile*``
files for the dockerfile referent; a closed allowlist of CI config files and
directories for the ``ci_workflow`` referent).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from docassay.data import load_list
from docassay.vocabularies.structure import SKIPPED_DIRS

# CI config file basenames and directories (data/project.json). A CI config
# anywhere in these shallow locations makes the ``ci_workflow`` claim true.
_CI_CONFIG_FILES: frozenset[str] = load_list("project.json", "ci_config_files")
_CI_CONFIG_DIRS: frozenset[str] = load_list("project.json", "ci_config_dirs")

_MAX_INFRA_SCAN_DEPTH = 3


@dataclass(frozen=True, slots=True)
class InfraEvidence:
    """One path in the tree that satisfies an infrastructure capability."""

    evidence_id: str
    kind: str
    path: str
    domain: str = ""
    line_start: int | None = None
    line_end: int | None = None

    @property
    def object(self) -> str:
        """The referent key grouping claims with evidence (kind-derived)."""
        return "dockerfile" if self.kind == "dockerfile" else "ci_workflow"

    @property
    def source_file(self) -> str:
        """Provenance: the path itself is the fact's location."""
        return self.path


def build_infra_inventory(project_root: Path) -> list[InfraEvidence]:
    """Every Dockerfile-like and CI-config path in the tree."""
    evidence: list[InfraEvidence] = []
    for dirpath, dirnames, filenames in Path(project_root).walk():
        rel_dir = dirpath.relative_to(project_root)
        if len(rel_dir.parts) > _MAX_INFRA_SCAN_DEPTH:
            dirnames[:] = []
            continue
        # Hidden dirs stay in the walk: CI lives under ``.github/workflows``.
        dirnames[:] = sorted(d for d in dirnames if d not in SKIPPED_DIRS)
        rel_base = "" if rel_dir == Path(".") else rel_dir.as_posix() + "/"
        for filename in sorted(filenames):
            rel = rel_base + filename
            low = filename.lower()
            if low == "dockerfile" or low.startswith("dockerfile."):
                evidence.append(
                    InfraEvidence(
                        evidence_id=f"dockerfile:{rel}",
                        kind="dockerfile",
                        path=rel,
                        line_start=1,
                        line_end=1,
                    )
                )
                continue
            if _is_ci_config(rel_base, filename):
                evidence.append(
                    InfraEvidence(
                        evidence_id=f"ci:{rel}",
                        kind="ci",
                        path=rel,
                        line_start=1,
                        line_end=1,
                    )
                )
    return _dedupe(evidence)


def _is_ci_config(rel_base: str, filename: str) -> bool:
    """Whether ``rel_base + filename`` is a known CI configuration location."""
    if filename.lower() in _CI_CONFIG_FILES:
        return True
    low = (rel_base + filename).lower()
    return any(low.startswith(dir_prefix + "/") for dir_prefix in _CI_CONFIG_DIRS)


def _dedupe(items: list[InfraEvidence]) -> list[InfraEvidence]:
    seen: set[str] = set()
    out: list[InfraEvidence] = []
    for item in items:
        if item.evidence_id in seen:
            continue
        seen.add(item.evidence_id)
        out.append(item)
    return out
