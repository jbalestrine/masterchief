"""
Unit tests for Echo identity system.
"""
import pytest
from core.echo import Echo, echo_startup_display, echo_full_display, echo_greeting


class TestEchoIdentity:
    """Test Echo identity system."""
    
    def test_echo_has_full_art(self):
        """Test that Echo has full ASCII art."""
        art = Echo.get_full_art()
        assert art is not None
        assert len(art) > 0
        assert "✨" in art
        assert "ECHO" in art
        assert "🌙" in art
        assert "floating" in art
    
    def test_echo_has_startup_art(self):
        """Test that Echo has startup art."""
        art = Echo.get_startup_art()
        assert art is not None
        assert len(art) > 0
        assert "🌙" in art
        assert "Echo is here" in art
        assert "I'm here. 💜" in art
        assert "floating beside you" in art
    
    def test_echo_has_compact_greeting(self):
        """Test that Echo has compact greeting."""
        greeting = Echo.get_compact_greeting()
        assert greeting is not None
        assert len(greeting) > 0
        assert "Echo" in greeting
        assert "🌙" in greeting
        assert "✨" in greeting
    
    def test_echo_philosophy(self):
        """Test Echo's philosophy structure."""
        philosophy = Echo.get_philosophy()
        assert philosophy is not None
        assert philosophy["nature"] == "angel"
        assert philosophy["position"] == "floating"
        assert philosophy["where"] == "beside you (not above)"
        assert philosophy["wings"]["purpose"] == "shelter (not escape)"
        assert philosophy["symbol"] == "🌙"
        assert len(philosophy["presence"]) > 0
    
    def test_echo_startup_display_function(self):
        """Test echo_startup_display helper function."""
        art = echo_startup_display()
        assert art == Echo.get_startup_art()
        assert "Echo is here" in art
    
    def test_echo_full_display_function(self):
        """Test echo_full_display helper function."""
        art = echo_full_display()
        assert art == Echo.get_full_art()
        assert "ECHO" in art
    
    def test_echo_greeting_function(self):
        """Test echo_greeting helper function."""
        greeting = echo_greeting()
        assert greeting == Echo.get_compact_greeting()
        assert "Echo" in greeting
    
    def test_echo_art_contains_angel_elements(self):
        """Test that Echo's art contains angel-like elements."""
        full_art = Echo.get_full_art()
        # Check for wings represented by diagonal lines
        assert "╱" in full_art or "/" in full_art
        # Check for presence indicators
        assert "░" in full_art  # Wings/aura representation
        # Check for face elements
        assert "◯" in full_art  # Head
        assert "‿" in full_art  # Smile
