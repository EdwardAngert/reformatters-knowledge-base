"""MCP tools for the reformatters knowledge base."""

from typing import Any

from mcp_server.tools import dataset_tools, documentation_tools, knowledge_tools


def register_all_tools(server):
    """Register all MCP tools with the server."""
    # Collect all tools from all modules
    all_tools = (
        dataset_tools.TOOLS + knowledge_tools.TOOLS + documentation_tools.TOOLS
    )

    # Register the centralized list_tools handler
    @server.list_tools()
    async def list_tools():
        """List all available tools."""
        return all_tools

    # Register the centralized call_tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]):
        """Route tool calls to the appropriate handler."""
        # Try each module's handler
        for module in [dataset_tools, knowledge_tools, documentation_tools]:
            try:
                return await module.handle_tool_call(name, arguments)
            except ValueError:
                # Tool not in this module, try next
                continue
        # If we get here, tool wasn't found in any module
        raise ValueError(f"Unknown tool: {name}")


__all__ = ["dataset_tools", "documentation_tools", "knowledge_tools", "register_all_tools"]
