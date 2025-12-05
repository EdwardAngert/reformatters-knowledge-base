"""Main MCP server implementation."""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from mcp.server import Server
from mcp.server.sse import SseServerTransport

from mcp_server.config import config
from mcp_server.tools import register_all_tools

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

mcp_server = Server("reformatters-knowledge-base")
sse_transport = SseServerTransport("/messages/")

# Register all tools with the MCP server
register_all_tools(mcp_server)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for the FastAPI app."""
    logger.info("Starting Reformatters Knowledge Base MCP Server")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Knowledge base path: {config.knowledge_base_path}")

    if not config.knowledge_base_path.exists():
        logger.warning(f"Knowledge base path does not exist: {config.knowledge_base_path}")

    yield

    logger.info("Shutting down MCP server")


app = FastAPI(
    title="Reformatters Knowledge Base MCP Server",
    description="MCP server providing access to reformatters documentation and expertise",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Reformatters Knowledge Base MCP Server",
        "version": "0.1.0",
        "status": "running",
        "environment": config.environment,
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/sse")
async def handle_sse(request: Request) -> Response:
    """Handle SSE connections for MCP."""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )
    return Response()


@app.post("/messages/")
async def handle_messages(request: Request) -> Response:
    """Handle incoming MCP messages."""
    return await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


logger.info("Registered MCP tools and resources")


def main() -> None:
    """Main entry point."""
    import uvicorn

    # Debug logging for Railway deployment
    logger.info(f"Starting uvicorn with host={config.host}, port={config.port}")
    logger.info(f"Environment variables: PORT={os.getenv('PORT')}, HOST={os.getenv('HOST')}")

    uvicorn.run(
        "mcp_server.server:app",
        host=config.host,
        port=config.port,
        reload=config.is_development,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
