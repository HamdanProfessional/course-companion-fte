#!/bin/bash
# Deploy MCP SSE Server to production

set -e

echo "=== Deploying MCP SSE Server ==="

# Configuration
SERVER="n00bi2761@92.113.147.250"
REMOTE_DIR="~/course-companion-mcp"
SSE_PORT="8080"

# Create remote directory first
echo "Creating remote directory..."
ssh -o StrictHostKeyChecking=no $SERVER "mkdir -p $REMOTE_DIR"

# Build and upload
echo "Packaging MCP server..."
cd chatgpt-app

# Create archive
tar -czf ../mcp-sse-server.tar.gz \
  mcp_server_sse.py \
  requirements-sse.txt

# Upload to server (to home directory first)
echo "Uploading to server..."
scp ../mcp-sse-server.tar.gz $SERVER:~/

# Install and start on server
echo "Installing on server..."
ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
# Move archive to target directory
mv ~/mcp-sse-server.tar.gz ~/course-companion-mcp/
cd ~/course-companion-mcp

# Extract
tar -xzf mcp-sse-server.tar.gz
rm mcp-sse-server.tar.gz

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -q -r requirements-sse.txt

# Kill existing MCP server on port 8080
lsof -ti:8080 | xargs -r kill -9 || true

# Start MCP SSE server
echo "Starting MCP SSE server on port 8080..."
nohup python3 mcp_server_sse.py > /tmp/mcp-sse.log 2>&1 &

sleep 3

# Check if running
if lsof -i:8080 > /dev/null; then
  echo "✅ MCP SSE server running on port 8080"
else
  echo "❌ Failed to start MCP SSE server"
  tail -20 /tmp/mcp-sse.log
fi

ENDSSH

# Cleanup
cd ..
rm ../mcp-sse-server.tar.gz

echo ""
echo "=== Deployment Complete ==="
echo "MCP SSE Endpoint: http://92.113.147.250:8080/mcp"
echo ""
echo "Add to ChatGPT Desktop Config:"
echo '{"mcpServers": {"course-companion-fte": {"transport": "sse", "url": "http://92.113.147.250:8080/mcp"}}}'
echo ""
