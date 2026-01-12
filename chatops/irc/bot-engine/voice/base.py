"""Base voice engine for TTS, STT, and audio processing."""

import logging
from dataclasses import dataclass
from typing import Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VoiceConfig:
    """Configuration for voice engine."""
    
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    device_index: Optional[int] = None
    
    # TTS settings
    tts_engine: str = "pyttsx3"  # pyttsx3, espeak, etc.
    tts_voice: Optional[str] = None
    tts_rate: int = 150
    tts_volume: float = 1.0
    
    # STT settings
    stt_engine: str = "whisper"  # whisper, vosk, etc.
    stt_model: str = "base"
    stt_language: str = "en"
    
    # Audio settings
    vad_enabled: bool = True
    silence_threshold: float = 0.01
    silence_duration: float = 1.0


class VoiceEngine:
    """Main voice engine coordinating TTS, STT, and audio I/O."""
    
    def __init__(self, config: VoiceConfig):
        """Initialize voice engine."""
        self.config = config
        self._initialized = False
        
        # Lazy imports to avoid hard dependencies
        self.tts = None
        self.stt = None
        self.recorder = None
        self.player = None
        self.vad = None
        
        logger.info("VoiceEngine initialized")
    
    def initialize(self):
        """Initialize all voice components."""
        if self._initialized:
            return
            
        try:
            from .tts import TTSEngine
            from .stt import STTEngine
            from .recorder import AudioRecorder
            from .player import AudioPlayer
            from .vad import VAD
            
            self.tts = TTSEngine(self.config)
            self.stt = STTEngine(self.config)
            self.recorder = AudioRecorder(self.config)
            self.player = AudioPlayer(self.config)
            self.vad = VAD(self.config)
            
            self._initialized = True
            logger.info("VoiceEngine components initialized")
        except ImportError as e:
            logger.error(f"Failed to initialize voice components: {e}")
            raise
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            blocking: Wait for speech to complete
            
        Returns:
            True if successful
        """
        if not self._initialized:
            self.initialize()
            
        try:
            audio_data = self.tts.synthesize(text)
            self.player.play(audio_data, blocking=blocking)
            return True
        except Exception as e:
            logger.error(f"Failed to speak: {e}")
            return False
    
    def listen(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Record audio until silence or timeout.
        
        Args:
            timeout: Maximum recording time in seconds
            
        Returns:
            Audio data as bytes or None
        """
        if not self._initialized:
            self.initialize()
            
        try:
            return self.recorder.record(timeout=timeout, use_vad=self.config.vad_enabled)
        except Exception as e:
            logger.error(f"Failed to record audio: {e}")
            return None
    
    def transcribe(self, audio_data: bytes) -> str:
        """
        Convert speech to text.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        if not self._initialized:
            self.initialize()
            
        try:
            return self.stt.transcribe(audio_data)
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return ""
    
    def stop_speaking(self):
        """Stop current speech output."""
        if self.player:
            self.player.stop()
    
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        if self.player:
            return self.player.is_playing()
        return False
