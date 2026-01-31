from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response
import json
import asyncio

router = APIRouter(tags=["MCP", "SSE"])

@router.post("/sse")
async def mcp_post(request: Request):
    """Handle MCP JSON-RPC POST requests from ChatGPT."""
    try:
        data = await request.json()

        method = data.get("method")
        params = data.get("params", {})
        req_id = data.get("id")

        # Handle initialize
        if method == "initialize":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "Course Companion FTE",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                },
                "id": req_id
            })

        # Handle tools/list
        elif method == "tools/list":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
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
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)


@router.get("/sse")
async def mcp_sse():
    """MCP SSE endpoint for streaming (for backwards compatibility)."""
    async def event_stream():
        try:
            # Send server announcement
            announcement = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "server": "Course Companion FTE Backend",
                    "version": "1.0.0"
                }
            }

            data = json.dumps(announcement)
            yield f"event: message\ndata: {data}\n\n"

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
            data = json.dumps(error_msg)
            yield f"event: error\ndata: {data}\n\n"

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
