#!/usr/bin/env python3
"""
Course Companion FTE - Local MCP Server for ChatGPT Desktop
This server runs locally and connects to the remote backend API.
It provides quiz data with widget metadata for ChatGPT Desktop App.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://92.113.147.250:3505")
WIDGET_URL = os.getenv("WIDGET_URL", "http://92.113.147.250:3505/ui")

# Create MCP server instance
server = Server("course-companion-fte")


class BackendClient:
    """HTTP client for the remote backend API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def get_quiz(self, quiz_id: str) -> Dict[str, Any]:
        """Get quiz by ID from backend."""
        response = await self.client.get(f"{self.base_url}/api/v1/quizzes/{quiz_id}")
        response.raise_for_status()
        return response.json()


async def get_quiz_tool(quiz_id: str) -> str:
    """
    Get quiz questions and load interactive UI widget.

    This tool fetches quiz data and instructs ChatGPT to render
    the interactive React quiz component.

    Args:
        quiz_id: The ID of the quiz (e.g., '45e2efd0-8065-4d10-9bf4-19408e3a73fb')

    Returns:
        JSON string with quiz data for the React widget
    """
    if not quiz_id:
        raise ValueError("quiz_id is required")

    logger.info(f"Fetching quiz: {quiz_id}")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            quiz_data = await backend.get_quiz(quiz_id)

            # The quiz data will be used by the React widget
            # Return as JSON string
            return json.dumps(quiz_data)

    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise ValueError(f"Failed to fetch quiz: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Error: {str(e)}")


async def list_quizzes_tool() -> str:
    """
    List all available quizzes.

    Returns:
        JSON string with list of available quizzes
    """
    logger.info("Listing quizzes")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            response = await backend.client.get(f"{backend.base_url}/api/v1/quizzes")
            response.raise_for_status()
            quizzes = response.json()

            # Format for display
            result = {
                "quizzes": [
                    {
                        "id": q["id"],
                        "title": q["title"],
                        "difficulty": q["difficulty"],
                        "question_count": len(q.get("questions", [])),
                    }
                    for q in quizzes
                ]
            }

            return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Failed to list quizzes: {str(e)}")


async def search_content_tool(query: str, limit: int = 5) -> str:
    """
    Search course content by keywords.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        JSON string with search results
    """
    logger.info(f"Searching: {query}")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            response = await backend.client.get(
                f"{backend.base_url}/api/v1/search",
                params={"q": query, "limit": limit}
            )
            response.raise_for_status()
            results = response.json()

            return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Search failed: {str(e)}")


# Register tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_quiz",
            description="Get quiz questions and load interactive UI widget. Returns quiz data for React component.",
            inputSchema={
                "type": "object",
                "properties": {
                    "quiz_id": {
                        "type": "string",
                        "description": "Quiz ID (e.g., '45e2efd0-8065-4d10-9bf4-19408e3a73fb')"
                    }
                },
                "required": ["quiz_id"]
            }
        ),
        Tool(
            name="list_quizzes",
            description="List all available quizzes with their IDs",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="search_content",
            description="Search course content by keywords",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'MCP', 'neural networks')"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "get_quiz":
            result = await get_quiz_tool(**arguments)
            return [TextContent(type="text", text=result)]
        elif name == "list_quizzes":
            result = await list_quizzes_tool()
            return [TextContent(type="text", text=result)]
        elif name == "search_content":
            result = await search_content_tool(**arguments)
            return [TextContent(type="text", text=result)]
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server with stdio transport."""
    logger.info("Starting Course Companion FTE MCP Server (Local)")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info(f"Widget URL: {WIDGET_URL}")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
