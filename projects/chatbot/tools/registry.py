"""
Tool registry — all tool definitions in OpenAI function-calling format.
Each agent type gets a curated subset of tools.
"""

# ── Core tools (always available) ─────────────────────────────────────────

TOOL_GET_DATETIME = {
    "type": "function",
    "function": {
        "name": "get_datetime",
        "description": "Returns the current date and time in UTC (ISO 8601 format).",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

TOOL_CALCULATE = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "Evaluates a mathematical expression safely and returns the numeric result. "
            "Supports: +, -, *, /, **, %, //, abs, round, min, max, sqrt, log, sin, cos, "
            "tan, ceil, floor, exp, pi, e. Use for any arithmetic or algebraic computation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A valid math expression, e.g. '2**10', 'sqrt(144)', '(3+4)*2.5'",
                }
            },
            "required": ["expression"],
        },
    },
}

TOOL_MEMORY_SET = {
    "type": "function",
    "function": {
        "name": "memory_set",
        "description": (
            "Stores a value in persistent memory under a given key. "
            "Use this to remember facts, user preferences, or intermediate data across conversations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Memory key (1-64 alphanumeric chars, underscores, or hyphens)",
                },
                "value": {
                    "type": "string",
                    "description": "Value to store",
                },
            },
            "required": ["key", "value"],
        },
    },
}

TOOL_MEMORY_GET = {
    "type": "function",
    "function": {
        "name": "memory_get",
        "description": "Retrieves a previously stored value from persistent memory by key.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Memory key to retrieve"},
            },
            "required": ["key"],
        },
    },
}

TOOL_MEMORY_LIST = {
    "type": "function",
    "function": {
        "name": "memory_list",
        "description": "Lists all keys currently stored in persistent memory.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

TOOL_MEMORY_DELETE = {
    "type": "function",
    "function": {
        "name": "memory_delete",
        "description": "Deletes a key from persistent memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Memory key to delete"},
            },
            "required": ["key"],
        },
    },
}

# ── Research tools ─────────────────────────────────────────────────────────

TOOL_WEB_SEARCH = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Searches the web using DuckDuckGo and returns titles, URLs, and snippets. "
            "Use for current events, factual lookups, documentation, or anything requiring "
            "up-to-date information beyond your training data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (1–10, default 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}

TOOL_FETCH_URL = {
    "type": "function",
    "function": {
        "name": "fetch_url",
        "description": (
            "Fetches the text content of a public web URL. "
            "Use to read articles, documentation, or any public web page after a web_search."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL starting with https:// or http://",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Max characters to return (default 8000)",
                    "default": 8000,
                },
            },
            "required": ["url"],
        },
    },
}

# ── Code / workspace tools ─────────────────────────────────────────────────

TOOL_RUN_PYTHON = {
    "type": "function",
    "function": {
        "name": "run_python",
        "description": (
            "Executes Python code in a sandboxed subprocess with a 15-second timeout. "
            "Returns stdout, stderr, and exit code. Use to test logic, run calculations, "
            "process data, generate output, or verify code before presenting it."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"},
                "input_data": {
                    "type": "string",
                    "description": "Optional stdin input for the script",
                    "default": "",
                },
            },
            "required": ["code"],
        },
    },
}

TOOL_READ_FILE = {
    "type": "function",
    "function": {
        "name": "read_workspace_file",
        "description": "Reads a file from the workspace directory. Path must be relative.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path"},
            },
            "required": ["path"],
        },
    },
}

TOOL_WRITE_FILE = {
    "type": "function",
    "function": {
        "name": "write_workspace_file",
        "description": (
            "Writes content to a file in the workspace directory. "
            "Creates the file (and parent directories) if they do not exist. "
            "Overwrites existing files."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
    },
}

TOOL_LIST_FILES = {
    "type": "function",
    "function": {
        "name": "list_workspace_files",
        "description": "Lists files and folders in the workspace directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "Relative folder path to list (leave empty for root)",
                    "default": "",
                },
            },
            "required": [],
        },
    },
}

# ── Subagent spawning ──────────────────────────────────────────────────────

TOOL_SPAWN_SUBAGENT = {
    "type": "function",
    "function": {
        "name": "spawn_subagent",
        "description": (
            "Delegates a complex subtask to a specialized subagent. "
            "Use 'research' for information gathering and web search, "
            "'coder' for code writing and execution tasks, "
            "'analyst' for data analysis and computations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "agent_type": {
                    "type": "string",
                    "enum": ["research", "coder", "analyst"],
                    "description": "Type of subagent to spawn",
                },
                "task": {
                    "type": "string",
                    "description": "Detailed task description for the subagent",
                },
                "context": {
                    "type": "string",
                    "description": "Additional context, data, or intermediate results",
                    "default": "",
                },
            },
            "required": ["agent_type", "task"],
        },
    },
}

# ── Tool sets per agent type ───────────────────────────────────────────────

CORE_TOOLS = [
    TOOL_GET_DATETIME,
    TOOL_CALCULATE,
    TOOL_MEMORY_SET,
    TOOL_MEMORY_GET,
    TOOL_MEMORY_LIST,
    TOOL_MEMORY_DELETE,
]

RESEARCH_TOOLS = CORE_TOOLS + [TOOL_WEB_SEARCH, TOOL_FETCH_URL]

CODER_TOOLS = CORE_TOOLS + [
    TOOL_WEB_SEARCH,
    TOOL_FETCH_URL,
    TOOL_RUN_PYTHON,
    TOOL_READ_FILE,
    TOOL_WRITE_FILE,
    TOOL_LIST_FILES,
]

ANALYST_TOOLS = CORE_TOOLS + [
    TOOL_WEB_SEARCH,
    TOOL_FETCH_URL,
    TOOL_RUN_PYTHON,
    TOOL_READ_FILE,
]

COORDINATOR_TOOLS = CORE_TOOLS + [
    TOOL_WEB_SEARCH,
    TOOL_FETCH_URL,
    TOOL_RUN_PYTHON,
    TOOL_READ_FILE,
    TOOL_WRITE_FILE,
    TOOL_LIST_FILES,
    TOOL_SPAWN_SUBAGENT,
]

_AGENT_TOOL_MAP = {
    "none":        [],
    "assistant":   CORE_TOOLS,
    "research":    RESEARCH_TOOLS,
    "coder":       CODER_TOOLS,
    "analyst":     ANALYST_TOOLS,
    "coordinator": COORDINATOR_TOOLS,
}


def get_tools_for_agent(agent_type: str) -> list:
    """Return the OpenAI tool list for a given agent type."""
    return _AGENT_TOOL_MAP.get(agent_type.lower(), COORDINATOR_TOOLS)
