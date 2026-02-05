#!/bin/bash
# Add /mcp endpoint to HTTPS nginx configuration

# Backup current config
sudo cp /etc/nginx/sites-available/course-backend /etc/nginx/sites-available/course-backend.backup

# Update course-backend config to add /mcp endpoint
sudo tee /etc/nginx/sites-available/course-backend > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name 92.113.147.250;

    # Redirect all HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name 92.113.147.250;

    # Self-signed SSL certificates
    ssl_certificate /etc/ssl/certs/backend-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/backend-selfsigned.key;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # MCP endpoint for ChatGPT Apps SDK
    location /mcp {
        proxy_pass http://localhost:3505/api/v1/sse;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
    }

    # Legacy /sse endpoint (for backwards compatibility)
    location /sse {
        proxy_pass http://localhost:3505/api/v1/sse;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
    }

    # Widget files
    location /ui/widget/ {
        alias /usr/share/nginx/html/ui/widget/;
        add_header Cache-Control "no-cache, no-transform";
        add_header Access-Control-Allow-Origin "https://chatgpt.com";
        default_type text/html;
        try_files $uri =404;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:3505/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # CORS headers
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # API documentation
    location /docs {
        proxy_pass http://localhost:3505/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://localhost:3505/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:3505/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Root endpoint
    location / {
        proxy_pass http://localhost:3505/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOFNGINX

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
if [ $? -eq 0 ]; then
    sudo systemctl reload nginx
    echo "✅ nginx HTTPS configuration updated and reloaded successfully"
    echo ""
    echo "Testing /mcp endpoint over HTTPS..."
    sleep 2

    # Test the endpoint
    response=$(curl -sk -X POST https://92.113.147.250/mcp \
      -H "Content-Type: application/json" \
      -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}')

    if echo "$response" | grep -q "protocolVersion"; then
        echo "✅ /mcp endpoint over HTTPS is working!"
        echo ""
        echo "Response:"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo "❌ /mcp endpoint returned unexpected response:"
        echo "$response"
    fi
else
    echo "❌ nginx configuration test failed. Restoring backup..."
    sudo cp /etc/nginx/sites-available/course-backend.backup /etc/nginx/sites-available/course-backend
    exit 1
fi
