"""Tools for searching and accessing the knowledge base."""

import logging
from pathlib import Path
from typing import Any

from mcp.server import Server

from mcp_server.config import config

logger = logging.getLogger(__name__)


def register_tools(server: Server) -> None:
    """Register knowledge base tools with the MCP server."""

    @server.list_tools()
    async def list_tools() -> list[dict[str, Any]]:
        """List available knowledge base tools."""
        return [
            {
                "name": "search_guides",
                "description": "Search user guides in the knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "search_playbooks",
                "description": "Search support playbooks in the knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "list_all_knowledge",
                "description": "Browse entire knowledge base structure",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Handle tool calls for knowledge base operations."""
        if name == "search_guides":
            return await _search_guides(arguments["query"])
        elif name == "search_playbooks":
            return await _search_playbooks(arguments["query"])
        elif name == "list_all_knowledge":
            return await _list_all_knowledge()
        else:
            raise ValueError(f"Unknown tool: {name}")


async def _search_guides(query: str) -> list[dict[str, Any]]:
    """Search user guides."""
    logger.info(f"Searching guides for: {query}")

    guides_path = config.knowledge_base_path / "guides"
    if not guides_path.exists():
        return [
            {
                "type": "text",
                "text": "Guides directory not found. Knowledge base may not be initialized yet.",
            }
        ]

    results = []
    query_lower = query.lower()

    for guide_file in guides_path.glob("*.md"):
        content = guide_file.read_text()
        if query_lower in content.lower():
            results.append(
                {
                    "name": guide_file.stem.replace("-", " ").title(),
                    "path": str(guide_file.relative_to(config.knowledge_base_path)),
                    "preview": content[:200] + "...",
                }
            )

    if not results:
        return [
            {
                "type": "text",
                "text": f"No guides found matching '{query}'",
            }
        ]

    result_text = f"Found {len(results)} guide(s) matching '{query}':\n\n"
    for r in results:
        result_text += f"**{r['name']}**\n"
        result_text += f"Path: `{r['path']}`\n"
        result_text += f"Preview: {r['preview']}\n\n"

    return [{"type": "text", "text": result_text}]


async def _search_playbooks(query: str) -> list[dict[str, Any]]:
    """Search support playbooks."""
    logger.info(f"Searching playbooks for: {query}")

    playbooks_path = config.knowledge_base_path / "playbooks"
    if not playbooks_path.exists():
        return [
            {
                "type": "text",
                "text": "Playbooks directory not found. Knowledge base may not be initialized yet.",
            }
        ]

    results = []
    query_lower = query.lower()

    for playbook_file in playbooks_path.rglob("*.md"):
        if playbook_file.name == "playbook-template.md":
            continue

        content = playbook_file.read_text()
        if query_lower in content.lower():
            results.append(
                {
                    "name": playbook_file.stem.replace("-", " ").title(),
                    "path": str(playbook_file.relative_to(config.knowledge_base_path)),
                    "category": playbook_file.parent.name,
                    "preview": content[:200] + "...",
                }
            )

    if not results:
        return [
            {
                "type": "text",
                "text": f"No playbooks found matching '{query}'",
            }
        ]

    result_text = f"Found {len(results)} playbook(s) matching '{query}':\n\n"
    for r in results:
        result_text += f"**{r['name']}** ({r['category']})\n"
        result_text += f"Path: `{r['path']}`\n"
        result_text += f"Preview: {r['preview']}\n\n"

    return [{"type": "text", "text": result_text}]


async def _list_all_knowledge() -> list[dict[str, Any]]:
    """List all knowledge base content."""
    logger.info("Listing all knowledge base content")

    kb_path = config.knowledge_base_path
    if not kb_path.exists():
        return [
            {
                "type": "text",
                "text": "Knowledge base not found. Initialize it first.",
            }
        ]

    result = "# Knowledge Base Structure\n\n"

    for category in ["guides", "playbooks", "examples", "architecture"]:
        category_path = kb_path / category
        if not category_path.exists():
            continue

        result += f"## {category.title()}\n\n"
        files = list(category_path.rglob("*.md"))

        if not files:
            result += "*No content yet*\n\n"
            continue

        for file in sorted(files):
            rel_path = file.relative_to(kb_path)
            result += f"- `{rel_path}`\n"

        result += "\n"

    return [{"type": "text", "text": result}]
