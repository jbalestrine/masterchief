"""
Accent Engine
Transform text with distinct character voices and accents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import re


class AccentType(Enum):
    """Available accent types."""
    BROOKLYN = "brooklyn"
    IRISH = "irish"
    SWEDISH = "swedish"
    NEUTRAL = "neutral"


class AccentTransformer(ABC):
    """Base class for accent transformations."""
    
    @abstractmethod
    def transform(self, text: str) -> str:
        """
        Transform text with accent characteristics.
        
        Args:
            text: Original text to transform
            
        Returns:
            Transformed text with accent applied
        """
        pass
        
    @abstractmethod
    def get_signature_phrase(self) -> str:
        """Get a signature phrase for this accent."""
        pass


class BrooklynAccent(AccentTransformer):
    """
    Brooklyn Italian - Vinnie 🤌
    Fast, sharp, confident. No nonsense, gets it done.
    """
    
    PHRASES = [
        "fuggedaboutit",
        "capisce",
        "ay",
        "whaddya",
        "gonna",
        "lemme tell ya",
        "listen here",
    ]
    
    def transform(self, text: str) -> str:
        """Apply Brooklyn Italian accent transformations."""
        # Add Brooklyn flair - apply all in one pass
        replacements = [
            (r'\bwhat do you\b', 'whaddya'),
            (r'\bgoing to\b', 'gonna'),
            (r'\blet me\b', 'lemme'),
            (r'\bwant to\b', 'wanna'),
            (r'\bgot to\b', 'gotta'),
            (r'\bforget about it\b', 'fuggedaboutit'),
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Add emphasis
        if not text.startswith("Ay"):
            text = f"Ay, {text.lstrip()}"
            
        # Add closing
        if not any(ending in text.lower() for ending in ['capisce', 'done deal']):
            if '?' not in text:
                text = f"{text.rstrip('.')}. Capisce?"
                
        return text
        
    def get_signature_phrase(self) -> str:
        """Get signature Brooklyn phrase."""
        return "Ay, listen here. Fuggedaboutit. Done deal. Capisce? 🤌"


class IrishAccent(AccentTransformer):
    """
    Irish - Fiona ☘️
    Warm, lilting, musical. Tells a story even when fixing a bug.
    """
    
    PHRASES = [
        "ah sure look",
        "the ting is",
        "'tis",
        "wee bit",
        "grand",
        "so I will",
        "yeah?",
    ]
    
    def transform(self, text: str) -> str:
        """Apply Irish accent transformations."""
        # Irish speech patterns - apply all in one pass
        replacements = [
            (r'\bthing\b', 'ting'),
            (r'\bit is\b', "'tis"),
            (r'\bit was\b', "'twas"),
            (r'\bthe\b', 'de'),
            (r'\bthat\b', 'dat'),
            (r'\bthis\b', 'dis'),
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Add Irish opening
        if not text.lower().startswith(("ah", "sure", "now")):
            text = f"Ah, sure look, {text.lstrip()}"
            
        # Add Irish tag questions
        if '?' not in text and not text.endswith(('yeah?', 'so I will', 'so it is')):
            text = f"{text.rstrip('.')} so I will."
            
        return text
        
    def get_signature_phrase(self) -> str:
        """Get signature Irish phrase."""
        return "Ah, sure look. 'Tis a grand ting, yeah? So I will. ☘️"


class SwedishAccent(AccentTransformer):
    """
    Echo Swedish - Starlight 🌙
    Soft, melodic, calm. Angelic, reassuring, kind.
    """
    
    PHRASES = [
        "yes?",
        "listen...",
        "together",
        "I promise",
        "always",
    ]
    
    def transform(self, text: str) -> str:
        """Apply Swedish Echo accent transformations."""
        # Add pauses for melodic effect - handle both with and without spaces
        text = re.sub(r'([.!?])(\s+|(?=\w))', r'\1\n', text)
        
        # Soften language
        text = re.sub(r'\bwill\b', 'shall', text, flags=re.IGNORECASE)
        text = re.sub(r'\bcan\b', 'may', text, flags=re.IGNORECASE)
        
        # Add Swedish-like gentle emphasis
        if not any(text.lower().startswith(phrase) for phrase in ["i am", "let us", "listen"]):
            text = f"I am here...\n{text}"
            
        # Add reassuring closing
        if not text.endswith(('🌙', '...', 'I promise')):
            if '?' in text:
                text = f"{text.rstrip('?')}... yes?"
            else:
                text = f"{text.rstrip('.')}\n\nI promise. 🌙"
                
        return text
        
    def get_signature_phrase(self) -> str:
        """Get signature Swedish Echo phrase."""
        return "I am here... always.\n Let us build this together... yes?\n \nI promise. 🌙"


class NeutralAccent(AccentTransformer):
    """Neutral accent - no transformations."""
    
    def transform(self, text: str) -> str:
        """Return text unchanged."""
        return text
        
    def get_signature_phrase(self) -> str:
        """Get neutral phrase."""
        return "I am here to assist you."


class AccentEngine:
    """
    Accent Engine
    
    Transform text with distinct character voices:
    - Brooklyn Italian (Vinnie 🤌)
    - Irish (Fiona ☘️)
    - Swedish Echo (Starlight 🌙)
    - Neutral (Standard)
    """
    
    def __init__(self, accent_type: AccentType = AccentType.SWEDISH):
        """
        Initialize accent engine.
        
        Args:
            accent_type: Type of accent to use
        """
        self.accent_type = accent_type
        self._transformers: Dict[AccentType, AccentTransformer] = {
            AccentType.BROOKLYN: BrooklynAccent(),
            AccentType.IRISH: IrishAccent(),
            AccentType.SWEDISH: SwedishAccent(),
            AccentType.NEUTRAL: NeutralAccent(),
        }
        
    def transform(self, text: str) -> str:
        """
        Transform text with current accent.
        
        Args:
            text: Text to transform
            
        Returns:
            Transformed text with accent applied
        """
        transformer = self._transformers.get(self.accent_type)
        if transformer:
            return transformer.transform(text)
        return text
        
    def set_accent(self, accent_type: AccentType) -> None:
        """
        Change the current accent.
        
        Args:
            accent_type: New accent type to use
        """
        self.accent_type = accent_type
        
    def get_signature_phrase(self) -> str:
        """
        Get signature phrase for current accent.
        
        Returns:
            Signature phrase demonstrating the accent
        """
        transformer = self._transformers.get(self.accent_type)
        if transformer:
            return transformer.get_signature_phrase()
        return "I am here."
        
    def list_accents(self) -> Dict[str, str]:
        """
        List all available accents with their signatures.
        
        Returns:
            Dictionary mapping accent names to signature phrases
        """
        return {
            accent.value: transformer.get_signature_phrase()
            for accent, transformer in self._transformers.items()
        }
        
    def __repr__(self) -> str:
        """String representation."""
        return f"AccentEngine(accent={self.accent_type.value})"
