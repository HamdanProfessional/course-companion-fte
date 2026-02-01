#!/bin/bash
# Update nginx configuration for MCP Server
# Run this script on the server: ssh n00bi2761@92.113.147.250

cat > /tmp/sse-testservers-new.conf << 'EOF'
# MCP Server proxy for ChatGPT Apps
server {
    listen 80;
    server_name sse.testservers.online;

    # Serve React UI component
    location /ui/ {
        proxy_pass http://92.113.147.250:3505/ui/;
        add_header Cache-Control "no-cache";
    }

    # Serve UI component.js
    location /ui/dist/component.js {
        proxy_pass http://92.113.147.250:3505/ui/dist/component.js;
        add_header Content-Type "application/javascript";
    }

    # Proxy MCP server (FastMCP) - /sse endpoint
    location /sse {
        proxy_pass http://localhost:3506/sse;

        # SSE specific headers
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;

        # Timeouts for SSE
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # Root MCP endpoint
    location /mcp {
        proxy_pass http://localhost:3506/mcp;

        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "✅ Created new nginx configuration"
echo ""
echo "Now run these commands:"
echo ""
echo "  sudo cp /tmp/sse-testservers-new.conf /etc/nginx/sites-available/sse-testservers"
echo "  sudo nginx -t"
echo "  sudo systemctl reload nginx"
echo ""
echo "Then test with:"
echo "  curl -I https://sse.testservers.online/sse"
