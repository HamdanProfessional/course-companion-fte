# Claude Code Rules

This file contains project-specific rules, skills, and agents for the Course Companion FTE (Hackathon IV) project.

## Project Overview

**Course Companion FTE** - A Digital Full-Time Equivalent educational tutor built for Panaversity Agent Factory Hackathon IV.

This is an AI-Native Course Companion that:
1. **Teaches** — Delivers course content with intelligent navigation
2. **Explains** — Breaks down concepts at the learner's level
3. **Quizzes** — Tests understanding with immediate feedback
4. **Tracks** — Monitors progress and identifies knowledge gaps
5. **Adapts** — Adjusts difficulty and approach (Phase 2)
6. **Web App** — Provides a Comprehensive Stand Alone Web App (Phase 3)

## Architecture: Zero-Backend-LLM (Phase 1)

**Key Principle:** Backend serves content verbatim, NO LLM calls. All AI intelligence happens in ChatGPT using the Course Companion FTE agent.

```
Student → ChatGPT App → Course Companion FTE Agent → Deterministic Backend
         (interface)     (All AI reasoning)    (Content APIs only)
```

**Benefits:**
- Near-zero marginal cost per user
- Scales to 100K+ users
- 85-90% cost reduction vs human tutors
- $0.002-0.004 per user per month

---

# Part 1: Runtime Skills

The Course Companion FTE uses four specialized skills. These are in `.claude/skills/`:

## Available Skills

### concept-explainer
**Location:** `.claude/skills/concept-explainer/SKILL.md`

**Use when:** Students ask "explain", "what is", "how does", "help me understand"

**Purpose:** Explains concepts at various complexity levels using analogies, examples, and progressive complexity adjustment.

---

### quiz-master
**Location:** `.claude/skills/quiz-master/SKILL.md`

**Use when:** Students request "quiz", "test me", "practice", "check my knowledge"

**Purpose:** Guides students through quizzes with encouragement, immediate feedback, and celebration of effort.

---

### socratic-tutor
**Location:** `.claude/skills/socratic-tutor/SKILL.md`

**Use when:** Students say "help me think", "I'm stuck", "give me a hint"

**Purpose:** Guides learning through questioning rather than direct answers, facilitating discovery.

---

### progress-motivator
**Location:** `.claude/skills/progress-motivator/SKILL.md`

**Use when:** Students ask about "my progress", "streak", "how am I doing"

**Purpose:** Tracks progress, celebrates achievements, maintains motivation through positive reinforcement.

---

# Part 2: Development Agents

Specialized agents for building the Course Companion FTE application. These are in `.claude/agents/`:

## Production Agent

### course-companion-fte
**Location:** `.claude/agents/course-companion-fte.md`

**Role:** Educational Tutor - runs in ChatGPT to deliver personalized learning

**Use proactively when:**
- Students need educational support or tutoring
- Course navigation or learning assessment is needed
- Explaining concepts, conducting quizzes, or tracking progress

**Loaded Skills:** concept-explainer, quiz-master, socratic-tutor, progress-motivator

---

## Development Agents

### fastapi-backend-dev
**Location:** `.claude/agents/fastapi-backend-dev.md`

**Role:** Backend Developer - builds deterministic APIs

**Use proactively when:**
- Creating backend endpoints, database schemas, or server-side logic
- Implementing content, quiz, progress, or search APIs
- Setting up PostgreSQL (Neon) or Cloudflare R2 storage

**Critical Responsibility:** Enforces **Zero-Backend-LLM** - NO LLM API calls in Phase 1 backend

**Tech Stack:** FastAPI, Python, SQLAlchemy, PostgreSQL, Cloudflare R2

---

### chatgpt-app-dev
**Location:** `.claude/agents/chatgpt-app-dev.md`

**Role:** ChatGPT App Frontend Developer - builds conversational interface

**Use proactively when:**
- Creating ChatGPT App manifest or configuration
- Implementing conversation flow orchestration
- Integrating with backend APIs or loading educational skills

**Tech Stack:** OpenAI Apps SDK, TypeScript/Python

---

### nextjs-frontend-dev
**Location:** `.claude/agents/nextjs-frontend-dev.md`

**Role:** Web Frontend Developer - builds LMS web application (Phase 3)

**Use proactively when:**
- Creating Next.js pages, React components, or UI/UX
- Building responsive dashboards, quiz interfaces, or progress visualization
- Implementing frontend features for the web application

**Tech Stack:** Next.js, React, TypeScript, Tailwind CSS

---

### devops-deploy
**Location:** `.claude/agents/devops-deploy.md`

**Role:** DevOps Engineer - infrastructure and deployment

**Use proactively when:**
- Setting up cloud infrastructure (Fly.io, Railway, Vercel)
- Configuring databases (Neon), storage (Cloudflare R2), or CI/CD
- Implementing monitoring, security, or cost optimization

**Tech Stack:** Docker, Fly.io, Neon, Cloudflare R2, Vercel, GitHub Actions

---

# Part 3: Spec-Driven Development (SDD)

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architect to build products.

## Task Context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions
- All changes are small, testable, and reference code precisely

## Core Guarantees (Product Promise)

- **Record every user input verbatim** in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- **PHR routing** (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- **ADR suggestions:** When an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge Capture (PHR) for Every User Input
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

### 4. Explicit ADR Suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with ADRs

### 5. Human as Tool Strategy
You MUST invoke the user for input when encountering situations that require human judgment.

## Default Policies (Must Follow)

- **Clarify and plan first** - Keep business understanding separate from technical plan
- **Do not invent APIs, data, or contracts** - Ask targeted clarifiers if missing
- **Never hardcode secrets or tokens** - Use `.env` and docs
- **Prefer the smallest viable diff** - Do not refactor unrelated code
- **Cite existing code** with code references (start:end:path)
- **Keep reasoning private** - Output only decisions, artifacts, and justifications

---

# Part 4: Project Structure

```
.claude/
├── agents/
│   ├── course-companion-fte.md      # Production: Educational tutor agent
│   ├── fastapi-backend-dev.md      # Development: Backend API developer
│   ├── chatgpt-app-dev.md          # Development: ChatGPT App developer
│   ├── nextjs-frontend-dev.md      # Development: Web app developer
│   └── devops-deploy.md            # Development: DevOps engineer
├── skills/
│   ├── concept-explainer/SKILL.md  # Explain concepts at learner's level
│   ├── quiz-master/SKILL.md        # Conduct quizzes with encouragement
│   ├── socratic-tutor/SKILL.md     # Guide through questioning
│   └── progress-motivator/SKILL.md # Track progress & motivate
└── commands/
    └── sp.*.md                     # Spec-driven development commands

.specify/
├── memory/constitution.md          # Project principles
├── templates/                      # SpecKit Plus templates
└── scripts/                        # Helper scripts

specs/
├── <feature>/spec.md               # Feature requirements
├── <feature>/plan.md               # Architecture decisions
└── <feature>/tasks.md              # Testable tasks

history/
├── prompts/                        # Prompt History Records
└── adr/                            # Architecture Decision Records
```

---

# Part 5: How Skills and Agents Work Together

## Development Workflow (Building the App)

```
User Request: "Build the backend APIs"
        ↓
Claude detects intent → Loads fastapi-backend-dev agent
        ↓
Agent creates Zero-Backend-LLM backend
        ↓
Deploy to Fly.io (using devops-deploy agent)
```

## Production Workflow (Running the App)

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

---

# Part 6: Important Reminders

## Zero-Backend-LLM Architecture (CRITICAL)

**Phase 1 Rule: Backend has ZERO LLM API calls**

| Component | Backend Does | ChatGPT Does |
|-----------|--------------|--------------|
| Content Delivery | Serve content verbatim | Explain at learner's level |
| Navigation | Return next/previous chapters | Suggest optimal path |
| Q&A | Return relevant sections | Answer using content only |
| Quizzes | Grade with answer key | Present, encourage, explain |
| Progress | Store completion, streaks | Celebrate, motivate |
| Access Control | Check access rights | Explain premium gracefully |

**Teams are IMMEDIATELY DISQUALIFIED from Phase 1 if the backend contains ANY LLM API calls.**

---

**Version:** 1.0 (Hackathon IV)
**Last Updated:** January 2026
**Architecture:** Agent Factory + Zero-Backend-LLM
**Cost Target:** $0.002-0.004 per user per month
**Scale:** 10 to 100,000 users without linear cost increase
