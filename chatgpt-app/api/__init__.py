"""
Course Companion FTE - API Modules
Contains backend API client functionality.
"""

from backend_client import (
    BackendClient,
    BackendConfig,
    BackendClientError,
    BackendConnectionError,
    BackendAuthError,
    BackendAccessDeniedError,
    BackendNotFoundError,
    get_backend_client,
    close_backend_client,
)

__all__ = [
    "BackendClient",
    "BackendConfig",
    "BackendClientError",
    "BackendConnectionError",
    "BackendAuthError",
    "BackendAccessDeniedError",
    "BackendNotFoundError",
    "get_backend_client",
    "close_backend_client",
]
