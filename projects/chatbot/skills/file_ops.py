"""
Sandboxed file operations confined to the workspace directory.
All paths are validated to prevent path-traversal attacks.
"""

import os
import pathlib

_WORKSPACE = pathlib.Path(os.getcwd()).resolve()
_MAX_READ_BYTES = 100_000  # 100 KB read cap


def _safe_path(rel: str) -> pathlib.Path | None:
    """Resolve and verify the path stays inside the workspace root."""
    if not rel:
        return _WORKSPACE
    try:
        candidate = (_WORKSPACE / rel).resolve()
        # Ensure it's under the workspace (prevents traversal)
        candidate.relative_to(_WORKSPACE)
        return candidate
    except (ValueError, Exception):
        return None


def read_file(path: str) -> dict:
    p = _safe_path(path)
    if p is None:
        return {"error": "Path is outside the workspace directory"}
    if not p.exists():
        return {"error": f"File not found: {path}"}
    if not p.is_file():
        return {"error": f"Not a regular file: {path}"}
    try:
        raw = p.read_bytes()
        truncated = len(raw) > _MAX_READ_BYTES
        text = raw[:_MAX_READ_BYTES].decode("utf-8", errors="replace")
        return {"path": path, "content": text, "bytes": len(raw), "truncated": truncated}
    except Exception as exc:
        return {"error": str(exc)}


def write_file(path: str, content: str) -> dict:
    p = _safe_path(path)
    if p is None:
        return {"error": "Path is outside the workspace directory"}
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"status": "written", "path": path, "bytes": len(content.encode("utf-8"))}
    except Exception as exc:
        return {"error": str(exc)}


def list_files(folder: str = "") -> dict:
    p = _safe_path(folder) if folder else _WORKSPACE
    if p is None:
        return {"error": "Path is outside the workspace directory"}
    if not p.exists():
        return {"error": f"Directory not found: {folder!r}"}
    if not p.is_dir():
        return {"error": f"Not a directory: {folder!r}"}
    try:
        entries = []
        for item in sorted(p.iterdir()):
            rel = str(item.relative_to(_WORKSPACE))
            entries.append({
                "name": item.name,
                "path": rel,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
            })
        return {"folder": folder or ".", "entries": entries, "count": len(entries)}
    except Exception as exc:
        return {"error": str(exc)}
