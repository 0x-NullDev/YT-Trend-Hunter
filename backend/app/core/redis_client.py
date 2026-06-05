"""
YT Trend Hunter - Redis Client
Async Redis connection management for caching and pub/sub.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import orjson
from loguru import logger
from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings


class RedisClient:
    """
    Async Redis client wrapper with connection pooling.
    Provides caching, rate limiting, and pub/sub capabilities.
    """

    def __init__(self) -> None:
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None

    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        try:
            self._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=20,
            )
            self._client = Redis(connection_pool=self._pool)
            await self._client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed (caching disabled): {e}")
            self._client = None

    async def close(self) -> None:
        """Close Redis connection pool."""
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.aclose()
        logger.info("Redis connection closed")

    @property
    def is_connected(self) -> bool:
        """Check if Redis client is connected."""
        return self._client is not None

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Any]: Cached value or None
        """
        if not self._client:
            return None
        try:
            full_key = f"{settings.REDIS_CACHE_PREFIX}{key}"
            value = await self._client.get(full_key)
            if value:
                return orjson.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis get failed for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            bool: True if successful
        """
        if not self._client:
            return False
        try:
            full_key = f"{settings.REDIS_CACHE_PREFIX}{key}"
            serialized = orjson.dumps(value)
            await self._client.set(
                full_key,
                serialized,
                ex=ttl or settings.REDIS_CACHE_TTL,
            )
            return True
        except Exception as e:
            logger.warning(f"Redis set failed for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if deleted
        """
        if not self._client:
            return False
        try:
            full_key = f"{settings.REDIS_CACHE_PREFIX}{key}"
            await self._client.delete(full_key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete failed for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Key pattern (e.g., "trends:*")
            
        Returns:
            int: Number of deleted keys
        """
        if not self._client:
            return 0
        try:
            full_pattern = f"{settings.REDIS_CACHE_PREFIX}{pattern}"
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor, match=full_pattern, count=100
                )
                if keys:
                    await self._client.delete(*keys)
                    deleted += len(keys)
                if cursor == 0:
                    break
            return deleted
        except Exception as e:
            logger.warning(f"Redis delete_pattern failed: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if key exists
        """
        if not self._client:
            return False
        try:
            full_key = f"{settings.REDIS_CACHE_PREFIX}{key}"
            return await self._client.exists(full_key) > 0
        except Exception:
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter.
        
        Args:
            key: Counter key
            amount: Amount to increment
            
        Returns:
            Optional[int]: New value or None
        """
        if not self._client:
            return None
        try:
            full_key = f"{settings.REDIS_CACHE_PREFIX}{key}"
            return await self._client.incr(full_key, amount)
        except Exception as e:
            logger.warning(f"Redis increment failed: {e}")
            return None

    async def publish(self, channel: str, message: Any) -> None:
        """
        Publish a message to a channel.
        
        Args:
            channel: Channel name
            message: Message to publish
        """
        if not self._client:
            return
        try:
            await self._client.publish(channel, orjson.dumps(message))
        except Exception as e:
            logger.warning(f"Redis publish failed: {e}")

    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[int]: TTL in seconds or None
        """
        if not self._client:
            return None
        try:
            full_key = f"{settings.REDIS_CACHE_PREFIX}{key}"
            return await self._client.ttl(full_key)
        except Exception:
            return None


# Global Redis client instance
redis_client = RedisClient()
