"""Shared paths for the demo artifact tree.

Convention: everything new for the artifact is written under
``research/submission/demo/``. Legacy inputs stay in the private archive;
this tree only reads them and never writes into them.

Run a script directly so its own directory is on ``sys.path``::

    PYTHONPATH=src uv run python .../injected_gold/scripts/score_injections.py
"""

from __future__ import annotations

from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ARTIFACT = SCRIPTS.parent  # research/submission/demo
RESEARCH = ARTIFACT.parent  # research/submission
REPO_ROOT = RESEARCH.parents[1]  # repository root


# Active artifact directories.
VALIDATION = ARTIFACT / "validation"
INJECTED_GOLD = ARTIFACT / "injected_gold"

TEST_REPOS = REPO_ROOT / "test_repos"
VALIDATION_REPOS = REPO_ROOT / "validation_repos"
