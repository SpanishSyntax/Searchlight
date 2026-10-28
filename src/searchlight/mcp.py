"""Searchlight Model Context Protocol (MCP) Server.

Provides atomic PDF discovery, full-text regex querying, metadata inspection,
plain text extraction, and page-targeted viewer launching over standard I/O (stdio).
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from searchlight import __version__
from searchlight.engine import search_pdfs
from searchlight.pdf_utils import extract_pdf_text, get_pdf_info
from searchlight.viewer import detect_viewer, open_pdf

logger = logging.getLogger("searchlight.mcp")

# Tool definitions complying with MCP specification (2024-11-05 / 2025-03-26)
TOOL_DEFINITIONS = [
    {
        "name": "searchlight_search",
        "description": (
            "Full-text regex and pattern querying across single PDF files or deep directory trees. "
            "Returns structured matches with file paths, page numbers, matching lines, and optional context."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text or regular expression pattern to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "Target PDF file or directory containing PDFs to scan (default '.').",
                    "default": ".",
                },
                "ignore_case": {
                    "type": "boolean",
                    "description": "Case-insensitive pattern matching (default True).",
                    "default": True,
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Recursively scan subdirectories for PDF files (default True).",
                    "default": True,
                },
                "max_count": {
                    "type": "integer",
                    "description": "Maximum number of matches to return per document (default 50).",
                    "default": 50,
                },
                "context": {
                    "type": "integer",
                    "description": "Number of context lines before and after match (default 0).",
                    "default": 0,
                },
                "page": {
                    "type": ["integer", "null"],
                    "description": "Optional page number filter (1-based index).",
                    "default": None,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "searchlight_info",
        "description": (
            "Extracts structured PDF document metadata including title, author, total page count, "
            "PDF version, paper size, encryption status, and creation timestamps."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Path to the target PDF file.",
                },
            },
            "required": ["file"],
        },
    },
    {
        "name": "searchlight_extract_text",
        "description": (
            "Extracts readable plain text from an entire PDF file or a specific page range using pdftotext."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Path to the target PDF file.",
                },
                "first_page": {
                    "type": ["integer", "null"],
                    "description": "First page to extract (1-based index, optional).",
                    "default": None,
                },
                "last_page": {
                    "type": ["integer", "null"],
                    "description": "Last page to extract (1-based index, optional).",
                    "default": None,
                },
                "layout": {
                    "type": "boolean",
                    "description": "Maintain original physical column/page layout (default False).",
                    "default": False,
                },
            },
            "required": ["file"],
        },
    },
    {
        "name": "searchlight_open_viewer",
        "description": (
            "Launches an external document viewer (e.g. zathura, sioyek, okular, evince, xdg-open) "
            "directly positioned at a specific page number."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Path to the target PDF file.",
                },
                "page": {
                    "type": ["integer", "null"],
                    "description": "Page number to open viewer at (1-based index).",
                    "default": None,
                },
                "viewer": {
                    "type": ["string", "null"],
                    "description": "Explicit viewer command (default auto-detects zathura/sioyek/etc.).",
                    "default": None,
                },
            },
            "required": ["file"],
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Routes and executes a registered Searchlight tool."""
    if name == "searchlight_search":
        query = str(arguments.get("query", "")).strip()
        if not query:
            return {"status": "error", "error": "`query` cannot be empty."}
        path = str(arguments.get("path", "."))
        ignore_case = bool(arguments.get("ignore_case", True))
        recursive = bool(arguments.get("recursive", True))
        max_count = int(arguments.get("max_count", 50))
        context = int(arguments.get("context", 0))
        page = arguments.get("page")
        if page is not None:
            page = int(page)

        try:
            result = search_pdfs(
                query=query,
                target=path,
                ignore_case=ignore_case,
                recursive=recursive,
                max_count=max_count,
                context=context,
                page=page,
            )
            return {"status": "ok", **result.to_dict()}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    elif name == "searchlight_info":
        file_path = str(arguments.get("file", "")).strip()
        if not file_path:
            return {"status": "error", "error": "`file` argument is required."}
        try:
            info = get_pdf_info(file_path)
            return {"status": "ok", **info}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    elif name == "searchlight_extract_text":
        file_path = str(arguments.get("file", "")).strip()
        if not file_path:
            return {"status": "error", "error": "`file` argument is required."}
        first_page = arguments.get("first_page")
        last_page = arguments.get("last_page")
        layout = bool(arguments.get("layout", False))
        if first_page is not None:
            first_page = int(first_page)
        if last_page is not None:
            last_page = int(last_page)

        try:
            res = extract_pdf_text(
                pdf_path=file_path,
                first_page=first_page,
                last_page=last_page,
                layout=layout,
            )
            return res
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    elif name == "searchlight_open_viewer":
        file_path = str(arguments.get("file", "")).strip()
        if not file_path:
            return {"status": "error", "error": "`file` argument is required."}
        page = arguments.get("page")
        if page is not None:
            page = int(page)
        viewer_cmd = arguments.get("viewer")
        detected = detect_viewer(viewer_cmd)

        try:
            opened = open_pdf(file_path, page=page, viewer=viewer_cmd)
            return {
                "status": "ok" if opened else "error",
                "viewer": detected,
                "file": file_path,
                "page": page,
                "opened": opened,
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    else:
        return {"status": "error", "error": f"Unknown tool: '{name}'"}


class StdioMCPServer:
    """Lightweight, zero-dependency JSON-RPC 2.0 MCP server over standard I/O."""

    def __init__(self) -> None:
        self.server_info = {
            "name": "searchlight",
            "version": __version__,
        }
        self.capabilities = {
            "tools": {
                "listChanged": False,
            }
        }

    def handle_request(self, msg: dict[str, Any]) -> dict[str, Any] | None:
        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        # Handle notifications (no response expected)
        if msg_id is None:
            if method == "notifications/initialized":
                logger.info("MCP client initialized.")
            return None

        # Standard JSON-RPC Methods
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": self.capabilities,
                    "serverInfo": self.server_info,
                    "instructions": (
                        "Searchlight MCP Server: High-performance PDF full-text regex querying, "
                        "metadata discovery, text extraction, and page viewer jumping."
                    ),
                },
            }

        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {},
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOL_DEFINITIONS,
                },
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            tool_result = execute_tool(tool_name, arguments)
            is_error = tool_result.get("status") == "error"

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(tool_result, indent=2),
                        }
                    ],
                    "isError": is_error,
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }

    def run(self) -> int:
        """Runs the main stdio loop reading JSON-RPC requests."""
        # Set stderr for logs, stdout exclusively for clean JSON-RPC
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        logger.info("Searchlight MCP server v%s running on stdio.", __version__)

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as err:
                    err_resp = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {err}",
                        },
                    }
                    sys.stdout.write(json.dumps(err_resp) + "\n")
                    sys.stdout.flush()
                    continue

                resp = self.handle_request(payload)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()

            except (KeyboardInterrupt, BrokenPipeError):
                break
            except Exception as exc:
                logger.exception("Unexpected error in MCP stdio loop: %s", exc)

        logger.info("Searchlight MCP server exiting.")
        return 0


def main() -> int:
    """CLI entry point for running the Searchlight MCP server."""
    server = StdioMCPServer()
    return server.run()


if __name__ == "__main__":
    sys.exit(main())
