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
  requirements-sse.txt \
  nginx-mcp-sse.conf \
  HTTPS_SETUP.md

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

# Kill existing MCP server on port 8080
echo "Killing any process on port 8080..."
lsof -ti:8080 | xargs -r kill -9 || true
sleep 1

# Install dependencies with --break-system-packages flag
echo "Installing Python dependencies..."
pip3 install -q --break-system-packages -r requirements-sse.txt

# Start MCP SSE server
echo "Starting MCP SSE server on port 8080..."
nohup python3 mcp_server_sse.py > /tmp/mcp-sse.log 2>&1 &

sleep 4

# Check if running
if lsof -i:8080 > /dev/null; then
  echo "✅ MCP SSE server running on port 8080"
  echo ""
  echo "=== Server Info ==="
  curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || echo "Health check not responding yet"
else
  echo "❌ Failed to start MCP SSE server"
  echo "=== Log Output ==="
  tail -30 /tmp/mcp-sse.log
fi

ENDSSH

# Cleanup
cd ..
rm ../mcp-sse-server.tar.gz 2>/dev/null || true

echo ""
echo "=== Deployment Complete ==="
echo "MCP SSE Endpoint: http://92.113.147.250:8080/mcp"
echo ""
echo "For HTTPS, see: chatgpt-app/HTTPS_SETUP.md"
echo ""
