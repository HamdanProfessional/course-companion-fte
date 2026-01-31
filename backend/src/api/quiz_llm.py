"""
LLM-Enhanced Quiz API Endpoints - Phase 2.

Extends Phase 1 quiz API with LLM-powered grading for open-ended questions.
Only active when ENABLE_PHASE_2_LLM=true.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.core.database import get_db
from src.core.config import settings
from src.models.database import User
from src.services.quiz_llm_service import (
    grade_quiz_with_llm,
    generate_quiz_insights,
    QuizLLMServiceError
)
from src.models.database import QuizAttempt

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class LLMQuizSubmission(BaseModel):
    """Quiz submission with open-ended answers."""

    answers: Dict[str, Any] = Field(
        description="Question ID -> Answer mapping. Can be multiple choice (A/B/C/D) or open-ended text."
    )


class LLMGradedQuestionResult(BaseModel):
    """Result for LLM-graded open-ended question."""

    question_id: str = Field(description="Question ID")
    score: int = Field(description="Points earned", ge=0)
    max_score: int = Field(description="Maximum points", ge=1)
    feedback: str = Field(description="Detailed feedback")
    corrections: List[str] = Field(description="Corrections to misconceptions")
    strengths: List[str] = Field(description="What student did well")
    suggestions: List[str] = Field(description="Improvement suggestions")


class LLMQuizResult(BaseModel):
    """LLM-graded quiz result."""

    quiz_id: str = Field(description="Quiz ID")
    total_score: int = Field(description="Total points earned")
    max_score: int = Field(description="Maximum possible points")
    percentage: float = Field(description="Score percentage")
    passed: bool = Field(description="Whether student passed (>=70%)")
    multiple_choice_results: Dict[str, Dict[str, Any]] = Field(
        description="Results for multiple-choice questions"
    )
    llm_graded_results: List[LLMGradedQuestionResult] = Field(
        description="Results for LLM-graded open-ended questions"
    )
    summary: str = Field(description="Overall feedback summary")
    graded_by: str = Field(default="llm", description="Grading method")


class QuizInsightsResponse(BaseModel):
    """Quiz performance insights."""

    attempts_analyzed: int = Field(description="Number of quiz attempts analyzed")
    average_score: float = Field(description="Average score across attempts")
    improvement: float = Field(description="Score change from first to last attempt")
    trend: str = Field(description="Performance trend (improving/stable/declining)")
    strengths: List[str] = Field(description="Identified strengths")
    focus_areas: List[str] = Field(description="Areas needing improvement")
    recommendations: List[str] = Field(description="Personalized recommendations")
    encouragement: str = Field(description="Encouraging message")


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


@router.post(
    "/quizzes/{quiz_id}/grade-llm",
    response_model=LLMQuizResult,
    tags=["Quiz (Phase 2)"],
    summary="Submit quiz for LLM grading",
    description="Grade quiz with LLM-powered open-ended question evaluation"
)
async def submit_quiz_llm(
    quiz_id: str,
    submission: LLMQuizSubmission,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit quiz for LLM-powered grading.

    Supports both multiple-choice and open-ended questions:

    **Multiple Choice** (Phase 1 method):
    - Answers: A, B, C, or D
    - Grading: Rule-based (instant)
    - Points: 10 per question

    **Open-Ended** (Phase 2 LLM method):
    - Answers: Free-form text (100+ characters)
    - Grading: LLM-powered evaluation
    - Points: Up to 30 per question
    - Feedback: Detailed, personalized

    **Example Request**:
    ```json
    {
        "answers": {
            "question-id-1": "A",
            "question-id-2": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes that work together to solve specific problems...",
            "question-id-3": "B"
        }
    }
    ```

    **Response**:
    - `total_score`: Combined score from all questions
    - `passed`: True if score >= 70%
    - `multiple_choice_results`: Rule-based MC results
    - `llm_graded_results`: LLM-graded open-ended results with:
        - Detailed feedback
        - Corrections for misconceptions
        - Identified strengths
        - Improvement suggestions
    - `summary`: Personalized overall feedback

    **Benefits**:
    - Automatic partial credit for open-ended answers
    - Detailed, actionable feedback
    - Faster than manual grading
    - Consistent evaluation criteria

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
        result = await grade_quiz_with_llm(
            quiz_id,
            str(user_id),
            submission.answers,
            db
        )

        # Save attempt to database
        from src.models.database import QuizAttempt
        import uuid
        from datetime import datetime

        attempt = QuizAttempt(
            id=uuid.uuid4(),
            user_id=user_id,
            quiz_id=UUID(quiz_id),
            score=int(result.percentage),
            answers=submission.answers,
            completed_at=datetime.utcnow()
        )
        db.add(attempt)
        await db.commit()

        return LLMQuizResult(**result.to_dict())

    except QuizLLMServiceError as e:
        logger.error(f"Quiz LLM service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in LLM quiz grading: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grade quiz with LLM"
        )


@router.get(
    "/quizzes/{quiz_id}/insights",
    response_model=QuizInsightsResponse,
    tags=["Quiz (Phase 2)"],
    summary="Get quiz performance insights",
    description="AI analyzes quiz attempts to provide learning insights"
)
async def get_quiz_insights(
    quiz_id: str,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered insights from quiz performance.

    Analyzes:
    - Progress over multiple attempts
    - Performance trends (improving/stable/declining)
    - Consistent strengths
    - Areas needing focus
    - Personalized recommendations

    **Requirements**:
    - At least 2 quiz attempts taken
    - Phase 2 LLM features enabled

    **Use Cases**:
    - Track learning progress over time
    - Identify knowledge gaps
    - Get personalized study recommendations
    - Understand learning patterns

    **Response**:
    - `average_score`: Mean score across all attempts
    - `improvement`: Score change from first to last attempt
    - `trend`: Performance trajectory
    - `strengths`: Topics consistently done well
    - `focus_areas`: Topics needing improvement
    - `recommendations`: Personalized study suggestions
    - `encouragement`: Motivational message

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
        # Get user's attempts for this quiz
        result = await db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.quiz_id == UUID(quiz_id))
            .order_by(QuizAttempt.completed_at)
        )
        attempts = result.scalars().all()

        if not attempts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No quiz attempts found for this user"
            )

        insights = await generate_quiz_insights(quiz_id, list(attempts), db)
        return QuizInsightsResponse(**insights)

    except QuizLLMServiceError as e:
        logger.error(f"Quiz LLM service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in quiz insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate insights"
        )


@router.get(
    "/quizzes/llm/status",
    tags=["Quiz (Phase 2)"],
    summary="Check LLM quiz grading status"
)
async def get_quiz_llm_status():
    """Check if LLM quiz grading features are enabled."""
    return {
        "phase_2_enabled": settings.enable_phase_2_llm,
        "llm_provider": settings.llm_provider if settings.enable_phase_2_llm else None,
        "llm_model": settings.openai_model if settings.llm_provider == "openai" else settings.anthropic_model,
        "features": {
            "llm_grading": True,
            "open_ended_questions": True,
            "performance_insights": True
        }
    }
