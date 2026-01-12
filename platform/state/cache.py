"""Caching utilities."""
import logging
import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching with TTL support."""
    
    def __init__(self, redis_client=None, default_ttl: int = 300):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.cache_prefix = "masterchief:cache"
    
    def _make_key(self, key: str) -> str:
        """Create cache key."""
        return f"{self.cache_prefix}:{key}"
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for caching."""
        return json.dumps(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize cached value."""
        return json.loads(value)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        if not self.redis:
            return None
        
        try:
            full_key = self._make_key(key)
            value = self.redis.get(full_key)
            if value:
                return self._deserialize(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL."""
        if not self.redis:
            return False
        
        try:
            full_key = self._make_key(key)
            serialized = self._serialize(value)
            ttl = ttl or self.default_ttl
            self.redis.setex(full_key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        if not self.redis:
            return False
        
        try:
            full_key = self._make_key(key)
            self.redis.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.redis:
            return 0
        
        try:
            full_pattern = self._make_key(pattern)
            keys = self.redis.keys(full_pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def cache_result(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """
        Decorator to cache function results.
        
        Args:
            ttl: Cache TTL in seconds
            key_func: Function to generate cache key from args
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    key_str = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                    cache_key = hashlib.md5(key_str.encode()).hexdigest()
                
                # Try to get from cache
                cached = await self.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
