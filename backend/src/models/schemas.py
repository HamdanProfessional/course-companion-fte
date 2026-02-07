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
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    PRO = "PRO"


class DifficultyLevel(str, Enum):
    """Content difficulty levels."""
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup."""
        if isinstance(value, str):
            upper_value = value.upper()
            for member in cls:
                if member.value == upper_value:
                    return member
        return None  # or raise ValueError


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

    @validator('difficulty_level', pre=True)
    def normalize_difficulty_level(cls, v):
        """Normalize difficulty level to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v


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


# =============================================================================
# Gamification Schemas
# =============================================================================

# -----------------------------------------------------------------------------
# Tip Schemas
# -----------------------------------------------------------------------------

class TipBase(BaseModel):
    """Base tip schema."""
    content: str
    category: str = Field(..., description="Category: study_habits, quiz_strategy, motivation, course_tips")
    difficulty_level: Optional[str] = Field(None, description="beginner, intermediate, advanced or None for all")


class TipCreate(TipBase):
    """Schema for creating a tip."""
    pass


class Tip(TipBase):
    """Schema for tip response."""
    id: uuid.UUID
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TipList(BaseModel):
    """Schema for list of tips."""
    tips: List[Tip]
    total: int


# -----------------------------------------------------------------------------
# Leaderboard Schemas
# -----------------------------------------------------------------------------

class LeaderboardOptInCreate(BaseModel):
    """Schema for opting into leaderboard."""
    display_name: str = Field(..., min_length=1, max_length=50, description="Anonymous display name")
    show_rank: bool = True
    show_score: bool = True
    show_streak: bool = True


class LeaderboardOptInUpdate(BaseModel):
    """Schema for updating leaderboard opt-in settings."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    is_opted_in: Optional[bool] = None
    show_rank: Optional[bool] = None
    show_score: Optional[bool] = None
    show_streak: Optional[bool] = None


class LeaderboardOptIn(BaseModel):
    """Schema for leaderboard opt-in response."""
    id: uuid.UUID
    user_id: uuid.UUID
    display_name: str
    is_opted_in: bool
    show_rank: bool
    show_score: bool
    show_streak: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Schema for a single leaderboard entry."""
    rank: int
    user_id: uuid.UUID
    display_name: str
    xp: int = Field(..., description="Total experience points")
    average_score: float = Field(..., description="Average quiz score percentage")
    current_streak: int = Field(..., description="Current learning streak")
    completed_chapters: int = Field(..., description="Number of completed chapters")


class Leaderboard(BaseModel):
    """Schema for leaderboard response."""
    leaderboard: List[LeaderboardEntry]
    total_entries: int
    user_rank: Optional[int] = None  # User's rank if they've opted in
    user_xp: Optional[int] = None  # User's XP if they've opted in


# -----------------------------------------------------------------------------
# Certificate Schemas
# -----------------------------------------------------------------------------

class CertificateGenerate(BaseModel):
    """Schema for generating a certificate."""
    student_name: str = Field(..., min_length=1, max_length=255, description="Full name for certificate")


class Certificate(BaseModel):
    """Schema for certificate response."""
    id: uuid.UUID
    certificate_id: str
    user_id: uuid.UUID
    student_name: str
    completion_percentage: int
    average_quiz_score: int
    total_chapters_completed: int
    total_streak_days: int
    issued_at: datetime
    verification_count: int

    class Config:
        from_attributes = True


class CertificateVerification(BaseModel):
    """Schema for certificate verification response."""
    certificate_id: str
    is_valid: bool
    student_name: str
    completion_percentage: int
    average_quiz_score: int
    total_chapters_completed: int
    total_streak_days: int
    issued_at: datetime
    verified_at: datetime
    verification_url: Optional[str] = None


class CertificateList(BaseModel):
    """Schema for list of user certificates."""
    certificates: List[Certificate]
    total: int
