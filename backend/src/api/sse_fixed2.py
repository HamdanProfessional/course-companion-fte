"""
MCP Server-Sent Events (SSE) Endpoint for ChatGPT Apps
Add this to your FastAPI backend to support ChatGPT Apps with MCP.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["MCP", "SSE"])

# MCP Server Configuration
MCP_SERVER_CONFIG = {
    "name": "Course Companion FTE Backend",
    "version": "1.0.0",
    "description": "Zero-Backend-LLM API for Course Companion FTE",
    "capabilities": {
        "tools": [
            {
                "name": "list_chapters",
                "description": "List all available chapters",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_chapter",
                "description": "Get detailed chapter content by ID",
                "inputSchema": {"type": "object", "properties": {"chapter_id": {"type": "string"}}, "required": ["chapter_id"]}
            },
            {
                "name": "search_content",
                "description": "Search course content",
                "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
            },
            {
                "name": "get_quiz",
                "description": "Get quiz with questions",
                "inputSchema": {"type": "object", "properties": {"quiz_id": {"type": "string"}}, "required": ["quiz_id"]}
            },
            {
                "name": "submit_quiz",
                "description": "Submit quiz answers for grading",
                "inputSchema": {"type": "object", "properties": {"quiz_id": {"type": "string"}, "answers": {"type": "object"}}, "required": ["quiz_id", "answers"]}
            },
            {
                "name": "get_progress",
                "description": "Get user learning progress",
                "inputSchema": {"type": "object", "properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}
            },
            {
                "name": "update_progress",
                "description": "Mark chapter as complete",
                "inputSchema": {"type": "object", "properties": {"user_id": {"type": "string"}, "chapter_id": {"type": "string"}}, "required": ["user_id", "chapter_id"]}
            },
            {
                "name": "get_streak",
                "description": "Get user streak information",
                "inputSchema": {"type": "object", "properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}
            },
            {
                "name": "check_access",
                "description": "Check content access (freemium)",
                "inputSchema": {"type": "object", "properties": {"user_id": {"type": "string"}, "resource": {"type": "string"}}, "required": ["user_id", "resource"]}
            }
        ],
        "resources": [
            {"uri": "chapters", "name": "Course Chapters", "description": "All course chapters", "mime_type": "application/json"},
            {"uri": "quizzes", "name": "Quizzes", "description": "All quizzes", "mime_type": "application/json"},
            {"uri": "progress", "name": "User Progress", "description": "Learning progress data", "mime_type": "application/json"}
        ]
    }
}


async def event_stream():
    """Stream SSE events to ChatGPT App."""
    try:
        # Send MCP server announcement
        announcement = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {
                "server": MCP_SERVER_CONFIG["name"],
                "version": MCP_SERVER_CONFIG["version"],
                "capabilities": MCP_SERVER_CONFIG["capabilities"]
            }
        }

        # Send announcement event
        data = json.dumps(announcement)
        yield f"event: message\ndata: {data}\n\n"

        # Send tools list
        tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {
                "tools": MCP_SERVER_CONFIG["capabilities"]["tools"]
            }
        }

        data = json.dumps(tools_msg)
        yield f"event: message\ndata: {data}\n\n"

        # Send resources list
        resources_msg = {
            "jsonrpc": "2.0",
            "method": "resources/list",
            "params": {
                "resources": MCP_SERVER_CONFIG["capabilities"]["resources"]
            }
        }

        data = json.dumps(resources_msg)
        yield f"event: message\ndata: {data}\n\n"

        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield ": keep-alive\n\n"

    except asyncio.CancelledError:
        logger.info("SSE connection closed by client")
    except Exception as e:
        logger.error(f"SSE error: {str(e)}")
        # Send error
        error_msg = {
            "jsonrpc": "2.0",
            "method": "error",
            "params": {"code": -1, "message": str(e)}
        }
        data = json.dumps(error_msg)
        yield f"event: error\ndata: {data}\n\n"


@router.get("/sse")
async def mcp_sse_endpoint():
    """MCP Server-Sent Events endpoint for ChatGPT Apps."""
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


@router.get("/mcp/manifest")
async def mcp_manifest():
    """Returns MCP server configuration as JSON."""
    return {
        "name": MCP_SERVER_CONFIG["name"],
        "version": MCP_SERVER_CONFIG["version"],
        "description": MCP_SERVER_CONFIG["description"],
        "server_url": "http://sse.testservers.online/api/v1/sse",
        "capabilities": MCP_SERVER_CONFIG["capabilities"]
    }


@router.get("/health-sse")
async def sse_health_check():
    """Health check for SSE endpoint."""
    return {
        "status": "healthy",
        "sse_endpoint": "/api/v1/sse",
        "backend_url": "http://sse.testservers.online",
        "mcp_server": "active"
    }
