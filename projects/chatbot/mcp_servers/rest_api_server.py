"""
REST API Fetcher MCP Server
Lets the AI fetch data from any public REST API endpoint.

Tools: rest_get, rest_post
"""

import json
from urllib.parse import urlparse
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rest-api-fetcher")

# Block internal/private addresses to prevent SSRF
_BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "::1",
    "metadata.google.internal",
}
_BLOCKED_PREFIXES = ("192.168.", "10.", "172.16.", "169.254.")


def _is_blocked(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
        host = host.lower()
        if host in _BLOCKED_HOSTS:
            return True
        if any(host.startswith(p) for p in _BLOCKED_PREFIXES):
            return True
        return False
    except Exception:
        return True


def _format_response(res: httpx.Response) -> str:
    content_type = res.headers.get("content-type", "")
    try:
        body = json.dumps(res.json(), indent=2) if "application/json" in content_type else res.text
    except Exception:
        body = res.text
    body = body[:8000] + ("\n…(truncated)" if len(body) > 8000 else "")
    return f"Status: {res.status_code} {res.reason_phrase}\n\n{body}"


@mcp.tool()
def rest_get(url: str, headers: dict = None) -> str:
    """Fetch data from a public REST API endpoint using a GET request."""
    if _is_blocked(url):
        return "Error: Requests to internal/private network addresses are not allowed."
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(url, headers={"Accept": "application/json", **(headers or {})})
        return _format_response(res)
    except Exception as e:
        return f"Fetch error: {e}"


@mcp.tool()
def rest_post(url: str, body: dict, headers: dict = None) -> str:
    """Send a POST request to a public REST API endpoint with a JSON body."""
    if _is_blocked(url):
        return "Error: Requests to internal/private network addresses are not allowed."
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                url,
                json=body,
                headers={"Accept": "application/json", **(headers or {})},
            )
        return _format_response(res)
    except Exception as e:
        return f"Fetch error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
