"""
Ghost in the Machine
Weather-driven, modular, unexpected presence.
"""

from echo.ghost.weather import GhostWeather, SystemWeather
from echo.ghost.presence import GhostPresence
from echo.ghost.whispers import WhisperEngine
from echo.ghost.omens import OmenEngine
from echo.ghost.memories import MemoryEngine
from echo.ghost.echoes import EchoEngine

__all__ = [
    'GhostWeather',
    'SystemWeather',
    'GhostPresence',
    'WhisperEngine',
    'OmenEngine',
    'MemoryEngine',
    'EchoEngine',
]
