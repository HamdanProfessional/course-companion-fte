# OpenAI Apps SDK Research

**Last Updated:** February 2026

Comprehensive research documentation for the OpenAI Apps SDK.

---

## Quick Start

1. **New to Apps SDK?** Start with [Planning Phase](./01-planning/)
2. **Building an app?** See [Build Phase](./02-build/)
3. **Ready to deploy?** Check [Deploy Phase](./03-deploy/)
4. **Submitting to directory?** Review [Guidelines](./04-guidelines/)

---

## Table of Contents

### Phase 1: Planning

| Document | Description |
|----------|-------------|
| [Use Case Research](./01-planning/01-use-case-research.md) | Identify use cases and define evaluation prompts |
| [Define Tools](./01-planning/02-define-tools.md) | Plan tools with metadata and schemas |
| [Design Components](./01-planning/03-design-components.md) | Plan UI components and state management |

### Phase 2: Build

| Document | Description |
|----------|-------------|
| [Build MCP Server](./02-build/01-mcp-server.md) | Wire tools, templates, and widget runtime |
| [Build ChatGPT UI](./02-build/02-chatgpt-ui.md) | Build UI components with `window.openai` API |
| [Authentication](./02-build/03-authentication.md) | OAuth 2.1 patterns |
| [State Management](./02-build/04-state-management.md) | Manage data and state |
| [Monetization](./02-build/05-monetization.md) | Checkout implementation |
| [Examples](./02-build/06-examples.md) | Pizzaz component gallery |

### Phase 3: Deploy

| Document | Description |
|----------|-------------|
| [Deploy Your App](./03-deploy/01-deploy-app.md) | Deployment options |
| [Connect from ChatGPT](./03-deploy/02-connect-chatgpt.md) | Connect to ChatGPT clients |
| [Test Your Integration](./03-deploy/03-testing-integration.md) | Testing strategies |
| [Submit Your App](./03-deploy/04-submit-app.md) | Submit to directory |

### Phase 4: Guidelines

| Document | Description |
|----------|-------------|
| [App Submission Guidelines](./04-guidelines/01-submission-guidelines.md) | Publishing policies |

---

## Key Concepts

### Architecture

```
User → ChatGPT → Model → MCP Tool Call → Your Server → Tool Response → Widget
```

### State Types

| Type | Location | Lifetime |
|------|----------|----------|
| Business Data | Server | Long-lived |
| UI State | Widget | Message-scoped |
| Cross-session | Backend | Cross-conversation |

### Tool Response

```javascript
{
  structuredContent: {},  // Widget + Model
  content: [],             // Model narration
  _meta: {}               // Widget only
}
```

---

## External Resources

- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk)
- [MCP Specification](https://modelcontextprotocol.io)
- [Pizzaz Examples](https://github.com/openai-apps-sdk-examples/pizzaz)

---

## Course Companion FTE

This research supports the Course Companion FTE project for Panaversity Agent Factory Hackathon IV.

**Architecture:** Zero-Backend-LLM
**Cost Target:** $0.002-0.004 per user per month
**Scale:** 10 to 100,000 users
