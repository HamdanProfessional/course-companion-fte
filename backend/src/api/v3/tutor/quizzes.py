"""
Quizzes Router - Phase 3 Unified API

Handles all quiz-related operations:
- Get quiz by chapter
- Submit quiz answers
- Rule-based grading (Phase 1)
- LLM-powered grading (Phase 3)
- Quiz insights and analytics

Path: /api/v3/tutor/quizzes
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.config import settings
from src.services.quiz_service import QuizService
from src.services.quiz_llm_service import grade_quiz_with_llm, generate_quiz_insights, QuizLLMServiceError
from src.models.database import Quiz, Question, QuizAttempt, User
from src.models.schemas import QuizWithQuestions, Question as QuestionSchema

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class QuestionItem(BaseModel):
    """Question item in quiz."""
    id: str
    question_text: str
    options: Dict[str, str]
    order: int
    type: str = "multiple_choice"  # multiple_choice or open_ended


class QuizDetail(BaseModel):
    """Quiz detail response."""
    id: str
    chapter_id: str
    title: str
    difficulty: str
    questions: List[QuestionItem]
    total_questions: int
    passing_score: int = 70


class QuizSubmission(BaseModel):
    """Quiz submission with answers."""
    answers: Dict[str, Any] = Field(
        description="Question ID -> Answer mapping (A/B/C/D or text for open-ended)"
    )
    grading_mode: str = Field(
        default="auto",
        description="Grading mode: 'auto' (rule-based), 'llm' (AI grading), or 'hybrid'"
    )


class QuestionResult(BaseModel):
    """Result for a single question."""
    question_id: str
    question_text: str
    selected_answer: str
    correct_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    points_earned: int
    max_points: int
    explanation: Optional[str] = None
    feedback: Optional[str] = None


class QuizGradingResult(BaseModel):
    """Quiz grading result."""
    quiz_id: str
    attempt_id: str
    total_score: int
    max_score: int
    percentage: float
    passed: bool
    grading_mode: str
    results: List[QuestionResult]
    summary: str
    completed_at: datetime


class QuizInsights(BaseModel):
    """Quiz performance insights."""
    attempts_analyzed: int
    average_score: float
    best_score: int
    improvement: float
    trend: str
    strengths: List[str]
    focus_areas: List[str]
    recommendations: List[str]
    encouragement: str


class QuizHistoryItem(BaseModel):
    """Single quiz attempt in history."""
    attempt_id: str
    quiz_id: str
    score: int
    passed: bool
    completed_at: datetime


# =============================================================================
# Helper Functions
# =============================================================================


async def check_quiz_access(quiz_id: str, user_id: UUID, db: AsyncSession) -> Quiz:
    """Check if user can access quiz (exists and has access)."""
    result = await db.execute(
        select(Quiz).where(Quiz.id == UUID(quiz_id))
    )
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {quiz_id} not found"
        )

    # Check if chapter requires premium access
    from src.services.content_service import ContentService
    content_service = ContentService(db)
    chapter = await content_service.get_chapter_content(str(quiz.chapter_id))

    if chapter and chapter.order >= 4:
        # Check user tier
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user and user.tier == "FREE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "detail": "Premium subscription required for this quiz",
                    "tier": user.tier,
                    "required_chapter_order": chapter.order
                }
            )

    return quiz


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/by-chapter/{chapter_id}", response_model=QuizDetail)
async def get_quiz_by_chapter(
    chapter_id: str,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get quiz for a specific chapter.

    Returns the complete quiz with all questions.
    Does not include correct answers (to prevent cheating).

    **Phase 3 Enhancement**: Includes question types and metadata.
    """
    try:
        result = await db.execute(
            select(Quiz).where(Quiz.chapter_id == UUID(chapter_id))
        )
        quiz = result.scalar_one_or_none()

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No quiz found for chapter {chapter_id}"
            )

        # Get questions
        result = await db.execute(
            select(Question)
            .where(Question.quiz_id == quiz.id)
            .order_by(Question.order)
        )
        questions = result.scalars().all()

        # Transform to response format (without correct answers)
        question_items = []
        for q in questions:
            question_items.append(QuestionItem(
                id=str(q.id),
                question_text=q.question_text,
                options=q.options,
                order=q.order,
                type="multiple_choice"
            ))

        return QuizDetail(
            id=str(quiz.id),
            chapter_id=str(quiz.chapter_id),
            title=quiz.title,
            difficulty=quiz.difficulty.value,
            questions=question_items,
            total_questions=len(question_items),
            passing_score=70
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quiz"
        )


@router.post("/{quiz_id}/submit", response_model=QuizGradingResult)
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit quiz for grading.

    Supports three grading modes:

    1. **auto** (default): Rule-based grading for multiple choice
       - Fast, deterministic
       - 10 points per question
       - No detailed feedback

    2. **llm**: AI-powered grading with detailed feedback
       - Requires premium subscription
       - Supports open-ended answers
       - Up to 30 points per question
       - Detailed explanations and suggestions

    3. **hybrid**: Rule-based MC + LLM for open-ended
       - Best of both worlds
       - Partial credit for nuanced answers

    **Phase 3 Enhancement**: LLM grading is the default for premium users.
    """
    try:
        # Check access
        await check_quiz_access(quiz_id, user_id, db)

        # Get quiz and questions
        result = await db.execute(
            select(Quiz).where(Quiz.id == UUID(quiz_id))
        )
        quiz = result.scalar_one_or_none()

        result = await db.execute(
            select(Question)
            .where(Question.quiz_id == quiz.id)
            .order_by(Question.order)
        )
        questions = result.scalars().all()

        # Determine grading mode
        grading_mode = submission.grading_mode

        # Use LLM if requested and enabled (Phase 3 default is enabled)
        use_llm = grading_mode in ["llm", "hybrid"] and settings.enable_phase_2_llm

        if use_llm:
            # Check premium access for LLM features
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if user.tier == "FREE":
                # Downgrade to auto for free users
                grading_mode = "auto"
                use_llm = False

        # Grade the quiz
        if use_llm:
            # Use LLM grading service
            llm_result = await grade_quiz_with_llm(
                quiz_id,
                str(user_id),
                submission.answers,
                db
            )

            # Create attempt record
            attempt_id = uuid.uuid4()
            attempt = QuizAttempt(
                id=attempt_id,
                user_id=user_id,
                quiz_id=UUID(quiz_id),
                score=int(llm_result.percentage),
                answers=submission.answers,
                completed_at=datetime.utcnow()
            )
            db.add(attempt)
            await db.commit()

            # Transform results
            results = []
            for q_result in llm_result.llm_graded_results:
                results.append(QuestionResult(
                    question_id=q_result.question_id,
                    question_text="",  # Would need to fetch from questions
                    selected_answer=submission.answers.get(q_result.question_id, ""),
                    correct_answer=None,
                    is_correct=None,
                    points_earned=q_result.score,
                    max_points=q_result.max_score,
                    explanation=None,
                    feedback=q_result.feedback
                ))

            return QuizGradingResult(
                quiz_id=quiz_id,
                attempt_id=str(attempt_id),
                total_score=llm_result.total_score,
                max_score=llm_result.max_score,
                percentage=llm_result.percentage,
                passed=llm_result.passed,
                grading_mode="llm",
                results=results,
                summary=llm_result.summary,
                completed_at=attempt.completed_at
            )

        else:
            # Rule-based grading (Phase 1 method)
            service = QuizService(db)
            result = await service.submit_quiz(
                UUID(quiz_id),
                user_id,
                submission.answers
            )

            # Get question details for results
            question_map = {str(q.id): q for q in questions}

            results = []
            for q_id, q_result in result.results.items():
                q = question_map.get(q_id)
                if q:
                    results.append(QuestionResult(
                        question_id=q_id,
                        question_text=q.question_text,
                        selected_answer=q_result.get("selected_answer", ""),
                        correct_answer=q.correct_answer.value,
                        is_correct=q_result.get("is_correct", False),
                        points_earned=10 if q_result.get("is_correct") else 0,
                        max_points=10,
                        explanation=q.explanation
                    ))

            # Get attempt ID
            attempt_result = await db.execute(
                select(QuizAttempt)
                .where(QuizAttempt.user_id == user_id)
                .where(QuizAttempt.quiz_id == UUID(quiz_id))
                .order_by(QuizAttempt.completed_at.desc())
                .limit(1)
            )
            attempt = attempt_result.scalar_one_or_none()

            return QuizGradingResult(
                quiz_id=quiz_id,
                attempt_id=str(attempt.id) if attempt else "",
                total_score=result.score,
                max_score=100,
                percentage=float(result.score),
                passed=result.passed,
                grading_mode="auto",
                results=results,
                summary="Quiz completed successfully." if result.passed else "Keep practicing! Review the material and try again.",
                completed_at=attempt.completed_at if attempt else datetime.utcnow()
            )

    except HTTPException:
        raise
    except QuizLLMServiceError as e:
        logger.error(f"LLM grading error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM grading failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit quiz"
        )


@router.get("/{quiz_id}/insights", response_model=QuizInsights)
async def get_quiz_insights(
    quiz_id: str,
    user_id: UUID = Query(description="User UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered quiz performance insights.

    Analyzes all attempts to provide:
    - Performance trends
    - Strengths and weaknesses
    - Personalized recommendations
    - Encouragement

    **Phase 3 Feature**: Requires at least 2 attempts and LLM enabled.
    """
    try:
        # Get attempts
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
                detail="No quiz attempts found"
            )

        if len(attempts) < 2:
            return QuizInsights(
                attempts_analyzed=len(attempts),
                average_score=attempts[0].score,
                best_score=max(a.score for a in attempts),
                improvement=0.0,
                trend="Not enough data",
                strengths=[],
                focus_areas=[],
                recommendations=["Take more attempts to see insights"],
                encouragement="Keep learning!"
            )

        # Use LLM for insights if enabled
        if settings.enable_phase_2_llm:
            insights = await generate_quiz_insights(quiz_id, list(attempts), db)
            return QuizInsights(**insights.to_dict())

        # Simple insights without LLM
        scores = [a.score for a in attempts]
        avg_score = sum(scores) / len(scores)
        best_score = max(scores)
        improvement = scores[-1] - scores[0]

        return QuizInsights(
            attempts_analyzed=len(attempts),
            average_score=round(avg_score, 1),
            best_score=best_score,
            improvement=round(improvement, 1),
            trend="improving" if improvement > 0 else "stable" if improvement == 0 else "declining",
            strengths=[],
            focus_areas=[],
            recommendations=[],
            encouragement="Good progress!" if improvement > 0 else "Keep practicing!"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate insights"
        )


@router.get("/{quiz_id}/history", response_model=List[QuizHistoryItem])
async def get_quiz_history(
    quiz_id: str,
    user_id: UUID = Query(description="User UUID"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's quiz attempt history.

    **Phase 3 Enhancement**: Shows score progression over time.
    """
    try:
        result = await db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.quiz_id == UUID(quiz_id))
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
        )
        attempts = result.scalars().all()

        return [
            QuizHistoryItem(
                attempt_id=str(a.id),
                quiz_id=str(a.quiz_id),
                score=a.score,
                passed=a.score >= 70,
                completed_at=a.completed_at
            )
            for a in attempts
        ]

    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quiz history"
        )
