# Connect from ChatGPT

**Source:** https://developers.openai.com/apps-sdk/deploy/connect-chatgpt
**Phase:** Deploy
**Last Updated:** February 2026

---

## Overview

Test your app in ChatGPT using Developer Mode.

**Note:** Public app publishing not available yet. Submissions accepted later this year.

---

## Prerequisites

### Supported Plans

ChatGPT Apps supported on:
- ✅ Plus, Pro, Go, Free plans
- ❌ Business, Enterprise, Education (coming later)

Developer mode available on all plans for testing.

---

## Enable Developer Mode

1. Navigate to **Settings → Apps & Connectors → Advanced settings**
2. Toggle **Developer mode** (if organization allows)

Once enabled, you'll see **Create** button under **Settings → Apps & Connectors**

---

## Create a Connector

### Step 1: Ensure Server Reachable

- MCP server accessible via HTTPS
- For local dev: Use ngrok or Cloudflare Tunnel

### Step 2: Add Connector

1. Navigate to **Settings → Connectors → Create**
2. Provide metadata:
   - **Connector name** - User-facing title (e.g., "Kanban board")
   - **Description** - What connector does, when to use it
   - **Connector URL** - Public `/mcp` endpoint (e.g., `https://abc123.ngrok.app/mcp`)
3. Click **Create**

### Success Indicators

- Connection succeeds → Tool list displayed
- Connection fails → Check with MCP Inspector or API Playground

---

## Try the App

### Step 1: Open New Chat

1. Open new ChatGPT conversation
2. Click **+** near message composer
3. Click **More**

### Step 2: Choose Connector

Select your app from available tools list

### Step 3: Test with Prompts

Example prompts:
- "What are my available tasks?"
- "Show my dashboard"
- "Create a new item"

### Behavior

- ChatGPT displays tool-call payloads
- Write tools require manual confirmation
- Can choose "remember approvals" for conversation

---

## Refresh Metadata

When tools or descriptions change:

1. Update MCP server and redeploy
2. In **Settings → Connectors**, click connector → **Refresh**
3. Verify tool list updates
4. Test updated flows

---

## Using Other Clients

### API Playground

1. Visit platform playground
2. **Tools → Add → MCP Server**
3. Paste HTTPS endpoint
4. Get raw request/response logs

### Mobile Clients

- Connector linked on web → Available on mobile
- Test mobile layouts early for custom controls

---

## Connection Issues

| Issue | Solution |
|-------|----------|
| Connection fails | Verify HTTPS endpoint, check with MCP Inspector |
| Tools not showing | Refresh connector metadata |
| Widget not rendering | Check `text/html+skybridge` MIME type |
| Auth errors | Verify OAuth configuration |

---

## Best Practices

1. **Use descriptive names** - Clear connector names help discovery
2. **Accurate descriptions** - Explain when to use your app
3. **Test thoroughly** - Try all tools before going live
4. **Monitor performance** - Track latency and errors

---

## Related Resources

- **Previous:** [Deploy Your App](./01-deploy-app.md)
- **Next:** [Test Your Integration](./03-testing-integration.md)
- **Submission:** [Submit Your App](./04-submit-app.md)
