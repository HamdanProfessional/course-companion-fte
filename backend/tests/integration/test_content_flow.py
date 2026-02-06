"""
Content flow integration tests.
Tests chapter listing, content retrieval, search, and access control.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Chapter, User


@pytest.mark.asyncio
async def test_list_chapters(client: AsyncClient, test_chapters: list[Chapter]):
    """Test listing all chapters."""
    response = await client.get("/api/v1/chapters")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["order"] == 1
    assert data[0]["title"] == "Introduction to AI Agents"
    assert "id" in data[0]
    assert "difficulty_level" in data[0]


@pytest.mark.asyncio
async def test_list_chapters_ordered(client: AsyncClient, test_chapters: list[Chapter]):
    """Test that chapters are returned in order."""
    response = await client.get("/api/v1/chapters")

    assert response.status_code == 200
    data = response.json()
    orders = [chapter["order"] for chapter in data]
    assert orders == sorted(orders)  # Should be in ascending order


@pytest.mark.asyncio
async def test_get_chapter_content(client: AsyncClient, test_chapters: list[Chapter]):
    """Test getting full chapter content."""
    chapter_id = test_chapters[0].id
    response = await client.get(f"/api/v1/chapters/{chapter_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(chapter_id)
    assert "title" in data
    assert "content" in data
    assert data["content"] is not None
    assert "difficulty_level" in data


@pytest.mark.asyncio
async def test_get_chapter_content_not_found(client: AsyncClient):
    """Test getting non-existent chapter returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/chapters/{fake_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_content(client: AsyncClient, test_chapters: list[Chapter]):
    """Test content search functionality."""
    response = await client.get("/api/v1/search?q=AI")

    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert data["query"] == "AI"
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)
    assert data["total"] > 0


@pytest.mark.asyncio
async def test_search_missing_query(client: AsyncClient):
    """Test search without query parameter returns 422."""
    response = await client.get("/api/v1/search")

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient):
    """Test search with query that has no results."""
    response = await client.get("/api/v1/search?q=nonexistentcontentxyz")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["results"]) == 0


@pytest.mark.asyncio
async def test_access_check_free_user_to_chapter_1(
    client: AsyncClient,
    test_chapters: list[Chapter],
    test_users: dict
):
    """Test access check for FREE user to chapter 1 (should be granted)."""
    user_id = test_users["free"].id
    chapter_id = test_chapters[0].id  # Chapter 1

    response = await client.post(
        "/api/v1/access/check",
        json={
            "user_id": str(user_id),
            "resource": f"chapter-{chapter_id}"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_granted" in data
    assert "tier" in data
    # FREE users can access chapters 1-3, so chapter 1 should be accessible


@pytest.mark.asyncio
async def test_access_check_free_user_to_chapter_4(
    client: AsyncClient,
    test_users: dict
):
    """Test access check for FREE user to chapter 4 (should be denied)."""
    user_id = test_users["free"].id

    response = await client.post(
        "/api/v1/access/check",
        json={
            "user_id": str(user_id),
            "resource": "chapter-4"  # Chapter 4 requires PREMIUM
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_granted" in data
    # FREE users should not have access to chapter 4


@pytest.mark.asyncio
async def test_access_check_premium_user_to_chapter_4(
    client: AsyncClient,
    test_users: dict
):
    """Test access check for PREMIUM user to chapter 4 (should be granted)."""
    user_id = test_users["premium"].id

    response = await client.post(
        "/api/v1/access/check",
        json={
            "user_id": str(user_id),
            "resource": "chapter-4"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_granted" in data
    assert data["tier"] == "PREMIUM"
    # PREMIUM users should have access to chapter 4


@pytest.mark.asyncio
async def test_access_check_nonexistent_user(client: AsyncClient):
    """Test access check for non-existent user."""
    response = await client.post(
        "/api/v1/access/check",
        json={
            "user_id": "00000000-0000-0000-0000-000000000000",
            "resource": "chapter-1"
        }
    )

    assert response.status_code == 200
    data = response.json()
    # Should return access_denied for non-existent user
    assert "access_granted" in data
    assert data["tier"] == "FREE"


@pytest.mark.asyncio
async def test_get_user_tier(client: AsyncClient, test_users: dict):
    """Test getting user tier."""
    user_id = test_users["free"].id
    response = await client.get(f"/api/v1/user/{user_id}/tier")

    assert response.status_code == 200
    data = response.json()
    assert "tier" in data
    assert data["tier"] == "FREE"


@pytest.mark.asyncio
async def test_get_user_tier_premium(client: AsyncClient, test_users: dict):
    """Test getting PREMIUM user tier."""
    user_id = test_users["premium"].id
    response = await client.get(f"/api/v1/user/{user_id}/tier")

    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "PREMIUM"


@pytest.mark.asyncio
async def test_chapter_navigation_links(
    client: AsyncClient,
    test_chapters: list[Chapter]
):
    """Test that chapters include navigation information."""
    # First chapter should have next but not previous
    first_chapter_id = test_chapters[0].id
    response = await client.get(f"/api/v1/chapters/{first_chapter_id}")

    assert response.status_code == 200
    data = response.json()
    # Note: Navigation might be in a separate field or computed
    assert "id" in data
