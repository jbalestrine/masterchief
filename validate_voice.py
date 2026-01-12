#!/usr/bin/env python3
"""Validation script for voice/audio system."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all voice modules can be imported."""
    print("Testing imports...")
    
    try:
        from chatops.irc.bot_engine import IRCBot, BindType
        print("  ✓ IRC bot imports")
        
        # Check new bind types
        assert hasattr(BindType, 'VOICE'), "VOICE bind type missing"
        assert hasattr(BindType, 'TTS'), "TTS bind type missing"
        assert hasattr(BindType, 'AUDIO'), "AUDIO bind type missing"
        print("  ✓ New bind types (VOICE, TTS, AUDIO)")
        
        from chatops.irc.bot_engine.voice import VoiceEngine, VoiceConfig
        print("  ✓ Voice engine imports")
        
        from chatops.irc.bot_engine.voice.base import (
            TTSConfig, STTConfig, RecorderConfig, PlayerConfig, AnnouncementConfig
        )
        print("  ✓ Voice config classes")
        
        from chatops.irc.bot_engine.voice.tts import TTSEngine
        print("  ✓ TTS engine")
        
        from chatops.irc.bot_engine.voice.stt import STTEngine
        print("  ✓ STT engine")
        
        from chatops.irc.bot_engine.voice.recorder import AudioRecorder
        print("  ✓ Audio recorder")
        
        from chatops.irc.bot_engine.voice.player import AudioPlayer
        print("  ✓ Audio player")
        
        from chatops.irc.bot_engine.voice.vad import VoiceActivityDetector
        print("  ✓ Voice activity detector")
        
        from chatops.irc.bot_engine.voice.announcements import AnnouncementManager
        print("  ✓ Announcement manager")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False


def test_voice_config():
    """Test voice configuration."""
    print("\nTesting voice configuration...")
    
    try:
        from chatops.irc.bot_engine.voice import VoiceConfig
        
        # Default config
        config = VoiceConfig()
        assert config.enabled is True
        print("  ✓ Default configuration")
        
        # From dict
        config_dict = {
            "enabled": True,
            "tts": {"rate": 200, "volume": 0.5},
            "stt": {"model": "small"}
        }
        config = VoiceConfig.from_dict(config_dict)
        assert config.tts.rate == 200
        assert config.stt.model == "small"
        print("  ✓ Configuration from dictionary")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False


def test_voice_engine():
    """Test voice engine initialization."""
    print("\nTesting voice engine...")
    
    try:
        from chatops.irc.bot_engine.voice import VoiceEngine, VoiceConfig
        
        # Create engine with disabled config (to avoid dependency issues)
        config = VoiceConfig(enabled=False)
        engine = VoiceEngine(config)
        
        assert engine.config.enabled is False
        assert engine._initialized is False
        print("  ✓ Engine initialization")
        
        # Test disabled methods
        result = engine.speak("test")
        assert result is False
        print("  ✓ Speak method (disabled)")
        
        result = engine.listen(5)
        assert result is None
        print("  ✓ Listen method (disabled)")
        
        result = engine.record("test.wav", 5)
        assert result is False
        print("  ✓ Record method (disabled)")
        
        result = engine.play("test.wav")
        assert result is False
        print("  ✓ Play method (disabled)")
        
        result = engine.announce("test_event")
        assert result is False
        print("  ✓ Announce method (disabled)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Engine error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bind_types():
    """Test IRC bot bind types."""
    print("\nTesting IRC bot bind types...")
    
    try:
        from chatops.irc.bot_engine import BindType
        
        # Check all bind types exist
        bind_types = [
            "PUB", "MSG", "JOIN", "PART", "TIME", "RAW", "DCC", "PUBM",
            "VOICE", "TTS", "AUDIO"
        ]
        
        for bt in bind_types:
            assert hasattr(BindType, bt), f"{bt} bind type missing"
            print(f"  ✓ BindType.{bt}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Bind type error: {e}")
        return False


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Voice/Audio System Validation")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_voice_config()))
    results.append(("Voice Engine", test_voice_engine()))
    results.append(("Bind Types", test_bind_types()))
    
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All validations passed!")
        return 0
    else:
        print("\n✗ Some validations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
