"""
FastAPI application entry point.
Zero-Backend-LLM: All AI intelligence happens in ChatGPT, backend serves content only.
"""

from datetime import datetime
from typing import List
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.core.config import settings
from src.core.database import init_db, close_db
from src.models.schemas import HealthResponse, ErrorResponse
from src.api.sse import router as sse_router
from src.api.content import router as content_router
from src.api.quiz import router as quiz_router
from src.api.progress import router as progress_router
from src.api.access import router as access_router
from src.api.adaptive import router as adaptive_router
from src.api.quiz_llm import router as quiz_llm_router
from src.api.costs import router as costs_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Zero-Backend-LLM Course Companion API - All AI in ChatGPT",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Lifecycle Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    await close_db()


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"} if settings.debug else {"detail": "Internal server error"},
    )


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.limit("120/minute")
async def health_check(request: Request):
    """
    Health check endpoint.
    Zero-LLM compliance: Simple status check only.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
    )


# =============================================================================
# API Routes
# =============================================================================

# Include routers
app.include_router(
    content_router,
    prefix="/api/v1",
    tags=["Content"]
)

app.include_router(
    quiz_router,
    prefix="/api/v1",
    tags=["Quiz"]
)

app.include_router(
    progress_router,
    prefix="/api/v1",
    tags=["Progress"]
)

app.include_router(
    access_router,
    prefix="/api/v1",
    tags=["Access"]
)

app.include_router(
    sse_router,
    prefix="/api/v1",
    tags=["MCP", "SSE"]
)

# Phase 2: Hybrid LLM Features (Optional)
app.include_router(
    adaptive_router,
    prefix="/api/v1",
    tags=["Adaptive Learning (Phase 2)"]
)

app.include_router(
    quiz_llm_router,
    prefix="/api/v1",
    tags=["Quiz (Phase 2)"]
)

app.include_router(
    costs_router,
    prefix="/api/v1",
    tags=["Cost Tracking (Phase 2)"]
)


# =============================================================================
# Root Endpoint
# =============================================================================

@app.get("/", tags=["Root"])
@limiter.limit("60/minute")
async def root(request: Request):
    """
    Root endpoint with API information.
    Zero-LLM compliance: Static information only.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Zero-Backend-LLM Course Companion API",
        "architecture": "Backend serves content verbatim, all AI intelligence in ChatGPT",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
