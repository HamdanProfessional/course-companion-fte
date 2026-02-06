"""
Pytest configuration and fixtures for backend tests.
"""

import os
import sys
import asyncio
import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.api.main import app
from src.core.database import async_session_maker, engine, Base
from src.models.database import (
    User,
    Chapter,
    Quiz,
    Question,
    Progress,
    Streak,
    QuizAttempt,
)


# ============================================================================
# Test Data
# ============================================================================

TEST_USERS = {
    "free": {
        "id": uuid.UUID("82b8b862-059a-416a-9ef4-e582a4870efa"),
        "email": "demo@example.com",
        "password": "password123",
        "tier": "FREE",
    },
    "premium": {
        "id": uuid.uuid4(),
        "email": "premium@example.com",
        "password": "password123",
        "tier": "PREMIUM",
    },
    "pro": {
        "id": uuid.uuid4(),
        "email": "pro@example.com",
        "password": "password123",
        "tier": "PRO",
    },
}


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Initialize database tables for testing."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup after all tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with async_session_maker() as session:
        # Start a transaction
        async with session.begin():
            yield session
        # Rollback after test


@pytest_asyncio.fixture
async def clean_db_session(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session with test data."""
    # Clear existing data
    await db_session.execute(QuizAttempt.__table__.delete())
    await db_session.execute(Streak.__table__.delete())
    await db_session.execute(Progress.__table__.delete())
    await db_session.execute(Question.__table__.delete())
    await db_session.execute(Quiz.__table__.delete())
    await db_session.execute(Chapter.__table__.delete())
    await db_session.execute(User.__table__.delete())

    # Create test users
    for user_type, user_data in TEST_USERS.items():
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            tier=user_data["tier"],
            created_at=datetime.utcnow() - timedelta(days=30),
            last_login=datetime.utcnow() - timedelta(hours=1),
        )
        db_session.add(user)

    await db_session.commit()
    yield db_session


@pytest_asyncio.fixture
async def test_users(clean_db_session: AsyncSession) -> Dict[str, User]:
    """Return test users from database."""
    users = {}
    for user_type, user_data in TEST_USERS.items():
        result = await clean_db_session.execute(
            select(User).where(User.id == user_data["id"])
        )
        user = result.scalar_one()
        users[user_type] = user
    return users


# ============================================================================
# API Client Fixture
# ============================================================================

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Auth Helper Functions
# ============================================================================

async def get_auth_token(client: AsyncClient, email: str, password: str) -> str:
    """Get authentication token for user."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest_asyncio.fixture
async def auth_headers_free(client: AsyncClient) -> Dict[str, str]:
    """Return auth headers for FREE user."""
    token = await get_auth_token(
        client,
        TEST_USERS["free"]["email"],
        TEST_USERS["free"]["password"]
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_premium(client: AsyncClient) -> Dict[str, str]:
    """Return auth headers for PREMIUM user."""
    token = await get_auth_token(
        client,
        TEST_USERS["premium"]["email"],
        TEST_USERS["premium"]["password"]
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_pro(client: AsyncClient) -> Dict[str, str]:
    """Return auth headers for PRO user."""
    token = await get_auth_token(
        client,
        TEST_USERS["pro"]["email"],
        TEST_USERS["pro"]["password"]
    )
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Content Data Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_chapters(clean_db_session: AsyncSession) -> list[Chapter]:
    """Create test chapters."""
    chapters = []
    chapters_data = [
        {
            "order": 1,
            "title": "Introduction to AI Agents",
            "content": "# Introduction\n\nThis is chapter 1 content.",
            "difficulty": "beginner",
            "estimated_time": 30,
        },
        {
            "order": 2,
            "title": "Agent Architectures",
            "content": "# Architectures\n\nThis is chapter 2 content.",
            "difficulty": "beginner",
            "estimated_time": 45,
        },
        {
            "order": 3,
            "title": "Multi-Agent Systems",
            "content": "# Multi-Agent\n\nThis is chapter 3 content.",
            "difficulty": "intermediate",
            "estimated_time": 60,
        },
    ]

    for chapter_data in chapters_data:
        chapter = Chapter(
            id=uuid.uuid4(),
            title=chapter_data["title"],
            content=chapter_data["content"],
            order=chapter_data["order"],
            difficulty_level=chapter_data["difficulty"],
            estimated_time=chapter_data["estimated_time"]
        )
        clean_db_session.add(chapter)
        chapters.append(chapter)

    await clean_db_session.commit()

    # Set navigation links
    await clean_db_session.refresh(chapters[0])
    await clean_db_session.refresh(chapters[1])
    await clean_db_session.refresh(chapters[2])

    chapters[0].next_chapter_id = chapters[1].id
    chapters[1].previous_chapter_id = chapters[0].id
    chapters[1].next_chapter_id = chapters[2].id
    chapters[2].previous_chapter_id = chapters[1].id

    await clean_db_session.commit()
    return chapters


@pytest_asyncio.fixture
async def test_quizzes(clean_db_session: AsyncSession, test_chapters: list[Chapter]) -> list[Quiz]:
    """Create test quizzes with questions."""
    quizzes = []

    for chapter in test_chapters[:2]:  # Create quizzes for first 2 chapters
        quiz = Quiz(
            id=uuid.uuid4(),
            chapter_id=chapter.id,
            title=f"{chapter.title} Quiz",
            difficulty=chapter.difficulty_level.upper(),
        )
        clean_db_session.add(quiz)
        quizzes.append(quiz)

    await clean_db_session.commit()

    # Add questions to quizzes
    for i, quiz in enumerate(quizzes):
        for j in range(3):  # 3 questions per quiz
            question = Question(
                id=uuid.uuid4(),
                quiz_id=quiz.id,
                question_text=f"Question {j+1} for quiz {i+1}",
                options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                correct_answer="A",
                explanation="Explanation for the answer",
                order=j + 1,
            )
            clean_db_session.add(question)

    await clean_db_session.commit()
    return quizzes


@pytest_asyncio.fixture
async def test_progress(
    clean_db_session: AsyncSession,
    test_users: Dict[str, User],
    test_chapters: list[Chapter]
) -> Dict[str, Progress]:
    """Create test progress records."""
    progress_records = {}

    # FREE user: 1 chapter completed
    free_progress = Progress(
        id=uuid.uuid4(),
        user_id=test_users["free"].id,
        completed_chapters=[str(test_chapters[0].id)],
        current_chapter_id=test_chapters[0].id,
        last_activity=datetime.utcnow() - timedelta(hours=2)
    )
    clean_db_session.add(free_progress)
    progress_records["free"] = free_progress

    # PREMIUM user: 2 chapters completed
    premium_progress = Progress(
        id=uuid.uuid4(),
        user_id=test_users["premium"].id,
        completed_chapters=[str(test_chapters[0].id), str(test_chapters[1].id)],
        current_chapter_id=test_chapters[1].id,
        last_activity=datetime.utcnow() - timedelta(hours=6)
    )
    clean_db_session.add(premium_progress)
    progress_records["premium"] = premium_progress

    await clean_db_session.commit()
    return progress_records


@pytest_asyncio.fixture
async def test_streaks(
    clean_db_session: AsyncSession,
    test_users: Dict[str, User]
) -> Dict[str, Streak]:
    """Create test streak records."""
    streaks = {}

    # FREE user: 5 day streak
    free_streak = Streak(
        id=uuid.uuid4(),
        user_id=test_users["free"].id,
        current_streak=5,
        longest_streak=5,
    )
    clean_db_session.add(free_streak)
    streaks["free"] = free_streak

    # PREMIUM user: 15 day streak
    premium_streak = Streak(
        id=uuid.uuid4(),
        user_id=test_users["premium"].id,
        current_streak=15,
        longest_streak=15,
    )
    clean_db_session.add(premium_streak)
    streaks["premium"] = premium_streak

    await clean_db_session.commit()
    return streaks
