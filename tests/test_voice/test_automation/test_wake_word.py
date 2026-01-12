"""Test wake word detection."""

import pytest
from chatops.irc.bot_engine.voice.automation.wake_word import WakeWordDetector


class TestWakeWordDetector:
    """Tests for WakeWordDetector."""
    
    def test_initialization(self):
        """Test wake word detector initialization."""
        detector = WakeWordDetector(
            wake_words=["hey chief", "okay chief"],
            engine="simple",
            sensitivity=0.5
        )
        
        assert detector is not None
        assert len(detector.wake_words) == 2
        assert "hey chief" in detector.wake_words
        assert detector.sensitivity == 0.5
    
    def test_detect_in_text(self):
        """Test detecting wake word in text."""
        detector = WakeWordDetector(
            wake_words=["hey chief"],
            engine="simple"
        )
        
        # Should detect
        assert detector.detect_in_text("Hey chief, what's up?")
        assert detector.detect_in_text("hey CHIEF please help")
        
        # Should not detect
        assert not detector.detect_in_text("Hello there")
        assert not detector.detect_in_text("chief alone")
    
    def test_add_wake_word(self):
        """Test adding a wake word."""
        detector = WakeWordDetector(
            wake_words=["hey chief"],
            engine="simple"
        )
        
        detector.add_wake_word("okay chief")
        
        assert "okay chief" in detector.wake_words
        assert len(detector.wake_words) == 2
    
    def test_remove_wake_word(self):
        """Test removing a wake word."""
        detector = WakeWordDetector(
            wake_words=["hey chief", "okay chief"],
            engine="simple"
        )
        
        detector.remove_wake_word("okay chief")
        
        assert "okay chief" not in detector.wake_words
        assert len(detector.wake_words) == 1
    
    def test_case_insensitive(self):
        """Test case insensitive wake word detection."""
        detector = WakeWordDetector(
            wake_words=["Hey MasterChief"],
            engine="simple"
        )
        
        assert detector.detect_in_text("hey masterchief")
        assert detector.detect_in_text("HEY MASTERCHIEF")
        assert detector.detect_in_text("Hey Masterchief")
