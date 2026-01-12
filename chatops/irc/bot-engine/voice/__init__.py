"""Voice system for MasterChief IRC Bot.

This module provides Text-to-Speech (TTS), Speech-to-Text (STT),
audio recording, playback, and voice cloning capabilities.
"""
from .base import VoiceConfig, VoiceCloningConfig

__all__ = ["VoiceConfig", "VoiceCloningConfig"]
