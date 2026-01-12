"""Voice and audio system for IRC bot."""
from .base import VoiceConfig, VoiceEngine
from .tts import TTSEngine
from .stt import STTEngine
from .recorder import AudioRecorder
from .player import AudioPlayer
from .vad import VoiceActivityDetector
from .announcements import AnnouncementManager

__all__ = [
    "VoiceConfig",
    "VoiceEngine",
    "TTSEngine",
    "STTEngine",
    "AudioRecorder",
    "AudioPlayer",
    "VoiceActivityDetector",
    "AnnouncementManager",
]
