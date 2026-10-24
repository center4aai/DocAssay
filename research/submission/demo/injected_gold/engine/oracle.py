"""Engine-free verification of injected defects (the ``verify_without_tool`` oracle).

For every manifest entry this re-reads the **mutated** working tree and proves the
defect exists using only the standard library (``re``, ``ast``, ``tomllib``). The
engine is never imported. The LLM injector reuses :func:`verify_entry`, so only
independently-verified mutations reach the manifest.

Extracted from the retired ``scripts/verify_operators.py`` (the checks are
unchanged); the deterministic registry/driver live under
the retired deterministic-operator pipeline (not shipped).

Run::

    PYTHONPATH=src uv run python .../injected_gold/engine/oracle.py \\
        --manifest .../runs/<date>/manifest.jsonl --snapshots .../snapshots
    PYTHONPATH=src uv run python .../injected_gold/engine/oracle.py --selftest
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _corpus import (  # noqa: E402
    build_inventory,
    iter_doc_texts,
    resolve_path,
    resolve_symbol,
)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _doc_line(root: Path, doc_path: str, line: int) -> str | None:
    if not doc_path or line <= 0:
        return None
    path = root / doc_path
    if not path.is_file():
        return None
    lines = _read(path).splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1]
    return None


def _parsed_deps(root: Path) -> dict[str, str]:
    inv = build_inventory(root)
    return inv.deps


def _symbol_present(root: Path, qualname: str) -> bool:
    inv = build_inventory(root)
    q = qualname.lower()
    return any(
        d.qualname.lower() == q or d.qualname.lower().endswith("." + q) or d.name.lower() == q
        for d in inv.defs
    )


def _file_parses(root: Path, rel: str) -> bool:
    try:
        ast.parse(_read(root / rel), filename=rel)
        return True
    except SyntaxError:
        return False


def _literal_present(root: Path, rel: str, literal: str) -> bool:
    text = _read(root / rel)
    return f'"{literal}"' in text or f"'{literal}'" in text


# Capability inventory for the conformance claim kinds. Mirrors the engine's
# allowlists (``evidence/infra.py``); standard library only, no engine import.
_SKIP_DIRS = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", "venv", "build", "dist", "target", ".tox"}
)
_CI_CONFIG_FILES = frozenset(
    {
        ".gitlab-ci.yml",
        ".travis.yml",
        "appveyor.yml",
        "azure-pipelines.yml",
        "bitbucket-pipelines.yml",
        "buildkite.yml",
        "jenkinsfile",
        "wercker.yml",
    }
)
_CI_CONFIG_DIRS = frozenset({".buildkite", ".circleci", ".github/workflows"})


def _walk_files(root: Path, max_depth: int = 3):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if len(rel.parts) > max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)
        base = "" if not rel.parts else rel.as_posix() + "/"
        for filename in sorted(filenames):
            yield base, filename


def _has_dockerfile(root: Path) -> bool:
    for _base, filename in _walk_files(root):
        low = filename.lower()
        if low == "dockerfile" or low.startswith("dockerfile."):
            return True
    return False


def _has_ci_config(root: Path) -> bool:
    for base, filename in _walk_files(root):
        low = filename.lower()
        if low in _CI_CONFIG_FILES:
            return True
        rel = (base + filename).lower()
        if any(rel == d or rel.startswith(d + "/") for d in _CI_CONFIG_DIRS):
            return True
    return False


def _manifest_license(root: Path, file: str) -> str | None:
    path = root / file
    if not path.is_file():
        return None
    if not file.endswith(".toml"):
        return None
    try:
        data = tomllib.loads(_read(path))
    except tomllib.TOMLDecodeError:
        return None
    for holder in (
        data.get("project"),
        (data.get("tool") or {}).get("poetry"),
    ):
        if not isinstance(holder, dict):
            continue
        field = holder.get("license")
        if isinstance(field, str) and field.strip():
            return field.strip()
        if isinstance(field, dict) and isinstance(field.get("text"), str):
            return field["text"].strip() or None
    return None


# --------------------------------------------------------------------------- #
# per-kind checks
# --------------------------------------------------------------------------- #
def _check_path_rename(root: Path, e: dict) -> str | None:
    if (root / e["old"]).exists():
        return f"old path still exists: {e['old']}"
    if not (root / e["new"]).exists():
        return f"new path missing: {e['new']}"
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["target"] not in line:
        return f"doc line no longer names the old path: {e['doc_path']}:{e['line']}"
    return None


def _check_symbol_rename(root: Path, e: dict) -> str | None:
    if not _file_parses(root, e["file"]):
        return f"mutated file does not parse: {e['file']}"
    if _symbol_present(root, e["old"]):
        return f"old symbol still present: {e['old']}"
    if not _symbol_present(root, e["new"]):
        return f"new symbol missing: {e['new']}"
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["symbol"] not in line:
        return f"doc line no longer names the symbol: {e['doc_path']}:{e['line']}"
    return None


def _check_symbol_delete(root: Path, e: dict) -> str | None:
    if not _file_parses(root, e["file"]):
        return f"mutated file does not parse: {e['file']}"
    if _symbol_present(root, e["old"]):
        return f"deleted symbol still present: {e['old']}"
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["symbol"] not in line:
        return f"doc line no longer names the symbol: {e['doc_path']}:{e['line']}"
    return None


def _check_dependency_remove(root: Path, e: dict) -> str | None:
    if e["old"] in _parsed_deps(root):
        return f"dependency still declared: {e['old']}"
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["target"] not in line:
        return f"doc line no longer names the dependency: {e['doc_path']}:{e['line']}"
    return None


def _check_dependency_version_break(root: Path, e: dict) -> str | None:
    deps = _parsed_deps(root)
    if deps.get(e["symbol"], "") != e["new"]:
        return f"constraint is {deps.get(e['symbol'])!r}, expected {e['new']!r}"
    line = _doc_line(root, e["doc_path"], e["line"])
    # Dependency names are normalized to lower case in the inventory, while a
    # document may spell them with their published case (``PyYAML``). The
    # name check is therefore case-insensitive.
    if line is None or e["symbol"].lower() not in line.lower():
        return f"doc line no longer names the dependency: {e['doc_path']}:{e['line']}"
    return None


def _check_literal_rename(root: Path, e: dict) -> str | None:
    if _literal_present(root, e["file"], e["old"]):
        return f"old literal still present in {e['file']}: {e['old']!r}"
    if not _literal_present(root, e["file"], e["new"]):
        return f"new literal missing in {e['file']}: {e['new']!r}"
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["target"] not in line:
        return f"doc line no longer names the old token: {e['doc_path']}:{e['line']}"
    return None


def _check_type_annot(root: Path, e: dict) -> str | None:
    name = e["symbol"]
    text = _read(root / e["file"])
    if re.search(rf"->\s*{re.escape(name)}\b", text):
        return f"old annotation still present in {e['file']}: -> {name}"
    if f"-> {name}Injected" not in text:
        return f"new annotation missing in {e['file']}"
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["target"] not in line:
        return f"doc line no longer names the old type: {e['doc_path']}:{e['line']}"
    return None


def _check_enum_member_remove(root: Path, e: dict) -> str | None:
    if not _file_parses(root, e["file"]):
        return f"mutated file does not parse: {e['file']}"
    tree = ast.parse(_read(root / e["file"]))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                    names.add(target.id)
    if e["old"] in names:
        return f"enum member still present: {e['old']}"
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["old"] not in line:
        return f"doc line no longer names the member: {e['doc_path']}:{e['line']}"
    return None


def _check_add_symbol(root: Path, e: dict) -> str | None:
    if not _file_parses(root, e["file"]):
        return f"mutated file does not parse: {e['file']}"
    if not _symbol_present(root, e["new"]):
        return f"added symbol missing: {e['new']}"
    needle = e["symbol"]
    for rel, text in iter_doc_texts(root):
        if needle in text:
            return f"added symbol is documented after all ({rel})"
    return None


def _check_doc_mutation(root: Path, e: dict) -> str | None:
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None:
        return f"doc line missing: {e['doc_path']}:{e['line']}"
    old = f"`{e['old']}`" if e.get("backticked") else e["old"]
    new = f"`{e['new']}`" if e.get("backticked") else e["new"]
    if old in line:
        return "old token still on the doc line"
    if new not in line:
        return "new token not on the doc line"
    return None


def _check_command_change(root: Path, e: dict) -> str | None:
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None:
        return f"doc line missing: {e['doc_path']}:{e['line']}"
    if line.strip() != e["new"]:
        return "the documented command was not replaced"
    return None


def _check_cross_doc(root: Path, e: dict) -> str | None:
    err = _check_doc_mutation(root, e)
    if err:
        return err
    old = f"`{e['old']}`" if e.get("backticked") else e["old"]
    if e.get("other") and old not in _read(root / e["other"]):
        return f"the other document no longer carries the canonical token: {e['other']}"
    return None


def _check_translation(root: Path, e: dict) -> str | None:
    err = _check_doc_mutation(root, e)
    if err:
        return err
    old = f"`{e['old']}`" if e.get("backticked") else e["old"]
    if e.get("other") and old not in _read(root / e["other"]):
        return f"the canonical document no longer carries the original token: {e['other']}"
    return None


def _check_control_present(root: Path, e: dict) -> str | None:
    inv = build_inventory(root)
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["target"] not in line:
        return f"doc line no longer names the target: {e['doc_path']}:{e['line']}"
    if e["surface"] == "path":
        if resolve_path(inv, e["target"], e["doc_path"]) is None:
            return f"control target does not resolve to a tree path: {e['target']}"
    else:
        if not resolve_symbol(inv, e["target"]):
            return f"control target does not resolve to a symbol: {e['target']}"
    return None


def _check_control_absent(root: Path, e: dict) -> str | None:
    inv = build_inventory(root)
    line = _doc_line(root, e["doc_path"], e["line"])
    if line is None or e["target"] not in line:
        return f"doc line no longer names the target: {e['doc_path']}:{e['line']}"
    if e["surface"] == "dependency":
        if e["target"] in inv.deps:
            return f"control dependency is declared after all: {e['target']}"
    else:
        top = e["target"].split(".")[0].lower()
        if top in inv.top_packages:
            return f"control symbol top segment is project-owned: {top}"
    return None


def _check_claim_dockerfile(root: Path, e: dict) -> str | None:
    if e["new"] not in _read(root / e["doc_path"]):
        return "claim line is missing from the document"
    if _has_dockerfile(root):
        return "a Dockerfile is present, so the claim is not refuted"
    return None


def _check_claim_ci_workflow(root: Path, e: dict) -> str | None:
    if e["new"] not in _read(root / e["doc_path"]):
        return "claim line is missing from the document"
    if _has_ci_config(root):
        return "a CI config is present, so the claim is not refuted"
    return None


def _check_claim_license(root: Path, e: dict) -> str | None:
    if e["new"] not in _read(root / e["doc_path"]):
        return "claim line is missing from the document"
    declared = _manifest_license(root, e["file"])
    if not declared:
        return "no declared license (the claim would be NEI, not REFUTED)"
    if declared.strip().lower() == e["old"].strip().lower():
        return f"declared license matches the claim: {declared!r}"
    return None


def _check_control_claim(root: Path, e: dict) -> str | None:
    """A conformance control: the recorded claim is true (present or absent)."""
    if e["new"] not in _read(root / e["doc_path"]):
        return "claim line is missing from the document"
    surface = e.get("surface")
    expect = bool(e.get("expect_present"))
    if surface == "dockerfile":
        actual = _has_dockerfile(root)
    elif surface == "ci_workflow":
        actual = _has_ci_config(root)
    elif surface == "license":
        declared = _manifest_license(root, e.get("file", "pyproject.toml"))
        claimed = str(e.get("old", "")).strip().lower()
        actual = bool(declared) and declared.strip().lower() == claimed
    else:
        return f"unknown control surface: {surface!r}"
    if actual != expect:
        return f"control expects present={expect}, actual={actual}"
    return None


_CHECKS = {
    "path_rename": _check_path_rename,
    "symbol_rename": _check_symbol_rename,
    "symbol_delete": _check_symbol_delete,
    "dependency_remove": _check_dependency_remove,
    "dependency_version_break": _check_dependency_version_break,
    "config_key_rename": _check_literal_rename,
    "endpoint_rename": _check_literal_rename,
    "schema_field_rename": _check_literal_rename,
    "type_annot_mutate": _check_type_annot,
    "enum_member_remove": _check_enum_member_remove,
    "add_symbol": _check_add_symbol,
    "command_change": _check_command_change,
    "cross_doc_mutate": _check_cross_doc,
    "translation_mutate": _check_translation,
    "doc_symbol_mutate": _check_doc_mutation,
    "control_present": _check_control_present,
    "control_absent": _check_control_absent,
    "claim_dockerfile": _check_claim_dockerfile,
    "claim_ci_workflow": _check_claim_ci_workflow,
    "claim_license": _check_claim_license,
    "control_claim": _check_control_claim,
}


def verify_entry(entry: dict, root: Path) -> tuple[bool, str]:
    """Independently verify one manifest entry against a snapshot root."""
    kind = entry.get("kind")
    check = _CHECKS.get(kind)
    if check is None:
        return False, f"unknown operator kind: {kind!r}"
    try:
        reason = check(Path(root), entry)
    except (OSError, ValueError, SyntaxError) as exc:  # noqa: BLE001
        return False, f"verification error: {exc}"
    return (reason is None), (reason or "ok")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def verify_manifest(manifest: Path, snapshots: Path) -> tuple[int, int, list[str]]:
    entries = [
        json.loads(line)
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ok = 0
    errors: list[str] = []
    for e in entries:
        suffix = "baseline" if e.get("control", "none") != "none" else "injected"
        root = snapshots / f"{e['repo']}__{suffix}"
        passed, reason = verify_entry(e, root)
        if passed:
            ok += 1
        else:
            loc = f"{e.get('doc_path')}:{e.get('line')}"
            errors.append(f"{e.get('op_id', e.get('name'))} {e['target']!r} @ {loc}: {reason}")
    return ok, len(entries), errors


def selftest() -> int:
    """Unit tests for the oracle on tiny temporary fixtures."""
    rng = tempfile.TemporaryDirectory()
    root = Path(rng.name)
    (root / "pkg").mkdir()
    (root / "pkg" / "__init__.py").write_text("class Widget:\n    pass\n", encoding="utf-8")
    (root / "helper.py").write_text("def run():\n    return 1\n", encoding="utf-8")
    (root / "README.md").write_text(
        "Use `pkg.Widget` and `helper.py`.\nSee `pkg.Widget` for details.\n"
        "External `requests.adapters` is not ours.\n",
        encoding="utf-8",
    )
    failures: list[str] = []

    def expect(name: str, entry: dict, should_pass: bool) -> None:
        passed, reason = verify_entry(entry, root)
        if passed != should_pass:
            failures.append(f"{name}: expected pass={should_pass}, got {reason}")

    base = {"repo": "t", "op_id": "t", "target": "pkg.Widget", "doc_path": "README.md", "line": 1}

    expect("control_present-ok", {**base, "kind": "control_present", "surface": "symbol"}, True)
    expect(
        "control_absent-ok",
        {
            **base,
            "target": "requests.adapters",
            "line": 3,
            "kind": "control_absent",
            "surface": "symbol",
        },
        True,
    )
    expect(
        "control_absent-bad",
        {**base, "target": "pkg.Widget", "kind": "control_absent", "surface": "symbol"},
        False,
    )
    expect(
        "path-present-missing",
        {**base, "target": "nope.py", "kind": "control_present", "surface": "path"},
        False,
    )

    # A real symbol rename: rename the class, doc line 1 still names it.
    (root / "pkg" / "__init__.py").write_text(
        "class WidgetInjected:\n    pass\n", encoding="utf-8"
    )
    expect(
        "symbol_rename-ok",
        {
            **base,
            "kind": "symbol_rename",
            "file": "pkg/__init__.py",
            "old": "pkg.Widget",
            "new": "pkg.WidgetInjected",
            "symbol": "pkg.Widget",
        },
        True,
    )

    # A real path rename.
    (root / "helper.py").rename(root / "helper2.py")
    expect(
        "path_rename-ok",
        {
            **base,
            "target": "helper.py",
            "kind": "path_rename",
            "file": "helper.py",
            "old": "helper.py",
            "new": "helper2.py",
            "doc_path": "README.md",
            "line": 1,
        },
        True,
    )

    # Capability claims (conformance templates): a recorded false claim with no
    # artifact, plus the license-mismatch variant.
    def make_croot(name: str) -> Path:
        p = root / name
        p.mkdir()
        (p / "README.md").write_text("placeholder\n", encoding="utf-8")
        (p / "pyproject.toml").write_text(
            '[project]\nname = "t"\nversion = "0.1.0"\nlicense = "Apache-2.0"\n',
            encoding="utf-8",
        )
        return p

    def expect_at(name: str, croot: Path, entry: dict, should_pass: bool) -> None:
        passed, reason = verify_entry(entry, croot)
        if passed != should_pass:
            failures.append(f"{name}: expected pass={should_pass}, got {reason}")

    docker_root = make_croot("c_docker")
    docker_line = "The project ships a `Dockerfile`."
    (docker_root / "README.md").write_text(docker_line + "\n", encoding="utf-8")
    docker_entry = {
        "repo": "t",
        "op_id": "t",
        "kind": "claim_dockerfile",
        "doc_path": "README.md",
        "target": "Dockerfile",
        "new": docker_line,
    }
    expect_at("claim_dockerfile-ok", docker_root, docker_entry, True)
    (docker_root / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
    expect_at("claim_dockerfile-present", docker_root, docker_entry, False)

    ci_root = make_croot("c_ci")
    ci_line = "CI runs on GitHub Actions."
    (ci_root / "README.md").write_text(ci_line + "\n", encoding="utf-8")
    ci_entry = {
        "repo": "t",
        "op_id": "t",
        "kind": "claim_ci_workflow",
        "doc_path": "README.md",
        "target": "GitHub Actions",
        "new": ci_line,
    }
    expect_at("claim_ci-ok", ci_root, ci_entry, True)
    (ci_root / ".github" / "workflows").mkdir(parents=True)
    (ci_root / ".github" / "workflows" / "ci.yml").write_text("on: push\n", encoding="utf-8")
    expect_at("claim_ci-present", ci_root, ci_entry, False)

    lic_root = make_croot("c_license")
    lic_line = "The project is released under the MIT license."
    (lic_root / "README.md").write_text(lic_line + "\n", encoding="utf-8")
    lic_entry = {
        "repo": "t",
        "op_id": "t",
        "kind": "claim_license",
        "doc_path": "README.md",
        "file": "pyproject.toml",
        "old": "MIT",
        "new": lic_line,
    }
    expect_at("claim_license-mismatch", lic_root, lic_entry, True)
    (lic_root / "README.md").write_text(
        "The project is released under the Apache-2.0 license.\n", encoding="utf-8"
    )
    expect_at(
        "claim_license-match",
        lic_root,
        {
            **lic_entry,
            "old": "Apache-2.0",
            "new": "The project is released under the Apache-2.0 license.",
        },
        False,
    )

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SELFTEST OK (oracle checks pass and fail as expected)")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", help="manifest.jsonl to verify")
    ap.add_argument("--snapshots", help="snapshots directory containing <repo>__injected")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.manifest or not args.snapshots:
        ap.error("--manifest and --snapshots are required (or use --selftest)")

    ok, total, errors = verify_manifest(Path(args.manifest), Path(args.snapshots))
    print(f"verified {ok}/{total} injected entries")
    for err in errors:
        print(f"  - {err}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
