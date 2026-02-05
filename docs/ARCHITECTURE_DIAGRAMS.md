# Course Companion FTE - Architecture Diagrams

**Project**: Course Companion FTE (Digital Full-Time Equivalent Educational Tutor)
**Hackathon**: Panaversity Agent Factory Hackathon IV
**Date**: February 2026

---

## Table of Contents

1. [Phase 1: Zero-Backend-LLM Architecture](#diagram-1-phase-1-zero-backend-llm-flow)
2. [Phase 2: Hybrid Intelligence Architecture](#diagram-2-phase-2-hybrid-architecture)
3. [Full System Architecture](#diagram-3-full-system-architecture)
4. [Data Flow Diagrams](#diagram-4-data-flows)

---

## Diagram 1: Phase 1 - Zero-Backend-LLM Flow

### Core Principle
Backend serves content **deterministically** (no LLM calls). All AI intelligence happens in ChatGPT.

```mermaid
graph TB
    subgraph "Student Interface"
        A[Student] --> B{ChatGPT App}
        B --> C[Course Companion FTE Agent]
    end

    subgraph "AI Intelligence (ChatGPT)"
        C --> D[concept-explainer Skill]
        C --> E[quiz-master Skill]
        C --> F[socratic-tutor Skill]
        C --> G[progress-motivator Skill]
    end

    subgraph "Deterministic Backend (FastAPI)"
        H[API Gateway] --> I[Content API]
        H --> J[Quiz API]
        H --> K[Progress API]
        H --> L[Q&A API]
        H --> M[Access API]
    end

    subgraph "Data Layer"
        I --> N[(PostgreSQL)]
        I --> O[Cloudflare R2<br/>Content Storage]
        J --> N
        K --> N
        L --> I
        M --> N
    end

    %% Interactions
    D -.->|Fetch Content| I
    D -.->|Search Content| L
    E -.->|Get Questions| J
    E -.->|Submit Answers| J
    F -.->|Get Progress| K
    G -.->|Update Streak| K

    style B fill:#e1f5ff
    style C fill:#fff9e1
    style H fill:#f0f0f0
    style N fill:#e8f5e9
    style O fill:#fff3e0

    classDef ai fill:#fff9e1,stroke:#f9a825,stroke-width:2px
    classDef backend fill:#f5f5f5,stroke:#616161,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px

    class C,D,E,F,G ai
    class H,I,J,K,L,M backend
    class N,O data
```

### Key Characteristics

| Component | Backend Does | ChatGPT Does |
|-----------|--------------|--------------|
| **Content Delivery** | Serve verbatim chapters | Explain at learner's level |
| **Navigation** | Return next/previous | Suggest optimal learning path |
| **Q&A** | Return relevant sections | Answer using content only |
| **Quizzes** | Grade with answer key | Present, encourage, explain |
| **Progress** | Store completion, streaks | Celebrate, motivate |
| **Access** | Check tier, enforce gates | Explain premium gracefully |

### Cost Impact
- **Per-User Cost**: $0.002-0.004 per month
- **Scaling**: 10 to 100,000+ users without linear cost increase
- **LLM Costs**: $0 (all LLM usage in ChatGPT, user pays)

---

## Diagram 2: Phase 2 - Hybrid Architecture

### Premium Features with Controlled LLM Usage

```mermaid
graph TB
    subgraph "User Request Flow"
        A[Premium User] --> B{Feature Request}
    end

    B -->|Phase 1 Features| C[Zero-LLM Path]
    B -->|Phase 2 Features| D{Check Access}

    C --> E[Deterministic APIs]
    E --> F[(Database)]

    D -->|Allowed| G[Hybrid APIs]
    D -->|Denied| H[Access Error]

    subgraph "Phase 2: Hybrid Features (Premium)"
        G --> I[Adaptive Learning<br/>Knowledge Gaps]
        G --> J[LLM-Graded Quizzes<br/>Free-form Responses]
        G --> K[Cross-Chapter Synthesis<br/>Connect Concepts]
    end

    subgraph "Cost Tracking"
        I --> L[Cost Tracking Service]
        J --> L
        K --> L
        L --> M[(Cost Database)]
    end

    subgraph "External LLM (Optional)"
        I -.->|ENABLE_PHASE_2_LLM=true| N[OpenAI API]
        J -.->|ENABLE_PHASE_2_LLM=true| N
        K -.->|ENABLE_PHASE_2_LLM=true| N
    end

    N --> O[Response Cache]
    O --> I
    O --> J
    O --> K

    style B fill:#e1f5ff
    style D fill:#fff3e0
    style G fill:#f3e5f5
    style L fill:#ffebee
    style N fill:#fce4ec

    classDef phase1 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef phase2 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef llm fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class C,E,F phase1
    class G,I,J,K phase2
    class N,O llm
```

### Feature Gating Matrix

| Feature | FREE | PREMIUM | PRO | LLM Used |
|---------|------|---------|-----|----------|
| Content Delivery | ✅ | ✅ | ✅ | ❌ |
| Rule-Based Quizzes | ✅ | ✅ | ✅ | ❌ |
| Progress Tracking | ✅ | ✅ | ✅ | ❌ |
| **Adaptive Learning** | ❌ | ✅ | ✅ | ✅ |
| **LLM Quiz Grading** | ❌ | ❌ | ✅ | ✅ |
| **Cross-Chapter Synthesis** | ❌ | ✅ | ✅ | ✅ |
| Cost Tracking | Hidden | Visible | Detailed | - |

### Environment Control
```bash
# Disable Phase 2 (Phase 1 compliance)
ENABLE_PHASE_2_LLM=false

# Enable Phase 2 (default)
ENABLE_PHASE_2_LLM=true
```

---

## Diagram 3: Full System Architecture

### Complete Implementation Stack

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[ChatGPT App<br/>OpenAI Apps SDK]
        B[Next.js Web App<br/>React + Tailwind]
    end

    subgraph "Agent Layer (ChatGPT)"
        C[Course Companion FTE<br/>Educational Agent]
        C --> D[concept-explainer]
        C --> E[quiz-master]
        C --> F[socratic-tutor]
        C --> G[progress-motivator]
    end

    subgraph "API Gateway (FastAPI)"
        H[Main Router<br/>localhost:3505]

        subgraph "Phase 1 APIs (Zero-LLM)"
            H --> I[Content API]
            H --> J[Quiz API]
            H --> K[Progress API]
            H --> L[Q&A API]
            H --> M[Access API]
            H --> N[MCP Server<br/>JSON-RPC 2.0]
        end

        subgraph "Phase 2 APIs (Hybrid)"
            H --> O[Adaptive Learning API]
            H --> P[LLM Quiz API]
            H --> Q[Cross-Chapter Synthesis API]
            H --> R[Cost Tracking API]
        end

        subgraph "Phase 3 APIs (Enhanced)"
            H --> S[Unified v3 API<br/>/api/v3/tutor/*]
            S --> T[Progress Dashboard]
            S --> U[AI Mentor Chat]
            S --> V[Gamification]
        end
    end

    subgraph "Service Layer"
        I --> W[ContentService]
        J --> X[QuizService]
        K --> Y[ProgressService]
        L --> W
        M --> Z[AccessService]
        O --> AA[AdaptiveService]
        Q --> W
        Q --> AB[LLM Service]
    end

    subgraph "Data Layer"
        W --> AC[(PostgreSQL<br/>Neon)]
        X --> AC
        Y --> AC
        Z --> AC
        AA --> AC
        AB --> AD[OpenAI API<br/>Optional]
    end

    subgraph "Storage Layer"
        W --> AE[Cloudflare R2<br/>S3-Compatible]
    end

    %% Frontend connections
    A -.->|MCP Protocol| N
    B -.->|HTTP/REST| H

    %% Widget support
    N --> AF[Widget Templates<br/>8 HTML Widgets]

    style A fill:#e3f2fd
    style B fill:#e8f5e9
    style C fill:#fff8e1
    style H fill:#f5f5f5
    style AC fill:#e8f5e9
    style AE fill:#fff3e0

    classDef frontend fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef agent fill:#fff9e1,stroke:#f9a825,stroke-width:2px
    classDef api fill:#f5f5f5,stroke:#616161,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px

    class A,B frontend
    class C,D,E,F,G agent
    class H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V api
    class AC,AE data
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **ChatGPT Frontend** | OpenAI Apps SDK | Conversational interface |
| **Web Frontend** | Next.js 14, React, Tailwind | Standalone web app |
| **Backend API** | FastAPI, Python 3.11 | RESTful API |
| **Database** | PostgreSQL (Neon) | User data, progress |
| **Storage** | Cloudflare R2 | Content files (S3-compatible) |
| **MCP Protocol** | JSON-RPC 2.0 | ChatGPT integration |
| **LLM (Optional)** | OpenAI API | Phase 2 premium features |
| **Deployment** | Docker, Fly.io | Container orchestration |

---

## Diagram 4: Data Flows

### Flow A: ChatGPT App Learning Session

```mermaid
sequenceDiagram
    actor S as Student
    participant C as ChatGPT
    participant A as Course Companion<br/>FTE Agent
    participant M as MCP Server
    participant B as Backend API
    participant D as Database

    S->>C: "Explain neural networks"
    C->>A: Load course-companion-fte
    A->>A: Detect intent (concept-explainer)
    A->>M: mcp.call_tool("get_chapter")
    M->>B: GET /api/v1/chapters/neural-networks
    B->>D: SELECT * FROM chapters
    D-->>B: Chapter content
    B-->>M: JSON response
    M-->>A: Content data

    A->>A: Generate explanation<br/>at learner's level
    A-->>C: Personalized explanation
    C-->>S: "Neural networks are..."

    Note over A,D: Zero LLM calls on backend
    Note over C,A: All AI in ChatGPT
```

### Flow B: Web App Quiz Flow

```mermaid
sequenceDiagram
    participant S as Student
    participant W as Web App<br/>(Next.js)
    participant B as Backend API
    participant D as Database

    S->>W: Start quiz
    W->>B: GET /api/v1/quizzes/chapter-1
    B->>D: Get quiz questions
    D-->>B: Questions + answers
    B-->>W: Quiz data

    S->>W: Submit answers
    W->>B: POST /api/v1/quizzes/submit
    B->>B: Grade with answer key<br/>(Zero-LLM)
    B->>D: Save attempt
    B->>D: Update progress
    B-->>W: Score + feedback
    W-->>S: Show results

    Note over B: Deterministic grading<br/>No LLM usage
```

### Flow C: Phase 2 Adaptive Learning (Premium)

```mermaid
sequenceDiagram
    participant S as Premium User
    participant W as Web App
    participant B as Backend API
    participant L as LLM Service
    participant C as Cost Tracker

    S->>W: View recommendations
    W->>B: GET /api/v1/adaptive/recommendations
    B->>B: Check user tier = PREMIUM

    alt ENABLE_PHASE_2_LLM=true
        B->>L: Analyze knowledge gaps
        L-->>B: Personalized plan
        B->>C: Track LLM cost
    else ENABLE_PHASE_2_LLM=false
        B->>B: Return rule-based<br/>recommendations
    end

    B-->>W: Recommendations
    W-->>S: Show learning path

    Note over B,L: Phase 2 only<br/>Premium gated
```

### Flow D: MCP Widget Rendering

```mermaid
sequenceDiagram
    participant C as ChatGPT
    participant M as MCP Server
    participant T as Tool Handler
    participant W as Widget Store

    C->>M: tools/call "get_achievements"
    M->>T: Route to handler
    T->>T: Fetch from database
    T-->>M: Response data

    T-->>M: Response with metadata:<br/>_meta.openai.outputTemplate =<br/>ui://widget/achievements.html

    M-->>C: JSON-RPC response

    C->>M: resources/read<br/>uri: ui://widget/achievements.html
    M->>W: Get widget HTML
    W-->>M: HTML content
    M-->>C: Render widget

    Note over C: Display interactive<br/>widget in UI
```

---

## Widget Integration Architecture

### Available Widgets (8 Total)

| Widget | Tool Trigger | Template URI |
|--------|--------------|--------------|
| Chapter List | `list_chapters` | `ui://widget/chapter-list.html` |
| Quiz Widget | `get_quiz` | `ui://widget/quiz.html` |
| Achievements | `get_achievements` | `ui://widget/achievements.html` |
| Streak Calendar | `get_streak_calendar` | `ui://widget/streak-calendar.html` |
| Progress Dashboard | `get_progress_summary` | `ui://widget/progress-dashboard.html` |
| Quiz Insights | `get_quiz_score_history` | `ui://widget/quiz-insights.html` |
| Adaptive Learning | `get_recommendations` | `ui://widget/adaptive-learning.html` |
| AI Mentor Chat | `chat_with_mentor` | `ui://widget/ai-mentor-chat.html` |

### Widget Metadata Structure

```json
{
  "result": {
    "achievements": [...],
    "_meta": {
      "openai": {
        "outputTemplate": "ui://widget/achievements.html"
      }
    }
  }
}
```

---

## Deployment Architecture

### Infrastructure Map

```
┌─────────────────────────────────────────────────────────┐
│                    Production Cloud                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Fly.io (Docker Container)                       │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  course-backend                            │  │  │
│  │  │  - FastAPI (uvicorn)                       │  │  │
│  │  │  - Port: 3505                              │  │  │
│  │  │  - Restart: unless-stopped                 │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │                        ↓                         │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  MCP Server (Integrated)                    │  │  │
│  │  │  - 41 Tools                                │  │  │
│  │  │  - 8 Widgets                               │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Neon (PostgreSQL)                               │  │
│  │  - Users, Progress, Quizzes, Attempts           │  │
│  │  - Connection: String-based                     │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Cloudflare R2 (S3-Compatible)                  │  │
│  │  - Chapter content (Markdown/HTML)              │  │
│  │  - Widget HTML templates                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Server: n00bi2761@92.113.147.250:3505                  │
└─────────────────────────────────────────────────────────┘
```

---

## Security & Access Control

### API Authentication Flow

```mermaid
graph LR
    A[Request] --> B{Auth Check}
    B -->|Valid JWT| C[Process Request]
    B -->|Invalid/No JWT| D[401 Unauthorized]

    C --> E{Feature Check}
    E -->|Public| F[Return Data]
    E -->|Tier-Based| G{Check Tier}

    G -->|FREE| H{Free Feature?}
    G -->|PREMIUM| I{Premium Feature?}
    G -->|PRO| J[Allow All]

    H -->|Yes| F
    H -->|No| K[403 Forbidden<br/>Upgrade Prompt]

    I -->|Yes| F
    I -->|No| K

    style A fill:#e1f5fe
    style F fill:#e8f5e9
    style K fill:#ffebee
```

---

## Performance Characteristics

### Scalability Metrics

| Metric | Phase 1 (Zero-LLM) | Phase 2 (Hybrid) | Phase 3 (Web App) |
|--------|-------------------|------------------|-------------------|
| **Concurrent Users** | 100,000+ | 10,000+ | 5,000+ |
| **API Response Time** | <100ms | 200-500ms* | <200ms |
| **Cost Per User** | $0.002-0.004/mo | $0.01-0.05/mo | $0.005-0.01/mo |
| **LLM Calls** | 0 | Limited | None (optional) |

*Phase 2 slower when LLM enabled (OpenAI API latency)

### Caching Strategy

```
┌─────────────────────────────────────────┐
│         Cache Strategy (Redis)          │
├─────────────────────────────────────────┤
│  Content: 1 hour (TTL)                  │
│  Quiz Questions: 30 minutes             │
│  Progress: 5 minutes (user-specific)    │
│  Search Results: 15 minutes             │
│  Widget HTML: Never (static)            │
└─────────────────────────────────────────┘
```

---

## Cost Analysis

### Phase 1 (Zero-LLM) - Minimum Cost

| Component | Monthly Cost | Per-User Cost (10K users) |
|-----------|-------------|---------------------------|
| Fly.io | $5-10 | $0.001 |
| Neon DB | $20-25 | $0.0025 |
| Cloudflare R2 | ~$0 | $0 |
| **Total** | **$25-35** | **$0.0035/user** |

### Phase 2 (Hybrid) - With LLM

| Component | Monthly Cost | Per-User Cost (10K users, 10% premium) |
|-----------|-------------|----------------------------------------|
| Infrastructure | $25-35 | $0.0035 |
| OpenAI API (1K users × 100 calls) | $20-30 | $0.002-0.003 |
| **Total** | **$45-65** | **~$0.006/user** |

**Cost Savings vs Human Tutor**: 85-90% reduction
**Human Tutor**: $20-50/hour × 10 hours/month = $200-500/month
**Course Companion FTE**: $0.003-0.006/month

---

## Monitoring & Observability

### Health Check Endpoints

```bash
# API Health
GET /health
Response: {"status": "healthy", "version": "1.0.0"}

# MCP Server Status
POST /api/v1/mcp
{"jsonrpc": "2.0", "id": 1, "method": "initialize"}

# Cost Tracking (Premium)
GET /api/v1/cotrary/costs/summary?user_id={uuid}
Response: { "total_cost": 0.045, "calls": 150 }
```

### Logging Strategy

```
┌──────────────────────────────────────────────────┐
│              Log Levels                          │
├──────────────────────────────────────────────────┤
│  ERROR: Failed requests, exceptions              │
│  WARNING: Access denied, feature gates           │
│  INFO: API calls, user actions                   │
│  DEBUG: LLM prompts, responses (Phase 2)         │
└──────────────────────────────────────────────────┘
```

---

## Conclusion

This architecture demonstrates a **Zero-Backend-LLM** approach for Phase 1, with **optional Phase 2 enhancements** for premium users. The design prioritizes:

1. **Cost Efficiency**: $0.002-0.004 per user per month
2. **Scalability**: 10 to 100,000+ users
3. **Flexibility**: Phase 1 compliance with optional Phase 2 features
4. **User Experience**: AI-native learning through ChatGPT
5. **Extensibility**: MCP protocol for future integrations

---

**Generated**: February 5, 2026
**Author**: Course Companion FTE Team
**Hackathon**: Panaversity Agent Factory IV
