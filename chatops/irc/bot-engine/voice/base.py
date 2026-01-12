"""Base classes and configuration for voice system."""
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TTSConfig:
    """Text-to-speech configuration."""
    enabled: bool = True
    engine: str = "pyttsx3"
    voice: Optional[str] = None  # Specific voice ID or None for default
    rate: int = 150  # Words per minute
    volume: float = 1.0  # 0.0 to 1.0
    save_to_file: bool = False
    output_dir: str = "./voice_output"


@dataclass
class STTConfig:
    """Speech-to-text configuration."""
    enabled: bool = True
    engine: str = "whisper"
    model: str = "base"  # tiny, base, small, medium, large
    language: str = "en"
    device: str = "cpu"  # cpu or cuda


@dataclass
class RecorderConfig:
    """Audio recorder configuration."""
    enabled: bool = True
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"  # wav, mp3, ogg
    vad_enabled: bool = True
    vad_aggressiveness: int = 2  # 0-3, higher = more aggressive
    silence_duration: float = 1.5  # Seconds of silence to stop recording


@dataclass
class PlayerConfig:
    """Audio player configuration."""
    enabled: bool = True
    volume: float = 0.8  # 0.0 to 1.0
    supported_formats: list = field(default_factory=lambda: ["wav", "mp3", "ogg"])


@dataclass
class AnnouncementConfig:
    """Announcement configuration."""
    enabled: bool = True
    directory: str = "./sounds"
    events: Dict[str, str] = field(default_factory=dict)


@dataclass
class VoiceConfig:
    """Main voice system configuration."""
    enabled: bool = True
    tts: TTSConfig = field(default_factory=TTSConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    recorder: RecorderConfig = field(default_factory=RecorderConfig)
    player: PlayerConfig = field(default_factory=PlayerConfig)
    announcements: AnnouncementConfig = field(default_factory=AnnouncementConfig)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "VoiceConfig":
        """Create VoiceConfig from dictionary."""
        return cls(
            enabled=config_dict.get("enabled", True),
            tts=TTSConfig(**config_dict.get("tts", {})),
            stt=STTConfig(**config_dict.get("stt", {})),
            recorder=RecorderConfig(**config_dict.get("recorder", {})),
            player=PlayerConfig(**config_dict.get("player", {})),
            announcements=AnnouncementConfig(**config_dict.get("announcements", {})),
        )


class VoiceEngine:
    """Main voice engine that coordinates all voice components."""

    def __init__(self, config: Optional[VoiceConfig] = None):
        """Initialize voice engine with configuration."""
        self.config = config or VoiceConfig()
        self._tts_engine = None
        self._stt_engine = None
        self._recorder = None
        self._player = None
        self._announcement_manager = None
        self._initialized = False
        
        logger.info("VoiceEngine initialized with config")

    def initialize(self):
        """Initialize all voice components lazily."""
        if self._initialized:
            return

        try:
            # Import and initialize components only when needed
            if self.config.tts.enabled:
                from .tts import TTSEngine
                self._tts_engine = TTSEngine(self.config.tts)
                logger.info("TTS engine initialized")

            if self.config.stt.enabled:
                from .stt import STTEngine
                self._stt_engine = STTEngine(self.config.stt)
                logger.info("STT engine initialized")

            if self.config.recorder.enabled:
                from .recorder import AudioRecorder
                self._recorder = AudioRecorder(self.config.recorder)
                logger.info("Audio recorder initialized")

            if self.config.player.enabled:
                from .player import AudioPlayer
                self._player = AudioPlayer(self.config.player)
                logger.info("Audio player initialized")

            if self.config.announcements.enabled:
                from .announcements import AnnouncementManager
                self._announcement_manager = AnnouncementManager(
                    self.config.announcements, self._player
                )
                logger.info("Announcement manager initialized")

            self._initialized = True
            logger.info("VoiceEngine fully initialized")

        except Exception as e:
            logger.error(f"Error initializing voice engine: {e}")
            raise

    def speak(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            save_to_file: Optional filename to save audio
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self.config.tts.enabled:
            logger.warning("TTS is disabled")
            return False

        try:
            if not self._initialized:
                self.initialize()

            if self._tts_engine:
                return self._tts_engine.speak(text, save_to_file)
            return False

        except Exception as e:
            logger.error(f"Error in speak: {e}")
            return False

    def listen(self, duration: Optional[int] = None) -> Optional[str]:
        """
        Record audio and transcribe to text.
        
        Args:
            duration: Recording duration in seconds (None for VAD-based)
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.config.enabled or not self.config.stt.enabled:
            logger.warning("STT is disabled")
            return None

        try:
            if not self._initialized:
                self.initialize()

            # Record audio
            if self._recorder:
                audio_file = self._recorder.record(duration)
                if audio_file and self._stt_engine:
                    return self._stt_engine.transcribe_file(audio_file)

            return None

        except Exception as e:
            logger.error(f"Error in listen: {e}")
            return None

    def record(self, filename: str, duration: int) -> bool:
        """
        Record audio to a file.
        
        Args:
            filename: Output filename
            duration: Recording duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self.config.recorder.enabled:
            logger.warning("Recorder is disabled")
            return False

        try:
            if not self._initialized:
                self.initialize()

            if self._recorder:
                result = self._recorder.record(duration, filename)
                return result is not None

            return False

        except Exception as e:
            logger.error(f"Error in record: {e}")
            return False

    def play(self, filename: str) -> bool:
        """
        Play an audio file.
        
        Args:
            filename: Audio file to play
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self.config.player.enabled:
            logger.warning("Player is disabled")
            return False

        try:
            if not self._initialized:
                self.initialize()

            if self._player:
                return self._player.play(filename)

            return False

        except Exception as e:
            logger.error(f"Error in play: {e}")
            return False

    def announce(self, event: str) -> bool:
        """
        Play announcement for an event.
        
        Args:
            event: Event name (e.g., 'deploy_success', 'alert_critical')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self.config.announcements.enabled:
            logger.warning("Announcements are disabled")
            return False

        try:
            if not self._initialized:
                self.initialize()

            if self._announcement_manager:
                return self._announcement_manager.announce(event)

            return False

        except Exception as e:
            logger.error(f"Error in announce: {e}")
            return False

    def shutdown(self):
        """Clean up resources."""
        logger.info("Shutting down voice engine")
        
        if self._tts_engine:
            try:
                self._tts_engine.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down TTS: {e}")

        if self._player:
            try:
                self._player.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down player: {e}")

        self._initialized = False
