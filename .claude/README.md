# Course Companion FTE - Agent & Skills Configuration

This directory contains the Agent and Skills configuration for the Course Companion FTE (Digital Full-Time Equivalent Educational Tutor) built for Hackathon IV.

## Directory Structure

```
.claude/
├── agents/                           # Claude Code subagents (.md files)
│   ├── course-companion-fte.md      # Production: Educational tutor agent
│   ├── fastapi-backend-dev.md      # Development: Backend API developer
│   ├── chatgpt-app-dev.md          # Development: ChatGPT App developer
│   ├── nextjs-frontend-dev.md      # Development: Web app developer
│   └── devops-deploy.md            # Development: DevOps engineer
├── skills/                           # Agent Skills (directories with SKILL.md)
│   ├── concept-explainer/          # Explain concepts at learner's level
│   ├── quiz-master/                # Conduct quizzes with encouragement
│   ├── socratic-tutor/             # Guide through questioning
│   ├── progress-motivator/         # Track progress & motivate
│   └── skill-creator/              # Skill creation tool
└── commands/                        # Spec-driven development commands
    └── sp.*.md
```

## Part 1: Production Agent

### course-companion-fte
**File:** `.claude/agents/course-companion-fte.md`

**Role:** Educational Tutor - runs in ChatGPT to deliver personalized learning

**Use proactively when:**
- Students need educational support or tutoring
- Course navigation or learning assessment is needed
- Explaining concepts, conducting quizzes, or tracking progress

**Loaded Skills:** concept-explainer, quiz-master, socratic-tutor, progress-motivator

**Capabilities:**
- Operates 24/7 (168 hours/week)
- Provides personalized educational support
- Uses all four specialized skills
- Implements Zero-Backend-LLM architecture (Phase 1)
- Maintains 99%+ consistency in educational delivery

## Part 2: Development Agents

### fastapi-backend-dev
**File:** `.claude/agents/fastapi-backend-dev.md`

**Role:** Backend Developer - builds deterministic APIs

**Use proactively when:**
- Creating backend endpoints, database schemas, or server-side logic
- Implementing content, quiz, progress, or search APIs
- Setting up PostgreSQL (Neon) or Cloudflare R2 storage

**Critical Responsibility:** Enforces **Zero-Backend-LLM** - NO LLM API calls in Phase 1 backend

**Tech Stack:** FastAPI, Python, SQLAlchemy, PostgreSQL, Cloudflare R2

---

### chatgpt-app-dev
**File:** `.claude/agents/chatgpt-app-dev.md`

**Role:** ChatGPT App Frontend Developer - builds conversational interface

**Use proactively when:**
- Creating ChatGPT App manifest or configuration
- Implementing conversation flow orchestration
- Integrating with backend APIs or loading educational skills

**Tech Stack:** OpenAI Apps SDK, TypeScript/Python

**Reach:** 800M+ ChatGPT users

---

### nextjs-frontend-dev
**File:** `.claude/agents/nextjs-frontend-dev.md`

**Role:** Web Frontend Developer - builds LMS web application (Phase 3)

**Use proactively when:**
- Creating Next.js pages, React components, or UI/UX
- Building responsive dashboards, quiz interfaces, or progress visualization
- Implementing frontend features for the web application

**Tech Stack:** Next.js, React, TypeScript, Tailwind CSS

---

### devops-deploy
**File:** `.claude/agents/devops-deploy.md`

**Role:** DevOps Engineer - infrastructure and deployment

**Use proactively when:**
- Setting up cloud infrastructure (Fly.io, Railway, Vercel)
- Configuring databases (Neon), storage (Cloudflare R2), or CI/CD
- Implementing monitoring, security, or cost optimization

**Tech Stack:** Docker, Fly.io, Neon, Cloudflare R2, Vercel, GitHub Actions

**Infrastructure:**
- Backend: Fly.io ($5-10/month)
- Database: Neon ($0-25/month)
- Storage: Cloudflare R2 (~$5/month)
- Frontend: Vercel (Free-$20/month)
- **Total: $16-70/month for 10K users**

## Part 3: Runtime Skills

These skills are loaded by the Course Companion FTE agent to deliver educational experiences:

### concept-explainer
**Directory:** `.claude/skills/concept-explainer/`

**Trigger:** "explain", "what is", "how does", "help me understand"

**Purpose:** Explains concepts at various complexity levels using:
- Analogies and real-world connections
- Progressive complexity adjustment
- Concrete examples from course material
- Common misconception addressing

---

### quiz-master
**Directory:** `.claude/skills/quiz-master/`

**Trigger:** "quiz", "test me", "practice", "check my knowledge"

**Purpose:** Conducts assessments with:
- Progressive difficulty
- Immediate detailed feedback
- Celebration of effort (not just correctness)
- Learning-focused approach

---

### socratic-tutor
**Directory:** `.claude/skills/socratic-tutor/`

**Trigger:** "help me think", "I'm stuck", "give me a hint"

**Purpose:** Guides discovery through:
- Targeted questions
- Progressive hints
- Building on student's existing knowledge
- Avoiding direct answers

---

### progress-motivator
**Directory:** `.claude/skills/progress-motivator/`

**Trigger:** "my progress", "streak", "how am I doing"

**Purpose:** Maintains motivation by:
- Tracking completion and streaks
- Celebrating achievements
- Providing encouragement
- Suggesting next steps

## How They Work Together

### Development Workflow (Building the App)

```
User Request: "Build the backend APIs"
        ↓
Claude detects intent → Loads fastapi-backend-dev agent
        ↓
Agent creates Zero-Backend-LLM backend
        ↓
Deploy to Fly.io (using devops-deploy agent)
```

### Production Workflow (Running the App)

```
Student: "Explain neural networks"
        ↓
ChatGPT → Loads course-companion-fte agent
        ↓
Agent detects intent → Loads concept-explainer skill
        ↓
Fetches content from backend APIs
        ↓
Provides personalized explanation
```

## Zero-Backend-LLM Architecture (Phase 1)

**Key Principle:** Backend serves content verbatim, NO LLM calls.

```
Student → ChatGPT App → Course Companion FTE Agent → Deterministic Backend
         (interface)     (All AI reasoning)    (Content APIs only)
```

**Benefits:**
- Near-zero marginal cost per user
- Scales to 100K+ users
- 85-90% cost reduction vs human tutors
- $0.002-0.004 per user per month

**Phase 1 Rule: Backend has ZERO LLM API calls**

| Component | Backend Does | ChatGPT Does |
|-----------|--------------|--------------|
| Content Delivery | Serve content verbatim | Explain at learner's level |
| Navigation | Return next/previous chapters | Suggest optimal path |
| Q&A | Return relevant sections | Answer using content only |
| Quizzes | Grade with answer key | Present, encourage, explain |
| Progress | Store completion, streaks | Celebrate, motivate |
| Access Control | Check access rights | Explain premium gracefully |

**⚠️ Teams are IMMEDIATELY DISQUALIFIED from Phase 1 if the backend contains ANY LLM API calls.**

## Agent Factory Architecture Context

This follows the **Agent Factory 8-layer architecture**:

| Layer | Technology | Phase | Purpose |
|:---:|-----|:---:|-----|
| L0 | gVisor | Phase 2-3 | Secure execution |
| L1 | Apache Kafka | Phase 2-3 | Event backbone |
| L2 | Dapr + Workflows | Phase 2-3 | Infrastructure + Durability |
| L3 | FastAPI | **Phase 1-3** | HTTP interface + A2A |
| L4 | OpenAI Agents SDK | Phase 2-3 | High-level orchestration |
| L5 | Claude Agent SDK | Phase 2-3 | Agentic execution |
| L6 | Runtime Skills + MCP | **Phase 1-3** | Domain knowledge + Tools |
| L7 | A2A Protocol | Phase 2-3 | Multi-FTE collaboration |

**Phase 1 Focus:** L3 (FastAPI) + L6 (Skills + MCP) — Deterministic backend

## Course Content Options

The FTE can be configured for any of these course topics:

| Option | Topic | Example Content |
|--------|-------|-----------------|
| A | AI Agent Development | Claude Agent SDK, MCP, Agent Skills |
| B | Cloud-Native Python | FastAPI, Containers, Kubernetes |
| C | Generative AI Fundamentals | LLMs, Prompting, RAG, Fine-tuning |
| D | Modern Python | Modern Python with Typing |

## Files Summary

### Production Agent
```
.claude/agents/course-companion-fte.md         (5.9 KB) - Main educational tutor
```

### Development Agents
```
.claude/agents/fastapi-backend-dev.md         (4.4 KB) - Backend API development
.claude/agents/chatgpt-app-dev.md             (4.5 KB) - ChatGPT App frontend
.claude/agents/nextjs-frontend-dev.md         (6.1 KB) - Web app development
.claude/agents/devops-deploy.md               (5.6 KB) - Infrastructure & DevOps
```

### Runtime Skills
```
.claude/skills/concept-explainer/SKILL.md     (5.0 KB) - Concept explanations
.claude/skills/quiz-master/SKILL.md           (6.6 KB) - Quiz delivery
.claude/skills/socratic-tutor/SKILL.md        (8.1 KB) - Guided discovery
.claude/skills/progress-motivator/SKILL.md     (10.7 KB) - Progress tracking
```

**Total:** ~57 KB of procedural knowledge for building and running the Course Companion FTE platform

---

**Version:** 1.0 (Hackathon IV)
**Last Updated:** January 2026
**Architecture:** Agent Factory + Zero-Backend-LLM
**Cost Target:** $0.002-0.004 per user per month
**Scale:** 10 to 100,000 users without linear cost increase
