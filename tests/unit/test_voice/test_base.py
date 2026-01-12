"""Unit tests for voice system base classes and configuration."""
import pytest
from chatops.irc.bot_engine.voice.base import (
    VoiceConfig,
    TTSConfig,
    STTConfig,
    RecorderConfig,
    PlayerConfig,
    AnnouncementConfig,
    VoiceEngine
)


class TestVoiceConfig:
    """Tests for VoiceConfig."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = VoiceConfig()
        assert config.enabled is True
        assert config.tts.enabled is True
        assert config.stt.enabled is True
        assert config.recorder.enabled is True
        assert config.player.enabled is True

    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "enabled": True,
            "tts": {"rate": 200, "volume": 0.5},
            "stt": {"model": "small", "language": "en"},
            "recorder": {"sample_rate": 48000},
            "player": {"volume": 0.7}
        }
        config = VoiceConfig.from_dict(config_dict)
        
        assert config.enabled is True
        assert config.tts.rate == 200
        assert config.tts.volume == 0.5
        assert config.stt.model == "small"
        assert config.recorder.sample_rate == 48000
        assert config.player.volume == 0.7


class TestTTSConfig:
    """Tests for TTSConfig."""

    def test_default_tts_config(self):
        """Test default TTS configuration."""
        config = TTSConfig()
        assert config.enabled is True
        assert config.engine == "pyttsx3"
        assert config.rate == 150
        assert config.volume == 1.0

    def test_custom_tts_config(self):
        """Test custom TTS configuration."""
        config = TTSConfig(
            rate=200,
            volume=0.8,
            voice="en-us"
        )
        assert config.rate == 200
        assert config.volume == 0.8
        assert config.voice == "en-us"


class TestSTTConfig:
    """Tests for STTConfig."""

    def test_default_stt_config(self):
        """Test default STT configuration."""
        config = STTConfig()
        assert config.enabled is True
        assert config.engine == "whisper"
        assert config.model == "base"
        assert config.language == "en"

    def test_custom_stt_config(self):
        """Test custom STT configuration."""
        config = STTConfig(
            model="small",
            language="es",
            device="cuda"
        )
        assert config.model == "small"
        assert config.language == "es"
        assert config.device == "cuda"


class TestRecorderConfig:
    """Tests for RecorderConfig."""

    def test_default_recorder_config(self):
        """Test default recorder configuration."""
        config = RecorderConfig()
        assert config.enabled is True
        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.vad_enabled is True

    def test_custom_recorder_config(self):
        """Test custom recorder configuration."""
        config = RecorderConfig(
            sample_rate=48000,
            channels=2,
            vad_enabled=False
        )
        assert config.sample_rate == 48000
        assert config.channels == 2
        assert config.vad_enabled is False


class TestPlayerConfig:
    """Tests for PlayerConfig."""

    def test_default_player_config(self):
        """Test default player configuration."""
        config = PlayerConfig()
        assert config.enabled is True
        assert config.volume == 0.8
        assert "wav" in config.supported_formats
        assert "mp3" in config.supported_formats


class TestVoiceEngine:
    """Tests for VoiceEngine."""

    def test_voice_engine_initialization(self):
        """Test VoiceEngine initialization."""
        engine = VoiceEngine()
        assert engine.config.enabled is True
        assert engine._initialized is False

    def test_voice_engine_with_custom_config(self):
        """Test VoiceEngine with custom configuration."""
        config = VoiceConfig(enabled=False)
        engine = VoiceEngine(config)
        assert engine.config.enabled is False

    def test_speak_when_disabled(self):
        """Test speak method when TTS is disabled."""
        config = VoiceConfig(enabled=False)
        engine = VoiceEngine(config)
        result = engine.speak("test")
        assert result is False

    def test_listen_when_disabled(self):
        """Test listen method when STT is disabled."""
        config = VoiceConfig(enabled=False)
        engine = VoiceEngine(config)
        result = engine.listen(5)
        assert result is None

    def test_record_when_disabled(self):
        """Test record method when recorder is disabled."""
        config = VoiceConfig(enabled=False)
        engine = VoiceEngine(config)
        result = engine.record("test.wav", 5)
        assert result is False

    def test_play_when_disabled(self):
        """Test play method when player is disabled."""
        config = VoiceConfig(enabled=False)
        engine = VoiceEngine(config)
        result = engine.play("test.wav")
        assert result is False

    def test_announce_when_disabled(self):
        """Test announce method when announcements are disabled."""
        config = VoiceConfig(enabled=False)
        engine = VoiceEngine(config)
        result = engine.announce("test_event")
        assert result is False
