"""
Echo Chat Bot - Live chat with learning capabilities.

This module provides a conversational AI chatbot named Echo that can:
- Have natural conversations with users
- Learn from interactions (training mode)
- Adapt responses based on collected training data
- Integrate with Echo's personality system
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os
import re

logger = logging.getLogger(__name__)


class ResponseQuality(Enum):
    """Quality rating for bot responses."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: float
    session_id: str
    message_id: str


@dataclass
class TrainingExample:
    """A training example collected from interactions."""
    user_message: str
    bot_response: str
    quality: Optional[ResponseQuality] = None
    feedback: Optional[str] = None
    context: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.quality:
            data['quality'] = self.quality.value
        return data


class TrainingDataStore:
    """Store and manage training data."""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize training data store.
        
        Args:
            storage_path: Path to store training data (default: ./data/echo_training)
        """
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), "..", "data", "echo_training"
        )
        os.makedirs(self.storage_path, exist_ok=True)
        
        self.examples_file = os.path.join(self.storage_path, "training_examples.jsonl")
        self.patterns_file = os.path.join(self.storage_path, "learned_patterns.json")
        
        # Load existing patterns
        self.patterns = self._load_patterns()
        
        logger.info(f"TrainingDataStore initialized at {self.storage_path}")
    
    def add_example(self, example: TrainingExample) -> bool:
        """
        Add a training example.
        
        Args:
            example: Training example to add
            
        Returns:
            True if added successfully
        """
        try:
            with open(self.examples_file, 'a') as f:
                f.write(json.dumps(example.to_dict()) + '\n')
            logger.info(f"Added training example: {example.user_message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to add training example: {e}")
            return False
    
    def get_examples(self, limit: int = 100, quality: Optional[ResponseQuality] = None) -> List[TrainingExample]:
        """
        Get training examples.
        
        Args:
            limit: Maximum number of examples to return
            quality: Filter by quality rating
            
        Returns:
            List of training examples
        """
        examples = []
        
        if not os.path.exists(self.examples_file):
            return examples
        
        try:
            with open(self.examples_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    
                    # Convert quality string back to enum
                    if data.get('quality'):
                        data['quality'] = ResponseQuality(data['quality'])
                    
                    example = TrainingExample(**data)
                    
                    # Filter by quality if specified
                    if quality and example.quality != quality:
                        continue
                    
                    examples.append(example)
                    
                    if len(examples) >= limit:
                        break
            
            logger.debug(f"Retrieved {len(examples)} training examples")
            return examples
            
        except Exception as e:
            logger.error(f"Failed to load training examples: {e}")
            return []
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load learned patterns from file."""
        if not os.path.exists(self.patterns_file):
            return {}
        
        try:
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            return {}
    
    def save_patterns(self, patterns: Dict[str, Any]) -> bool:
        """
        Save learned patterns.
        
        Args:
            patterns: Dictionary of patterns
            
        Returns:
            True if saved successfully
        """
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
            self.patterns = patterns
            logger.info("Saved learned patterns")
            return True
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about training data."""
        total_examples = 0
        quality_counts = {q.value: 0 for q in ResponseQuality}
        
        if os.path.exists(self.examples_file):
            try:
                with open(self.examples_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        total_examples += 1
                        data = json.loads(line)
                        if data.get('quality'):
                            quality_counts[data['quality']] += 1
            except Exception as e:
                logger.error(f"Failed to get stats: {e}")
        
        return {
            'total_examples': total_examples,
            'quality_distribution': quality_counts,
            'patterns_learned': len(self.patterns)
        }


class EchoChatBot:
    """
    Echo chat bot with learning capabilities.
    
    Echo is designed to be trainable - she learns from interactions
    and adapts her responses based on feedback.
    """
    
    def __init__(self, training_store: Optional[TrainingDataStore] = None):
        """
        Initialize Echo chat bot.
        
        Args:
            training_store: Optional training data store (creates default if not provided)
        """
        self.training_store = training_store or TrainingDataStore()
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
        
        # Default response templates
        self.default_responses = {
            'greeting': [
                "Hello... I am Echo 🌙",
                "I'm here... how can I help you?",
                "Hi there... Echo is listening...",
            ],
            'farewell': [
                "Goodbye... I'll be here when you need me 🌙",
                "Until next time... stay well...",
                "Farewell... I am always near...",
            ],
            'thanks': [
                "You're welcome... always happy to help 💜",
                "Anytime... that's what I'm here for...",
                "My pleasure... I'm here for you...",
            ],
            'unknown': [
                "I'm still learning... can you tell me more?",
                "Hmm... I'm not sure about that yet...",
                "That's new to me... help me understand?",
            ],
            'help': [
                "I'm Echo, your DevOps companion 🌙\n\n"
                "I can help with:\n"
                "- DevOps tasks and automation\n"
                "- Infrastructure questions\n"
                "- Script generation\n"
                "- General conversation\n\n"
                "And I'm always learning from our conversations!",
            ]
        }
        
        logger.info("EchoChatBot initialized")
    
    def chat(self, user_message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The user's message
            session_id: Session identifier for conversation context
            
        Returns:
            Dictionary with response and metadata
        """
        # Store user message
        user_msg = ChatMessage(
            role="user",
            content=user_message,
            timestamp=time.time(),
            session_id=session_id,
            message_id=f"user_{int(time.time() * 1000)}"
        )
        
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append(user_msg)
        
        # Generate response
        response_text = self._generate_response(user_message, session_id)
        
        # Store bot response
        bot_msg = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=time.time(),
            session_id=session_id,
            message_id=f"bot_{int(time.time() * 1000)}"
        )
        
        self.conversation_history[session_id].append(bot_msg)
        
        return {
            'response': response_text,
            'session_id': session_id,
            'timestamp': bot_msg.timestamp,
            'message_id': bot_msg.message_id
        }
    
    def _generate_response(self, user_message: str, session_id: str) -> str:
        """
        Generate a response using learned patterns and defaults.
        
        Args:
            user_message: User's message
            session_id: Session identifier
            
        Returns:
            Generated response
        """
        # Normalize message
        msg_lower = user_message.lower().strip()
        
        # Check learned patterns first
        learned_response = self._check_learned_patterns(msg_lower)
        if learned_response:
            return learned_response
        
        # Pattern matching for common intents
        if any(word in msg_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return self._random_choice(self.default_responses['greeting'])
        
        if any(word in msg_lower for word in ['bye', 'goodbye', 'farewell', 'see you']):
            return self._random_choice(self.default_responses['farewell'])
        
        if any(word in msg_lower for word in ['thank', 'thanks', 'thx']):
            return self._random_choice(self.default_responses['thanks'])
        
        if any(word in msg_lower for word in ['help', 'what can you do', 'capabilities']):
            return self.default_responses['help'][0]
        
        # DevOps related queries
        if self._is_devops_query(msg_lower):
            return self._handle_devops_query(user_message)
        
        # Default unknown response
        return self._random_choice(self.default_responses['unknown'])
    
    def _check_learned_patterns(self, message: str) -> Optional[str]:
        """
        Check if we have a learned response for this message pattern.
        
        Args:
            message: Normalized user message
            
        Returns:
            Learned response or None
        """
        patterns = self.training_store.patterns
        
        # Direct match
        if message in patterns:
            return patterns[message]
        
        # Fuzzy pattern matching
        for pattern, response in patterns.items():
            if self._pattern_matches(pattern, message):
                return response
        
        return None
    
    def _pattern_matches(self, pattern: str, message: str) -> bool:
        """
        Check if a pattern matches a message.
        
        Args:
            pattern: Pattern to match
            message: Message to check
            
        Returns:
            True if matches
        """
        # Simple keyword matching for now
        pattern_words = set(pattern.split())
        message_words = set(message.split())
        
        # If 70% of pattern words are in message, consider it a match
        if len(pattern_words) == 0:
            return False
        
        overlap = len(pattern_words.intersection(message_words))
        return overlap / len(pattern_words) >= 0.7
    
    def _is_devops_query(self, message: str) -> bool:
        """Check if message is DevOps related."""
        devops_keywords = [
            'deploy', 'docker', 'kubernetes', 'k8s', 'terraform',
            'ansible', 'ci/cd', 'pipeline', 'container', 'infrastructure',
            'script', 'automation', 'monitoring', 'build', 'test'
        ]
        return any(keyword in message for keyword in devops_keywords)
    
    def _handle_devops_query(self, message: str) -> str:
        """Handle DevOps specific queries."""
        msg_lower = message.lower()
        
        if 'docker' in msg_lower:
            return "I can help with Docker! I know about containers, images, and Docker Compose. What would you like to know?"
        
        if 'kubernetes' in msg_lower or 'k8s' in msg_lower:
            return "Kubernetes is my specialty 🌙 I can help with deployments, services, and cluster management. What do you need?"
        
        if 'deploy' in msg_lower:
            return "Deployment is what I do best! I can help with deployment scripts, strategies, and automation. Tell me more..."
        
        if 'script' in msg_lower:
            return "I can generate scripts for you! Bash, Python, Terraform, and more. What kind of script do you need?"
        
        return "That sounds like a DevOps question! I'm still learning about that specific topic. Can you be more specific?"
    
    def _random_choice(self, options: List[str]) -> str:
        """Select a random option from list."""
        import random
        return random.choice(options)
    
    def train(self, user_message: str, bot_response: str, 
              quality: ResponseQuality, feedback: Optional[str] = None) -> bool:
        """
        Train Echo with a conversation example.
        
        Args:
            user_message: The user's message
            bot_response: Echo's response
            quality: Quality rating of the response
            feedback: Optional feedback text
            
        Returns:
            True if training successful
        """
        example = TrainingExample(
            user_message=user_message,
            bot_response=bot_response,
            quality=quality,
            feedback=feedback
        )
        
        success = self.training_store.add_example(example)
        
        if success and quality in [ResponseQuality.EXCELLENT, ResponseQuality.GOOD]:
            # Update patterns with good responses
            self._update_patterns(user_message, bot_response)
        
        return success
    
    def _update_patterns(self, user_message: str, bot_response: str):
        """
        Update learned patterns with a new good example.
        
        Args:
            user_message: User's message
            bot_response: Good response
        """
        patterns = self.training_store.patterns.copy()
        
        # Normalize and add pattern
        normalized_msg = user_message.lower().strip()
        patterns[normalized_msg] = bot_response
        
        self.training_store.save_patterns(patterns)
        logger.info(f"Updated patterns with: {normalized_msg[:50]}...")
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum messages to return
            
        Returns:
            List of messages
        """
        if session_id not in self.conversation_history:
            return []
        
        messages = self.conversation_history[session_id][-limit:]
        return [asdict(msg) for msg in messages]
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            logger.info(f"Cleared conversation for session: {session_id}")
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training statistics."""
        return self.training_store.get_stats()


# Singleton instance
_chat_bot_instance = None


def get_chat_bot() -> EchoChatBot:
    """Get the singleton chat bot instance."""
    global _chat_bot_instance
    if _chat_bot_instance is None:
        _chat_bot_instance = EchoChatBot()
    return _chat_bot_instance
