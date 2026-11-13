---
name: python-mcp-tool
description: Add a tool to a Python MCP server on the official SDK v2 (MCPServer), with an Annotated schema, structured output, ToolError for recoverable failures and in-memory Client tests.
---

# Add a tool to a Python MCP server

Examples: `references/server.py` and `references/test_server.py`.

1. Write the function with type hints for every parameter. Use `Annotated[type, Field(description=..., ...)]` for
   descriptions and limits; give optional parameters defaults.
2. Return a Pydantic model (or `TypedDict`) so clients get `structured_content` as well as text.
3. Write the docstring as the tool description: one sentence on what it does, what it returns, read-only or not.
4. Decorate with `@mcp.tool()`. Name it as a snake_case verb phrase.
5. For a failure the model can recover from, `raise ToolError("...")` with a message that tells it what to try.
   Let unexpected exceptions propagate; the SDK logs them and returns a generic error.
6. Test through the in-memory client: `async with Client(mcp, raise_exceptions=True) as c:`. Cover the schema
   (descriptions and limits are present), a good call, a `ToolError` case and a schema rejection. Mark tests
   `@pytest.mark.anyio` with an `anyio_backend` fixture returning `"asyncio"`.
7. Run `uv run pytest`, `uv run ruff check` and `uv run ruff format --check`. Check there is no `print(` in the server.
