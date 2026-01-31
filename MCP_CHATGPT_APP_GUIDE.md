# How to Build a Proper MCP/SSE Server for ChatGPT Apps

> A complete guide based on real-world debugging and testing with ChatGPT's MCP integration.

---

## What You Need to Know

**MCP (Model Context Protocol)** is an open standard that allows ChatGPT Apps to connect to external data sources and tools.

**SSE (Server-Sent Events)** is the required transport layer for MCP servers.

### Critical: The MCP Specification Matters

ChatGPT **strictly validates** MCP responses. If your response format is wrong by even one field, you'll get a `424 Failed Dependency` error with Pydantic validation errors.

---

## The Correct MCP Response Formats

### 1. Initialize Response (MOST IMPORTANT)

When ChatGPT sends:
```json
{"jsonrpc": "2.0", "method": "initialize", "id": 1}
```

You **MUST** respond with:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "Your Server Name",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {}
    }
  },
  "id": 1
}
```

**Critical Fields:**
- ✅ `protocolVersion` (required) - Use "2024-11-05"
- ✅ `serverInfo` (required) - NOT `server`
- ✅ `capabilities.tools` (required) - Must be `{}` empty dict, NOT `[]`

**Common Mistakes:**
- ❌ Using `"server"` instead of `"serverInfo"`
- ❌ Using `"tools": []` instead of `"tools": {}`
- ❌ Missing `"protocolVersion"`

### 2. Tools List Response

When ChatGPT sends:
```json
{"jsonrpc": "2.0", "method": "tools/list", "id": 2}
```

Respond with:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "your_tool_name",
        "description": "What the tool does",
        "inputSchema": {
          "type": "object",
          "properties": {
            "param_name": {
              "type": "string",
              "description": "Parameter description"
            }
          },
          "required": ["param_name"]
        }
      }
    ]
  },
  "id": 2
}
```

**Critical Fields:**
- ✅ `inputSchema` (required) - JSON Schema format
- ✅ `properties` - Define parameters
- ✅ `required` - Array of required parameter names

---

## Complete Working Example (FastAPI)

### File: `mcp_server.py`

```python
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response
import json
import asyncio

router = APIRouter(tags=["MCP", "SSE"])

@router.post("/sse")  # POST for JSON-RPC requests from ChatGPT
async def mcp_post(request: Request):
    """Handle MCP JSON-RPC POST requests from ChatGPT."""
    try:
        data = await request.json()

        method = data.get("method")
        params = data.get("params", {})
        req_id = data.get("id")

        # Handle initialize - CRITICAL: Must match MCP spec
        if method == "initialize":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",  # REQUIRED
                    "serverInfo": {                    # REQUIRED (not "server")
                        "name": "Your App Name",
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
                            "name": "get_weather",
                            "description": "Get current weather for a location",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "City name or zip code"
                                    }
                                },
                                "required": ["location"]
                            }
                        },
                        {
                            "name": "calculate",
                            "description": "Perform a calculation",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "expression": {
                                        "type": "string",
                                        "description": "Math expression (e.g., '2 + 2')"
                                    }
                                },
                                "required": ["expression"]
                            }
                        }
                    ]
                },
                "id": req_id
            })

        # Handle tools/call - When ChatGPT actually uses your tools
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # Call your actual tool logic here
            if tool_name == "get_weather":
                result = get_weather(arguments.get("location"))
            elif tool_name == "calculate":
                result = calculate(arguments.get("expression"))
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
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)


@router.get("/sse")  # GET for SSE streaming (optional but recommended)
async def mcp_sse():
    """MCP SSE endpoint for streaming (backwards compatibility)."""
    async def event_stream():
        try:
            # Send server announcement
            announcement = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "server": "Your Server Name",
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


# Your actual tool implementations
def get_weather(location: str) -> dict:
    """Example tool: Get weather."""
    # Call your weather API here
    return {
        "location": location,
        "temperature": "72°F",
        "condition": "Sunny"
    }

def calculate(expression: str) -> dict:
    """Example tool: Calculate math expression."""
    try:
        result = eval(expression)
        return {
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e)
        }
```

### File: `main.py`

```python
from fastapi import FastAPI
from mcp_server import router as mcp_router

app = FastAPI(title="Your App")

# Include MCP router with /api/v1 prefix
app.include_router(mcp_router, prefix="/api/v1", tags=["MCP"])

@app.get("/")
async def root():
    return {"status": "healthy", "mcp_endpoint": "/api/v1/sse"}
```

---

## Testing Your MCP Server

Before connecting to ChatGPT, test with curl:

### Test Initialize:
```bash
curl -X POST https://your-server.com/api/v1/sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1}'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {"name": "...", "version": "..."},
    "capabilities": {"tools": {}}
  },
  "id": 1
}
```

### Test Tools List:
```bash
curl -X POST https://your-server.com/api/v1/sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "your_tool",
        "description": "...",
        "inputSchema": {...}
      }
    ]
  },
  "id": 2
}
```

---

## Creating the ChatGPT App

1. Go to ChatGPT → Create **"NEW APP (BETA)"**

2. Fill in the form:
   - **Name**: Your app name
   - **Description**: What your app does
   - **MCP server url**: `https://your-server.com/api/v1/sse`
   - **Authentication**: No Auth (or configure as needed)

3. Add instructions telling ChatGPT how to use your tools.

4. Save and test!

---

## Common Errors and Fixes

### Error 1: "Field required"
```
3 validation errors for InitializeResult
protocolVersion Field required
serverInfo Field required
capabilities.tools Input should be a valid dictionary
```

**Fix**: Check your `initialize` response matches the exact format above.

### Error 2: "code 424"
```
Failed Dependency - Pydantic validation error
```

**Fix**: Your JSON structure doesn't match MCP spec. Check field names carefully.

### Error 3: "405 Method Not Allowed"
```
POST /api/v1/sse HTTP/1.1" 405
```

**Fix**: Your endpoint only accepts GET. ChatGPT sends POST requests. Add `@router.post("/sse")`.

### Error 4: Cloudflare Blocking
```
401 Unauthorized - Access token is missing
```

**Fix**: If using Cloudflare, disable "Bot Fight Mode" for your domain.

### Error 5: Nginx Timeout
```
504 Gateway Timeout
```

**Fix**: Add to nginx config:
```nginx
proxy_read_timeout 86400s;
proxy_send_timeout 86400s;
```

---

## Nginx Configuration (for reverse proxy)

```nginx
server {
    listen 80;
    server_name mcp.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;

        # SSE specific headers
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;

        # Timeouts
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## Key Takeaways

1. **Response format is critical** - ChatGPT validates with Pydantic
2. **Use correct field names** - `serverInfo` not `server`, `protocolVersion` required
3. **capabilities.tools must be `{}`** - Empty dict, not array
4. **inputSchema is required** - Every tool needs JSON Schema
5. **Handle both POST and GET** - ChatGPT sends POST, SSE uses GET
6. **Test with curl first** - Verify your responses before connecting ChatGPT

---

## Quick Checklist

Before deploying to ChatGPT, verify:

- [ ] `initialize` returns `protocolVersion`, `serverInfo`, `capabilities.tools: {}`
- [ ] `tools/list` returns tools with `inputSchema`
- [ ] POST handler exists at your endpoint
- [ ] GET handler exists (for SSE compatibility)
- [ ] Tested with curl successfully
- [ ] Nginx/proxy configured for long connections
- [ ] HTTPS enabled (ChatGPT requires HTTPS for MCP URLs)

---

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChatGPT Apps Documentation](https://platform.openai.com/docs/apps)

---

**Made with ❤️ after hours of debugging MCP validation errors**

If this guide helped you build your MCP server, share it with others!
