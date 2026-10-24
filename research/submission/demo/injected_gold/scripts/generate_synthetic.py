"""Synthetic-corpus generator for the injected-gold evaluation.

Three deterministic subcommands (the LLM roles live in ``.opencode/agents`` and
are orchestrated by the agent, not by this script):

- ``spec-validate`` — schema + completeness check of a project ``spec.json``.
  Only ``project``, ``dependencies``, ``modules`` and ``docs`` are mandatory;
  surfaces such as config keys, endpoints, schema fields and enum members are
  optional so that a spec describes a natural project, not a checklist.
- ``materialize``   — write ``pyproject.toml`` + the package source tree of a
  project from its spec (the deterministic *code writer*, used as the "mode A"
  of the pilot). It never writes documentation.
- ``baseline-report`` — *diagnostic*: run the engine once on a frozen baseline
  and print what it finds. This is **not** an acceptance gate. Findings are
  recorded, never used to edit the docs or to select/repair a repository;
  accepting the corpus is the job of the independent audit (``repo-auditor``).

``check`` remains as a deprecated alias for ``baseline-report``. It prints a
warning and always exits 0 as long as the engine run itself succeeds, so no
caller can turn baseline findings into a corpus-acceptance criterion.

The engine (``docassay``) is invoked only by ``baseline-report``/``check``
and never influences spec content or documentation. Standard library only
otherwise.

Run::

    PYTHONPATH=src uv run python .../scripts/generate_synthetic.py spec-validate \\
        --spec .../synthetic/quillpad/spec.json
    PYTHONPATH=src uv run python .../scripts/generate_synthetic.py materialize \\
        --spec .../synthetic/quillpad/spec.json --out .../synthetic/quillpad
    PYTHONPATH=src uv run python .../scripts/generate_synthetic.py baseline-report \\
        --repo .../synthetic/quillpad
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ARTIFACT = SCRIPTS.parents[1]
INJECTED_GOLD = SCRIPTS.parent
REPO_ROOT = INJECTED_GOLD.parents[2]

# Only the four structural keys are mandatory. The remaining surfaces are
# natural-project options: a library may have no HTTP endpoints, no schema
# fields, no enum members, no configuration keys, and no example commands.
# Requiring them would make the spec a checklist of tool-visible surfaces
# rather than a description of a project.
REQUIRED_KEYS = (
    "project",
    "dependencies",
    "modules",
    "docs",
)

OPTIONAL_LIST_KEYS = (
    "config_keys",
    "endpoints",
    "schema_fields",
    "enum_members",
    "example_commands",
    "paths",
)


# --------------------------------------------------------------------------- #
# spec validation
# --------------------------------------------------------------------------- #
def load_spec(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_spec(spec: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_KEYS:
        if key not in spec:
            errors.append(f"missing key: {key}")
    if errors:
        return errors

    project = spec["project"]
    if not isinstance(project, dict):
        return ["project must be an object"]
    for field in ("name", "pkg", "version", "description"):
        if not project.get(field):
            errors.append(f"project.{field} is required")

    if not isinstance(spec["modules"], list) or not spec["modules"]:
        errors.append("modules must be a non-empty list")
        return errors
    if not isinstance(spec["docs"], list) or not spec["docs"]:
        errors.append("docs must be a non-empty list")
        return errors
    if not isinstance(spec["dependencies"], list):
        errors.append("dependencies must be a list")

    for m in spec["modules"]:
        if not isinstance(m, dict):
            errors.append("module entries must be objects")
            continue
        if not m.get("path", "").endswith(".py"):
            errors.append(f"module path must be a .py file: {m.get('path')!r}")
        symbols = m.get("symbols", [])
        if not isinstance(symbols, list):
            errors.append(f"{m.get('path')}: symbols must be a list")
            continue
        for s in symbols:
            if not isinstance(s, dict):
                errors.append(f"{m.get('path')}: symbol entries must be objects")
                continue
            if not s.get("name"):
                errors.append(f"{m.get('path')}: symbol needs a name")
            if s.get("kind") not in ("class", "function", "constant"):
                errors.append(f"{m.get('path')}: bad symbol kind {s.get('kind')!r}")
            rt = s.get("return_type")
            # Natural projects use builtins, generics, and third-party types.
            # We only require that an annotation, if present, is a string.
            if rt is not None and not isinstance(rt, str):
                errors.append(f"{m.get('path')}: return_type must be a string or null")
            members = s.get("members")
            if members is not None and not isinstance(members, list):
                errors.append(f"{m.get('path')}: members must be a list")

    for dep in spec["dependencies"]:
        if not isinstance(dep, dict) or not dep.get("name"):
            errors.append("dependency entries need a name")

    for key in OPTIONAL_LIST_KEYS:
        value = spec.get(key)
        if value is not None and not isinstance(value, list):
            errors.append(f"{key} must be a list when present")
        elif isinstance(value, list) and any(not isinstance(v, str) for v in value):
            errors.append(f"{key} entries must be strings")

    data_files = spec.get("data_files", [])
    if data_files is not None and not isinstance(data_files, list):
        errors.append("data_files must be a list when present")
    elif isinstance(data_files, list):
        for data in data_files:
            if not isinstance(data, dict) or not data.get("path"):
                errors.append("data_files entries need path")
            elif not (data.get("content") or data.get("text")):
                errors.append("data_files entries need content/text")

    for doc in spec["docs"]:
        if not isinstance(doc, dict) or not doc.get("path"):
            errors.append("docs entries need a path")
    return errors


# --------------------------------------------------------------------------- #
# deterministic code materialization ("mode A" code writer)
# --------------------------------------------------------------------------- #
def _q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _pyproject(spec: dict) -> str:
    project = spec["project"]
    deps = [f"{d['name']}{d.get('constraint', '')}" for d in spec["dependencies"]]
    deps_toml = ",\n".join(f"    {_q(d)}" for d in deps)
    return (
        "[build-system]\n"
        'requires = ["setuptools>=68"]\n'
        'build-backend = "setuptools.build_meta"\n'
        "\n"
        "[project]\n"
        f"name = {_q(project['name'])}\n"
        f"version = {_q(project['version'])}\n"
        f"description = {_q(project['description'])}\n"
        'requires-python = ">=3.11"\n'
        "dependencies = [\n"
        f"{deps_toml}\n"
        "]\n"
        "\n"
        "[tool.setuptools]\n"
        f"packages = [{_q(project['pkg'])}]\n"
    )


def _class_src(symbol: dict) -> str:
    members = symbol.get("members") or []
    lines = [f"class {symbol['name']}:", '    """Project class."""', ""]
    lines.append("    def __init__(self) -> None:")
    if members:
        for member in members:
            lines.append(f"        self.{member} = None")
    else:
        lines.append("        pass")
    lines.append("")
    return "\n".join(lines)


def _function_src(symbol: dict) -> str:
    rt = symbol.get("return_type")
    ret = f" -> {rt}" if rt else ""
    return (
        f"def {symbol['name']}(){ret}:\n"
        '    """Project function."""\n'
        "    return None\n"
    )


def _literal_dict(name: str, values: list[str], value_default: str = "") -> str:
    rows = ",\n".join(f"    {_q(v)}: {_q(value_default)}" for v in values)
    return f"{name} = {{\n{rows},\n}}\n"


def _enum_block(members: list[str]) -> str:
    return "\n".join(f"{m} = {_q(m.lower())}" for m in members) + "\n"


def materialize(spec: dict, out: Path) -> list[str]:
    out = Path(out)
    pkg = spec["project"]["pkg"]
    pkg_dir = out / pkg
    pkg_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    def write(rel: str, text: str) -> None:
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(rel)

    write("pyproject.toml", _pyproject(spec))

    modules = spec["modules"]

    def target_module(preferred: list[str], fallback: str) -> str:
        for stem in preferred:
            for m in modules:
                if Path(m["path"]).stem == stem:
                    return m["path"]
        # Dedicated, definition-free module so this surface never collides with
        # the symbol operators (which key on the file that holds a def).
        return f"{pkg}/{fallback}.py"

    config_keys = spec.get("config_keys") or []
    endpoints = spec.get("endpoints") or []
    schema_fields = spec.get("schema_fields") or []
    enum_members = spec.get("enum_members") or []

    # Optional surfaces: do not create a module for a surface the project does
    # not have. This keeps the materialized tree natural instead of adding
    # empty config/routes/fields/constants files to every project.
    config_mod = target_module(["config", "settings"], "config") if config_keys else ""
    routes_mod = target_module(["routes", "router"], "routes") if endpoints else ""
    fields_mod = target_module(["models", "schemas"], "fields") if schema_fields else ""
    enum_mod = target_module(["constants", "enums"], "constants") if enum_members else ""

    def literal_block(rel: str) -> str:
        blocks: list[str] = []
        if config_mod and rel == config_mod and config_keys:
            blocks.append(_literal_dict("ENV_DEFAULTS", config_keys))
        if routes_mod and rel == routes_mod and endpoints:
            blocks.append(_literal_dict("ROUTES", endpoints, "handler"))
        if fields_mod and rel == fields_mod and schema_fields:
            blocks.append(_literal_dict("FIELDS", schema_fields, "str"))
        if enum_mod and rel == enum_mod and enum_members:
            blocks.append(_enum_block(enum_members))
        return "\n\n".join(blocks)

    module_paths = {m["path"] for m in modules}
    enum_set = set(enum_members)
    for m in modules:
        rel = m["path"]
        parts = [f'"""Module {rel}."""', "from __future__ import annotations", ""]
        for s in m.get("symbols", []):
            if s.get("kind") == "class":
                parts.append(_class_src(s))
            elif s.get("kind") == "function":
                parts.append(_function_src(s))
            elif s.get("kind") == "constant" and s.get("name") not in enum_set:
                # A natural project may declare a constant directly in its
                # module. Constants that are also enum_members keep the legacy
                # placement (one assignment in the enum module) so the existing
                # dev corpus materializes identically.
                parts.append(f"{s['name']} = {_q(s['name'].lower())}\n")
        body = "\n".join(parts).rstrip() + "\n"
        block = literal_block(rel)
        if block:
            body += "\n\n" + block
        write(rel, body)

    for extra in (config_mod, routes_mod, fields_mod, enum_mod):
        if not extra:
            continue
        if extra in module_paths or extra == f"{pkg}/__init__.py":
            continue
        block = literal_block(extra)
        if block:
            write(
                extra,
                f'"""Module {extra}."""\nfrom __future__ import annotations\n\n{block}',
            )

    write(
        f"{pkg}/__init__.py",
        f'"""Package {pkg}."""\n'
        f'__version__ = {_q(spec["project"]["version"])}\n',
    )
    for data in spec.get("data_files", []):
        write(data["path"], data.get("content") or data.get("text") or "")
    return written


# --------------------------------------------------------------------------- #
# baseline diagnostic (NOT an acceptance gate)
# --------------------------------------------------------------------------- #
def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True)


def _load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def baseline_report(repo: Path) -> dict:
    """Report what the engine finds on a frozen baseline. Diagnostic only.

    The result is a *record* of one engine run over one snapshot of the corpus.
    Nothing in this module consumes it: baseline findings must not be used to
    edit the documentation, to swap repositories, or to decide whether the
    corpus is accepted. Making docs "0 REFUTED" would tune them to the tool
    under test and hide its false positives. Corpus consistency is established
    independently, by the read-only audit against the spec and the source tree;
    the injected-vs-baseline finding diff is what makes an injection
    attributable.

    Raises ``SystemExit`` only when the engine itself fails to run.
    """
    repo = Path(repo).resolve()
    work = Path(tempfile.mkdtemp(prefix="synth-baseline-"))
    baseline_jsonl = work / "baseline.jsonl"

    proc = _run(
        [sys.executable, "-m", "docassay.core.dump_claims", str(repo), str(baseline_jsonl)],
        REPO_ROOT,
    )
    if proc.returncode != 0:
        raise SystemExit(f"dump_claims failed:\n{proc.stderr[-2000:]}")

    claims = _load_jsonl(baseline_jsonl)
    refuted = [c for c in claims if c.get("code_verdict") == "REFUTED"]
    nei = [c for c in claims if c.get("code_verdict") == "NEI"]
    supported = [c for c in claims if c.get("code_verdict") == "SUPPORTED"]

    return {
        "repo": str(repo),
        "diagnostic_only": True,
        "note": (
            "Recorded baseline findings. Not an acceptance criterion: do not "
            "edit docs, select, or repair a repository to change them. Corpus "
            "acceptance is the independent audit against spec + source."
        ),
        "baseline_claims": len(claims),
        "baseline_supported": len(supported),
        "baseline_refuted": len(refuted),
        "baseline_nei": len(nei),
        "refuted_examples": [
            {
                "predicate": c.get("predicate"),
                "object": c.get("object"),
                "source": c.get("source"),
                "line": c.get("line_start"),
                "reason": c.get("code_verdict_reason"),
            }
            for c in refuted[:15]
        ],
        "workdir": str(work),
    }


def check(repo: Path, **_deprecated_kwargs) -> dict:
    """Deprecated alias for :func:`baseline_report` (diagnostic only)."""
    warnings.warn(
        "check() is a deprecated alias for baseline_report(); baseline findings "
        "are diagnostic and must not gate corpus acceptance",
        DeprecationWarning,
        stacklevel=2,
    )
    return baseline_report(repo)


def _cmd_spec_validate(args: argparse.Namespace) -> int:
    spec = load_spec(Path(args.spec))
    errors = validate_spec(spec)
    if errors:
        print("SPEC INVALID:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"spec ok: {args.spec}")
    return 0


def _cmd_materialize(args: argparse.Namespace) -> int:
    spec = load_spec(Path(args.spec))
    errors = validate_spec(spec)
    if errors:
        print("SPEC INVALID:")
        for e in errors:
            print(f"  - {e}")
        return 1
    written = materialize(spec, Path(args.out))
    for rel in written:
        print(f"wrote {rel}")
    return 0


def _cmd_baseline_report(args: argparse.Namespace) -> int:
    """Print the baseline diagnostic. Always returns 0 if the engine ran."""
    report = baseline_report(Path(args.repo))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(
        "\nWARNING: baseline findings are DIAGNOSTIC ONLY. They must not be used "
        "to select or repair a corpus, nor to edit documentation. Corpus "
        "acceptance is the independent audit against spec + source.",
        file=sys.stderr,
    )
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    """Deprecated alias for ``baseline-report``; never gates acceptance."""
    print(
        "WARNING: 'check' is deprecated and is a DIAGNOSTIC, not an acceptance "
        "gate. It no longer fails on REFUTED claims; use 'baseline-report'. "
        "Baseline findings must not be used to select, repair, or edit a corpus.",
        file=sys.stderr,
    )
    return _cmd_baseline_report(args)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("spec-validate")
    p.add_argument("--spec", required=True)
    p.set_defaults(func=_cmd_spec_validate)

    p = sub.add_parser("materialize")
    p.add_argument("--spec", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=_cmd_materialize)

    p = sub.add_parser(
        "baseline-report",
        help="diagnostic: print what the engine finds on a frozen baseline",
    )
    p.add_argument("--repo", required=True)
    p.set_defaults(func=_cmd_baseline_report)

    p = sub.add_parser("check", help="deprecated alias for baseline-report")
    p.add_argument("--repo", required=True)
    # Accepted for compatibility with old invocations; ignored on purpose, so
    # that no tolerance can be read as a pass/fail threshold.
    p.add_argument("--refuted-tolerance", type=int, default=None, help=argparse.SUPPRESS)
    p.set_defaults(func=_cmd_check)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
