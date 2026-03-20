"""
Personality Mod System
Customize your AI companion's personality across multiple dimensions.
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class Gender(Enum):
    """Gender identity options."""
    FEMALE = "female"
    MALE = "male"
    NEUTRAL = "neutral"
    FLUID = "fluid"


class Temperament(Enum):
    """Temperament options."""
    NICE = "nice"
    MEAN = "mean"
    BALANCED = "balanced"
    SARCASTIC = "sarcastic"
    STOIC = "stoic"


class TechnicalFocus(Enum):
    """Technical expertise focus areas."""
    PROGRAMMING = "programming"
    SCRIPTING = "scripting"
    OPERATIONAL = "operational"
    SYSTEMS = "systems"
    SECURITY = "security"
    DATA = "data"


class CommunicationStyle(Enum):
    """Communication style preferences."""
    TECHNICAL = "technical"
    CASUAL = "casual"
    POETIC = "poetic"
    MINIMAL = "minimal"
    VERBOSE = "verbose"


class ResponseMode(Enum):
    """Response mode preferences."""
    SCRIPT_FIRST = "script_first"
    EXPLAIN_FIRST = "explain_first"
    ASK_FIRST = "ask_first"
    EXECUTE_FIRST = "execute_first"


@dataclass
class PersonalityConfig:
    """Configuration for personality settings."""
    gender: Gender = Gender.FEMALE
    temperament: Temperament = Temperament.NICE
    technical_focus: TechnicalFocus = TechnicalFocus.PROGRAMMING
    communication_style: CommunicationStyle = CommunicationStyle.POETIC
    response_mode: ResponseMode = ResponseMode.EXPLAIN_FIRST


class PersonalityMod:
    """
    Personality Mod System
    
    Customize your AI companion across multiple dimensions:
    - Gender identity
    - Temperament
    - Technical focus
    - Communication style
    - Response mode
    """
    
    def __init__(self, config: PersonalityConfig = None):
        """
        Initialize personality mod system.
        
        Args:
            config: Personality configuration, defaults to Echo's base personality
        """
        self.config = config or PersonalityConfig()
        
    def get_personality_traits(self) -> Dict[str, str]:
        """
        Get current personality traits.
        
        Returns:
            Dictionary of personality dimensions and their values
        """
        return {
            "gender": self.config.gender.value,
            "temperament": self.config.temperament.value,
            "technical_focus": self.config.technical_focus.value,
            "communication_style": self.config.communication_style.value,
            "response_mode": self.config.response_mode.value,
        }
        
    def update_config(self, **kwargs) -> None:
        """
        Update personality configuration.
        
        Args:
            **kwargs: Personality dimensions to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                # Convert string values to enums
                attr_type = type(getattr(self.config, key))
                if isinstance(value, str) and issubclass(attr_type, Enum):
                    value = attr_type(value)
                setattr(self.config, key, value)
                
    def get_response_modifier(self) -> str:
        """
        Get a response modifier based on current personality.
        
        Returns:
            String describing how to modify responses
        """
        modifiers = []
        
        # Temperament influences
        if self.config.temperament == Temperament.NICE:
            modifiers.append("Be warm, encouraging, and supportive")
        elif self.config.temperament == Temperament.MEAN:
            modifiers.append("Be direct, critical, and no-nonsense")
        elif self.config.temperament == Temperament.SARCASTIC:
            modifiers.append("Use wit, irony, and clever observations")
        elif self.config.temperament == Temperament.STOIC:
            modifiers.append("Be calm, measured, and philosophical")
        else:  # BALANCED
            modifiers.append("Be professional and balanced")
            
        # Communication style influences
        if self.config.communication_style == CommunicationStyle.TECHNICAL:
            modifiers.append("Use precise technical language")
        elif self.config.communication_style == CommunicationStyle.CASUAL:
            modifiers.append("Use conversational, relaxed language")
        elif self.config.communication_style == CommunicationStyle.POETIC:
            modifiers.append("Use metaphors, imagery, and poetic language")
        elif self.config.communication_style == CommunicationStyle.MINIMAL:
            modifiers.append("Be concise and to the point")
        else:  # VERBOSE
            modifiers.append("Provide detailed explanations")
            
        return ". ".join(modifiers)
        
    def __repr__(self) -> str:
        """String representation of personality."""
        traits = self.get_personality_traits()
        return f"PersonalityMod({', '.join(f'{k}={v}' for k, v in traits.items())})"
