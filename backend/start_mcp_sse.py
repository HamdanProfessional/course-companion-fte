#!/usr/bin/env python3
"""
MCP Server with SSE transport for Course Companion FTE.
Runs the MCP server with HTTP/SSE transport for remote ChatGPT Apps integration.
"""

import asyncio
import sys
import os
import logging

# Add backend to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.api.mcp_server import create_mcp_server
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "3506"))


async def main():
    """Start the MCP server with SSE transport."""
    logger.info(f"Starting Course Companion FTE MCP Server (SSE) on {HOST}:{PORT}")

    # Create the MCP server
    mcp = create_mcp_server()

    # Create FastAPI app from MCP server with SSE transport
    app = mcp.create_sse_server()

    # Run with uvicorn
    config = uvicorn.Config(app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
