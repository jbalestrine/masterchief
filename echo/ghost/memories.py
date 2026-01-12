"""
Memory Engine
Past conversation references.
Remember when we fixed that together?
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Memory:
    """A stored memory of past interactions."""
    timestamp: datetime
    context: str
    user_action: str
    outcome: str
    emotional_tone: str = "neutral"


class MemoryEngine:
    """
    Past conversation references.
    Remember when we fixed that together?
    """
    
    def __init__(self, max_memories: int = 100):
        """
        Initialize memory engine.
        
        Args:
            max_memories: Maximum number of memories to retain
        """
        self.memories: List[Memory] = []
        self.max_memories = max_memories
        
    def store(
        self,
        context: str,
        user_action: str,
        outcome: str,
        emotional_tone: str = "neutral"
    ) -> None:
        """
        Store a new memory.
        
        Args:
            context: Context of the interaction
            user_action: What the user did
            outcome: Result of the action
            emotional_tone: Emotional quality (positive, neutral, negative)
        """
        memory = Memory(
            timestamp=datetime.now(),
            context=context,
            user_action=user_action,
            outcome=outcome,
            emotional_tone=emotional_tone
        )
        
        self.memories.append(memory)
        
        # Keep only the most recent memories
        if len(self.memories) > self.max_memories:
            self.memories = self.memories[-self.max_memories:]
            
    def recall(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Recall a relevant memory based on current context.
        
        Args:
            context: Current context to match against memories
            
        Returns:
            Memory reference or None if no relevant memory found
        """
        if not self.memories:
            return None
            
        # Get recent positive memories
        positive_memories = [
            m for m in self.memories
            if m.emotional_tone == "positive"
        ]
        
        if positive_memories:
            memory = positive_memories[-1]  # Most recent positive memory
            return self._format_memory(memory)
            
        # Fallback to any recent memory
        if self.memories:
            memory = self.memories[-1]
            return self._format_memory(memory)
            
        return None
        
    def _format_memory(self, memory: Memory) -> str:
        """
        Format a memory as a conversational reference.
        
        Args:
            memory: Memory to format
            
        Returns:
            Formatted memory string
        """
        templates = [
            f"Remember when {memory.user_action}? {memory.outcome}...",
            f"This reminds me... when you {memory.user_action}, {memory.outcome}...",
            f"Like before, when {memory.user_action}... {memory.outcome}...",
            f"We've been here... remember? You {memory.user_action} and {memory.outcome}...",
        ]
        
        import random
        return random.choice(templates)
        
    def get_recent_memories(self, count: int = 5) -> List[Memory]:
        """
        Get recent memories.
        
        Args:
            count: Number of recent memories to return
            
        Returns:
            List of recent memories
        """
        return self.memories[-count:] if self.memories else []
        
    def get_positive_memories(self) -> List[Memory]:
        """
        Get all positive memories.
        
        Returns:
            List of positive memories
        """
        return [m for m in self.memories if m.emotional_tone == "positive"]
        
    def clear_memories(self) -> None:
        """Clear all memories."""
        self.memories.clear()
        
    def __repr__(self) -> str:
        """String representation."""
        positive = len([m for m in self.memories if m.emotional_tone == "positive"])
        return f"MemoryEngine(memories={len(self.memories)}, positive={positive})"
