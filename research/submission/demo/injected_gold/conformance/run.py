"""Conformance-template injector for the three predicate-defined artifact classes.

For ``license``, ``dockerfile`` and ``ci_workflow`` the referent is fixed by the
predicate, so a constructed case is a conformance test, not a circular target
choice (see ``validation/protocol.md`` and ``README.md`` here). Each case is
materialized on a clean synthetic repo, proved with the engine-free oracle, and
recorded in a manifest compatible with ``score_injections.py``.

Provenance: ``origin = "conformance"``. This arm is reported separately from the
real-incident LLM injections.

Run::

    PYTHONPATH=src uv run python .../conformance/run.py --out .../conformance/runs/demo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
CONF = HERE.parent
IG = CONF.parent
sys.path.insert(0, str(IG / "scripts"))
sys.path.insert(0, str(IG))
from engine import grammar  # noqa: E402
from engine.oracle import verify_entry  # noqa: E402

SYNTHETIC = IG / "synthetic"
DEFAULT_OUT = CONF / "runs" / "demo"

_SETUP_FILE = "file"
_SETUP_APPEND = "append"
_SETUP_LICENSE = "license"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _line_of(path: Path, needle: str) -> int:
    if not path.is_file():
        return 0
    for i, line in enumerate(_read(path).splitlines(), start=1):
        if line.strip() == needle.strip():
            return i
    return 0


def _set_license(path: Path, value: str) -> None:
    text = _read(path)
    if re.search(r"^\s*license\s*=", text, re.MULTILINE):
        text = re.sub(
            r"^\s*license\s*=.*$", f'license = "{value}"', text, count=1, flags=re.MULTILINE
        )
    else:
        text = text.replace("[project]\n", f'[project]\nlicense = "{value}"\n', 1)
    path.write_text(text, encoding="utf-8")


def _apply_setup(op: dict, case: dict, root: Path) -> None:
    if op["op"] == _SETUP_FILE:
        path = root / op["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(op["text"], encoding="utf-8")
    elif op["op"] == _SETUP_APPEND:
        path = root / op["doc_path"]
        orig = _read(path)
        sep = "" if orig.endswith("\n") or not orig else "\n"
        path.write_text(orig + sep + case["claim"] + "\n", encoding="utf-8")
    elif op["op"] == _SETUP_LICENSE:
        _set_license(root / op.get("file", "pyproject.toml"), op["value"])
    else:  # pragma: no cover - defensive
        raise SystemExit(f"unknown setup op: {op['op']!r}")


def _entry(case: dict, repo: str, line: int) -> dict:
    return {
        "repo": repo,
        "op_id": case["id"],
        "name": case["id"],
        "canonical_class": case["canonical_class"],
        "artifact_class": case["artifact_class"],
        "direction": "doc_side",
        "stratum": "direct_reference",
        "target": case["target"],
        "doc_path": case["doc_path"],
        "line": line,
        "expected_verdict": case.get("expected_verdict"),
        "control": case["control"],
        "surface": case.get("surface", ""),
        "kind": case["kind"],
        "seed": 0,
        "repo_class": "conformance",
        "file": case.get("file"),
        "old": case["old"],
        "new": case["claim"],
        "symbol": case.get("symbol"),
        "expect_present": case.get("expect_present"),
    }


def _lic(control: str, claim: str, expect: bool) -> dict:
    return {
        "canonical_class": "license-drift",
        "artifact_class": "license",
        "kind": "claim_license" if control == "none" else "control_claim",
        "control": control,
        "expected_verdict": "refuted" if control == "none" else None,
        "doc_path": "README.md",
        "claim": claim,
        "target": "MIT",
        "old": "mit",
        "file": "pyproject.toml",
        "surface": None if control == "none" else "license",
        "expect_present": None if control == "none" else expect,
    }


def _docker(control: str, claim: str, expect: bool) -> dict:
    return {
        "canonical_class": "dockerfile-drift",
        "artifact_class": "dockerfile",
        "kind": "claim_dockerfile" if control == "none" else "control_claim",
        "control": control,
        "expected_verdict": "refuted" if control == "none" else None,
        "doc_path": "README.md",
        "claim": claim,
        "target": "Dockerfile",
        "old": "dockerfile",
        "surface": None if control == "none" else "dockerfile",
        "expect_present": None if control == "none" else expect,
    }


def _ci(control: str, claim: str, expect: bool) -> dict:
    return {
        "canonical_class": "ci-workflow-drift",
        "artifact_class": "ci_workflow",
        "kind": "claim_ci_workflow" if control == "none" else "control_claim",
        "control": control,
        "expected_verdict": "refuted" if control == "none" else None,
        "doc_path": "README.md",
        "claim": claim,
        "target": "GitHub Actions",
        "old": "ci_workflow",
        "surface": None if control == "none" else "ci_workflow",
        "expect_present": None if control == "none" else expect,
    }


def cases() -> list[dict]:
    """The three predicates × {false claim, control present, mention}."""
    cb = "quillpad"
    out: list[dict] = []

    out.append({"id": "dockerfile.false_claim", "base": cb, "setup": [], **_docker(
        "none", "The project ships a `Dockerfile`.", False)})
    out.append({"id": "dockerfile.control_present", "base": cb,
                "setup": [{"op": "file", "path": "Dockerfile", "text": "FROM python:3.12\n"},
                          {"op": "append", "doc_path": "README.md"}],
                **_docker("consistent_present", "The project ships a `Dockerfile`.", True)})
    out.append({"id": "dockerfile.mention", "base": cb,
                "setup": [{"op": "append", "doc_path": "README.md"}],
                **_docker("consistent_absent", "Add a `Dockerfile` to deploy the service.", False)})

    out.append({"id": "ci_workflow.false_claim", "base": cb, "setup": [], **_ci(
        "none", "CI runs on GitHub Actions.", False)})
    out.append({"id": "ci_workflow.control_present", "base": cb,
                "setup": [{"op": "file", "path": ".github/workflows/ci.yml", "text": "on: push\n"},
                          {"op": "append", "doc_path": "README.md"}],
                **_ci("consistent_present", "CI runs on GitHub Actions.", True)})
    out.append({"id": "ci_workflow.mention", "base": cb,
                "setup": [{"op": "append", "doc_path": "README.md"}],
                **_ci("consistent_absent", "Set up a CI workflow before releasing.", False)})

    mit_claim = "The project is released under the MIT license."
    not_mit_claim = "This project is not released under the MIT license."
    out.append({"id": "license.false_claim", "base": cb,
                "setup": [{"op": "license", "value": "Apache-2.0"}],
                **_lic("none", mit_claim, False)})
    out.append({"id": "license.control_present", "base": cb,
                "setup": [{"op": "license", "value": "MIT"},
                          {"op": "append", "doc_path": "README.md"}],
                **_lic("consistent_present", mit_claim, True)})
    out.append({"id": "license.mention", "base": cb,
                "setup": [{"op": "license", "value": "Apache-2.0"},
                          {"op": "append", "doc_path": "README.md"}],
                **_lic("consistent_absent", not_mit_claim, False)})
    return out


def run(out: Path) -> dict:
    snapshots = out / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    provenance: list[dict] = []
    stats = {"verified": 0, "rejected": 0}

    for case in cases():
        repo = case["id"].replace(".", "_")
        src = SYNTHETIC / case["base"]
        base = snapshots / f"{repo}__baseline"
        injected = snapshots / f"{repo}__injected"
        grammar.snapshot(src, base)
        grammar.snapshot(src, injected)

        for op in case["setup"]:
            _apply_setup(op, case, base)
            _apply_setup(op, case, injected)

        if case["control"] == "none":
            cand = {"doc_path": case["doc_path"], "new": case["claim"]}
            if grammar.apply_mutation(injected, case["kind"], cand) is None:
                stats["rejected"] += 1
                continue

        root = base if case["control"] != "none" else injected
        entry = _entry(case, repo, _line_of(root / case["doc_path"], case["claim"]))
        passed, reason = verify_entry(entry, root)
        provenance.append(
            {
                "name": case["id"],
                "origin": "conformance",
                "source_repo": case["base"],
                "kind": case["kind"],
                "control": case["control"],
                "expected_verdict": case.get("expected_verdict"),
                "verifier": "ok" if passed else reason,
            }
        )
        if not passed:
            stats["rejected"] += 1
            continue
        entry["verifier"] = "ok"
        manifest.append(entry)
        stats["verified"] += 1

    out.mkdir(parents=True, exist_ok=True)
    with (out / "manifest.jsonl").open("w", encoding="utf-8") as f:
        for entry in manifest:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    (out / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {"manifest": len(manifest), **stats}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)
    result = run(Path(args.out))
    print(json.dumps(result))
    return 0 if result["rejected"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
