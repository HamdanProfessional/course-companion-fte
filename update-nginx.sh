#!/bin/bash
# Update nginx to add /mcp endpoint for ChatGPT Apps SDK

# Backup current config
sudo cp /etc/nginx/sites-available/sse-testservers /etc/nginx/sites-available/sse-testservers.backup

# Update nginx configuration
sudo tee /etc/nginx/sites-available/sse-testservers > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name sse.testservers.online;
    root /usr/share/nginx/html;

    # Root endpoint
    location = / {
        return 200 '{"status":"Course Companion FTE MCP Server","version":"1.0.0","endpoints":{"/mcp":"MCP JSON-RPC endpoint","/ui/widget/":"Widget files"}}';
        add_header Content-Type application/json;
    }

    # MCP endpoint for ChatGPT Apps SDK
    location /mcp {
        proxy_pass http://localhost:3505/api/v1/sse;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;

        # MCP requires these headers
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Legacy /sse endpoint (for backwards compatibility)
    location /sse {
        proxy_pass http://localhost:3505/api/v1/sse;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
    }

    # Widget HTML files
    location ~ ^/ui/widget/([^/]+\.html)$ {
        try_files /ui/widget/$1 /ui/widget/chapter-list.html;
        add_header Cache-Control "no-cache, no-transform";
        add_header Access-Control-Allow-Origin "https://chatgpt.com";
        default_type text/html;
    }

    # Health check endpoint
    location /health {
        return 200 '{"status":"healthy"}';
        add_header Content-Type application/json;
    }
}
EOFNGINX

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
if [ $? -eq 0 ]; then
    sudo systemctl reload nginx
    echo "✅ nginx configuration updated and reloaded successfully"
    echo ""
    echo "Testing /mcp endpoint..."
    sleep 2

    # Test the endpoint
    response=$(curl -s -X POST http://localhost/mcp \
      -H "Content-Type: application/json" \
      -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}')

    if echo "$response" | grep -q "protocolVersion"; then
        echo "✅ /mcp endpoint is working!"
        echo ""
        echo "Test with HTTPS:"
        echo "curl -X POST https://sse.testservers.online/mcp \\"
        echo "  -H 'Content-Type: application/json' \\"
        echo "  -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{}}'"
    else
        echo "❌ /mcp endpoint returned unexpected response:"
        echo "$response"
    fi
else
    echo "❌ nginx configuration test failed. Restoring backup..."
    sudo cp /etc/nginx/sites-available/sse-testservers.backup /etc/nginx/sites-available/sse-testservers
    exit 1
fi
