"""Tests for voice profile management."""
import unittest
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
    spec.loader.exec_module(module)
    return module

# Load modules
bot_engine_path = project_root / "chatops" / "irc" / "bot-engine"
voice_profile_module = load_module("voice.cloning.voice_profile", bot_engine_path / "voice" / "cloning" / "voice_profile.py")

VoiceProfile = voice_profile_module.VoiceProfile
VoiceProfileManager = voice_profile_module.VoiceProfileManager


class TestVoiceProfile(unittest.TestCase):
    """Test VoiceProfile class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.profile = VoiceProfile(
            name="test-profile",
            engine="xtts",
            created_at=datetime.now(),
            sample_files=["sample1.wav", "sample2.wav"],
            model_path="/path/to/model",
            is_master=False,
            metadata={"test": "data"}
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_to_dict(self):
        """Test profile serialization to dict."""
        data = self.profile.to_dict()
        
        self.assertEqual(data['name'], "test-profile")
        self.assertEqual(data['engine'], "xtts")
        self.assertEqual(data['sample_files'], ["sample1.wav", "sample2.wav"])
        self.assertEqual(data['model_path'], "/path/to/model")
        self.assertFalse(data['is_master'])
        self.assertEqual(data['metadata'], {"test": "data"})
        self.assertIsInstance(data['created_at'], str)
    
    def test_from_dict(self):
        """Test profile deserialization from dict."""
        data = self.profile.to_dict()
        loaded = VoiceProfile.from_dict(data)
        
        self.assertEqual(loaded.name, self.profile.name)
        self.assertEqual(loaded.engine, self.profile.engine)
        self.assertEqual(loaded.sample_files, self.profile.sample_files)
        self.assertEqual(loaded.model_path, self.profile.model_path)
        self.assertEqual(loaded.is_master, self.profile.is_master)
        self.assertEqual(loaded.metadata, self.profile.metadata)
    
    def test_save_and_load(self):
        """Test saving and loading profile."""
        # Save profile
        self.profile.save(self.temp_dir)
        
        # Check file was created
        profile_file = os.path.join(self.temp_dir, "test-profile.json")
        self.assertTrue(os.path.exists(profile_file))
        
        # Load profile
        loaded = VoiceProfile.load("test-profile", self.temp_dir)
        
        self.assertEqual(loaded.name, self.profile.name)
        self.assertEqual(loaded.engine, self.profile.engine)
        self.assertEqual(loaded.sample_files, self.profile.sample_files)
    
    def test_load_nonexistent(self):
        """Test loading nonexistent profile raises error."""
        with self.assertRaises(FileNotFoundError):
            VoiceProfile.load("nonexistent", self.temp_dir)


class TestVoiceProfileManager(unittest.TestCase):
    """Test VoiceProfileManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = VoiceProfileManager(self.temp_dir)
        
        # Create test profiles
        self.profile1 = VoiceProfile(
            name="profile1",
            engine="xtts",
            created_at=datetime.now(),
            sample_files=["sample1.wav"],
            model_path="/path/to/model1",
            is_master=False
        )
        
        self.profile2 = VoiceProfile(
            name="profile2",
            engine="tortoise",
            created_at=datetime.now(),
            sample_files=["sample2.wav"],
            model_path="/path/to/model2",
            is_master=True
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_list_profiles_empty(self):
        """Test listing profiles when none exist."""
        profiles = self.manager.list_profiles()
        self.assertEqual(len(profiles), 0)
    
    def test_list_profiles_with_profiles(self):
        """Test listing profiles with saved profiles."""
        self.profile1.save(self.temp_dir)
        self.profile2.save(self.temp_dir)
        
        profiles = self.manager.list_profiles()
        self.assertEqual(len(profiles), 2)
        
        names = [p.name for p in profiles]
        self.assertIn("profile1", names)
        self.assertIn("profile2", names)
    
    def test_get_profile(self):
        """Test getting specific profile."""
        self.profile1.save(self.temp_dir)
        
        profile = self.manager.get_profile("profile1")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "profile1")
    
    def test_get_profile_nonexistent(self):
        """Test getting nonexistent profile returns None."""
        profile = self.manager.get_profile("nonexistent")
        self.assertIsNone(profile)
    
    def test_delete_profile(self):
        """Test deleting a profile."""
        self.profile1.save(self.temp_dir)
        
        # Verify exists
        self.assertTrue(self.manager.delete_profile("profile1"))
        
        # Verify deleted
        profile = self.manager.get_profile("profile1")
        self.assertIsNone(profile)
    
    def test_delete_nonexistent_profile(self):
        """Test deleting nonexistent profile returns False."""
        self.assertFalse(self.manager.delete_profile("nonexistent"))
    
    def test_get_master_voice(self):
        """Test getting master voice profile."""
        self.profile1.save(self.temp_dir)
        self.profile2.save(self.temp_dir)
        
        master = self.manager.get_master_voice()
        self.assertIsNotNone(master)
        self.assertEqual(master.name, "profile2")
        self.assertTrue(master.is_master)
    
    def test_get_master_voice_none(self):
        """Test getting master voice when none set."""
        self.profile1.save(self.temp_dir)
        
        master = self.manager.get_master_voice()
        self.assertIsNone(master)
    
    def test_set_master_voice(self):
        """Test setting master voice."""
        self.profile1.save(self.temp_dir)
        self.profile2.save(self.temp_dir)
        
        # Set profile1 as master
        self.assertTrue(self.manager.set_master_voice("profile1"))
        
        # Verify
        master = self.manager.get_master_voice()
        self.assertEqual(master.name, "profile1")
        self.assertTrue(master.is_master)
        
        # Verify profile2 is no longer master
        profile2 = self.manager.get_profile("profile2")
        self.assertFalse(profile2.is_master)
    
    def test_set_master_voice_nonexistent(self):
        """Test setting nonexistent profile as master."""
        self.assertFalse(self.manager.set_master_voice("nonexistent"))


if __name__ == '__main__':
    unittest.main()
