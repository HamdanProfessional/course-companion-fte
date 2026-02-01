#!/bin/bash
# Start MCP Server for Course Companion FTE

echo "Starting MCP Server..."

cd /home/n00bi2761/course-companion/backend

# Add local bin to PATH for fastmcp
export PATH="/home/n00bi2761/.local/bin:$PATH"

# Kill any existing MCP server on port 3506
pkill -f "mcp_server_app.py" 2>/dev/null
lsof -ti :3506 | xargs kill -9 2>/dev/null

# Set environment variables
export BACKEND_URL="http://92.113.147.250:3505"
export WIDGET_URL="http://sse.testservers.online/ui"

# Start MCP server in background
nohup python3 mcp_server_app.py > mcp_server.log 2>&1 &

# Get PID
MCP_PID=$!
echo $MCP_PID > mcp_server.pid

echo "MCP Server started with PID: $MCP_PID"
echo "Logs: tail -f mcp_server.log"
echo ""
echo "Test with:"
echo "  curl http://localhost:3506/sse"
echo "  curl https://sse.testservers.online/mcp/sse"
