"""Unit tests for Searchlight MCP server and PDF utilities."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from searchlight.mcp import StdioMCPServer, TOOL_DEFINITIONS, execute_tool
from searchlight.pdf_utils import extract_pdf_text, get_pdf_info


def test_tool_definitions_valid():
    names = [t["name"] for t in TOOL_DEFINITIONS]
    assert "searchlight_search" in names
    assert "searchlight_info" in names
    assert "searchlight_extract_text" in names
    assert "searchlight_open_viewer" in names


def test_mcp_initialize():
    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    }
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 1
    assert "serverInfo" in resp["result"]
    assert resp["result"]["serverInfo"]["name"] == "searchlight"


def test_mcp_tools_list():
    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    assert len(tools) == 4
    tool_map = {t["name"]: t for t in tools}
    assert "searchlight_search" in tool_map


def test_mcp_ping():
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 3, "method": "ping"}
    resp = server.handle_request(req)
    assert resp == {"jsonrpc": "2.0", "id": 3, "result": {}}


def test_mcp_notification():
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    resp = server.handle_request(req)
    assert resp is None


def test_execute_tool_search(tmp_path: Path):
    # Testing search execution against empty temp directory
    res = execute_tool("searchlight_search", {"query": "sample", "path": str(tmp_path)})
    assert res["status"] == "ok"
    assert res["total_matches"] == 0


def test_execute_tool_unknown():
    res = execute_tool("nonexistent_tool", {})
    assert res["status"] == "error"
    assert "Unknown tool" in res["error"]


def test_execute_tool_call_via_server():
    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "searchlight_search",
            "arguments": {"query": "", "path": "."},
        },
    }
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 4
    assert resp["result"]["isError"] is True
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "error"


@patch("searchlight.pdf_utils.shutil.which")
@patch("searchlight.pdf_utils.subprocess.run")
def test_pdf_info_mock(mock_run: MagicMock, mock_which: MagicMock, tmp_path: Path):
    dummy_pdf = tmp_path / "test.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy content")

    mock_which.return_value = "/fake/bin/pdfinfo"
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=(
            "Title:          Sample Paper\n"
            "Author:         Alice & Bob\n"
            "Pages:          14\n"
            "Page size:      595 x 842 pts (A4)\n"
            "PDF version:    1.7\n"
            "Encrypted:      no\n"
        ),
        stderr="",
    )

    info = get_pdf_info(dummy_pdf)
    assert info["title"] == "Sample Paper"
    assert info["author"] == "Alice & Bob"
    assert info["pages"] == 14
    assert info["pdf_version"] == "1.7"
    assert info["encrypted"] is False


@patch("searchlight.pdf_utils.shutil.which")
@patch("searchlight.pdf_utils.subprocess.run")
def test_pdf_extract_text_mock(mock_run: MagicMock, mock_which: MagicMock, tmp_path: Path):
    dummy_pdf = tmp_path / "test.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy content")

    mock_which.return_value = "/fake/bin/pdftotext"
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="First paragraph of extracted text.\nSecond line.",
        stderr="",
    )

    extracted = extract_pdf_text(dummy_pdf, first_page=1, last_page=2)
    assert extracted["status"] == "ok"
    assert "First paragraph" in extracted["text"]
    assert extracted["char_count"] > 0
