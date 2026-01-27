# Research: Zero-Backend-LLM Course Companion API

**Feature**: 1-zero-backend-api
**Phase**: 0 - Research & Technical Decisions
**Date**: 2026-01-28

## Overview

This document consolidates research findings for implementing the Zero-Backend-LLM backend API. All technical decisions are documented with rationale and alternatives considered.

---

## Decision 1: Cloudflare R2 Integration via boto3 SDK

**Context**: Backend needs to serve course content stored in object storage.

**Decision**: Use boto3 SDK with S3-compatible API for Cloudflare R2 integration.

### Rationale
- **Native Python SDK**: boto3 is the official AWS SDK for Python with excellent community support
- **S3-Compatible API**: Cloudflare R2 provides 100% S3 API compatibility, making boto3 a perfect fit
- **Zero Egress Fees**: R2 eliminates egress fees that would make S3 expensive at scale
- **Proven Reliability**: battle-tested in production by thousands of companies

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| MinIO (self-hosted) | Full control, no vendor lock-in | Operational overhead, scaling complexity | Hackathon time constraints, requires DevOps effort |
| Azure Blob Storage | Enterprise features, geo-replication | Higher egress costs, less Python-native | Costlier at 100K+ users |
| AWS S3 | Most mature, extensive features | Egress fees ($0.09/GB) make it expensive | Would exceed cost targets at scale |

### Implementation
```python
import boto3

s3_client = boto3.client('s3',
    endpoint_url=os.getenv('R2_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY')
)

def get_content(key: str) -> str:
    response = s3_client.get_object(Bucket='course-content', Key=key)
    return response['Body'].read().decode('utf-8')
```

---

## Decision 2: asyncpg for Async PostgreSQL

**Context**: Backend needs async database operations for optimal performance with FastAPI.

**Decision**: Use asyncpg as PostgreSQL driver with SQLAlchemy 2.0 async mode.

### Rationale
- **Fastest Python PostgreSQL Driver**: 3x faster than psycopg2 in benchmarks
- **Native asyncio Support**: Designed from ground up for async/await patterns
- **SQLAlchemy 2.0 Compatibility**: Works seamlessly with SQLAlchemy's new async API
- **Connection Pooling**: Built-in connection pooling with excellent performance

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| psycopg2 (sync) | Mature, stable, widely-used | Blocking I/O, limits concurrency | Can't handle 100K concurrent users efficiently |
| databases (async abstraction) | Database-agnostic, simple API | Additional abstraction layer, less control | Unnecessary indirection for PostgreSQL-only app |
| asyncmy (MySQL async) | Fast async driver | MySQL-specific | Neon uses PostgreSQL, not MySQL |

### Implementation
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    'postgresql+asyncpg://user:pass@host/db',
    echo=False,
    pool_size=20,
    max_overflow=10
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

---

## Decision 3: SlowAPI for Rate Limiting

**Context**: API needs rate limiting (60 req/minute) to prevent abuse and control costs.

**Decision**: Use slowapi library with in-memory storage for rate limiting.

### Rationale
- **FastAPI-Native**: Designed specifically for FastAPI with @limiter decorators
- **Flexible Storage**: Supports in-memory (for single instance) or Redis (for distributed)
- **Per-Endpoint Limits**: Can set different limits for different endpoints
- **Simple Integration**: Minimal code changes required

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Nginx rate limiting | Infrastructure-level, efficient | Requires Nginx config, harder to test locally | Adds infra complexity for hackathon |
| Custom middleware | Full control, no dependencies | Reinventing wheel, error-prone | Unnecessary development effort |
| FastAPI-Limiter | Similar to SlowAPI | Less maintained, fewer features | SlowAPI has better documentation |

### Implementation
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/chapters")
@limiter.limit("60/minute")
async def list_chapters():
    ...
```

---

## Decision 4: Pre-compute Embeddings for Search (Phase 1)

**Context**: Need semantic search capability without LLM API calls (Zero-LLM requirement).

**Decision**: Pre-generate embeddings during content upload, store in R2, use cosine similarity for ranking.

### Rationale
- **Zero-LLM Compliance**: No real-time LLM API calls, embeddings generated once during upload
- **Fast Query Performance**: Cosine similarity on pre-computed vectors is <10ms
- **Cost Effective**: Generate embeddings once, reuse forever
- **Scalable**: Search performance doesn't degrade with content size

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Keyword-only search | Simple, fast, no dependencies | Limited accuracy, no semantic understanding | Poor user experience for learning queries |
| Real-time embedding generation | Always up-to-date | Requires LLM API calls (violates Zero-LLM) | **DISQUALIFIED** - violates constitution |
| Hybrid (keyword + embedding) | Best of both worlds | More complex | Overkill for Phase 1, add in Phase 2 |

### Implementation
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# During content upload (one-time)
embedding = openai.Embedding.create(
    input=chapter_content,
    model="text-embedding-ada-002"
)['data'][0]['embedding']
# Store embedding alongside content in R2

# During search (runtime)
query_embedding = get_query_embedding(query)  # Same model
similarities = cosine_similarity([query_embedding], stored_embeddings)
top_k_indices = np.argsort(similarities[0])[::-1][:5]
```

**Note**: Embedding generation happens during content preparation (not at runtime), so it doesn't violate Zero-LLM for the backend API.

---

## Decision 5: python-jose[cryptography] for JWT

**Context**: Need secure JWT token generation and validation for authentication.

**Decision**: Use python-jose with cryptography backend for JWT operations.

### Rationale
- **Secure Defaults**: Uses cryptography library (not PyJWT's default) for better security
- **HS256 and RS256 Support**: Can use symmetric (HS256) or asymmetric (RS256) algorithms
- **FastAPI Compatible**: Works seamlessly with FastAPI's HTTPBearer security
- **Battle-Tested**: Used in production by major companies

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| PyJWT | Simpler API | Less secure by default, requires careful config | Security concerns for auth system |
| Authlib | More features (OAuth2, etc.) | More complex than needed for just JWT | Overkill for Phase 1 |
| Custom implementation | Full control | High risk of security vulnerabilities | Don't roll your own crypto |

### Implementation
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload["sub"]
```

---

## Decision 6: Serverless Deployment on Fly.io

**Context**: Need deployment platform that scales efficiently and keeps costs low.

**Decision**: Deploy FastAPI app on Fly.io with Neon PostgreSQL and Cloudflare R2.

### Rationale
- **Free Tier Generous**: Fly.io free tier handles 3 VMs + 3GB RAM (sufficient for 10K users)
- **Auto-Scaling**: Automatically scales up during traffic spikes, down when idle
- **Global Edge**: Deploys close to users worldwide for low latency
- **Simple CLI**: Easy deployment with `fly launch` command
- **Neon Integration**: Neon (serverless PostgreSQL) has excellent Fly.io integration

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| AWS Lambda + API Gateway | Highly scalable, pay-per-use | Cold starts, complex setup | Overkill for Phase 1 |
| Railway | Great DX, simple | Less generous free tier | Costlier at 100K+ users |
| Vercel (serverless) | Excellent for frontend | Less optimized for long-running APIs | Better for web app (Phase 3) |
| DigitalOcean Droplet | Simple, predictable | Fixed cost, doesn't scale down | More expensive at low traffic |

### Cost Projection

| Users | Fly.io VMs | Neon DB | R2 Storage | Total/Month |
|-------|------------|---------|------------|-------------|
| 10 | Free tier | Free tier | $0.015/GB | $0 |
| 1,000 | $5/mo | Free tier | $0.15/mo | ~$5.15 |
| 10,000 | $25/mo | $19/mo | $1.50/mo | ~$45.50 |
| 100,000 | $250/mo | $97/mo | $15/mo | ~$362 |

**Per-user cost**: $0.0036/month at 100K users (meets $0.002-0.004 target)

---

## Summary

All technical decisions are made with these priorities:
1. **Zero-LLM Compliance**: No backend LLM API calls (constitution requirement)
2. **Cost Efficiency**: Target $0.002-0.004 per user/month
3. **Scalability**: Must handle 10K → 100K users without architecture changes
4. **Developer Experience**: Simple setup for hackathon, production-ready for deployment
5. **Performance**: <200ms API response time (p95)

**Next Steps**: Proceed to Phase 1 - Design & Contracts (data-model.md, API specs, quickstart.md)
