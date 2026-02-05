"""
AI Mentor Service - Phase 2 LLM-Powered Educational Support.

Provides personalized tutoring through conversational AI.
Only active when ENABLE_PHASE_2_LLM=true.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.core.llm import get_llm_client, LLMClientError
from src.models.database import User, Chapter, Quiz, QuizAttempt, Progress

logger = logging.getLogger(__name__)


class MentorServiceError(Exception):
    """Base exception for mentor service errors."""
    pass


class MentorResponse:
    """AI mentor response to student question."""

    def __init__(
        self,
        answer: str,
        related_chapters: List[Dict[str, str]],
        practice_problems: List[Dict[str, Any]],
        follow_up_questions: List[str],
        confidence: float
    ):
        self.answer = answer
        self.related_chapters = related_chapters
        self.practice_problems = practice_problems
        self.follow_up_questions = follow_up_questions
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "related_chapters": self.related_chapters,
            "practice_problems": self.practice_problems,
            "follow_up_questions": self.follow_up_questions,
            "confidence": self.confidence
        }


class StudyGuidance:
    """Personalized study recommendations."""

    def __init__(
        self,
        learning_pace: str,
        strengths: List[str],
        areas_for_improvement: List[str],
        recommended_focus: List[str],
        study_tips: List[str],
        estimated_completion_weeks: int
    ):
        self.learning_pace = learning_pace
        self.strengths = strengths
        self.areas_for_improvement = areas_for_improvement
        self.recommended_focus = recommended_focus
        self.study_tips = study_tips
        self.estimated_completion_weeks = estimated_completion_weeks

    def to_dict(self) -> Dict[str, Any]:
        return {
            "learning_pace": self.learning_pace,
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "recommended_focus": self.recommended_focus,
            "study_tips": self.study_tips,
            "estimated_completion_weeks": self.estimated_completion_weeks
        }


async def answer_concept_question(
    user_id: str,
    question: str,
    context: Optional[Dict[str, Any]],
    db: AsyncSession
) -> MentorResponse:
    """
    Answer student's conceptual question using AI.

    Args:
        user_id: User UUID
        question: Student's question
        context: Optional context (current_chapter, recent_scores, etc.)
        db: Database session

    Returns:
        MentorResponse with answer, related chapters, and follow-up questions

    Raises:
        MentorServiceError: If answering fails
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise MentorServiceError("Phase 2 LLM features are not enabled")

    try:
        # Get user progress for context
        result = await db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        # Get all chapters for references
        result = await db.execute(
            select(Chapter)
            .order_by(Chapter.order)
            .limit(5)  # Last 5 chapters for context
        )
        recent_chapters = result.scalars().all()

        # Build context for LLM
        chapters_info = []
        for ch in recent_chapters:
            chapters_info.append({
                "id": str(ch.id),
                "title": ch.title,
                "order": ch.order,
                "difficulty": ch.difficulty_level
            })

        context_str = ""
        if context:
            if context.get("current_chapter"):
                context_str += f"Current Chapter: {context['current_chapter']}\n"
            if context.get("recent_quiz_scores"):
                scores = context["recent_quiz_scores"]
                avg_score = sum(scores) / len(scores) if scores else 0
                context_str += f"Recent Quiz Average: {avg_score:.1f}%\n"

        system_prompt = """You are an AI tutor helping students learn about AI agents, MCP, and building agents with ChatGPT.

Your role:
- Answer questions clearly at the appropriate level
- Provide practical examples when possible
- Relate concepts to course content
- Suggest related topics for further learning
- Generate 2-3 follow-up questions to deepen understanding

Be encouraging and supportive. If you're not confident about an answer, acknowledge it.

Respond in JSON format:
{
    "answer": "Your comprehensive answer...",
    "related_chapters": [
        {"id": "chapter-id", "title": "Chapter Title", "reason": "Relevance explanation"}
    ],
    "practice_problems": [
        {"topic": "Topic name", "difficulty": "beginner|intermediate", "description": "What to practice"}
    ],
    "follow_up_questions": [
        "Question 1?",
        "Question 2?"
    ],
    "confidence": 0.9
}"""

        user_prompt = f"""Student Question: {question}

{context_str}

Available Chapters (for reference):
{format_chapters_for_mentor(chapters_info)}

Provide a helpful answer in JSON format."""

        response = await llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.6,  # Balanced creativity
            response_format={"type": "json_object"}
        )

        import json
        response_data = json.loads(response)

        return MentorResponse(
            answer=response_data.get("answer", "I'd be happy to help with that!"),
            related_chapters=response_data.get("related_chapters", []),
            practice_problems=response_data.get("practice_problems", []),
            follow_up_questions=response_data.get("follow_up_questions", []),
            confidence=response_data.get("confidence", 0.7)
        )

    except LLMClientError as e:
        logger.error(f"LLM error in mentor answer: {e}")
        raise MentorServiceError(f"Failed to answer question: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in mentor answer: {e}")
        raise MentorServiceError(f"Answer generation failed: {e}")


async def provide_study_guidance(
    user_id: str,
    db: AsyncSession
) -> StudyGuidance:
    """
    Provide personalized study recommendations based on performance.

    Analyzes:
    - Learning pace (chapters per week)
    - Quiz performance trends
    - Time spent per chapter
    - Areas of struggle

    Args:
        user_id: User UUID
        db: Database session

    Returns:
        StudyGuidance with personalized recommendations
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise MentorServiceError("Phase 2 LLM features are not enabled")

    try:
        # Get user progress
        result = await db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        if not progress or not progress.last_activity:
            return StudyGuidance(
                learning_pace="Not started",
                strengths=["Start your learning journey!"],
                areas_for_improvement=["Complete first chapter"],
                recommended_focus=["Begin with Chapter 1"],
                study_tips=["Set a consistent study schedule", "Take notes while learning"],
                estimated_completion_weeks=4
            )

        # Get quiz attempts
        result = await db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(10)
        )
        attempts = result.scalars().all()

        # Calculate metrics
        completed_count = len(progress.completed_chapters) if progress.completed_chapters else 0

        if attempts:
            avg_score = sum(a.score for a in attempts) / len(attempts)
            recent_scores = [a.score for a in attempts[:3]]
            recent_avg = sum(recent_scores) / len(recent_scores)
        else:
            avg_score = 0
            recent_avg = 0

        # Determine learning pace
        days_active = (progress.last_activity - progress.created_at).days if progress.created_at else 1
        if days_active > 0:
            chapters_per_week = (completed_count / days_active) * 7
        else:
            chapters_per_week = 0

        if chapters_per_week < 0.5:
            pace = "Leisurely"
        elif chapters_per_week < 1:
            pace = "Moderate"
        else:
            pace = "Accelerated"

        # Build analysis for LLM
        analysis_data = {
            "completed_chapters": completed_count,
            "learning_pace": f"{chapters_per_week:.2f} chapters/week",
            "overall_quiz_average": round(avg_score, 1),
            "recent_quiz_average": round(recent_avg, 1),
            "total_quizzes_taken": len(attempts)
        }

        system_prompt = """You are an AI learning coach that provides personalized study guidance.

Analyze the student's performance data and provide:
1. Learning pace assessment
2. Identified strengths (based on good performance)
3. Areas for improvement (based on weak performance)
4. Recommended focus areas
5. Practical study tips
6. Estimated weeks to complete course

Be encouraging and constructive. Focus on actionable advice.

Respond in JSON format:
{
    "learning_pace": "Moderate",
    "strengths": ["strength1", "strength2"],
    "areas_for_improvement": ["area1", "area2"],
    "recommended_focus": ["focus1", "focus2"],
    "study_tips": ["tip1", "tip2", "tip3"],
    "estimated_completion_weeks": 4
}"""

        user_prompt = f"""Provide study guidance for this student:

Performance Data:
{format_analysis(analysis_data)}

Course: 4 chapters total
Available study time: Unknown (ask in follow-up)

Provide personalized guidance in JSON format."""

        response = await llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        import json
        guidance_data = json.loads(response)

        return StudyGuidance(
            learning_pace=guidance_data.get("learning_pace", pace),
            strengths=guidance_data.get("strengths", []),
            areas_for_improvement=guidance_data.get("areas_for_improvement", []),
            recommended_focus=guidance_data.get("recommended_focus", []),
            study_tips=guidance_data.get("study_tips", []),
            estimated_completion_weeks=guidance_data.get("estimated_completion_weeks", 4)
        )

    except LLMClientError as e:
        logger.error(f"LLM error in study guidance: {e}")
        raise MentorServiceError(f"Failed to provide guidance: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in study guidance: {e}")
        raise MentorServiceError(f"Guidance generation failed: {e}")


async def generate_practice_problems(
    topic: str,
    difficulty: str,
    count: int
) -> List[Dict[str, Any]]:
    """
    Generate practice problems for a specific topic.

    Args:
        topic: Topic to generate problems for
        difficulty: beginner/intermediate/advanced
        count: Number of problems to generate

    Returns:
        List of practice problems with solutions
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise MentorServiceError("Phase 2 LLM features are not enabled")

    try:
        system_prompt = f"""You are an AI educational content creator specializing in AI agents, MCP, and ChatGPT app development.

Generate {count} practice problems for the given topic at {difficulty} level.

Each problem should include:
- Description
- Difficulty level
- Estimated time to solve
- Hints (2-3)
- Solution approach
- Learning outcome

Respond in JSON format:
{{
    "problems": [
        {{
            "title": "Problem title",
            "description": "What to do...",
            "difficulty": "{difficulty}",
            "estimated_minutes": 15,
            "hints": ["hint1", "hint2"],
            "solution_approach": "How to solve it...",
            "learning_outcome": "What you'll learn"
        }}
    ]
}}"""

        user_prompt = f"""Generate {count} practice problems for:

Topic: {topic}
Difficulty: {difficulty}
Course Context: AI Agent Development, MCP Integration, ChatGPT Apps

Generate practical, hands-on problems in JSON format."""

        response = await llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        import json
        data = json.loads(response)
        return data.get("problems", [])

    except LLMClientError as e:
        logger.error(f"LLM error in problem generation: {e}")
        raise MentorServiceError(f"Failed to generate problems: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in problem generation: {e}")
        raise MentorServiceError(f"Problem generation failed: {e}")


# Helper functions

def format_chapters_for_mentor(chapters: List[Dict[str, Any]]) -> str:
    """Format chapters for mentor prompt."""
    lines = []
    for ch in chapters:
        lines.append(f"- {ch['title']} (Order: {ch['order']}, Difficulty: {ch['difficulty']})")
    return "\n".join(lines)


def format_analysis(data: Dict[str, Any]) -> str:
    """Format analysis data for prompt."""
    lines = []
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


# =============================================================================
# MentorService Class - Wrapper for v3 API
# =============================================================================


class MentorService:
    """
    AI Mentor service wrapper class for Phase 3 API.

    Provides instance-based interface for mentor functionality.
    Wraps standalone async functions into a class-based API.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize mentor service.

        Args:
            db: Database session
        """
        self.db = db

    async def answer_question(
        self,
        user_id: str,
        question: str,
        chapter_context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Answer student's question using AI.

        Args:
            user_id: User UUID
            question: Student's question
            chapter_context: Optional chapter context
            conversation_history: Optional conversation history

        Returns:
            Dict with answer, follow_up_questions, related_chapters, confidence
        """
        context = {"chapter_context": chapter_context} if chapter_context else None

        # Call the standalone function
        response = await answer_concept_question(
            user_id=user_id,
            question=question,
            context=context,
            db=self.db
        )

        return response.to_dict()

    async def explain_topic(
        self,
        topic: str,
        context: Optional[str] = None,
        complexity_level: str = "intermediate",
        include_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Explain a topic at requested complexity level.

        Args:
            topic: Topic to explain
            context: Optional content context
            complexity_level: beginner/intermediate/advanced
            include_examples: Whether to include examples

        Returns:
            Dict with explanation, examples, analogies, key_points
        """
        llm_client = get_llm_client()
        if not llm_client:
            raise MentorServiceError("Phase 2 LLM features are not enabled")

        try:
            # Build context from course content if available
            context_text = f"\n\nCourse Context:\n{context}" if context else ""

            system_prompt = f"""You are an expert AI tutor explaining concepts about AI agents, MCP, and ChatGPT app development.

Topic: {topic}
Complexity Level: {complexity_level}

Provide a clear explanation with:
1. Main explanation ({complexity_level} level)
2. Real-world examples (if applicable)
3. Helpful analogies
4. Key points to remember

Respond in JSON format:
{{
    "explanation": "Clear explanation...",
    "examples": ["example1", "example2"],
    "analogies": ["analogy1", "analogy2"],
    "key_points": ["point1", "point2", "point3"]
}}"""

            user_prompt = f"""Explain '{topic}' at {complexity_level} level.{context_text}

{"Include practical examples" if include_examples else "Focus on concise explanation"}"""

            response = await llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response)

            return result

        except LLMClientError as e:
            logger.error(f"LLM error in topic explanation: {e}")
            raise MentorServiceError(f"Failed to explain topic: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in topic explanation: {e}")
            raise MentorServiceError(f"Explanation generation failed: {e}")

    async def get_study_guidance(self, user_id: str) -> StudyGuidance:
        """
        Get personalized study recommendations.

        Args:
            user_id: User UUID

        Returns:
            StudyGuidance with recommendations
        """
        return await provide_study_guidance(user_id, self.db)

    async def generate_problems(
        self,
        topic: str,
        difficulty: str = "intermediate",
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate practice problems.

        Args:
            topic: Topic for problems
            difficulty: beginner/intermediate/advanced
            count: Number of problems

        Returns:
            List of practice problems
        """
        return await generate_practice_problems(topic, difficulty, count)
