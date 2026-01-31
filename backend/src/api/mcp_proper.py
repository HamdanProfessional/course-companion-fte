"""
Proper MCP Server for ChatGPT Apps
Implements bidirectional MCP protocol with SSE
"""
import asyncio
import json
import logging
from typing import Any
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from mcp import ClientSession, Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)

router = APIRouter(tags=["MCP"])

# Store active connections
active_sessions = {}

async def handle_mcp_request(data: dict) -> dict:
    """Handle incoming MCP JSON-RPC requests."""
    method = data.get("method")
    params = data.get("params", {})
    request_id = data.get("id")

    logger.info(f"Received MCP request: {method}")

    # Handle initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "server": {
                    "name": "Course Companion FTE",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            },
            "id": request_id
        }

    # Handle tools/list
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "list_chapters",
                        "description": "List all available chapters"
                    },
                    {
                        "name": "get_chapter",
                        "description": "Get chapter content by ID"
                    },
                    {
                        "name": "search_content",
                        "description": "Search course content"
                    },
                    {
                        "name": "get_quiz",
                        "description": "Get quiz questions"
                    },
                    {
                        "name": "submit_quiz",
                        "description": "Submit quiz answers"
                    },
                    {
                        "name": "get_progress",
                        "description": "Get user progress"
                    },
                    {
                        "name": "update_progress",
                        "description": "Update progress"
                    },
                    {
                        "name": "get_streak",
                        "description": "Get streak info"
                    },
                    {
                        "name": "check_access",
                        "description": "Check content access"
                    }
                ]
            },
            "id": request_id
        }

    # Handle tool calls
    elif method == "tools/call":
        # For now, just acknowledge
        return {
            "jsonrpc": "2.0",
            "result": {
                "content": [{"type": "text", "text": "Tool executed"}]
            },
            "id": request_id
        }

    # Default error
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}"
        },
        "id": request_id
    }


@router.post("/api/v1/mcp")
async def mcp_post_endpoint(request: Request):
    """Handle incoming MCP JSON-RPC POST requests."""
    try:
        data = await request.json()
        response = await handle_mcp_request(data)
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"MCP POST error: {str(e)}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)}
            },
            status_code=500
        )


@router.get("/api/v1/mcp")
async def mcp_sse_endpoint():
    """
    MCP SSE endpoint - sends initialization and keeps connection alive.
    ChatGPT will POST requests to the same endpoint.
    """
    async def event_stream():
        try:
            # Send a simple ping to establish connection
            yield ": ping\n\n"

            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield ": keep-alive\n\n"

        except asyncio.CancelledError:
            logger.info("SSE connection closed")
        except Exception as e:
            logger.error(f"SSE error: {str(e)}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Chunking": "no",
            "Content-Type": "text/event-stream; charset=utf-8",
        }
    )
