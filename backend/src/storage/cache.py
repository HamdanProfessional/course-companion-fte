"""
In-memory cache for frequently accessed content.
Zero-LLM compliance: Simple caching, no LLM services.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import time


class SimpleCache:
    """
    Simple in-memory cache with TTL (Time To Live) expiration.
    Thread-safe for basic usage.
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key in self._cache:
            item = self._cache[key]
            if item["expires_at"] > datetime.utcnow():
                return item["value"]
            else:
                # Expired, remove from cache
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with expiration.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (overrides default)
        """
        ttl = ttl or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
        }

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove all expired items from cache.

        Returns:
            Number of items removed
        """
        now = datetime.utcnow()
        expired_keys = [
            key for key, item in self._cache.items()
            if item["expires_at"] < now
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def size(self) -> int:
        """Return number of cached items."""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        return {
            "size": len(self._cache),
            "default_ttl": self.default_ttl,
            "items": [
                {
                    "key": key,
                    "created_at": item["created_at"].isoformat(),
                    "expires_at": item["expires_at"].isoformat(),
                }
                for key, item in self._cache.items()
            ]
        }


# Global cache instance
cache = SimpleCache(default_ttl=300)  # 5 minutes default TTL
