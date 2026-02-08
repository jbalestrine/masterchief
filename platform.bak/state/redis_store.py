"""Redis state store implementation (OPTIONAL)."""
import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RedisStateStore:
    """
    Redis state store (OPTIONAL).
    
    This implementation uses Redis for state storage and is suitable for
    production deployments that need to scale horizontally.
    """
    
    def __init__(self, redis_url: str = None):
        """
        Initialize Redis state store.
        
        Args:
            redis_url: Redis connection URL (default: redis://localhost:6379/0)
        """
        try:
            import redis
        except ImportError:
            raise ImportError(
                "Redis package is required for RedisStateStore. "
                "Install it with: pip install redis"
            )
        
        if redis_url is None:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
        self.redis_url = redis_url
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        logger.info(f"Initialized Redis state store: {redis_url}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value or None if not found or expired
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        Set a value with optional TTL.
        
        Args:
            key: The key to set
            value: The value to store (must be JSON-serializable)
            ttl: Optional time to live in seconds
        """
        try:
            value_json = json.dumps(value)
            if ttl:
                self.redis_client.setex(key, ttl, value_json)
            else:
                self.redis_client.set(key, value_json)
            logger.debug(f"Set key: {key} (ttl={ttl})")
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            raise
    
    def delete(self, key: str):
        """
        Delete a key.
        
        Args:
            key: The key to delete
        """
        try:
            self.redis_client.delete(key)
            logger.debug(f"Deleted key: {key}")
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists
        """
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking key {key}: {e}")
            return False
    
    def keys(self, pattern: str = "*") -> list:
        """
        Get all keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user:*", "*:config")
            
        Returns:
            List of matching keys
        """
        try:
            return [k.decode() if isinstance(k, bytes) else k 
                    for k in self.redis_client.keys(pattern)]
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []
    
    def clear(self):
        """Clear all keys (use with caution in production)."""
        try:
            self.redis_client.flushdb()
            logger.info("Cleared all state")
        except Exception as e:
            logger.error(f"Error clearing state: {e}")
    
    def size(self) -> int:
        """Get the number of keys in the store."""
        try:
            return self.redis_client.dbsize()
        except Exception as e:
            logger.error(f"Error getting size: {e}")
            return 0
