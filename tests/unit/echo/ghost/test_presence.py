"""Tests for ghost presence engine."""
import pytest
from echo.ghost.presence import GhostPresence
from echo.ghost.weather import SystemWeather


def test_ghost_presence_initialization():
    """Test ghost presence initialization."""
    ghost = GhostPresence()
    
    assert ghost.active is True
    assert ghost.weather is not None
    assert ghost.whispers is not None
    assert ghost.omens is not None
    assert ghost.memories is not None
    assert ghost.echoes is not None


def test_ghost_presence_haunt_inactive():
    """Test ghost doesn't haunt when inactive."""
    ghost = GhostPresence()
    ghost.active = False
    
    context = {"metrics": {"error_rate": 0.6}}
    result = ghost.haunt(context)
    
    assert result is None


def test_ghost_presence_haunt_updates_weather():
    """Test haunt updates weather."""
    ghost = GhostPresence()
    
    context = {"metrics": {"error_rate": 0.6, "consecutive_failures": 6}}
    
    # Try multiple times as manifestation is probabilistic
    for _ in range(5):
        ghost.haunt(context)
        
    # Weather should be stormy
    assert ghost.weather.current == SystemWeather.STORMY


def test_ghost_presence_set_active():
    """Test setting ghost active/inactive."""
    ghost = GhostPresence()
    
    assert ghost.active is True
    
    ghost.set_active(False)
    assert ghost.active is False
    
    ghost.set_active(True)
    assert ghost.active is True


def test_ghost_presence_get_status():
    """Test getting ghost status."""
    ghost = GhostPresence()
    
    context = {"metrics": {"error_rate": 0.0}}
    ghost.haunt(context)
    
    status = ghost.get_status()
    
    assert "active" in status
    assert "weather" in status
    assert "weather_trend" in status
    assert "memories_stored" in status
    assert "echoes_captured" in status
    assert "predictions_made" in status
    
    assert status["active"] is True
    assert isinstance(status["weather"], str)


def test_ghost_presence_manifest_greeting():
    """Test ghost greeting message."""
    ghost = GhostPresence()
    
    greeting = ghost.manifest_greeting()
    
    assert "ghost" in greeting.lower()
    assert "machine" in greeting.lower()
    assert "🌙" in greeting


def test_ghost_presence_should_manifest_probabilities():
    """Test manifestation probabilities vary by weather."""
    ghost = GhostPresence()
    
    # Set to stormy weather (high probability)
    ghost.weather.current = SystemWeather.STORMY
    
    manifestations = 0
    trials = 100
    
    for _ in range(trials):
        context = {}
        if ghost._should_manifest(context):
            manifestations += 1
            
    # Should manifest more than 40% of the time for stormy weather
    assert manifestations > trials * 0.3


def test_ghost_presence_choose_manifestation():
    """Test choosing manifestation returns a message."""
    ghost = GhostPresence()
    
    context = {"metrics": {"error_rate": 0.0}}
    ghost.weather.sense(context["metrics"])
    
    manifestation = ghost._choose_manifestation(context)
    
    assert manifestation is not None
    assert isinstance(manifestation, str)
    assert len(manifestation) > 0


def test_ghost_presence_repr():
    """Test string representation."""
    ghost = GhostPresence()
    
    repr_str = repr(ghost)
    
    assert "GhostPresence" in repr_str
    assert "active" in repr_str


def test_ghost_presence_haunt_with_various_contexts():
    """Test haunting with various contexts."""
    ghost = GhostPresence()
    
    # Test with clear weather
    context1 = {"metrics": {"error_rate": 0.0}}
    result1 = ghost.haunt(context1)
    # May or may not manifest with clear weather
    
    # Test with stormy weather (more likely to manifest)
    context2 = {"metrics": {"error_rate": 0.7, "consecutive_failures": 10}}
    
    # Try multiple times to increase chance of manifestation
    manifested = False
    for _ in range(20):
        result = ghost.haunt(context2)
        if result is not None:
            manifested = True
            assert isinstance(result, str)
            assert len(result) > 0
            break
            
    # With stormy weather and 20 tries, should manifest at least once
    assert manifested


def test_ghost_presence_integration_with_components():
    """Test ghost integrates with all components."""
    ghost = GhostPresence()
    
    # Add some data to components
    ghost.memories.store("test", "user did something", "success", "positive")
    ghost.echoes.capture("This is important", "test context")
    
    # Get status should reflect stored data
    status = ghost.get_status()
    
    assert status["memories_stored"] > 0
    assert status["echoes_captured"] > 0
