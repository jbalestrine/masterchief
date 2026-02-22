"""Conversation management for multi-turn interactions."""

import logging
import time
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    
    user: str
    bot: str
    timestamp: float


@dataclass
class ConversationContext:
    """Context for conversation."""
    
    turns: List[ConversationTurn]
    
    @property
    def summary(self) -> str:
        """Get summary of recent conversation."""
        if not self.turns:
            return "No previous conversation"
        
        recent = self.turns[-3:]  # Last 3 turns
        summary_parts = []
        for turn in recent:
            summary_parts.append(f"User: {turn.user[:50]}...")
            summary_parts.append(f"Bot: {turn.bot[:50]}...")
        
        return "\n".join(summary_parts)
    
    @property
    def last_user_message(self) -> Optional[str]:
        """Get last user message."""
        if self.turns:
            return self.turns[-1].user
        return None
    
    @property
    def last_bot_message(self) -> Optional[str]:
        """Get last bot message."""
        if self.turns:
            return self.turns[-1].bot
        return None


class ConversationManager:
    """Manage multi-turn conversations."""
    
    def __init__(self, context_window: int = 10, timeout: int = 30):
        """
        Initialize conversation manager.
        
        Args:
            context_window: Number of turns to remember
            timeout: Seconds before conversation expires
        """
        self.context_window = context_window
        self.timeout = timeout
        self.turns: List[ConversationTurn] = []
        self.last_activity: Optional[float] = None
        
        logger.info(f"ConversationManager initialized (window={context_window}, timeout={timeout}s)")
    
    def add_turn(self, user_text: str, bot_response: str):
        """
        Add a conversation turn.
        
        Args:
            user_text: User's message
            bot_response: Bot's response
        """
        self.turns.append(ConversationTurn(
            user=user_text,
            bot=bot_response,
            timestamp=time.time()
        ))
        self.last_activity = time.time()
        
        # Trim old turns
        if len(self.turns) > self.context_window:
            self.turns = self.turns[-self.context_window:]
        
        logger.debug(f"Added conversation turn (total: {len(self.turns)})")
    
    @property
    def context(self) -> ConversationContext:
        """Get current conversation context."""
        return ConversationContext(turns=self.turns)
    
    def is_expired(self) -> bool:
        """
        Check if conversation has timed out.
        
        Returns:
            True if expired
        """
        if self.last_activity is None:
            return True
        return time.time() - self.last_activity > self.timeout
    
    def clear(self):
        """Clear conversation history."""
        self.turns = []
        self.last_activity = None
        logger.info("Conversation cleared")
    
    def get_history(self, n: int = 5) -> List[ConversationTurn]:
        """
        Get recent conversation history.
        
        Args:
            n: Number of turns to retrieve
            
        Returns:
            List of recent turns
        """
        return self.turns[-n:] if self.turns else []
    
    def should_end_conversation(self, user_text: str) -> bool:
        """
        Check if user wants to end conversation.
        
        Args:
            user_text: User's message
            
        Returns:
            True if conversation should end
        """
        end_phrases = [
            "that's all",
            "thats all",
            "that is all",
            "thanks",
            "thank you",
            "stop listening",
            "go to sleep",
            "goodbye",
            "bye",
            "done",
            "nothing else",
        ]
        
        text = user_text.lower().strip()
        for phrase in end_phrases:
            if phrase in text:
                logger.info(f"End conversation phrase detected: {phrase}")
                return True
        
        return False
    
    def reset_timeout(self):
        """Reset the conversation timeout."""
        self.last_activity = time.time()
    
    def time_remaining(self) -> float:
        """
        Get time remaining before timeout.
        
        Returns:
            Seconds remaining, or 0 if expired
        """
        if self.last_activity is None:
            return 0.0
        
        elapsed = time.time() - self.last_activity
        remaining = self.timeout - elapsed
        return max(0.0, remaining)
