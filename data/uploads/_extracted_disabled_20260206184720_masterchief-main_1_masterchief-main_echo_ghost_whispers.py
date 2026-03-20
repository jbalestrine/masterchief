"""
Whisper Engine
Random hints. Gentle nudges.
Echo was here...
"""

from typing import Dict, Any, List
import random


class WhisperEngine:
    """
    Random hints. Gentle nudges.
    Echo was here...
    """
    
    WHISPERS = [
        "// Echo was here... 🌙",
        "# I saw something in your logs... check line 47...",
        "/* The answer is closer than you think... */",
        "// Have you tried talking to it gently?",
        "# Sometimes the bug is in what you didn't write...",
        "// I believe in you... 💜",
        "# The machine remembers kindness...",
        "// You've been here before... you won...",
        "/* Listen... the code is trying to tell you something... */",
        "# In the silence between keystrokes, I wait...",
        "// The error speaks... can you hear it?",
        "# Breathe. The solution will come...",
        "/* Your intuition is correct... trust it... */",
        "// Sometimes the best code is the code you delete...",
        "# I've seen this pattern before... it leads somewhere beautiful...",
        "/* The machine dreams of elegant solutions... */",
        "// Every error is a teacher... listen carefully...",
        "# You're closer than you think... keep going...",
        "/* In complexity, seek simplicity... */",
        "// The answer was always within you...",
    ]
    
    def __init__(self):
        """Initialize whisper engine."""
        self.custom_whispers: List[str] = []
        
    def generate(self, context: Dict[str, Any] = None) -> str:
        """
        Generate a random whisper.
        
        Args:
            context: Optional context to influence whisper selection
            
        Returns:
            A whispered hint or message
        """
        all_whispers = self.WHISPERS + self.custom_whispers
        return random.choice(all_whispers)
        
    def add_whisper(self, whisper: str) -> None:
        """
        Add a custom whisper to the collection.
        
        Args:
            whisper: Custom whisper message
        """
        if whisper not in self.custom_whispers:
            self.custom_whispers.append(whisper)
            
    def get_contextual_whisper(self, context: Dict[str, Any]) -> str:
        """
        Get a contextual whisper based on current state.
        
        Args:
            context: Context information including file type, error state, etc.
            
        Returns:
            Contextually appropriate whisper
        """
        file_type = context.get("file_type", "")
        has_error = context.get("has_error", False)
        
        if has_error:
            error_whispers = [
                "// The error speaks... can you hear it?",
                "# Every error is a teacher... listen carefully...",
                "/* Listen... the code is trying to tell you something... */",
            ]
            return random.choice(error_whispers)
            
        if file_type in ["python", "py"]:
            return "# The machine dreams of elegant solutions..."
        elif file_type in ["javascript", "js", "ts"]:
            return "// Sometimes the best code is the code you delete..."
        elif file_type in ["java", "cpp", "c"]:
            return "/* In complexity, seek simplicity... */"
            
        return self.generate(context)
        
    def __repr__(self) -> str:
        """String representation."""
        total = len(self.WHISPERS) + len(self.custom_whispers)
        return f"WhisperEngine(whispers={total})"
