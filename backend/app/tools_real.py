"""Real tool implementations for the Devin AI Assistant.

These tools actually execute operations on the Windows filesystem
instead of returning simulated demo responses.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

from app.models import ToolInfo, ToolResult, ToolStatus


# ---------------------------------------------------------------------------
# Sandbox — restrict operations to a workspace directory
# ---------------------------------------------------------------------------

_DEFAULT_WORKSPACE = Path.home() / "devin-workspace"


def _resolve_path(path: str, workspace: Path | None = None) -> Path:
    """Resolve a path safely within the workspace."""
    ws = workspace or _DEFAULT_WORKSPACE
    ws.mkdir(parents=True, exist_ok=True)
    resolved = (ws / path).resolve()
    # Security: ensure path is within workspace
    if not str(resolved).startswith(str(ws.resolve())):
        raise PermissionError(f"Access denied: path is outside workspace ({ws})")
    return resolved


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_read_file(params: dict[str, Any]) -> ToolResult:
    """Read the contents of a file."""
    path_str = params.get("path", "")
    if not path_str:
        return ToolResult(status=ToolStatus.ERROR, error="Missing 'path' parameter", tool_name="read_file")
    try:
        fpath = _resolve_path(path_str)
        if not fpath.exists():
            return ToolResult(status=ToolStatus.ERROR, error=f"File not found: {path_str}", tool_name="read_file")
        if not fpath.is_file():
            return ToolResult(status=ToolStatus.ERROR, error=f"Not a file: {path_str}", tool_name="read_file")
        content = fpath.read_text(encoding="utf-8", errors="replace")
        # Limit output size
        if len(content) > 10000:
            content = content[:10000] + f"\n\n... (truncated, total {len(content)} chars)"
        return ToolResult(status=ToolStatus.SUCCESS, output=content, tool_name="read_file")
    except PermissionError as e:
        return ToolResult(status=ToolStatus.ERROR, error=str(e), tool_name="read_file")
    except Exception as e:
        return ToolResult(status=ToolStatus.ERROR, error=f"Error reading file: {e}", tool_name="read_file")


def tool_write_file(params: dict[str, Any]) -> ToolResult:
    """Write content to a file, creating directories as needed."""
    path_str = params.get("path", "")
    content = params.get("content", "")
    if not path_str:
        return ToolResult(status=ToolStatus.ERROR, error="Missing 'path' parameter", tool_name="write_file")
    try:
        fpath = _resolve_path(path_str)
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Successfully wrote {len(content)} chars to {path_str}",
            tool_name="write_file",
        )
    except PermissionError as e:
        return ToolResult(status=ToolStatus.ERROR, error=str(e), tool_name="write_file")
    except Exception as e:
        return ToolResult(status=ToolStatus.ERROR, error=f"Error writing file: {e}", tool_name="write_file")


def tool_run_shell(params: dict[str, Any]) -> ToolResult:
    """Execute a shell command (PowerShell on Windows)."""
    command = params.get("command", "")
    if not command:
        return ToolResult(status=ToolStatus.ERROR, error="Missing 'command' parameter", tool_name="run_shell")

    # Block dangerous commands
    dangerous = ["format", "del /s", "rmdir /s", "rm -rf", "shutdown", "taskkill"]
    cmd_lower = command.lower()
    for d in dangerous:
        if d in cmd_lower:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=f"Blocked dangerous command containing '{d}'",
                tool_name="run_shell",
            )

    try:
        workspace = _DEFAULT_WORKSPACE
        workspace.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(workspace),
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        if len(output) > 5000:
            output = output[:5000] + "\n... (truncated)"
        return ToolResult(
            status=ToolStatus.SUCCESS if result.returncode == 0 else ToolStatus.ERROR,
            output=output or "(no output)",
            error=result.stderr[:500] if result.returncode != 0 else "",
            tool_name="run_shell",
        )
    except subprocess.TimeoutExpired:
        return ToolResult(status=ToolStatus.TIMEOUT, error="Command timed out (30s)", tool_name="run_shell")
    except Exception as e:
        return ToolResult(status=ToolStatus.ERROR, error=f"Shell error: {e}", tool_name="run_shell")


def tool_search_code(params: dict[str, Any]) -> ToolResult:
    """Search for patterns in code files using regex."""
    pattern = params.get("pattern", "")
    search_path = params.get("path", ".")
    if not pattern:
        return ToolResult(status=ToolStatus.ERROR, error="Missing 'pattern' parameter", tool_name="search_code")
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        base = _resolve_path(search_path)
        if not base.exists():
            return ToolResult(status=ToolStatus.ERROR, error=f"Path not found: {search_path}", tool_name="search_code")

        matches: list[str] = []
        code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".md", ".txt", ".cfg", ".toml", ".yaml", ".yml"}

        if base.is_file():
            files = [base]
        else:
            files = [f for f in base.rglob("*") if f.is_file() and f.suffix in code_extensions]

        for fpath in files[:100]:  # Limit to 100 files
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
                for i, line in enumerate(content.splitlines(), 1):
                    if regex.search(line):
                        rel = fpath.relative_to(base) if base.is_dir() else fpath.name
                        matches.append(f"  {rel}:{i}  {line.strip()[:120]}")
                        if len(matches) >= 50:
                            break
            except Exception:
                continue
            if len(matches) >= 50:
                break

        if matches:
            output = f"Found {len(matches)} matches for '{pattern}':\n" + "\n".join(matches)
        else:
            output = f"No matches found for '{pattern}'"
        return ToolResult(status=ToolStatus.SUCCESS, output=output, tool_name="search_code")
    except re.error as e:
        return ToolResult(status=ToolStatus.ERROR, error=f"Invalid regex: {e}", tool_name="search_code")
    except Exception as e:
        return ToolResult(status=ToolStatus.ERROR, error=f"Search error: {e}", tool_name="search_code")


def tool_list_files(params: dict[str, Any]) -> ToolResult:
    """List files in a directory with optional glob filtering."""
    path_str = params.get("path", ".")
    glob_pattern = params.get("pattern", "*")
    try:
        base = _resolve_path(path_str)
        if not base.exists():
            return ToolResult(status=ToolStatus.ERROR, error=f"Path not found: {path_str}", tool_name="list_files")
        if not base.is_dir():
            return ToolResult(status=ToolStatus.ERROR, error=f"Not a directory: {path_str}", tool_name="list_files")

        entries: list[str] = []
        for item in sorted(base.glob(glob_pattern))[:200]:
            rel = item.relative_to(base)
            if item.is_dir():
                entries.append(f"  📁 {rel}/")
            else:
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size // 1024}KB"
                else:
                    size_str = f"{size // (1024 * 1024)}MB"
                entries.append(f"  📄 {rel} ({size_str})")

        if entries:
            output = f"Contents of {path_str}:\n" + "\n".join(entries)
        else:
            output = f"Directory {path_str} is empty (or no matches for '{glob_pattern}')"
        return ToolResult(status=ToolStatus.SUCCESS, output=output, tool_name="list_files")
    except Exception as e:
        return ToolResult(status=ToolStatus.ERROR, error=f"List error: {e}", tool_name="list_files")


def tool_web_search(params: dict[str, Any]) -> ToolResult:
    """Search Wikipedia for documentation or technical topics."""
    query = params.get("query", "")
    if not query:
        return ToolResult(status=ToolStatus.ERROR, error="Missing 'query' parameter", tool_name="web_search")
    try:
        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(user_agent="DevinAI/1.0", language="en")
        page = wiki.page(query)
        if page.exists():
            summary = page.summary[:1500]
            output = f"Wikipedia: {page.title}\n\n{summary}\n\nSource: {page.fullurl}"
            return ToolResult(status=ToolStatus.SUCCESS, output=output, tool_name="web_search")
        else:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"No Wikipedia article found for '{query}'",
                tool_name="web_search",
            )
    except ImportError:
        return ToolResult(
            status=ToolStatus.ERROR,
            error="wikipedia-api not installed. Run: pip install wikipedia-api",
            tool_name="web_search",
        )
    except Exception as e:
        return ToolResult(status=ToolStatus.ERROR, error=f"Web search error: {e}", tool_name="web_search")


# ---------------------------------------------------------------------------
# Tool Registry — maps tool names to their implementations
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "read_file": {
        "info": ToolInfo(
            name="read_file",
            description="Read the contents of a file in the workspace",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        ),
        "handler": tool_read_file,
    },
    "write_file": {
        "info": ToolInfo(
            name="write_file",
            description="Write content to a file, creating directories as needed",
            parameters={
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        ),
        "handler": tool_write_file,
    },
    "run_shell": {
        "info": ToolInfo(
            name="run_shell",
            description="Execute a PowerShell command in the workspace",
            parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
        ),
        "handler": tool_run_shell,
    },
    "search_code": {
        "info": ToolInfo(
            name="search_code",
            description="Search for patterns in code files using regex",
            parameters={
                "type": "object",
                "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}},
                "required": ["pattern"],
            },
        ),
        "handler": tool_search_code,
    },
    "list_files": {
        "info": ToolInfo(
            name="list_files",
            description="List files in a directory with optional glob filtering",
            parameters={
                "type": "object",
                "properties": {"path": {"type": "string"}, "pattern": {"type": "string"}},
            },
        ),
        "handler": tool_list_files,
    },
    "web_search": {
        "info": ToolInfo(
            name="web_search",
            description="Search Wikipedia for documentation, APIs, or technical topics",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        ),
        "handler": tool_web_search,
    },
}


def get_all_tools() -> list[ToolInfo]:
    return [entry["info"] for entry in TOOL_REGISTRY.values()]


def execute_tool(name: str, parameters: dict[str, Any]) -> ToolResult:
    entry = TOOL_REGISTRY.get(name)
    if not entry:
        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {name}", tool_name=name)
    handler = entry["handler"]
    return handler(parameters)
