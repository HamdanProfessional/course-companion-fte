# Quickstart Guide: ChatGPT App for Course Companion FTE

**Feature**: 2-chatgpt-app
**Prerequisites**: OpenAI ChatGPT account, backend API deployed
**Estimated Setup Time**: 10 minutes

---

## Overview

This guide will help you create and configure a ChatGPT App for the Course Companion FTE platform. By the end, you'll have a working ChatGPT App that students can use to learn through conversation.

---

## 1. Prerequisites

### Required Accounts
- **OpenAI ChatGPT**: [Sign up free](https://chat.openai.com/)
- **GitHub**: For app manifest repository
- **Backend API**: Must be deployed (see `specs/1-zero-backend-api/quickstart.md`)

### Required Information
- Backend API URL (e.g., `https://api.coursecompanion.example.com`)
- Course Companion FTE agent skills (`.claude/skills/`)

---

## 2. Project Structure

```
chatgpt-app/
├── manifest.yaml              # ChatGPT App configuration (REQUIRED)
├── api/
│   ├── backend_client.py      # Backend API integration (Python)
│   └── types.ts               # TypeScript interfaces (if using TS)
└── lib/
    ├── intent-detector.py     # Intent detection logic
    └── skill-loader.py        # Dynamic skill loading

.claude/
├── agents/
│   └── course-companion-fte.md    # Educational agent
└── skills/
    ├── concept-explainer/SKILL.md
    ├── quiz-master/SKILL.md
    ├── socratic-tutor/SKILL.md
    └── progress-motivator/SKILL.md
```

---

## 3. Create manifest.yaml

Create `chatgpt-app/manifest.yaml`:

```yaml
name: Course Companion FTE
description: |
  Your AI-powered tutor for mastering course content. Get personalized explanations,
  take quizzes, track progress, and learn 24/7 through natural conversation.

version: 1.0.0
author: Course Companion FTE Team

# Tools - Backend API Integration
tools:
  - name: content_api
    description: Retrieve course content, chapters, and sections
    type: http
    endpoint: ${BACKEND_URL}/api/v1

  - name: quiz_api
    description: Get quizzes, submit answers, view results
    type: http
    endpoint: ${BACKEND_URL}/api/v1

  - name: progress_api
    description: Track learning progress and streaks
    type: http
    endpoint: ${BACKEND_URL}/api/v1

  - name: access_api
    description: Check and manage user access tiers
    type: http
    endpoint: ${BACKEND_URL}/api/v1

# Environment Variables
env:
  BACKEND_URL: "https://your-backend-api.com"

# Pricing and Access
pricing:
  type: freemium
  free_tier:
    - "First 3 chapters"
    - "Basic quizzes"
    - "Progress tracking"
  premium_tier:
    - "All chapters"
    - "Advanced quizzes"
    - "Detailed analytics"

# Skills Reference
skills:
  - concept-explainer
  - quiz-master
  - socratic-tutor
  - progress-motivator
```

**Key Fields**:
- `name`: App name displayed in ChatGPT
- `description`: Brief description of app functionality
- `tools`: Backend API endpoints the app can call
- `skills`: Educational skills to load (must exist in `.claude/skills/`)
- `env`: Environment variables for backend URL
- `pricing`: Freemium tier configuration

---

## 4. Create Backend API Client

### Option A: Python Client

Create `chatgpt-app/api/backend_client.py`:

```python
import os
import requests
from typing import Dict, List, Optional

class BackendClient:
    """Client for Course Companion FTE backend API."""

    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL")
        if not self.base_url:
            raise ValueError("BACKEND_URL environment variable not set")

    def get_chapters(self) -> List[Dict]:
        """Get all chapters."""
        response = requests.get(f"{self.base_url}/chapters")
        response.raise_for_status()
        return response.json()

    def get_chapter(self, chapter_id: str) -> Dict:
        """Get specific chapter content."""
        response = requests.get(f"{self.base_url}/chapters/{chapter_id}")
        response.raise_for_status()
        return response.json()

    def get_quiz(self, quiz_id: str) -> Dict:
        """Get quiz with questions."""
        response = requests.get(f"{self.base_url}/quizzes/{quiz_id}")
        response.raise_for_status()
        return response.json()

    def submit_quiz(self, quiz_id: str, answers: Dict[str, str]) -> Dict:
        """Submit quiz answers and get results."""
        response = requests.post(
            f"{self.base_url}/quizzes/{quiz_id}/submit",
            json={"answers": answers}
        )
        response.raise_for_status()
        return response.json()

    def get_progress(self, user_id: str) -> Dict:
        """Get user progress."""
        response = requests.get(f"{self.base_url}/progress/{user_id}")
        response.raise_for_status()
        return response.json()

    def get_streak(self, user_id: str) -> Dict:
        """Get user streak information."""
        response = requests.get(f"{self.base_url}/streaks/{user_id}")
        response.raise_for_status()
        return response.json()

    def check_access(self, user_id: str, resource: str) -> Dict:
        """Check if user has access to resource."""
        response = requests.post(
            f"{self.base_url}/access/check",
            json={"user_id": user_id, "resource": resource}
        )
        response.raise_for_status()
        return response.json()
```

### Option B: TypeScript Client

Create `chatgpt-app/api/backend_client.ts`:

```typescript
interface Chapter {
  id: string;
  title: string;
  content?: string;
  order: number;
  difficulty_level: string;
  estimated_time: number;
}

interface Quiz {
  id: string;
  title: string;
  questions: Question[];
}

interface QuizResult {
  score: number;
  passed: boolean;
  feedback: string;
}

class BackendClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.BACKEND_URL || '';
    if (!this.baseUrl) {
      throw new Error('BACKEND_URL environment variable not set');
    }
  }

  async getChapters(): Promise<Chapter[]> {
    const response = await fetch(`${this.baseUrl}/chapters`);
    if (!response.ok) throw new Error(`Failed to fetch chapters: ${response.statusText}`);
    return response.json();
  }

  async getChapter(chapterId: string): Promise<Chapter> {
    const response = await fetch(`${this.baseUrl}/chapters/${chapterId}`);
    if (!response.ok) throw new Error(`Failed to fetch chapter: ${response.statusText}`);
    return response.json();
  }

  async getQuiz(quizId: string): Promise<Quiz> {
    const response = await fetch(`${this.baseUrl}/quizzes/${quizId}`);
    if (!response.ok) throw new Error(`Failed to fetch quiz: ${response.statusText}`);
    return response.json();
  }

  async submitQuiz(quizId: string, answers: Record<string, string>): Promise<QuizResult> {
    const response = await fetch(`${this.baseUrl}/quizzes/${quizId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });
    if (!response.ok) throw new Error(`Failed to submit quiz: ${response.statusText}`);
    return response.json();
  }

  async getProgress(userId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/progress/${userId}`);
    if (!response.ok) throw new Error(`Failed to fetch progress: ${response.statusText}`);
    return response.json();
  }

  async getStreak(userId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/streaks/${userId}`);
    if (!response.ok) throw new Error(`Failed to fetch streak: ${response.statusText}`);
    return response.json();
  }
}

export default BackendClient;
```

---

## 5. Create Intent Detector

Create `chatgpt-app/lib/intent-detector.py`:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Intent:
    type: str
    confidence: float
    skill: Optional[str] = None

def detect_intent(message: str) -> Intent:
    """
    Detect student intent from natural language message.
    Returns intent with confidence score and recommended skill.
    """
    message_lower = message.lower()

    # Priority 1: Quiz intent (explicit assessment requests)
    if any(keyword in message_lower for keyword in
           ["quiz", "test me", "practice", "check my knowledge"]):
        return Intent(type="quiz", confidence=0.95, skill="quiz-master")

    # Priority 2: Explain intent (core learning)
    if any(keyword in message_lower for keyword in
           ["explain", "what is", "how does", "help me understand"]):
        return Intent(type="explain", confidence=0.9, skill="concept-explainer")

    # Priority 3: Socratic intent (targeted help)
    if any(keyword in message_lower for keyword in
           ["stuck", "help me think", "give me a hint", "i'm lost"]):
        return Intent(type="socratic", confidence=0.85, skill="socratic-tutor")

    # Priority 4: Progress intent (tracking)
    if any(keyword in message_lower for keyword in
           ["progress", "streak", "how am i doing", "my stats"]):
        return Intent(type="progress", confidence=0.9, skill="progress-motivator")

    # Priority 5: General tutoring (fallback)
    return Intent(type="general", confidence=0.5, skill="concept-explainer")
```

---

## 6. Configure Skills

Ensure skills exist in `.claude/skills/`:

```bash
.claude/skills/
├── concept-explainer/
│   └── SKILL.md
├── quiz-master/
│   └── SKILL.md
├── socratic-tutor/
│   └── SKILL.md
└── progress-motivator/
    └── SKILL.md
```

Each `SKILL.md` should contain:
- Skill name and description
- When to use this skill
- How to approach the task
- Example responses

---

## 7. Test Locally

Before deploying to ChatGPT App Store:

```bash
# Test intent detection
python -c "
from lib.intent_detector import detect_intent
print(detect_intent('explain neural networks'))
print(detect_intent('quiz me'))
print(detect_intent('how am i doing?'))
"

# Test backend client
python -c "
from api.backend_client import BackendClient
client = BackendClient()
chapters = client.get_chapters()
print(f'Found {len(chapters)} chapters')
"
```

---

## 8. Deploy to ChatGPT App Store

### Create App Package

```bash
# Package the app
tar -czf course-companion-fte.tar.gz chatgpt-app/

# Or create a ZIP file
zip -r course-companion-fte.zip chatgpt-app/
```

### Submit to App Store

1. Go to [ChatGPT App Store](https://chat.openai.com/apps)
2. Click "Create New App"
3. Upload `course-companion-fte.tar.gz` or `course-companion-fte.zip`
4. Fill in app metadata:
   - Name: Course Companion FTE
   - Description: AI-powered tutor for personalized learning
   - Category: Education
   - Tags: tutoring, learning, quiz, progress
5. Review and submit

---

## 9. Verify Deployment

After approval, test the app in ChatGPT:

1. Open ChatGPT
2. Select "Apps" from the sidebar
3. Choose "Course Companion FTE"
4. Test various queries:
   - "Explain neural networks"
   - "Quiz me on machine learning"
   - "How am I doing?"
   - "I'm stuck on backpropagation"

---

## 10. Monitor and Update

### Monitoring
- Track usage through ChatGPT App Store analytics
- Monitor backend API logs for errors
- Collect user feedback

### Updates
To update the app:
1. Modify `manifest.yaml` or skills
2. Create new package
3. Submit update to App Store
4. Users get automatic updates

---

## Troubleshooting

### Issue: Skills not loading
```bash
# Solution: Verify skills exist in correct location
ls .claude/skills/*/SKILL.md
# Should show all 4 skills
```

### Issue: Backend API calls failing
```bash
# Solution: Verify BACKEND_URL is correct
echo $BACKEND_URL
# Test API directly
curl $BACKEND_URL/health
```

### Issue: Intent detection not working
```python
# Solution: Test intent detector with sample queries
python -c "from lib.intent_detector import detect_intent; print(detect_intent('your query here'))"
```

### Issue: App rejected from App Store
- Check `manifest.yaml` schema validation
- Verify all required fields are present
- Ensure skills are properly formatted
- Review ChatGPT App Store guidelines

---

## Next Steps

1. **Test Thoroughly**: Try various user queries and edge cases
2. **Gather Feedback**: Share with beta users for feedback
3. **Iterate**: Update skills and responses based on feedback
4. **Scale**: Monitor performance and optimize as needed

---

## Useful Resources

- [ChatGPT App Store Documentation](https://platform.openai.com/docs/apps)
- [OpenAI Apps SDK Reference](https://platform.openai.com/docs/apps/reference)
- [Backend API Documentation](../1-zero-backend-api/contracts/)
- [Agent Skills Specification](../../.claude/spec/agent-skills-spec.md)

---

**Need Help?**
- Check `agent-context.md` for agent details
- Review `plan.md` for architecture decisions
- See `contracts/` for API specifications
- Open an issue on GitHub
