"""Pipeline integration: SARIF export, exit status on findings, pre-commit hook."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from docassay.core.cli import main
from docassay.core.pipeline import analyze_repository
from docassay.core.sarif import to_sarif

_README = (
    "# Demo project\nThis is the demo project that many teams use every day.\n"
    "The entry point lives in `src/app.py` and the helper in `src/gone.py`.\n"
)


def _repo(root: Path) -> Path:
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (root / "README.md").write_text(_README, encoding="utf-8")
    return root


def test_sarif_reports_each_refuted_claim(tmp_path: Path) -> None:
    root = _repo(tmp_path / "repo")
    log = to_sarif(analyze_repository(root), scan_root=root)
    assert log["version"] == "2.1.0"
    run = log["runs"][0]
    assert run["tool"]["driver"]["name"] == "DocAssay"
    results = run["results"]
    assert [r["ruleId"] for r in results] == ["PATH_EXISTS"]
    location = results[0]["locations"][0]["physicalLocation"]
    assert location["artifactLocation"]["uri"] == "README.md"
    assert location["region"]["startLine"] == 3
    assert "`src/gone.py`" in results[0]["message"]["text"]
    assert run["tool"]["driver"]["rules"][results[0]["ruleIndex"]]["id"] == "PATH_EXISTS"


def test_cli_sarif_output_and_fail_on(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    root = _repo(tmp_path / "repo")
    out = tmp_path / "docassay.sarif"
    assert main(["analyze", "--format", "sarif", "--output", str(out), str(root)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["runs"][0]["results"]
    assert main(["analyze", "--fail-on", "refuted", str(root)]) == 1
    (root / "src" / "gone.py").write_text("y = 2\n", encoding="utf-8")
    assert main(["analyze", "--fail-on", "refuted", str(root)]) == 0
    capsys.readouterr()


def test_pre_commit_hook_runs_the_cli() -> None:
    hooks = Path(__file__).resolve().parents[3] / ".pre-commit-hooks.yaml"
    text = hooks.read_text(encoding="utf-8")
    assert "id: docassay" in text
    assert "docassay analyze --fail-on refuted" in text
    assert "pass_filenames: false" in text
