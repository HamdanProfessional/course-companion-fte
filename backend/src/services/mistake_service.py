"""
Mistake Bank Service - Tracks and manages student mistakes for review

Features:
- Track wrong answers from both chapter quizzes and infinite (AI) quizzes
- Mark mistakes as mastered
- Filter by source, category, difficulty
- Export/Import mistakes
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from src.models.database import (
    User,
    QuizAttempt,
    Question,
    Chapter,
    Quiz
)

logger = logging.getLogger(__name__)


class MistakeServiceError(Exception):
    """Base exception for mistake service errors."""
    pass


class MistakeNotFoundError(MistakeServiceError):
    """Raised when a mistake is not found."""
    pass


class MistakeItem:
    """A mistake item (not stored in DB, returned from quiz attempts)."""

    def __init__(
        self,
        id: str,
        question_id: str,
        quiz_id: str,
        quiz_title: str,
        question_text: str,
        wrong_answer: str,
        correct_answer: str,
        explanation: Optional[str] = None,
        feedback: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: str = "beginner",
        date: Optional[str] = None,
        mastered: bool = False,
        times_wrong: int = 1,
        last_reviewed: Optional[str] = None,
        source: str = "chapter",
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
    ):
        self.id = id
        self.question_id = question_id
        self.quiz_id = quiz_id
        self.quiz_title = quiz_title
        self.question_text = question_text
        self.wrong_answer = wrong_answer
        self.correct_answer = correct_answer
        self.explanation = explanation
        self.feedback = feedback
        self.category = category
        self.difficulty = difficulty
        self.date = date or datetime.utcnow().isoformat()
        self.mastered = mastered
        self.times_wrong = times_wrong
        self.last_reviewed = last_reviewed
        self.source = source
        self.topic = topic
        self.subtopic = subtopic

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "quiz_id": str(self.quiz_id),
            "quiz_title": self.quiz_title,
            "question_text": self.question_text,
            "wrong_answer": self.wrong_answer,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "feedback": self.feedback,
            "category": self.category,
            "difficulty": self.difficulty,
            "date": self.date,
            "mastered": self.mastered,
            "times_wrong": self.times_wrong,
            "last_reviewed": self.last_reviewed,
            "source": self.source,
            "topic": self.topic,
            "subtopic": self.subtopic,
        }


class MistakeService:
    """Service for managing student mistakes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_mistakes_from_chapter_quizzes(
        self,
        user_id: UUID,
        limit: int = 100
    ) -> List[MistakeItem]:
        """
        Get mistakes from chapter quiz attempts.

        Finds questions where the student got wrong answers and aggregates
        by question to count how many times each was answered incorrectly.
        """
        # Get all quiz attempts for this user
        result = await self.db.execute(
            select(QuizAttempt, Quiz, Chapter)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .join(Chapter, Quiz.chapter_id == Chapter.id)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.desc())
        )

        attempts = result.all()

        # Track mistakes by question_id to aggregate times_wrong
        question_mistakes: Dict[str, Dict[str, Any]] = {}

        for attempt, quiz, chapter in attempts:
            # Get questions for this quiz
            questions_result = await self.db.execute(
                select(Question).where(Question.quiz_id == quiz.id)
            )
            questions = questions_result.scalars().all()

            # Check each question to see if student got it wrong
            for question in questions:
                question_id_str = str(question.id)

                # Get the user's answer for this question
                user_answer = attempt.answers.get(question_id_str) if attempt.answers else None

                # Get correct answer - handle both string and enum types
                correct_answer = question.correct_answer
                if hasattr(correct_answer, 'value'):
                    correct_answer = correct_answer.value

                # Check if the answer is wrong OR not answered
                # Only count if it was actually answered (not None/empty)
                is_wrong = (
                    user_answer is not None and
                    user_answer != "" and
                    str(user_answer) != str(correct_answer)
                )

                if is_wrong:
                    # This question was answered wrong
                    if question_id_str not in question_mistakes:
                        # First time this question was wrong
                        question_mistakes[question_id_str] = {
                            "question": question,
                            "quiz": quiz,
                            "chapter": chapter,
                            "times_wrong": 0,
                            "wrong_answer": user_answer,
                            "last_attempt": attempt,
                        }

                    # Increment the count
                    question_mistakes[question_id_str]["times_wrong"] += 1

                    # Update if this is a more recent attempt
                    if attempt.completed_at and (
                        not question_mistakes[question_id_str]["last_attempt"].completed_at or
                        attempt.completed_at > question_mistakes[question_id_str]["last_attempt"].completed_at
                    ):
                        question_mistakes[question_id_str]["last_attempt"] = attempt
                        question_mistakes[question_id_str]["wrong_answer"] = user_answer

        # Convert tracked mistakes to MistakeItem objects
        mistakes = []
        for question_id_str, mistake_data in question_mistakes.items():
            question = mistake_data["question"]
            quiz = mistake_data["quiz"]
            chapter = mistake_data["chapter"]
            attempt = mistake_data["last_attempt"]

            mistakes.append(
                MistakeItem(
                    id=f"{attempt.id}_{question.id}",
                    question_id=str(question.id),
                    quiz_id=str(quiz.id),
                    quiz_title=f"Chapter {chapter.order}: {chapter.title}",
                    question_text=question.question_text,
                    wrong_answer=mistake_data["wrong_answer"] or "Review needed",
                    correct_answer=question.correct_answer.value if hasattr(question.correct_answer, 'value') else str(question.correct_answer),
                    explanation=question.explanation,
                    category=chapter.title,
                    difficulty=quiz.difficulty or "beginner",
                    date=attempt.completed_at.isoformat() if attempt.completed_at else None,
                    times_wrong=mistake_data["times_wrong"],
                    source="chapter",
                )
            )

        # Sort by times_wrong (descending) and then by date (most recent first)
        mistakes.sort(key=lambda m: (-m.times_wrong, m.date or ""))

        return mistakes[:limit]

    async def get_mistake_stats(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get statistics about user's mistakes."""
        # Get total quiz attempts
        total_attempts_result = await self.db.execute(
            select(func.count(QuizAttempt.id)).where(
                QuizAttempt.user_id == user_id
            )
        )
        total_attempts = total_attempts_result.scalar() or 0

        # Get average score
        avg_score_result = await self.db.execute(
            select(func.avg(QuizAttempt.score)).where(
                QuizAttempt.user_id == user_id
            )
        )
        avg_score = avg_score_result.scalar() or 0

        # Get mistakes count (attempts with wrong answers)
        mistakes_count_result = await self.db.execute(
            select(func.count(QuizAttempt.id)).where(
                and_(
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.score < 100
                )
            )
        )
        mistakes_count = mistakes_count_result.scalar() or 0

        return {
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 1),
            "mistakes_count": mistakes_count,
            "by_category": {},  # Would need detailed tracking
            "by_difficulty": {},  # Would need detailed tracking
        }

    async def add_infinite_quiz_mistake(
        self,
        user_id: UUID,
        question_data: Dict[str, Any],
        wrong_answer: str
    ) -> MistakeItem:
        """
        Add a mistake from infinite (AI-generated) quiz.

        Note: Currently this just returns the item without storing.
        In production, you'd want to store these in a dedicated table.
        """
        return MistakeItem(
            id=str(uuid4()),
            question_id=question_data.get("id", ""),
            quiz_id="infinite-quiz",
            quiz_title=f"AI Quiz: {question_data.get('topic', 'General')}",
            question_text=question_data.get("question_text", ""),
            wrong_answer=wrong_answer,
            correct_answer=question_data.get("correct_answer", ""),
            explanation=question_data.get("explanation", ""),
            category=question_data.get("topic"),
            difficulty=question_data.get("difficulty", "beginner"),
            source="infinite",
            topic=question_data.get("topic"),
            subtopic=question_data.get("subtopic"),
        )

    async def export_mistakes(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Export mistakes for backup."""
        mistakes = await self.get_mistakes_from_chapter_quizzes(user_id)

        return {
            "user_id": str(user_id),
            "export_date": datetime.utcnow().isoformat(),
            "total_mistakes": len(mistakes),
            "mistakes": [m.to_dict() for m in mistakes],
        }
