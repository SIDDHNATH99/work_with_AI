"""
Notes MCP Server
Persistent key-value notes stored in a local JSON file.
Useful for the AI to save and recall information across conversations.

Tools: notes_save, notes_get, notes_list, notes_delete, notes_search
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes")

NOTES_FILE = Path(__file__).parent / "notes_data.json"


def _load() -> dict:
    if not NOTES_FILE.exists():
        return {}
    try:
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(notes: dict) -> None:
    NOTES_FILE.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")


@mcp.tool()
def notes_save(key: str, content: str) -> str:
    """Save or update a note with a given key. Use to remember information for later."""
    notes = _load()
    is_update = key in notes
    notes[key] = {"content": content, "updatedAt": datetime.now(timezone.utc).isoformat()}
    _save(notes)
    return f"Note '{key}' {'updated' if is_update else 'saved'} successfully."


@mcp.tool()
def notes_get(key: str) -> str:
    """Retrieve a saved note by its key."""
    notes = _load()
    note = notes.get(key)
    if not note:
        return f"No note found for key '{key}'."
    return f"[{key}] (saved: {note['updatedAt']})\n\n{note['content']}"


@mcp.tool()
def notes_list() -> str:
    """List all saved note keys with their last-updated timestamps."""
    notes = _load()
    if not notes:
        return "No notes saved yet."
    lines = [f"• {k}  (updated: {v['updatedAt']})" for k, v in notes.items()]
    return "\n".join(lines)


@mcp.tool()
def notes_delete(key: str) -> str:
    """Delete a saved note by its key."""
    notes = _load()
    if key not in notes:
        return f"Note '{key}' not found."
    del notes[key]
    _save(notes)
    return f"Note '{key}' deleted."


@mcp.tool()
def notes_search(keyword: str) -> str:
    """Search note contents and keys for a keyword."""
    notes = _load()
    kw = keyword.lower()
    matches = [
        f"• {k}: {v['content'][:120]}{'…' if len(v['content']) > 120 else ''}"
        for k, v in notes.items()
        if kw in k.lower() or kw in v["content"].lower()
    ]
    if not matches:
        return f"No notes match '{keyword}'."
    return "\n".join(matches)


if __name__ == "__main__":
    mcp.run(transport="stdio")
