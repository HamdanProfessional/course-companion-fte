#!/usr/bin/env python3
"""
MCP Server startup script for Course Companion FTE.
Runs the MCP server with stdio transport for ChatGPT Apps integration.
"""

import asyncio
import sys
import os

# Add backend to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.api.mcp_server import create_mcp_server

# Widget metadata for ChatGPT UI
WIDGET_URL = os.getenv("WIDGET_URL", "http://92.113.147.250:3505/ui")
WIDGET_DOMAIN = os.getenv("WIDGET_DOMAIN", "92.113.147.250:3505")


async def main():
    """Start the MCP server."""
    print(f"Starting Course Companion FTE MCP Server...", file=sys.stderr)
    print(f"Widget URL: {WIDGET_URL}", file=sys.stderr)

    # Create and run the MCP server
    mcp = create_mcp_server()

    # Run with stdio transport (required for ChatGPT Apps)
    await mcp.run(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())
