"""
AI Mentor API Endpoints - Phase 2.

Provides conversational AI tutoring:
- Answer conceptual questions
- Provide study guidance
- Generate practice problems

Only active when ENABLE_PHASE_2_LLM=true.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.config import settings
from src.services.mentor_service import (
    answer_concept_question,
    provide_study_guidance,
    generate_practice_problems,
    MentorServiceError
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class MentorQuestionRequest(BaseModel):
    """Request to ask AI mentor a question."""

    question: str = Field(
        description="Student's question",
        min_length=10,
        max_length=1000
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context (current_chapter, recent_quiz_scores, etc.)"
    )


class MentorQuestionResponse(BaseModel):
    """AI mentor response to question."""

    answer: str = Field(description="AI's answer to the question")
    related_chapters: List[Dict[str, str]] = Field(
        description="Related chapters for further reading"
    )
    practice_problems: List[Dict[str, Any]] = Field(
        description="Suggested practice problems"
    )
    follow_up_questions: List[str] = Field(
        description="Questions to deepen understanding"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the answer (0-1)"
    )


class StudyGuidanceResponse(BaseModel):
    """Personalized study guidance response."""

    learning_pace: str = Field(description="Assessment of learning speed")
    strengths: List[str] = Field(description="Identified strengths")
    areas_for_improvement: List[str] = Field(description="Areas needing work")
    recommended_focus: List[str] = Field(description="Suggested focus areas")
    study_tips: List[str] = Field(description="Practical study advice")
    estimated_completion_weeks: int = Field(
        description="Estimated weeks to complete course",
        ge=1,
        le=52
    )


class PracticeProblemsRequest(BaseModel):
    """Request to generate practice problems."""

    topic: str = Field(
        description="Topic to generate problems for",
        min_length=3,
        max_length=100
    )
    difficulty: str = Field(
        description="Difficulty level",
        pattern="^(beginner|intermediate|advanced)$"
    )
    count: int = Field(
        description="Number of problems to generate",
        ge=1,
        le=10,
        default=3
    )


class PracticeProblem(BaseModel):
    """Generated practice problem."""

    title: str = Field(description="Problem title")
    description: str = Field(description="What to do")
    difficulty: str = Field(description="Problem difficulty")
    estimated_minutes: int = Field(description="Time to solve")
    hints: List[str] = Field(description="Hints to help solve")
    solution_approach: str = Field(description="How to approach solution")
    learning_outcome: str = Field(description="What you'll learn")


class PracticeProblemsResponse(BaseModel):
    """Generated practice problems response."""

    problems: List[PracticeProblem] = Field(description="Generated problems")
    topic: str = Field(description="Topic problems are for")
    count: int = Field(description="Number of problems generated")


# =============================================================================
# API Endpoints
# =============================================================================


@router.post(
    "/mentor/ask",
    response_model=MentorQuestionResponse,
    tags=["AI Mentor (Phase 2)"],
    summary="Ask AI mentor a question",
    description="Get personalized answer with related chapters and practice suggestions"
)
async def ask_mentor(
    request: MentorQuestionRequest,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Ask the AI mentor a conceptual question.

    The AI will:
    - Provide a clear, personalized answer
    - Reference relevant course chapters
    - Suggest practice problems
    - Generate follow-up questions to deepen understanding

    **Example**:
    ```json
    {
        "question": "How do I implement MCP in my ChatGPT app?",
        "context": {
            "current_chapter": "Understanding MCP",
            "recent_quiz_scores": [85, 90, 88]
        }
    }
    ```

    **Response**:
    - `answer`: Comprehensive explanation
    - `related_chapters`: Chapters for further reading
    - `practice_problems`: Hands-on exercises
    - `follow_up_questions`: Questions to explore next
    - `confidence`: AI's confidence in the answer (0-1)

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

    try:
        response = await answer_concept_question(
            str(user_id),
            request.question,
            request.context,
            db
        )
        return MentorQuestionResponse(**response.to_dict())

    except MentorServiceError as e:
        logger.error(f"Mentor service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in mentor ask: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question"
        )


@router.get(
    "/mentor/guidance",
    response_model=StudyGuidanceResponse,
    tags=["AI Mentor (Phase 2)"],
    summary="Get personalized study guidance",
    description="AI analyzes performance and provides study recommendations"
)
async def get_study_guidance(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized study guidance from AI mentor.

    Analyzes:
    - Learning pace (chapters per week)
    - Quiz performance trends
    - Strengths and weaknesses
    - Time to completion estimate

    Returns:
    - Learning pace assessment
    - Identified strengths (build on these!)
    - Areas for improvement (focus areas)
    - Recommended study focus
    - Practical study tips
    - Estimated completion time

    **Use Case**: Call this weekly to get updated guidance as you progress.

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

    try:
        guidance = await provide_study_guidance(str(user_id), db)
        return StudyGuidanceResponse(**guidance.to_dict())

    except MentorServiceError as e:
        logger.error(f"Mentor service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in study guidance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate guidance"
        )


@router.post(
    "/mentor/practice-problems",
    response_model=PracticeProblemsResponse,
    tags=["AI Mentor (Phase 2)"],
    summary="Generate practice problems",
    description="AI generates hands-on practice problems for specific topics"
)
async def create_practice_problems(request: PracticeProblemsRequest):
    """
    Generate practice problems for a specific topic.

    The AI will create hands-on problems including:
    - Problem description
    - Difficulty level
    - Estimated completion time
    - Helpful hints
    - Solution approach
    - Learning outcomes

    **Example**:
    ```json
    {
        "topic": "MCP server implementation",
        "difficulty": "intermediate",
        "count": 3
    }
    ```

    **Use Cases**:
    - Extra practice on difficult topics
    - Prepare for quizzes
    - Apply concepts to real scenarios
    - Deepen understanding

    **Difficulty Levels**:
    - `beginner`: Fundamental concepts, 15-30 min per problem
    - `intermediate`: Application of concepts, 30-60 min per problem
    - `advanced`: Complex scenarios, 60-90 min per problem

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

    try:
        problems = await generate_practice_problems(
            request.topic,
            request.difficulty,
            request.count
        )

        return PracticeProblemsResponse(
            problems=[PracticeProblem(**p) for p in problems],
            topic=request.topic,
            count=len(problems)
        )

    except MentorServiceError as e:
        logger.error(f"Mentor service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in problem generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate practice problems"
        )


@router.get(
    "/mentor/status",
    tags=["AI Mentor (Phase 2)"],
    summary="Check AI mentor feature status"
)
async def get_mentor_status():
    """Check if AI mentor features are enabled."""
    return {
        "phase_2_enabled": settings.enable_phase_2_llm,
        "llm_provider": settings.llm_provider if settings.enable_phase_2_llm else None,
        "features": {
            "ask_questions": True,
            "study_guidance": True,
            "practice_problems": True
        }
    }
