"""
Quiz flow integration tests.
Tests quiz listing, submission, grading, and history.
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Quiz, Question, QuizAttempt


@pytest.mark.asyncio
async def test_list_quizzes(client: AsyncClient, test_quizzes: list[Quiz]):
    """Test listing all quizzes."""
    response = await client.get("/api/v1/quizzes")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # We created 2 quizzes
    assert "id" in data[0]
    assert "title" in data[0]
    assert "difficulty" in data[0]


@pytest.mark.asyncio
async def test_get_quiz_details(client: AsyncClient, test_quizzes: list[Quiz]):
    """Test getting quiz details with questions."""
    quiz_id = test_quizzes[0].id
    response = await client.get(f"/api/v1/quizzes/{quiz_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(quiz_id)
    assert "title" in data
    assert "questions" in data
    assert len(data["questions"]) == 3  # We created 3 questions per quiz
    assert "question_text" in data["questions"][0]
    assert "options" in data["questions"][0]
    # Note: correct_answer is NOT included in quiz details (to prevent cheating)


@pytest.mark.asyncio
async def test_submit_quiz_perfect_score(
    client: AsyncClient,
    test_quizzes: list[Quiz],
    test_users: dict,
    clean_db_session: AsyncSession
):
    """Test quiz submission with all correct answers."""
    quiz_id = test_quizzes[0].id
    user_id = test_users["free"].id

    # Get questions to submit correct answers
    result = await clean_db_session.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    questions = result.scalars().all()

    # Submit all correct answers
    answers = {
        str(question.id): question.correct_answer
        for question in questions
    }

    response = await client.post(
        f"/api/v1/quizzes/{quiz_id}/submit?user_id={user_id}",
        json={"answers": answers}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["quiz_id"] == str(quiz_id)
    assert data["total_score"] == 30  # 3 questions * 10 points each
    assert data["max_score"] == 30
    assert data["percentage"] == 100
    assert data["passed"] is True
    assert len(data["results"]) == 3
    assert all(r["is_correct"] for r in data["results"])


@pytest.mark.asyncio
async def test_submit_quiz_partial_score(
    client: AsyncClient,
    test_quizzes: list[Quiz],
    test_users: dict,
    clean_db_session: AsyncSession
):
    """Test quiz submission with some correct answers."""
    quiz_id = test_quizzes[0].id
    user_id = test_users["free"].id

    # Get questions
    result = await clean_db_session.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    questions = result.scalars().all()

    # Submit 2 correct, 1 wrong
    answers = {}
    for i, question in enumerate(questions):
        if i < 2:
            answers[str(question.id)] = question.correct_answer
        else:
            # Wrong answer
            answers[str(question.id)] = "B" if question.correct_answer != "B" else "A"

    response = await client.post(
        f"/api/v1/quizzes/{quiz_id}/submit?user_id={user_id}",
        json={"answers": answers}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["percentage"] == 66.67  # 2/3 correct
    assert data["passed"] is True  # Default passing is 60%


@pytest.mark.asyncio
async def test_submit_quiz_failing_score(
    client: AsyncClient,
    test_quizzes: list[Quiz],
    test_users: dict,
    clean_db_session: AsyncSession
):
    """Test quiz submission with failing score."""
    quiz_id = test_quizzes[0].id
    user_id = test_users["free"].id

    # Get questions
    result = await clean_db_session.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    questions = result.scalars().all()

    # Submit all wrong answers
    answers = {}
    for question in questions:
        answers[str(question.id)] = "B" if question.correct_answer != "B" else "A"

    response = await client.post(
        f"/api/v1/quizzes/{quiz_id}/submit?user_id={user_id}",
        json={"answers": answers}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["percentage"] == 0
    assert data["passed"] is False


@pytest.mark.asyncio
async def test_submit_quiz_creates_attempt_record(
    client: AsyncClient,
    test_quizzes: list[Quiz],
    test_users: dict,
    clean_db_session: AsyncSession
):
    """Test that quiz submission creates attempt record in database."""
    quiz_id = test_quizzes[0].id
    user_id = test_users["free"].id

    # Get questions
    result = await clean_db_session.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    questions = result.scalars().all()

    answers = {str(q.id): q.correct_answer for q in questions}

    # Submit quiz
    await client.post(
        f"/api/v1/quizzes/{quiz_id}/submit?user_id={user_id}",
        json={"answers": answers}
    )

    # Check attempt was created
    result = await clean_db_session.execute(
        select(QuizAttempt).where(
            QuizAttempt.user_id == user_id,
            QuizAttempt.quiz_id == quiz_id
        )
    )
    attempt = result.scalar_one_or_none()
    assert attempt is not None
    assert attempt.score == 100
    assert attempt.completed_at is not None


@pytest.mark.asyncio
async def test_get_quiz_by_chapter(
    client: AsyncClient,
    test_chapters: list,
    test_quizzes: list[Quiz]
):
    """Test getting quiz by chapter ID."""
    chapter_id = test_chapters[0].id
    quiz_id = test_quizzes[0].id

    response = await client.get(f"/api/v1/chapters/{chapter_id}/quiz")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(quiz_id)
    assert "questions" in data


@pytest.mark.asyncio
async def test_submit_quiz_invalid_user_id(client: AsyncClient, test_quizzes: list[Quiz]):
    """Test quiz submission with invalid user ID."""
    quiz_id = test_quizzes[0].id
    invalid_user_id = uuid.uuid4()

    response = await client.post(
        f"/api/v1/quizzes/{quiz_id}/submit?user_id={invalid_user_id}",
        json={"answers": {}}
    )

    # Should still process, just won't find user
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_submit_quiz_missing_answers(client: AsyncClient, test_quizzes: list[Quiz], test_users: dict):
    """Test quiz submission with missing answers field."""
    quiz_id = test_quizzes[0].id
    user_id = test_users["free"].id

    response = await client.post(
        f"/api/v1/quizzes/{quiz_id}/submit?user_id={user_id}",
        json={}  # Missing answers
    )

    assert response.status_code == 422  # Validation error
