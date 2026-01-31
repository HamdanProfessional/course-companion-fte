"""
Adaptive Learning Service - Phase 2 LLM-Powered Features.

Uses LLM to analyze student performance and provide personalized recommendations.
Only active when ENABLE_PHASE_2_LLM=true.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.core.llm import get_llm_client, LLMClientError
from src.services.cost_tracking_service import get_cost_tracking_client
from src.models.database import (
    User, Chapter, Quiz, QuizAttempt, Progress, Question
)
from src.core.database import get_db

logger = logging.getLogger(__name__)


class AdaptiveServiceError(Exception):
    """Base exception for adaptive service errors."""
    pass


class KnowledgeGapAnalysis:
    """Knowledge gap analysis result."""

    def __init__(
        self,
        weak_topics: List[str],
        strong_topics: List[str],
        recommended_review: List[str],
        confidence_score: float,
        explanation: str
    ):
        self.weak_topics = weak_topics
        self.strong_topics = strong_topics
        self.recommended_review = recommended_review
        self.confidence_score = confidence_score
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weak_topics": self.weak_topics,
            "strong_topics": self.strong_topics,
            "recommended_review": self.recommended_review,
            "confidence_score": self.confidence_score,
            "explanation": self.explanation
        }


class ChapterRecommendation:
    """Personalized chapter recommendation."""

    def __init__(
        self,
        next_chapter_id: str,
        next_chapter_title: str,
        reason: str,
        alternative_paths: List[Dict[str, str]],
        estimated_completion_minutes: int,
        difficulty_match: str
    ):
        self.next_chapter_id = next_chapter_id
        self.next_chapter_title = next_chapter_title
        self.reason = reason
        self.alternative_paths = alternative_paths
        self.estimated_completion_minutes = estimated_completion_minutes
        self.difficulty_match = difficulty_match

    def to_dict(self) -> Dict[str, Any]:
        return {
            "next_chapter_id": self.next_chapter_id,
            "next_chapter_title": self.next_chapter_title,
            "reason": self.reason,
            "alternative_paths": self.alternative_paths,
            "estimated_completion_minutes": self.estimated_completion_minutes,
            "difficulty_match": self.difficulty_match
        }


class LearningPath:
    """Personalized learning path."""

    def __init__(
        self,
        path: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
        total_hours: float,
        rationale: str
    ):
        self.path = path
        self.milestones = milestones
        self.total_hours = total_hours
        self.rationale = rationale

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "milestones": self.milestones,
            "total_hours": self.total_hours,
            "rationale": self.rationale
        }


async def analyze_knowledge_gaps(
    user_id: str,
    db: AsyncSession
) -> KnowledgeGapAnalysis:
    """
    Analyze quiz performance to identify knowledge gaps.

    Uses LLM to:
    - Identify weak topics from incorrect answers
    - Identify strong topics from correct answers
    - Suggest prerequisite chapters for review
    - Provide explanation of analysis

    Args:
        user_id: User UUID
        db: Database session

    Returns:
        KnowledgeGapAnalysis with weak/strong topics and recommendations

    Raises:
        AdaptiveServiceError: If analysis fails
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise AdaptiveServiceError("Phase 2 LLM features are not enabled")

    try:
        # Fetch user's quiz attempts with question details
        result = await db.execute(
            select(QuizAttempt)
            .options(
                selectinload(QuizAttempt.quiz)
                .selectinload(Quiz.questions)
            )
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(10)  # Last 10 quiz attempts
        )
        attempts = result.scalars().all()

        if not attempts:
            # No quiz history yet
            return KnowledgeGapAnalysis(
                weak_topics=[],
                strong_topics=[],
                recommended_review=[],
                confidence_score=0.0,
                explanation="Take some quizzes first to enable knowledge gap analysis."
            )

        # Analyze performance data
        performance_data = []
        for attempt in attempts:
            quiz = attempt.quiz
            if not quiz:
                continue

            for question in quiz.questions:
                is_correct = attempt.answers.get(str(question.id)) == question.correct_answer

                performance_data.append({
                    "chapter": quiz.chapter_id if hasattr(quiz, 'chapter_id') else "unknown",
                    "question": question.question_text[:100],  # Truncate for context
                    "correct": is_correct,
                    "topic": quiz.title if quiz else "Unknown"
                })

        # Calculate topic performance
        topic_performance = {}
        for item in performance_data:
            topic = item["topic"]
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            topic_performance[topic]["total"] += 1
            if item["correct"]:
                topic_performance[topic]["correct"] += 1

        # Prepare analysis prompt
        performance_summary = "\n".join([
            f"- {topic}: {stats['correct']}/{stats['total']} correct ({stats['correct']/stats['total']*100:.0f}%)"
            for topic, stats in topic_performance.items()
        ])

        system_prompt = """You are an AI learning analyst that identifies knowledge gaps from quiz performance.
Analyze the provided performance data and identify:
1. Weak topics (topics where student scored <70%)
2. Strong topics (topics where student scored >85%)
3. Recommended review (specific chapters or topics to review)
4. Confidence score (0-1) based on amount of data
5. Brief explanation of the analysis

Respond in JSON format:
{
    "weak_topics": ["topic1", "topic2"],
    "strong_topics": ["topic3", "topic4"],
    "recommended_review": ["chapter-id-1", "chapter-id-2"],
    "confidence_score": 0.85,
    "explanation": "Based on your quiz performance..."
}"""

        user_prompt = f"""Analyze this student's quiz performance:

{performance_summary}

Provide knowledge gap analysis in JSON format."""

        # Get LLM analysis
        response = await llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more deterministic analysis
            response_format={"type": "json_object"}
        )

        # Parse response
        import json
        analysis_data = json.loads(response)

        return KnowledgeGapAnalysis(
            weak_topics=analysis_data.get("weak_topics", []),
            strong_topics=analysis_data.get("strong_topics", []),
            recommended_review=analysis_data.get("recommended_review", []),
            confidence_score=analysis_data.get("confidence_score", 0.5),
            explanation=analysis_data.get("explanation", "Analysis complete.")
        )

    except LLMClientError as e:
        logger.error(f"LLM error in knowledge gap analysis: {e}")
        raise AdaptiveServiceError(f"Failed to analyze knowledge gaps: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in knowledge gap analysis: {e}")
        raise AdaptiveServiceError(f"Analysis failed: {e}")


async def recommend_next_chapter(
    user_id: str,
    db: AsyncSession
) -> ChapterRecommendation:
    """
    Recommend optimal next chapter based on performance and progress.

    Args:
        user_id: User UUID
        db: Database session

    Returns:
        ChapterRecommendation with personalized suggestion

    Raises:
        AdaptiveServiceError: If recommendation fails
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise AdaptiveServiceError("Phase 2 LLM features are not enabled")

    try:
        # Get user progress
        result = await db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        # Get all available chapters
        result = await db.execute(
            select(Chapter)
            .order_by(Chapter.order)
        )
        chapters = result.scalars().all()

        # Get recent quiz performance
        result = await db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(5)
        )
        recent_attempts = result.scalars().all()

        # Determine completed chapters
        completed_ids = progress.completed_chapters if progress else []
        completed_chapters = [c for c in chapters if str(c.id) in completed_ids]
        available_chapters = [c for c in chapters if str(c.id) not in completed_ids]

        if not available_chapters:
            # All chapters completed
            return ChapterRecommendation(
                next_chapter_id="",
                next_chapter_title="Course Complete!",
                reason="Congratulations! You've completed all chapters.",
                alternative_paths=[],
                estimated_completion_minutes=0,
                difficulty_match="N/A"
            )

        # Calculate recent quiz average
        if recent_attempts:
            avg_score = sum(a.score for a in recent_attempts) / len(recent_attempts)
        else:
            avg_score = 0  # No quizzes taken yet

        # Prepare context for LLM
        last_completed = completed_chapters[-1] if completed_chapters else None
        next_in_sequence = available_chapters[0]

        chapters_summary = []
        for c in available_chapters[:5]:  # Next 5 chapters
            chapters_summary.append({
                "id": str(c.id),
                "title": c.title,
                "order": c.order,
                "difficulty": c.difficulty_level,
                "estimated_time": c.estimated_time
            })

        context = {
            "last_completed": {
                "title": last_completed.title if last_completed else "None",
                "order": last_completed.order if last_completed else 0
            },
            "recent_quiz_average": round(avg_score, 1),
            "available_chapters": chapters_summary,
            "completed_count": len(completed_chapters),
            "total_chapters": len(chapters)
        }

        # Generate recommendation
        system_prompt = """You are an AI learning advisor that recommends the optimal next chapter.
Consider:
1. Student's recent quiz performance (higher scores = ready for harder content)
2. Natural progression (don't skip too far ahead)
3. Difficulty level matching
4. Estimated completion time

Respond in JSON format:
{
    "next_chapter_id": "chapter-id",
    "next_chapter_title": "Chapter Title",
    "reason": "Based on your strong performance in chapter 3...",
    "alternative_paths": [
        {"id": "alt-id-1", "title": "Alternative Chapter 1", "reason": "If you want to focus on X"},
        {"id": "alt-id-2", "title": "Alternative Chapter 2", "reason": "If you prefer easier content"}
    ],
    "estimated_completion_minutes": 45,
    "difficulty_match": "Perfect match for your current level"
}"""

        user_prompt = f"""Recommend the next chapter for this student:

Context:
{format_context(context)}

Available chapters:
{format_chapters(chapters_summary)}

Provide recommendation in JSON format."""

        # Generate recommendation with cost tracking
        # Note: GLM API doesn't support response_format parameter, so we don't pass it
        # The LLM is instructed via system_prompt to respond in JSON

        # Use cost-tracking client if available
        cost_client = get_cost_tracking_client(str(user_id), "adaptive", db)
        if cost_client:
            logger.info(f"Using cost-tracking client for adaptive recommendations (user: {user_id})")
            response = await cost_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.4
            )
        else:
            response = await llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.4
            )

        import json
        import re

        # Log raw response for debugging
        logger.info(f"GLM API response: {response[:200]}...")

        # Try to parse JSON response
        try:
            # GLM might return JSON with markdown code blocks, extract JSON
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            elif '```' in response:
                # Extract content between code blocks
                response = re.sub(r'```\w*\n?', '', response).strip()

            rec_data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from GLM response: {e}")
            logger.error(f"Response was: {response}")
            # Fallback to default recommendation
            rec_data = {
                "next_chapter_id": str(next_in_sequence.id),
                "next_chapter_title": next_in_sequence.title,
                "reason": "Continue with the next chapter in sequence.",
                "alternative_paths": [],
                "estimated_completion_minutes": 30,
                "difficulty_match": "Appropriate for your level"
            }

        return ChapterRecommendation(
            next_chapter_id=rec_data.get("next_chapter_id", str(next_in_sequence.id)),
            next_chapter_title=rec_data.get("next_chapter_title", next_in_sequence.title),
            reason=rec_data.get("reason", "Continue with the next chapter in sequence."),
            alternative_paths=rec_data.get("alternative_paths", []),
            estimated_completion_minutes=rec_data.get("estimated_completion_minutes", 30),
            difficulty_match=rec_data.get("difficulty_match", "Appropriate for your level")
        )

    except LLMClientError as e:
        logger.error(f"LLM error in chapter recommendation: {e}")
        raise AdaptiveServiceError(f"Failed to generate recommendation: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in chapter recommendation: {e}")
        raise AdaptiveServiceError(f"Recommendation failed: {e}")


async def generate_personalized_path(
    user_id: str,
    learning_goals: List[str],
    available_time_hours: int,
    db: AsyncSession
) -> LearningPath:
    """
    Generate personalized learning path based on goals and time constraints.

    Args:
        user_id: User UUID
        learning_goals: List of learning objectives
        available_time_hours: Hours per week available for learning
        db: Database session

    Returns:
        LearningPath with optimized chapter sequence

    Raises:
        AdaptiveServiceError: If path generation fails
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise AdaptiveServiceError("Phase 2 LLM features are not enabled")

    try:
        # Get all chapters
        result = await db.execute(
            select(Chapter)
            .order_by(Chapter.order)
        )
        chapters = result.scalars().all()

        # Get user progress
        result = await db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        completed_ids = progress.completed_chapters if progress else []

        # Prepare chapter data
        chapters_data = []
        for c in chapters:
            chapters_data.append({
                "id": str(c.id),
                "title": c.title,
                "order": c.order,
                "difficulty": c.difficulty_level,
                "estimated_time_minutes": c.estimated_time,
                "completed": str(c.id) in completed_ids
            })

        # Filter out completed chapters for planning
        incomplete_chapters = [c for c in chapters_data if not c["completed"]]

        system_prompt = """You are an AI curriculum designer that creates personalized learning paths.
Optimize the chapter sequence based on:
1. Learning goals (prioritize relevant chapters)
2. Available time (fit within weekly hours)
3. Logical dependencies (don't teach advanced before basics)
4. Difficulty progression (gradual increase)

Respond in JSON format:
{
    "path": [
        {
            "chapter_id": "id",
            "title": "Chapter Title",
            "order": 1,
            "estimated_minutes": 30,
            "reason": "Foundational for your goals"
        }
    ],
    "milestones": [
        {
            "week": 1,
            "chapters": ["chapter-id-1", "chapter-id-2"],
            "goal": "Complete foundational topics",
            "total_hours": 2.5
        }
    ],
    "total_hours": 15.5,
    "rationale": "This path prioritizes chapters relevant to your goals..."
}"""

        user_prompt = f"""Create a personalized learning path for this student:

Learning Goals:
{format_goals(learning_goals)}

Available Time: {available_time_hours} hours per week

Available Chapters:
{format_chapters_for_path(incomplete_chapters)}

Completed Chapters: {len(completed_ids)}/{len(chapters)}

Generate optimal learning path in JSON format."""

        response = await llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        import json
        path_data = json.loads(response)

        return LearningPath(
            path=path_data.get("path", []),
            milestones=path_data.get("milestones", []),
            total_hours=path_data.get("total_hours", 0),
            rationale=path_data.get("rationale", "Personalized learning path generated.")
        )

    except LLMClientError as e:
        logger.error(f"LLM error in path generation: {e}")
        raise AdaptiveServiceError(f"Failed to generate path: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in path generation: {e}")
        raise AdaptiveServiceError(f"Path generation failed: {e}")


# Helper functions

def format_context(context: Dict[str, Any]) -> str:
    """Format context dict for prompt."""
    lines = []
    for key, value in context.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def format_chapters(chapters: List[Dict[str, Any]]) -> str:
    """Format chapters list for prompt."""
    lines = []
    for c in chapters:
        lines.append(
            f"- {c['title']} (Order: {c['order']}, Difficulty: {c['difficulty']}, Time: {c['estimated_time']}min)"
        )
    return "\n".join(lines)


def format_goals(goals: List[str]) -> str:
    """Format learning goals for prompt."""
    return "\n".join([f"- {goal}" for goal in goals])


def format_chapters_for_path(chapters: List[Dict[str, Any]]) -> str:
    """Format chapters for path planning."""
    lines = []
    for c in chapters:
        lines.append(
            f"{c['title']} - {c['difficulty']} - {c['estimated_time_minutes']}min"
        )
    return "\n".join(lines)
