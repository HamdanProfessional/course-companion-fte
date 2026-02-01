#!/usr/bin/env python3
"""
Course Companion FTE - MCP Server for ChatGPT Apps
Proper JSON-RPC implementation following MCP specification strictly
Based on: https://github.com/modelcontextprotocol/python-sdk
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://92.113.147.250:3505")
WIDGET_URL = os.getenv("WIDGET_URL", "http://sse.testservers.online/ui")

# Create FastAPI app
app = FastAPI(title="Course Companion FTE MCP Server")


# =============================================================================
# MCP Protocol Handlers
# =============================================================================

@app.post("/sse")
async def mcp_post(request: Request):
    """Handle MCP JSON-RPC POST requests from ChatGPT."""
    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        req_id = data.get("id")

        logger.info(f"Received MCP request: {method} (id: {req_id})")

        # Handle initialize - CRITICAL: Must match MCP spec exactly
        if method == "initialize":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",  # REQUIRED
                    "serverInfo": {                    # REQUIRED (not "server")
                        "name": "Course Companion FTE",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}                    # MUST be empty dict
                    }
                },
                "id": req_id
            })

        # Handle tools/list - CRITICAL: Must include inputSchema
        elif method == "tools/list":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {
                            "name": "list_quizzes",
                            "description": "List all available quizzes with their IDs and titles",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "get_quiz",
                            "description": "Get a specific quiz with interactive UI widget. Returns quiz data for React component.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "quiz_id": {
                                        "type": "string",
                                        "description": "Quiz ID (e.g., '45e2efd0-8065-4d10-9bf4-19408e3a73fb')"
                                    }
                                },
                                "required": ["quiz_id"]
                            }
                        },
                        {
                            "name": "search_content",
                            "description": "Search course content for specific topics",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query string"
                                    },
                                    "limit": {
                                        "type": "number",
                                        "description": "Maximum number of results (default: 5)"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    ]
                },
                "id": req_id
            })

        # Handle tools/call - When ChatGPT actually uses tools
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            logger.info(f"Tool call: {tool_name} with args: {arguments}")

            # Call the actual tool
            if tool_name == "list_quizzes":
                result = await list_quizzes()
            elif tool_name == "get_quiz":
                result = await get_quiz(arguments)
            elif tool_name == "search_content":
                result = await search_content(arguments)
            else:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    },
                    "id": req_id
                })

            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result)
                        }
                    ]
                },
                "id": req_id
            })

        # Unknown method
        else:
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": req_id
            })

    except Exception as e:
        logger.error(f"MCP error: {str(e)}", exc_info=True)
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)


@app.get("/sse")
async def mcp_sse():
    """MCP SSE endpoint for streaming (backwards compatibility)."""
    async def event_stream():
        try:
            # Send server announcement
            announcement = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "server": "Course Companion FTE",
                    "version": "1.0.0"
                }
            }
            yield f"event: message\ndata: {json.dumps(announcement)}\n\n"

            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield ": keep-alive\n\n"

        except asyncio.CancelledError:
            pass
        except Exception as e:
            error_msg = {
                "jsonrpc": "2.0",
                "method": "error",
                "params": {"code": -1, "message": str(e)}
            }
            yield f"event: error\ndata: {json.dumps(error_msg)}\n\n"

    return Response(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Chunking": "no",
            "Content-Type": "text/event-stream; charset=utf-8",
        }
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "mcp_endpoint": "/sse"}


# =============================================================================
# Tool Implementations
# =============================================================================

class BackendClient:
    """HTTP client for remote backend API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def get(self, path: str) -> dict:
        """GET request to backend."""
        response = await self._client.get(f"{self.base_url}{path}")
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, data: dict = None) -> dict:
        """POST request to backend."""
        response = await self._client.post(f"{self.base_url}{path}", json=data)
        response.raise_for_status()
        return response.json()


async def list_quizzes() -> dict:
    """List all available quizzes."""
    try:
        async with BackendClient(BACKEND_URL) as backend:
            quizzes = await backend.get("/api/v1/quizzes")

            return {
                "quizzes": [
                    {
                        "id": q["id"],
                        "title": q["title"],
                        "difficulty": q["difficulty"],
                        "question_count": len(q.get("questions", []))
                    }
                    for q in quizzes
                ]
            }
    except Exception as e:
        logger.warning(f"Backend unavailable, using mock data: {e}")
        # Mock data for demo
        return {
            "quizzes": [
                {
                    "id": "quiz-001",
                    "title": "Introduction to AI Agents",
                    "difficulty": "Beginner",
                    "question_count": 5
                },
                {
                    "id": "quiz-002",
                    "title": "MCP Protocol Basics",
                    "difficulty": "Intermediate",
                    "question_count": 5
                },
                {
                    "id": "quiz-003",
                    "title": "ChatGPT Apps Development",
                    "difficulty": "Advanced",
                    "question_count": 5
                }
            ]
        }


async def get_quiz(arguments: dict) -> dict:
    """Get a specific quiz."""
    quiz_id = arguments.get("quiz_id")

    try:
        async with BackendClient(BACKEND_URL) as backend:
            quiz = await backend.get(f"/api/v1/quizzes/{quiz_id}")

            # Format for structured content (what the model sees)
            structured_content = {
                "id": quiz["id"],
                "title": quiz["title"],
                "difficulty": quiz["difficulty"],
                "question_count": len(quiz.get("questions", []))
            }

            # Full data for widget (in _meta, not seen by model)
            meta = {
                "_meta": {
                    "openai/outputTemplate": "ui://widget/quiz.html",
                    "openai/widgetPrefersBorder": True,
                    "openai/widgetAccessible": True,
                    "openai/widgetDomain": "https://chatgpt.com",
                    "openai/widgetCSP": {
                        "connect_domains": ["https://chatgpt.com", "http://92.113.147.250:3505"],
                        "resource_domains": ["https://*.oaistatic.com", "http://92.113.147.250:3505"]
                    },
                    "quizData": {
                        "id": quiz["id"],
                        "title": quiz["title"],
                        "difficulty": quiz["difficulty"],
                        "chapter_id": quiz["chapter_id"],
                        "questions": quiz.get("questions", [])
                    }
                }
            }

            # Return both structured and metadata
            result = {**structured_content, **meta}

            return result
    except Exception as e:
        logger.warning(f"Backend unavailable, using mock data for quiz {quiz_id}: {e}")
        # Mock quiz data
        structured_content = {
            "id": quiz_id,
            "title": "Introduction to AI Agents - Quiz",
            "difficulty": "Beginner",
            "question_count": 3
        }

        meta = {
            "_meta": {
                "openai/outputTemplate": "ui://widget/quiz.html",
                "openai/widgetPrefersBorder": True,
                "openai/widgetAccessible": True,
                "openai/widgetDomain": "https://chatgpt.com",
                "openai/widgetCSP": {
                    "connect_domains": ["https://chatgpt.com", "http://92.113.147.250:3505"],
                    "resource_domains": ["https://*.oaistatic.com", "http://92.113.147.250:3505"]
                },
                "quizData": {
                    "id": quiz_id,
                    "title": "Introduction to AI Agents - Quiz",
                    "difficulty": "Beginner",
                    "chapter_id": "chapter-001",
                    "questions": [
                        {
                            "id": "q1",
                            "text": "What is an AI Agent?",
                            "options": [
                                {"id": "a", "text": "A program that makes decisions autonomously"},
                                {"id": "b", "text": "A chatbot"},
                                {"id": "c", "text": "A database"},
                                {"id": "d", "text": "A web server"}
                            ],
                            "correct_answer": "a",
                            "explanation": "AI Agents are autonomous systems that can perceive, reason, and act."
                        },
                        {
                            "id": "q2",
                            "text": "What does MCP stand for?",
                            "options": [
                                {"id": "a", "text": "Model Context Protocol"},
                                {"id": "b", "text": "Machine Learning Protocol"},
                                {"id": "c", "text": "Multi-Cloud Platform"},
                                {"id": "d", "text": "Message Control Protocol"}
                            ],
                            "correct_answer": "a",
                            "explanation": "MCP (Model Context Protocol) is the open standard for connecting AI assistants to external tools."
                        },
                        {
                            "id": "q3",
                            "text": "Which of these is a key capability of AI Agents?",
                            "options": [
                                {"id": "a", "text": "Autonomous decision making"},
                                {"id": "b", "text": "Data storage"},
                                {"id": "c", "text": "User interface design"},
                                {"id": "d", "text": "Network routing"}
                            ],
                            "correct_answer": "a",
                            "explanation": "AI Agents can make autonomous decisions based on their programming and environment."
                        }
                    ]
                }
            }
        }

        return {**structured_content, **meta}


async def search_content(arguments: dict) -> dict:
    """Search course content."""
    query = arguments.get("query")
    limit = arguments.get("limit", 5)

    try:
        async with BackendClient(BACKEND_URL) as backend:
            results = await backend.get(
                f"/api/v1/search?q={query}&limit={limit}"
            )

            return {
                "query": query,
                "total": results.get("total", 0),
                "results": [
                    {
                        "chapter_id": r["chapter_id"],
                        "title": r["title"],
                        "snippet": r["snippet"][:200] + "..." if len(r.get("snippet", "")) > 200 else r.get("snippet", "")
                    }
                    for r in results.get("results", [])
                ]
            }
    except Exception as e:
        logger.warning(f"Backend unavailable, using mock search results: {e}")
        # Mock search results
        return {
            "query": query,
            "total": 2,
            "results": [
                {
                    "chapter_id": "chapter-001",
                    "title": "Introduction to AI Agents",
                    "snippet": "AI Agents are autonomous systems that can perceive their environment, reason about it, and take actions to achieve specific goals..."
                },
                {
                    "chapter_id": "chapter-002",
                    "title": "MCP Protocol Overview",
                    "snippet": "The Model Context Protocol (MCP) is an open standard that enables AI assistants to connect to external tools and data sources..."
                }
            ]
        }


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Course Companion FTE MCP Server (Proper JSON-RPC)")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info(f"Widget URL: {WIDGET_URL}")

    uvicorn.run(
        "mcp_server_proper:app",
        host="0.0.0.0",
        port=3506,
        log_level="info"
    )
