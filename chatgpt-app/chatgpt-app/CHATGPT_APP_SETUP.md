# Course Companion FTE - ChatGPT App Setup Guide

## Status: ✅ Ready to Deploy

### MCP Server Configuration
- **URL**: `https://sse.testservers.online/api/v1/sse`
- **Protocol**: MCP (Model Context Protocol) with SSE (Server-Sent Events)
- **Authentication**: None
- **Status**: ✅ Tested and working

### Available Tools (9)

The MCP server exposes these tools to ChatGPT:

| Tool Name | Description |
|-----------|-------------|
| `list_chapters` | List all available chapters |
| `get_chapter` | Get detailed chapter content by ID |
| `search_content` | Search course content |
| `get_quiz` | Get quiz questions |
| `submit_quiz` | Submit quiz answers for grading |
| `get_progress` | Get user learning progress |
| `update_progress` | Mark chapter as complete |
| `get_streak` | Get streak information |
| `check_access` | Check content access (freemium) |

### Creating the ChatGPT App

1. **Go to ChatGPT** → Create a "NEW APP (BETA)"

2. **Fill in the form**:
   - **Name**: `Course Companion FTE`
   - **Description**: `Your AI-powered tutor for mastering AI Agent Development. Get personalized explanations, take quizzes, track progress, and learn 24/7.`
   - **MCP server url**: `https://sse.testservers.online/api/v1/sse`
   - **Authentication**: `No Auth`

3. **Paste Instructions**:
   Copy the content from `instructions.md` into the instructions field.

4. **Save and Test**

### Testing the App

Test these commands:

1. **List chapters**:
   ```
   "Show me all available chapters"
   ```

2. **Get chapter content**:
   ```
   "Tell me about chapter 1"
   ```

3. **Search for topic**:
   ```
   "What do you have about MCP?"
   ```

4. **Take a quiz**:
   ```
   "Test my knowledge with a quiz"
   ```

5. **Check progress**:
   ```
   "How am I doing?"
   ```

### Backend Endpoint Status

| Endpoint | Status |
|----------|--------|
| POST /api/v1/sse (initialize) | ✅ Working |
| POST /api/v1/sse (tools/list) | ✅ Working |
| GET /api/v1/sse (SSE stream) | ✅ Working |
| POST /api/v1/sse (tools/call) | ✅ Ready |

### Files Prepared

- ✅ `manifest.json` - MCP server configuration
- ✅ `instructions.md` - System prompt with intent detection
- ✅ Backend SSE endpoint at `/api/v1/sse`

### Next Steps

1. Create the app in ChatGPT UI
2. Test the MCP connection
3. Verify all 9 tools are discovered
4. Test each tool works correctly
5. Deploy to users

---

**Deployment Date**: 2026-01-31
**MCP Protocol Version**: 2.0
**Backend URL**: https://sse.testservers.online
