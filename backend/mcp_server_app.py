#!/usr/bin/env python3
"""
Course Companion FTE - MCP Server for ChatGPT Apps
Based on OpenAI Apps SDK official documentation

This MCP server:
1. Registers UI templates as resources (text/html+skybridge)
2. Defines tools with proper metadata
3. Returns structuredContent, content, and _meta
4. Works with ChatGPT Apps in both Desktop and browser
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://92.113.147.250:3505")
WIDGET_URL = os.getenv("WIDGET_URL", "http://sse.testservers.online/ui")

# Create FastMCP server
mcp = FastMCP(
    name="Course Companion FTE",
    instructions="""
Course Companion FTE - Your AI-powered tutor for mastering AI Agent Development.

Available tools:
- list_quizzes: List all available quizzes
- get_quiz: Get a specific quiz with interactive UI
- search_content: Search course content
- get_progress: Get learning progress

The get_quiz tool loads an interactive quiz widget where you can answer questions and see immediate feedback.
"""
)


# =============================================================================
# HTTP Client for Backend API
# =============================================================================

class BackendClient:
    """HTTP client for remote backend API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def get_quiz(self, quiz_id: str) -> dict:
        """Get quiz by ID."""
        response = await self._client.get(f"{self.base_url}/api/v1/quizzes/{quiz_id}")
        response.raise_for_status()
        return response.json()

    async def list_quizzes(self) -> list:
        """List all quizzes."""
        response = await self._client.get(f"{self.base_url}/api/v1/quizzes")
        response.raise_for_status()
        return response.json()

    async def search_content(self, query: str, limit: int = 5) -> dict:
        """Search course content."""
        response = await self._client.get(
            f"{self.base_url}/api/v1/search",
            params={"q": query, "limit": limit}
        )
        response.raise_for_status()
        return response.json()


# =============================================================================
# UI Template Resource
# =============================================================================

def get_quiz_widget_html() -> str:
    """
    Returns the HTML template for the quiz widget.
    This will be registered as an MCP resource with text/html+skybridge MIME type.
    """
    # Read the React component bundle
    component_js_path = Path(__file__).parent.parent / "chatgpt-ui" / "dist" / "component.js"

    # For local development, use the hosted version
    component_url = f"{WIDGET_URL}/dist/component.js"

    return f"""
<div id="root"></div>
<script type="module" src="{component_url}"></script>
    """.strip()


@mcp.resource("ui://widget/quiz.html")
async def quiz_widget_resource() -> str:
    """
    Register the quiz widget UI template.
    MIME type: text/html+skybridge tells ChatGPT this is a widget template.
    """
    html = get_quiz_widget_html()

    # Return with metadata for CSP, borders, etc.
    # In FastMCP, resources return the content directly
    return html


# =============================================================================
# Tools
# =============================================================================

@mcp.tool()
async def list_quizzes() -> dict:
    """
    List all available quizzes.

    Returns a list of all quizzes with their IDs, titles, and question counts.
    Use this to see what quizzes are available before taking one.
    """
    logger.info("Listing quizzes")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            quizzes = await backend.list_quizzes()

            # Format for structured content (what the model sees)
            structured = {
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

            return {
                "structuredContent": structured,
                "content": f"Found {len(quizzes)} quizzes available.",
            }

    except Exception as e:
        logger.error(f"Error listing quizzes: {e}")
        return {
            "structuredContent": {"error": str(e)},
            "content": f"Sorry, I couldn't list the quizzes. Error: {str(e)}",
        }


@mcp.tool()
async def get_quiz(quiz_id: str) -> dict:
    """
    Get a quiz and load the interactive quiz UI widget.

    This tool fetches the quiz data and instructs ChatGPT to render
    the interactive React quiz component where you can answer questions.

    Args:
        quiz_id: The ID of the quiz (e.g., '45e2efd0-8065-4d10-9bf4-19408e3a73fb')

    Returns:
        Quiz data with structured content for the model and widget rendering
    """
    if not quiz_id:
        raise ValueError("quiz_id is required")

    logger.info(f"Getting quiz: {quiz_id}")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            quiz = await backend.get_quiz(quiz_id)

            # Format for structured content (what the model sees)
            # Keep this concise - only what the model needs to reason about
            structured_content = {
                "id": quiz["id"],
                "title": quiz["title"],
                "difficulty": quiz["difficulty"],
                "question_count": len(quiz.get("questions", [])),
            }

            # Put detailed quiz data in _meta (only the widget sees this, never the model)
            meta = {
                "_meta": {
                    # Points to the UI template resource
                    "openai/outputTemplate": "ui://widget/quiz.html",

                    # Widget settings
                    "openai/widgetPrefersBorder": True,
                    "openai/widgetAccessible": True,  # Allow widget to call tools

                    # CSP and domain settings
                    "openai/widgetDomain": "https://chatgpt.com",
                    "openai/widgetCSP": {
                        "connect_domains": ["https://chatgpt.com", "http://92.113.147.250:3505"],
                        "resource_domains": ["https://*.oaistatic.com", "http://92.113.147.250:3505"],
                    },

                    # Full quiz data for the widget (model never sees this)
                    "quizData": {
                        "id": quiz["id"],
                        "title": quiz["title"],
                        "difficulty": quiz["difficulty"],
                        "chapter_id": quiz["chapter_id"],
                        "questions": quiz.get("questions", []),
                    },
                }
            }

            return {
                "structuredContent": structured_content,
                "content": f"Loading {quiz['title']} quiz...",
                **meta
            }

    except Exception as e:
        logger.error(f"Error getting quiz: {e}")
        return {
            "structuredContent": {"error": str(e)},
            "content": f"Sorry, I couldn't load the quiz. Error: {str(e)}",
        }


@mcp.tool()
async def search_content(query: str, limit: int = 5) -> dict:
    """
    Search course content for specific topics.

    Args:
        query: Search query string (keywords, topics, concepts)
        limit: Maximum number of results (default: 5)

    Returns:
        Search results with relevant chapters and content snippets
    """
    if not query or not query.strip():
        raise ValueError("query is required")

    logger.info(f"Searching: {query}")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            results = await backend.search_content(query, limit)

            structured = {
                "query": query,
                "total": results.get("total", 0),
                "results": [
                    {
                        "chapter_id": r["chapter_id"],
                        "title": r["title"],
                        "snippet": r["snippet"][:200] + "..." if len(r.get("snippet", "")) > 200 else r.get("snippet", ""),
                    }
                    for r in results.get("results", [])
                ]
            }

            return {
                "structuredContent": structured,
                "content": f"Found {results.get('total', 0)} results for '{query}'",
            }

    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "structuredContent": {"error": str(e)},
            "content": f"Search failed: {str(e)}",
        }


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Run the MCP server with SSE transport for remote access."""
    logger.info("Starting Course Companion FTE MCP Server")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info(f"Widget URL: {WIDGET_URL}")

    # Run FastMCP with SSE transport
    # This will start an HTTP server on the specified port
    import uvicorn

    if "__compiled__" not in dir(sys):
        # When running as script, start the server
        mcp.run(transport="sse", host="0.0.0.0", port=3506)


if __name__ == "__main__":
    main()
