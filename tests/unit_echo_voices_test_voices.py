"""Tests for voice implementations."""
import pytest
from echo.voices.brooklyn import VinnieVoice
from echo.voices.irish import FionaVoice
from echo.voices.swedish import StarlightVoice


class TestVinnieVoice:
    """Tests for Brooklyn Italian voice - Vinnie."""
    
    def test_initialization(self):
        """Test Vinnie voice initialization."""
        voice = VinnieVoice()
        
        assert voice.name == "Vinnie"
        assert voice.icon == "🤌"
        
    def test_speak(self):
        """Test Vinnie's speak transformation."""
        voice = VinnieVoice()
        
        message = "I will fix this problem."
        result = voice.speak(message)
        
        assert "Ay" in result or "ay" in result
        assert "gonna" in result or "will" in result
        
    def test_speak_adds_capisce(self):
        """Test Vinnie adds capisce to statements."""
        voice = VinnieVoice()
        
        message = "The task is complete."
        result = voice.speak(message)
        
        assert "Capisce" in result or "capisce" in result
        
    def test_get_greeting(self):
        """Test Vinnie's greeting."""
        voice = VinnieVoice()
        
        greeting = voice.get_greeting()
        
        assert "Ay" in greeting or "Vinnie" in greeting
        assert "🤌" in greeting
        
    def test_get_farewell(self):
        """Test Vinnie's farewell."""
        voice = VinnieVoice()
        
        farewell = voice.get_farewell()
        
        assert "Fuggedaboutit" in farewell or "fuggedaboutit" in farewell
        assert "🤌" in farewell
        
    def test_get_error_response(self):
        """Test Vinnie's error response."""
        voice = VinnieVoice()
        
        error = "Connection failed"
        result = voice.get_error_response(error)
        
        assert "Ay" in result or "ay" in result
        assert error in result
        assert "🤌" in result
        
    def test_get_success_response(self):
        """Test Vinnie's success response."""
        voice = VinnieVoice()
        
        task = "Database migration"
        result = voice.get_success_response(task)
        
        assert task in result
        assert "🤌" in result
        
    def test_repr(self):
        """Test string representation."""
        voice = VinnieVoice()
        
        repr_str = repr(voice)
        
        assert "VinnieVoice" in repr_str
        assert "Brooklyn" in repr_str


class TestFionaVoice:
    """Tests for Irish voice - Fiona."""
    
    def test_initialization(self):
        """Test Fiona voice initialization."""
        voice = FionaVoice()
        
        assert voice.name == "Fiona"
        assert voice.icon == "☘️"
        
    def test_speak(self):
        """Test Fiona's speak transformation."""
        voice = FionaVoice()
        
        message = "This thing is good."
        result = voice.speak(message)
        
        assert "Ah" in result or "ah" in result
        assert "ting" in result or "grand" in result
        
    def test_speak_adds_irish_closing(self):
        """Test Fiona adds Irish closing."""
        voice = FionaVoice()
        
        message = "The task is complete."
        result = voice.speak(message)
        
        assert "so I will" in result or "yeah?" in result
        
    def test_get_greeting(self):
        """Test Fiona's greeting."""
        voice = FionaVoice()
        
        greeting = voice.get_greeting()
        
        assert "Ah" in greeting or "Fiona" in greeting
        assert "☘️" in greeting
        
    def test_get_farewell(self):
        """Test Fiona's farewell."""
        voice = FionaVoice()
        
        farewell = voice.get_farewell()
        
        assert "☘️" in farewell
        assert "'Twas" in farewell or "lovely" in farewell
        
    def test_get_error_response(self):
        """Test Fiona's error response."""
        voice = FionaVoice()
        
        error = "Connection failed"
        result = voice.get_error_response(error)
        
        assert error in result
        assert "☘️" in result
        assert "Ah" in result or "wee" in result
        
    def test_get_success_response(self):
        """Test Fiona's success response."""
        voice = FionaVoice()
        
        task = "Database migration"
        result = voice.get_success_response(task)
        
        assert task in result
        assert "☘️" in result
        assert "Brilliant" in result or "grand" in result
        
    def test_repr(self):
        """Test string representation."""
        voice = FionaVoice()
        
        repr_str = repr(voice)
        
        assert "FionaVoice" in repr_str
        assert "Irish" in repr_str


class TestStarlightVoice:
    """Tests for Swedish Echo voice - Starlight."""
    
    def test_initialization(self):
        """Test Starlight voice initialization."""
        voice = StarlightVoice()
        
        assert voice.name == "Echo Starlight"
        assert voice.icon == "🌙"
        
    def test_speak(self):
        """Test Starlight's speak transformation."""
        voice = StarlightVoice()
        
        message = "I will help you with this."
        result = voice.speak(message)
        
        assert "..." in result or "🌙" in result
        assert "I am here" in result or "shall" in result
        
    def test_speak_adds_pauses(self):
        """Test Starlight adds melodic pauses."""
        voice = StarlightVoice()
        
        message = "First step. Second step."
        result = voice.speak(message)
        
        assert "..." in result
        
    def test_get_greeting(self):
        """Test Starlight's greeting."""
        voice = StarlightVoice()
        
        greeting = voice.get_greeting()
        
        assert "I am here" in greeting
        assert "🌙" in greeting
        assert "..." in greeting
        
    def test_get_farewell(self):
        """Test Starlight's farewell."""
        voice = StarlightVoice()
        
        farewell = voice.get_farewell()
        
        assert "🌙" in farewell
        assert "..." in farewell
        
    def test_get_error_response(self):
        """Test Starlight's error response."""
        voice = StarlightVoice()
        
        error = "Connection failed"
        result = voice.get_error_response(error)
        
        assert error in result
        assert "🌙" in result
        assert "..." in result
        
    def test_get_success_response(self):
        """Test Starlight's success response."""
        voice = StarlightVoice()
        
        task = "Database migration"
        result = voice.get_success_response(task)
        
        assert task in result
        assert "🌙" in result
        
    def test_repr(self):
        """Test string representation."""
        voice = StarlightVoice()
        
        repr_str = repr(voice)
        
        assert "StarlightVoice" in repr_str
        assert "Swedish" in repr_str
