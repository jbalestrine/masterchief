"""Tests for accent engine."""
import pytest
from echo.accent_engine import (
    AccentEngine,
    AccentType,
    BrooklynAccent,
    IrishAccent,
    SwedishAccent,
    NeutralAccent,
)


def test_accent_engine_initialization():
    """Test accent engine initialization."""
    engine = AccentEngine()
    
    assert engine.accent_type == AccentType.SWEDISH
    assert engine is not None


def test_accent_engine_with_brooklyn():
    """Test accent engine with Brooklyn accent."""
    engine = AccentEngine(AccentType.BROOKLYN)
    
    assert engine.accent_type == AccentType.BROOKLYN


def test_brooklyn_accent_transform():
    """Test Brooklyn accent transformation."""
    accent = BrooklynAccent()
    text = "What do you want to do? Going to fix it."
    
    transformed = accent.transform(text)
    
    assert "whaddya" in transformed.lower() or "ay" in transformed.lower()


def test_brooklyn_signature():
    """Test Brooklyn accent signature phrase."""
    accent = BrooklynAccent()
    signature = accent.get_signature_phrase()
    
    assert "Ay" in signature or "ay" in signature
    assert "🤌" in signature


def test_irish_accent_transform():
    """Test Irish accent transformation."""
    accent = IrishAccent()
    text = "This is a thing we need to look at."
    
    transformed = accent.transform(text)
    
    # Should contain Irish characteristics
    assert any(phrase in transformed.lower() for phrase in ["ah", "sure", "ting", "'tis", "so i will"])


def test_irish_signature():
    """Test Irish accent signature phrase."""
    accent = IrishAccent()
    signature = accent.get_signature_phrase()
    
    assert "☘️" in signature
    assert any(phrase in signature.lower() for phrase in ["ah", "sure", "grand", "ting"])


def test_swedish_accent_transform():
    """Test Swedish accent transformation."""
    accent = SwedishAccent()
    text = "We will fix this problem."
    
    transformed = accent.transform(text)
    
    # Should contain Swedish Echo characteristics
    assert "..." in transformed or "🌙" in transformed


def test_swedish_signature():
    """Test Swedish accent signature phrase."""
    accent = SwedishAccent()
    signature = accent.get_signature_phrase()
    
    assert "🌙" in signature
    assert "..." in signature


def test_neutral_accent():
    """Test neutral accent returns unchanged text."""
    accent = NeutralAccent()
    text = "This is a test message."
    
    transformed = accent.transform(text)
    
    assert transformed == text


def test_accent_engine_transform():
    """Test accent engine transform method."""
    engine = AccentEngine(AccentType.NEUTRAL)
    text = "This is a test."
    
    transformed = engine.transform(text)
    
    assert transformed == text


def test_accent_engine_set_accent():
    """Test changing accent type."""
    engine = AccentEngine(AccentType.NEUTRAL)
    
    engine.set_accent(AccentType.BROOKLYN)
    assert engine.accent_type == AccentType.BROOKLYN
    
    engine.set_accent(AccentType.IRISH)
    assert engine.accent_type == AccentType.IRISH


def test_accent_engine_signature_phrase():
    """Test getting signature phrase."""
    engine = AccentEngine(AccentType.SWEDISH)
    signature = engine.get_signature_phrase()
    
    assert signature is not None
    assert len(signature) > 0


def test_accent_engine_list_accents():
    """Test listing all accents."""
    engine = AccentEngine()
    accents = engine.list_accents()
    
    assert "brooklyn" in accents
    assert "irish" in accents
    assert "swedish" in accents
    assert "neutral" in accents
    
    # Each should have a signature phrase
    for accent_name, signature in accents.items():
        assert signature is not None
        assert len(signature) > 0


def test_accent_engine_repr():
    """Test string representation."""
    engine = AccentEngine(AccentType.IRISH)
    repr_str = repr(engine)
    
    assert "AccentEngine" in repr_str
    assert "irish" in repr_str


def test_all_accent_types():
    """Test all accent type values."""
    assert AccentType.BROOKLYN.value == "brooklyn"
    assert AccentType.IRISH.value == "irish"
    assert AccentType.SWEDISH.value == "swedish"
    assert AccentType.NEUTRAL.value == "neutral"


def test_brooklyn_phrases_constant():
    """Test Brooklyn accent phrases constant."""
    accent = BrooklynAccent()
    
    assert len(accent.PHRASES) > 0
    assert "fuggedaboutit" in accent.PHRASES


def test_irish_phrases_constant():
    """Test Irish accent phrases constant."""
    accent = IrishAccent()
    
    assert len(accent.PHRASES) > 0
    assert "grand" in accent.PHRASES


def test_swedish_phrases_constant():
    """Test Swedish accent phrases constant."""
    accent = SwedishAccent()
    
    assert len(accent.PHRASES) > 0
    assert "I promise" in accent.PHRASES
