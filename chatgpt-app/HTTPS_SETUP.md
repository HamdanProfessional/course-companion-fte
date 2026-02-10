# MCP SSE Server - HTTPS Setup Guide

## Problem
ChatGPT Desktop requires HTTPS for SSE connections. HTTP is not supported.

## Solution Options

### Option 1: Use existing SSL certificate (Recommended)

If you have SSL for a subdomain like `sse.testservers.online`:

1. **On your server, create SSL certificate:**
```bash
sudo certbot certonly --nginx -d sse.testservers.online
```

2. **Create nginx config** at `/etc/nginx/sites-available/mcp-sse`:
```nginx
server {
    listen 443 ssl http2;
    server_name sse.testservers.online;

    ssl_certificate /etc/letsencrypt/live/sse.testservers.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sse.testservers.online/privkey.pem;

    # SSE endpoint (no buffering!)
    location /mcp {
        proxy_pass http://localhost:8080;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header X-Accel-Buffering no;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
    }

    # Health endpoint
    location /health {
        proxy_pass http://localhost:8080;
    }

    # Messages endpoint
    location /messages {
        proxy_pass http://localhost:8080;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name sse.testservers.online;
    return 301 https://$server_name$request_uri;
}
```

3. **Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/mcp-sse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

4. **Deploy MCP server:**
```bash
cd ~/Hackathon_4
bash scripts/deploy-mcp-sse.sh
```

5. **ChatGPT Desktop Config:**
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

### Option 2: Use ngrok (Quick Test)

For testing without SSL setup:

```bash
# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Run ngrok tunnel to port 8080
ngrok http 8080
```

Then use the ngrok HTTPS URL in ChatGPT Desktop config.

### Option 3: Self-signed certificate (Not recommended)

ChatGPT Desktop may not accept self-signed certs. Use Option 1 or 2.

## Verification

Test the SSE endpoint:
```bash
curl https://sse.testservers.online/health
```

Should return:
```json
{
  "status": "healthy",
  "server": "course-companion-fte",
  "transport": "SSE"
}
```

## Troubleshooting

**Certificate issues:**
```bash
sudo certbot renew --force-renewal
```

**Nginx errors:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

**Port 8080 in use:**
```bash
lsof -ti:8080 | xargs kill -9
```
