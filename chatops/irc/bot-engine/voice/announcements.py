"""Voice announcements module."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceAnnouncer:
    """Voice announcements for IRC events."""
    
    def __init__(self, voice_engine):
        """Initialize voice announcer."""
        self.voice_engine = voice_engine
        self.enabled = False
        logger.info("VoiceAnnouncer initialized")
    
    def enable(self):
        """Enable voice announcements."""
        self.enabled = True
        logger.info("Voice announcements enabled")
    
    def disable(self):
        """Disable voice announcements."""
        self.enabled = False
        logger.info("Voice announcements disabled")
    
    def announce_join(self, nick: str, channel: str):
        """Announce user join."""
        if self.enabled:
            self.voice_engine.speak(f"{nick} joined {channel}", blocking=False)
    
    def announce_part(self, nick: str, channel: str):
        """Announce user part."""
        if self.enabled:
            self.voice_engine.speak(f"{nick} left {channel}", blocking=False)
    
    def announce_message(self, nick: str, message: str, channel: Optional[str] = None):
        """Announce channel message."""
        if self.enabled:
            location = f"in {channel}" if channel else "privately"
            self.voice_engine.speak(f"{nick} says {location}: {message}", blocking=False)
    
    def announce_custom(self, message: str):
        """Announce custom message."""
        if self.enabled:
            self.voice_engine.speak(message, blocking=False)
