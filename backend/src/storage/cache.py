"""
In-memory cache for frequently accessed content.
Zero-LLM compliance: Simple caching, no LLM services.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import time


class SimpleCache:
    """
    Simple in-memory cache with TTL (Time To Live) expiration.
    Thread-safe for basic usage.
    Implements LRU-style eviction when cache size limit is reached.
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
            max_size: Maximum number of items to store (default: 1000)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._access_times: Dict[str, datetime] = {}  # Track for LRU eviction

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
                # Update access time for LRU tracking
                self._access_times[key] = datetime.utcnow()
                return item["value"]
            else:
                # Expired, remove from cache
                del self._cache[key]
                self._access_times.pop(key, None)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with expiration.
        Evicts least recently used item if cache is at capacity.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (overrides default)
        """
        # Evict if cache is full and this is a new key
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_lru()

        ttl = ttl or self.default_ttl
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl)
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": now,
        }
        self._access_times[key] = now

    def _evict_lru(self) -> None:
        """Evict the least recently used item from cache."""
        if not self._access_times:
            return
        # Find the least recently accessed key
        lru_key = min(self._access_times, key=self._access_times.get)
        del self._cache[lru_key]
        del self._access_times[lru_key]

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
            self._access_times.pop(key, None)
            return True
        return False

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
        self._access_times.clear()

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
            self._access_times.pop(key, None)
        return len(expired_keys)

    def size(self) -> int:
        """Return number of cached items."""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
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
cache = SimpleCache(default_ttl=300, max_size=1000)  # 5 minutes default TTL, max 1000 items
