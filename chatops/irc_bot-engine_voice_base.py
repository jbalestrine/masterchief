"""Base voice engine for TTS, STT, and audio processing."""

import logging
from dataclasses import dataclass
from typing import Optional, Any
"""Base configuration classes for voice system."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class VoiceConfig:
    """Base voice system configuration."""
    enabled: bool = True
    sample_rate: int = 22050
    device: str = "auto"  # cuda, cpu, or auto
    output_dir: str = "./voice_output/"


@dataclass
class VoiceCloningConfig:
    """Configuration for voice cloning system."""
    enabled: bool = True
    profiles_dir: str = "./voice_profiles/"
    samples_dir: str = "./voice_samples/"
    device: str = "auto"  # cuda, cpu, or auto
    engine: str = "xtts"  # xtts, tortoise, or openvoice
    
    # XTTS specific settings
    xtts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    # Tortoise specific settings
    tortoise_model: str = "tortoise-tts"
    tortoise_preset: str = "fast"  # ultra_fast, fast, standard, high_quality
    
    # OpenVoice specific settings
    openvoice_model: str = "openvoice"
    
    # Master voice settings
    master_voice_name: Optional[str] = None
    
    # Additional settings
    metadata: Dict[str, Any] = field(default_factory=dict)
"""Base classes and configuration for voice system."""
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
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
