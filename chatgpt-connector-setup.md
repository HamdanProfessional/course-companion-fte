# ChatGPT App Connector Setup Guide

## How to Connect Your Course Companion FTE App to ChatGPT with Widgets

---

## Prerequisites

✅ MCP Server running at `https://sse.testservers.online`
✅ Widget HTML files deployed at `/ui/widget/*.html`
✅ Server accessible via HTTPS with valid TLS certificate

---

## Step 1: Enable Developer Mode in ChatGPT

1. Open ChatGPT (https://chatgpt.com)
2. Go to **Settings → Apps & Connectors → Advanced settings** (bottom of page)
3. Toggle **Developer mode** ON

**Note:** If you don't see this option, your account/organization may not support developer mode yet.

---

## Step 2: Create a Connector

1. In ChatGPT, navigate to **Settings → Connectors → Create**

2. Fill in the connector metadata:

   **Connector Name:**
   ```
   Course Companion FTE
   ```

   **Description:**
   ```
   Your AI-powered tutor for mastering AI Agent Development. Get personalized explanations, take quizzes, track progress, and learn 24/7 with interactive chapters and assessments.
   ```

   **Connector URL:**
   ```
   https://sse.testservers.online/mcp
   ```

3. Click **Create**

4. If successful, you'll see a list of tools:
   - list_chapters
   - get_chapter
   - search_content
   - get_quiz
   - submit_quiz
   - get_progress
   - update_progress
   - get_streak
   - check_access

---

## Step 3: Test the App with Widgets

1. **Open a new chat in ChatGPT**

2. **Click the + button** near the message composer, then click **More**

3. **Choose "Course Companion FTE"** from the list

4. **Try these prompts to see widgets:**

   ```
   Show me the chapters
   ```
   → Should display **Chapter List Widget** with interactive cards

   ```
   Give me a quiz
   ```
   → Should display **Quiz Widget** with multiple choice questions

---

## Troubleshooting

### "Connector creation failed"

**Check:**
```bash
# Test MCP endpoint manually
curl -X POST https://sse.testservers.online/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {}
  }'
```

**Should return:**
```json
{"jsonrpc":"2.0","result":{"protocolVersion":"2024-11-05",...},"id":1}
```

### "Widgets not showing, only text"

**Possible causes:**
1. Metadata not in correct format (we've fixed this)
2. Widget HTML not accessible
3. Wrong resource URI in outputTemplate

**Verify:**
```bash
# Check widget is accessible
curl -I https://sse.testservers.online/ui/widget/chapter-list.html

# Should return: HTTP/1.1 200 OK
```

### "Can't see my connector"

**Try:**
1. Refresh the page
2. Make sure Developer Mode is still ON
3. Check connector URL is correct

---

## Refreshing Metadata

When you update tools or widgets:

1. Update code on server
2. Restart Docker container
3. In ChatGPT: **Settings → Connectors**
4. Click into your connector → **Refresh**
5. Test with prompts

---

## Expected Widget Behavior

### Chapter List Widget
- 📚 Clickable chapter cards
- Gradient purple numbers (1, 2, 3, 4)
- Green BEGINNER badges
- Clock icons with time estimates
- Hover effects
- Clicking a chapter calls `get_chapter` tool

### Quiz Widget
- Progress bar at top
- Question cards with options A/B/C/D
- Click to select answers
- Previous/Next navigation
- Submit button when all answered
- Score display with pass/fail
- Review of correct/incorrect answers

---

## Next Steps

Once working:

1. **Test all tools** - Ensure each endpoint works correctly
2. **Verify widgets** - Check all interactive elements
3. **Test user flows** - Simulate learner journey
4. **Add more widgets** - Create widgets for other tools (search, progress, etc.)

---

## Important Notes

- **Developer mode** is for testing only (your account)
- **Public app submission** will be available later in 2026
- **Widgets require** proper ChatGPT App connector (not just MCP server)
- **HTTPS is required** - no HTTP allowed
- **Valid TLS certificate** - self-signed certs won't work

---

## Support

If you encounter issues:

1. Check server logs: `docker logs 8cb5cb6e723a`
2. Verify nginx configuration
3. Test MCP endpoint manually
4. Check widget files are accessible
5. Ensure metadata format is correct

---

**Created:** February 2, 2026
**App:** Course Companion FTE
**MCP Server:** https://sse.testservers.online/mcp
