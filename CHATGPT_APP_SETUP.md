# ChatGPT App with UI Widget - Setup Guide

## Overview

This setup provides a ChatGPT App with an interactive React quiz widget that renders inside ChatGPT.

**Sources:**
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui/)
- [Build your MCP server](https://developers.openai.com/apps-sdk/build/mcp-server/)

## Architecture

```
┌─────────────────┐
│  ChatGPT App    │ (Browser or Desktop)
│  (Developer Mode)│
└────────┬────────┘
         │ HTTPS (via tunnel)
         ↓
┌─────────────────┐
│  MCP Server     │ (Port 3506)
│  - Tools        │
│  - UI Templates │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│  Backend API    │ (Port 3505)
│  - Quiz Data    │
└─────────────────┘
```

## What's Deployed

✅ **Backend API**: http://92.113.147.250:3505
- 4 chapters with content
- 4 quizzes with 6 questions each
- Search, progress tracking

✅ **React UI Component**: http://92.113.147.250:3505/ui
- Interactive quiz interface
- Built with esbuild
- Uses `window.openai` API

✅ **MCP Server**: Ready to run on port 3506
- Registers UI template as resource
- Defines tools with proper metadata
- Returns structuredContent, content, and _meta

## How to Run the MCP Server

### Option 1: Run in Docker (Recommended)

```bash
# SSH to server
ssh n00bi2761@92.113.147.250

# Expose port 3506 for MCP server
docker stop course-backend
docker run -d \
  --name course-backend \
  -p 3505:3505 \
  -p 3506:3506 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e BACKEND_URL="http://localhost:3505" \
  -e WIDGET_URL="http://92.113.147.250:3505/ui" \
  backend-backend

# Start MCP server
docker exec -d course-backend python3 -m uvicorn mcp_server_app:app --host 0.0.0.0 --port 3506
```

### Option 2: Run on Host

```bash
# SSH to server
ssh n00bi2761@92.113.147.250

cd ~/course-companion/backend

# Install dependencies (with --break-system-packages flag for system Python)
pip3 install --break-system-packages --user fastmcp httpx

# Run MCP server
BACKEND_URL=http://92.113.147.250:3505 \
WIDGET_URL=http://92.113.147.250:3505/ui \
python3 mcp_server_app.py
```

## Set Up HTTPS Tunnel (Required for ChatGPT Apps)

ChatGPT Apps require HTTPS. Use cloudflared:

```bash
# SSH to server
ssh n00bi2761@92.113.147.250

# Install cloudflared (if not installed)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Start tunnel (maps https://domain to http://localhost:3506)
cloudflared tunnel --url http://localhost:3506

# You'll get a URL like: https://abc-123.trycloudflare.com
```

The tunnel URL is your MCP server URL for ChatGPT Apps.

## Connect in ChatGPT Developer Mode

1. Open ChatGPT (chatgpt.com) with **Developer Mode** enabled
2. Go to Apps → Create New App
3. Add MCP Server with URL: `https://your-trycloudflare-url.com/mcp/sse`
4. The app will:
   - Connect to your MCP server
   - Load tools: `list_quizzes`, `get_quiz`, `search_content`
   - Render the UI widget when you call `get_quiz`

## Test the App

In ChatGPT Developer Mode, try:

```
List all quizzes
```

```
Get the quiz "Introduction to AI Agents - Quiz"
```

The second command should render the interactive quiz widget!

## Troubleshooting

**Widget doesn't render:**
- Ensure MCP server is running: `curl http://localhost:3506/`
- Check HTTPS tunnel is active
- Verify tool metadata includes `openai/outputTemplate`

**Can't connect to MCP server:**
- Check firewall allows port 3506
- Verify cloudflared tunnel is running
- Test the tunnel URL in browser

**Questions return empty:**
- Check Backend API is accessible: `curl http://92.113.147.250:3505/api/v1/quizzes`
- Verify MCP server can reach backend
- Check MCP server logs

## Current Status

- ✅ Backend API deployed and working
- ✅ React UI component built and hosted
- ✅ MCP server code ready
- ⚠️ Need to run MCP server + HTTPS tunnel
- ⚠️ Need to connect in ChatGPT Developer Mode

**Next Steps:**
1. Run MCP server on port 3506
2. Set up HTTPS tunnel with cloudflared
3. Connect in ChatGPT Developer Mode
4. Test the quiz widget!

## Resources

- OpenAI Apps SDK Docs: https://developers.openai.com/apps-sdk/
- MCP Protocol: https://modelcontextprotocol.io/
- FastMCP GitHub: https://github.com/jlowin/fastmcp
