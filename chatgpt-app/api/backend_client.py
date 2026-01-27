"""
Backend API Client for Course Companion FTE ChatGPT App.
Zero-LLM compliance: Client makes HTTP requests to deterministic backend only.
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
from datetime import datetime


@dataclass
class BackendConfig:
    """Backend API configuration."""
    base_url: str
    default_user_id: str
    timeout: int = 30


class BackendClientError(Exception):
    """Base exception for backend client errors."""
    pass


class BackendConnectionError(BackendClientError):
    """Connection error to backend."""
    pass


class BackendAuthError(BackendClientError):
    """Authentication error (401)."""
    pass


class BackendAccessDeniedError(BackendClientError):
    """Access denied error (403)."""
    pass


class BackendNotFoundError(BackendClientError):
    """Resource not found error (404)."""
    pass


class BackendClient:
    """
    Async HTTP client for Course Companion FTE backend API.
    Zero-LLM: Makes HTTP requests to deterministic backend only.
    """

    def __init__(self, config: Optional[BackendConfig] = None):
        """
        Initialize backend client.

        Args:
            config: Backend configuration (defaults to environment variables)
        """
        if config is None:
            config = BackendConfig(
                base_url=os.getenv("BACKEND_URL", "http://localhost:8000"),
                default_user_id=os.getenv("DEFAULT_USER_ID", "00000000-0000-0000-0000-000000000000"),
            )

        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make HTTP request to backend.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., "/api/v1/chapters")
            params: Query parameters
            json: JSON request body

        Returns:
            Response data

        Raises:
            BackendConnectionError: Connection error
            BackendAuthError: 401 error
            BackendAccessDeniedError: 403 error
            BackendNotFoundError: 404 error
            BackendClientError: Other errors
        """
        session = await self._get_session()
        url = f"{self.base_url}{path}"

        try:
            async with session.request(method, url, params=params, json=json) as response:
                # Handle error responses
                if response.status == 401:
                    raise BackendAuthError("Authentication failed")
                elif response.status == 403:
                    data = await response.json() if response.content_length else {}
                    raise BackendAccessDeniedError(data.get("detail", "Access denied"))
                elif response.status == 404:
                    raise BackendNotFoundError("Resource not found")
                elif response.status >= 400:
                    data = await response.json() if response.content_length else {}
                    raise BackendClientError(data.get("detail", f"HTTP {response.status}"))

                # Return response data
                return await response.json()

        except aiohttp.ClientError as e:
            raise BackendConnectionError(f"Connection error: {str(e)}")

    # =========================================================================
    # Content APIs
    # =========================================================================

    async def list_chapters(self) -> List[Dict[str, Any]]:
        """List all chapters."""
        return await self._request("GET", "/api/v1/chapters")

    async def get_chapter(self, chapter_id: str) -> Dict[str, Any]:
        """Get chapter content by ID."""
        return await self._request("GET", f"/api/v1/chapters/{chapter_id}")

    async def get_next_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """Get next chapter in sequence."""
        try:
            return await self._request("GET", f"/api/v1/chapters/{chapter_id}/next")
        except BackendNotFoundError:
            return None

    async def get_previous_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """Get previous chapter in sequence."""
        try:
            return await self._request("GET", f"/api/v1/chapters/{chapter_id}/previous")
        except BackendNotFoundError:
            return None

    async def search_content(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search course content."""
        params = {"q": query, "limit": limit}
        return await self._request("GET", "/api/v1/search", params=params)

    # =========================================================================
    # Quiz APIs
    # =========================================================================

    async def list_quizzes(self) -> List[Dict[str, Any]]:
        """List all quizzes."""
        return await self._request("GET", "/api/v1/quizzes")

    async def get_quiz(self, quiz_id: str) -> Dict[str, Any]:
        """Get quiz with questions."""
        return await self._request("GET", f"/api/v1/quizzes/{quiz_id}")

    async def submit_quiz(
        self,
        quiz_id: str,
        user_id: str,
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Submit quiz answers for grading.
        Zero-LLM: Grading happens in backend using rule-based answer keys.

        Args:
            quiz_id: Quiz ID
            user_id: User ID
            answers: Map of question_id to selected answer

        Returns:
            Quiz results with score and feedback
        """
        return await self._request(
            "POST",
            f"/api/v1/quizzes/{quiz_id}/submit",
            json={"answers": answers}
        )

    async def get_quiz_results(self, quiz_id: str, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get quiz attempt history."""
        params = {"user_id": user_id, "limit": limit}
        return await self._request("GET", f"/api/v1/quizzes/{quiz_id}/results", params=params)

    # =========================================================================
    # Progress APIs
    # =========================================================================

    async def get_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user progress."""
        return await self._request("GET", f"/api/v1/progress/{user_id}")

    async def update_progress(self, user_id: str, chapter_id: str) -> Dict[str, Any]:
        """Mark chapter as complete and update progress."""
        return await self._request(
            "PUT",
            f"/api/v1/progress/{user_id}",
            json={"chapter_id": chapter_id}
        )

    async def get_streak(self, user_id: str) -> Dict[str, Any]:
        """Get user streak information."""
        return await self._request("GET", f"/api/v1/streaks/{user_id}")

    async def record_checkin(self, user_id: str) -> Dict[str, Any]:
        """Record daily activity checkin."""
        return await self._request("POST", f"/api/v1/streaks/{user_id}/checkin")

    # =========================================================================
    # Access Control APIs
    # =========================================================================

    async def check_access(self, user_id: str, resource: str) -> Dict[str, Any]:
        """
        Check if user has access to resource.
        Zero-LLM: Deterministic rule-based access control.

        Args:
            user_id: User ID
            resource: Resource identifier (e.g., "chapter-4")

        Returns:
            Access check result
        """
        return await self._request(
            "POST",
            "/api/v1/access/check",
            json={"user_id": user_id, "resource": resource}
        )

    async def get_user_tier(self, user_id: str) -> Dict[str, Any]:
        """Get user subscription tier."""
        return await self._request("GET", f"/api/v1/user/{user_id}/tier")

    async def upgrade_tier(self, user_id: str, new_tier: str) -> Dict[str, Any]:
        """Upgrade user to new subscription tier."""
        return await self._request(
            "POST",
            "/api/v1/access/upgrade",
            json={"user_id": user_id, "new_tier": new_tier}
        )


# ============================================================================
# Global client instance
# ============================================================================

_global_client: Optional[BackendClient] = None


def get_backend_client() -> BackendClient:
    """Get global backend client instance."""
    global _global_client
    if _global_client is None:
        _global_client = BackendClient()
    return _global_client


async def close_backend_client():
    """Close global backend client."""
    global _global_client
    if _global_client:
        await _global_client.close()
        _global_client = None
