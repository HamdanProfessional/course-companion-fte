# MCP Server for ChatGPT App - WORKING! ✅

## ✅ Current Status (Feb 1, 2026)

**MCP Server:** RUNNING on port 3506
- ✅ Listening at `http://92.113.147.250:3506`
- ✅ HTTPS proxy working at `https://sse.testservers.online/mcp/sse`
- ✅ Firewall ports 3505 and 3506 opened
- ✅ Returns proper JSON-RPC responses following MCP specification
- ✅ Tools available: `list_quizzes`, `get_quiz`, `search_content`
- ✅ Mock data fallback when backend is unavailable

## 🔧 How It Works

**Architecture:**
```
ChatGPT (Developer Mode)
    ↓ HTTPS
Cloudflare Proxy (sse.testservers.online)
    ↓ HTTP
nginx Reverse Proxy (/mcp/sse → localhost:3506)
    ↓
FastAPI MCP Server (mcp_server_proper.py)
    ↓ JSON-RPC
Backend API (optional) OR Mock Data (fallback)
```

**Tools Available:**

1. **list_quizzes** - List all available quizzes
   - Returns: Quiz ID, title, difficulty, question count
   - Mock data includes 3 demo quizzes

2. **get_quiz** - Get a specific quiz with widget
   - Returns: Quiz data with `_meta` for ChatGPT widget
   - Includes interactive quiz UI component
   - Mock data includes 3 questions per quiz

3. **search_content** - Search course content
   - Returns: Chapter ID, title, snippet
   - Mock data returns 2 sample chapters

## 🚀 How to Start MCP Server

If the MCP server is not running:

```bash
# SSH to server
ssh n00bi2761@92.113.147.250

# Run the startup script
cd ~/course-companion/backend
./start_mcp_proper.sh

# Or manually:
cd ~/course-companion/backend
export PATH=/home/n00bi2761/.local/bin:$PATH
nohup python3 mcp_server_proper.py > mcp_proper.log 2>&1 &

# Check logs
tail -f ~/course-companion/backend/mcp_proper.log
```

## 🧪 Test the MCP Server

**Test 1: Health Check**
```bash
curl http://92.113.147.250:3506/health
# Expected: {"status":"healthy","mcp_endpoint":"/sse"}
```

**Test 2: Initialize (MCP handshake)**
```bash
curl -X POST "https://sse.testservers.online/mcp/sse" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1}'
```

**Test 3: List Tools**
```bash
curl -X POST "https://sse.testservers.online/mcp/sse" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}'
```

**Test 4: Call list_quizzes**
```bash
curl -X POST "https://sse.testservers.online/mcp/sse" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_quizzes","arguments":{}},"id":3}'
```

**Test 5: Get Quiz with Widget**
```bash
curl -X POST "https://sse.testservers.online/mcp/sse" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_quiz","arguments":{"quiz_id":"quiz-001"}},"id":4}'
```

## 🎯 Connect in ChatGPT Developer Mode

1. Go to https://chatgpt.com (with Developer Mode enabled)
2. Apps → Create New App → Add MCP Server
3. Server URL: `https://sse.testservers.online/mcp/sse`
4. Test with:
   ```
   List all quizzes
   Get the quiz "Introduction to AI Agents"
   Search for "MCP protocol"
   ```

## 📝 What's Working

- ✅ MCP server running on port 3506
- ✅ JSON-RPC responses following MCP spec exactly
- ✅ nginx reverse proxy configured correctly
- ✅ HTTPS via Cloudflare proxy
- ✅ Firewall ports opened
- ✅ Three tools available: list_quizzes, get_quiz, search_content
- ✅ Mock data fallback for demo purposes
- ✅ Widget metadata (`_meta`) included in quiz responses

## 🔍 Server Details

**MCP Server Process:**
- File: `~/course-companion/backend/mcp_server_proper.py`
- Port: 3506
- Host: 0.0.0.0 (all interfaces)
- Process: Running as user n00bi2761
- Logs: `~/course-companion/backend/mcp_proper.log`

**Dependencies Installed:**
- fastapi
- uvicorn
- httpx
- pydantic
- pydantic-settings

## 🛠️ Troubleshooting

**If MCP server stops responding:**
```bash
# Check if process is running
ssh n00bi2761@92.113.147.250 "ps aux | grep mcp_server"

# Check logs
ssh n00bi2761@92.113.147.250 "tail -50 ~/course-companion/backend/mcp_proper.log"

# Restart server
ssh n00bi2761@92.113.147.250 "~/course-companion/backend/start_mcp_proper.sh"
```

**If HTTPS endpoint fails:**
```bash
# Check nginx status
ssh n00bi2761@92.113.147.250 "echo 2763 | sudo -S systemctl status nginx"

# Check nginx error logs
ssh n00bi2761@92.113.147.250 "echo 2763 | sudo -S tail -20 /var/log/nginx/error.log"

# Reload nginx
ssh n00bi2761@92.113.147.250 "echo 2763 | sudo -S systemctl reload nginx"
```

## 📊 Mock Data

**Quizzes Available:**
1. **quiz-001** - Introduction to AI Agents (Beginner)
2. **quiz-002** - MCP Protocol Basics (Intermediate)
3. **quiz-003** - ChatGPT Apps Development (Advanced)

**Sample Questions:**
Each quiz includes 3 questions with:
- Multiple choice options (a, b, c, d)
- Correct answer
- Explanation

## 🎉 ChatGPT App Features

When connected to ChatGPT, the app provides:

1. **Conversational Quiz Discovery** - "Show me available quizzes"
2. **Interactive Quiz Widget** - Renders quiz UI inside ChatGPT
3. **Instant Feedback** - Shows correct/incorrect with explanations
4. **Content Search** - Search course material for topics
5. **Zero-LLM Backend** - All content served deterministically

**Sources:**
- [Build your ChatGPT UI](https://developers.openai.com/apps-sdk/build/chatgpt-ui/)
- [Build your MCP server](https://developers.openai.com/apps-sdk/build/mcp-server/)
