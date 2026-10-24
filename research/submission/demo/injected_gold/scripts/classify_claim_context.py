"""Engine-free claim-form / context classifier for Stage C annotation (S0).

Deterministic, standard-library only. It **never imports** ``docassay`` and
never reads tool output. Given a document, the project module inventory, the
declared dependencies, and the tracked paths, it assigns the frozen labels from
``runs/stage-c-2026-10-20/taxonomy.json``:

- ``claim_form``: ``path`` / ``dependency`` / ``qualified`` /
  ``section_qualified`` / ``bare_call`` / ``bare`` / ``not_a_claim``
- ``context_source``: ``heading`` / ``table`` / ``prose`` / ``list`` /
  ``path_prose`` / ``none``
- ``context_module`` and ``context_line`` where a section qualification applies.

The rules are the normative §9.1 text of
``validation/stage-c-plan.md`` and ``SCOPE.md`` §3.3.2. This classifier is a
label comparator for T4/T5, not the engine: its labels are reported next to
independent labels, never substituted for them.

Run::

    PYTHONPATH=src uv run python .../scripts/classify_claim_context.py --self-check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

BACKTICK_RE = re.compile(r"`([^`\n]+)`")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DOTTED_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$")
CALL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(\)$")
SIGNATURE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*(?:->.*)?$")
VERSION_RE = re.compile(r"^(.*?)\s*(?:>=|<=|==|!=|~=|>|<)\s*[0-9]")
PATH_EXT = (".py", ".md", ".rst", ".txt", ".toml", ".yaml", ".yml", ".json",
            ".csv", ".tsv", ".ini", ".cfg", ".sh", ".cfg", ".lock")
BUILTINS = frozenset(
    """abs all any ascii bin bool breakpoint bytearray bytes callable chr classmethod
    compile complex delattr dict dir divmod enumerate eval exec filter float format
    frozenset getattr globals hasattr hash help hex id input int isinstance issubclass
    iter len list locals map max memoryview min next object oct open ord pow print
    property range repr reversed round set setattr slice sorted staticmethod str sum
    super tuple type vars zip None True False""".split()
)
KEYWORDS = frozenset(
    """and as assert async await break class continue def del elif else except finally
    for from global if import in is lambda nonlocal not or pass raise return try while
    with yield match case""".split()
)
USAGE_VERBS = (
    "uses", "use", "calls", "call", "invokes", "invoke", "wraps", "wrap",
    "delegates to", "delegate to", "is used by", "are used by", "depends on",
    "depend on", "imports", "import", "returns", "return",
)
DECLARATION_VERBS = (
    "provides", "provide", "declares", "declare", "exposes", "expose",
    "contains", "contain", "defines", "define", "documents", "document",
    "includes", "include",
)
NOT_CURRENT = (
    "before ", "after ", "will be removed", "used to", "migrate", "migration",
    "deprecated", "legacy", "no longer", "planned", "roadmap", "not yet",
    "future", "historical",
)


@dataclass(frozen=True)
class Label:
    claim_form: str
    context_source: str
    context_module: str | None = None
    context_line: int | None = None
    reason: str = ""


def _token_kind(token: str) -> str:
    token = token.strip()
    if not token:
        return "empty"
    if "/" in token and not token.startswith("/"):
        return "path"
    if token.lower().endswith(PATH_EXT):
        return "path"
    if CALL_RE.fullmatch(token):
        return "bare_call"
    if SIGNATURE_RE.fullmatch(token) and "(" in token:
        return "bare_call"
    if DOTTED_RE.fullmatch(token):
        return "dotted"
    if IDENT_RE.fullmatch(token):
        return "bare"
    return "other"


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


KIND_PREFIX_RE = re.compile(
    r"^(?:class|def|function|method|property|attribute|constant)\s+", re.IGNORECASE
)


def _strip_kind_prefix(token: str) -> str:
    token = token.strip()
    if token.startswith("`") and token.endswith("`"):
        token = token[1:-1].strip()
    return KIND_PREFIX_RE.sub("", token.strip())


def _is_member_heading(title: str) -> bool:
    """A code-shaped member/signature subheading (backticked or `class X`)."""
    if "`" in title:
        return _member_token(title) is not None
    return bool(KIND_PREFIX_RE.match(title.strip())) and _member_token(title) is not None


def _member_token(token: str) -> str | None:
    """Return the bare member name if ``token`` is a code-shaped member token."""
    token = _strip_kind_prefix(token)
    kind = _token_kind(token)
    if kind in ("path", "other", "empty"):
        return None
    if kind == "dotted":
        return None
    if kind == "bare_call":
        name = token.split("(", 1)[0]
    else:
        name = token
    if not IDENT_RE.fullmatch(name):
        return None
    if _is_dunder(name) or name in BUILTINS or name in KEYWORDS:
        return None
    return name


def _module_token(token: str, modules: frozenset[str]) -> str | None:
    """A token that resolves to a project module (dotted module or .py path)."""
    token = token.strip()
    if token in modules:
        return token
    if token.lower().endswith(".py"):
        candidate = token.replace("/", ".")[:-3]
        if candidate in modules:
            return candidate
        for module in modules:
            if module.replace(".", "/") + ".py" == token:
                return module
    return None


def _find_module(text: str, modules: frozenset[str]) -> str | None:
    for match in BACKTICK_RE.finditer(text):
        module = _module_token(match.group(1), modules)
        if module:
            return module
    for word in re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", text):
        module = _module_token(word, modules)
        if module:
            return module
    return None


def _has_usage_gap(text: str, module: str, name: str) -> bool:
    """A usage verb between the module reference and the token blocks qualification."""
    low = text.lower()
    module_at = low.find(module.lower())
    name_at = low.find(name.lower())
    if module_at < 0 or name_at < 0:
        return False
    gap = low[min(module_at, name_at): max(module_at, name_at)]
    if name_at < module_at:
        return False
    for verb in USAGE_VERBS:
        if re.search(rf"\b{re.escape(verb)}\b", gap):
            if any(re.search(rf"\b{re.escape(v)}\b", gap) for v in DECLARATION_VERBS):
                return False
            return True
    return False


def _table_module(line: str, modules: frozenset[str]) -> str | None:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    for cell in cells:
        for token in re.findall(r"`([^`]+)`", cell):
            module = _module_token(token, modules)
            if module:
                return module
        module = _module_token(cell, modules)
        if module:
            return module
    return None


def classify_line(
    line: str,
    *,
    heading_module: str | None = None,
    heading_line: int | None = None,
    modules: frozenset[str] = frozenset(),
    dependencies: frozenset[str] = frozenset(),
    paths: frozenset[str] = frozenset(),
    table: bool = False,
    list_item: bool = False,
) -> Label:
    """Classify one physical line (outside a fence)."""
    text = line.strip()
    low = text.lower()
    if not text or text.startswith("```") or text.startswith("~~~"):
        return Label("not_a_claim", "none", reason="fence_or_blank")
    if any(marker in low for marker in NOT_CURRENT):
        # A historical line is not a current-state claim for annotation.
        return Label("not_a_claim", "none", reason="not_current")

    inline = [m.group(1).strip() for m in BACKTICK_RE.finditer(text)]
    links = [m.group(1).strip() for m in LINK_RE.finditer(text)]
    tokens = inline + links

    # Dependency mentions: a declared dependency name, with or without a constraint.
    dep_hits: list[str] = []
    for token in tokens:
        base = VERSION_RE.match(token)
        name = (base.group(1) if base else token).strip().strip("`").lower()
        if name in dependencies:
            dep_hits.append(name)
    if dep_hits:
        return Label("dependency", "none", reason="declared_dependency")

    # Path mentions.
    path_hits = [t for t in tokens if _token_kind(t) == "path"]
    if path_hits:
        return Label("path", "none", reason="path_token")

    # Document-written qualified symbol (not the module token itself).
    for token in tokens:
        if _token_kind(token) == "dotted" and _module_token(token, modules) is None:
            top = token.split(".", 1)[0]
            if top in {m.split(".", 1)[0] for m in modules}:
                return Label("qualified", "none", reason="dotted_project_name")

    # Section-qualified: a bare member under a document-supplied module context.
    members = [name for name in (_member_token(t) for t in tokens) if name]
    if len(members) == 1:
        token = next(t for t in tokens if _member_token(t) == members[0])
        line_module = _table_module(text, modules) if table else _find_module(text, modules)
        module = line_module or heading_module
        source = "none"
        context_line = heading_line
        if line_module:
            source = "table" if table else "prose"
            context_line = None
            if _has_usage_gap(text, line_module, members[0]):
                return Label(
                    "bare",
                    "none",
                    reason="usage_verb_gap",
                )
            # path_prose: a .py path that resolves to the module.
            if any(t.strip().lower().endswith(".py") for t in tokens):
                source = "path_prose"
        elif heading_module:
            source = "heading"
        if module:
            if list_item and source == "heading":
                source = "list"
            return Label(
                "section_qualified",
                source,
                context_module=module,
                context_line=context_line,
                reason="module_context",
            )

    # Bare forms.
    call = next((t for t in tokens if _token_kind(t) == "bare_call"), None)
    if call:
        return Label("bare_call", "none", reason="bare_call")
    if members:
        return Label("bare", "none", reason="bare_member")
    return Label("not_a_claim", "none", reason="no_code_shaped_token")


def classify_document(
    text: str,
    *,
    modules: frozenset[str] = frozenset(),
    dependencies: frozenset[str] = frozenset(),
    paths: frozenset[str] = frozenset(),
) -> list[dict]:
    """Classify every line of a document, maintaining heading module context."""
    rows: list[dict] = []
    stack: list[tuple[int, str]] = []  # (level, module)
    heading_module: str | None = None
    heading_line: int | None = None
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            rows.append({"line": number, "text": line, "claim_form": "not_a_claim",
                         "context_source": "none", "context_module": None,
                         "context_line": None, "reason": "fence"})
            continue
        if in_fence:
            rows.append({"line": number, "text": line, "claim_form": "not_a_claim",
                         "context_source": "none", "context_module": None,
                         "context_line": None, "reason": "fence"})
            continue
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            module = _find_module(title, modules)
            if module:
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, module))
                heading_module, heading_line = module, number
                rows.append({"line": number, "text": line, "claim_form": "not_a_claim",
                             "context_source": "none", "context_module": None,
                             "context_line": None, "reason": "module_heading"})
                continue
            if _is_member_heading(title) and stack:
                # Member/signature subheading inherits the module and is itself
                # the annotated line.
                heading_module, heading_line = stack[-1][1], number
                rows.append({
                    "line": number,
                    "text": line,
                    "claim_form": "section_qualified",
                    "context_source": "heading",
                    "context_module": heading_module,
                    "context_line": heading_line,
                    "reason": "member_heading",
                })
                continue
            while stack and stack[-1][0] >= level:
                stack.pop()
            heading_module, heading_line = None, None
            rows.append({"line": number, "text": line, "claim_form": "not_a_claim",
                         "context_source": "none", "context_module": None,
                         "context_line": None, "reason": "heading"})
            continue
        label = classify_line(
            line,
            heading_module=heading_module,
            heading_line=heading_line,
            modules=modules,
            dependencies=dependencies,
            paths=paths,
            table=stripped.startswith("|"),
            list_item=bool(LIST_RE.match(line)),
        )
        rows.append({
            "line": number,
            "text": line,
            "claim_form": label.claim_form,
            "context_source": label.context_source,
            "context_module": label.context_module,
            "context_line": label.context_line,
            "reason": label.reason,
        })
    return rows


# --------------------------------------------------------------------------- #
# self-check: the normative boundary cases of §9.2
# --------------------------------------------------------------------------- #

MODULES = frozenset({"contourkit.grid", "contourkit.raster", "plotline.canvas",
                     "morpheme.lexicon", "palette.harmony"})


def _self_check() -> int:
    cases: list[tuple[str, dict, str, str]] = [
        ("## `contourkit.grid`\n\n### `sample()`\n",
         {"claim_form": "section_qualified", "context_source": "heading"}),
        ("## `contourkit.grid`\n\n## Notes\n\n`sample`\n",
         {"claim_form": "bare", "context_source": "none"}),
        ("## `plotline.canvas`\n\n### `class Canvas`\n",
         {"claim_form": "section_qualified", "context_source": "heading"}),
        ("## `contourkit.grid`\n\n`sample` and `simplify`\n",
         {"claim_form": "bare", "context_source": "none"}),
        ("The `contourkit.grid` module uses `sample`\n",
         {"claim_form": "bare", "context_source": "none"}),
        ("The `contourkit.grid` module provides `sample`\n",
         {"claim_form": "section_qualified", "context_source": "prose"}),
        ("| `Canvas` | `plotline.canvas` | drawing |\n",
         {"claim_form": "section_qualified", "context_source": "table"}),
        ("`numpy.array`\n", {"claim_form": "not_a_claim", "context_source": "none"}),
    ]
    failed = 0
    for text, expected in cases:
        rows = classify_document(text, modules=MODULES)
        substantive = [r for r in rows if r["claim_form"] != "not_a_claim"]
        if expected["claim_form"] == "not_a_claim":
            if substantive:
                print(f"FAIL (unexpected claim): {text!r} -> {substantive[-1]}")
                failed += 1
            continue
        if not substantive:
            print(f"FAIL (no claim): {text!r}")
            failed += 1
            continue
        got = substantive[-1] if len(substantive) > 1 else substantive[0]
        # A qualified foreign name is not a project claim; the line classifier
        # returns not_a_claim above, which is the expected label here.
        for key, value in expected.items():
            actual = got[key]
            if actual != value:
                print(f"FAIL {key}: {text!r} -> {actual!r} != {value!r}")
                failed += 1
    if failed:
        print(f"SELF-CHECK FAILED: {failed} case(s)")
        return 1
    print(f"SELF-CHECK OK: {len(cases)} boundary cases")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--document", default="")
    ap.add_argument("--modules", default="", help="comma-separated module names")
    ap.add_argument("--dependencies", default="", help="comma-separated package names")
    ap.add_argument("--paths", default="", help="comma-separated tracked paths")
    args = ap.parse_args(argv)
    if args.self_check:
        return _self_check()
    if not args.document:
        ap.print_help()
        return 2
    text = Path(args.document).read_text(encoding="utf-8")
    rows = classify_document(
        text,
        modules=frozenset(m.strip() for m in args.modules.split(",") if m.strip()),
        dependencies=frozenset(
            d.strip().lower() for d in args.dependencies.split(",") if d.strip()
        ),
        paths=frozenset(p.strip() for p in args.paths.split(",") if p.strip()),
    )
    json.dump(rows, sys.stdout, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
