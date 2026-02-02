"""
AI Features Router - Phase 3 Unified API

Consolidates all AI-powered features:
- Adaptive learning recommendations
- AI mentor Q&A
- LLM quiz grading
- Content generation and explanation
- Knowledge gap analysis

Path: /api/v3/tutor/ai
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.config import settings
from src.services.adaptive_service import (
    analyze_knowledge_gaps,
    recommend_next_chapter,
    generate_personalized_path,
    AdaptiveServiceError
)
from src.services.mentor_service import MentorService, MentorServiceError
from src.models.database import User
from src.models.schemas import ChapterDetail

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Enums and Models
# =============================================================================


class MentorMessageRole(str, Enum):
    """Message role types."""
    user = "user"
    assistant = "assistant"
    system = "system"


class MentorMessage(BaseModel):
    """Chat message."""
    role: MentorMessageRole
    content: str
    timestamp: Optional[str] = None


class AdaptiveAnalysis(BaseModel):
    """Knowledge gap analysis result."""
    weak_topics: List[str]
    strong_topics: List[str]
    recommended_review: List[str]
    confidence_score: float
    explanation: str


class ChapterRecommendation(BaseModel):
    """Personalized chapter recommendation."""
    next_chapter_id: str
    next_chapter_title: str
    reason: str
    alternative_paths: List[Dict[str, Any]]
    estimated_completion_minutes: int
    difficulty_match: str


class LearningPathRequest(BaseModel):
    """Request for personalized learning path."""
    learning_goals: List[str] = Field(..., min_items=1, max_items=10)
    available_time_hours: int = Field(default=5, ge=1, le=40)
    focus_areas: Optional[List[str]] = None


class LearningPathResponse(BaseModel):
    """Personalized learning path."""
    path: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    total_hours: float
    rationale: str


class MentorChatRequest(BaseModel):
    """Mentor chat request."""
    question: str = Field(..., min_length=5, description="Question to ask the AI mentor")
    chapter_context: Optional[str] = None
    conversation_history: Optional[List[MentorMessage]] = None


class MentorChatResponse(BaseModel):
    """Mentor chat response."""
    answer: str
    follow_up_questions: List[str]
    related_chapters: List[str]
    confidence: float


class ContentExplanationRequest(BaseModel):
    """Request for content explanation."""
    chapter_id: str
    topic: str
    complexity_level: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    include_examples: bool = True


class ContentExplanationResponse(BaseModel):
    """Content explanation response."""
    explanation: str
    examples: List[str]
    analogies: List[str]
    key_points: List[str]
    difficulty_level: str


class QuizGradingRequest(BaseModel):
    """Request for LLM quiz grading."""
    quiz_id: str
    answers: Dict[str, Any] = Field(..., description="Question ID -> Answer (text or choice)")
    question_contexts: Optional[Dict[str, str]] = None


# =============================================================================
# Helper Functions
# =============================================================================


async def verify_premium_access(user_id: UUID, db: AsyncSession) -> User:
    """Verify user has premium access for AI features."""
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
                "detail": "AI features require Premium or Pro subscription",
                "tier": user.tier,
                "upgrade_url": "/api/v3/tutor/access/upgrade"
            }
        )

    return user


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/status")
async def get_ai_status():
    """
    Check AI features status and configuration.

    Returns information about available AI features and configuration.
    """
    # Determine model based on provider
    if settings.llm_provider == "openai":
        model = settings.openai_model
    elif settings.llm_provider == "anthropic":
        model = settings.anthropic_model
    elif settings.llm_provider == "glm":
        model = settings.glm_model
    else:
        model = "unknown"

    return {
        "phase": "Phase 3 - Full LLM Integration",
        "llm_enabled": settings.enable_phase_2_llm,
        "llm_provider": settings.llm_provider if settings.enable_phase_2_llm else None,
        "model": model,
        "features": {
            "adaptive_learning": True,
            "ai_mentor": True,
            "llm_quiz_grading": True,
            "content_explanation": True,
            "knowledge_analysis": True,
            "personalized_paths": True
        },
        "requirements": {
            "adaptive_learning": "Premium tier",
            "ai_mentor": "Premium tier",
            "llm_quiz_grading": "Premium tier",
            "content_explanation": "Free tier (basic), Premium (advanced)"
        }
    }


@router.get("/adaptive/analysis", response_model=AdaptiveAnalysis)
async def get_knowledge_analysis(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze knowledge gaps from quiz performance.

    Uses AI to identify:
    - Weak topics (below 70% accuracy)
    - Strong topics (above 85% accuracy)
    - Recommended chapters for review
    - Confidence score based on data amount

    **Phase 3 Feature**: Available to all premium users.
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        await verify_premium_access(user_id, db)

        analysis = await analyze_knowledge_gaps(str(user_id), db)

        return AdaptiveAnalysis(
            weak_topics=analysis.weak_topics,
            strong_topics=analysis.strong_topics,
            recommended_review=analysis.recommended_review,
            confidence_score=analysis.confidence_score,
            explanation=analysis.explanation
        )

    except HTTPException:
        raise
    except AdaptiveServiceError as e:
        logger.error(f"Adaptive service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in knowledge analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze knowledge gaps"
        )


@router.get("/adaptive/recommendations", response_model=ChapterRecommendation)
async def get_recommendations(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized chapter recommendations.

    Analyzes:
    - Recent quiz performance
    - Current progress
    - Natural progression
    - Difficulty matching

    **Phase 3 Feature**: Smart recommendations for premium users.
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        await verify_premium_access(user_id, db)

        recommendation = await recommend_next_chapter(str(user_id), db)

        return ChapterRecommendation(
            next_chapter_id=recommendation.next_chapter_id,
            next_chapter_title=recommendation.next_chapter_title,
            reason=recommendation.reason,
            alternative_paths=recommendation.alternative_paths,
            estimated_completion_minutes=recommendation.estimated_completion_minutes,
            difficulty_match=recommendation.difficulty_match
        )

    except HTTPException:
        raise
    except AdaptiveServiceError as e:
        logger.error(f"Adaptive service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


@router.post("/adaptive/path", response_model=LearningPathResponse)
async def create_learning_path(
    request: LearningPathRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized learning path.

    Creates an optimized chapter sequence based on:
    - Learning goals
    - Available time per week
    - Logical dependencies
    - Difficulty progression
    - Current progress

    **Phase 3 Feature**: AI-powered learning paths.
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        await verify_premium_access(user_id, db)

        path = await generate_personalized_path(
            str(user_id),
            request.learning_goals,
            request.available_time_hours,
            db
        )

        return LearningPathResponse(
            path=[p.model_dump() if hasattr(p, 'model_dump') else p for p in path.path],
            milestones=[m.model_dump() if hasattr(m, 'model_dump') else m for m in path.milestones],
            total_hours=path.total_hours,
            rationale=path.rationale
        )

    except HTTPException:
        raise
    except AdaptiveServiceError as e:
        logger.error(f"Adaptive service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating learning path: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate learning path"
        )


@router.post("/mentor/chat", response_model=MentorChatResponse)
async def mentor_chat(
    request: MentorChatRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with AI mentor for conceptual Q&A.

    The AI mentor:
    - Understands course context
    - Provides detailed explanations
    - Asks follow-up questions
    - Suggests relevant chapters
    - Adapts to user's level

    **Phase 3 Feature**: Interactive AI tutoring.

    Example question:
    ```
    "Can you explain how MCP servers work and how they connect to ChatGPT?"
    ```
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        # Premium check can be optional for basic mentor features
        user = await verify_premium_access(user_id, db)

        # Convert conversation history
        history = []
        if request.conversation_history:
            for msg in request.conversation_history:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Get mentor service
        mentor_service = MentorService(db)

        # Get answer from mentor
        response = await mentor_service.answer_question(
            user_id=str(user_id),
            question=request.question,
            chapter_context=request.chapter_context,
            conversation_history=history
        )

        return MentorChatResponse(
            answer=response.get("answer", ""),
            follow_up_questions=response.get("follow_up_questions", []),
            related_chapters=response.get("related_chapters", []),
            confidence=response.get("confidence", 0.8)
        )

    except HTTPException:
        raise
    except MentorServiceError as e:
        logger.error(f"Mentor service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in mentor chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get mentor response"
        )


@router.post("/explain", response_model=ContentExplanationResponse)
async def explain_content(
    request: ContentExplanationRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated explanation for a topic.

    Provides:
    - Clear explanation at requested complexity
    - Real-world examples
    - Helpful analogies
    - Key points summary

    **Phase 3 Feature**: Personalized content explanations.

    Complexity levels:
    - `beginner`: Simple language, lots of examples
    - `intermediate`: Balanced (default)
    - `advanced`: Technical depth, nuanced
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        # Get user for tier check
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        # Free users get basic explanations, premium get detailed
        if user and user.tier == "FREE":
            # Simplified response for free users
            return ContentExplanationResponse(
                explanation=f"This is a basic explanation of {request.topic}. For detailed explanations with examples and analogies, please upgrade to Premium.",
                examples=[],
                analogies=[],
                key_points=[],
                difficulty_level=request.complexity_level
            )

        # Get chapter content for context
        from src.services.content_service import ContentService
        content_service = ContentService(db)
        chapter = await content_service.get_chapter_content(request.chapter_id)

        context = chapter.content if chapter else None

        # Generate explanation using mentor service
        mentor_service = MentorService(db)
        explanation = await mentor_service.explain_topic(
            topic=request.topic,
            context=context,
            complexity_level=request.complexity_level,
            include_examples=request.include_examples
        )

        return ContentExplanationResponse(
            explanation=explanation.get("explanation", ""),
            examples=explanation.get("examples", []),
            analogies=explanation.get("analogies", []),
            key_points=explanation.get("key_points", []),
            difficulty_level=request.complexity_level
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate explanation"
        )


@router.post("/quiz/grade-llm")
async def grade_quiz_with_ai(
    request: QuizGradingRequest,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Grade quiz using LLM for detailed feedback.

    Supports:
    - Open-ended text answers
    - Partial credit scoring
    - Detailed feedback
    - Improvement suggestions

    **Phase 3 Feature**: AI-powered quiz grading.

    This is an alias to the quizzes endpoint with LLM mode enabled.
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        await verify_premium_access(user_id, db)

        from src.services.quiz_llm_service import grade_quiz_with_llm

        result = await grade_quiz_with_llm(
            request.quiz_id,
            str(user_id),
            request.answers,
            db
        )

        return {
            "quiz_id": request.quiz_id,
            "total_score": result.total_score,
            "max_score": result.max_score,
            "percentage": result.percentage,
            "passed": result.passed,
            "llm_graded_results": result.llm_graded_results,
            "summary": result.summary,
            "graded_by": "llm_phase_3"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM grading: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grade quiz with LLM"
        )


@router.get("/usage/costs")
async def get_llm_usage_costs(
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get LLM usage costs for a user (admin/monitoring).

    **Phase 3 Feature**: Cost tracking and monitoring.
    """
    try:
        # Check if user is admin
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or user.tier != "PRO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cost tracking is only available to Pro users"
            )

        from src.services.cost_tracking_service import CostTrackingService

        cost_service = CostTrackingService(db)
        costs = await cost_service.get_user_costs(str(user_id))

        return {
            "user_id": str(user_id),
            "total_requests": costs.get("total_requests", 0),
            "total_cost_usd": costs.get("total_cost_usd", 0.0),
            "cost_breakdown": costs.get("cost_breakdown", {}),
            "average_cost_per_request": costs.get("average_cost_per_request", 0.0),
            "period": "all_time"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting usage costs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage costs"
        )
