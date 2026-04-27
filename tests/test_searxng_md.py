import pytest
import llm
from unittest.mock import patch, MagicMock


def test_tool_registered():
    """searxng_search_md is registered as an llm tool."""
    tools = list(llm.get_tools())
    # get_tools() may return strings or objects with a .name attribute
    tool_names = [t.name if hasattr(t, "name") else t for t in tools]
    assert "searxng_search_md" in tool_names, (
        "searxng_search_md not found in llm.get_tools() — "
        "check the [project.entry-points.llm] entry in pyproject.toml"
    )


def test_unset_url_raises(monkeypatch):
    """searxng_search_md raises ValueError when no URL is configured."""
    from llm_tools_searxng_md import searxng_search_md

    monkeypatch.delenv("SEARXNG_URL", raising=False)

    with patch("llm.get_key", return_value=None):
        with pytest.raises(ValueError, match="SearXNG URL is required"):
            searxng_search_md("test query")


def test_searxng_search_returns_markdown(monkeypatch):
    """searxng_search_md formats results as numbered markdown list (POST by default)."""
    from llm_tools_searxng_md import searxng_search_md

    monkeypatch.delenv("SEARXNG_METHOD", raising=False)

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {
                "title": "SearXNG — the privacy-respecting metasearch engine",
                "url": "https://searxng.org",
                "content": "SearXNG is a free internet metasearch engine.",
            },
            {
                "title": "GitHub: searxng/searxng",
                "url": "https://github.com/searxng/searxng",
                "content": "Source code for SearXNG.",
            },
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("llm.get_key", return_value="https://your-searxng.example.com"):
        with patch("httpx.post", return_value=mock_response) as mock_post:
            result = searxng_search_md("searxng", max_results=2)

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs[0][0].endswith("/search")
    assert call_kwargs[1]["data"]["q"] == "searxng"
    assert call_kwargs[1]["data"]["format"] == "json"

    assert "[1]" in result
    assert "[2]" in result
    assert "SearXNG" in result
    assert "https://searxng.org" in result


def test_searxng_search_get_method(monkeypatch):
    """searxng_search_md uses GET when SEARXNG_METHOD=GET."""
    from llm_tools_searxng_md import searxng_search_md

    monkeypatch.setenv("SEARXNG_METHOD", "GET")

    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status = MagicMock()

    with patch("llm.get_key", return_value="https://your-searxng.example.com"):
        with patch("httpx.get", return_value=mock_response) as mock_get:
            searxng_search_md("test")

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args
    assert call_kwargs[1]["params"]["q"] == "test"
    assert call_kwargs[1]["params"]["format"] == "json"


def test_searxng_search_no_results(monkeypatch):
    """searxng_search_md returns a helpful message when no results come back."""
    from llm_tools_searxng_md import searxng_search_md

    monkeypatch.delenv("SEARXNG_METHOD", raising=False)

    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status = MagicMock()

    with patch("llm.get_key", return_value="https://your-searxng.example.com"):
        with patch("httpx.post", return_value=mock_response):
            result = searxng_search_md("xyzzy_nonexistent_query_12345")

    assert "No results" in result


def test_get_key_alias_used():
    """llm.get_key is called with the correct alias and env var."""
    from llm_tools_searxng_md import searxng_search_md

    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status = MagicMock()

    with patch("llm.get_key", return_value="https://my-searxng.example.com") as mock_key:
        with patch("httpx.post", return_value=mock_response):
            searxng_search_md("test")

    mock_key.assert_called_once_with(alias="searxng_url", env="SEARXNG_URL")
