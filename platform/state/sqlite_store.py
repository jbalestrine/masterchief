"""SQLite-backed state store implementation."""
import json
import logging
import sqlite3
import time
import fnmatch
from pathlib import Path
from typing import Any, Optional
import threading

logger = logging.getLogger(__name__)


class SQLiteStateStore:
    """
    SQLite-backed state store (DEFAULT for persistence).
    
    This implementation stores state in a SQLite database file,
    providing persistence across application restarts without
    requiring an external database server.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize SQLite state store.
        
        Args:
            db_path: Path to SQLite database file (default: data/state.db)
        """
        if db_path is None:
            import os
            db_path = os.environ.get('STATE_DB_PATH', 'data/state.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()
        logger.info(f"Initialized SQLite state store: {self.db_path}")
    
    def _init_db(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL,
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON state(expires_at)
            """)
            conn.commit()
    
    def _get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=10.0
        )
    
    def _cleanup_expired(self, conn):
        """Remove expired entries."""
        current_time = time.time()
        conn.execute("""
            DELETE FROM state 
            WHERE expires_at IS NOT NULL 
            AND expires_at < ?
        """, (current_time,))
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value or None if not found or expired
        """
        with self._lock:
            with self._get_connection() as conn:
                # Clean up expired entries
                self._cleanup_expired(conn)
                conn.commit()
                
                # Get value
                row = conn.execute("""
                    SELECT value FROM state 
                    WHERE key = ? 
                    AND (expires_at IS NULL OR expires_at > ?)
                """, (key, time.time())).fetchone()
                
                if row:
                    try:
                        return json.loads(row[0])
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode value for key: {key}")
                        return None
                return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        Set a value with optional TTL.
        
        Args:
            key: The key to set
            value: The value to store (must be JSON-serializable)
            ttl: Optional time to live in seconds
        """
        with self._lock:
            expires_at = time.time() + ttl if ttl else None
            
            try:
                value_json = json.dumps(value)
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to serialize value for key {key}: {e}")
                raise
            
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO state (key, value, expires_at, updated_at)
                    VALUES (?, ?, ?, strftime('%s', 'now'))
                """, (key, value_json, expires_at))
                conn.commit()
                logger.debug(f"Set key: {key} (ttl={ttl})")
    
    def delete(self, key: str):
        """
        Delete a key.
        
        Args:
            key: The key to delete
        """
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM state WHERE key = ?", (key,))
                conn.commit()
                logger.debug(f"Deleted key: {key}")
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists and is not expired
        """
        with self._lock:
            with self._get_connection() as conn:
                row = conn.execute("""
                    SELECT 1 FROM state 
                    WHERE key = ? 
                    AND (expires_at IS NULL OR expires_at > ?)
                """, (key, time.time())).fetchone()
                return row is not None
    
    def keys(self, pattern: str = "*") -> list:
        """
        Get all keys matching pattern.
        
        Args:
            pattern: Glob-style pattern (e.g., "user:*", "*:config")
            
        Returns:
            List of matching keys
        """
        with self._lock:
            with self._get_connection() as conn:
                # Clean up expired entries
                self._cleanup_expired(conn)
                conn.commit()
                
                # Get all non-expired keys
                rows = conn.execute("""
                    SELECT key FROM state 
                    WHERE expires_at IS NULL OR expires_at > ?
                """, (time.time(),)).fetchall()
                
                all_keys = [row[0] for row in rows]
                
                # Filter by pattern
                if pattern == "*":
                    return all_keys
                return [k for k in all_keys if fnmatch.fnmatch(k, pattern)]
    
    def clear(self):
        """Clear all keys."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM state")
                conn.commit()
                logger.info("Cleared all state")
    
    def size(self) -> int:
        """Get the number of non-expired keys in the store."""
        with self._lock:
            with self._get_connection() as conn:
                self._cleanup_expired(conn)
                conn.commit()
                
                row = conn.execute("""
                    SELECT COUNT(*) FROM state 
                    WHERE expires_at IS NULL OR expires_at > ?
                """, (time.time(),)).fetchone()
                return row[0] if row else 0
