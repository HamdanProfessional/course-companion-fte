"""
Pydantic schemas for teacher dashboard API responses.
Matches frontend TypeScript interfaces from web-app/src/hooks/useTeacher.ts
Zero-LLM compliance: All responses are deterministic database data.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# =============================================================================
# Dashboard Statistics
# =============================================================================

class TeacherStats(BaseModel):
    """Overall teacher dashboard statistics."""
    total_students: int = Field(..., description="Total number of student accounts")
    active_students: int = Field(..., description="Students active in last 7 days")
    average_score: float = Field(..., description="Average quiz score across all students")
    completion_rate: float = Field(..., description="Average course completion rate")
    students_at_risk: int = Field(..., description="Number of at-risk students")
    students_failing_quizzes: int = Field(..., description="Students with avg score < 70%")
    students_with_stale_streaks: int = Field(..., description="Students with zero streak")

    class Config:
        json_schema_extra = {
            "example": {
                "total_students": 156,
                "active_students": 89,
                "average_score": 78.5,
                "completion_rate": 42.3,
                "students_at_risk": 12,
                "students_failing_quizzes": 8,
                "students_with_stale_streaks": 23
            }
        }


# =============================================================================
# Student Data
# =============================================================================

class TeacherStudent(BaseModel):
    """Student with progress information for teacher dashboard."""
    user_id: str = Field(..., description="Student user ID")
    name: str = Field(..., description="Student display name (from email)")
    email: str = Field(..., description="Student email address")
    progress: float = Field(..., description="Course completion percentage (0-100)")
    streak: int = Field(..., description="Current learning streak")
    last_activity: str = Field(..., description="ISO timestamp of last activity")
    tier: str = Field(..., description="Subscription tier (FREE, PRO, PREMIUM)")
    quiz_scores: Optional[List[float]] = Field(None, description="Last 10 quiz scores")
    completed_chapters: Optional[int] = Field(None, description="Number of completed chapters")
    total_chapters: Optional[int] = Field(None, description="Total number of chapters")
    joined_date: Optional[str] = Field(None, description="ISO timestamp of account creation")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "john.doe",
                "email": "john.doe@example.com",
                "progress": 65.5,
                "streak": 7,
                "last_activity": "2026-02-07T10:30:00Z",
                "tier": "PRO",
                "quiz_scores": [85, 90, 78, 92, 88],
                "completed_chapters": 13,
                "total_chapters": 20,
                "joined_date": "2026-01-15T08:00:00Z"
            }
        }


# =============================================================================
# Quiz Statistics
# =============================================================================

class QuizStats(BaseModel):
    """Overall quiz performance statistics."""
    total_attempts: int = Field(..., description="Total quiz attempts across all students")
    average_score: float = Field(..., description="Average quiz score (0-100)")
    pass_rate: float = Field(..., description="Percentage of attempts with score >= 70%")
    completion_rate: float = Field(..., description="Percentage of students who attempted quizzes")

    class Config:
        json_schema_extra = {
            "example": {
                "total_attempts": 342,
                "average_score": 78.2,
                "pass_rate": 85.4,
                "completion_rate": 67.8
            }
        }


# =============================================================================
# Quiz Performance Data
# =============================================================================

class QuizPerformance(BaseModel):
    """Per-quiz performance breakdown."""
    quiz_id: str = Field(..., description="Quiz ID")
    quiz_title: str = Field(..., description="Quiz title")
    total_attempts: int = Field(..., description="Number of attempts for this quiz")
    average_score: float = Field(..., description="Average score for this quiz (0-100)")
    highest_score: float = Field(..., description="Highest score achieved")
    lowest_score: float = Field(..., description="Lowest score achieved")
    pass_rate: float = Field(..., description="Percentage of attempts with score >= 70%")

    class Config:
        json_schema_extra = {
            "example": {
                "quiz_id": "123e4567-e89b-12d3-a456-426614174001",
                "quiz_title": "Introduction to Neural Networks",
                "total_attempts": 45,
                "average_score": 82.3,
                "highest_score": 100.0,
                "lowest_score": 45.0,
                "pass_rate": 91.1
            }
        }


# =============================================================================
# Question Analysis
# =============================================================================

class QuestionAnalysis(BaseModel):
    """Question-level analytics for difficulty assessment."""
    question_id: str = Field(..., description="Question ID")
    question_text: str = Field(..., description="Question text (truncated to 100 chars)")
    total_attempts: int = Field(..., description="Number of times question was attempted")
    correct_rate: float = Field(..., description="Percentage of correct answers (0-100)")
    average_time: float = Field(..., description="Average time to answer (seconds)")
    difficulty: str = Field(..., description="Difficulty level: easy, medium, or hard")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "123e4567-e89b-12d3-a456-426614174002",
                "question_text": "What is the primary function of a neural network's hidden layer?",
                "total_attempts": 156,
                "correct_rate": 78.5,
                "average_time": 45.2,
                "difficulty": "medium"
            }
        }


# =============================================================================
# Engagement Metrics
# =============================================================================

class EngagementMetrics(BaseModel):
    """Student engagement metrics for teacher dashboard."""
    average_session_time: str = Field(..., description="Average session duration (e.g., '25 min')")
    active_students: int = Field(..., description="Number of active students in last 7 days")
    completion_rate: float = Field(..., description="Average course completion rate")
    weekly_activity: List[int] = Field(..., description="Activity count for last 7 days")

    class Config:
        json_schema_extra = {
            "example": {
                "average_session_time": "25 min",
                "active_students": 89,
                "completion_rate": 42.3,
                "weekly_activity": [45, 62, 58, 71, 69, 54, 38]
            }
        }


# =============================================================================
# At-Risk Students
# =============================================================================

class AtRiskStudent(BaseModel):
    """Student identified as at-risk with specific factors."""
    user_id: str = Field(..., description="Student user ID")
    name: str = Field(..., description="Student display name")
    email: str = Field(..., description="Student email address")
    risk_level: str = Field(..., description="Risk level: high, medium, or low")
    risk_factors: List[str] = Field(..., description="List of identified risk factors")
    last_activity: str = Field(..., description="ISO timestamp of last activity")
    progress: float = Field(..., description="Course completion percentage")
    streak: int = Field(..., description="Current learning streak")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174003",
                "name": "jane.smith",
                "email": "jane.smith@example.com",
                "risk_level": "high",
                "risk_factors": [
                    "No activity for 7+ days",
                    "Quiz average below 60%",
                    "Zero current streak"
                ],
                "last_activity": "2026-01-28T15:45:00Z",
                "progress": 15.5,
                "streak": 0
            }
        }


# =============================================================================
# Recent Activity
# =============================================================================

class RecentActivity(BaseModel):
    """Recent student activity feed item."""
    activity_id: str = Field(..., description="Unique activity identifier")
    student_name: str = Field(..., description="Student display name")
    activity_type: str = Field(..., description="Type of activity")
    description: str = Field(..., description="Human-readable activity description")
    timestamp: str = Field(..., description="ISO timestamp of activity")

    class Config:
        json_schema_extra = {
            "example": {
                "activity_id": "act_1234567890",
                "student_name": "john.doe",
                "activity_type": "quiz_completed",
                "description": "Completed 'Introduction to Neural Networks' quiz with score 85%",
                "timestamp": "2026-02-07T10:30:00Z"
            }
        }
