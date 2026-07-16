import time
from typing import Dict, Optional, Set
import redis
from app.core.config import settings
from app.core.logging import logger


class RedisService:
    """
    Service for token revocation, blocklist management, and API rate limiting.
    Includes in-memory fallback for environments without an active Redis instance.
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._fallback_store: Dict[str, str] = {}
        self._fallback_blocklist: Set[str] = set()
        self._fallback_rate_limits: Dict[str, list] = {}

        try:
            self._redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            # Test connection immediately
            self._redis.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(
                f"Redis server is offline or unreachable: {str(e)}. "
                "Falling back to thread-safe in-memory caching and rate limiting."
            )
            self._redis = None

    def is_token_blocked(self, jti: str) -> bool:
        """
        Checks if a JWT ID (jti) exists in the blocklist (meaning it has been revoked).
        """
        if self._redis:
            try:
                return self._redis.exists(f"blocked_token:{jti}") > 0
            except Exception as e:
                logger.error(f"Redis operation failed: {str(e)}")
        
        # Fallback to local memory list
        return jti in self._fallback_blocklist

    def block_token(self, jti: str, expire_seconds: int) -> None:
        """
        Blocks a JWT ID (jti) until it expires.
        """
        if self._redis:
            try:
                self._redis.setex(f"blocked_token:{jti}", expire_seconds, "1")
                return
            except Exception as e:
                logger.error(f"Redis operation failed: {str(e)}")

        # Fallback to local memory list
        self._fallback_blocklist.add(jti)

    def check_rate_limit(self, key: str, limit: int, period_seconds: int) -> bool:
        """
        Performs rate-limiting check using a sliding window algorithm.
        Returns:
            True if request is allowed, False if limit exceeded.
        """
        now = time.time()
        
        if self._redis:
            try:
                pipeline = self._redis.pipeline()
                redis_key = f"rate_limit:{key}"
                
                # Clear elements older than window period
                pipeline.zremrangebyscore(redis_key, 0, now - period_seconds)
                # Add current request timestamp
                pipeline.zadd(redis_key, {str(now): now})
                # Count current requests in window
                pipeline.zcard(redis_key)
                # Set key TTL to match period
                pipeline.expire(redis_key, period_seconds)
                
                _, _, count, _ = pipeline.execute()
                
                return count <= limit
            except Exception as e:
                logger.error(f"Redis rate limiting failed: {str(e)}")

        # Fallback to in-memory sliding window
        window_start = now - period_seconds
        if key not in self._fallback_rate_limits:
            self._fallback_rate_limits[key] = []
        
        # Filter older timestamps
        self._fallback_rate_limits[key] = [t for t in self._fallback_rate_limits[key] if t > window_start]
        # Append current call
        self._fallback_rate_limits[key].append(now)
        
        return len(self._fallback_rate_limits[key]) <= limit


# Global single instance initialized on start
redis_service = RedisService()
