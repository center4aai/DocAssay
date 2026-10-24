"""Tests for the MCP server surface (docassay.mcp_server).

The tool bodies live on ``Oracle`` (transport-independent), so they are tested
directly here; the MCP wiring itself is exercised end-to-end over stdio when the
optional ``agent`` extra is installed.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

from docassay.api import Oracle


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def _mini_repo(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "1.2.3"\ndependencies = ["requests>=2.0"]\n'
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("class Klass:\n    pass\n")
    (tmp_path / "README.md").write_text(_english_readme("It ships `src/mod.py`.\n"))
    return tmp_path


def test_tool_bodies_are_transport_independent(tmp_path: Path) -> None:
    oracle = Oracle(_mini_repo(tmp_path))

    assert oracle.verify_claim("The project depends on requests.")["status"] == "SUPPORTED"
    assert oracle.lookup("SYMBOL_EXISTS", "Klass")
    assert "licenses" in oracle.project_metadata()
    assert "versions" not in oracle.project_metadata()
    assert oracle.list_facts(predicate="PATH_EXISTS")


def test_build_server_registers_tools(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from docassay.mcp_server import build_server

    server = build_server(_mini_repo(tmp_path))
    assert server is not None


async def _round_trip(repo: Path) -> dict:
    """Drive a real stdio client against ``docassay mcp`` and collect answers."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "docassay.core.cli", "mcp", "--repo", str(repo)],
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        init = await session.initialize()
        tools = await session.list_tools()
        call = await session.call_tool(
            "verify_claim", {"claim": "The project depends on requests."}
        )
        resources = await session.list_resources()
        summary = await session.read_resource("repo://summary")
        return {
            "server": init.server_info,
            "tools": sorted(t.name for t in tools.tools),
            "verdict": json.loads(call.content[0].text),
            "resources": sorted(str(r.uri) for r in resources.resources),
            "summary": summary.contents[0].text,
        }


def test_stdio_protocol_round_trip(tmp_path: Path) -> None:
    """The shipped surface works over the wire: handshake, tools, resource."""
    pytest.importorskip("mcp")
    repo = _mini_repo(tmp_path)

    result = asyncio.run(asyncio.wait_for(_round_trip(repo), timeout=120))

    assert result["server"].name == "docassay"
    assert result["server"].version
    assert result["tools"] == ["list_facts", "lookup", "project_metadata", "verify_claim"]
    assert result["verdict"]["status"] == "SUPPORTED"
    assert result["resources"] == ["repo://summary"]
    # The resource must stay context-sized: the full inventory is paged through
    # ``list_facts``, not dumped here.
    assert len(result["summary"]) < 200_000
    assert "fact_counts" in json.loads(result["summary"])
