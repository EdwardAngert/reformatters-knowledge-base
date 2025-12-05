"""Stdio-based MCP server for Claude Desktop integration."""

import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server

from mcp_server.config import config
from mcp_server.tools import dataset_tools, documentation_tools, knowledge_tools

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def run_server():
    """Run the MCP server using stdio transport for Claude Desktop."""
    logger.info("Starting Reformatters Knowledge Base MCP Server (stdio mode)")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Knowledge base path: {config.knowledge_base_path}")

    if not config.knowledge_base_path.exists():
        logger.warning(f"Knowledge base path does not exist: {config.knowledge_base_path}")

    # Create MCP server
    mcp_server = Server("reformatters-knowledge-base")

    # Register all tools
    dataset_tools.register_tools(mcp_server)
    documentation_tools.register_tools(mcp_server)
    knowledge_tools.register_tools(mcp_server)

    logger.info("Registered MCP tools and resources")

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


def main():
    """Entry point for the stdio server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
