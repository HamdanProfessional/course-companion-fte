# Deploy Your App

**Source:** https://developers.openai.com/apps-sdk/deploy
**Phase:** Deploy
**Last Updated:** February 2026

---

## Overview

Host your MCP server and component bundle behind a stable HTTPS endpoint.

---

## Deployment Options

### Managed Containers

**Platforms:** Fly.io, Render, Railway

**Benefits:**
- Quick spin-up
- Automatic TLS
- Simple scaling

### Cloud Serverless

**Platforms:** Google Cloud Run, Azure Container Apps

**Benefits:**
- Scale-to-zero
- Pay-per-use

**Caution:** Long cold starts can interrupt streaming HTTP

### Kubernetes

**Best for:** Teams with existing clusters

**Requirements:**
- Ingress controller supporting server-sent events
- Front pods with proper ingress

---

## Requirements

Regardless of platform, ensure:

| Requirement | Purpose |
|-------------|---------|
| `/mcp` stays responsive | Low latency for tool calls |
| Streaming responses | Support for SSE |
| Proper HTTP status codes | Error handling |
| HTTPS endpoint | Secure communication |

---

## Local Development

Use ngrok to expose local server:

```bash
ngrok http 2091
# https://<subdomain>.ngrok.app/mcp → http://127.0.0.1:2091/mcp
```

### Development Workflow

```
1. Change code
2. Rebuild component bundle (npm run build)
3. Restart MCP server
4. Refresh connector in ChatGPT settings
```

---

## Environment Configuration

### Secrets

- Store API keys outside repo
- Use platform secret managers
- Inject as environment variables

### Logging

Log:
- Tool-call IDs
- Request latency
- Error payloads

### Observability

Monitor:
- CPU usage
- Memory usage
- Request counts

---

## Dogfood and Rollout

### Before Broad Launch

1. **Gate access** - Keep in developer mode until stable
2. **Run golden prompts** - Test discovery prompts
3. **Capture artifacts** - Record screenshots of MCP Inspector and ChatGPT

### Production Readiness

- Update directory metadata
- Confirm auth configuration
- Verify storage setup
- Publish release notes

---

## Deployment Checklist

- [ ] MCP server accessible via HTTPS
- [ ] Component bundle built and embedded
- [ ] Environment variables configured
- [ ] Logging and monitoring set up
- [ ] Error handling tested
- [ ] Golden prompts validated
- [ ] Screenshots captured

---

## Related Resources

- **Next:** [Connect from ChatGPT](./02-connect-chatgpt.md)
- **Testing:** [Test Your Integration](./03-testing-integration.md)
- **Troubleshooting:** [Troubleshooting Guide](https://developers.openai.com/apps-sdk/guides/troubleshooting)
