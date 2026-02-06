"""
Authentication flow integration tests.
Tests user registration, login, token validation, and access control.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import User, Progress, Streak


@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient):
    """Test successful user registration."""
    new_user = {
        "email": "newuser@example.com",
        "password": "SecurePass123",
    }

    response = await client.post("/api/v1/auth/register", json=new_user)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == new_user["email"]
    assert data["user"]["tier"] == "FREE"


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(client: AsyncClient, test_users):
    """Test registration with duplicate email returns error."""
    duplicate_user = {
        "email": "demo@example.com",  # Already exists
        "password": "AnotherPass123",
    }

    response = await client.post("/api/v1/auth/register", json=duplicate_user)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient):
    """Test successful login with valid credentials."""
    credentials = {
        "email": "demo@example.com",
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/login", json=credentials)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == credentials["email"]


@pytest.mark.asyncio
async def test_user_login_invalid_password(client: AsyncClient):
    """Test login with invalid password returns 401."""
    invalid_credentials = {
        "email": "demo@example.com",
        "password": "wrongpassword",
    }

    response = await client.post("/api/v1/auth/login", json=invalid_credentials)

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_user_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user returns 401."""
    credentials = {
        "email": "nonexistent@example.com",
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/login", json=credentials)

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers_free: dict):
    """Test getting current authenticated user."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers_free)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "demo@example.com"
    assert data["tier"] == "FREE"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test getting current user without auth token returns 401."""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token returns 401."""
    invalid_headers = {"Authorization": "Bearer invalid_token"}

    response = await client.get("/api/v1/auth/me", headers=invalid_headers)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_new_user_has_progress_and_streak(
    client: AsyncClient,
    clean_db_session: AsyncSession
):
    """Test that new user registration creates progress and streak records."""
    new_user = {
        "email": "progresscheck@example.com",
        "password": "SecurePass123",
    }

    await client.post("/api/v1/auth/register", json=new_user)

    # Check that progress was created
    result = await clean_db_session.execute(
        select(User).where(User.email == "progresscheck@example.com")
    )
    user = result.scalar_one()

    progress_result = await clean_db_session.execute(
        select(Progress).where(Progress.user_id == user.id)
    )
    progress = progress_result.scalar_one_or_none()
    assert progress is not None
    assert progress.completed_chapters == []

    streak_result = await clean_db_session.execute(
        select(Streak).where(Streak.user_id == user.id)
    )
    streak = streak_result.scalar_one_or_none()
    assert streak is not None
    assert streak.current_streak == 0
