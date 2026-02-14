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
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime
import uuid

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
# Mentor service - Phase 3 feature
from src.services.mentor_service import MentorService, MentorServiceError

from src.models.database import User
from src.models.schemas import ChapterDetail
from src.api.dependencies import get_current_user, get_optional_user

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


class GenerateQuizRequest(BaseModel):
    """Request for AI-generated quiz questions."""
    topic: str = Field(..., min_length=3, description="Topic to generate questions about (e.g., 'AI Agents', 'MCP Integration')")
    subtopic: Optional[str] = Field(None, description="Specific subtopic (optional)")
    difficulty: str = Field(default="beginner", description="Difficulty: beginner, intermediate, advanced, mixed")
    num_questions: int = Field(default=5, ge=3, le=10, description="Number of questions to generate (3-10)")


class GeneratedQuestionItem(BaseModel):
    """AI-generated question."""
    id: str
    question_text: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str
    difficulty: str
    topic: str
    subtopic: str


class GeneratedQuizResponse(BaseModel):
    """Response with AI-generated quiz."""
    quiz_id: str
    questions: List[GeneratedQuestionItem]
    total_questions: int
    topic: str
    subtopic: Optional[str]
    difficulty: str
    generated_at: str


# =============================================================================
# Helper Functions
# =============================================================================


async def verify_premium_access(user: Optional[User]) -> User:
    """Verify user has premium access for AI features."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Authentication required for AI features",
                "login_url": "/api/v3/tutor/auth/login"
            }
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
    elif settings.llm_provider == "deepseek":
        model = settings.deepseek_model
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
    user_id: Optional[str] = Query(None, description="User ID"),
    current_user: Optional[User] = Depends(get_optional_user),
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

    **Authentication**: Optional - Works for authenticated users or guest users with user_id.

    Args:
        user_id: User UUID from query param
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        AdaptiveAnalysis with weak/strong topics and recommendations
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        # Determine user_id: prefer current_user, fall back to query param
        _user_id = None
        if current_user:
            await verify_premium_access(current_user)
            _user_id = str(current_user.id)
        elif user_id:
            _user_id = user_id

        # Return default response for guest users without user_id
        if _user_id is None:
            return AdaptiveAnalysis(
                weak_topics=[],
                strong_topics=[],
                recommended_review=[],
                confidence_score=0.0,
                explanation="Please log in to enable knowledge gap analysis and personalized recommendations."
            )

        analysis = await analyze_knowledge_gaps(_user_id, db)

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
        # Service returns degraded response, so this shouldn't happen
        # But if it does, return 200 with degraded response
        logger.warning(f"Adaptive service returned error instead of degraded response: {e}")
        return AdaptiveAnalysis(
            weak_topics=[],
            strong_topics=[],
            recommended_review=[],
            confidence_score=0.0,
            explanation="AI analysis temporarily unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error in knowledge analysis: {e}")
        # Return degraded response instead of 500 error
        return AdaptiveAnalysis(
            weak_topics=[],
            strong_topics=[],
            recommended_review=[],
            confidence_score=0.0,
            explanation="AI analysis temporarily unavailable. Please try again later."
        )


@router.get("/adaptive/recommendations", response_model=ChapterRecommendation)
async def get_recommendations(
    user_id: Optional[str] = Query(None, description="User ID"),
    current_user: Optional[User] = Depends(get_optional_user),
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

    **Authentication**: Optional - Works for authenticated users or guest users with user_id.

    Args:
        user_id: User UUID from query param
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        ChapterRecommendation with personalized suggestion
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        # Determine user_id: prefer current_user, fall back to query param
        _user_id = None
        if current_user:
            await verify_premium_access(current_user)
            _user_id = str(current_user.id)
        elif user_id:
            _user_id = user_id

        # Return default response for guest users without user_id
        if _user_id is None:
            return ChapterRecommendation(
                next_chapter_id="",
                next_chapter_title="Getting Started",
                reason="Please log in to enable personalized chapter recommendations based on your progress.",
                alternative_paths=[],
                estimated_completion_minutes=15,
                difficulty_match="beginner"
            )

        recommendation = await recommend_next_chapter(_user_id, db)

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
        # Service returns degraded response, so this shouldn't happen
        # But if it does, return 200 with degraded response
        logger.warning(f"Adaptive service returned error instead of degraded response: {e}")
        return ChapterRecommendation(
            next_chapter_id="",
            next_chapter_title="Getting Started",
            reason="AI recommendations temporarily unavailable. Please continue with the next chapter in your course.",
            alternative_paths=[],
            estimated_completion_minutes=15,
            difficulty_match="beginner"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting recommendations: {e}")
        # Return degraded response instead of 500 error
        return ChapterRecommendation(
            next_chapter_id="",
            next_chapter_title="Getting Started",
            reason="AI recommendations temporarily unavailable. Please try again later.",
            alternative_paths=[],
            estimated_completion_minutes=15,
            difficulty_match="beginner"
        )


@router.post("/adaptive/path", response_model=LearningPathResponse)
async def create_learning_path(
    request: LearningPathRequest,
    current_user: User = Depends(get_current_user),
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

    **Authentication**: Required - Users must be logged in.

    Args:
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        LearningPathResponse with optimized chapter sequence
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        await verify_premium_access(current_user)

        path = await generate_personalized_path(
            str(current_user.id),
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
        # Service returns degraded response, so this shouldn't happen
        # But if it does, return 200 with degraded response
        logger.warning(f"Adaptive service returned error instead of degraded response: {e}")
        return LearningPathResponse(
            path=[],
            milestones=[],
            total_hours=0.0,
            rationale="AI learning path generation temporarily unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error creating learning path: {e}")
        # Return degraded response instead of 500 error
        return LearningPathResponse(
            path=[],
            milestones=[],
            total_hours=0.0,
            rationale="AI learning path generation temporarily unavailable. Please try again later."
        )


@router.post("/mentor/chat", response_model=MentorChatResponse)
async def mentor_chat(
    request: MentorChatRequest,
    conversation_id: Optional[UUID] = Query(None, description="Conversation UUID for chat history"),
    user_id: Optional[str] = Query(None, description="User ID for alternative auth"),
    current_user: Optional[User] = Depends(get_optional_user),
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
    - Saves conversation history to database

    **Phase 3 Feature**: Interactive AI tutoring with chat history.

    **Authentication**: Optional - Works for authenticated users or user_id.

    Example question:
    ```
    "Can you explain how MCP servers work and how they connect to ChatGPT?"
    ```
    """
    # Determine actual user_id: prefer current_user, fall back to query param
    _user_id = None
    if current_user:
        await verify_premium_access(current_user)
        _user_id = str(current_user.id)
    elif user_id:
        _user_id = user_id

    # Log AFTER determining user_id
    logger.info(f"mentor chat request from user {_user_id}, conversation_id: {conversation_id}")
    logger.info(f"Question: {request.question[:100]}...")
    logger.info(f"Conversation history length: {len(request.conversation_history) if request.conversation_history else 0}")

    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
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
            user_id=_user_id,
            question=request.question,
            chapter_context=request.chapter_context,
            conversation_history=history
        )

        # Save to chat history if conversation_id provided
        if conversation_id:
            from src.models.database import ChatConversation, ChatMessage

            # Verify conversation belongs to user
            from sqlalchemy import select
            conv_result = await db.execute(
                select(ChatConversation).where(
                    ChatConversation.id == conversation_id,
                    ChatConversation.user_id == _user_id
                )
            )
            conversation = conv_result.scalar_one_or_none()

            if conversation:
                # Save user message
                user_message = ChatMessage(
                    conversation_id=conversation_id,
                    role="user",
                    content=request.question
                )
                db.add(user_message)

                # Save assistant response
                assistant_message = ChatMessage(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response.get("answer", "")
                )
                db.add(assistant_message)

                # Update conversation title if it's first message
                from sqlalchemy import func
                msg_count_result = await db.execute(
                    select(func.count(ChatMessage.id)).where(ChatMessage.conversation_id == conversation_id)
                )
                msg_count = msg_count_result.scalar() - 2  # Subtract two messages we just added

                if msg_count == 0:
                    # Update title with first message preview
                    conversation.title = request.question[:100] + ("..." if len(request.question) > 100 else "")

                conversation.updated_at = func.now()
                await db.commit()

        return MentorChatResponse(
            answer=response.get("answer", ""),
            follow_up_questions=response.get("follow_up_questions", []),
            related_chapters=response.get("related_chapters", []),
            confidence=response.get("confidence", 0.8)
        )

    except HTTPException:
        raise
    except MentorServiceError as e:
        logger.error(f"Mentor service error for user {user_id}: {e}")
        # Return proper JSON error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "message": "Failed to generate mentor response"}
        )
    except Exception as e:
        logger.error(f"Unexpected error in mentor chat for user {user_id}: {e}")
        # Return proper JSON error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "message": "Failed to generate mentor response"}
        )


@router.post("/explain", response_model=ContentExplanationResponse)
async def explain_content(
    request: ContentExplanationRequest,
    current_user: User = Depends(get_current_user),
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

    **Authentication**: Required - Users must be logged in.

    Complexity levels:
    - `beginner`: Simple language, lots of examples
    - `intermediate`: Balanced (default)
    - `advanced`: Technical depth, nuanced

    Args:
        request: Content explanation request
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        ContentExplanationResponse with explanation and examples
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        # Free users get basic explanations, premium get detailed
        if current_user.tier == "FREE":
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
    except MentorServiceError as e:
        logger.error(f"LLM error in topic explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate explanation"
        )
    except Exception as e:
        logger.error(f"Unexpected error in topic explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate explanation"
        )


@router.post("/quiz/grade-llm")
async def grade_quiz_with_ai(
    request: QuizGradingRequest,
    current_user: User = Depends(get_current_user),
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

    **Authentication**: Required - Users must be logged in.

    This is an alias to quizzes endpoint with LLM mode enabled.
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        await verify_premium_access(current_user)

        # Quiz LLM service - Phase 3 feature (may not exist in Zero-Backend-LLM architecture)
        try:
            from src.services.quiz_llm_service import grade_quiz_with_llm
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="LLM quiz grading is not available in Zero-Backend-LLM mode. Please enable Phase 2/3 LLM features."
            )

        result = await grade_quiz_with_llm(
            request.quiz_id,
            str(current_user.id),
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get LLM usage costs for a user (admin/monitoring).

    **Phase 3 Feature**: Cost tracking and monitoring.

    **Authentication**: Required - Pro users only.

    Args:
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        Cost breakdown by feature and time period
    """
    try:
        if current_user.tier != "PRO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cost tracking is only available to Pro users"
            )

        # Cost tracking service - Phase 3 feature (may not exist in Zero-Backend-LLM architecture)
        try:
            from src.services.cost_tracking_service import CostTrackingService
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Cost tracking is not available in Zero-Backend-LLM mode. Please enable Phase 2/3 LLM features."
            )

        cost_service = CostTrackingService(db)
        costs = await cost_service.get_user_costs(str(current_user.id))

        return {
            "user_id": str(current_user.id),
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


class GenerateQuizRequest(BaseModel):
    """Request for AI-generated quiz questions."""
    topic: str = Field(..., min_length=3, description="Topic to generate questions about (e.g., 'AI Agents', 'MCP Integration')")
    subtopic: Optional[str] = Field(None, description="Specific subtopic (optional)")
    difficulty: str = Field(default="beginner", description="Difficulty: beginner, intermediate, advanced, mixed")
    num_questions: int = Field(default=5, ge=3, le=10, description="Number of questions to generate (3-10)")


class GeneratedQuestionItem(BaseModel):
    """AI-generated question."""
    id: str
    question_text: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str
    difficulty: str
    topic: str
    subtopic: str


class GeneratedQuizResponse(BaseModel):
    """Response with AI-generated quiz."""
    quiz_id: str
    questions: List[GeneratedQuestionItem]
    total_questions: int
    topic: str
    subtopic: Optional[str]
    difficulty: str
    generated_at: str


@router.post("/generate-quiz", response_model=GeneratedQuizResponse)
async def generate_quiz_with_ai(
    request: GenerateQuizRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate unlimited quiz questions using AI.

    Creates unique, AI-generated multiple-choice questions on any topic
    related to AI agents, MCP, ChatGPT apps, and web development.

    **Features:**
    - Generate 3-10 questions per request
    - 4 difficulty levels: beginner, intermediate, advanced, mixed
    - Detailed explanations for each answer
    - Never runs out of practice material

    **Example Request:**
    ```json
    {
        "topic": "AI Agents",
        "subtopic": "MCP Integration",
        "difficulty": "intermediate",
        "num_questions": 5
    }
    ```

    **Phase 3 Feature**: AI-powered infinite quiz generation.

    **Authentication**: Required - Users must be logged in.

    Args:
        request: Quiz generation request
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        GeneratedQuizResponse with AI-generated questions
    """
    if not settings.enable_phase_2_llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"detail": "LLM features are not enabled", "phase_2_enabled": False}
        )

    try:
        # Import LLM client
        from src.core.llm import get_llm_client

        llm_client = get_llm_client()
        if not llm_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM client not available"
            )

        # Prepare prompt for quiz generation
        difficulty_desc = {
            "beginner": "basic concepts, simple questions, foundational knowledge",
            "intermediate": "practical applications, some complexity, real-world scenarios",
            "advanced": "complex scenarios, edge cases, advanced concepts",
            "mixed": "mix of beginner, intermediate, and advanced questions"
        }

        system_prompt = f"""You are an expert AI tutor generating quiz questions about AI agents, MCP (Model Context Protocol), ChatGPT applications, and web development.

Generate {request.num_questions} multiple-choice questions in the following JSON format:
{{
    "questions": [
    {{
        "question": "Clear question text",
        "options": {{
            "A": "First option",
            "B": "Second option",
            "C": "Third option",
            "D": "Fourth option"
        }},
        "correct_answer": "A",
        "explanation": "Detailed explanation of why this is correct",
        "difficulty": "{request.difficulty}"
    }}
]

Requirements:
- Questions must be clear and unambiguous
- All options should be plausible
- Only one correct answer per question
- Explanations should be educational
- Difficulty must match requested level
- Questions should cover different aspects of {request.topic}"""

        user_prompt = f"""Generate {request.num_questions} multiple-choice quiz questions about:

Topic: {request.topic}
{f"Subtopic: {request.subtopic}" if request.subtopic else ""}
Difficulty: {request.difficulty} ({difficulty_desc.get(request.difficulty, request.difficulty)})

Return valid JSON with the questions array."""

        # Generate questions
        response = await llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=2000
        )

        # Parse JSON response
        import json
        import re

        try:
            # First, try to find complete JSON object
            # Look for balanced braces
            brace_count = 0
            json_start = -1
            json_end = -1

            for i, char in enumerate(response):
                if char == '{':
                    if brace_count == 0:
                        json_start = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and json_start >= 0:
                        json_end = i + 1
                        break

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                response_data = json.loads(json_str)
            else:
                # Try extracting JSON from markdown code blocks
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group(1))
                elif '```' in response:
                    cleaned = re.sub(r'```\w*\n?', '', response).strip()
                    response_data = json.loads(cleaned)
                else:
                    response_data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse generated quiz: {str(e)}"
            )

        questions_data = response_data.get("questions", [])

        if not questions_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No questions generated. Please try again."
            )

        # Transform to response format
        questions = []
        for i, q_data in enumerate(questions_data):
            questions.append(GeneratedQuestionItem(
                id=f"gen_{uuid.uuid4().hex[:8]}_{i}",
                question_text=q_data.get("question", ""),
                options=q_data.get("options", {}),
                correct_answer=q_data.get("correct_answer", "A"),
                explanation=q_data.get("explanation", ""),
                difficulty=q_data.get("difficulty", request.difficulty),
                topic=request.topic,
                subtopic=request.subtopic or ""
            ))

        # Create unique quiz ID
        quiz_id = f"quiz_gen_{uuid.uuid4().hex}"

        return GeneratedQuizResponse(
            quiz_id=quiz_id,
            questions=questions,
            total_questions=len(questions),
            topic=request.topic,
            subtopic=request.subtopic,
            difficulty=request.difficulty,
            generated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )
