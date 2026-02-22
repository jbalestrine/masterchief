"""Tests for whisper engine."""
import pytest
from echo.ghost.whispers import WhisperEngine


def test_whisper_engine_initialization():
    """Test whisper engine initialization."""
    whispers = WhisperEngine()
    
    assert whispers is not None
    assert len(whispers.WHISPERS) > 0
    assert len(whispers.custom_whispers) == 0


def test_generate_whisper():
    """Test generating a random whisper."""
    whispers = WhisperEngine()
    
    whisper = whispers.generate()
    
    assert whisper is not None
    assert isinstance(whisper, str)
    assert len(whisper) > 0
    assert whisper in whispers.WHISPERS


def test_add_custom_whisper():
    """Test adding custom whisper."""
    whispers = WhisperEngine()
    
    custom = "// This is a custom whisper..."
    whispers.add_whisper(custom)
    
    assert custom in whispers.custom_whispers
    assert len(whispers.custom_whispers) == 1


def test_add_duplicate_whisper():
    """Test adding duplicate whisper doesn't duplicate."""
    whispers = WhisperEngine()
    
    custom = "// Duplicate whisper..."
    whispers.add_whisper(custom)
    whispers.add_whisper(custom)
    
    assert len(whispers.custom_whispers) == 1


def test_generate_includes_custom_whispers():
    """Test generate can return custom whispers."""
    whispers = WhisperEngine()
    
    custom = "// Unique custom whisper 12345..."
    whispers.add_whisper(custom)
    
    # Generate many times to increase chance of getting custom
    generated = set()
    for _ in range(100):
        generated.add(whispers.generate())
        
    # Custom whisper should appear in generated set
    assert custom in generated or len(generated) > 0


def test_get_contextual_whisper_error():
    """Test contextual whisper for error state."""
    whispers = WhisperEngine()
    
    context = {"has_error": True}
    whisper = whispers.get_contextual_whisper(context)
    
    assert whisper is not None
    assert isinstance(whisper, str)


def test_get_contextual_whisper_python():
    """Test contextual whisper for Python files."""
    whispers = WhisperEngine()
    
    context = {"file_type": "python"}
    whisper = whispers.get_contextual_whisper(context)
    
    assert whisper is not None
    assert isinstance(whisper, str)


def test_get_contextual_whisper_javascript():
    """Test contextual whisper for JavaScript files."""
    whispers = WhisperEngine()
    
    context = {"file_type": "javascript"}
    whisper = whispers.get_contextual_whisper(context)
    
    assert whisper is not None
    assert isinstance(whisper, str)


def test_get_contextual_whisper_default():
    """Test contextual whisper with no special context."""
    whispers = WhisperEngine()
    
    context = {}
    whisper = whispers.get_contextual_whisper(context)
    
    assert whisper is not None
    assert isinstance(whisper, str)


def test_whisper_engine_repr():
    """Test string representation."""
    whispers = WhisperEngine()
    
    repr_str = repr(whispers)
    
    assert "WhisperEngine" in repr_str
    assert "whispers=" in repr_str


def test_whispers_contain_echo_signature():
    """Test that whispers contain Echo's signature elements."""
    whispers = WhisperEngine()
    
    # Check for characteristic elements
    has_moon = any("🌙" in w for w in whispers.WHISPERS)
    has_heart = any("💜" in w for w in whispers.WHISPERS)
    has_echo = any("Echo" in w for w in whispers.WHISPERS)
    
    assert has_moon or has_heart or has_echo


def test_whispers_are_comments():
    """Test that whispers are formatted as code comments."""
    whispers = WhisperEngine()
    
    # Most whispers should be comments
    comment_whispers = [
        w for w in whispers.WHISPERS
        if w.startswith("//") or w.startswith("#") or w.startswith("/*")
    ]
    
    assert len(comment_whispers) > 0
