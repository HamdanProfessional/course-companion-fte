# How to Add MCP/SSE Support to Your Backend

## Step 1: Add SSE Endpoint to Backend

### 1.1 Copy the SSE file

Copy the SSE endpoint file to your backend:
```bash
cp backend/src/api/sse.py backend/src/api/
```

### 1.2 Update backend/src/api/main.py

Add the SSE router to your main FastAPI app:

```python
from fastapi import FastAPI
from src.api.sse import router as sse_router

app = FastAPI()

# Include the SSE router
app.include_router(sse_router, prefix="/api/v1")
```

### 1.3 Update backend/requirements.txt

Add any dependencies if needed:
```
# Already included in FastAPI, no additional dependencies needed
```

### 1.4 Restart Backend

```bash
# SSH into your server
ssh -o n00bi2761@92.113.147.250

# Navigate to app
cd /path/to/your/backend

# Restart the service
sudo systemctl restart course-companion-backend
# or
pkill -f uvicorn && uvicorn src.api.main:app --host 0.0.0.0 --port 8180
```

## Step 2: Verify SSE Endpoint

### Test SSE endpoint
```bash
curl -N https://sse.testservers.online/api/v1/sse
```

You should see Server-Sent Events streaming:
```
event: message
data: {"jsonrpc":"2.0","method":"notifications/initialized",...}

event: message
data: {"jsonrpc":"2.0","method":"tools/list",...}

: keep-alive
```

### Test health check
```bash
curl https://sse.testservers.online/api/v1/health-sse
```

Should return:
```json
{
  "status": "healthy",
  "sse_endpoint": "/api/v1/sse",
  "backend_url": "http://92.113.147.250:8180"
}
```

## Step 3: Configure ChatGPT App

### 3.1 Go to ChatGPT

1. Open https://chat.openai.com
2. Click "Explore GPTs" or look for "Create ChatGPT App"

### 3.2 Create New App

1. Click "Create" or "Create ChatGPT App"
2. **Name**: `Course Companion FTE`
3. **Description**: Your AI-powered tutor for mastering AI Agent Development

### 3.3 Add MCP Server

In the ChatGPT App configuration, add MCP server:
- **Server URL**: `https://sse.testservers.online/api/v1/sse`
- **Type**: MCP Server (Model Context Protocol)

### 3.4 Configure Actions

The MCP server will automatically expose tools. You may also need to add:
- HTTP endpoints that ChatGPT can call directly
- OpenAPI schema for additional tools

### 3.5 Add Instructions

Copy content from `chatgpt-app/chatgpt-app/instructions.md` into the instructions field.

### 3.6 Save & Test

Click "Save" and test your ChatGPT App with:
- "Explain what MCP is"
- "Quiz me"
- "How am I doing?"

## Troubleshooting

### SSE endpoint returns 404
**Problem**: `/api/v1/sse` not found
**Solution**:
- Verify `sse.py` was copied to backend/src/api/
- Verify router is included in main.py
- Restart backend service

### SSE connection drops
**Problem**: Connection closes immediately
**Solution**:
- Check firewall allows HTTP connections
- Verify CORS settings (if needed)
- Check backend logs for errors

### ChatGPT App can't connect
**Problem**: Connection timeout or refused
**Solution**:
- Verify backend is running: `curl https://sse.testservers.online/api/v1/health-sse`
- Check SSE endpoint: `curl -N https://sse.testservers.online/api/v1/sse`
- Verify port 8180 is accessible from internet

### Tools not appearing in ChatGPT
**Problem**: Tools don't show up in ChatGPT App
**Solution**:
- Check SSE endpoint returns tools/list event
- Verify tool schemas are correct
- Check ChatGPT App logs for errors

## Verification Commands

```bash
# Test SSE endpoint (should stream events)
curl -N https://sse.testservers.online/api/v1/sse | head -20

# Test health check
curl https://sse.testservers.online/api/v1/health-sse

# Test backend API still works
curl http://92.113.147.250:8180/api/v1/chapters
```

## Success Criteria

✅ SSE endpoint streams events to ChatGPT App
✅ Tools are properly declared in MCP server config
✅ ChatGPT App can connect to MCP server
✅ Tools are callable from ChatGPT App
✅ Backend API still works for direct HTTP calls

---

## Summary

Your backend at `http://92.113.147.250:8180` needs:

1. ✅ SSE endpoint at `/api/v1/sse` - Done (sse.py created)
2. ✅ MCP server configuration - Done (in sse.py)
3. ⏳ Add router to main.py - Instructions above
4. ⏳ Restart backend service - Instructions above
5. ⏳ Configure ChatGPT App - Instructions above

The SSE endpoint is critical for ChatGPT Apps to work properly!
