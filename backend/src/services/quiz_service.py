"""
Quiz service business logic.
Zero-LLM compliance: Rule-based grading only, no LLM evaluation.
"""

from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.database import Quiz, Question, QuizAttempt
from src.models.schemas import (
    QuizWithQuestions,
    QuizSubmission,
    QuizResult,
    QuizResultItem,
    AnswerChoice
)


class QuizService:
    """Business logic for quiz management and grading."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_quiz(self, quiz_id: str) -> QuizWithQuestions:
        """
        Get quiz with questions (without correct answers).

        Args:
            quiz_id: Quiz UUID

        Returns:
            Quiz with questions
        """
        result = await self.db.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.id == quiz_id)
        )
        quiz = result.scalar_one_or_none()
        if not quiz:
            return None

        return QuizWithQuestions(
            id=str(quiz.id),
            title=quiz.title,
            difficulty=quiz.difficulty,
            chapter_id=str(quiz.chapter_id),
            created_at=quiz.created_at,
            questions=[
                {
                    "id": str(q.id),
                    "quiz_id": str(q.quiz_id),
                    "question_text": q.question_text,
                    "options": q.options,
                    "explanation": q.explanation,
                    "order": q.order,
                }
                for q in quiz.questions
            ]
        )

    async def list_quizzes(self) -> List[QuizWithQuestions]:
        """
        List all quizzes.

        Returns:
            List of quizzes
        """
        result = await self.db.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions))
        )
        quizzes = result.scalars().all()

        return [
            QuizWithQuestions(
                id=str(quiz.id),
                title=quiz.title,
                difficulty=quiz.difficulty,
                chapter_id=str(quiz.chapter_id),
                created_at=quiz.created_at,
                questions=[]
            )
            for quiz in quizzes
        ]

    async def grade_quiz(
        self,
        quiz_id: str,
        user_id: str,
        submission: QuizSubmission
    ) -> QuizResult:
        """
        Grade quiz submission using rule-based answer key matching.
        Zero-LLM: Deterministic grading, no AI evaluation.

        Args:
            quiz_id: Quiz UUID
            user_id: User UUID
            submission: Quiz submission with answers

        Returns:
            Quiz results with score and detailed feedback
        """
        # Get quiz with questions (including correct answers)
        result = await self.db.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.id == quiz_id)
        )
        quiz = result.scalar_one_or_none()
        if not quiz:
            return None

        # Grade each question
        results = []
        correct_count = 0

        for question in quiz.questions:
            question_id_str = str(question.id)
            selected_answer = submission.answers.get(question_id_str)
            correct_answer = question.correct_answer

            # Determine if correct
            is_correct = selected_answer == correct_answer if selected_answer else False
            if is_correct:
                correct_count += 1

            results.append(QuizResultItem(
                question_id=question_id_str,
                question_text=question.question_text,
                selected_answer=selected_answer or AnswerChoice.A,  # Default if not answered
                correct_answer=correct_answer,
                is_correct=is_correct,
                explanation=question.explanation,
            ))

        # Calculate score percentage
        total_questions = len(quiz.questions)
        score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
        passed = score >= 70

        # Record attempt
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            answers=submission.answers,
        )
        self.db.add(attempt)
        await self.db.commit()

        return QuizResult(
            quiz_id=quiz_id,
            score=score,
            passed=passed,
            total_questions=total_questions,
            correct_answers=correct_count,
            results=results
        )

    async def get_quiz_results(
        self,
        quiz_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get user's quiz attempt history.

        Args:
            quiz_id: Quiz UUID
            user_id: User UUID
            limit: Maximum attempts to return

        Returns:
            List of quiz attempts
        """
        result = await self.db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
        )
        attempts = result.scalars().all()

        return [
            {
                "id": str(attempt.id),
                "score": attempt.score,
                "completed_at": attempt.completed_at.isoformat(),
            }
            for attempt in attempts
        ]
