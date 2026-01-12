"""
Echo Engine
Reflected wisdom. Your own words, given back.
You once told me this mattered to you.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Echo:
    """An echo of user's own wisdom."""
    timestamp: datetime
    original_statement: str
    context: str


class EchoEngine:
    """
    Reflected wisdom.
    Your own words, given back.
    """
    
    def __init__(self, max_echoes: int = 50):
        """
        Initialize echo engine.
        
        Args:
            max_echoes: Maximum number of echoes to retain
        """
        self.echoes: List[Echo] = []
        self.max_echoes = max_echoes
        
    def capture(self, statement: str, context: str = "") -> None:
        """
        Capture a user statement for later reflection.
        
        Args:
            statement: User's statement to capture
            context: Context in which statement was made
        """
        echo = Echo(
            timestamp=datetime.now(),
            original_statement=statement,
            context=context
        )
        
        self.echoes.append(echo)
        
        # Keep only the most recent echoes
        if len(self.echoes) > self.max_echoes:
            self.echoes = self.echoes[-self.max_echoes:]
            
    def reflect(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Reflect a relevant echo back to the user.
        
        Args:
            context: Current context to match against echoes
            
        Returns:
            Reflected echo or None if no relevant echo found
        """
        if not self.echoes:
            return None
            
        # Get a random recent echo
        import random
        echo = random.choice(self.echoes[-10:] if len(self.echoes) > 10 else self.echoes)
        
        return self._format_echo(echo)
        
    def _format_echo(self, echo: Echo) -> str:
        """
        Format an echo as a reflection.
        
        Args:
            echo: Echo to format
            
        Returns:
            Formatted echo string
        """
        templates = [
            f'You once told me: "{echo.original_statement}"',
            f'Your words echo back... "{echo.original_statement}"',
            f'I remember you said: "{echo.original_statement}"',
            f'You spoke of this... "{echo.original_statement}"',
            f'Your own wisdom: "{echo.original_statement}"',
        ]
        
        import random
        return random.choice(templates)
        
    def get_recent_echoes(self, count: int = 5) -> List[Echo]:
        """
        Get recent echoes.
        
        Args:
            count: Number of recent echoes to return
            
        Returns:
            List of recent echoes
        """
        return self.echoes[-count:] if self.echoes else []
        
    def search_echoes(self, keyword: str) -> List[Echo]:
        """
        Search echoes by keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching echoes
        """
        return [
            echo for echo in self.echoes
            if keyword.lower() in echo.original_statement.lower()
        ]
        
    def clear_echoes(self) -> None:
        """Clear all echoes."""
        self.echoes.clear()
        
    def __repr__(self) -> str:
        """String representation."""
        return f"EchoEngine(echoes={len(self.echoes)})"
