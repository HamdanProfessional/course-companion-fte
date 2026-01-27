"""
Basic API endpoint tests.
Verify that the API routes work correctly.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.core.database import async_session_maker


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "architecture" in data
        assert data["architecture"] == "Backend serves content verbatim, all AI intelligence in ChatGPT"


@pytest.mark.asyncio
async def test_list_chapters():
    """Test list chapters endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/chapters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_endpoint():
    """Test search endpoint with query."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/search?q=AI")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_search_missing_query():
    """Test search endpoint without query returns 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/search")
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_quizzes():
    """Test list quizzes endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_access_check():
    """Test access check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/access/check",
            json={
                "user_id": "00000000-0000-0000-0000-000000000000",
                "resource": "chapter-1"
            }
        )
        # Will return 200 even if user doesn't exist (access denied response)
        assert response.status_code == 200
        data = response.json()
        assert "access_granted" in data
        assert "tier" in data
