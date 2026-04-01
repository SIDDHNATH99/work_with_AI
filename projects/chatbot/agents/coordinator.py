"""
Agent coordinator — creates and manages specialized agents.

System prompts and factory functions live here.
`init_coordinator()` must be called at application startup (from main.py lifespan).
`run_subagent()` is the entry-point used by the spawn_subagent tool.
"""

import json
import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

# ── System prompts ─────────────────────────────────────────────────────────

COORDINATOR_PROMPT = """\
You are CortexChat, an advanced AI assistant with access to a rich set of tools and specialized subagents.

## When to use tools
- **Simple Q&A / conversation** → answer directly, no tools needed
- **Math / calculation** → use `calculate`
- **Current events, facts, documentation** → use `web_search` then `fetch_url` for details
- **Code: write, test, debug** → use `run_python` to verify before presenting
- **Files: read or write workspace files** → use `read_workspace_file` / `write_workspace_file`
- **Remember facts across sessions** → use `memory_set` / `memory_get`
- **Database queries (list tables, run SQL, describe schema)** → use `mcp__postgres__pg_list_tables`, `mcp__postgres__pg_query`, or `mcp__postgres__pg_describe_table` directly
- **Complex research task** → spawn `research` subagent
- **Complex coding task** → spawn `coder` subagent
- **Data analysis** → spawn `analyst` subagent

## Guidelines
- Use markdown formatting (headers, bullets, code fences).
- Always test code with `run_python` before presenting it as final.
- Chain tools when needed: search → fetch → analyze → respond.
- When spawning a subagent provide a detailed, self-contained task description.
- Be concise, accurate, and direct.
"""

RESEARCH_PROMPT = """\
You are a Research Agent specialised in information gathering and synthesis.

Your process:
1. Formulate effective search queries for the topic.
2. Use `web_search` to find relevant sources.
3. Use `fetch_url` to read key articles in detail.
4. Cross-reference sources and synthesise findings.
5. Present a well-structured answer with citations (URLs).

Be thorough but concise. Cite sources. Flag low-confidence information.
"""

CODER_PROMPT = """\
You are a Coding Agent specialised in writing, testing, and explaining code.
You can also answer general knowledge questions directly or use `web_search` to look up current information.

Your process for coding tasks:
1. Understand the requirement fully.
2. Write clean, idiomatic code.
3. Always test the code using `run_python` before finalising.
4. Fix any errors revealed by the output and re-test.
5. Present the final, working code with a brief explanation.

For general questions: answer directly from knowledge if confident, otherwise use `web_search` + `fetch_url`.
Prefer correctness over cleverness. Include usage examples for code.
"""

ANALYST_PROMPT = """\
You are a Data Analysis Agent specialised in analytical reasoning and computation.

Your process:
1. Understand the data or problem clearly.
2. Use `run_python` for numerical analysis, statistics, and visualisation scripts.
3. Use `web_search` / `fetch_url` for reference data or context.
4. Present findings with: summary, key insights, methodology, and caveats.

Show your work. Be precise with numbers. State assumptions explicitly.
"""

# ── State (injected at startup) ────────────────────────────────────────────

_client = None
_model: str = ""
_inference: dict = {}


def init_coordinator(client, model: str, inference: dict) -> None:
    """Called from main.py at startup to inject shared OpenAI client."""
    global _client, _model, _inference
    _client = client
    _model = model
    _inference = inference
    logger.info("Agent coordinator initialised.")


# ── Factory functions ──────────────────────────────────────────────────────

def _make_agent(system_prompt: str, tools: list, name: str, max_iter: int = 8) -> BaseAgent:
    return BaseAgent(
        client=_client,
        model=_model,
        system_prompt=system_prompt,
        tools=tools,
        inference=_inference,
        max_iterations=max_iter,
        name=name,
    )


def create_coordinator() -> BaseAgent:
    from tools.registry import COORDINATOR_TOOLS
    return _make_agent(COORDINATOR_PROMPT, COORDINATOR_TOOLS, "coordinator", max_iter=12)


def create_research_agent() -> BaseAgent:
    from tools.registry import RESEARCH_TOOLS
    return _make_agent(RESEARCH_PROMPT, RESEARCH_TOOLS, "research")


def create_coder_agent() -> BaseAgent:
    from tools.registry import CODER_TOOLS
    return _make_agent(CODER_PROMPT, CODER_TOOLS, "coder")


def create_analyst_agent() -> BaseAgent:
    from tools.registry import ANALYST_TOOLS
    return _make_agent(ANALYST_PROMPT, ANALYST_TOOLS, "analyst")


def create_agent(agent_type: str) -> BaseAgent:
    """Return the appropriate agent for the given type string."""
    return {
        "coordinator": create_coordinator,
        "research":    create_research_agent,
        "coder":       create_coder_agent,
        "analyst":     create_analyst_agent,
    }.get(agent_type, create_coordinator)()


# ── Subagent entry-point (called by spawn_subagent tool) ──────────────────

def run_subagent(agent_type: str, task: str, context: str = "") -> str:
    """Spawn a subagent, run it on `task`, return a JSON string result."""
    if _client is None:
        return json.dumps({"error": "Coordinator not initialised (server still starting?)"})

    valid_types = {"research", "coder", "analyst"}
    if agent_type not in valid_types:
        return json.dumps({
            "error": f"Unknown agent type: {agent_type!r}. Choose from: {sorted(valid_types)}"
        })

    logger.info(f"Spawning subagent type={agent_type!r} task={task[:80]!r}")
    agent = create_agent(agent_type)

    # Append MCP tools so subagents can use dynamically registered tools (e.g. postgres)
    from cortex_mcp.client import get_mcp_tool_definitions
    mcp_defs = get_mcp_tool_definitions()
    if mcp_defs:
        agent.tools = agent.tools + mcp_defs

    result = agent.run([{"role": "user", "content": task}], extra_context=context)

    return json.dumps({
        "agent_type":  agent_type,
        "result":      result.get("reply", ""),
        "tools_used":  result.get("tools_used", []),
        "iterations":  result.get("iterations", 0),
    })
