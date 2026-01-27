# Course Companion FTE - ChatGPT App

**ChatGPT App for Course Companion FTE Educational Platform**

## Overview

The Course Companion FTE ChatGPT App provides a conversational interface for learning AI Agent Development. It integrates with the Zero-Backend-LLM backend API and dynamically loads educational skills to deliver personalized tutoring.

## Architecture: Zero-Backend-LLM

```
Student → ChatGPT → Course Companion FTE Agent → Backend API (Deterministic)
         (interface)   (All AI reasoning)        (Content APIs only)
```

**Key Principle**: All AI intelligence happens in ChatGPT. Backend serves content verbatim only.

## Features

### Educational Skills (4 Skills)

1. **concept-explainer** - Explains concepts at learner's level with analogies
2. **quiz-master** - Conducts quizzes with encouragement and feedback
3. **socratic-tutor** - Guides learning through questioning
4. **progress-motivator** - Tracks progress and maintains motivation

### Intent Detection

Automatically detects student intent and loads appropriate skill:
- **Explain** ("explain X", "what is Y") → concept-explainer
- **Quiz** ("quiz me", "test me") → quiz-master
- **Socratic** ("stuck", "help me think") → socratic-tutor
- **Progress** ("how am I doing?", "my progress") → progress-motivator

### Backend Integration

Integrates with Zero-Backend-LLM backend for:
- Content delivery (chapters, search, navigation)
- Quiz management (get questions, submit answers, grading)
- Progress tracking (completion, streaks)
- Access control (freemium enforcement)

## Project Structure

```
chatgpt-app/
├── manifest.yaml          # ChatGPT App definition
├── .env.example          # Environment variables template
├── api/
│   ├── backend_client.py # Backend API client (Python)
│   └── types.ts          # TypeScript type definitions
├── lib/
│   └── intent_detector.py # Intent detection logic
└── README.md             # This file
```

## Setup

### 1. Backend Deployment

First, deploy the Zero-Backend-LLM backend:

```bash
cd ../backend
fly launch
fly deploy
fly secrets set DATABASE_URL="your-neon-db-url"
fly secrets set JWT_SECRET="your-jwt-secret"
```

Get your backend URL (e.g., `https://your-backend.fly.dev`)

### 2. Configure ChatGPT App

```bash
cd chatgpt-app

# Copy environment template
cp .env.example .env

# Edit .env with your backend URL
echo "BACKEND_URL=https://your-backend.fly.dev" > .env
```

### 3. Update manifest.yaml

Edit `manifest.yaml` and update the `BACKEND_URL`:

```yaml
env:
  BACKEND_URL: "https://your-backend.fly.dev"
```

### 4. Test Integration

Test the backend client:

```bash
# Install dependencies
pip install aiohttp

# Test intent detection
python lib/intent_detector.py

# Test backend client (requires backend to be running)
python -c "
import asyncio
from api.backend_client import get_backend_client

async def test():
    client = get_backend_client()
    chapters = await client.list_chapters()
    print(f'Found {len(chapters)} chapters')

asyncio.run(test())
"
```

## Usage

### In ChatGPT

1. Open the Course Companion FTE App
2. Start learning with natural language:

```
You: "Explain what MCP is"

App: [Loads concept-explainer skill, fetches chapter content]
"MCP (Model Context Protocol) is like a universal USB cable for AI apps..."
```

```
You: "Quiz me on MCP"

App: [Loads quiz-master skill, retrieves quiz]
"Great! Let's test your knowledge of MCP..."
```

```
You: "How am I doing?"

App: [Loads progress-motivator skill, fetches progress]
"Let me check your progress... Great job! Here's your learning journey..."
```

## Intent Detection Algorithm

**Keyword-based matching** (Zero-LLM, no classification models):

| Intent | Keywords | Skill | Priority |
|--------|----------|-------|----------|
| Quiz | quiz, test me, practice | quiz-master | 100 |
| Explain | explain, what is, how does | concept-explainer | 80 |
| Socratic | stuck, help me think, hint | socratic-tutor | 60 |
| Progress | progress, streak, how am i doing | progress-motivator | 40 |
| General | (fallback) | general-tutoring | 20 |

**Conflict Resolution**: Higher priority wins when multiple intents detected.

## Backend API Integration

### Content APIs

```python
from api.backend_client import get_backend_client

client = get_backend_client()

# List chapters
chapters = await client.list_chapters()

# Get chapter content
chapter = await client.get_chapter(chapter_id)

# Search content
results = await client.search_content("neural networks")
```

### Quiz APIs

```python
# Get quiz
quiz = await client.get_quiz(quiz_id)

# Submit answers
result = await client.submit_quiz(quiz_id, user_id, answers)

# Get attempt history
history = await client.get_quiz_results(quiz_id, user_id)
```

### Progress APIs

```python
# Get progress
progress = await client.get_progress(user_id)

# Update progress
progress = await client.update_progress(user_id, chapter_id)

# Get streak
streak = await client.get_streak(user_id)

# Record checkin
streak = await client.record_checkin(user_id)
```

## Zero-LLM Compliance

**Verified Compliant**: ChatGPT App makes NO LLM API calls.

### What Happens Where

| Component | ChatGPT App | Backend |
|-----------|-------------|---------|
| AI Reasoning | ✅ All in ChatGPT | ❌ None |
| Content Storage | ❌ None | ✅ PostgreSQL/R2 |
| Quiz Grading | ❌ None | ✅ Rule-based (answer keys) |
| Intent Detection | ✅ Keyword matching | ❌ None |
| Progress Tracking | ❌ None | ✅ Database queries |

### Forbidden in Backend

- ❌ OpenAI API calls (GPT-4, etc.)
- ❌ Anthropic API calls (Claude, etc.)
- ❌ LLM content generation
- ❌ Real-time embedding generation

## Deployment to ChatGPT App Store

### 1. Prepare App Package

```bash
# Create package
tar -czf course-companion-fte.tar.gz manifest.yaml
```

### 2. Submit to App Store

1. Visit https://chat.openai.com/apps
2. Click "Create New App"
3. Upload `course-companion-fte.tar.gz`
4. Fill in metadata:
   - Name: Course Companion FTE
   - Description: Your AI-powered tutor for AI Agent Development
   - Category: Education
5. Configure environment variables:
   - BACKEND_URL: Your deployed backend URL
6. Submit for review

### 3. Test in Development

ChatGPT provides a development environment for testing before production release.

## Error Handling

The ChatGPT App handles errors gracefully:

| Error | Response |
|-------|----------|
| Backend unavailable | "I'm having trouble connecting. Let me help with what I know..." |
| Access denied (403) | "This is premium content. Upgrade to unlock..." |
| Not found (404) | "I couldn't find that. Let me help you..." |
| Timeout | "Taking longer than expected. Let's try again..." |

## Cost Efficiency

**Zero infrastructure costs** - ChatGPT platform hosts the app.

| Resource | Cost/Month |
|----------|------------|
| ChatGPT App Hosting | $0 (OpenAI) |
| Backend API | $0.0036/user |
| **Total** | **$0.0036/user** ✅ |

## Testing

### Intent Detection Test

```bash
python lib/intent_detector.py
```

Expected output:
```
Intent Detection Test Results:
============================================================

Message: 'Explain what MCP is'
  Intent: explain
  Skill: concept-explainer
  Confidence: 0.90
  Keywords: ['explain']
```

### Backend Integration Test

```bash
# Test backend connection
curl https://your-backend.fly.dev/health
# Expected: {"status":"healthy",...}

# Test API endpoints
curl https://your-backend.fly.dev/api/v1/chapters
curl https://your-backend.fly.dev/api/v1/quizzes
```

## Skills Reference

The 4 educational skills are defined in `.claude/skills/`:

- `.claude/skills/concept-explainer/SKILL.md`
- `.claude/skills/quiz-master/SKILL.md`
- `.claude/skills/socratic-tutor/SKILL.md`
- `.claude/skills/progress-motivator/SKILL.md`

These skills are loaded by the Course Companion FTE agent when the ChatGPT App starts.

## Troubleshooting

### Backend Connection Fails

1. Check backend is running: `curl https://your-backend.fly.dev/health`
2. Verify BACKEND_URL in manifest.yaml
3. Check firewall/CORS settings

### Intent Detection Not Working

1. Test intent detector: `python lib/intent_detector.py`
2. Check keyword patterns in `lib/intent_detector.py`
3. Verify message format (lowercase matching)

### Skills Not Loading

1. Check skills exist in `.claude/skills/`
2. Verify skill names match in manifest.yaml
3. Check ChatGPT App console for errors

## Documentation

- **Backend API**: ../backend/README.md
- **Implementation Status**: ../IMPLEMENTATION_STATUS.md
- **Project README**: ../README.md
- **SDD Specifications**: ../specs/2-chatgpt-app/

## License

MIT License - Hackathon IV Project
