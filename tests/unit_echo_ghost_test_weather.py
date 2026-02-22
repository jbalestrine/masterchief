"""Tests for ghost weather system."""
import pytest
from echo.ghost.weather import GhostWeather, SystemWeather, WeatherHistory


def test_ghost_weather_initialization():
    """Test ghost weather initialization."""
    weather = GhostWeather()
    
    assert weather.current == SystemWeather.CLEAR
    assert len(weather.history) == 0


def test_sense_clear_weather():
    """Test sensing clear weather."""
    weather = GhostWeather()
    
    metrics = {
        "error_rate": 0.0,
        "user_idle_time": 0.0,
        "consecutive_failures": 0,
        "recent_success": False,
    }
    
    result = weather.sense(metrics)
    
    assert result == SystemWeather.CLEAR
    assert weather.current == SystemWeather.CLEAR


def test_sense_lightning_weather():
    """Test sensing lightning weather (breakthrough)."""
    weather = GhostWeather()
    
    metrics = {
        "error_rate": 0.05,
        "recent_success": True,
    }
    
    result = weather.sense(metrics)
    
    assert result == SystemWeather.LIGHTNING
    assert weather.current == SystemWeather.LIGHTNING


def test_sense_stormy_weather():
    """Test sensing stormy weather."""
    weather = GhostWeather()
    
    metrics = {
        "error_rate": 0.6,
        "consecutive_failures": 6,
    }
    
    result = weather.sense(metrics)
    
    assert result == SystemWeather.STORMY
    assert weather.current == SystemWeather.STORMY


def test_sense_rainy_weather():
    """Test sensing rainy weather."""
    weather = GhostWeather()
    
    metrics = {
        "error_rate": 0.3,
        "consecutive_failures": 2,
    }
    
    result = weather.sense(metrics)
    
    assert result == SystemWeather.RAINY
    assert weather.current == SystemWeather.RAINY


def test_sense_foggy_weather():
    """Test sensing foggy weather."""
    weather = GhostWeather()
    
    metrics = {
        "user_idle_time": 15.0,
        "error_rate": 0.0,
    }
    
    result = weather.sense(metrics)
    
    assert result == SystemWeather.FOGGY
    assert weather.current == SystemWeather.FOGGY


def test_sense_snow_weather():
    """Test sensing snow weather (quiet)."""
    weather = GhostWeather()
    
    metrics = {
        "user_idle_time": 35.0,
        "error_rate": 0.0,
    }
    
    result = weather.sense(metrics)
    
    assert result == SystemWeather.SNOW
    assert weather.current == SystemWeather.SNOW


def test_sense_cloudy_weather():
    """Test sensing cloudy weather."""
    weather = GhostWeather()
    
    metrics = {
        "error_rate": 0.15,
        "consecutive_failures": 1,
    }
    
    result = weather.sense(metrics)
    
    assert result == SystemWeather.CLOUDY
    assert weather.current == SystemWeather.CLOUDY


def test_get_echo_response():
    """Test getting Echo's weather response."""
    weather = GhostWeather()
    
    weather.current = SystemWeather.CLEAR
    response = weather.get_echo_response()
    assert "calm" in response.lower() or "here" in response.lower()
    
    weather.current = SystemWeather.LIGHTNING
    response = weather.get_echo_response()
    assert "⚡" in response or "brilliant" in response.lower()
    
    weather.current = SystemWeather.STORMY
    response = weather.get_echo_response()
    assert "storm" in response.lower()


def test_weather_history_tracking():
    """Test weather history is tracked."""
    weather = GhostWeather()
    
    metrics1 = {"error_rate": 0.0}
    weather.sense(metrics1)
    
    assert len(weather.history) == 1
    assert weather.history[0].weather == SystemWeather.CLEAR
    
    metrics2 = {"error_rate": 0.6, "consecutive_failures": 6}
    weather.sense(metrics2)
    
    assert len(weather.history) == 2
    assert weather.history[1].weather == SystemWeather.STORMY


def test_get_weather_history():
    """Test getting weather history."""
    weather = GhostWeather()
    
    for i in range(5):
        weather.sense({"error_rate": 0.0})
        
    history = weather.get_weather_history(3)
    
    assert len(history) == 3
    assert all(isinstance(h, WeatherHistory) for h in history)


def test_weather_history_limit():
    """Test weather history is limited to 100 entries."""
    weather = GhostWeather()
    
    for i in range(150):
        weather.sense({"error_rate": 0.0})
        
    assert len(weather.history) == 100


def test_get_weather_trend_stable():
    """Test stable weather trend."""
    weather = GhostWeather()
    
    for i in range(3):
        weather.sense({"error_rate": 0.0})
        
    trend = weather.get_weather_trend()
    assert trend == "stable"


def test_get_weather_trend_worsening():
    """Test worsening weather trend."""
    weather = GhostWeather()
    
    weather.sense({"error_rate": 0.0})
    weather.sense({"error_rate": 0.15})
    weather.sense({"error_rate": 0.3})
    
    trend = weather.get_weather_trend()
    assert trend == "worsening"


def test_get_weather_trend_improving():
    """Test improving weather trend."""
    weather = GhostWeather()
    
    weather.sense({"error_rate": 0.6, "consecutive_failures": 6})
    weather.sense({"error_rate": 0.3})
    weather.sense({"error_rate": 0.0})
    
    trend = weather.get_weather_trend()
    assert trend == "improving"


def test_ghost_weather_repr():
    """Test string representation."""
    weather = GhostWeather()
    weather.sense({"error_rate": 0.0})
    
    repr_str = repr(weather)
    
    assert "GhostWeather" in repr_str
    assert "clear" in repr_str


def test_all_weather_values():
    """Test all weather enum values."""
    assert SystemWeather.CLEAR.value == "clear"
    assert SystemWeather.CLOUDY.value == "cloudy"
    assert SystemWeather.FOGGY.value == "foggy"
    assert SystemWeather.RAINY.value == "rainy"
    assert SystemWeather.STORMY.value == "stormy"
    assert SystemWeather.LIGHTNING.value == "lightning"
    assert SystemWeather.SNOW.value == "snow"
    assert SystemWeather.AURORA.value == "aurora"
