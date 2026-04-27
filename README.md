# llm-tools-searxng-md

An [llm](https://llm.datasette.io/) plugin that exposes a `searxng_search_md` tool backed by a self-hosted [SearXNG](https://searxng.org/) instance.

> **Relationship to llm-tools-searxng**: This is a markdown-output alternative to [llm-tools-searxng](https://pypi.org/project/llm-tools-searxng/) by Justyn Shull. Use that one if you want structured JSON; use this one if you want LLM-friendly markdown. This package also uses `llm keys set` for URL management and defaults to POST (better compatibility with most SearXNG instances).

## Installation

```bash
llm install llm-tools-searxng-md
```

Or in editable mode from source:

```bash
llm install -e /path/to/llm-tools-searxng
```

## Configuration

### Recommended: llm keys

```bash
llm keys set searxng_url
# paste your SearXNG instance URL when prompted
```

### Alternative: environment variable

```bash
export SEARXNG_URL=https://your-searxng.example.com
```

The URL is resolved in order: `llm keys set searxng_url` → `SEARXNG_URL` env var. **One of these is required** — there is no default.

The endpoint used is `$SEARXNG_URL/search` with `format=json` — your instance must have the JSON output format enabled in its settings.

### HTTP method

By default the plugin uses **POST** (better compatibility with most SearXNG instances). To force GET:

```bash
export SEARXNG_METHOD=GET
```

## Public SearXNG instances

If you don't run your own instance, several public ones are available. Check the [SearXNG instance list](https://searx.space/) for uptime and privacy policies before using one. A few commonly cited options:

- `https://paulgo.io`
- `https://search.brave4u.com`
- `https://searx.be`

Note: public instances may rate-limit or restrict the JSON API. Self-hosting is recommended for reliable tool use.

## Usage

After installing, the tool is automatically available to any model that supports tool calling:

```bash
llm prompt -T searxng_search_md "what is searxng"
```

Specify a model explicitly if your default does not support tools:

```bash
llm prompt -m gpt-4o -T searxng_search_md "latest news on llm tool plugins"
```

Verify the tool is registered:

```bash
llm tools
# should list: searxng_search_md
```

## Tool signature

```python
def searxng_search_md(query: str, max_results: int = 8) -> str
```

Returns the top `max_results` results as a numbered markdown list with title, URL, and snippet for each result.

## Running tests

```bash
pip install -e '.[test]'
pytest tests/
```

## Publishing to PyPI

Build and publish with `uv`:

```bash
uv build
uv publish
```

Or with the standard toolchain:

```bash
pip install build twine
python -m build
twine upload dist/*
```

Bump `version` in `pyproject.toml` before each release.

## License

Apache-2.0
