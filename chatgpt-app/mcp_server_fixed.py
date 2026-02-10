#!/usr/bin/env python3
"""
Course Companion FTE - Local MCP Server for ChatGPT Desktop (Fixed)
This server runs locally and connects to the remote backend API.
It provides quiz data with widget metadata for ChatGPT Desktop App.

FIXED: Now includes proper widget metadata for ChatGPT to load React components.
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

# Widget configuration for ChatGPT
WIDGET_DOMAIN = "92.113.147.250"  # Your server domain
WIDGET_FULL_URL = f"http://{WIDGET_DOMAIN}:3505/ui"

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


def create_widget_response(content: str) -> Dict[str, Any]:
    """
    Create a tool response with widget metadata for ChatGPT.

    This tells ChatGPT to load the React widget component.
    """
    return {
        "content": [
            {"type": "text", "text": content}
        ],
        "_meta": {
            "openai/widgetDomain": WIDGET_DOMAIN,
            "openai/widgetUrl": WIDGET_FULL_URL,
            "openai/widgetCSP": {
                "connect_domains": ["https://chatgpt.com"],
                "resource_domains": ["https://*.oaistatic.com", f"http://{WIDGET_DOMAIN}:*"]
            }
        }
    }


async def get_quiz_tool(quiz_id: str) -> Dict[str, Any]:
    """
    Get quiz questions and load interactive UI widget.

    This tool fetches quiz data and instructs ChatGPT to render
    the interactive React quiz component.

    Args:
        quiz_id: The ID of the quiz (e.g., '45e2efd0-8065-4d10-9bf4-19408e3a73fb')

    Returns:
        Response with quiz data and widget metadata
    """
    if not quiz_id:
        raise ValueError("quiz_id is required")

    logger.info(f"Fetching quiz: {quiz_id}")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            quiz_data = await backend.get_quiz(quiz_id)

            # Return with widget metadata
            content = json.dumps(quiz_data, indent=2)
            return create_widget_response(content)

    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise ValueError(f"Failed to fetch quiz: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Error: {str(e)}")


async def list_quizzes_tool() -> Dict[str, Any]:
    """
    List all available quizzes.

    Returns:
        Response with list of available quizzes
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

            content = json.dumps(result, indent=2)
            return {"content": [{"type": "text", "text": content}]}

    except Exception as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Failed to list quizzes: {str(e)}")


async def search_content_tool(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search course content by keywords.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        Response with search results
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

            content = json.dumps(results, indent=2)
            return {"content": [{"type": "text", "text": content}]}

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
            description="Get quiz questions and load interactive UI widget. Shows a React quiz component in ChatGPT.",
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
async def call_tool(name: str, arguments: Any) -> Any:
    """
    Handle tool calls and return proper response format.

    CRITICAL: This must return the dict with _meta for widgets to work!
    """
    try:
        if name == "get_quiz":
            result = await get_quiz_tool(**arguments)
            return result
        elif name == "list_quizzes":
            result = await list_quizzes_tool()
            return result
        elif name == "search_content":
            result = await search_content_tool(**arguments)
            return result
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


async def main():
    """Run the MCP server with stdio transport."""
    logger.info("Starting Course Companion FTE MCP Server (Fixed)")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info(f"Widget URL: {WIDGET_FULL_URL}")
    logger.info("=" * 60)
    logger.info("WIDGET SUPPORT: ENABLED")
    logger.info(f"  Widget Domain: {WIDGET_DOMAIN}")
    logger.info(f"  Widget URL: {WIDGET_FULL_URL}")
    logger.info("=" * 60)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
