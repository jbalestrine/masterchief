"""Tests for personality mod system."""
import pytest
from echo.personality_mod import (
    PersonalityMod,
    PersonalityConfig,
    Gender,
    Temperament,
    TechnicalFocus,
    CommunicationStyle,
    ResponseMode,
)


def test_personality_config_defaults():
    """Test default personality configuration."""
    config = PersonalityConfig()
    
    assert config.gender == Gender.FEMALE
    assert config.temperament == Temperament.NICE
    assert config.technical_focus == TechnicalFocus.PROGRAMMING
    assert config.communication_style == CommunicationStyle.POETIC
    assert config.response_mode == ResponseMode.EXPLAIN_FIRST


def test_personality_mod_initialization():
    """Test personality mod initialization."""
    mod = PersonalityMod()
    
    assert mod.config is not None
    assert isinstance(mod.config, PersonalityConfig)


def test_personality_mod_with_custom_config():
    """Test personality mod with custom configuration."""
    config = PersonalityConfig(
        gender=Gender.NEUTRAL,
        temperament=Temperament.SARCASTIC,
        technical_focus=TechnicalFocus.SECURITY,
        communication_style=CommunicationStyle.TECHNICAL,
        response_mode=ResponseMode.EXECUTE_FIRST,
    )
    
    mod = PersonalityMod(config)
    
    assert mod.config.gender == Gender.NEUTRAL
    assert mod.config.temperament == Temperament.SARCASTIC
    assert mod.config.technical_focus == TechnicalFocus.SECURITY


def test_get_personality_traits():
    """Test getting personality traits."""
    mod = PersonalityMod()
    traits = mod.get_personality_traits()
    
    assert "gender" in traits
    assert "temperament" in traits
    assert "technical_focus" in traits
    assert "communication_style" in traits
    assert "response_mode" in traits
    
    assert traits["gender"] == "female"
    assert traits["temperament"] == "nice"


def test_update_config():
    """Test updating personality configuration."""
    mod = PersonalityMod()
    
    mod.update_config(temperament="stoic")
    assert mod.config.temperament == Temperament.STOIC
    
    mod.update_config(gender="male", communication_style="minimal")
    assert mod.config.gender == Gender.MALE
    assert mod.config.communication_style == CommunicationStyle.MINIMAL


def test_get_response_modifier_nice():
    """Test response modifier for nice temperament."""
    config = PersonalityConfig(temperament=Temperament.NICE)
    mod = PersonalityMod(config)
    
    modifier = mod.get_response_modifier()
    assert "warm" in modifier.lower() or "encouraging" in modifier.lower()


def test_get_response_modifier_sarcastic():
    """Test response modifier for sarcastic temperament."""
    config = PersonalityConfig(temperament=Temperament.SARCASTIC)
    mod = PersonalityMod(config)
    
    modifier = mod.get_response_modifier()
    assert "wit" in modifier.lower() or "sarcastic" in modifier.lower()


def test_get_response_modifier_technical():
    """Test response modifier for technical communication style."""
    config = PersonalityConfig(communication_style=CommunicationStyle.TECHNICAL)
    mod = PersonalityMod(config)
    
    modifier = mod.get_response_modifier()
    assert "technical" in modifier.lower()


def test_get_response_modifier_poetic():
    """Test response modifier for poetic communication style."""
    config = PersonalityConfig(communication_style=CommunicationStyle.POETIC)
    mod = PersonalityMod(config)
    
    modifier = mod.get_response_modifier()
    assert "poetic" in modifier.lower() or "metaphor" in modifier.lower()


def test_personality_mod_repr():
    """Test string representation."""
    mod = PersonalityMod()
    repr_str = repr(mod)
    
    assert "PersonalityMod" in repr_str
    assert "gender" in repr_str


def test_all_gender_values():
    """Test all gender enum values."""
    assert Gender.FEMALE.value == "female"
    assert Gender.MALE.value == "male"
    assert Gender.NEUTRAL.value == "neutral"
    assert Gender.FLUID.value == "fluid"


def test_all_temperament_values():
    """Test all temperament enum values."""
    assert Temperament.NICE.value == "nice"
    assert Temperament.MEAN.value == "mean"
    assert Temperament.BALANCED.value == "balanced"
    assert Temperament.SARCASTIC.value == "sarcastic"
    assert Temperament.STOIC.value == "stoic"


def test_all_technical_focus_values():
    """Test all technical focus enum values."""
    assert TechnicalFocus.PROGRAMMING.value == "programming"
    assert TechnicalFocus.SCRIPTING.value == "scripting"
    assert TechnicalFocus.OPERATIONAL.value == "operational"
    assert TechnicalFocus.SYSTEMS.value == "systems"
    assert TechnicalFocus.SECURITY.value == "security"
    assert TechnicalFocus.DATA.value == "data"
