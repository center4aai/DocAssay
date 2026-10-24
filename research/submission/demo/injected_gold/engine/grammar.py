"""Mutation grammar and on-disk applier (engine-free).

This is the part of the former ``scripts/inject.py`` that is **not** circular and
is still used: the set of mutation kinds and *how each kind is applied* to a
repository snapshot. The LLM injector
(``llm_injection/scripts/llm_inject.py``) reuses it; the retired *target
selection* (the operator registry) does not live here.

Standard library only — the engine is never imported. The retired registry, the
registry-driven driver and its samplers are archived under
the retired deterministic-operator pipeline (not shipped).
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path


def write_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8")
    return lambda: write_text(path, text)


def snapshot(src: Path, dst: Path, ignore=()) -> None:
    """Copy ``src`` to a git-less ``dst`` (mutations must be visible on disk)."""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", *ignore))


DOC_EDIT_KINDS = frozenset(
    {"command_change", "cross_doc_mutate", "translation_mutate", "doc_symbol_mutate"}
)
# Doc-side capability claims used by the conformance templates for the three
# predicate-defined artifact classes (license / dockerfile / ci_workflow). The
# mutation appends one recorded claim line; it changes no code.
CLAIM_KINDS = frozenset({"claim_dockerfile", "claim_ci_workflow", "claim_license"})
REPLACE_KINDS = frozenset(
    {
        "config_key_rename",
        "endpoint_rename",
        "schema_field_rename",
        "type_annot_mutate",
        "dependency_version_break",
        "dependency_remove",
    }
)


def conflicts(
    kind: str,
    cand: dict,
    renamed: set[str],
    touched: set[str],
    replacements: dict[str, list[str]],
) -> bool:
    """Whether a mutation conflicts with an earlier mutation on the same file.

    Content edits on the same file are independent (different symbol/line), but
    (a) a rename/delete removes a file other mutations may still rely on, and
    (b) two string replacements on one file must not overlap (``current_user``
    is a substring of ``get_current_user``; replacing one breaks the other).
    """
    doc = cand.get("doc_path", "")
    if kind == "path_rename":
        old, new = cand["old"], cand["new"]
        if old in renamed or old in touched or new in touched:
            return True
        return bool(doc) and (doc in renamed or doc in touched)
    file = cand.get("file")
    if file and file in renamed:
        return True
    if kind in DOC_EDIT_KINDS and doc and doc in renamed:
        return True
    if kind in REPLACE_KINDS:
        old = cand.get("old") or ""
        for prev in replacements.get(file or "", ()):
            if prev and old and (prev in old or old in prev):
                return True
    return False


def mark(
    kind: str,
    cand: dict,
    renamed: set[str],
    touched: set[str],
    replacements: dict[str, list[str]],
) -> None:
    doc = cand.get("doc_path", "")
    if kind == "path_rename":
        renamed.update({cand["old"], cand["new"]})
        touched.update({cand["old"], cand["new"]})
    file = cand.get("file")
    if file:
        touched.add(file)
    if doc:
        touched.add(doc)
    if kind in REPLACE_KINDS and file:
        replacements.setdefault(file, []).append(cand.get("old") or "")


def apply_mutation(snap: Path, kind: str, cand: dict):
    """Apply one mutation to ``snap``; return an undo callable or ``None``."""
    file = cand.get("file")
    if file and not (snap / file).is_file():
        return None
    if kind in DOC_EDIT_KINDS:
        doc = snap / cand["doc_path"]
        if not doc.is_file():
            return None

    if kind in CLAIM_KINDS:
        path = snap / cand["doc_path"]
        if not path.is_file():
            return None
        orig = path.read_text(encoding="utf-8", errors="ignore")
        sep = "" if orig.endswith("\n") or not orig else "\n"
        write_text(path, orig + sep + cand["new"] + "\n")
        return lambda: write_text(path, orig)

    if kind == "path_rename":
        old, new = snap / cand["old"], snap / cand["new"]
        if not old.is_file() or new.exists():
            return None
        new.parent.mkdir(parents=True, exist_ok=True)
        os.rename(old, new)
        return lambda: os.rename(new, old)

    if kind == "symbol_rename":
        path = snap / cand["file"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        lines = orig.splitlines(keepends=True)
        idx = cand["lineno"] - 1
        newline = re.sub(
            rf"\b{re.escape(cand['symbol'])}\b", f"{cand['symbol']}Injected", lines[idx], count=1
        )
        if newline == lines[idx]:
            return None
        lines[idx] = newline
        write_text(path, "".join(lines))
        return lambda: write_text(path, orig)

    if kind == "symbol_delete":
        path = snap / cand["file"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        lines = orig.splitlines(keepends=True)
        del lines[cand["start_lineno"] - 1 : cand["end_lineno"]]
        write_text(path, "".join(lines))
        return lambda: write_text(path, orig)

    if kind == "dependency_remove":
        path = snap / cand["file"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        dep = cand["old"]
        pattern = re.compile(
            rf"""["']{re.escape(dep)}([<>!=~;\[]?[^"']*)?["']\s*,?""", re.IGNORECASE
        )
        new = pattern.sub("", orig, count=1)
        if new == orig:
            lines = orig.splitlines(keepends=True)
            for i, line in enumerate(lines):
                if line.strip().lower().startswith(dep):
                    del lines[i]
                    new = "".join(lines)
                    break
        if new == orig:
            return None
        write_text(path, new)
        return lambda: write_text(path, orig)

    if kind == "dependency_version_break":
        path = snap / cand["file"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        dep = cand["symbol"]
        constraint = cand["new"]
        pattern = re.compile(rf"""["']{re.escape(dep)}[^"']*["']""", re.IGNORECASE)
        new = pattern.sub(f'"{dep}{constraint}"', orig, count=1)
        if new == orig:
            return None
        write_text(path, new)
        return lambda: write_text(path, orig)

    if kind in ("config_key_rename", "endpoint_rename", "schema_field_rename", "type_annot_mutate"):
        path = snap / cand["file"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        new = orig.replace(cand["old"], cand["new"])
        if new == orig:
            return None
        write_text(path, new)
        return lambda: write_text(path, orig)

    if kind == "enum_member_remove":
        path = snap / cand["file"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        lines = orig.splitlines(keepends=True)
        del lines[cand["lineno"] - 1]
        write_text(path, "".join(lines))
        return lambda: write_text(path, orig)

    if kind == "add_symbol":
        path = snap / cand["file"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        block = (
            f"\n\n\ndef {cand['new']}():\n"
            f'    """Injected public symbol (missing documentation)."""\n'
            "    return None\n"
        )
        write_text(path, orig + block)
        return lambda: write_text(path, orig)

    if kind == "command_change":
        path = snap / cand["doc_path"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        lines = orig.splitlines(keepends=True)
        idx = cand["line"] - 1
        keep = "\n" if lines[idx].endswith("\n") else ""
        lines[idx] = cand["new"] + keep
        write_text(path, "".join(lines))
        return lambda: write_text(path, orig)

    if kind in (
        "cross_doc_mutate",
        "translation_mutate",
        "doc_symbol_mutate",
    ):
        path = snap / cand["doc_path"]
        orig = path.read_text(encoding="utf-8", errors="ignore")
        lines = orig.splitlines(keepends=True)
        idx = cand["line"] - 1
        old_fmt, new_fmt = f"`{cand['old']}`", f"`{cand['new']}`"
        if old_fmt not in lines[idx]:
            return None
        lines[idx] = lines[idx].replace(old_fmt, new_fmt, 1)
        write_text(path, "".join(lines))
        return lambda: write_text(path, orig)

    if kind in ("control_present", "control_absent"):
        return lambda: None

    return None


def resources(kind: str, cand: dict) -> list[tuple]:
    """Resource ids a code-side mutation touches (for conflict avoidance)."""
    if kind == "path_rename":
        return [("path", cand["old"])]
    if kind in ("symbol_rename", "symbol_delete", "enum_member_remove"):
        # Line-number-based edits shift later lines: one such edit per file.
        return [("linefile", cand["file"])]
    if kind == "add_symbol":
        return [("file", cand["file"])]
    if kind in ("dependency_remove", "dependency_version_break"):
        return [("file", cand["file"], cand.get("symbol"))]
    if kind in (
        "config_key_rename",
        "endpoint_rename",
        "schema_field_rename",
        "type_annot_mutate",
    ):
        return [("file", cand["file"], cand.get("old"))]
    if kind in CLAIM_KINDS:
        return [("doc", cand.get("doc_path", ""), cand.get("line", 0))]
    return [("doc", cand.get("doc_path", ""), cand.get("line", 0))]
