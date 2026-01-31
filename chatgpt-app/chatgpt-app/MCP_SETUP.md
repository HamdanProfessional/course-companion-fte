# MCP Server Configuration for Course Companion FTE Backend

## What is MCP?

**MCP (Model Context Protocol)** is an open standard that lets AI applications (like ChatGPT Apps) connect to external data sources and tools in a standardized way.

For ChatGPT Apps, your backend needs to expose an **MCP server** that supports **Server-Sent Events (SSE)** for streaming responses.

## MCP Server Requirements

### 1. SSE Endpoint
Your backend needs an SSE endpoint that ChatGPT Apps can connect to:
- **Path**: Typically `/api/v1/sse` or `/sse`
- **Protocol**: Server-Sent Events (text/event-stream)
- **Purpose**: Stream responses back to ChatGPT

### 2. Tool Exposure
MCP server exposes tools (API endpoints) that ChatGPT Apps can call:
- Content tools (chapters, search)
- Quiz tools (get quiz, submit answers)
- Progress tools (get progress, update progress)

### 3. Capabilities
Your MCP server needs to declare what it can do:
```json
{
  "tools": [
    {
      "name": "get_chapters",
      "description": "Get all chapters",
      "inputSchema": {...}
    }
  ],
  "resources": [...]
}
```

## Configuration for Your Backend

Since your backend is at `https://sse.testservers.online`, you need to add:

### Option A: Add MCP Server to Backend (Recommended)

Add SSE endpoint to your FastAPI backend:

```python
from fastapi import Response
import json
import asyncio

@router.get("/sse")
async def sse_endpoint():
    """MCP Server-Sent Events endpoint for ChatGPT Apps"""

    async def event_stream():
        # Send MCP server announcement
        yield "event: mcp-server\ndata: " + json.dumps({
            "name": "Course Companion FTE Backend",
            "version": "1.0.0",
            "capabilities": {
                "tools": ["get_chapters", "get_quiz", "submit_quiz", "get_progress", "update_progress"],
                "resources": ["chapters", "quizzes", "progress"]
            }
        }) + "\n\n"

        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield ": keep-alive\n\n"

    return Response(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Chunking": "no"
        }
    )
```

### Option B: Use MCP Adapter (Quick Fix)

If you can't modify the backend, use an MCP adapter server that:
1. Receives requests from ChatGPT App
2. Translates them to your backend API calls
3. Streams responses via SSE

## ChatGPT App Configuration

In your ChatGPT App manifest:

```json
{
  "name": "Course Companion FTE",
  "mcp_servers": [
    {
      "url": "https://sse.testservers.online/api/v1/sse",
      "description": "Course Companion FTE Backend MCP Server"
    }
  ],
  "actions": [...]
}
```

## Why SSE is Required

1. **Streaming Responses**: ChatGPT Apps need to stream responses in real-time
2. **Long Operations**: Quizzes, content fetching may take time
3. **Keep-Alive**: Maintain connection between requests
4. **Bidirectional**: Support two-way communication

## Next Steps

You need to **add SSE support to your backend** at `http://92.113.147.250:8180`:

1. Add `/api/v1/sse` endpoint to backend
2. Return Server-Sent Events with tool declarations
3. Handle SSE connections properly
4. Test SSE endpoint: `curl -N https://sse.testservers.online/api/v1/sse`

Would you like me to create the full SSE endpoint code for your FastAPI backend?
