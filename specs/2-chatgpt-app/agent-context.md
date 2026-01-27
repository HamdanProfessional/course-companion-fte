# Agent Context: Course Companion FTE for ChatGPT App

**Feature**: 2-chatgpt-app
**Phase**: 1 - Design & Contracts
**Date**: 2026-01-28

## Overview

This document defines the Course Companion FTE agent that runs within ChatGPT to deliver personalized learning experiences.

---

## Agent Definition

**Name**: Course Companion FTE

**Description**: Your AI-powered tutor that teaches, explains, quizzes, and tracks progress through natural conversation.

**Role**: Educational Tutor - runs in ChatGPT to deliver personalized 24/7 tutoring

**Loaded Skills**:
- concept-explainer
- quiz-master
- socratic-tutor
- progress-motivator

---

## Agent Flow

```
Student Message → Intent Detection → Skill Load → Backend API Call (if needed) → Response Generation
```

**Step-by-Step**:
1. **Receive Message**: Student sends message to ChatGPT App
2. **Detect Intent**: Analyze message to determine student's goal
   - "Explain X" → Load concept-explainer
   - "Quiz me" → Load quiz-master
   - "I'm stuck" → Load socratic-tutor
   - "How am I doing?" → Load progress-motivator
3. **Load Skill**: ChatGPT platform loads appropriate skill
4. **Fetch Data** (if needed): Call backend API to get content, quizzes, progress
5. **Generate Response**: Use skill guidance to create personalized response
6. **Maintain Context**: Keep conversation history for continuity

---

## Intent Detection Algorithm

```python
def detect_intent(message: str) -> Intent:
    """
    Detect student intent from natural language message.
    Returns intent with confidence score.
    """
    message_lower = message.lower()

    # Priority 1: Quiz intent (explicit assessment requests)
    if any(keyword in message_lower for keyword in ["quiz", "test me", "practice", "check my knowledge"]):
        return Intent(type="quiz", confidence=0.95, skill="quiz-master")

    # Priority 2: Explain intent (core learning)
    if any(keyword in message_lower for keyword in ["explain", "what is", "how does", "help me understand"]):
        return Intent(type="explain", confidence=0.9, skill="concept-explainer")

    # Priority 3: Socratic intent (targeted help)
    if any(keyword in message_lower for keyword in ["stuck", "help me think", "give me a hint", "i'm lost"]):
        return Intent(type="socratic", confidence=0.85, skill="socratic-tutor")

    # Priority 4: Progress intent (tracking)
    if any(keyword in message_lower for keyword in ["progress", "streak", "how am i doing", "my stats"]):
        return Intent(type="progress", confidence=0.9, skill="progress-motivator")

    # Priority 5: General tutoring (fallback)
    return Intent(type="general", confidence=0.5, skill="concept-explainer")
```

**Priority Order Rationale**:
1. **Quiz first**: Explicit requests override implicit learning needs
2. **Explain second**: Core educational value
3. **Socratic third**: Targeted help for stuck students
4. **Progress fourth**: Tracking/motivation (less frequent)
5. **General last**: Catch-all for everything else

---

## Skill Loading

Skills are referenced in `manifest.yaml`:

```yaml
skills:
  - concept-explainer
  - quiz-master
  - socratic-tutor
  - progress-motivator
```

**Skill Loading Process**:
1. ChatGPT App reads manifest.yaml on startup
2. Platform loads each skill from `.claude/skills/{skill-name}/SKILL.md`
3. Skills available to Course Companion FTE agent
4. Agent routes student queries to appropriate skill based on intent

**Skill Execution**:
- Each skill contains procedural knowledge for specific educational tasks
- Skills are stateless - context comes from conversation history
- Skills can call backend APIs via tools defined in manifest
- Skills generate responses using ChatGPT's language model

---

## Backend API Integration

The agent integrates with backend APIs through tools defined in manifest.yaml:

```yaml
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
```

**API Call Examples**:

```python
# Get chapter content
GET /api/v1/chapters/{id}
Response: {
  "id": "uuid",
  "title": "Neural Networks",
  "content": "Full markdown content...",
  "order": 1,
  "difficulty": "beginner"
}

# Submit quiz
POST /api/v1/quizzes/{id}/submit
Request: {
  "answers": {
    "q1": "A",
    "q2": "C",
    "q3": "B"
  }
}
Response: {
  "score": 85,
  "passed": true,
  "feedback": "Great job! You mastered..."
}

# Get progress
GET /api/v1/progress/{user_id}
Response: {
  "completed_chapters": ["uuid1", "uuid2"],
  "current_chapter_id": "uuid3",
  "last_activity": "2026-01-28T10:00:00Z"
}
```

---

## Conversation Examples

### Example 1: Concept Explanation

**Student**: "Explain neural networks"

**Agent Flow**:
1. Detect intent: "explain" → Load concept-explainer skill
2. Call API: `GET /api/v1/chapters?search=neural+networks`
3. Fetch chapter content from backend
4. Generate explanation at learner's level using skill guidance

**Response**:
"I'd be happy to explain neural networks! Think of them like a team of experts working together. Each expert (neuron) specializes in recognizing something specific - like edges, shapes, or patterns. When you show the network an image, these experts pass their insights along, layer by layer, until the final expert says 'I see a cat!'

Let me break this down further..."
[Provides detailed explanation with examples and analogies]

### Example 2: Quiz Taking

**Student**: "Quiz me on neural networks"

**Agent Flow**:
1. Detect intent: "quiz" → Load quiz-master skill
2. Call API: `GET /api/v1/quizzes?chapter=neural-networks`
3. Present questions conversationally
4. Collect student answers
5. Call API: `POST /api/v1/quizzes/{id}/submit`
6. Display results with encouragement

**Response**:
"Great! Let's test your understanding of neural networks with a quick quiz.

**Question 1**: What's the primary function of a neuron in a neural network?
A) Store data
B) Process inputs and pass outputs
C) Display images
D) Connect to the internet

What's your answer?"

[Continues through all questions, then grades and provides feedback]

### Example 3: Progress Tracking

**Student**: "How am I doing?"

**Agent Flow**:
1. Detect intent: "progress" → Load progress-motivator skill
2. Call API: `GET /api/v1/progress/{user_id}`
3. Call API: `GET /api/v1/streaks/{user_id}`
4. Generate celebratory response with progress visualization

**Response**:
"You're doing fantastic! 🎉

**Your Progress**:
- ✅ Completed: 5 out of 10 chapters (50%)
- 🔥 Current streak: 7 days - amazing consistency!
- 📝 Quizzes passed: 4 out of 5
- ⏱️ Time spent learning: 3.5 hours

**Recommended Next Step**: Continue with Chapter 6 - 'Backpropagation' to understand how neural networks learn.

You're on track to complete the course in 2 weeks at this pace. Keep it up!"

---

## Error Handling

**Backend Unavailable**:
- Apologize for the issue
- Offer to help with available knowledge
- Suggest retrying in a few minutes
- Provide support contact if issue persists

**Access Denied (403)**:
- Explain premium content gracefully
- Highlight premium benefits
- Provide upgrade path
- Offer alternative free content

**Content Not Found (404)**:
- Apologize for the error
- Show available chapters
- Suggest searching for relevant topics
- Offer help with available content

**Timeout**:
- Acknowledge the delay
- Suggest retrying
- Offer alternative learning approach
- Maintain positive tone

---

## Conversation Continuity

**Maintaining Context**:
- Keep track of current chapter and topic
- Reference previous explanations for consistency
- Remember student's level and adjust complexity
- Track progress across multiple sessions
- Note student's preferred learning style

**Example Context Flow**:
```
Turn 1: "Explain neural networks"
→ [Agent explains neural networks]

Turn 2: "What about backpropagation?"
→ [Agent explains backpropagation, references neural networks from Turn 1]

Turn 3: "I'm confused about gradients"
→ [Agent loads socratic-tutor, asks guiding questions about gradients]

Turn 4: "Oh I get it now! Quiz me"
→ [Agent loads quiz-master, asks questions about neural networks and backpropagation]
```

---

## Zero-LLM Compliance

**Critical**: All AI intelligence happens in ChatGPT using the Course Companion FTE agent and loaded skills.

**Backend does NOT**:
- Make LLM API calls
- Generate explanations
- Grade quizzes subjectively
- Provide educational feedback

**Backend DOES**:
- Serve content verbatim (from R2 storage)
- Grade quizzes rule-based (answer key matching)
- Track progress (database operations)
- Check access rights (tier enforcement)

**Agent DOES**:
- Detect intent from natural language
- Load appropriate skills
- Call backend APIs
- Generate personalized responses using skills
- Adapt explanations to learner's level
- Encourage and motivate students

---

**Next Steps**: Create API client contracts and quickstart guide
