"""In-memory state store implementation."""
import logging
import threading
import time
from typing import Any, Dict, Optional
import fnmatch

logger = logging.getLogger(__name__)


class MemoryStateStore:
    """
    In-memory state store (DEFAULT for development).
    
    This implementation stores state in memory and is suitable for
    development and testing. Data is lost when the application restarts.
    """
    
    def __init__(self):
        self._store: Dict[str, tuple] = {}  # key -> (value, expires_at)
        self._lock = threading.RLock()
        logger.info("Initialized in-memory state store")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value or None if not found or expired
        """
        with self._lock:
            if key not in self._store:
                return None
            
            value, expires_at = self._store[key]
            
            # Check if expired
            if expires_at and time.time() > expires_at:
                del self._store[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        Set a value with optional TTL.
        
        Args:
            key: The key to set
            value: The value to store
            ttl: Optional time to live in seconds
        """
        with self._lock:
            expires_at = time.time() + ttl if ttl else None
            self._store[key] = (value, expires_at)
            logger.debug(f"Set key: {key} (ttl={ttl})")
    
    def delete(self, key: str):
        """
        Delete a key.
        
        Args:
            key: The key to delete
        """
        with self._lock:
            if key in self._store:
                del self._store[key]
                logger.debug(f"Deleted key: {key}")
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists and is not expired
        """
        return self.get(key) is not None
    
    def keys(self, pattern: str = "*") -> list:
        """
        Get all keys matching pattern.
        
        Args:
            pattern: Glob-style pattern (e.g., "user:*", "*:config")
            
        Returns:
            List of matching keys
        """
        with self._lock:
            # Clean up expired keys first
            current_time = time.time()
            expired_keys = [
                k for k, (_, expires_at) in self._store.items()
                if expires_at and current_time > expires_at
            ]
            for k in expired_keys:
                del self._store[k]
            
            # Return keys matching pattern
            all_keys = list(self._store.keys())
            if pattern == "*":
                return all_keys
            return [k for k in all_keys if fnmatch.fnmatch(k, pattern)]
    
    def clear(self):
        """Clear all keys."""
        with self._lock:
            self._store.clear()
            logger.info("Cleared all state")
    
    def size(self) -> int:
        """Get the number of keys in the store."""
        with self._lock:
            return len(self._store)
