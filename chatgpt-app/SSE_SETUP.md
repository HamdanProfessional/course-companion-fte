# Course Companion FTE - MCP SSE Server

Server-Sent Events (SSE) transport for the MCP server, allowing remote connections from ChatGPT Desktop.

## Quick Start

### 1. Deploy the Server

```bash
# From project root
bash scripts/deploy-mcp-sse.sh
```

### 2. Configure ChatGPT Desktop

Add to your ChatGPT Desktop MCP config (`config.json`):

```json
{
  "mcpServers": {
    "course-companion-fte": {
      "transport": "sse",
      "url": "http://92.113.147.250:8080/mcp"
    }
  }
}
```

Or for testservers.online:

```json
{
  "mcpServers": {
    "course-companion-fte": {
      "transport": "sse",
      "url": "https://sse.testservers.online/mcp"
    }
  }
}
```

### 3. Restart ChatGPT Desktop

Then restart ChatGPT Desktop to load the new MCP server.

### 4. Test the Connection

In ChatGPT, type:
```
@course-companion-fte List all available quizzes
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/mcp` | SSE endpoint for MCP connections |
| `/health` | Health check |
| `/` | Server info |

## Widget Support

When you use `get_quiz`, ChatGPT will load the React quiz widget from:
- Widget URL: `http://92.113.147.250:3505/ui`
- Domain: `92.113.147.250`

## Troubleshooting

**Widget not showing?**
1. Check the widget is accessible: `curl http://92.113.147.250:3505/ui`
2. Check MCP server health: `curl http://92.113.147.250:8080/health`
3. Check ChatGPT Desktop logs for errors

**Connection refused?**
- Ensure port 8080 is open on the server
- Check firewall rules

**SSE connection drops?**
- Check nginx/proxy settings (disable buffering for `/mcp`)
- Ensure `X-Accel-Buffering: no` header is set
