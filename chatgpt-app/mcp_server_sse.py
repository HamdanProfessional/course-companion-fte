#!/usr/bin/env python3
"""
Course Companion FTE - MCP Server with SSE Transport
For hosting on web servers (e.g., sse.testservers.online/mcp)

This version uses Server-Sent Events (SSE) transport instead of stdio,
allowing ChatGPT to connect remotely via HTTP.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://92.113.147.250:3505")
WIDGET_DOMAIN = os.getenv("WIDGET_DOMAIN", "92.113.147.250")
WIDGET_FULL_URL = os.getenv("WIDGET_URL", f"http://{WIDGET_DOMAIN}:3505/ui")

# Create FastAPI app for SSE endpoint
app = FastAPI(title="Course Companion FTE MCP Server")

# Create MCP server instance
mcp_server = Server("course-companion-fte")


class BackendClient:
    """HTTP client for the remote backend API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def get_chapters(self) -> list[Dict[str, Any]]:
        """Get all chapters from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/chapters")
        response.raise_for_status()
        return response.json()

    async def get_chapter(self, chapter_id: str) -> Dict[str, Any]:
        """Get chapter by ID from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/chapters/{chapter_id}")
        response.raise_for_status()
        return response.json()

    async def get_quiz_by_id(self, quiz_id: str) -> Dict[str, Any]:
        """Get quiz by ID from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/quizzes/by-chapter/{quiz_id}")
        response.raise_for_status()
        return response.json()

    async def list_all_quizzes(self) -> list[Dict[str, Any]]:
        """List all available chapters with quizzes (v3 API)."""
        # First get all chapters
        chapters = await self.get_chapters()

        # Filter chapters that have quizzes
        quizzes = []
        for chapter in chapters:
            if chapter.get("has_quiz"):
                quizzes.append({
                    "id": chapter["id"],
                    "title": chapter["title"],
                    "difficulty": chapter.get("difficulty_level", "intermediate"),
                    "order": chapter.get("order", 0)
                })
        return quizzes

    async def get_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user progress from backend (v3 API)."""
        response = await self.client.get(f"{self.base_url}/api/v3/tutor/progress/{user_id}")
        response.raise_for_status()
        return response.json()

    async def search_content(self, query: str, limit: int = 5) -> list[Dict[str, Any]]:
        """Search chapters and content by keywords."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/search",
            params={"q": query, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    async def search_content(self, query: str, limit: int = 5) -> list[Dict[str, Any]]:
        """Search course content."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/search",
            params={"q": query, "limit": limit}
        )
        response.raise_for_status()
        return response.json()


def create_widget_response(content: str) -> Dict[str, Any]:
    """
    Create a tool response with widget metadata for ChatGPT.
    """
    return {
        "content": [
            {"type": "text", "text": content}
        ],
        "_meta": {
            "openai/widgetDomain": WIDGET_DOMAIN,
            "openai/widgetUrl": WIDGET_FULL_URL,
            "openai/widgetCSP": {
                "connect_domains": ["https://chatgpt.com", "http://*.testservers.online"],
                "resource_domains": [
                    "https://*.oaistatic.com",
                    f"http://{WIDGET_DOMAIN}:*",
                    "https://*.testservers.online"
                ]
            }
        }
    }


async def get_chapter_tool(chapter_id: str) -> Dict[str, Any]:
    """Get chapter content."""
    if not chapter_id:
        raise ValueError("chapter_id is required")

    logger.info(f"Fetching chapter: {chapter_id}")

    async with BackendClient(BACKEND_URL) as backend:
        chapter_data = await backend.get_chapter(chapter_id)
        content = json.dumps(chapter_data, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def list_chapters_tool() -> Dict[str, Any]:
    """List all available chapters."""
    logger.info("Listing chapters")

    async with BackendClient(BACKEND_URL) as backend:
        chapters = await backend.get_chapters()

        result = {
            "chapters": [
                {
                    "id": c.get("id"),
                    "title": c.get("title"),
                    "order": c.get("order"),
                    "difficulty": c.get("difficulty_level", "intermediate"),
                    "has_quiz": c.get("has_quiz", False),
                    "estimated_time": c.get("estimated_time", 30)
                }
                for c in chapters
            ],
            "total": len(chapters)
        }

        content = json.dumps(result, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def get_quiz_tool(chapter_id: str) -> Dict[str, Any]:
    """Get quiz for a chapter and return with widget metadata."""
    if not chapter_id:
        raise ValueError("chapter_id is required")

    logger.info(f"Fetching quiz for chapter: {chapter_id}")

    async with BackendClient(BACKEND_URL) as backend:
        quiz_data = await backend.get_quiz_by_id(chapter_id)
        content = json.dumps(quiz_data, indent=2)
        return create_widget_response(content)


async def list_quizzes_tool() -> Dict[str, Any]:
    """List all available quizzes (by chapter)."""
    logger.info("Listing quizzes")

    async with BackendClient(BACKEND_URL) as backend:
        quizzes = await backend.list_all_quizzes()

        result = {
            "quizzes": quizzes,
            "total": len(quizzes),
            "note": "Each quiz is associated with a chapter. Use the chapter ID to get the full quiz."
        }

        content = json.dumps(result, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def get_progress_tool(user_id: str) -> Dict[str, Any]:
    """Get user progress."""
    if not user_id:
        raise ValueError("user_id is required")

    logger.info(f"Fetching progress for user: {user_id}")

    async with BackendClient(BACKEND_URL) as backend:
        progress_data = await backend.get_progress(user_id)
        content = json.dumps(progress_data, indent=2)
        return {"content": [{"type": "text", "text": content}]}


async def search_content_tool(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search course content."""
    logger.info(f"Searching: {query}")

    async with BackendClient(BACKEND_URL) as backend:
        results = await backend.search_content(query, limit)
        content = json.dumps(results, indent=2)
        return {"content": [{"type": "text", "text": content}]}


# Register MCP tools
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="list_chapters",
            description="List all available course chapters with their IDs, titles, and difficulty levels. Use this to find chapter IDs for getting content or quizzes.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_chapter",
            description="Get full chapter content including text, examples, and key concepts. Use chapter_id from list_chapters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "string",
                        "description": "Chapter ID to get content for (e.g., from list_chapters)"
                    }
                },
                "required": ["chapter_id"]
            }
        ),
        Tool(
            name="get_quiz",
            description="Get quiz questions for a chapter and load interactive UI widget. Shows a React quiz component in ChatGPT. Use chapter_id from list_chapters or list_quizzes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "string",
                        "description": "Chapter ID to get quiz for"
                    }
                },
                "required": ["chapter_id"]
            }
        ),
        Tool(
            name="list_quizzes",
            description="List all available quizzes organized by chapter. Returns chapter IDs that can be used with get_quiz.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_progress",
            description="Get user's learning progress including completed chapters, quiz scores, and streak. Requires user_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (UUID format)"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="search_content",
            description="Search course content by keywords across all chapters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'MCP', 'neural networks', 'FastAPI')"
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


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> Any:
    """Handle tool calls."""
    try:
        if name == "list_chapters":
            return await list_chapters_tool()
        elif name == "get_chapter":
            return await get_chapter_tool(**arguments)
        elif name == "get_quiz":
            return await get_quiz_tool(**arguments)
        elif name == "list_quizzes":
            return await list_quizzes_tool()
        elif name == "get_progress":
            return await get_progress_tool(**arguments)
        elif name == "search_content":
            return await search_content_tool(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return {"content": [{"type": "text", "text": f"API Error: {e.response.status_code} - {str(e)}"}]}
    except Exception as e:
        logger.error(f"Tool error: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "course-companion-fte",
        "transport": "SSE",
        "backend": BACKEND_URL,
        "widget_url": WIDGET_FULL_URL,
        "timestamp": datetime.utcnow().isoformat()
    }


# SSE endpoint for MCP
@app.get("/mcp")
async def mcp_endpoint():
    """
    SSE endpoint for MCP connections.
    ChatGPT will connect to this endpoint for server-sent events transport.
    """
    async def event_stream():
        """Stream events for MCP protocol."""
        logger.info("New SSE connection established")

        # Create SSE transport
        transport = SseServerTransport("/messages")

        # Handle the connection
        async with transport.connect() as streams:
            await mcp_server.run(
                streams[0],
                streams[1],
                mcp_server.create_initialization_options()
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


# Messages endpoint for POST requests from ChatGPT
@app.post("/messages")
async def messages_endpoint(request: dict):
    """
    Handle POST requests to /messages endpoint.
    This is used by ChatGPT to send messages to the MCP server.
    """
    logger.info(f"Received message: {request.get('method', 'unknown')}")

    # Process the message through MCP server
    # Note: This is a simplified version - full implementation would
    # properly handle all MCP protocol messages

    return {"status": "ok"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "Course Companion FTE MCP Server",
        "version": "1.0.0",
        "transport": "SSE (Server-Sent Events)",
        "endpoints": {
            "mcp": "/mcp",
            "messages": "/messages",
            "health": "/health"
        },
        "usage": {
            "chatgpt_config": {
                "sse": f"sse.testservers.online/mcp",
                "transport": "sse"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    logger.info("=" * 60)
    logger.info("Course Companion FTE MCP Server (SSE Transport)")
    logger.info(f"Starting on port {port}...")
    logger.info(f"SSE Endpoint: http://0.0.0.0:{port}/mcp")
    logger.info(f"Backend: {BACKEND_URL}")
    logger.info(f"Widget: {WIDGET_FULL_URL}")
    logger.info("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
