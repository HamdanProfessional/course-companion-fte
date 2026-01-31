"""
Minimal MCP SSE endpoint for ChatGPT compatibility.
Reduces data size to avoid timeout issues.
"""
import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["MCP"])

@router.get("/api/v1/mcp")
async def mcp_minimal():
    """Minimal MCP SSE endpoint for ChatGPT compatibility."""

    async def stream():
        # Only send initialize with minimal info
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "server": {
                    "name": "Course Companion FTE",
                    "version": "1.0.0"
                }
            }
        }
        yield f"event: message\ndata: {json.dumps(init_msg)}\n\n"

        # Send tools list - simplified (no inputSchema to reduce size)
        tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {
                "tools": [
                    {"name": "list_chapters", "description": "List all chapters"},
                    {"name": "get_chapter", "description": "Get chapter by ID"},
                    {"name": "search_content", "description": "Search content"},
                    {"name": "get_quiz", "description": "Get quiz"},
                    {"name": "submit_quiz", "description": "Submit quiz"},
                    {"name": "get_progress", "description": "Get progress"},
                    {"name": "update_progress", "description": "Update progress"},
                    {"name": "get_streak", "description": "Get streak"},
                    {"name": "check_access", "description": "Check access"}
                ]
            }
        }
        yield f"event: message\ndata: {json.dumps(tools_msg)}\n\n"

        # Keep alive
        while True:
            await asyncio.sleep(30)
            yield ": keep-alive\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Chunking": "no"
        }
    )
