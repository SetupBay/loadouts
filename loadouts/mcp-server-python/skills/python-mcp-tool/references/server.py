"""Glossary MCP server: one read-only tool, built on the official MCP Python SDK v2 (MCPServer)."""

import logging
import sys
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field

# stdout carries the protocol over stdio; logs go to stderr.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("glossary")

GLOSSARY = {
    "loadout": "A set of agent instruction files, skills and MCP configs for one kind of project.",
    "skill": "A folder with a SKILL.md that an agent loads when the task matches its description.",
    "fixture": "A small project the verifier copies a loadout into and runs commands against.",
}

mcp = MCPServer("glossary")


class Definition(BaseModel):
    term: str
    definition: str
    related: list[str]


@mcp.tool()
def lookup_term(
    term: Annotated[
        str,
        Field(min_length=1, max_length=64, description="Glossary term, case-insensitive"),
    ],
    limit: Annotated[int, Field(ge=1, le=10, description="Maximum related terms to return")] = 3,
) -> Definition:
    """Look up a project glossary term. Returns the definition and related terms. Read-only."""
    key = term.strip().lower()
    if key not in GLOSSARY:
        # ToolError: the model sees this message and can retry with a better term.
        raise ToolError(f"Unknown term {key!r}. Known terms: {', '.join(sorted(GLOSSARY))}.")
    log.info("lookup %s", key)
    related = [t for t in sorted(GLOSSARY) if t != key][:limit]
    return Definition(term=key, definition=GLOSSARY[key], related=related)


if __name__ == "__main__":
    mcp.run()
