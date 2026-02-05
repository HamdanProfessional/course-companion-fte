"""
SQLAlchemy database models for Course Companion FTE.
Zero-LLM compliance: All data is deterministic, no LLM generation.
"""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    PRO = "PRO"


class DifficultyLevel(str, Enum):
    """Content difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AnswerChoice(str, Enum):
    """Multiple choice answer options."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class User(Base):
    """User account with authentication and subscription tier."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        default="student",
        nullable=False
    )  # "student" or "teacher"
    tier: Mapped[str] = mapped_column(
        String(20),
        default="FREE",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    progress: Mapped[Optional["Progress"]] = relationship(
        "Progress",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    streak: Mapped[Optional["Streak"]] = relationship(
        "Streak",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, tier={self.tier})>"


class Chapter(Base):
    """Course chapter with content stored in R2."""

    __tablename__ = "chapters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    difficulty_level: Mapped[str] = mapped_column(
        String(20),
        default="BEGINNER",
        nullable=False
    )
    estimated_time: Mapped[int] = mapped_column(Integer, default=30)  # Minutes
    r2_content_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Navigation
    next_chapter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID,
        ForeignKey("chapters.id"),
        nullable=True
    )
    previous_chapter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID,
        ForeignKey("chapters.id"),
        nullable=True
    )

    # Relationships
    quiz: Mapped[Optional["Quiz"]] = relationship(
        "Quiz",
        back_populates="chapter",
        uselist=False,
        cascade="all, delete-orphan"
    )
    next_chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter",
        remote_side=[id],
        foreign_keys=[next_chapter_id]
    )
    previous_chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter",
        remote_side=[id],
        foreign_keys=[previous_chapter_id]
    )

    __table_args__ = (
        Index("idx_chapters_order", "order", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, title={self.title}, order={self.order})>"


class Quiz(Base):
    """Quiz associated with a chapter."""

    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("chapters.id"),
        nullable=False,
        unique=True  # One quiz per chapter
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="BEGINNER",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    chapter: Mapped["Chapter"] = relationship(
        "Chapter",
        back_populates="quiz"
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.order"
    )
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_quizzes_chapter_id", "chapter_id"),
    )

    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, title={self.title}, chapter_id={self.chapter_id})>"


class Question(Base):
    """Multiple-choice question within a quiz."""

    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("quizzes.id"),
        nullable=False
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)  # {"A": "...", "B": "...", ...}
    correct_answer: Mapped[str] = mapped_column(
        String(1),
        nullable=False
    )
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")

    __table_args__ = (
        Index("idx_questions_quiz_id", "quiz_id"),
        CheckConstraint("correct_answer IN ('A', 'B', 'C', 'D')", name="check_valid_answer"),
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, quiz_id={self.quiz_id}, order={self.order})>"


class Progress(Base):
    """Student progress through the course."""

    __tablename__ = "progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )
    completed_chapters: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False
    )  # Array of chapter UUID strings
    current_chapter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID,
        ForeignKey("chapters.id"),
        nullable=True
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="progress")
    current_chapter: Mapped[Optional["Chapter"]] = relationship("Chapter")

    __table_args__ = (
        Index("idx_progress_user_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Progress(user_id={self.user_id}, completed={len(self.completed_chapters)})>"


class Streak(Base):
    """Student learning streak for gamification."""

    __tablename__ = "streaks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_checkin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="streak")

    __table_args__ = (
        Index("idx_streaks_user_id", "user_id", unique=True),
        CheckConstraint("current_streak >= 0", name="check_current_streak_non_negative"),
        CheckConstraint("longest_streak >= 0", name="check_longest_streak_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<Streak(user_id={self.user_id}, current={self.current_streak}, longest={self.longest_streak})>"


class QuizAttempt(Base):
    """Record of a student's quiz attempt."""

    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("quizzes.id"),
        nullable=False,
        index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # Percentage (0-100)
    answers: Mapped[dict] = mapped_column(JSON, nullable=False)  # {question_id: answer, ...}
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")

    __table_args__ = (
        Index("idx_quiz_attempts_user_id", "user_id"),
        Index("idx_quiz_attempts_quiz_id", "quiz_id"),
        CheckConstraint("score >= 0 AND score <= 100", name="check_score_range"),
    )

    def __repr__(self) -> str:
        return f"<QuizAttempt(id={self.id}, user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score}%)>"


class LLMCost(Base):
    """Track LLM API costs for Phase 2 features."""

    __tablename__ = "llm_costs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    feature: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # "adaptive", "quiz_llm", "mentor"
    provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # "openai" or "anthropic"
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # e.g., "gpt-4o-mini"
    tokens_used: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    cost_usd: Mapped[float] = mapped_column(  # Cost in USD
        Float,
        nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index("idx_llm_costs_user_id", "user_id"),
        Index("idx_llm_costs_timestamp", "timestamp"),
        CheckConstraint("tokens_used >= 0", name="check_tokens_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<LLMCost(id={self.id}, user_id={self.user_id}, feature={self.feature}, cost=${self.cost_usd:.4f})>"
