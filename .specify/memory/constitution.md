# Course Companion FTE Constitution

<!--
Sync Impact Report:
Version: 1.0.0
Ratified: 2026-01-28
Last Amended: 2026-01-28

Modified Principles: N/A (initial version)
Added Sections:
- Core Principles
- Architecture Standards
- Development Standards
- Quality Gates

Templates Updated:
- ✅ constitution.md (this file)
- ✅ All templates aligned with Zero-Backend-LLM architecture

Follow-up TODOs: None
-->

## Core Principles

### I. Zero-Backend-LLM First (NON-NEGOTIABLE)

**Phase 1 backend MUST NOT contain LLM API calls**. All AI intelligence happens in ChatGPT using the Course Companion FTE agent. Backend is purely deterministic - serving content, tracking progress, enforcing rules.

**Rationale**: This ensures near-zero marginal cost per user, scalability to 100k+ users, and 85-90% cost reduction vs human tutors. Hybrid intelligence (Phase 2) must be selective, justified, and premium-gated.

**Enforcement**: Any Phase 1 backend code containing LLM API calls results in immediate disqualification from hackathon.

### II. Spec-Driven Development

All features start as specifications (spec.md) written by humans, then manufactured into code by general agents (Claude Code), then delivered by custom agents (Course Companion FTE).

**Rationale**: If you can describe the excellence you want, AI can build the Digital FTE to deliver it. Your spec is your source code.

### III. Educational Excellence First

Every feature must prioritize educational value over technical complexity. Tutor must: explain at learner's level, celebrate effort, maintain motivation, and adapt tone.

**Rationale**: Digital FTE must maintain 99%+ consistency in educational delivery and provide better learning outcomes than human tutoring.

### IV. Progressive Enhancement

Start with Zero-Backend-LLM (Phase 1), add Hybrid Intelligence only where demonstrably valuable (Phase 2), build standalone Web App (Phase 3). Each phase must be production-complete.

**Rationale**: Ensures cost efficiency, validates hybrid value with data, and provides multiple access paths (ChatGPT + Web).

### V. Cost-Efficiency by Design

Default to serverless, pay-as-you-go services. Optimize for $0.002-0.004 per user per month. Scale infrastructure elastically from 10 to 100,000 users without linear cost increase.

**Rationale**: 99% cost reduction vs human tutors requires aggressive cost discipline. Every architectural decision must be cost-justified.

### VI. Agent Skills as Procedural Knowledge

Runtime skills (concept-explainer, quiz-master, socratic-tutor, progress-motivator) contain all procedural knowledge for educational tasks. Skills load dynamically based on student intent.

**Rationale**: Skills enable instant ramp-up (no weeks of training), consistent quality (99%+), and easy updates to teaching methodology.

## Architecture Standards

### Zero-Backend-LLM Backend Requirements

**ALLOWED** in Phase 1 backend:
- Content APIs (serve course material verbatim)
- Navigation APIs (return next/previous chapters)
- Quiz APIs (rule-based grading with answer keys)
- Progress APIs (track completion, streaks, last activity)
- Search APIs (keyword and semantic search)
- Access Control APIs (freemium gating, tier management)

**FORBIDDEN** in Phase 1 backend:
- LLM API calls (OpenAI, Anthropic, etc.)
- RAG summarization (LLM inference)
- Prompt orchestration (LLM inference)
- Agent loops (must run in ChatGPT)
- Content generation (pre-generate and store only)

### Hybrid Intelligence Requirements (Phase 2)

Hybrid features MUST be:
- Feature-scoped (limited to specific premium features)
- User-initiated (user explicitly requests)
- Premium-gated (paid users only)
- Isolated (separate API routes: `/api/v2/hybrid/*`)
- Cost-tracked (monitor per-user LLM costs)

Maximum 2 hybrid features. Must justify why zero-LLM cannot deliver equivalent value.

### Agent Factory Architecture

Follow 8-layer architecture:
- L3: FastAPI (HTTP interface) - Phase 1, 2, 3
- L6: Runtime Skills + MCP (domain knowledge + tools) - Phase 1, 2, 3
- L4, L5: Agent SDKs (orchestration + execution) - Phase 2, 3
- L0, L1, L2: Infrastructure (sandbox, events, durability) - Phase 2, 3

## Development Standards

### Technology Stack

**Backend**: FastAPI (Python 3.11+), SQLAlchemy, Pydantic
**Database**: PostgreSQL (Neon serverless)
**Storage**: Cloudflare R2 (course content, media)
**ChatGPT Frontend**: OpenAI Apps SDK
**Web Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
**Hosting**: Fly.io (backend), Vercel (web)
**CI/CD**: GitHub Actions

### Code Quality

- Type hints on all functions (Python typing)
- Pydantic models for all request/response validation
- Async/await for I/O operations
- Proper error handling with HTTPException
- Docstrings on all endpoints
- Test coverage >80% for critical paths

### Testing Discipline

**Unit Tests**: Test individual functions, services, models in isolation
**Integration Tests**: Test API endpoints, database interactions
**Contract Tests**: Test API contracts (OpenAPI schema validation)
**Load Tests**: Verify performance under expected concurrent load (100+ users)

### Security Standards

- JWT-based authentication
- Password hashing (bcrypt)
- Rate limiting on all endpoints (60 requests/minute default)
- Input validation and sanitization
- SQL injection prevention (use ORM)
- XSS protection (sanitize user content)
- CORS configuration
- HTTPS only in production
- Environment variable secrets management

### Documentation Standards

- README.md with project overview, setup instructions, architecture diagram
- API documentation (OpenAPI/Swagger) for all endpoints
- Architecture diagram showing Zero-Backend-LLM flow
- Cost analysis document (monthly per-user costs)
- Demo video (5 minutes) showing both ChatGPT App and Web App

## Quality Gates

### Phase 1 Gates

1. **Zero-LLM Verification**: Code review + API audit must confirm ZERO LLM API calls in backend
2. **Feature Completeness**: All 6 required features implemented and functional
3. **ChatGPT App Quality**: UX testing in actual ChatGPT environment
4. **Cost Efficiency**: Monthly cost <$41 for 10K users ($0.004 per user max)
5. **Progress Tracking**: Data persists across sessions
6. **Freemium Gate**: Access control functional for free vs premium tiers

### Phase 2 Gates

1. **Hybrid Feature Value**: Demo + justification document showing clear educational value
2. **Cost Justification**: Cost analysis document showing per-user LLM costs
3. **Architecture Separation**: Code review confirming isolated `/api/v2/hybrid/*` routes
4. **Premium Gating**: Functional testing confirming free users cannot access hybrid features
5. **Cost Tracking**: Monitoring in place for per-user LLM token usage

### Phase 3 Gates

1. **Web Functionality**: All 6 required features working in web interface
2. **Responsive Design**: Works on desktop, tablet, mobile
3. **Progress Persistence**: Data syncs correctly between ChatGPT App and Web App
4. **API Integration**: Single consolidated backend serves both frontends

## Governance

### Amendment Process

1. Propose amendment with rationale (why change needed)
2. Document impact on existing principles and templates
3. Update constitution with new version (semantic versioning)
4. Propagate changes to all dependent templates (plan, spec, tasks)
5. Require team consensus for MAJOR version changes

### Versioning Policy

- **MAJOR**: Backward incompatible principle removals or redefinitions (e.g., allowing LLM in Phase 1 backend)
- **MINOR**: New principle or section added, materially expanded guidance
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

### Compliance Review

All pull requests must:
- Verify Zero-Backend-LLM compliance (no LLM in Phase 1 backend)
- Check cost efficiency implications
- Validate educational quality standards
- Confirm agent skills are loaded and used correctly

Use runtime guidance files for development:
- `.claude/README.md` - Agent and skills overview
- `CLAUDE.md` - Project-specific rules and SDD workflow
- `Requirements.md` - Hackathon requirements and judging criteria

**Version**: 1.0.0 | **Ratified**: 2026-01-28 | **Last Amended**: 2026-01-28
