# Build Your MCP Server

**Source:** https://developers.openai.com/apps-sdk/build/mcp-server
**Phase:** Build
**Last Updated:** February 2026

---

## Overview

ChatGPT Apps have three components:

1. **MCP Server** - Defines tools, enforces auth, returns data, points to UI bundle
2. **Widget/UI Bundle** - Renders in iframe, uses `window.openai` API
3. **Model** - Decides when to call tools, narrates the experience

### Architecture Flow

```
User prompt
   ↓
ChatGPT model ──► MCP tool call ──► Your server ──► Tool response
   │                                                   │
   └───── renders narration ◄──── widget iframe ◄──────┘
                              (HTML template + window.openai)
```

---

## Prerequisites

- Comfortable with TypeScript or Python
- Web bundler (Vite, esbuild, etc.)
- MCP server reachable over HTTP
- Built UI bundle

### Example Project Layout

```
your-chatgpt-app/
├─ server/
│  └─ src/index.ts          # MCP server + tool handlers
├─ web/
│  ├─ src/component.tsx     # React widget
│  └─ dist/app.{js,css}     # Bundled assets
└─ package.json
```

---

## Implementation Details

### Step 1: Register Component Template

Each UI bundle is exposed as an MCP resource with `mimeType: "text/html+skybridge"`.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { readFileSync } from "node:fs";

const server = new McpServer({ name: "kanban-server", version: "1.0.0" });
const HTML = readFileSync("web/dist/kanban.js", "utf8");
const CSS = readFileSync("web/dist/kanban.css", "utf8");

server.registerResource(
  "kanban-widget",
  "ui://widget/kanban-board.html",
  {},
  async () => ({
    contents: [
      {
        uri: "ui://widget/kanban-board.html",
        mimeType: "text/html+skybridge",
        text: `
<div id="kanban-root"></div>
<style>${CSS}</style>
<script type="module">${HTML}</script>
        `.trim(),
        _meta: {
          "openai/widgetPrefersBorder": true,
          "openai/widgetDomain": "https://myapp.example.com",
          "openai/widgetCSP": {
            connect_domains: ["https://api.myapp.example.com"],
            resource_domains: ["https://*.oaistatic.com"],
            frame_domains: ["https://*.example-embed.com"],
          },
        },
      },
    ],
  })
);
```

**Best Practice:** Version template URIs when updating bundles (e.g., `kanban-board-v2.html`).

---

### Step 2: Describe Tools

```typescript
import { z } from "zod";

server.registerTool(
  "kanban-board",
  {
    title: "Show Kanban Board",
    inputSchema: { workspace: z.string() },
    _meta: {
      "openai/outputTemplate": "ui://widget/kanban-board.html",
      "openai/toolInvocation/invoking": "Preparing the board…",
      "openai/toolInvocation/invoked": "Board ready.",
    },
  },
  async ({ workspace }) => {
    const board = await loadBoard(workspace);
    return {
      structuredContent: board.summary,
      content: [{ type: "text", text: `Showing board ${workspace}` }],
      _meta: board.details,
    };
  }
);
```

---

### Step 3: Return Structured Data

Every tool response includes three payloads:

| Payload | Purpose | Model Access |
|---------|---------|--------------|
| `structuredContent` | Concise JSON for widget + model | ✅ Visible |
| `content` | Optional narration for model | ✅ Visible |
| `_meta` | Large/sensitive data for widget only | ❌ Hidden |

```typescript
async function loadKanbanBoard(workspace: string) {
  const tasks = await db.fetchTasks(workspace);
  return {
    structuredContent: {
      columns: ["todo", "in-progress", "done"].map((status) => ({
        id: status,
        title: status.replace("-", " "),
        tasks: tasks.filter((task) => task.status === status).slice(0, 5),
      })),
    },
    content: [
      {
        type: "text",
        text: "Here's the latest snapshot. Drag cards to update status.",
      },
    ],
    _meta: {
      tasksById: Object.fromEntries(tasks.map((task) => [task.id, task])),
      lastSyncedAt: new Date().toISOString(),
    },
  };
}
```

---

### Step 4: Run Locally

```bash
npm run build       # compile server + widget
node dist/index.js  # start MCP server
```

Use MCP Inspector to verify:
- List roots at `http://localhost:<port>/mcp`
- Test tool calls
- Verify widget rendering

---

### Step 5: Expose HTTPS Endpoint

ChatGPT requires HTTPS. Use ngrok for development:

```bash
ngrok http <port>
# Forwarding: https://<subdomain>.ngrok.app -> http://127.0.0.1:<port>
```

For production, deploy to:
- Cloudflare Workers
- Fly.io
- Vercel
- AWS

---

## Advanced Capabilities

### Component-Initiated Tool Calls

```typescript
"_meta": {
  "openai/outputTemplate": "ui://widget/kanban-board.html",
  "openai/widgetAccessible": true,  // Enable callTool from widget
  "openai/visibility": "private"    // Hide from model
}
```

### Tool Annotations

```typescript
{
  "name": "update_task",
  "annotations": {
    "readOnlyHint": false,      // Can mutate state
    "openWorldHint": false,     // Bounded target (not arbitrary URLs)
    "destructiveHint": false    // No irreversible side effects
  }
}
```

| Annotation | When to Set |
|------------|-------------|
| `readOnlyHint: true` | GET requests, queries |
| `openWorldHint: false` | Bounded operations (e.g., update by ID) |
| `destructiveHint: true` | DELETE, overwrite operations |

### Content Security Policy

```typescript
"_meta": {
  "openai/widgetCSP": {
    connect_domains: ["https://api.example.com"],
    resource_domains: ["https://persistent.oaistatic.com"],
    redirect_domains: ["https://checkout.example.com"],
    frame_domains: ["https://*.example-embed.com"]
  }
}
```

| Domain Type | Purpose |
|-------------|---------|
| `connect_domains` | API calls |
| `resource_domains` | Images, fonts, scripts |
| `redirect_domains` | External checkout flows |
| `frame_domains` | Embedded iframes (use sparingly) |

### Company Knowledge Compatibility

Implement `search` and `fetch` tools for company knowledge:

```typescript
server.registerTool(
  "search",
  {
    title: "Search knowledge",
    inputSchema: { query: z.string() },
    annotations: { readOnlyHint: true },
  },
  async ({ query }) => ({
    content: [
      {
        type: "text",
        text: JSON.stringify({
          results: [
            { id: "doc-1", title: "Overview", url: "https://example.com" },
          ],
        }),
      },
    ],
  })
);
```

---

## Best Practices

1. **Design idempotent handlers** - Model may retry calls
2. **Keep `structuredContent` concise** - Only what model needs
3. **Version template URIs** - Cache-bust on breaking changes
4. **Set tool annotations** - Help ChatGPT classify tools
5. **Never expose secrets** - All payloads are user-visible

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Widget doesn't render | Check `mimeType: "text/html+skybridge"` |
| `window.openai` undefined | Verify MIME type, check CSP violations |
| CSP/CORS failures | Allow exact domains in `widgetCSP` |
| Stale bundles | Version template URIs on updates |
| Large payloads | Trim `structuredContent` to essentials |

---

## Related Resources

- **Next:** [Build ChatGPT UI](./02-chatgpt-ui.md)
- **Authentication:** [Authentication Guide](./03-authentication.md)
- **Examples:** [Apps SDK Examples](https://github.com/openai-apps-sdk-examples)

---

## Example: Complete Server

```typescript
// server/src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "hello-world", version: "1.0.0" });

// Register widget template
server.registerResource("hello", "ui://widget/hello.html", {}, async () => ({
  contents: [
    {
      uri: "ui://widget/hello.html",
      mimeType: "text/html+skybridge",
      text: `
<div id="root"></div>
<script type="module" src="https://example.com/hello-widget.js"></script>
      `.trim(),
    },
  ],
}));

// Register tool
server.registerTool(
  "hello_widget",
  {
    title: "Show hello widget",
    inputSchema: { name: { type: "string" } },
    _meta: { "openai/outputTemplate": "ui://widget/hello.html" },
  },
  async ({ name }) => ({
    structuredContent: { message: `Hello ${name}!` },
    content: [{ type: "text", text: `Greeting ${name}` }],
    _meta: {},
  })
);

await server.start();
```

```javascript
// hello-widget.js
const root = document.getElementById("root");
const { message } = window.openai.toolOutput ?? { message: "Hi!" };
root.textContent = message;
```
