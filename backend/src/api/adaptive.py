"""
Adaptive Learning API Endpoints - Phase 2.

Provides LLM-powered adaptive learning features:
- Knowledge gap analysis
- Personalized chapter recommendations
- Custom learning path generation

Only active when ENABLE_PHASE_2_LLM=true.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.config import settings
from src.models.database import User
from src.services.adaptive_service import (
    analyze_knowledge_gaps,
    recommend_next_chapter,
    generate_personalized_path,
    AdaptiveServiceError
)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


# =============================================================================
# Request/Response Models
# =============================================================================


class KnowledgeGapResponse(BaseModel):
    """Knowledge gap analysis response."""

    weak_topics: List[str] = Field(
        description="Topics where student needs improvement (<70% score)"
    )
    strong_topics: List[str] = Field(
        description="Topics where student excels (>85% score)"
    )
    recommended_review: List[str] = Field(
        description="Chapter IDs recommended for review"
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in analysis (0-1, based on data amount)"
    )
    explanation: str = Field(description="Human-readable explanation of the analysis")


class ChapterRecommendationResponse(BaseModel):
    """Personalized chapter recommendation response."""

    next_chapter_id: str = Field(description="ID of recommended next chapter")
    next_chapter_title: str = Field(description="Title of recommended next chapter")
    reason: str = Field(description="Explanation of why this chapter is recommended")
    alternative_paths: List[dict] = Field(
        description="Alternative chapter options with reasons"
    )
    estimated_completion_minutes: int = Field(
        description="Estimated time to complete the chapter"
    )
    difficulty_match: str = Field(description="How well difficulty matches student's level")


class ChapterPathItem(BaseModel):
    """Single chapter in learning path."""

    chapter_id: str = Field(description="Chapter ID")
    title: str = Field(description="Chapter title")
    order: int = Field(description="Order in path (1-based)")
    estimated_minutes: int = Field(description="Estimated completion time")
    reason: str = Field(description="Why this chapter is included")


class LearningPathMilestone(BaseModel):
    """Milestone in learning path."""

    week: int = Field(description="Week number (1-based)")
    chapters: List[str] = Field(description="Chapter IDs to complete this week")
    goal: str = Field(description="Learning goal for this week")
    total_hours: float = Field(description="Total hours needed this week")


class LearningPathRequest(BaseModel):
    """Request to generate personalized learning path."""

    learning_goals: List[str] = Field(
        description="Student's learning objectives",
        min_items=1,
        max_items=10
    )
    available_time_hours: int = Field(
        description="Hours per week available for learning",
        ge=1,
        le=40,
        default=5
    )


class LearningPathResponse(BaseModel):
    """Personalized learning path response."""

    path: List[ChapterPathItem] = Field(description="Optimized chapter sequence")
    milestones: List[LearningPathMilestone] = Field(
        description="Weekly milestones and goals"
    )
    total_hours: float = Field(description="Total hours to complete path")
    rationale: str = Field(description="Explanation of path design decisions")


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str = Field(description="Error message")
    phase_2_enabled: bool = Field(
        description="Whether Phase 2 LLM features are enabled",
        default=False
    )


# =============================================================================
# API Endpoints
# =============================================================================


async def check_premium_access(user_id: str, db: AsyncSession) -> User:
    """
    Check if user has premium tier access (PREMIUM or PRO).

    Args:
        user_id: User UUID
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If user is FREE tier
    """
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.tier == "FREE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": "Phase 2 features require Premium or Pro subscription",
                "tier": user.tier,
                "upgrade_url": "/api/v1/access/upgrade"
            }
        )

    return user


@router.get(
    "/adaptive/analysis",
    response_model=KnowledgeGapResponse,
    tags=["Adaptive Learning (Phase 2)"],
    summary="Analyze knowledge gaps from quiz performance",
    description="Uses LLM to identify weak and strong topics based on quiz history"
)
async def get_knowledge_analysis(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered knowledge gap analysis.

    Analyzes quiz performance to:
    - Identify topics where student struggles (<70% accuracy)
    - Identify topics where student excels (>85% accuracy)
    - Recommend specific chapters for review
    - Provide confidence score based on amount of data

    **Requires**: At least 1 quiz attempt taken

    **Phase 2 Feature**: Only available when ENABLE_PHASE_2_LLM=true
    """
    # Check if Phase 2 is enabled
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Phase 2 LLM features are not enabled",
                "phase_2_enabled": False
            }
        )

    # Check premium access
    await check_premium_access(str(user_id), db)

    try:
        analysis = await analyze_knowledge_gaps(str(user_id), db)
        return KnowledgeGapResponse(**analysis.to_dict())

    except AdaptiveServiceError as e:
        logger.error(f"Adaptive service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in knowledge analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze knowledge gaps"
        )


@router.get(
    "/adaptive/recommendations",
    response_model=ChapterRecommendationResponse,
    tags=["Adaptive Learning (Phase 2)"],
    summary="Get personalized chapter recommendations",
    description="Uses LLM to recommend optimal next chapter based on performance"
)
async def get_recommendations(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized chapter recommendation.

    Analyzes:
    - Recent quiz performance (higher scores = ready for harder content)
    - Current progress and completed chapters
    - Natural progression through course
    - Difficulty level matching

    Returns:
    - Next chapter to study
    - Explanation of recommendation
    - Alternative paths if student wants different focus
    - Estimated completion time
    - Difficulty match assessment

    **Phase 2 Feature**: Only available when ENABLE_PHASE_2_LLM=true
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Phase 2 LLM features are not enabled",
                "phase_2_enabled": False
            }
        )

    # Check premium access
    await check_premium_access(str(user_id), db)

    try:
        recommendation = await recommend_next_chapter(str(user_id), db)
        return ChapterRecommendationResponse(**recommendation.to_dict())

    except AdaptiveServiceError as e:
        logger.error(f"Adaptive service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


@router.post(
    "/adaptive/path",
    response_model=LearningPathResponse,
    tags=["Adaptive Learning (Phase 2)"],
    summary="Generate personalized learning path",
    description="Creates optimized chapter sequence based on goals and time constraints"
)
async def create_learning_path(
    request: LearningPathRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized learning path.

    Takes into account:
    - Student's learning goals (prioritizes relevant chapters)
    - Available time per week
    - Logical dependencies (basics before advanced)
    - Difficulty progression
    - Current progress

    Returns:
    - Optimized chapter sequence
    - Weekly milestones with goals
    - Total time commitment
    - Rationale for path design

    Example:
    ```json
    {
        "learning_goals": ["Master MCP integration", "Build reusable skills"],
        "available_time_hours": 5
    }
    ```

    **Phase 2 Feature**: Only available when ENABLE_PHASE_2_LLM=true
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Phase 2 LLM features are not enabled",
                "phase_2_enabled": False
            }
        )

    # Check premium access
    await check_premium_access(str(user_id), db)

    try:
        path = await generate_personalized_path(
            str(user_id),
            request.learning_goals,
            request.available_time_hours,
            db
        )
        return LearningPathResponse(**path.to_dict())

    except AdaptiveServiceError as e:
        logger.error(f"Adaptive service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in path generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate learning path"
        )


@router.get(
    "/adaptive/status",
    tags=["Adaptive Learning (Phase 2)"],
    summary="Check Phase 2 LLM feature status"
)
async def get_adaptive_status():
    """
    Check if Phase 2 adaptive learning features are enabled.

    Returns configuration and provider information.
    """
    # Get the correct model based on provider
    if settings.llm_provider == "openai":
        model = settings.openai_model
    elif settings.llm_provider == "anthropic":
        model = settings.anthropic_model
    elif settings.llm_provider == "glm":
        model = settings.glm_model
    else:
        model = "unknown"

    return {
        "phase_2_enabled": settings.enable_phase_2_llm,
        "llm_provider": settings.llm_provider if settings.enable_phase_2_llm else None,
        "model": model,
        "features": {
            "knowledge_gap_analysis": True,
            "chapter_recommendations": True,
            "learning_path_generation": True
        }
    }
