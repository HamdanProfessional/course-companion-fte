"""
LLM-Enhanced Quiz Service - Phase 2.

Extends Phase 1 rule-based quiz grading with LLM-powered open-ended question grading.
Only active when ENABLE_PHASE_2_LLM=true.
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.llm import get_llm_client, LLMClientError
from src.services.cost_tracking_service import get_cost_tracking_client
from src.models.database import Quiz, Question, QuizAttempt, User
from src.services.quiz_service import QuizService

logger = logging.getLogger(__name__)


class QuizLLMServiceError(Exception):
    """Base exception for quiz LLM service errors."""
    pass


class LLMGradedResponse:
    """LLM grading result for open-ended answers."""

    def __init__(
        self,
        question_id: str,
        score: int,
        max_score: int,
        feedback: str,
        corrections: List[str],
        strengths: List[str],
        suggestions: List[str]
    ):
        self.question_id = question_id
        self.score = score
        self.max_score = max_score
        self.feedback = feedback
        self.corrections = corrections
        self.strengths = strengths
        self.suggestions = suggestions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "score": self.score,
            "max_score": self.max_score,
            "feedback": self.feedback,
            "corrections": self.corrections,
            "strengths": self.strengths,
            "suggestions": self.suggestions
        }


class LLMQuizResult:
    """Complete quiz result with LLM-graded open-ended answers."""

    def __init__(
        self,
        quiz_id: str,
        total_score: int,
        max_score: int,
        percentage: float,
        passed: bool,
        multiple_choice_results: Dict[str, Any],
        llm_graded_results: List[LLMGradedResponse],
        summary: str
    ):
        self.quiz_id = quiz_id
        self.total_score = total_score
        self.max_score = max_score
        self.percentage = percentage
        self.passed = passed
        self.multiple_choice_results = multiple_choice_results
        self.llm_graded_results = llm_graded_results
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quiz_id": self.quiz_id,
            "total_score": self.total_score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "passed": self.passed,
            "multiple_choice_results": self.multiple_choice_results,
            "llm_graded_results": [r.to_dict() for r in self.llm_graded_results],
            "summary": self.summary,
            "graded_by": "llm"
        }


async def grade_quiz_with_llm(
    quiz_id: str,
    user_id: str,
    answers: Dict[str, Any],
    db: AsyncSession
) -> LLMQuizResult:
    """
    Grade quiz with LLM for open-ended questions.

    Process:
    1. Grade multiple-choice questions (rule-based, Phase 1 method)
    2. Grade open-ended questions (LLM-powered)
    3. Combine results for total score
    4. Generate personalized feedback summary

    Args:
        quiz_id: Quiz UUID
        user_id: User UUID
        answers: Dictionary of question_id -> answer
        db: Database session

    Returns:
        LLMQuizResult with combined grading

    Raises:
        QuizLLMServiceError: If grading fails
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise QuizLLMServiceError("Phase 2 LLM features are not enabled")

    try:
        # Fetch quiz with questions
        result = await db.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.id == UUID(quiz_id))
        )
        quiz = result.scalar_one_or_none()

        if not quiz:
            raise QuizLLMServiceError(f"Quiz {quiz_id} not found")

        # Separate multiple-choice and open-ended answers
        mc_answers = {}
        open_answers = {}
        mc_questions = []
        open_questions = []

        for question in quiz.questions:
            q_id = str(question.id)

            if q_id in answers:
                answer = answers[q_id]

                # Check if answer is open-ended (long text)
                if isinstance(answer, str) and len(answer) > 100:
                    open_answers[q_id] = {
                        "question": question.question_text,
                        "answer": answer,
                        "max_score": 30  # Open-ended worth more
                    }
                    open_questions.append(question)
                else:
                    # Multiple choice (A, B, C, D)
                    mc_answers[q_id] = answer
                    mc_questions.append(question)

        # Grade multiple-choice questions (rule-based)
        mc_score = 0
        mc_max_score = 0
        mc_results = {}

        for question in mc_questions:
            q_id = str(question.id)
            user_answer = mc_answers.get(q_id)
            correct_answer = question.correct_answer
            is_correct = user_answer == correct_answer

            if is_correct:
                mc_score += 10  # 10 points per MC question

            mc_max_score += 10

            mc_results[q_id] = {
                "question": question.question_text,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "points_earned": 10 if is_correct else 0,
                "explanation": question.explanation or ""
            }

        # Grade open-ended questions (LLM-powered)
        llm_graded_results = []
        open_score = 0
        open_max_score = 0

        for q_id, answer_data in open_answers.items():
            # Use cost-tracking client for each LLM call
            cost_client = get_cost_tracking_client(str(user_id), "quiz_llm", db)
            if cost_client:
                logger.info(f"Using cost-tracking client for quiz grading (user: {user_id})")
                graded_response = await cost_client.generate(
                    prompt=f"""Grade this student's answer:

Question: {answer_data["question"]}

Student Answer:
{answer_data["answer"]}

Provide grading in JSON format.""",
                    system_prompt="""You are an AI tutor grading open-ended quiz questions about AI agents, MCP, and ChatGPT app development.

Grading Rubric:
- 25-30 points: Excellent (accurate, complete, well-explained)
- 20-24 points: Good (mostly correct, minor gaps)
- 15-19 points: Fair (some correct concepts, significant gaps)
- 10-14 points: Needs Work (minimal understanding)
- 0-9 points: Incorrect (not on track)

Respond in JSON format with keys: score, max_score, feedback, corrections, strengths, suggestions""",
                    temperature=0.3
                )
                # Parse JSON from cost_client response
                import json
                import re
                try:
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', graded_response, re.DOTALL)
                    if json_match:
                        graded_response = json_match.group(1)
                    elif '```' in graded_response:
                        graded_response = re.sub(r'```\w*\n?', '', graded_response).strip()
                    grading = json.loads(graded_response)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from GLM response: {e}")
                    grading = {
                        "score": 15,
                        "max_score": 30,
                        "feedback": "Unable to parse grading. Please try again.",
                        "corrections": [],
                        "strengths": [],
                        "suggestions": ["Review the question and answer more carefully."]
                    }
                graded = LLMGradedResponse(
                    question_id=q_id,
                    score=grading.get("score", 15),
                    max_score=grading.get("max_score", 30),
                    feedback=grading.get("feedback", "Review the course material."),
                    corrections=grading.get("corrections", []),
                    strengths=grading.get("strengths", []),
                    suggestions=grading.get("suggestions", [])
                )
            else:
                # Fallback to original function without cost tracking
                graded = await _grade_open_answer_with_llm(
                    q_id,
                    answer_data["question"],
                    answer_data["answer"],
                    llm_client
                )

            llm_graded_results.append(graded)
            open_score += graded.score
            open_max_score += graded.max_score

        # Calculate totals
        total_score = mc_score + open_score
        max_score = mc_max_score + open_max_score
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= 70

        # Generate summary
        summary = await _generate_quiz_summary(
            quiz.title,
            percentage,
            passed,
            mc_score,
            open_score,
            llm_client
        )

        return LLMQuizResult(
            quiz_id=quiz_id,
            total_score=total_score,
            max_score=max_score,
            percentage=round(percentage, 1),
            passed=passed,
            multiple_choice_results=mc_results,
            llm_graded_results=llm_graded_results,
            summary=summary
        )

    except LLMClientError as e:
        logger.error(f"LLM error in quiz grading: {e}")
        raise QuizLLMServiceError(f"Failed to grade with LLM: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in LLM quiz grading: {e}")
        raise QuizLLMServiceError(f"LLM grading failed: {e}")


async def _grade_open_answer_with_llm(
    question_id: str,
    question_text: str,
    student_answer: str,
    llm_client
) -> LLMGradedResponse:
    """
    Grade open-ended answer using LLM.

    Uses LLM to:
    - Evaluate correctness
    - Identify key concepts covered
    - Point out missing elements
    - Provide constructive feedback
    - Suggest improvements
    """
    system_prompt = """You are an AI tutor grading open-ended quiz questions about AI agents, MCP, and ChatGPT app development.

Your role:
- Evaluate the answer's accuracy and completeness
- Award partial credit for partially correct answers
- Provide constructive, encouraging feedback
- Identify strengths in the answer
- Suggest specific improvements

Grading Rubric:
- 25-30 points: Excellent (accurate, complete, well-explained)
- 20-24 points: Good (mostly correct, minor gaps)
- 15-19 points: Fair (some correct concepts, significant gaps)
- 10-14 points: Needs Work (minimal understanding)
- 0-9 points: Incorrect (not on track)

Respond in JSON format:
{
    "score": 25,
    "max_score": 30,
    "feedback": "Overall feedback...",
    "corrections": [" misconception 1...", "misconception 2..."],
    "strengths": ["strength 1...", "strength 2..."],
    "suggestions": ["suggestion 1...", "suggestion 2..."]
}"""

    user_prompt = f"""Grade this student's answer:

Question: {question_text}

Student Answer:
{student_answer}

Provide grading in JSON format."""

    # Get cost-tracking client if user_id is available
    # Note: We don't have user_id in this function scope, so we skip cost tracking here
    # Cost tracking will be done in the calling function

    response = await llm_client.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.3  # Low temperature for consistent grading
    )

    import json
    import re

    # Try to parse JSON response
    try:
        # GLM might return JSON with markdown code blocks, extract JSON
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        elif '```' in response:
            # Extract content between code blocks
            response = re.sub(r'```\w*\n?', '', response).strip()

        grading = json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from GLM response: {e}")
        logger.error(f"Response was: {response}")
        # Fallback to default grading
        grading = {
            "score": 15,
            "max_score": 30,
            "feedback": "Unable to parse grading. Please try again.",
            "corrections": [],
            "strengths": [],
            "suggestions": ["Review the question and answer more carefully."]
        }

    return LLMGradedResponse(
        question_id=question_id,
        score=grading.get("score", 15),
        max_score=grading.get("max_score", 30),
        feedback=grading.get("feedback", "Review the course material."),
        corrections=grading.get("corrections", []),
        strengths=grading.get("strengths", []),
        suggestions=grading.get("suggestions", [])
    )


async def _generate_quiz_summary(
    quiz_title: str,
    percentage: float,
    passed: bool,
    mc_score: int,
    open_score: int,
    llm_client
) -> str:
    """Generate personalized quiz summary."""
    system_prompt = """You are an encouraging AI tutor providing quiz feedback.

Generate a brief, personalized summary (2-3 sentences) that:
- Acknowledges the student's performance
- Highlights what they did well
- Suggests what to focus on next

Be encouraging and constructive."""

    user_prompt = f"""Generate quiz feedback:

Quiz: {quiz_title}
Score: {percentage:.1f}%
Passed: {"Yes" if passed else "No"}
Multiple Choice: {mc_score} points
Open-Ended: {open_score} points

Provide 2-3 sentences of feedback."""

    response = await llm_client.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )

    return response.strip()


async def generate_quiz_insights(
    quiz_id: str,
    user_attempts: List[QuizAttempt],
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Generate insights from quiz attempts using LLM.

    Analyzes patterns in student's quiz performance to provide:
    - Learning progress over time
    - Consistent weak areas
    - Improvement suggestions
    - Personalized study recommendations

    Args:
        quiz_id: Quiz UUID
        user_attempts: List of user's quiz attempts
        db: Database session

    Returns:
        Insights dictionary with analysis
    """
    llm_client = get_llm_client()
    if not llm_client:
        raise QuizLLMServiceError("Phase 2 LLM features are not enabled")

    try:
        if len(user_attempts) < 2:
            return {
                "insufficient_data": "Take the quiz at least twice to see insights",
                "attempts_count": len(user_attempts)
            }

        # Prepare attempt data
        attempts_data = []
        for attempt in user_attempts:
            attempts_data.append({
                "score": attempt.score,
                "completed_at": attempt.completed_at.isoformat(),
                "answers_count": len(attempt.answers)
            })

        # Calculate trends
        scores = [a["score"] for a in attempts_data]
        avg_score = sum(scores) / len(scores)
        first_score = scores[0]
        last_score = scores[-1]
        improvement = last_score - first_score

        system_prompt = """You are an AI learning analyzer providing quiz performance insights.

Analyze the student's quiz attempts and provide:
1. Progress trend (improving, stable, declining)
2. Consistent strengths
3. Areas needing focus
4. Personalized recommendations

Respond in JSON format:
{
    "trend": "improving|stable|declining",
    "strengths": ["strength1", "strength2"],
    "focus_areas": ["area1", "area2"],
    "recommendations": ["rec1", "rec2"],
    "encouragement": "Encouraging message..."
}"""

        user_prompt = f"""Analyze quiz performance:

Attempts: {len(attempts_data)}
Average Score: {avg_score:.1f}%
First Attempt: {first_score}%
Last Attempt: {last_score}%
Improvement: {improvement:+.1f}%

Provide insights in JSON format."""

        response = await llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        import json
        insights = json.loads(response)

        return {
            "attempts_analyzed": len(user_attempts),
            "average_score": round(avg_score, 1),
            "improvement": round(improvement, 1),
            "trend": insights.get("trend", "stable"),
            "strengths": insights.get("strengths", []),
            "focus_areas": insights.get("focus_areas", []),
            "recommendations": insights.get("recommendations", []),
            "encouragement": insights.get("encouragement", "Keep up the good work!")
        }

    except LLMClientError as e:
        logger.error(f"LLM error in insights generation: {e}")
        raise QuizLLMServiceError(f"Failed to generate insights: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in insights: {e}")
        raise QuizLLMServiceError(f"Insights generation failed: {e}")
