# Course Companion FTE - ChatGPT App UI

React/TypeScript UI components for the Course Companion FTE ChatGPT App.

## Project Structure

```
chatgpt-app/ui/
├── src/
│   └── index.tsx          # Main React component (quiz interface)
├── dist/
│   └── component.js       # Bundled output (generated)
├── index.html             # HTML wrapper
├── package.json           # Dependencies
└── tsconfig.json          # TypeScript config
```

## Setup

```bash
cd chatgpt-app/ui
npm install
```

## Build

```bash
npm run build
```

This creates `dist/component.js` - the bundled React component.

## How It Works

1. **User triggers quiz tool** → ChatGPT calls `get_quiz`
2. **MCP Server response** → Includes component URL in metadata
3. **ChatGPT loads component** → Renders React UI in iframe
4. **User interacts** → Component uses `window.openai` API
5. **State sync** → Component persists state to ChatGPT

## Component Features

- ✅ Visual quiz interface with clickable options
- ✅ Progress tracking
- ✅ Instant feedback
- ✅ Score calculation
- ✅ Results screen
- ✅ State persistence via `window.openai.setWidgetState()`
- ✅ Follow-up messages via `window.openai.sendFollowUpMessage()`

## Next Steps

1. Build the component: `npm run build`
2. Host `dist/` folder on a web server
3. Update MCP server to include component URL in quiz response
4. Test in ChatGPT App

## Integration with MCP Server

The MCP server needs to return the component URL in the tool response metadata:

```json
{
  "role": "tool",
  "tool_call_id": "...",
  "content": "...quiz data as JSON...",
  "metadata": {
    "openai/widgetDomain": "https://your-domain.com",
    "openai/widgetCSP": {
      "connect_domains": ["https://chatgpt.com"],
      "resource_domains": ["https://*.oaistatic.com"]
    },
    "openai/widgetUrl": "https://your-domain.com/ui/index.html"
  }
}
```

This tells ChatGPT to load your React component in an iframe!
