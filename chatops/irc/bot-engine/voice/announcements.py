"""Event-based audio announcements."""
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class AnnouncementManager:
    """Manages event-based audio announcements."""

    def __init__(self, config, player=None):
        """
        Initialize announcement manager.
        
        Args:
            config: AnnouncementConfig object
            player: AudioPlayer instance
        """
        self.config = config
        self.player = player
        self._event_sounds: Dict[str, str] = {}
        
        # Load configured event sounds
        self._load_event_sounds()
        
        logger.info("AnnouncementManager initialized")

    def _load_event_sounds(self):
        """Load event sound mappings from configuration."""
        if not self.config.events:
            logger.warning("No event sounds configured")
            return

        sound_dir = Path(self.config.directory)
        
        for event, sound_file in self.config.events.items():
            sound_path = sound_dir / sound_file
            if sound_path.exists():
                self._event_sounds[event] = str(sound_path)
                logger.info(f"Loaded sound for event '{event}': {sound_file}")
            else:
                logger.warning(f"Sound file not found for event '{event}': {sound_path}")

    def register_event(self, event: str, sound_file: str) -> bool:
        """
        Register a sound for an event.
        
        Args:
            event: Event name
            sound_file: Path to sound file (absolute or relative to sound directory)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle absolute and relative paths
            sound_path = Path(sound_file)
            if not sound_path.is_absolute():
                sound_path = Path(self.config.directory) / sound_file
            
            if not sound_path.exists():
                logger.error(f"Sound file not found: {sound_path}")
                return False
            
            self._event_sounds[event] = str(sound_path)
            logger.info(f"Registered sound for event '{event}': {sound_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering event sound: {e}")
            return False

    def unregister_event(self, event: str) -> bool:
        """
        Unregister a sound for an event.
        
        Args:
            event: Event name
            
        Returns:
            True if successful, False otherwise
        """
        if event in self._event_sounds:
            del self._event_sounds[event]
            logger.info(f"Unregistered event: {event}")
            return True
        
        logger.warning(f"Event not found: {event}")
        return False

    def announce(self, event: str) -> bool:
        """
        Play announcement for an event.
        
        Args:
            event: Event name
            
        Returns:
            True if announcement played successfully, False otherwise
        """
        if not self.player:
            logger.warning("No audio player available")
            return False

        if event not in self._event_sounds:
            logger.warning(f"No sound registered for event: {event}")
            return False

        try:
            sound_file = self._event_sounds[event]
            logger.info(f"Playing announcement for event: {event}")
            return self.player.play_async(sound_file)
            
        except Exception as e:
            logger.error(f"Error playing announcement: {e}")
            return False

    def get_registered_events(self) -> Dict[str, str]:
        """
        Get all registered events and their sound files.
        
        Returns:
            Dictionary of event names to sound file paths
        """
        return self._event_sounds.copy()

    def has_event(self, event: str) -> bool:
        """
        Check if an event has a registered sound.
        
        Args:
            event: Event name
            
        Returns:
            True if event has a sound, False otherwise
        """
        return event in self._event_sounds
