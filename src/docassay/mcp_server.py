"""MCP server: DocAssay as a source of truth for coding agents.

Run over stdio::

    docassay mcp --repo /path/to/repo

The server answers four tools over the deterministic, LLM-free inventory of the
repository:

- ``list_facts(predicate?, limit?)`` -- the ground-truth facts with provenance;
- ``verify_claim(claim)`` -- ``SUPPORTED`` / ``REFUTED`` / ``NEI`` for one claim;
- ``lookup(predicate, name)`` -- one referent at a time;
- ``project_metadata()`` -- license, dependencies, Docker/CI presence.

and one read-only resource, ``repo://summary``, with the project-level metadata
(licence, dependency list, fact counts, infra flags). The *full* inventory is
deliberately not a resource: it reaches tens of megabytes on large repositories,
so an agent pages through it with ``list_facts(predicate=…, limit=…)`` instead.

Requires the optional ``agent`` extra (``uv sync --extra agent``). The MCP
package is imported lazily, so importing this module -- and the CLI entry point
that wraps it -- still works when the extra is absent; the tool bodies are
transport-independent ``Oracle`` methods (``docassay.api``), so they are
exercised by the test-suite without the MCP package installed.
"""

from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _dist_version
from pathlib import Path

from docassay.api import Oracle

#: Told to the client during ``initialize``; OpenCode appends it to the agent's
#: system prompt, so keep it short and actionable.
_INSTRUCTIONS = (
    "DocAssay exposes a deterministic, LLM-free fact inventory of one repository. "
    "Ask list_facts or lookup for ground truth with source provenance, and "
    "verify_claim to adjudicate one documentation sentence as SUPPORTED, REFUTED "
    "or NEI before repeating it. Never guess a dependency, path or symbol: query it."
)


def _package_version() -> str:
    """The installed DocAssay version, or ``0.0.0`` in an uninstalled checkout."""
    try:
        return _dist_version("docassay")
    except PackageNotFoundError:  # pragma: no cover - editable/source checkouts
        return "0.0.0"


def _server_class():
    """The MCP server class, imported lazily so the ``agent`` extra stays optional."""
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise ImportError(
            "the MCP server needs the optional 'agent' extra; run: uv sync --extra agent"
        ) from exc
    return MCPServer


def build_server(repo_root: str | Path, *, refresh: bool = False):
    """Build an MCP server bound to one repository."""
    oracle = Oracle(repo_root, refresh=refresh)
    server = _server_class()(
        "docassay",
        version=_package_version(),
        instructions=_INSTRUCTIONS,
    )

    @server.tool()
    def list_facts(predicate: str | None = None, limit: int = 500) -> list[dict]:
        """Deterministic facts of the repository, with source provenance.

        Args:
            predicate: optional predicate filter (DEPENDENCY, PATH_EXISTS,
                SYMBOL_EXISTS, LICENSE, HAS_DOCKERFILE,
                HAS_CI_WORKFLOW); omit for every fact.
            limit: maximum number of facts to return.
        """
        return oracle.list_facts(predicate=predicate, limit=limit)

    @server.tool()
    def verify_claim(claim: str) -> dict:
        """Verify one free-form claim about the repository.

        Returns an aggregate status (``SUPPORTED`` / ``REFUTED`` / ``NEI`` /
        ``NO_CLAIM``) and, per referent, the verdict, the abstention layer and
        reason, and the supporting/refuting evidence lines.
        """
        return oracle.verify_claim(claim)

    @server.tool()
    def lookup(predicate: str, name: str) -> list[dict]:
        """Look up a single referent (dependency, path, symbol, ...) by name."""
        return oracle.lookup(predicate, name)

    @server.tool()
    def project_metadata() -> dict:
        """Project-level ground truth: license, dependencies, infra."""
        return oracle.project_metadata()

    @server.resource("repo://summary")
    def summary_resource() -> str:
        """Project-level metadata as JSON (counts, licences, deps, infra)."""
        return json.dumps(oracle.project_metadata(), ensure_ascii=False)

    return server


def run(repo_root: str | Path, *, refresh: bool = False) -> int:
    """Run the MCP server over stdio (blocking)."""
    build_server(repo_root, refresh=refresh).run()
    return 0
