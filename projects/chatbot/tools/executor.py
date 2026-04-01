"""
Tool executor — dispatches tool calls to the appropriate skill handler.
Handlers are registered in _TOOL_HANDLERS dict and can be extended at runtime
(e.g., by MCP bridge registering dynamic tools).
"""

import json
import logging

logger = logging.getLogger(__name__)


def execute_tool(tool_name: str, args: dict) -> str:
    """
    Execute a registered tool and return a JSON string result.
    Never raises — errors are returned as {"error": "..."} JSON.
    """
    try:
        handler = _TOOL_HANDLERS.get(tool_name)
        if handler is None:
            return json.dumps({"error": f"Unknown tool: {tool_name!r}"})
        return handler(**args)
    except Exception as exc:
        logger.error(f"Tool '{tool_name}' raised an exception: {exc}", exc_info=True)
        return json.dumps({"error": str(exc)})


# ── Individual handlers (lazy imports for optional deps) ──────────────────

def _h_get_datetime(**_) -> str:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return json.dumps({
        "utc": now.isoformat(),
        "readable": now.strftime("%A, %B %d %Y %H:%M UTC"),
    })


def _h_calculate(expression: str = "", **_) -> str:
    from skills.calculator import safe_calculate
    return json.dumps(safe_calculate(expression))


def _h_memory_set(key: str = "", value: str = "", **_) -> str:
    from skills.memory_store import memory_set
    return json.dumps(memory_set(key, str(value)))


def _h_memory_get(key: str = "", **_) -> str:
    from skills.memory_store import memory_get
    return json.dumps(memory_get(key))


def _h_memory_list(**_) -> str:
    from skills.memory_store import memory_list
    return json.dumps(memory_list())


def _h_memory_delete(key: str = "", **_) -> str:
    from skills.memory_store import memory_delete
    return json.dumps(memory_delete(key))


def _h_web_search(query: str = "", max_results: int = 5, **_) -> str:
    from skills.web_search import search
    return json.dumps(search(query, min(max(1, int(max_results)), 10)))


def _h_fetch_url(url: str = "", max_chars: int = 8000, **_) -> str:
    from skills.web_search import fetch_url
    return json.dumps(fetch_url(url, int(max_chars)))


def _h_run_python(code: str = "", input_data: str = "", **_) -> str:
    from skills.code_runner import run_python
    return json.dumps(run_python(code, input_data=str(input_data)))


def _h_read_workspace_file(path: str = "", **_) -> str:
    from skills.file_ops import read_file
    return json.dumps(read_file(path))


def _h_write_workspace_file(path: str = "", content: str = "", **_) -> str:
    from skills.file_ops import write_file
    return json.dumps(write_file(path, content))


def _h_list_workspace_files(folder: str = "", **_) -> str:
    from skills.file_ops import list_files
    return json.dumps(list_files(folder))


def _h_spawn_subagent(agent_type: str = "", task: str = "", context: str = "", **_) -> str:
    from agents.coordinator import run_subagent
    return run_subagent(agent_type, task, context)


# ── Dispatch table ─────────────────────────────────────────────────────────
# This dict is intentionally module-level so MCP bridge can inject entries.

_TOOL_HANDLERS: dict = {
    "get_datetime":          _h_get_datetime,
    "calculate":             _h_calculate,
    "memory_set":            _h_memory_set,
    "memory_get":            _h_memory_get,
    "memory_list":           _h_memory_list,
    "memory_delete":         _h_memory_delete,
    "web_search":            _h_web_search,
    "fetch_url":             _h_fetch_url,
    "run_python":            _h_run_python,
    "read_workspace_file":   _h_read_workspace_file,
    "write_workspace_file":  _h_write_workspace_file,
    "list_workspace_files":  _h_list_workspace_files,
    "spawn_subagent":        _h_spawn_subagent,
}
