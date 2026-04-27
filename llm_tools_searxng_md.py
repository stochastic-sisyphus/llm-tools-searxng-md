import os

import httpx
import llm


@llm.hookimpl
def register_tools(register):
    register(searxng_search_md)


def searxng_search_md(query: str, max_results: int = 8) -> str:
    """Search the web via self-hosted SearXNG. Returns top results as markdown.

    Args:
        query: Search query string
        max_results: Max number of results to return (default 8)
    """
    base_url = llm.get_key(alias="searxng_url", env="SEARXNG_URL")
    if not base_url:
        raise ValueError(
            "SearXNG URL is required. Set via 'llm keys set searxng_url <URL>' or SEARXNG_URL env var."
        )

    method = os.environ.get("SEARXNG_METHOD", "POST").upper()
    search_url = f"{base_url.rstrip('/')}/search"
    params = {"q": query, "format": "json"}

    if method == "POST":
        r = httpx.post(search_url, data=params, timeout=15)
    else:
        r = httpx.get(search_url, params=params, timeout=15)

    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])[:max_results]
    if not results:
        return f"No results for: {query}"
    out = []
    for i, res in enumerate(results, 1):
        title = res.get("title", "").strip()
        url = res.get("url", "")
        content = res.get("content", "").strip()
        out.append(f"[{i}] {title}\n  {url}\n  {content}\n")
    return "\n".join(out)
