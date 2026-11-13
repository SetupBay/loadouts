import pytest
from mcp import Client

from server import mcp


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with Client(mcp, raise_exceptions=True) as c:
        yield c


@pytest.mark.anyio
async def test_lists_tool_with_described_schema(client: Client):
    tools = (await client.list_tools()).tools
    assert [t.name for t in tools] == ["lookup_term"]
    props = tools[0].input_schema["properties"]
    assert props["term"]["description"] == "Glossary term, case-insensitive"
    assert props["limit"]["maximum"] == 10


@pytest.mark.anyio
async def test_lookup_returns_structured_content(client: Client):
    result = await client.call_tool("lookup_term", {"term": " Loadout ", "limit": 1})
    assert not result.is_error
    assert result.structured_content == {
        "term": "loadout",
        "definition": "A set of agent instruction files, skills and MCP configs for one kind of project.",
        "related": ["fixture"],
    }


@pytest.mark.anyio
async def test_unknown_term_is_a_tool_error_the_model_can_read(client: Client):
    result = await client.call_tool("lookup_term", {"term": "widget"})
    assert result.is_error
    assert "Known terms: fixture, loadout, skill" in result.content[0].text


@pytest.mark.anyio
async def test_schema_rejects_bad_limit_before_the_tool_runs(client: Client):
    result = await client.call_tool("lookup_term", {"term": "skill", "limit": 50})
    assert result.is_error
    assert "limit" in result.content[0].text
