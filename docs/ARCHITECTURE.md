# Course Companion FTE - Architecture Diagram

## System Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COURSE COMPANION FTE ARCHITECTURE                          ║
║                         (Agent Factory Hackathon IV)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                                    USER                                     │
│                        (Student / Teacher / Admin)                          │
└────────────────────────────┬───────────────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
        ╔═══════════▼═════════╗  ╔═════▼════════════════╗
        ║   CHATGPT APP      ║  ║    WEB APP (Next.js)  ║
        ║  (OpenAI SDK)       ║  ║    Phase 1-2-3        ║
        ╚═══════════╦═════════╝  ╚═════╦════════════════╝
                    │                     │
                    │    ┌─────────────────┴──────────────────┐
                    │    │                                    │
            ╔═══════▼═════▼════════════════════════════════════▼════════╗
            ║              FASTAPI BACKEND (Phase 3)                   ║
            ║  ┌─────────────────────────────────────────────────────┐  ║
            ║  │  v3/tutor/ - Unified API Endpoints                  │  ║
            ║  │                                                     │  ║
            ║  │  ┌────────────────┐  ┌─────────────────┐          │  ║
            ║  │  │ DETERMINISTIC  │  │  HYBRID (LLM)   │          │  ║
            ║  │  │    (Phase 1)   │  │   (Phase 2)     │          │  ║
            ║  │  │                │  │                 │          │  ║
            ║  │  │ • content      │  │ • ai/mentor     │          │  ║
            ║  │  │ • quizzes      │  │ • ai/adaptive   │          │  ║
            ║  │  │ • progress     │  │ • quizzes/llm   │          │  ║
            ║  │  │ • access       │  │ (Premium Gated) │          │  ║
            ║  │  └────────────────┘  └─────────────────┘          │  ║
            ║  │                                                     │  ║
            ║  │  Services Layer                                     │  ║
            ║  │  ┌──────────────┐  ┌──────────────┐               │  ║
            ║  │  │ Content      │  │ Progress     │               │  ║
            ║  │  │ Quiz         │  │ Streak       │               │  ║
            ║  │  │ Certificate  │  │ Teacher      │               │  ║
            ║  │  │ MCP Server   │  │ LLM Service  │               │  ║
            ║  │  └──────────────┘  └──────────────┘               │  ║
            ║  └─────────────────────────────────────────────────────┘  ║
            ╚═══════════╦═══════════════════════════════════════════════╝
                        │
        ┌───────────────┼───────────────┬─────────────────┐
        │               │               │                 │
  ╔═════▼═════╗  ╔═════▼═════╗  ╔═════▼═════╗  ╔══════▼════════╗
  ║ PostgreSQL║  ║Cloudflare ║  ║   Claude  ║  ║   OpenAI      ║
  ║  (Neon)   ║  ║    R2     ║  ║   API     ║  ║   API         ║
  ║           ║  ║  Storage  ║  ║ (Hybrid)  ║  ║  (Optional)    ║
  ╚═══════════╝  ╚═══════════╝  ╚═══════════╝  ╚═══════════════╝


┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENT SKILLS (Runtime)                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │concept-explainer │  │  quiz-master     │  │socratic-tutor   │        │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘        │
│           ┌──────────────────┐                                          │
│           │progress-motivator│                                          │
│           └──────────────────┘                                          │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                    TIER & ACCESS CONTROL                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐              │
│  │     FREE      │  │   PREMIUM     │  │      PRO      │              │
│  │               │  │               │  │               │              │
│  │ • Chaps 1-3   │  │ • All Chaps   │  │ • All Chaps   │              │
│  │ • Basic Quiz  │  │ • All Quizzes │  │ • LLM Grading │              │
│  │ • ChatGPT     │  │ • Progress    │  │ • AI Mentor   │              │
│  │               │  │ • Streaks     │  │ • Adaptive    │              │
│  │               │  │               │  │ • Certificates│              │
│  └────────────────┘  └────────────────┘  └────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│   STUDENT    │
└──────┬───────┘
       │
       │ 1. Request Chapter
       ▼
┌──────────────────┐
│   WEB APP        │  ←→ localStorage: user_id, user_tier
│   (Next.js)      │
└──────┬───────────┘
       │
       │ 2. GET /api/v3/tutor/content/chapters/{id}
       ▼
┌──────────────────────────────────┐
│   FASTAPI BACKEND                │
│   ┌────────────────────────┐     │
│   │ ContentService         │     │
│   │ • Check cache          │     │
│   │ • Query DB/Chapters    │     │
│   │ • Return content       │     │
│   └────────────────────────┘     │
└──────────┬───────────────────────┘
           │
           │ 3. Response with content
           ▼
┌──────────────────┐
│   WEB APP        │  Renders chapter with:
│                  │  • Reading progress bar
│                  │  • Table of contents
│                  │  • "Mark as Complete" button
└──────────────────┘


┌──────────────┐
│   STUDENT    │
└──────┬───────┘
       │
       │ 1. Submit Quiz
       ▼
┌──────────────────┐
│   WEB APP        │
└──────┬───────────┘
       │
       │ 2. POST /api/v3/tutor/quizzes/{id}/submit
       ▼
┌──────────────────────────────────┐
│   FASTAPI BACKEND                │
│   ┌────────────────────────┐     │
│   │ QuizService            │     │
│   │ • Grade with answer key│     │
│   │ • Record attempt       │     │
│   │ • Return results       │     │
│   └────────────────────────┘     │
│                                   │
│   ┌────────────────────────┐     │
│   │ IF (premium && llm)    │     │
│   │ • LLMGradeService      │     │
│   │ • Detailed feedback    │     │
│   └────────────────────────┘     │
└──────────┬───────────────────────┘
           │
           │ 3. Quiz results
           ▼
┌──────────────────┐
│   WEB APP        │  Shows:
│                  │  • Score, pass/fail
│                  │  • Question results
│                  │  • Take again button
└──────────────────┘
```

## Zero-Backend-LLM Architecture (Phase 1)

```
┌──────────────┐
│   STUDENT    │
└──────┬───────┘
       │
       │ Question: "Explain neural networks"
       ▼
┌────────────────────────────────────────┐
│         CHATGPT APP                   │
│  ┌──────────────────────────────────┐ │
│  │ 1. Detect Intent                 │ │
│  │    → "explain" → concept-explainer│ │
│  └──────────────────────────────────┘ │
│  ┌──────────────────────────────────┐ │
│  │ 2. Call Backend API              │ │
│  │    GET /api/v3/tutor/content/... │ │
│  └──────────────────────────────────┘ │
└──────────────┬─────────────────────────┘
               │
               │ 3. Return content VERBATIM
               ▼
┌────────────────────────────────────────┐
│         CHATGPT (LLM)                  │
│  ┌──────────────────────────────────┐ │
│  │ 4. Explain at learner's level    │ │
│  │    • Use analogies               │ │
│  │    • Adjust complexity           │ │
│  │    • Add examples                │ │
│  │    • ALL LLM WORK HERE          │ │
│  └──────────────────────────────────┘ │
└──────────────┬─────────────────────────┘
               │
               │ 5. Natural language explanation
               ▼
┌──────────────┐
│   STUDENT    │ (Understands the concept!)
└──────────────┘


KEY: NO LLM calls in backend for Phase 1!
```

## Hybrid Architecture (Phase 2)

```
┌──────────────┐
│ PRO STUDENT  │
└──────┬───────┘
       │
       │ Request: "Grade my essay answer"
       ▼
┌────────────────────────────────────────┐
│         WEB APP                       │
│  • Verify user tier = PRO             │
│  • Enable "LLM Grading" mode          │
└──────────────┬─────────────────────────┘
               │
               │ POST /api/v3/tutor/quizzes/{id}/submit
               │ Body: { answers, grading_mode: "llm" }
               ▼
┌────────────────────────────────────────┐
│         FASTAPI BACKEND               │
│  ┌──────────────────────────────────┐ │
│  │ IF (user.tier == "PRO")          │ │
│  │    AND (grading_mode == "llm")   │ │
│  │ THEN:                            │ │
│  │    LLMGradeService.grade_quiz()   │ │
│  │       ↓                           │ │
│  │    Claude API call                │ │
│  │       ↓                           │ │
│  │    Detailed feedback              │ │
│  └──────────────────────────────────┘ │
└──────────────┬─────────────────────────┘
               │
               │ Enhanced results with AI feedback
               ▼
┌──────────────┐
│ PRO STUDENT  │ (Gets detailed, personalized feedback!)
└──────────────┘


KEY: LLM calls ONLY for premium features!
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    PRODUCTION SERVER                          │
│                   92.113.147.250                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────┐  ┌──────────────────────┐          │
│  │   FRONTEND (Web)     │  │    BACKEND (API)      │          │
│  │   Port: 3225         │  │    Port: 3505         │          │
│  │   Next.js + PM2      │  │    FastAPI + PM2      │          │
│  └──────────────────────┘  └──────────────────────┘          │
│                                                                │
│  ┌──────────────────────┐  ┌──────────────────────┐          │
│  │   PostgreSQL (Neon)  │  │   Cloudflare R2      │          │
│  │   Remote             │  │   Remote             │          │
│  └──────────────────────┘  └──────────────────────┘          │
│                                                                │
└────────────────────────────────────────────────────────────────┘

Access URLs:
• Frontend:  http://92.113.147.250:3225
• Backend:   http://92.113.147.250:3505
• API Docs:  http://92.113.147.250:3505/docs
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COMPONENT MAPPING                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  FRONTEND (web-app/)          →  BACKEND (backend/src/)           │
│  ─────────────────────────────────────────────────────────────     │
│  /pages/dashboard.tsx         →  /api/v3/tutor/progress/summary  │
│  /pages/chapters/[id].tsx     →  /api/v3/tutor/content/chapters  │
│  /pages/quizzes/[id].tsx      →  /api/v3/tutor/quizzes/{id}      │
│  /pages/progress.tsx          →  /api/v3/tutor/progress/*        │
│  /pages/ai-mentor.tsx         →  /api/v3/tutor/ai/mentor         │
│  /pages/subscription.tsx      →  /api/v3/tutor/access/plans      │
│                                                                     │
│  AGENT SKILLS (.claude/skills/)                                    │
│  ─────────────────────────────────────────────────────────────     │
│  concept-explainer/          →  Content retrieval + ChatGPT       │
│  quiz-master/                →  Quiz API + encouragement           │
│  socratic-tutor/             →  Q&A from content                   │
│  progress-motivator/         →  Progress tracking + celebration   │
│                                                                     │
│  DATA MODELS (backend/src/models/)                                │
│  ─────────────────────────────────────────────────────────────     │
│  User, Chapter, Quiz, Question, QuizAttempt                      │
│  Progress, Streak, Certificate, TeacherAnalytics                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Architecture Version:** 1.0
**Last Updated:** February 2026
**Production:** http://92.113.147.250:3225
