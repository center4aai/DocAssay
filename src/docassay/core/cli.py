"""Command-line interface for DocAssay (methodology §10).

Usage::

    docassay analyze [--format text|sarif] [--output F] [--fail-on none|refuted]
                             <repo_root>
    docassay dump <repo_root> <output.jsonl>
    docassay export <repo_root> <output.json>
    docassay export-md <repo_root> <output.md>
    docassay corpus-md [--dir DIR] [output]
    docassay report <repo_root> [--top-k N] [--sample-per-stratum M]
                       [--out findings.jsonl] [--review-out review.jsonl]
    docassay review <repo_root> <review.jsonl>
    docassay consolidate <review.jsonl ...> [--out aggregate.md]
    docassay mcp [--repo ROOT] [--refresh]

``analyze`` prints a verdict summary; ``dump`` writes one JSONL record per claim
with verdict, provenance and cross-document consistency; ``export`` writes the
self-contained JSON bundle (the contract the web viewer consumes); ``export-md``
renders it as a readable Markdown report; ``corpus-md`` aggregates a corpus.
``report`` prints the triage surface (top findings + noise budget + measurement
plan), ``review`` writes the labelled-review file, ``consolidate`` merges review
files into precision and confirmed-findings results. ``mcp`` serves the
deterministic fact inventory to a coding agent over the Model Context Protocol
(requires the ``agent`` extra).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from docassay.core.analyze_repo import analyze
from docassay.core.bundle import corpus_markdown, write_bundle, write_markdown
from docassay.core.dump_claims import dump
from docassay.core.triage_report import report, review, run_consolidate


def _add_analyze_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("analyze", help="analyze a repository and print verdict summary")
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("--format", choices=("text", "sarif"), default="text", help="output format")
    parser.add_argument("--output", type=Path, default=None, help="SARIF output file")
    parser.add_argument(
        "--fail-on",
        choices=("none", "refuted"),
        default="none",
        help="exit with status 1 when a claim is refuted (CI and pre-commit use)",
    )


def _add_dump_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("dump", help="dump claims with verdicts to JSONL")
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("output", type=Path)


def _add_export_parsers(sub: argparse._SubParsersAction) -> None:
    export = sub.add_parser("export", help="write the JSON analysis bundle of a repository")
    export.add_argument("repo_root", type=Path)
    export.add_argument("output", type=Path)

    export_md = sub.add_parser("export-md", help="write a readable Markdown report of a repository")
    export_md.add_argument("repo_root", type=Path)
    export_md.add_argument("output", type=Path)

    corpus = sub.add_parser(
        "corpus-md",
        help="write the cross-repository aggregate Markdown (default dir: ./test_repos)",
    )
    corpus.add_argument("--dir", type=Path, default=None, help="corpus directory")
    corpus.add_argument(
        "output", type=Path, nargs="?", default=None, help="output file (default: stdout)"
    )


def _add_web_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("web", help="launch the web UI (requires the [web] extra)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="bind port (default: $DOCASSAY_PORT or 8000)",
    )
    parser.add_argument("--workdir", type=Path, default=None, help="server cache directory")
    parser.add_argument("--corpus", type=Path, default=None, help="corpus directory to list")
    parser.add_argument("--static", type=Path, default=None, help="built frontend directory")
    parser.add_argument(
        "--public-url",
        default=None,
        help="address to print for the UI when the host port differs "
        "(default: $DOCASSAY_PUBLIC_URL)",
    )
    parser.add_argument(
        "--allow-bare-index",
        action="store_true",
        help="redirect a loopback Host (localhost/127.0.0.1) to ?token= even when "
        "the connection arrives from a bridge (used by the demo container)",
    )
    parser.add_argument(
        "--allow-root",
        type=Path,
        action="append",
        default=None,
        help="allow local path analysis only under this root (repeatable)",
    )
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=None,
        help="extra Host header to answer; \"*\" disables the check (repeatable)",
    )


def _add_triage_parsers(sub: argparse._SubParsersAction) -> None:
    report_parser = sub.add_parser(
        "report", help="print the triage report (top findings + noise budget + measurement plan)"
    )
    report_parser.add_argument("repo_root", type=Path)
    report_parser.add_argument("--top-k", type=int, default=15, help="findings to rank for review")
    report_parser.add_argument(
        "--sample-per-stratum", type=int, default=5, help="review sample per stratum"
    )
    report_parser.add_argument("--seed", type=int, default=0, help="sampling seed (deterministic)")
    report_parser.add_argument("--out", type=Path, help="write all triage items to JSONL")
    report_parser.add_argument(
        "--review-out", type=Path, help="write the review JSONL for labelling"
    )

    review_parser = sub.add_parser(
        "review", help="write the review JSONL (top findings + stratified sample) for labelling"
    )
    review_parser.add_argument("repo_root", type=Path)
    review_parser.add_argument("output", type=Path)
    review_parser.add_argument("--top-k", type=int, default=15)
    review_parser.add_argument("--sample-per-stratum", type=int, default=5)
    review_parser.add_argument("--seed", type=int, default=0)

    consolidate = sub.add_parser(
        "consolidate", help="merge labelled review files into precision + confirmed findings"
    )
    consolidate.add_argument("review_files", type=Path, nargs="+")
    consolidate.add_argument("--out", type=Path, help="write the consolidation to a file")


def _add_mcp_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        "mcp", help="run the MCP server (deterministic source of truth for coding agents)"
    )
    parser.add_argument(
        "--repo", type=Path, default=Path("."), help="repository root to inventory (default: cwd)"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "rebuild the inventory on every list_facts/lookup query "
            "(verify_claim always re-runs the analysis)"
        ),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docassay")
    sub = parser.add_subparsers(dest="command", required=True)
    _add_analyze_parser(sub)
    _add_dump_parser(sub)
    _add_export_parsers(sub)
    _add_web_parser(sub)
    _add_triage_parsers(sub)
    _add_mcp_parser(sub)
    return parser


def _cmd_analyze(args: argparse.Namespace) -> int:
    return analyze(args.repo_root, fmt=args.format, output=args.output, fail_on=args.fail_on)


def _cmd_dump(args: argparse.Namespace) -> int:
    return dump(args.repo_root, args.output)


def _cmd_export(args: argparse.Namespace) -> int:
    return write_bundle(args.repo_root, args.output)


def _cmd_export_md(args: argparse.Namespace) -> int:
    return write_markdown(args.repo_root, args.output)


def _cmd_corpus_md(args: argparse.Namespace) -> int:
    return corpus_markdown(args.dir or Path("test_repos"), args.output)


def _cmd_web(args: argparse.Namespace) -> int:
    try:
        from docassay.webapp.server import run as run_web
    except ImportError:
        print("the web extra is not installed; run: uv sync --extra web", file=sys.stderr)
        return 3
    return run_web(
        host=args.host,
        port=args.port,
        workdir=args.workdir,
        corpus=args.corpus,
        static=args.static,
        allow_root=args.allow_root,
        allowed_hosts=args.allowed_host,
        public_url=args.public_url,
        allow_bare_index=args.allow_bare_index,
    )


def _cmd_report(args: argparse.Namespace) -> int:
    return report(
        args.repo_root,
        top_k=args.top_k,
        sample_per_stratum=args.sample_per_stratum,
        seed=args.seed,
        out_findings=args.out,
        review_out=args.review_out,
    )


def _cmd_review(args: argparse.Namespace) -> int:
    return review(
        args.repo_root,
        args.output,
        top_k=args.top_k,
        sample_per_stratum=args.sample_per_stratum,
        seed=args.seed,
    )


def _cmd_consolidate(args: argparse.Namespace) -> int:
    return run_consolidate(args.review_files, args.out)


def _cmd_mcp(args: argparse.Namespace) -> int:
    from docassay.mcp_server import run as run_mcp

    # The MCP package is imported lazily inside ``run_mcp`` (see ``mcp_server``),
    # so the missing-extra error surfaces here, not at the import above.
    try:
        return run_mcp(args.repo, refresh=args.refresh)
    except ImportError:
        print("the agent extra is not installed; run: uv sync --extra agent", file=sys.stderr)
        return 3


_COMMANDS: dict[str, Callable[[argparse.Namespace], int]] = {
    "analyze": _cmd_analyze,
    "dump": _cmd_dump,
    "export": _cmd_export,
    "export-md": _cmd_export_md,
    "corpus-md": _cmd_corpus_md,
    "web": _cmd_web,
    "report": _cmd_report,
    "review": _cmd_review,
    "consolidate": _cmd_consolidate,
    "mcp": _cmd_mcp,
}


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    handler = _COMMANDS.get(args.command)
    return handler(args) if handler is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
