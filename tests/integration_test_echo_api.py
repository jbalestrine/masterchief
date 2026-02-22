"""
Integration tests for Echo Chat API endpoints.
"""

import os
import sys
import unittest
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import after path is set
from main import app


class TestEchoAPI(unittest.TestCase):
    """Test Echo chat API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_echo_chat_page_loads(self):
        """Test that Echo chat page loads successfully."""
        response = self.client.get('/echo-chat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Echo Starlite - Chat', response.data)
        self.assertIn(b'Training Stats', response.data)
    
    def test_echo_chat_api(self):
        """Test Echo chat API endpoint."""
        response = self.client.post('/api/echo/chat',
                                     json={'message': 'Hello', 'session_id': 'test'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('session_id', data)
        self.assertIn('timestamp', data)
        self.assertIn('message_id', data)
        self.assertEqual(data['session_id'], 'test')
    
    def test_echo_chat_api_no_message(self):
        """Test Echo chat API with no message."""
        response = self.client.post('/api/echo/chat',
                                     json={'session_id': 'test'})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_echo_stats_api(self):
        """Test Echo stats API endpoint."""
        response = self.client.get('/api/echo/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_examples', data)
        self.assertIn('quality_distribution', data)
        self.assertIn('patterns_learned', data)
    
    def test_echo_train_api(self):
        """Test Echo training API endpoint."""
        response = self.client.post('/api/echo/train',
                                     json={
                                         'user_message': 'test question',
                                         'bot_response': 'test answer',
                                         'quality': 'excellent'
                                     })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertTrue(data['success'])
    
    def test_echo_history_api(self):
        """Test Echo history API endpoint."""
        # First, send a message
        self.client.post('/api/echo/chat',
                         json={'message': 'Test message', 'session_id': 'history_test'})
        
        # Then get history
        response = self.client.get('/api/echo/history?session_id=history_test')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('history', data)
        self.assertIsInstance(data['history'], list)
    
    def test_echo_search_api(self):
        """Test Echo search API endpoint."""
        response = self.client.get('/api/echo/search?q=test')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertIsInstance(data['results'], list)
    
    def test_echo_search_api_no_query(self):
        """Test Echo search API with no query parameter."""
        response = self.client.get('/api/echo/search')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
