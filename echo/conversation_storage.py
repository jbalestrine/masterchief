"""
Persistent Conversation Storage for Echo Starlite
Stores and retrieves conversations using SQLite for persistent memory.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import threading


class ConversationStorage:
    """
    SQLite-backed persistent storage for Echo's conversations.
    Thread-safe for use in IRC bot and other concurrent contexts.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize conversation storage.
        
        Args:
            db_path: Path to SQLite database file. 
                     Defaults to data/echo_conversations.db
        """
        if db_path is None:
            # Create data directory in the project root
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "echo_conversations.db")
        
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema if it doesn't exist."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user TEXT NOT NULL,
                    message TEXT NOT NULL,
                    echo_response TEXT,
                    context_tags TEXT,
                    emotional_tone TEXT DEFAULT 'neutral',
                    channel TEXT
                )
            """)
            
            # Create index for efficient queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON conversations(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user 
                ON conversations(user)
            """)
            
            conn.commit()
            conn.close()
    
    def store_message(
        self,
        user: str,
        message: str,
        echo_response: str = None,
        context_tags: List[str] = None,
        emotional_tone: str = "neutral",
        channel: str = None
    ) -> int:
        """
        Store a conversation message.
        
        Args:
            user: Username or identifier
            message: User's message
            echo_response: Echo's response (optional)
            context_tags: List of context tags for categorization
            emotional_tone: Emotional quality (positive, neutral, negative)
            channel: IRC channel or conversation context
            
        Returns:
            ID of the stored message
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now(timezone.utc).isoformat()
            context_json = json.dumps(context_tags) if context_tags else None
            
            cursor.execute("""
                INSERT INTO conversations 
                (timestamp, user, message, echo_response, context_tags, 
                 emotional_tone, channel)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, user, message, echo_response, context_json, 
                  emotional_tone, channel))
            
            message_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return message_id
    
    def update_echo_response(self, message_id: int, echo_response: str):
        """
        Update Echo's response for a stored message.
        
        Args:
            message_id: ID of the message to update
            echo_response: Echo's response text
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE conversations 
                SET echo_response = ?
                WHERE id = ?
            """, (echo_response, message_id))
            
            conn.commit()
            conn.close()
    
    def get_conversation_history(
        self,
        user: str = None,
        limit: int = 50,
        channel: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            user: Filter by specific user (optional)
            limit: Maximum number of messages to return
            channel: Filter by channel (optional)
            
        Returns:
            List of conversation messages, most recent first
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM conversations WHERE 1=1"
            params = []
            
            if user:
                query += " AND user = ?"
                params.append(user)
            
            if channel:
                query += " AND channel = ?"
                params.append(channel)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            messages = []
            for row in rows:
                msg = dict(row)
                if msg['context_tags']:
                    msg['context_tags'] = json.loads(msg['context_tags'])
                messages.append(msg)
            
            conn.close()
            return messages
    
    def search_conversations(
        self,
        query: str,
        user: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search conversations by text content.
        
        Args:
            query: Search query string
            user: Filter by specific user (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching conversation messages
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_query = """
                SELECT * FROM conversations 
                WHERE (message LIKE ? OR echo_response LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%"]
            
            if user:
                search_query += " AND user = ?"
                params.append(user)
            
            search_query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(search_query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            messages = []
            for row in rows:
                msg = dict(row)
                if msg['context_tags']:
                    msg['context_tags'] = json.loads(msg['context_tags'])
                messages.append(msg)
            
            conn.close()
            return messages
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get conversation statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total messages
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total = cursor.fetchone()[0]
            
            # Unique users
            cursor.execute("SELECT COUNT(DISTINCT user) FROM conversations")
            unique_users = cursor.fetchone()[0]
            
            # Messages by emotional tone
            cursor.execute("""
                SELECT emotional_tone, COUNT(*) as count 
                FROM conversations 
                GROUP BY emotional_tone
            """)
            tone_counts = dict(cursor.fetchall())
            
            # Most active user
            cursor.execute("""
                SELECT user, COUNT(*) as count 
                FROM conversations 
                GROUP BY user 
                ORDER BY count DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            most_active_user = result[0] if result else None
            
            conn.close()
            
            return {
                'total_messages': total,
                'unique_users': unique_users,
                'emotional_tone_distribution': tone_counts,
                'most_active_user': most_active_user
            }
    
    def get_recent_context(
        self,
        user: str,
        minutes: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent conversation context for a user.
        
        Args:
            user: Username to get context for
            minutes: How many minutes back to look
            limit: Maximum number of messages
            
        Returns:
            List of recent messages with context
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Calculate timestamp threshold
            from datetime import timedelta
            threshold = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()
            
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE user = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user, threshold, limit))
            
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            messages = []
            for row in rows:
                msg = dict(row)
                if msg['context_tags']:
                    msg['context_tags'] = json.loads(msg['context_tags'])
                messages.append(msg)
            
            conn.close()
            return messages
    
    def clear_old_conversations(self, days: int = 90):
        """
        Clear conversations older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of messages deleted
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            from datetime import timedelta
            threshold = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                DELETE FROM conversations 
                WHERE timestamp < ?
            """, (threshold,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted


# Singleton instance for easy access
_storage_instance = None


def get_storage(db_path: str = None) -> ConversationStorage:
    """
    Get singleton conversation storage instance.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        ConversationStorage instance
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ConversationStorage(db_path)
    return _storage_instance
