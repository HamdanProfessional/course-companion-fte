"""
Quiz API endpoints.
Zero-LLM compliance: Rule-based grading, no AI evaluation.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.quiz_service import QuizService
from src.models.schemas import (
    QuizWithQuestions,
    QuizSubmission,
    QuizResult,
)

router = APIRouter()


@router.get("/quizzes", response_model=List[QuizWithQuestions], tags=["Quiz"])
async def list_quizzes(
    db: AsyncSession = Depends(get_db)
):
    """
    List all quizzes.
    Zero-LLM: Returns verbatim quiz list from database.
    """
    service = QuizService(db)
    quizzes = await service.list_quizzes()
    return quizzes


@router.get("/quizzes/{quiz_id}", response_model=QuizWithQuestions, tags=["Quiz"])
async def get_quiz(
    quiz_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get quiz with questions (without correct answers).
    Zero-LLM: Returns verbatim quiz questions from database.
    """
    service = QuizService(db)
    quiz = await service.get_quiz(quiz_id)

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {quiz_id} not found"
        )

    return quiz


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizResult, tags=["Quiz"])
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    user_id: str,  # In production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Submit quiz answers for grading.
    Zero-LLM: Rule-based grading using answer keys (no AI evaluation).
    Compares submitted answers to pre-defined correct answers.
    """
    service = QuizService(db)
    result = await service.grade_quiz(quiz_id, user_id, submission)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {quiz_id} not found"
        )

    return result


@router.get("/quizzes/{quiz_id}/results", tags=["Quiz"])
async def get_quiz_results(
    quiz_id: str,
    user_id: str,  # In production, get from JWT token
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's quiz attempt history.
    Zero-LLM: Returns verbatim attempt history from database.
    """
    service = QuizService(db)
    results = await service.get_quiz_results(quiz_id, user_id, limit)

    if results is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {quiz_id} not found"
        )

    return {
        "quiz_id": quiz_id,
        "user_id": user_id,
        "attempts": results,
        "total": len(results)
    }
