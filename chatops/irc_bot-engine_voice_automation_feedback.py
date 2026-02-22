"""Audio feedback sounds for voice automation."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AudioFeedback:
    """Manage audio feedback sounds."""
    
    SOUNDS = {
        "wake": "wake_chime.wav",
        "success": "success.wav",
        "error": "error.wav",
        "listening": "listening.wav",
        "processing": "processing.wav",
        "sleep": "sleep_chime.wav",
        "confirm": "confirm.wav",
        "cancel": "cancel.wav",
    }
    
    def __init__(self, sounds_dir: Optional[Path] = None, player: Optional['AudioPlayer'] = None):
        """
        Initialize audio feedback.
        
        Args:
            sounds_dir: Directory containing sound files
            player: AudioPlayer instance
        """
        if sounds_dir is None:
            sounds_dir = Path(__file__).parent.parent / "sounds"
        
        self.sounds_dir = Path(sounds_dir)
        self.player = player
        self.enabled = True
        
        logger.info(f"AudioFeedback initialized (dir: {self.sounds_dir})")
    
    def play(self, sound_type: str, blocking: bool = False):
        """
        Play a feedback sound.
        
        Args:
            sound_type: Type of sound (wake, success, error, etc.)
            blocking: Wait for sound to finish
        """
        if not self.enabled:
            return
        
        if not self.player:
            logger.warning("No audio player available for feedback")
            return
        
        sound_file = self.sounds_dir / self.SOUNDS.get(sound_type, "default.wav")
        
        if sound_file.exists():
            try:
                self.player.play(str(sound_file), blocking=blocking)
                logger.debug(f"Played sound: {sound_type}")
            except Exception as e:
                logger.error(f"Failed to play sound {sound_type}: {e}")
        else:
            logger.warning(f"Sound file not found: {sound_file}")
    
    def play_wake(self):
        """Play wake chime."""
        self.play("wake", blocking=False)
    
    def play_sleep(self):
        """Play sleep chime."""
        self.play("sleep", blocking=False)
    
    def play_listening(self):
        """Play listening sound."""
        self.play("listening", blocking=False)
    
    def play_processing(self):
        """Play processing sound."""
        self.play("processing", blocking=False)
    
    def play_success(self):
        """Play success sound."""
        self.play("success", blocking=False)
    
    def play_error(self):
        """Play error sound."""
        self.play("error", blocking=False)
    
    def enable(self):
        """Enable audio feedback."""
        self.enabled = True
        logger.info("Audio feedback enabled")
    
    def disable(self):
        """Disable audio feedback."""
        self.enabled = False
        logger.info("Audio feedback disabled")
