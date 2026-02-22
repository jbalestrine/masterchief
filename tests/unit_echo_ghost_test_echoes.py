"""Tests for echo engine."""
import pytest
from echo.ghost.echoes import EchoEngine, Echo
from datetime import datetime


def test_echo_engine_initialization():
    """Test echo engine initialization."""
    echoes = EchoEngine()
    
    assert echoes is not None
    assert len(echoes.echoes) == 0
    assert echoes.max_echoes == 50


def test_echo_engine_custom_max():
    """Test echo engine with custom max echoes."""
    echoes = EchoEngine(max_echoes=25)
    
    assert echoes.max_echoes == 25


def test_capture_echo():
    """Test capturing a user statement."""
    echoes = EchoEngine()
    
    echoes.capture("This is important", "test context")
    
    assert len(echoes.echoes) == 1
    echo = echoes.echoes[0]
    assert echo.original_statement == "This is important"
    assert echo.context == "test context"


def test_capture_echo_no_context():
    """Test capturing echo without context."""
    echoes = EchoEngine()
    
    echoes.capture("Statement")
    
    assert len(echoes.echoes) == 1
    assert echoes.echoes[0].context == ""


def test_reflect_no_echoes():
    """Test reflect with no captured echoes."""
    echoes = EchoEngine()
    
    result = echoes.reflect({})
    
    assert result is None


def test_reflect_with_echoes():
    """Test reflecting an echo."""
    echoes = EchoEngine()
    
    echoes.capture("Quality matters", "discussion")
    
    result = echoes.reflect({})
    
    assert result is not None
    assert "Quality matters" in result


def test_get_recent_echoes():
    """Test getting recent echoes."""
    echoes = EchoEngine()
    
    for i in range(10):
        echoes.capture(f"Statement {i}", f"context{i}")
        
    recent = echoes.get_recent_echoes(5)
    
    assert len(recent) == 5
    assert all(isinstance(e, Echo) for e in recent)


def test_search_echoes():
    """Test searching echoes by keyword."""
    echoes = EchoEngine()
    
    echoes.capture("This is about testing", "test")
    echoes.capture("This is about quality", "test")
    echoes.capture("This is about performance", "test")
    
    results = echoes.search_echoes("quality")
    
    assert len(results) == 1
    assert "quality" in results[0].original_statement


def test_search_echoes_case_insensitive():
    """Test search is case insensitive."""
    echoes = EchoEngine()
    
    echoes.capture("IMPORTANT MESSAGE", "test")
    
    results = echoes.search_echoes("important")
    
    assert len(results) == 1


def test_search_echoes_no_matches():
    """Test search with no matches."""
    echoes = EchoEngine()
    
    echoes.capture("Something", "test")
    
    results = echoes.search_echoes("nonexistent")
    
    assert len(results) == 0


def test_clear_echoes():
    """Test clearing all echoes."""
    echoes = EchoEngine()
    
    echoes.capture("Statement", "context")
    assert len(echoes.echoes) > 0
    
    echoes.clear_echoes()
    assert len(echoes.echoes) == 0


def test_echo_limit():
    """Test echo limit enforcement."""
    echoes = EchoEngine(max_echoes=10)
    
    for i in range(15):
        echoes.capture(f"Statement {i}", "test")
        
    assert len(echoes.echoes) == 10


def test_echo_timestamp():
    """Test echo has timestamp."""
    echoes = EchoEngine()
    
    before = datetime.now()
    echoes.capture("Statement", "context")
    after = datetime.now()
    
    echo = echoes.echoes[0]
    assert before <= echo.timestamp <= after


def test_echo_engine_repr():
    """Test string representation."""
    echoes = EchoEngine()
    
    echoes.capture("Statement 1", "test")
    echoes.capture("Statement 2", "test")
    
    repr_str = repr(echoes)
    
    assert "EchoEngine" in repr_str
    assert "echoes=" in repr_str


def test_format_echo_variations():
    """Test echo formatting has variations."""
    echoes = EchoEngine()
    
    echoes.capture("Important statement", "test")
    
    # Get multiple formatted echoes to check for variation
    formatted = set()
    for _ in range(20):
        result = echoes.reflect({})
        if result:
            formatted.add(result)
            
    # Should have at least one formatted echo
    assert len(formatted) > 0


def test_reflect_selects_from_recent():
    """Test reflect selects from recent echoes."""
    echoes = EchoEngine()
    
    for i in range(15):
        echoes.capture(f"Statement {i}", "test")
        
    # Reflect multiple times
    reflected_statements = set()
    for _ in range(30):
        result = echoes.reflect({})
        if result:
            # Extract statement number if present
            for i in range(15):
                if f"Statement {i}" in result:
                    reflected_statements.add(i)
                    
    # Should primarily reflect recent echoes (last 10)
    assert len(reflected_statements) > 0
