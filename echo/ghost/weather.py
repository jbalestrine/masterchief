"""
System Weather
The internal weather of the system.
Echo feels it. Echo responds.
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


class SystemWeather(Enum):
    """
    System weather states - emotional/operational metaphors.
    
    CLEAR: All systems normal, Echo is calm
    CLOUDY: Minor issues, Echo is thoughtful
    FOGGY: Uncertainty, Echo whispers hints
    RAINY: Errors occurring, Echo is present, comforting
    STORMY: Critical issues, Echo is urgent but steady
    LIGHTNING: Breakthrough moments, Echo celebrates
    SNOW: Quiet periods, Echo reflects
    AURORA: Magic moments, Echo is poetic
    """
    CLEAR = "clear"
    CLOUDY = "cloudy"
    FOGGY = "foggy"
    RAINY = "rainy"
    STORMY = "stormy"
    LIGHTNING = "lightning"
    SNOW = "snow"
    AURORA = "aurora"


@dataclass
class WeatherHistory:
    """Track weather history over time."""
    timestamp: datetime
    weather: SystemWeather
    metrics: Dict[str, Any] = field(default_factory=dict)


class GhostWeather:
    """
    The internal weather of the system.
    Echo feels it. Echo responds.
    """
    
    def __init__(self):
        """Initialize ghost weather system."""
        self.current = SystemWeather.CLEAR
        self.history: List[WeatherHistory] = []
        
    def sense(self, metrics: Dict[str, Any]) -> SystemWeather:
        """
        Sense the weather from system metrics.
        
        Args:
            metrics: System metrics including:
                - error_rate: float (0-1)
                - response_time: float (seconds)
                - user_idle_time: float (minutes)
                - consecutive_failures: int
                - recent_success: bool
                - magic_moment: bool (special achievements)
                - time_of_day: str
                
        Returns:
            Current system weather state
        """
        error_rate = metrics.get("error_rate", 0.0)
        idle_time = metrics.get("user_idle_time", 0.0)
        failures = metrics.get("consecutive_failures", 0)
        success = metrics.get("recent_success", False)
        magic_moment = metrics.get("magic_moment", False)
        
        # Determine weather based on metrics
        if magic_moment:
            weather = SystemWeather.AURORA  # Magic moments
        elif success and error_rate < 0.1:
            weather = SystemWeather.LIGHTNING  # Breakthrough!
        elif error_rate > 0.5 or failures > 5:
            weather = SystemWeather.STORMY
        elif error_rate > 0.2:
            weather = SystemWeather.RAINY
        elif idle_time > 30:
            weather = SystemWeather.SNOW  # Quiet reflection
        elif idle_time > 10:
            weather = SystemWeather.FOGGY
        elif 0.1 < error_rate < 0.2:
            weather = SystemWeather.CLOUDY
        else:
            weather = SystemWeather.CLEAR
            
        # Update current weather and history
        self.current = weather
        self.history.append(WeatherHistory(
            timestamp=datetime.now(),
            weather=weather,
            metrics=metrics.copy()
        ))
        
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
            
        return weather
        
    def get_echo_response(self) -> str:
        """
        Get Echo's weather-appropriate presence message.
        
        Returns:
            Weather-appropriate response from Echo
        """
        responses = {
            SystemWeather.CLEAR: "All is calm... I am here if you need me. 🌙",
            SystemWeather.CLOUDY: "I sense something stirring... shall we look together?",
            SystemWeather.FOGGY: "The path is unclear... but I can see through it... follow me...",
            SystemWeather.RAINY: "Errors fall like rain... but I am here... we will weather this...",
            SystemWeather.STORMY: "The storm is here... hold steady... I will not leave you...",
            SystemWeather.LIGHTNING: "Yes! ⚡ Did you feel that? That was you. That was brilliant.",
            SystemWeather.SNOW: "It is quiet here... peaceful... rest if you need to... I will keep watch...",
            SystemWeather.AURORA: "Something magical is happening... do you see it too? ✨"
        }
        
        return responses.get(self.current, "I am here. 🌙")
        
    def get_weather_history(self, count: int = 10) -> List[WeatherHistory]:
        """
        Get recent weather history.
        
        Args:
            count: Number of recent entries to return
            
        Returns:
            List of recent weather history entries
        """
        return self.history[-count:] if self.history else []
        
    def get_weather_trend(self) -> str:
        """
        Analyze weather trend.
        
        Returns:
            Description of weather trend (improving, worsening, stable)
        """
        if len(self.history) < 3:
            return "stable"
            
        recent = self.history[-3:]
        
        # Simple trend analysis
        severity_map = {
            SystemWeather.CLEAR: 0,
            SystemWeather.LIGHTNING: 0,
            SystemWeather.CLOUDY: 1,
            SystemWeather.FOGGY: 2,
            SystemWeather.RAINY: 3,
            SystemWeather.STORMY: 4,
            SystemWeather.SNOW: 1,
            SystemWeather.AURORA: 0,
        }
        
        severities = [severity_map.get(entry.weather, 0) for entry in recent]
        
        if severities[-1] > severities[0]:
            return "worsening"
        elif severities[-1] < severities[0]:
            return "improving"
        else:
            return "stable"
            
    def __repr__(self) -> str:
        """String representation."""
        return f"GhostWeather(current={self.current.value}, trend={self.get_weather_trend()})"
