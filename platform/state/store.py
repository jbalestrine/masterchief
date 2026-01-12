"""Redis-backed state store for centralized state management."""
import json
import logging
from typing import Any, Dict, Optional, List
from datetime import timedelta

logger = logging.getLogger(__name__)


class StateStore:
    """Redis-backed centralized state store."""
    
    def __init__(self, redis_client=None, key_prefix: str = "masterchief:state"):
        self.redis = redis_client
        self.key_prefix = key_prefix
    
    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.key_prefix}:{key}"
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the state store.
        
        Args:
            key: State key
            value: Value to store (will be JSON serialized)
            ttl: Time to live in seconds (optional)
        
        Returns:
            Success status
        """
        if not self.redis:
            logger.warning("Redis client not initialized")
            return False
        
        try:
            full_key = self._make_key(key)
            serialized = json.dumps(value)
            
            if ttl:
                self.redis.setex(full_key, ttl, serialized)
            else:
                self.redis.set(full_key, serialized)
            
            logger.debug(f"Set state: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to set state {key}: {e}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the state store.
        
        Args:
            key: State key
            default: Default value if key doesn't exist
        
        Returns:
            Stored value or default
        """
        if not self.redis:
            logger.warning("Redis client not initialized")
            return default
        
        try:
            full_key = self._make_key(key)
            value = self.redis.get(full_key)
            
            if value is None:
                return default
            
            return json.loads(value)
        except Exception as e:
            logger.error(f"Failed to get state {key}: {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """Delete a key from the state store."""
        if not self.redis:
            return False
        
        try:
            full_key = self._make_key(key)
            self.redis.delete(full_key)
            logger.debug(f"Deleted state: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete state {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        if not self.redis:
            return False
        
        try:
            full_key = self._make_key(key)
            return bool(self.redis.exists(full_key))
        except Exception as e:
            logger.error(f"Failed to check existence of {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Atomically increment a numeric value."""
        if not self.redis:
            return None
        
        try:
            full_key = self._make_key(key)
            return self.redis.incrby(full_key, amount)
        except Exception as e:
            logger.error(f"Failed to increment {key}: {e}")
            return None
    
    async def set_hash(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set multiple fields in a hash."""
        if not self.redis:
            return False
        
        try:
            full_key = self._make_key(key)
            serialized_mapping = {k: json.dumps(v) for k, v in mapping.items()}
            self.redis.hset(full_key, mapping=serialized_mapping)
            return True
        except Exception as e:
            logger.error(f"Failed to set hash {key}: {e}")
            return False
    
    async def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """Get all fields from a hash."""
        if not self.redis:
            return None
        
        try:
            full_key = self._make_key(key)
            result = self.redis.hgetall(full_key)
            return {k.decode(): json.loads(v) for k, v in result.items()}
        except Exception as e:
            logger.error(f"Failed to get hash {key}: {e}")
            return None
    
    async def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching a pattern."""
        if not self.redis:
            return []
        
        try:
            full_pattern = self._make_key(pattern)
            keys = self.redis.keys(full_pattern)
            # Remove prefix from returned keys
            prefix_len = len(self.key_prefix) + 1
            return [k.decode()[prefix_len:] for k in keys]
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []
    
    async def snapshot(self, keys: List[str]) -> Dict[str, Any]:
        """Create a snapshot of multiple keys."""
        snapshot = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                snapshot[key] = value
        return snapshot
    
    async def restore(self, snapshot: Dict[str, Any]):
        """Restore state from a snapshot."""
        for key, value in snapshot.items():
            await self.set(key, value)
        logger.info(f"Restored {len(snapshot)} keys from snapshot")


# Singleton instance
_state_store_instance: Optional[StateStore] = None


def get_state_store(redis_client=None) -> StateStore:
    """Get or create the global state store instance."""
    global _state_store_instance
    if _state_store_instance is None:
        _state_store_instance = StateStore(redis_client=redis_client)
    return _state_store_instance
