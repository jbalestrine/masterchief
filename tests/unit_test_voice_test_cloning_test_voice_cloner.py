"""Tests for VoiceCloner main class."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modules directly from file paths due to hyphenated directory names
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load modules
bot_engine_path = project_root / "chatops" / "irc" / "bot-engine"
voice_base = load_module("voice.base", bot_engine_path / "voice" / "base.py")
voice_profile_module = load_module("voice.cloning.voice_profile", bot_engine_path / "voice" / "cloning" / "voice_profile.py")
cloning_base = load_module("voice.cloning.base", bot_engine_path / "voice" / "cloning" / "base.py")
xtts = load_module("voice.cloning.xtts_cloner", bot_engine_path / "voice" / "cloning" / "xtts_cloner.py")
tortoise = load_module("voice.cloning.tortoise_cloner", bot_engine_path / "voice" / "cloning" / "tortoise_cloner.py")
openvoice = load_module("voice.cloning.openvoice_cloner", bot_engine_path / "voice" / "cloning" / "openvoice_cloner.py")
trainer = load_module("voice.cloning.trainer", bot_engine_path / "voice" / "cloning" / "trainer.py")
voice_cloner_module = load_module("voice.cloning.voice_cloner", bot_engine_path / "voice" / "cloning" / "voice_cloner.py")

VoiceCloningConfig = voice_base.VoiceCloningConfig
VoiceCloner = voice_cloner_module.VoiceCloner
VoiceProfile = voice_profile_module.VoiceProfile


class TestVoiceCloner(unittest.TestCase):
    """Test VoiceCloner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = VoiceCloningConfig(
            profiles_dir=os.path.join(self.temp_dir, "profiles"),
            samples_dir=os.path.join(self.temp_dir, "samples"),
            device="cpu",
            engine="xtts"
        )
        
        # Create directories
        os.makedirs(self.config.profiles_dir, exist_ok=True)
        os.makedirs(self.config.samples_dir, exist_ok=True)
        
        self.cloner = VoiceCloner(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test VoiceCloner initialization."""
        self.assertIsNotNone(self.cloner)
        self.assertIsNotNone(self.cloner.xtts)
        self.assertIsNotNone(self.cloner.tortoise)
        self.assertIsNotNone(self.cloner.openvoice)
        self.assertIsNotNone(self.cloner.profiles)
    
    def test_get_cloner_xtts(self):
        """Test getting XTTS cloner."""
        cloner = self.cloner._get_cloner("xtts")
        self.assertEqual(cloner, self.cloner.xtts)
    
    def test_get_cloner_tortoise(self):
        """Test getting Tortoise cloner."""
        cloner = self.cloner._get_cloner("tortoise")
        self.assertEqual(cloner, self.cloner.tortoise)
    
    def test_get_cloner_openvoice(self):
        """Test getting OpenVoice cloner."""
        cloner = self.cloner._get_cloner("openvoice")
        self.assertEqual(cloner, self.cloner.openvoice)
    
    def test_get_cloner_invalid(self):
        """Test getting invalid cloner raises error."""
        with self.assertRaises(ValueError):
            self.cloner._get_cloner("invalid")
    
    def test_clone_voice(self):
        """Test cloning a voice."""
        # Mock train_voice directly on the instance
        mock_model_path = os.path.join(self.temp_dir, "model.pt")
        self.cloner.xtts.train_voice = Mock(return_value=mock_model_path)
        
        # Create mock audio files
        audio_files = []
        for i in range(3):
            filepath = os.path.join(self.temp_dir, f"audio_{i}.wav")
            with open(filepath, 'w') as f:
                f.write("mock audio")
            audio_files.append(filepath)
        
        # Clone voice
        profile = self.cloner.clone_voice(
            name="test-voice",
            audio_files=audio_files,
            engine="xtts"
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "test-voice")
        self.assertEqual(profile.engine, "xtts")
        self.assertEqual(len(profile.sample_files), 3)
        self.assertFalse(profile.is_master)
    
    def test_clone_voice_no_files(self):
        """Test cloning voice with no audio files raises error."""
        with self.assertRaises(ValueError):
            self.cloner.clone_voice(
                name="test-voice",
                audio_files=[],
                engine="xtts"
            )
    
    def test_create_master_voice(self):
        """Test creating master voice."""
        # Mock train_voice directly on the instance
        mock_model_path = os.path.join(self.temp_dir, "model.pt")
        self.cloner.xtts.train_voice = Mock(return_value=mock_model_path)
        
        # Create mock audio files
        audio_files = []
        for i in range(3):
            filepath = os.path.join(self.temp_dir, f"audio_{i}.wav")
            with open(filepath, 'w') as f:
                f.write("mock audio")
            audio_files.append(filepath)
        
        # Create master voice
        profile = self.cloner.create_master_voice(
            name="master-voice",
            audio_files=audio_files,
            engine="xtts"
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "master-voice")
        
        # Reload the profile from disk to check is_master flag
        loaded_profile = self.cloner.get_profile("master-voice")
        self.assertTrue(loaded_profile.is_master)
        self.assertEqual(self.cloner.master_voice.name, "master-voice")
    
    def test_list_profiles(self):
        """Test listing profiles."""
        # Initially empty
        profiles = self.cloner.list_profiles()
        self.assertEqual(len(profiles), 0)
    
    def test_set_master_voice(self):
        """Test setting master voice."""
        # Mock train_voice directly on the instance
        mock_model_path = os.path.join(self.temp_dir, "model.pt")
        self.cloner.xtts.train_voice = Mock(return_value=mock_model_path)
        
        # Create audio file
        audio_file = os.path.join(self.temp_dir, "audio.wav")
        with open(audio_file, 'w') as f:
            f.write("mock audio")
        
        # Clone voice
        profile = self.cloner.clone_voice(
            name="test-voice",
            audio_files=[audio_file],
            engine="xtts"
        )
        
        # Set as master
        self.cloner.set_master_voice("test-voice")
        
        self.assertEqual(self.cloner.master_voice.name, "test-voice")
        self.assertTrue(self.cloner.master_voice.is_master)
    
    def test_set_master_voice_nonexistent(self):
        """Test setting nonexistent voice as master raises error."""
        with self.assertRaises(ValueError):
            self.cloner.set_master_voice("nonexistent")
    
    def test_speak_as_master(self):
        """Test speaking with master voice."""
        # Mock train_voice and synthesize_speech directly on the instance
        mock_model_path = os.path.join(self.temp_dir, "model.pt")
        self.cloner.xtts.train_voice = Mock(return_value=mock_model_path)
        self.cloner.xtts.synthesize_speech = Mock(return_value=b"mock audio data")
        
        # Create audio file
        audio_file = os.path.join(self.temp_dir, "audio.wav")
        with open(audio_file, 'w') as f:
            f.write("mock audio")
        
        # Create master voice
        self.cloner.create_master_voice(
            name="master",
            audio_files=[audio_file],
            engine="xtts"
        )
        
        # Speak
        audio = self.cloner.speak_as_master("Hello world")
        
        self.assertEqual(audio, b"mock audio data")
        self.cloner.xtts.synthesize_speech.assert_called_once()
    
    def test_speak_as_master_no_master(self):
        """Test speaking without master voice raises error."""
        with self.assertRaises(ValueError):
            self.cloner.speak_as_master("Hello world")
    
    def test_get_profile(self):
        """Test getting profile."""
        profile = self.cloner.get_profile("nonexistent")
        self.assertIsNone(profile)
    
    def test_delete_profile(self):
        """Test deleting profile."""
        result = self.cloner.delete_profile("nonexistent")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
