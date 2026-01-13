"""
Unit tests for Echo's conversation storage system.
"""

import unittest
import tempfile
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path to import conversation_storage directly
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
echo_dir = project_root / "echo"
sys.path.insert(0, str(project_root))

# Import directly without going through __init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "conversation_storage", 
    echo_dir / "conversation_storage.py"
)
conversation_storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conversation_storage)

ConversationStorage = conversation_storage.ConversationStorage
get_storage = conversation_storage.get_storage


class TestConversationStorage(unittest.TestCase):
    """Test cases for ConversationStorage."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.storage = ConversationStorage(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_initialization(self):
        """Test that storage initializes correctly."""
        self.assertIsNotNone(self.storage)
        self.assertEqual(self.storage.db_path, self.temp_db.name)
        
        # Verify database and tables were created
        self.assertTrue(os.path.exists(self.temp_db.name))
    
    def test_store_message(self):
        """Test storing a message."""
        message_id = self.storage.store_message(
            user="testuser",
            message="Hello Echo!",
            echo_response="Hello! How can I help?",
            context_tags=["greeting"],
            emotional_tone="positive"
        )
        
        self.assertIsNotNone(message_id)
        self.assertIsInstance(message_id, int)
        self.assertGreater(message_id, 0)
    
    def test_store_message_minimal(self):
        """Test storing a message with minimal parameters."""
        message_id = self.storage.store_message(
            user="testuser",
            message="Test message"
        )
        
        self.assertIsNotNone(message_id)
    
    def test_update_echo_response(self):
        """Test updating Echo's response."""
        # Store initial message
        message_id = self.storage.store_message(
            user="testuser",
            message="What's the weather?"
        )
        
        # Update with Echo's response
        self.storage.update_echo_response(
            message_id,
            "It's sunny today! ☀️"
        )
        
        # Verify update
        history = self.storage.get_conversation_history(user="testuser", limit=1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['echo_response'], "It's sunny today! ☀️")
    
    def test_get_conversation_history(self):
        """Test retrieving conversation history."""
        # Store multiple messages
        self.storage.store_message("user1", "Message 1", "Response 1")
        self.storage.store_message("user1", "Message 2", "Response 2")
        self.storage.store_message("user2", "Message 3", "Response 3")
        
        # Get history for user1
        history = self.storage.get_conversation_history(user="user1")
        self.assertEqual(len(history), 2)
        
        # Verify messages are in reverse chronological order (most recent first)
        self.assertEqual(history[0]['message'], "Message 2")
        self.assertEqual(history[1]['message'], "Message 1")
    
    def test_get_conversation_history_with_limit(self):
        """Test conversation history with limit."""
        # Store multiple messages
        for i in range(10):
            self.storage.store_message("testuser", f"Message {i}")
        
        # Get limited history
        history = self.storage.get_conversation_history(user="testuser", limit=5)
        self.assertEqual(len(history), 5)
        
        # Most recent should be Message 9
        self.assertEqual(history[0]['message'], "Message 9")
    
    def test_get_conversation_history_by_channel(self):
        """Test filtering conversation history by channel."""
        # Store messages in different channels
        self.storage.store_message("user1", "Channel1 msg", channel="#channel1")
        self.storage.store_message("user1", "Channel2 msg", channel="#channel2")
        
        # Get history for specific channel
        history = self.storage.get_conversation_history(channel="#channel1")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['message'], "Channel1 msg")
    
    def test_search_conversations(self):
        """Test searching conversations."""
        # Store messages with searchable content
        self.storage.store_message("user1", "How do I deploy?", "Use kubectl apply")
        self.storage.store_message("user1", "What about Docker?", "Docker is containerization")
        self.storage.store_message("user1", "Tell me about Python", "Python is great")
        
        # Search for "deploy"
        results = self.storage.search_conversations("deploy")
        self.assertEqual(len(results), 1)
        self.assertIn("deploy", results[0]['message'].lower())
        
        # Search for "docker"
        results = self.storage.search_conversations("Docker")
        self.assertEqual(len(results), 1)
        self.assertIn("docker", results[0]['message'].lower())
    
    def test_search_conversations_in_response(self):
        """Test searching in Echo's responses."""
        self.storage.store_message("user1", "Question?", "The answer contains kubectl")
        
        results = self.storage.search_conversations("kubectl")
        self.assertEqual(len(results), 1)
        self.assertIn("kubectl", results[0]['echo_response'])
    
    def test_search_conversations_with_user_filter(self):
        """Test searching with user filter."""
        self.storage.store_message("user1", "Docker question", "Docker answer")
        self.storage.store_message("user2", "Docker question", "Docker answer")
        
        # Search only for user1
        results = self.storage.search_conversations("Docker", user="user1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['user'], "user1")
    
    def test_get_statistics(self):
        """Test getting conversation statistics."""
        # Store test data
        self.storage.store_message("user1", "Msg1", emotional_tone="positive")
        self.storage.store_message("user1", "Msg2", emotional_tone="positive")
        self.storage.store_message("user2", "Msg3", emotional_tone="neutral")
        self.storage.store_message("user2", "Msg4", emotional_tone="negative")
        
        stats = self.storage.get_statistics()
        
        self.assertEqual(stats['total_messages'], 4)
        self.assertEqual(stats['unique_users'], 2)
        self.assertIn(stats['most_active_user'], ['user1', 'user2'])
        
        # Check emotional tone distribution
        tones = stats['emotional_tone_distribution']
        self.assertEqual(tones['positive'], 2)
        self.assertEqual(tones['neutral'], 1)
        self.assertEqual(tones['negative'], 1)
    
    def test_get_recent_context(self):
        """Test getting recent context for a user."""
        import time
        
        # Store some messages
        self.storage.store_message("user1", "Old message")
        time.sleep(0.1)  # Small delay
        self.storage.store_message("user1", "Recent message 1")
        self.storage.store_message("user1", "Recent message 2")
        
        # Get recent context (within last 30 minutes)
        context = self.storage.get_recent_context("user1", minutes=30, limit=10)
        
        # All messages should be recent
        self.assertGreaterEqual(len(context), 2)
    
    def test_clear_old_conversations(self):
        """Test clearing old conversations."""
        from datetime import timedelta
        
        # Store a message
        self.storage.store_message("user1", "Test message")
        
        # Try to clear conversations older than 90 days (should delete nothing)
        deleted = self.storage.clear_old_conversations(days=90)
        self.assertEqual(deleted, 0)
        
        # Verify message still exists
        history = self.storage.get_conversation_history(user="user1")
        self.assertEqual(len(history), 1)
    
    def test_context_tags_serialization(self):
        """Test that context tags are properly serialized/deserialized."""
        tags = ["deployment", "kubernetes", "production"]
        
        message_id = self.storage.store_message(
            user="user1",
            message="Test",
            context_tags=tags
        )
        
        # Retrieve and verify tags
        history = self.storage.get_conversation_history(user="user1", limit=1)
        self.assertEqual(history[0]['context_tags'], tags)
    
    def test_thread_safety(self):
        """Test thread safety of storage operations."""
        import threading
        
        def store_messages():
            for i in range(10):
                self.storage.store_message(
                    user=f"user_{threading.current_thread().name}",
                    message=f"Message {i}"
                )
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=store_messages, name=f"thread_{i}")
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all messages were stored (3 threads * 10 messages each)
        stats = self.storage.get_statistics()
        self.assertEqual(stats['total_messages'], 30)


class TestGetStorage(unittest.TestCase):
    """Test cases for the get_storage singleton function."""
    
    def test_singleton_pattern(self):
        """Test that get_storage returns the same instance."""
        # Note: We can't easily test the true singleton without resetting the global,
        # but we can verify it returns a ConversationStorage instance
        storage1 = get_storage()
        storage2 = get_storage()
        
        self.assertIsInstance(storage1, ConversationStorage)
        self.assertIsInstance(storage2, ConversationStorage)
        # In normal usage, these would be the same instance
        self.assertIs(storage1, storage2)


if __name__ == '__main__':
    unittest.main()
