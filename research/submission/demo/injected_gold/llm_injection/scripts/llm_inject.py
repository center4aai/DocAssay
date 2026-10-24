"""Autonomous, offline LLM-injection runner (protocol §4.2).

Three stages, runnable separately or together (``all``):

1. **prepare** — for each ``(corpus repo, drift class, sample)`` assemble a
   four-block prompt (system contract + per-class task + target repository +
   few-shot examples) into ``runs/<date>/injector_input/``. Engine-free: the
   inventory and document excerpts come from ``_corpus`` (standard library),
   never from ``src/docassay``.
2. **run** — drive the ``repo-injector`` subagent once per bundle via
   ``opencode run --agent repo-injector`` (the injector never touches the
   network; it only reads the bundle) and capture its one JSON proposal.
3. **finalize** — validate each proposal against ``prompts/output.schema.json``,
   apply it to a git-less snapshot, prove it with the engine-free oracle
   (``engine.oracle.verify_entry``), and freeze ``manifest.jsonl`` +
   ``provenance.json``. The engine is never imported here.

Run::

    B=research/submission/demo/injected_gold/llm_injection
    PYTHONPATH=src uv run python $B/scripts/llm_inject.py prepare --repos quillpad --seed 1
    PYTHONPATH=src uv run python $B/scripts/llm_inject.py run --model <provider/model>
    PYTHONPATH=src uv run python $B/scripts/llm_inject.py finalize
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve()
LLM = HERE.parents[1]
IG = LLM.parent
SYNTHETIC = IG / "synthetic"
SYNTHETIC_NATURAL = IG / "synthetic-natural"
_EXTRA_CORPUS: Path | None = None
BANK = LLM / "exemplars" / "bank.json"
PROMPTS = LLM / "prompts"
RUNS = LLM / "runs"
DEFAULT_RUN = RUNS / f"llm-{date.today().isoformat()}"

sys.path.insert(0, str(IG / "scripts"))
sys.path.insert(0, str(IG))
import _corpus  # noqa: E402
from engine import grammar  # noqa: E402
from engine.oracle import verify_entry  # noqa: E402

CLASSES = [
    "path-location-drift",
    "identifier-drift",
    "removed-referent-drift",
    "external-dependency-drift",
]
CLASS_TO_KIND = {
    "path-location-drift": "path_rename",
    "identifier-drift": "symbol_rename",
    "removed-referent-drift": "symbol_delete",
    "external-dependency-drift": "dependency_version_break",
}
CLASS_TO_FILE = {
    "path-location-drift": "class.path-location.md",
    "identifier-drift": "class.identifier.md",
    "removed-referent-drift": "class.removed-referent.md",
    "external-dependency-drift": "class.external-dependency.md",
}
CLASS_TO_ARTIFACT = {
    "path-location-drift": "path",
    "identifier-drift": "identifier",
    "removed-referent-drift": "referent",
    "external-dependency-drift": "dependency",
}
MAX_DOC_LINES = 400
MAX_EX_FILES = 2
MAX_EX_LINES = 8


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_json_object(text: str) -> dict | None:
    """Return the first balanced ``{...}`` object parsed from ``text``."""
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


def _resolve_repo(spec: str) -> Path:
    p = Path(spec)
    if p.is_dir():
        return p.resolve()
    roots = ([_EXTRA_CORPUS] if _EXTRA_CORPUS else []) + [SYNTHETIC, SYNTHETIC_NATURAL]
    for root in roots:
        cand = root / spec
        if cand.is_dir():
            return cand.resolve()
    raise SystemExit(f"corpus repo not found: {spec}")


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def render_inventory(inv: _corpus.RepoInventory) -> str:
    out = ["files:"]
    out.append("  " + ", ".join(sorted(inv.files)))
    syms = sorted({d.qualname for d in inv.defs if d.kind in ("class", "function")})
    out.append("symbols:")
    out.append("  " + (", ".join(syms) if syms else "(none)"))
    out.append("dependencies:")
    deps = [f"{name}{spec}" for name, spec in sorted(inv.deps.items())]
    out.append("  " + (", ".join(deps) if deps else "(none)"))
    lits = sorted(k for k in inv.str_literals if k and len(k) <= 60)
    out.append("string literals:")
    out.append("  " + (", ".join(lits[:60]) if lits else "(none)"))
    return "\n".join(out)


def render_doc_excerpts(src: Path) -> str:
    docs = _corpus.iter_doc_texts(src)
    out: list[str] = []
    used = 0
    for rel, text in docs:
        out.append(f"### {rel}")
        for i, line in enumerate(text.splitlines(), start=1):
            if used >= MAX_DOC_LINES:
                out.append("  … (truncated)")
                break
            out.append(f"{i:>4}: {line}")
            used += 1
    return "\n".join(out) if out else "(no documents)"


def render_exemplars(bank: dict, cls: str, n: int, rng: random.Random) -> tuple[str, list[str]]:
    pool = [
        e
        for e in bank["classes"][cls].get("triaged", [])
        if e.get("evidence") and e["evidence"].get("status") == "ok" and e["evidence"].get("files")
    ]
    pool.sort(key=lambda e: e["id"])
    chosen = pool if len(pool) <= n else rng.sample(sorted(pool, key=lambda e: e["id"]), n)
    chosen.sort(key=lambda e: e["id"])
    blocks: list[str] = []
    ids: list[str] = []
    for e in chosen:
        files = [f for f in e["evidence"]["files"] if f.get("removed") or f.get("added")]
        if not files:
            continue
        ids.append(e["id"])
        body = [f"### example {len(blocks) + 1}"]
        for f in files[:MAX_EX_FILES]:
            body.append(f"{f['path']} ({f['side']})")
            for line in f.get("removed", [])[:MAX_EX_LINES]:
                body.append(f"  - {line}")
            for line in f.get("added", [])[:MAX_EX_LINES]:
                body.append(f"  + {line}")
        blocks.append("\n".join(body))
    return ("\n\n".join(blocks) if blocks else "(no examples available)"), ids


def assemble_prompt(
    cls: str, repo: str, inv, src: Path, bank: dict, n_ex: int, rng, prompts_dir: Path = PROMPTS
) -> tuple[str, list[str]]:
    system = _read(Path(prompts_dir) / "injector.system.md")
    template = _read(Path(prompts_dir) / CLASS_TO_FILE[cls])
    ex_text, ids = render_exemplars(bank, cls, n_ex, rng)
    body = (
        template.replace("{{REPO_INVENTORY}}", render_inventory(inv))
        .replace("{{DOC_EXCERPTS}}", render_doc_excerpts(src))
        .replace("{{EXEMPLARS}}", ex_text)
    )
    header = f"# Injection task\n\ncorpus repository: `{repo}`\n"
    return header + "\n" + system + "\n\n---\n\n" + body + "\n", ids


# --------------------------------------------------------------------------- #
# stage 1: prepare
# --------------------------------------------------------------------------- #
def cmd_prepare(args) -> int:
    out = Path(args.out)
    (out / "injector_input").mkdir(parents=True, exist_ok=True)
    bank = json.loads(_read(BANK))
    prompts_dir = Path(getattr(args, "prompts", "") or PROMPTS)
    repos = [r for r in args.repos.split(",") if r]
    classes = [c for c in (args.classes.split(",") if args.classes else CLASSES) if c]
    seeds = [
        int(s) for s in (args.seeds.split(",") if getattr(args, "seeds", "") else []) if s.strip()
    ] or [args.seed]
    tasks: list[dict] = []
    for repo in repos:
        src = _resolve_repo(repo)
        inv = _corpus.build_inventory(src)
        repo_name = src.name
        for cls in classes:
            for seed in seeds:
                for sample in range(args.samples):
                    rng = random.Random(f"{seed}:{repo_name}:{cls}:{sample}")
                    prompt, ids = assemble_prompt(
                        cls, repo_name, inv, src, bank, args.exemplars, rng, prompts_dir
                    )
                    name = f"{repo_name}__{cls}__s{seed}_{sample}"
                    bundle = out / "injector_input" / f"{name}.md"
                    bundle.write_text(prompt, encoding="utf-8")
                    tasks.append(
                        {
                            "name": name,
                            "repo": repo_name,
                            # One mutation per snapshot: every bundle gets its
                            # own baseline/injected pair. Class and seed never
                            # share a snapshot, so a finding is attributable to
                            # exactly one mutation.
                            "snapshot_id": f"{repo_name}__{cls}__s{seed}_{sample}",
                            "src": str(src),
                            "class": cls,
                            "kind": CLASS_TO_KIND[cls],
                            "artifact_class": CLASS_TO_ARTIFACT[cls],
                            "sample": sample,
                            "seed": seed,
                            "bundle": str(bundle),
                            "prompt_sha256": _sha(prompt),
                            "prompts_dir": str(prompts_dir),
                            "exemplar_ids": ids,
                        }
                    )
    (out / "plan.json").write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"prepared {len(tasks)} prompt bundles -> {out / 'injector_input'}")
    return 0


# --------------------------------------------------------------------------- #
# stage 2: run
# --------------------------------------------------------------------------- #
def _run_opencode(bundle_text: str, model: str, agent: str, timeout: int) -> tuple[str, str]:
    cmd = ["opencode", "run", "--agent", agent, "--format", "json"]
    if model:
        cmd += ["--model", model]
    cmd.append(bundle_text)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return proc.stdout, proc.stderr


def _text_from_ndjson(stdout: str) -> str:
    chunks: list[str] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = ev.get("part") or {}
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            chunks.append(part["text"])
        elif ev.get("type") == "error":
            err = ev.get("error") or {}
            chunks.append(f"[error] {err.get('type')}: {err.get('message')}")
    return "\n".join(chunks)


def _filter_repos(plan: list[dict], repos: str) -> list[dict]:
    if not repos:
        return plan
    keep = {r for r in repos.split(",") if r}
    return [t for t in plan if t["repo"] in keep]


def cmd_run(args) -> int:
    out = Path(args.out)
    plan = _filter_repos(json.loads(_read(out / "plan.json")), getattr(args, "repos", ""))
    (out / "injector_output").mkdir(parents=True, exist_ok=True)
    model = args.model or os.environ.get("INJECTOR_MODEL", "")
    for task in plan:
        bundle_text = _read(Path(task["bundle"]))
        dest = out / "injector_output" / f"{task['name']}.json"
        if args.dry_run:
            print(f"[dry-run] would run: {task['name']} ({len(bundle_text)} chars)")
            continue
        try:
            stdout, stderr = _run_opencode(bundle_text, model, args.agent, args.timeout)
        except subprocess.TimeoutExpired:
            dest.write_text(
                json.dumps({"status": "timeout"}, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print(f"  {task['name']}: TIMEOUT")
            continue
        text = _text_from_ndjson(stdout)
        proposal = extract_json_object(text)
        payload = {
            "status": "ok" if proposal else "no_json",
            "proposal": proposal,
            "model": model,
            "raw_text": text,
            "stderr_tail": stderr[-1000:],
        }
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {task['name']}: {payload['status']}")
    print(f"ran injector on {len(plan)} bundles -> {out / 'injector_output'}")
    return 0


# --------------------------------------------------------------------------- #
# stage 3: finalize
# --------------------------------------------------------------------------- #
_REQUIRED = {
    "path_rename": ("old", "new", "target", "doc_path"),
    "symbol_rename": ("old", "new", "symbol", "target", "doc_path"),
    "symbol_delete": ("old", "symbol", "target", "doc_path"),
    "dependency_version_break": ("file", "new", "symbol", "target", "doc_path"),
    "dependency_remove": ("file", "old", "symbol", "target", "doc_path"),
}


def resolve_kind(task: dict, proposal: dict) -> str:
    """Infer the harness dispatch kind; the model never chooses it.

    Natural prompts ask for a drift *type*, not a harness field. For the
    external-dependency class, a null ``new`` (or an explicit removal form) is
    the removal mutation; otherwise it is a constraint break.
    """
    cls = task["class"]
    if cls == "path-location-drift":
        return "path_rename"
    if cls == "identifier-drift":
        return "symbol_rename"
    if cls == "removed-referent-drift":
        return "symbol_delete"
    if cls == "external-dependency-drift":
        if proposal.get("new") in (None, "") or proposal.get("form") == "removal":
            return "dependency_remove"
        return "dependency_version_break"
    return task["kind"]


def validate_proposal(p: dict, task: dict) -> str | None:
    if not isinstance(p, dict):
        return "not an object"
    if p.get("injectable") is False:
        return "injectable=false"
    if p.get("drift_type") != task["class"]:
        return f"drift_type mismatch: {p.get('drift_type')!r}"
    kind = resolve_kind(task, p)
    for field in _REQUIRED[kind]:
        if p.get(field) in (None, ""):
            if field == "new" and kind == "dependency_remove":
                continue
            return f"missing field: {field}"
    # A removal proposal must name the manifest entry it removes; the bare
    # dependency name is used to resolve it on disk.
    if kind == "dependency_remove" and not (p.get("old") or p.get("symbol")):
        return "removal proposal needs the dependency name"
    return None


def _find_line(src: Path, doc_path: str, target: str, doc_line_text: str = "") -> int:
    path = src / doc_path
    if not path.is_file():
        return 0
    lines = _read(path).splitlines()
    if doc_line_text:
        for i, line in enumerate(lines, start=1):
            if line.strip() == doc_line_text.strip():
                return i
    for i, line in enumerate(lines, start=1):
        if target and target in line:
            return i
    return 0


def _constraint(raw: str, symbol: str) -> str:
    """Return the constraint part of a natural dependency requirement.

    The class prompt asks for the new *constraint*, but a natural answer often
    writes the full requirement (``click>=999``, ``PyYAML>=999``).  The applier
    prefixes the dependency name itself, so strip a leading name here rather
    than treating a semantically valid proposal as a generator failure.  This
    is a harness parsing rule; it does not change the injector prompt or the
    tool.
    """
    raw = str(raw or "").strip()
    if not raw:
        return raw
    names = {symbol, symbol.replace("-", "_"), symbol.replace("_", "-")}
    for name in names:
        match = re.match(rf"^{re.escape(name)}\s*(?=[<>=!~].*$)", raw, re.IGNORECASE)
        if match:
            return raw[match.end() :].strip()
    return raw


def _build_cand(proposal: dict, kind: str, src: Path, inv) -> dict | None:
    doc_path = proposal["doc_path"]
    line = _find_line(src, doc_path, proposal["target"], proposal.get("doc_line_text", ""))
    if line <= 0:
        return None
    base = {
        "target": proposal["target"],
        "doc_path": doc_path,
        "line": line,
        "stratum": "direct_reference",
    }
    if kind == "path_rename":
        old = proposal["old"]
        return {**base, "file": old, "old": old, "new": proposal["new"]}
    if kind == "dependency_remove":
        return {
            **base,
            "file": proposal["file"],
            "symbol": proposal["symbol"].lower().replace("_", "-"),
            # ``old`` is the name as it appears in the manifest; the applier
            # uses it to find and remove the entry.
            "old": proposal.get("old") or proposal["symbol"],
            "new": None,
        }
    if kind == "dependency_version_break":
        symbol = proposal["symbol"].lower().replace("_", "-")
        raw_new = str(proposal["new"]).strip()
        return {
            **base,
            "file": proposal["file"],
            "symbol": symbol,
            "old": proposal.get("old") or "",
            "new": _constraint(raw_new, symbol),
            "new_raw": raw_new,
        }
    # symbol kinds: resolve the definition for its exact span
    defs = _corpus.resolve_symbol(inv, proposal["old"]) or _corpus.resolve_symbol(
        inv, proposal.get("symbol", "")
    )
    defs = [d for d in defs if d.kind != "method"]
    if len(defs) > 1 and proposal.get("file"):
        defs = [d for d in defs if d.file == proposal["file"]]
    if len(defs) != 1:
        return None
    d = defs[0]
    cand = {
        **base,
        "file": d.file,
        "old": d.qualname,
        "symbol": d.name,
        "lineno": d.lineno,
        "start_lineno": d.start_lineno or d.lineno,
        "end_lineno": d.end_lineno,
    }
    if kind == "symbol_rename":
        # The deterministic applier renames to ``<name>Injected`` (see
        # inject._apply); the injector's chosen replacement name is not used so
        # the oracle and the applier stay in agreement.
        cand["new"] = f"{d.name}Injected"
    return cand


def cmd_finalize(args) -> int:
    out = Path(args.out)
    plan = _filter_repos(json.loads(_read(out / "plan.json")), getattr(args, "repos", ""))
    snap_dir = out / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    provenance: list[dict] = []
    stats: dict[str, int] = {}
    by_class: dict[str, dict[str, int]] = {}
    planned_by_class: dict[str, int] = {}
    snaps: dict[str, Path] = {}
    invs: dict[str, object] = {}
    used_by: dict[str, set[tuple]] = {}
    targets_by: dict[str, set[str]] = {}

    for task in plan:
        planned_by_class[task["class"]] = planned_by_class.get(task["class"], 0) + 1

    def bump(status: str, cls: str) -> None:
        stats[status] = stats.get(status, 0) + 1
        row = by_class.setdefault(cls, {})
        row[status] = row.get(status, 0) + 1

    for task in plan:
        repo = task["repo"]
        cls = task["class"]
        snapshot = task.get("snapshot_id", repo)
        used = used_by.setdefault(snapshot, set())
        used_targets = targets_by.setdefault(snapshot, set())
        prop_file = out / "injector_output" / f"{task['name']}.json"
        prov = {
            "name": task["name"],
            "repo": repo,
            "snapshot_id": snapshot,
            "drift_type": cls,
            "seed": task["seed"],
            "prompt_sha256": task["prompt_sha256"],
            "prompts_dir": task.get("prompts_dir", ""),
            "exemplar_ids": task["exemplar_ids"],
            "injector_model": "",
        }

        if not prop_file.is_file():
            prov["status"] = "no_output"
            prov["verifier"] = "no_output"
            provenance.append(prov)
            bump("no_output", cls)
            continue

        payload = json.loads(_read(prop_file))
        proposal = payload.get("proposal")
        prov["injector_model"] = payload.get("model", "")
        if payload.get("status") == "timeout":
            prov["status"] = "timeout"
            prov["verifier"] = "timeout"
            provenance.append(prov)
            bump("timeout", cls)
            continue
        if not isinstance(proposal, dict):
            prov["status"] = "no_json"
            prov["verifier"] = "no_json"
            provenance.append(prov)
            bump("no_json", cls)
            continue
        if proposal.get("injectable") is False:
            prov["status"] = "declined"
            prov["verifier"] = "declined"
            prov["decline_reason"] = proposal.get("reason", "")
            provenance.append(prov)
            bump("declined", cls)
            continue

        kind = resolve_kind(task, proposal)
        prov["kind"] = kind
        err = validate_proposal(proposal, task)
        if err:
            prov["status"] = "invalid"
            prov["verifier"] = f"rejected: {err}"
            provenance.append(prov)
            bump("invalid", cls)
            continue

        src = Path(task["src"])
        if snapshot not in snaps:
            snaps[snapshot] = snap_dir / f"{snapshot}__injected"
            grammar.snapshot(src, snaps[snapshot])
            grammar.snapshot(src, snap_dir / f"{snapshot}__baseline")
            invs[snapshot] = _corpus.build_inventory(src)
        snap, inv = snaps[snapshot], invs[snapshot]

        cand = _build_cand(proposal, kind, src, inv)
        if cand is None:
            prov["status"] = "unresolved"
            prov["verifier"] = "rejected: candidate could not be resolved on disk"
            provenance.append(prov)
            bump("unresolved", cls)
            continue
        res = grammar.resources(kind, cand)
        target = str(cand["target"])
        if any(r in used for r in res) or target in used_targets:
            prov["status"] = "conflict"
            prov["verifier"] = "skipped: resource conflict"
            provenance.append(prov)
            bump("conflict", cls)
            continue

        entry = _assemble_entry(task, proposal, cand, kind)
        undo = grammar.apply_mutation(snap, kind, cand)
        if undo is None:
            prov["status"] = "apply_failed"
            prov["verifier"] = "rejected: mutation could not be applied"
            provenance.append(prov)
            bump("apply_failed", cls)
            continue
        passed, reason = verify_entry(entry, snap)
        if not passed:
            undo()
            prov["status"] = "verify_failed"
            prov["verifier"] = f"rejected: {reason}"
            provenance.append(prov)
            bump("verify_failed", cls)
            continue
        entry["verifier"] = "ok"
        manifest.append(entry)
        prov["status"] = "verified"
        prov["verifier"] = "ok"
        provenance.append(prov)
        used.update(res)
        used_targets.add(target)
        bump("verified", cls)

    for cls in planned_by_class:
        by_class.setdefault(cls, {})
    stats_payload = {
        "planned": len(plan),
        "overall": dict(sorted(stats.items())),
        "by_class": {
            cls: {"planned": planned_by_class.get(cls, 0), **dict(sorted(row.items()))}
            for cls, row in sorted(by_class.items())
        },
    }

    (out / "manifest.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in manifest), encoding="utf-8"
    )
    (out / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "stats.json").write_text(
        json.dumps(stats_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"finalized {len(manifest)}/{len(plan)} -> {out / 'manifest.jsonl'}")
    print(f"  stats: {stats}")
    return 0


def _assemble_entry(task: dict, proposal: dict, cand: dict, kind: str | None = None) -> dict:
    kind = kind or task["kind"]
    old = cand.get("old")
    if kind == "dependency_remove":
        # The oracle checks the normalized manifest key; the applier already
        # used the raw manifest name.
        old = cand.get("symbol") or old
    if kind == "dependency_remove":
        form = "removal"
    elif kind == "dependency_version_break":
        form = "constraint"
    else:
        form = "n/a"
    return {
        "repo": task.get("snapshot_id", task["repo"]),
        "repo_name": task["repo"],
        "snapshot_id": task.get("snapshot_id", task["repo"]),
        "op_id": f"llm.{task['class']}",
        "canonical_class": task["class"],
        "artifact_class": task["artifact_class"],
        "kind": kind,
        "form": form,
        "control": "none",
        "expected_verdict": "refuted",
        "surface": task["artifact_class"],
        "target": cand["target"],
        "doc_path": cand["doc_path"],
        "line": cand["line"],
        "file": cand.get("file"),
        "old": old,
        "new": cand.get("new"),
        "new_raw": cand.get("new_raw"),
        "symbol": cand.get("symbol"),
        "seed": task["seed"],
        "prompt_sha256": task.get("prompt_sha256", ""),
        "exemplar_ids": task["exemplar_ids"],
        "rationale": proposal.get("rationale", ""),
        "target_claim": proposal.get("target_claim", ""),
    }


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #
def _add_out(ap) -> None:
    ap.add_argument("--out", default=str(DEFAULT_RUN), help="run directory")


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="assemble prompt bundles + plan")
    p.add_argument("--repos", default="quillpad")
    p.add_argument("--classes", default="")
    p.add_argument("--samples", type=int, default=1)
    p.add_argument("--exemplars", type=int, default=4)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--seeds", default="", help="comma-separated seeds; overrides --seed")
    p.add_argument("--prompts", default=str(PROMPTS), help="prompt directory")
    p.add_argument("--corpus-dir", default="", help="extra corpus root (Stage C)")
    _add_out(p)
    p.set_defaults(func=cmd_prepare)

    r = sub.add_parser("run", help="drive the repo-injector subagent")
    r.add_argument("--repos", default="", help="subset of repos from the plan (default: all)")
    r.add_argument("--corpus-dir", default="", help="extra corpus root (Stage C)")
    r.add_argument(
        "--model", default="", help="provider/model (default: $INJECTOR_MODEL or opencode default)"
    )
    r.add_argument("--agent", default="repo-injector")
    r.add_argument("--timeout", type=int, default=240)
    r.add_argument("--dry-run", action="store_true")
    _add_out(r)
    r.set_defaults(func=cmd_run)

    f = sub.add_parser("finalize", help="validate + apply + verify + freeze manifest")
    f.add_argument("--repos", default="", help="subset of repos from the plan (default: all)")
    _add_out(f)
    f.set_defaults(func=cmd_finalize)

    a = sub.add_parser("all", help="prepare + run + finalize")
    a.add_argument("--repos", default="quillpad")
    a.add_argument("--classes", default="")
    a.add_argument("--samples", type=int, default=1)
    a.add_argument("--exemplars", type=int, default=4)
    a.add_argument("--seed", type=int, default=1)
    a.add_argument("--seeds", default="", help="comma-separated seeds; overrides --seed")
    a.add_argument("--model", default="")
    a.add_argument("--agent", default="repo-injector")
    a.add_argument("--timeout", type=int, default=240)
    a.add_argument("--prompts", default=str(PROMPTS), help="prompt directory")
    a.add_argument("--corpus-dir", default="", help="extra corpus root (Stage C)")
    _add_out(a)
    a.set_defaults(func=None)

    args = ap.parse_args(argv)
    global _EXTRA_CORPUS
    if getattr(args, "corpus_dir", ""):
        _EXTRA_CORPUS = Path(args.corpus_dir).resolve()
    if args.cmd == "all":
        ns = argparse.Namespace(**vars(args))
        cmd_prepare(ns)
        cmd_run(ns)
        return cmd_finalize(ns)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
