"""Unit tests for announcements module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from chatops.irc.bot_engine.voice.announcements import AnnouncementManager
from chatops.irc.bot_engine.voice.base import AnnouncementConfig


class TestAnnouncementManager:
    """Tests for AnnouncementManager."""

    def test_initialization(self):
        """Test AnnouncementManager initialization."""
        config = AnnouncementConfig(
            enabled=True,
            directory="./sounds",
            events={}
        )
        manager = AnnouncementManager(config)
        
        assert manager.config == config
        assert manager._event_sounds == {}

    def test_register_event(self, tmp_path):
        """Test registering an event sound."""
        config = AnnouncementConfig(
            enabled=True,
            directory=str(tmp_path),
            events={}
        )
        manager = AnnouncementManager(config)
        
        # Create a test sound file
        sound_file = tmp_path / "test.wav"
        sound_file.touch()
        
        result = manager.register_event("test_event", str(sound_file))
        assert result is True
        assert manager.has_event("test_event")

    def test_register_nonexistent_file(self, tmp_path):
        """Test registering a nonexistent sound file."""
        config = AnnouncementConfig(
            enabled=True,
            directory=str(tmp_path),
            events={}
        )
        manager = AnnouncementManager(config)
        
        result = manager.register_event("test_event", "nonexistent.wav")
        assert result is False
        assert not manager.has_event("test_event")

    def test_unregister_event(self, tmp_path):
        """Test unregistering an event."""
        config = AnnouncementConfig(
            enabled=True,
            directory=str(tmp_path),
            events={}
        )
        manager = AnnouncementManager(config)
        
        # Create and register a test sound
        sound_file = tmp_path / "test.wav"
        sound_file.touch()
        manager.register_event("test_event", str(sound_file))
        
        # Unregister
        result = manager.unregister_event("test_event")
        assert result is True
        assert not manager.has_event("test_event")

    def test_announce_with_player(self, tmp_path):
        """Test announcing an event with a player."""
        config = AnnouncementConfig(
            enabled=True,
            directory=str(tmp_path),
            events={}
        )
        
        # Mock player
        mock_player = Mock()
        mock_player.play_async.return_value = True
        
        manager = AnnouncementManager(config, mock_player)
        
        # Create and register a test sound
        sound_file = tmp_path / "test.wav"
        sound_file.touch()
        manager.register_event("test_event", str(sound_file))
        
        # Announce
        result = manager.announce("test_event")
        assert result is True
        mock_player.play_async.assert_called_once()

    def test_announce_without_player(self, tmp_path):
        """Test announcing without a player."""
        config = AnnouncementConfig(
            enabled=True,
            directory=str(tmp_path),
            events={}
        )
        manager = AnnouncementManager(config, player=None)
        
        # Create and register a test sound
        sound_file = tmp_path / "test.wav"
        sound_file.touch()
        manager.register_event("test_event", str(sound_file))
        
        # Announce should fail without player
        result = manager.announce("test_event")
        assert result is False

    def test_announce_unregistered_event(self):
        """Test announcing an unregistered event."""
        config = AnnouncementConfig(
            enabled=True,
            directory="./sounds",
            events={}
        )
        mock_player = Mock()
        manager = AnnouncementManager(config, mock_player)
        
        result = manager.announce("nonexistent_event")
        assert result is False
        mock_player.play_async.assert_not_called()

    def test_get_registered_events(self, tmp_path):
        """Test getting all registered events."""
        config = AnnouncementConfig(
            enabled=True,
            directory=str(tmp_path),
            events={}
        )
        manager = AnnouncementManager(config)
        
        # Register multiple events
        for i in range(3):
            sound_file = tmp_path / f"sound{i}.wav"
            sound_file.touch()
            manager.register_event(f"event{i}", str(sound_file))
        
        events = manager.get_registered_events()
        assert len(events) == 3
        assert "event0" in events
        assert "event1" in events
        assert "event2" in events

    def test_has_event(self, tmp_path):
        """Test has_event method."""
        config = AnnouncementConfig(
            enabled=True,
            directory=str(tmp_path),
            events={}
        )
        manager = AnnouncementManager(config)
        
        assert not manager.has_event("test_event")
        
        # Register event
        sound_file = tmp_path / "test.wav"
        sound_file.touch()
        manager.register_event("test_event", str(sound_file))
        
        assert manager.has_event("test_event")
