"""
API v3: Unified Phase 3 Tutor API.

This API consolidates all features (content, quiz, progress, LLM features)
into a single unified endpoint structure for the Phase 3 Web Application.

Key Design:
- Single entry point: /api/v3/tutor/
- LLM features enabled by default (Phase 3)
- Backward compatible with v1 endpoints
- Structured by domain: content, quizzes, progress, ai, access, tips, leaderboard, certificates
"""

from fastapi import APIRouter
from .tutor import router as tutor_router
from .certificate import verify as certificate_verify_router

# Create v3 router
router = APIRouter()

# Include unified tutor router
router.include_router(
    tutor_router,
    prefix="/tutor",
    tags=["Tutor API v3 (Phase 3)"]
)

# Include public certificate verification router (no auth required)
router.include_router(
    certificate_verify_router.router,
    prefix="/certificate",
    tags=["Certificate Verification (Public)"]
)
