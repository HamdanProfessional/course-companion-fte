"""
Pydantic schemas for request/response validation.
Zero-LLM compliance: All schemas are deterministic, no LLM generation.
"""

import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, validator


# =============================================================================
# Enums
# =============================================================================

class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"


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


# =============================================================================
# User Schemas
# =============================================================================

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    @validator("password")
    def validate_password(cls, v):
        """Ensure password has at least one letter and one number."""
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: uuid.UUID
    email: str
    tier: UserTier
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserTierUpdate(BaseModel):
    """Schema for updating user tier."""
    new_tier: UserTier = Field(..., description="New subscription tier")


# =============================================================================
# Chapter Schemas
# =============================================================================

class ChapterBase(BaseModel):
    """Base chapter schema."""
    title: str
    order: int
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    estimated_time: int = Field(default=30, description="Estimated reading time in minutes")


class ChapterCreate(ChapterBase):
    """Schema for creating a chapter."""
    content: Optional[str] = None
    r2_content_key: Optional[str] = None


class Chapter(ChapterBase):
    """Schema for chapter response (list view)."""
    id: uuid.UUID
    difficulty_level: DifficultyLevel
    estimated_time: int

    class Config:
        from_attributes = True


class ChapterDetail(Chapter):
    """Schema for chapter detail (full content)."""
    content: Optional[str] = None
    r2_content_key: Optional[str] = None
    quiz_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class ChapterList(BaseModel):
    """Schema for list of chapters."""
    chapters: List[Chapter]
    total: int


# =============================================================================
# Quiz Schemas
# =============================================================================

class QuestionBase(BaseModel):
    """Base question schema."""
    question_text: str
    options: Dict[str, str] = Field(..., description="Multiple choice options (A, B, C, D)")
    explanation: Optional[str] = None
    order: int

    @validator("options")
    def validate_options(cls, v):
        """Ensure exactly 4 options (A, B, C, D)."""
        required_keys = {"A", "B", "C", "D"}
        if set(v.keys()) != required_keys:
            raise ValueError("Options must contain exactly 4 keys: A, B, C, D")
        return v


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    correct_answer: AnswerChoice


class Question(QuestionBase):
    """Schema for question response (without correct answer)."""
    id: uuid.UUID
    quiz_id: uuid.UUID

    class Config:
        from_attributes = True


class QuestionWithAnswer(Question):
    """Schema for question with correct answer (admin only)."""
    correct_answer: AnswerChoice


class QuizBase(BaseModel):
    """Base quiz schema."""
    title: str
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER


class QuizCreate(QuizBase):
    """Schema for creating a quiz."""
    chapter_id: uuid.UUID


class Quiz(QuizBase):
    """Schema for quiz response."""
    id: uuid.UUID
    chapter_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class QuizWithQuestions(Quiz):
    """Schema for quiz with questions."""
    questions: List[Question]


class QuizSubmission(BaseModel):
    """Schema for submitting quiz answers."""
    answers: Dict[str, AnswerChoice] = Field(..., description="Map of question_id to selected answer")


class QuizResultItem(BaseModel):
    """Schema for individual question result."""
    question_id: uuid.UUID
    question_text: str
    selected_answer: AnswerChoice
    correct_answer: AnswerChoice
    is_correct: bool
    explanation: Optional[str] = None


class QuizResult(BaseModel):
    """Schema for quiz grading result."""
    quiz_id: uuid.UUID
    score: int = Field(..., ge=0, le=100, description="Score as percentage (0-100)")
    passed: bool = Field(..., description="Passed if score >= 70%")
    total_questions: int
    correct_answers: int
    results: List[QuizResultItem]


# =============================================================================
# Progress Schemas
# =============================================================================

class ProgressBase(BaseModel):
    """Base progress schema."""
    completed_chapters: List[str] = Field(default_factory=list, description="List of completed chapter IDs")
    current_chapter_id: Optional[uuid.UUID] = None


class ProgressCreate(ProgressBase):
    """Schema for creating progress."""
    user_id: uuid.UUID


class ProgressUpdate(BaseModel):
    """Schema for updating progress."""
    chapter_id: uuid.UUID = Field(..., description="Chapter ID to mark as complete")


class Progress(ProgressBase):
    """Schema for progress response."""
    id: uuid.UUID
    user_id: uuid.UUID
    completion_percentage: float = Field(..., description="Percentage of course completed")
    last_activity: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Streak Schemas
# =============================================================================

class StreakBase(BaseModel):
    """Base streak schema."""
    current_streak: int = Field(default=0, ge=0)
    longest_streak: int = Field(default=0, ge=0)
    last_checkin: Optional[date] = None


class StreakCreate(StreakBase):
    """Schema for creating streak."""
    user_id: uuid.UUID


class StreakUpdate(BaseModel):
    """Schema for updating streak (checkin)."""
    pass  # Automatic calculation


class Streak(StreakBase):
    """Schema for streak response."""
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True


# =============================================================================
# Access Control Schemas
# =============================================================================

class AccessCheck(BaseModel):
    """Schema for access check request."""
    user_id: uuid.UUID
    resource: str = Field(..., description="Resource to check access for (e.g., 'chapter-4')")


class AccessResponse(BaseModel):
    """Schema for access check response."""
    access_granted: bool
    tier: UserTier
    reason: Optional[str] = None
    upgrade_url: Optional[str] = None


class TierUpdateResponse(BaseModel):
    """Schema for tier update response."""
    user_id: uuid.UUID
    old_tier: UserTier
    new_tier: UserTier
    upgraded_at: datetime


# =============================================================================
# Search Schemas
# =============================================================================

class SearchResult(BaseModel):
    """Schema for search result item."""
    chapter_id: uuid.UUID
    title: str
    snippet: str = Field(..., description="Relevant content snippet")
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str
    results: List[SearchResult]
    total: int


# =============================================================================
# Common Schemas
# =============================================================================

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str


class MessageResponse(BaseModel):
    """Schema for generic message response."""
    message: str
