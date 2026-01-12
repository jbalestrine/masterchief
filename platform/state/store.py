"""Abstract state store interface and factory."""
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class StateStore:
    """Abstract state store interface."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set a value with optional TTL (time to live) in seconds."""
        raise NotImplementedError
    
    def delete(self, key: str):
        """Delete a key."""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        raise NotImplementedError
    
    def keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern."""
        raise NotImplementedError
    
    def clear(self):
        """Clear all keys."""
        raise NotImplementedError


def create_state_store(backend: str = None, **kwargs) -> StateStore:
    """
    Create a state store with the specified backend.
    
    Args:
        backend: Backend type ('memory', 'sqlite', or 'redis').
                 If None, uses STATE_STORE_BACKEND env var or defaults to 'sqlite'.
        **kwargs: Additional backend-specific arguments
    
    Returns:
        StateStore instance
    """
    if backend is None:
        backend = os.environ.get('STATE_STORE_BACKEND', 'sqlite')
    
    backend = backend.lower()
    
    if backend == 'redis':
        try:
            from .redis_store import RedisStateStore
            logger.info("Using Redis state store backend")
            return RedisStateStore(**kwargs)
        except ImportError:
            logger.warning("Redis not available, falling back to SQLite state store")
            backend = 'sqlite'
    
    if backend == 'sqlite':
        from .sqlite_store import SQLiteStateStore
        logger.info("Using SQLite state store backend")
        return SQLiteStateStore(**kwargs)
    
    if backend == 'memory':
        from .memory_store import MemoryStateStore
        logger.info("Using in-memory state store backend")
        return MemoryStateStore(**kwargs)
    
    raise ValueError(f"Unknown state store backend: {backend}")
