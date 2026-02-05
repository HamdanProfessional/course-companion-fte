# Test Your Integration

**Source:** https://developers.openai.com/apps-sdk/deploy/testing
**Phase:** Deploy
**Last Updated:** February 2026

---

## Overview

Testing validates connector behavior before exposing to users.

### Three Focus Areas

| Area | What to Test |
|------|--------------|
| **Tool Correctness** | Schema validation, error handling, edge cases |
| **Component UX** | Rendering, interactions, state persistence |
| **Discovery Precision** | Golden prompts (direct, indirect, negative) |

---

## MCP Inspector

### Fastest Local Debugging

```bash
npx @modelcontextprotocol/inspector@latest
```

### Steps

1. Run MCP server
2. Launch inspector
3. Enter server URL (e.g., `http://127.0.0.1:2091/mcp`)
4. Click **List Tools** and **Call Tool**

### Benefits

- Inspect raw requests/responses
- Render components inline
- Surface errors immediately
- Capture screenshots for launch review

---

## ChatGPT Developer Mode Testing

### After HTTPS Reachable

1. Link in **Settings → Connectors → Developer mode**
2. Toggle on in new conversation
3. Run golden prompt set:
   - Direct prompts
   - Indirect prompts
   - Negative prompts
4. Record:
   - Model selects right tool
   - Arguments passed correctly
   - Confirmation prompts appear as expected

### Mobile Testing

Test mobile layouts:
- ChatGPT iOS app
- ChatGPT Android app

---

## API Playground Testing

### For Raw Logs

1. Open API Playground
2. **Tools → Add → MCP Server**
3. Provide HTTPS endpoint
4. Issue test prompts
5. Inspect JSON request/response in right panel

---

## Test Coverage Checklist

### Tool Correctness

- [ ] Each tool exercised with representative inputs
- [ ] Schema validation working
- [ ] Error handling tested
- [ ] Edge cases covered (empty results, missing IDs)
- [ ] Auth flows tested (if applicable)

### Component UX

- [ ] Widgets render without console errors
- [ ] Custom styling injected correctly
- [ ] State restoration works
- [ ] Mobile layouts tested

### Discovery Precision

- [ ] Direct prompts trigger correctly
- [ ] Indirect prompts match as expected
- [ ] Negative prompts don't trigger
- [ ] Tool descriptions accurate

---

## Regression Checklist Before Launch

| Item | Check |
|------|-------|
| Tool list | Matches documentation, no unused prototypes |
| Structured content | Matches declared `outputSchema` for every tool |
| Widgets | No console errors, correct styling, state restoration |
| Auth | Valid tokens issued, invalid tokens rejected meaningfully |
| Discovery | Golden prompts pass, negative prompts don't trigger |

---

## Automated Testing

### Test Fixtures

Keep test fixtures close to MCP code:

```typescript
// fixtures/test-prompts.ts
export const goldenPrompts = {
  direct: [
    "Show my tasks",
    "Create a new task called 'Review PRs'"
  ],
  indirect: [
    "What do I need to work on?",
    "Help me get organized"
  ],
  negative: [
    "Tell me a joke",
    "What's the weather?"
  ]
};
```

### Auth Testing

Automated tests for OAuth flows:
- Token issuance
- Token validation
- Token refresh
- Scope enforcement

---

## Documentation

Capture findings in a doc:
- Compare results release over release
- Track discovery precision/recall
- Document edge cases and fixes
- Maintain troubleshooting playbook

---

## Best Practices

1. **Test early, test often** - Use MCP Inspector during development
2. **Golden prompt set** - Maintain and test regularly
3. **Mobile testing** - Don't forget mobile layouts
4. **Error scenarios** - Test failure modes
5. **Documentation** - Keep test results organized

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Widget not rendering | Check `text/html+skybridge` MIME type |
| Tool not discovered | Verify tool description and metadata |
| Auth failing | Check token validation logic |
| State not persisting | Verify `widgetState` API usage |

---

## Related Resources

- **Previous:** [Connect from ChatGPT](./02-connect-chatgpt.md)
- **Next:** [Submit Your App](./04-submit-app.md)
- **MCP Inspector:** [Model Context Protocol Inspector](https://github.com/modelcontextprotocol/inspector)

---

## Test Plan Template

```markdown
## Test Plan: [Your App Name]

### Golden Prompts

**Direct:**
- [ ] Prompt 1
- [ ] Prompt 2

**Indirect:**
- [ ] Prompt 1
- [ ] Prompt 2

**Negative:**
- [ ] Prompt 1
- [ ] Prompt 2

### Tool Tests

- [ ] Tool 1: Test case 1, 2, 3
- [ ] Tool 2: Test case 1, 2, 3

### Component Tests

- [ ] Rendering: Mobile, Desktop
- [ ] State: Persistence, Reset
- [ ] Errors: Fallback UI

### Auth Tests

- [ ] Login flow
- [ ] Token validation
- [ ] Invalid tokens
```
