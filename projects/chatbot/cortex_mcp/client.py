"""
MCP (Model Context Protocol) client.

Connects to configured MCP servers, discovers their tools, and registers
them into the tool executor so agents can call them transparently.

Configuration (in .env):
    MCP_SERVERS_JSON = [
        {"name": "filesystem", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]},
        {"name": "my-server",  "command": "python", "args": ["my_mcp_server.py"]}
    ]

Each registered MCP tool gets a name prefixed with "mcp__<server>__<tool>"
so it never collides with built-in tools.
"""

import asyncio
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

# Runtime state
_mcp_tool_definitions: list[dict] = []   # OpenAI-format tool defs from MCP servers


def get_mcp_tool_definitions() -> list[dict]:
    """Return all dynamically registered MCP tool definitions."""
    return list(_mcp_tool_definitions)


def _load_server_configs() -> list[dict]:
    raw = os.getenv("MCP_SERVERS_JSON", "[]").strip()
    if not raw:
        return []
    try:
        configs = json.loads(raw)
        return configs if isinstance(configs, list) else []
    except json.JSONDecodeError:
        logger.warning("MCP_SERVERS_JSON is not valid JSON — skipping MCP servers")
        return []


def _build_stdio_params(cfg: dict):
    """Build StdioServerParameters from a config dict."""
    from mcp import StdioServerParameters
    # Use the same Python interpreter that is running the chatbot
    command = cfg["command"]
    if command in ("python", "python3"):
        command = sys.executable
    # Merge extra env vars on top of the current environment so the
    # subprocess inherits PATH, PYTHONPATH, etc.
    merged_env = os.environ.copy()
    if cfg.get("env"):
        merged_env.update(cfg["env"])
    return StdioServerParameters(
        command=command,
        args=cfg.get("args", []),
        env=merged_env,
    )


def _tool_to_openai(tool, server_name: str) -> dict:
    """Convert an MCP Tool object to OpenAI function-calling format."""
    schema = {}
    if hasattr(tool, "inputSchema") and tool.inputSchema:
        schema = tool.inputSchema
    if not schema:
        schema = {"type": "object", "properties": {}, "required": []}
    return {
        "type": "function",
        "function": {
            "name":        f"mcp__{server_name}__{tool.name}",
            "description": f"[MCP:{server_name}] {tool.description or tool.name}",
            "parameters":  schema,
        },
    }


async def _discover_tools(cfg: dict) -> list:
    """Connect to one MCP server and list its tools."""
    try:
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        params = _build_stdio_params(cfg)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                resp = await session.list_tools()
                return resp.tools
    except Exception as exc:
        logger.warning(f"MCP server '{cfg.get('name')}' tool discovery failed: {exc}")
        return []


async def _call_tool_async(cfg: dict, original_name: str, args: dict) -> str:
    """Invoke a single MCP tool and return a JSON string result."""
    try:
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        params = _build_stdio_params(cfg)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(original_name, args)
                texts = [item.text for item in result.content if hasattr(item, "text")]
                return json.dumps({"result": "\n".join(texts)})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _get_or_create_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


async def initialize_mcp_tools() -> None:
    """
    Discover tools from all configured MCP servers and register them
    into the tool executor.  Called once at application startup.
    Gracefully skips unavailable servers.
    """
    global _mcp_tool_definitions

    # Check mcp package availability first
    try:
        import mcp  # noqa: F401
    except ImportError:
        logger.info("mcp package not installed — MCP integration disabled. "
                    "Install with: pip install mcp")
        return

    configs = _load_server_configs()
    if not configs:
        logger.info("No MCP servers configured (MCP_SERVERS_JSON not set)")
        return

    from tools import executor as exec_module

    logger.info(f"Initialising {len(configs)} MCP server(s)…")

    for cfg in configs:
        server_name = cfg.get("name", "unknown")
        try:
            tools = await _discover_tools(cfg)
            count = 0
            for tool in tools:
                openai_def = _tool_to_openai(tool, server_name)
                full_name = openai_def["function"]["name"]
                original_name = tool.name
                cfg_snapshot = dict(cfg)  # capture for closure

                # Register handler in executor dispatch table.
                # The handler is called from within FastAPI's running event loop,
                # so we must run the async call in a separate thread's loop.
                def _make_handler(ocfg, oname):
                    def handler(**kwargs):
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                            future = pool.submit(
                                asyncio.run,
                                _call_tool_async(ocfg, oname, kwargs)
                            )
                            return future.result(timeout=30)
                    return handler

                exec_module._TOOL_HANDLERS[full_name] = _make_handler(cfg_snapshot, original_name)
                _mcp_tool_definitions.append(openai_def)
                count += 1

            logger.info(f"  ✓ MCP '{server_name}': {count} tool(s) registered")
        except Exception as exc:
            logger.warning(f"  ✗ MCP '{server_name}' failed: {exc}")
