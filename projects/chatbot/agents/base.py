"""
BaseAgent — agentic tool-calling loop for OpenAI-compatible APIs.

Implements the standard ReAct pattern:
  1. Send messages + tools to model
  2. If response contains tool_calls → execute them, append results
  3. Loop until no tool_calls or max_iterations reached
  4. Return final text response + metadata
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Generic agent that runs a tool-calling loop against any
    OpenAI-compatible API endpoint.
    """

    def __init__(
        self,
        client,
        model: str,
        system_prompt: str,
        tools: list | None = None,
        inference: dict | None = None,
        max_iterations: int = 10,
        name: str = "agent",
    ):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.inference = inference or {}
        self.max_iterations = max_iterations
        self.name = name

    def run(self, messages: list, extra_context: str = "") -> dict:
        """
        Run the agentic loop.

        Args:
            messages:      Conversation history in OpenAI format.
            extra_context: Optional extra text appended to the system prompt.

        Returns:
            dict with keys: reply, tools_used, iterations, tokens_used, error?
        """
        from tools.executor import execute_tool

        sys_prompt = self.system_prompt
        if extra_context:
            sys_prompt += f"\n\n### Additional Context\n{extra_context}"

        api_msgs = [{"role": "system", "content": sys_prompt}] + list(messages)
        tools_used: list[str] = []

        for iteration in range(1, self.max_iterations + 1):
            # Build API call kwargs
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": api_msgs,
                **self.inference,
            }
            if self.tools:
                kwargs["tools"] = self.tools
                kwargs["tool_choice"] = "auto"

            try:
                response = self.client.chat.completions.create(**kwargs)
            except Exception as exc:
                logger.error(f"[{self.name}] API error on iteration {iteration}: {exc}", exc_info=True)
                return {
                    "reply": f"API error: {exc}",
                    "tools_used": tools_used,
                    "iterations": iteration,
                    "tokens_used": 0,
                    "error": str(exc),
                }

            choice = response.choices[0]
            msg = choice.message

            # ── No tool calls → done ───────────────────────────────────
            if not msg.tool_calls:
                return {
                    "reply":       msg.content or "",
                    "tools_used":  tools_used,
                    "iterations":  iteration,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                }

            # ── Append assistant turn (with tool_calls) ────────────────
            api_msgs.append({
                "role":       "assistant",
                "content":    msg.content,
                "tool_calls": [
                    {
                        "id":   tc.id,
                        "type": "function",
                        "function": {
                            "name":      tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            # ── Execute each tool call, append results ─────────────────
            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                logger.info(
                    f"[{self.name}] iter={iteration} tool={tool_name} "
                    f"args={json.dumps(args)[:200]}"
                )
                tools_used.append(tool_name)
                result = execute_tool(tool_name, args)

                api_msgs.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result,
                })

        # Max iterations exhausted
        return {
            "reply": (
                "I reached the tool-call iteration limit. "
                "Please try a more specific request or break it into smaller steps."
            ),
            "tools_used":  tools_used,
            "iterations":  self.max_iterations,
            "tokens_used": 0,
            "error":       "max_iterations_reached",
        }
