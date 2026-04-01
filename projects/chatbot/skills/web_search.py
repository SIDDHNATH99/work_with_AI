"""
Web search (DuckDuckGo) and URL-fetching skills.
Includes SSRF-prevention checks for fetch_url.
"""

import ipaddress
import re
import urllib.parse


def search(query: str, max_results: int = 5) -> dict:
    """Search the web using DuckDuckGo (no API key required)."""
    try:
        from ddgs import DDGS
    except ImportError:
        return {"error": "ddgs not installed. Run: pip install ddgs"}

    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title":   r.get("title", ""),
                    "url":     r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
        return {"query": query, "count": len(results), "results": results}
    except Exception as exc:
        return {"error": str(exc)}


def fetch_url(url: str, max_chars: int = 8000) -> dict:
    """Fetch text content from a public URL (SSRF-safe)."""
    # Validate scheme
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return {"error": "Only http:// and https:// URLs are allowed"}

    # Block private/loopback destinations (SSRF prevention)
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname or ""
        if hostname.lower() in ("localhost", "0.0.0.0", "::1"):
            return {"error": "Local/loopback addresses are not allowed"}
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return {"error": "Private/reserved IP addresses are not allowed"}
        except ValueError:
            pass  # hostname — not a raw IP, proceed
    except Exception:
        return {"error": "Invalid URL"}

    try:
        import httpx
    except ImportError:
        return {"error": "httpx not installed. Run: pip install httpx"}

    try:
        headers = {"User-Agent": "CortexChat/2.0 (research assistant; +https://github.com)"}
        with httpx.Client(timeout=15, follow_redirects=True, max_redirects=5) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            text = resp.text

            if "html" in content_type:
                # Strip scripts, styles, and tags for readable plain text
                text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<style[^>]*>.*?</style>",  " ", text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<[^>]+>", " ", text)
                text = re.sub(r"\s+", " ", text).strip()

            truncated = len(text) > max_chars
            return {
                "url":       url,
                "content":   text[:max_chars],
                "chars":     len(text),
                "truncated": truncated,
                "status":    resp.status_code,
            }
    except Exception as exc:
        return {"error": str(exc)}
