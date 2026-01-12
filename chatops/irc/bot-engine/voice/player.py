"""Audio playback module."""

import logging
from typing import Optional
import threading
"""Audio playback using pygame."""
import logging
import threading
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)


class AudioPlayer:
    """Play audio through speakers."""
    
    """Audio player using pygame for playing audio files."""

    def __init__(self, config):
        """Initialize audio player."""
        self.config = config
        self._playing = False
        self._lock = threading.Lock()
        self._initialize()
    
    def _initialize(self):
        """Initialize audio output."""
        try:
            import sounddevice as sd
            self.sd = sd
            logger.info("Audio player initialized")
        except ImportError:
            logger.warning("sounddevice not installed, audio playback will not work")
            self.sd = None
    
    def play(self, audio_data: bytes, blocking: bool = True) -> bool:
        """
        Play audio data.
        
        Args:
            audio_data: Audio bytes (WAV format)
            blocking: Wait for playback to complete
            
        Returns:
            True if successful
        """
        if not self.sd:
            logger.error("Audio player not initialized")
            return False
        
        if isinstance(audio_data, str):
            # If it's a file path, read the file
            try:
                with open(audio_data, 'rb') as f:
                    audio_data = f.read()
            except Exception as e:
                logger.error(f"Failed to read audio file: {e}")
                return False
        
        try:
            import wave
            import io
            import numpy as np
            
            # Parse WAV data
            buffer = io.BytesIO(audio_data)
            with wave.open(buffer, 'rb') as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                frames = wf.readframes(wf.getnframes())
                audio_array = np.frombuffer(frames, dtype=np.int16)
                
                if channels > 1:
                    audio_array = audio_array.reshape(-1, channels)
            
            with self._lock:
                self._playing = True
            
            # Play audio
            self.sd.play(audio_array, sample_rate, blocking=blocking)
            
            if blocking:
                self.sd.wait()
                with self._lock:
                    self._playing = False
            else:
                # Set flag to False after playback in separate thread
                def reset_flag():
                    self.sd.wait()
                    with self._lock:
                        self._playing = False
                
                thread = threading.Thread(target=reset_flag, daemon=True)
                thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            with self._lock:
                self._playing = False
            return False
    
    def stop(self):
        """Stop current playback."""
        if self.sd:
            try:
                self.sd.stop()
                with self._lock:
                    self._playing = False
            except Exception as e:
                logger.error(f"Failed to stop playback: {e}")
    
    def is_playing(self) -> bool:
        """Check if currently playing audio."""
        with self._lock:
            return self._playing
        
        # Try to import pygame
        try:
            import pygame
            self._pygame = pygame
            
            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.config.volume)
            
            logger.info("AudioPlayer initialized successfully")
        except ImportError:
            logger.warning("pygame not installed, audio playback will not be available")
            self._pygame = None
        except Exception as e:
            logger.error(f"Error initializing audio player: {e}")
            self._pygame = None

    def play(self, filename: str, blocking: bool = False) -> bool:
        """
        Play an audio file.
        
        Args:
            filename: Path to audio file
            blocking: If True, wait for playback to complete
            
        Returns:
            True if playback started successfully, False otherwise
        """
        if not self._pygame:
            logger.warning("Audio player not available")
            return False

        try:
            file_path = Path(filename)
            if not file_path.exists():
                logger.error(f"Audio file not found: {filename}")
                return False

            # Check file format
            file_ext = file_path.suffix.lower().lstrip('.')
            if file_ext not in self.config.supported_formats:
                logger.warning(f"Unsupported audio format: {file_ext}")
                # Try to play anyway
            
            with self._lock:
                # Stop any currently playing audio
                if self._playing:
                    self._pygame.mixer.music.stop()
                
                # Load and play
                logger.info(f"Playing audio: {filename}")
                self._pygame.mixer.music.load(str(file_path))
                self._pygame.mixer.music.play()
                self._playing = True
            
            if blocking:
                # Wait for playback to complete
                while self._pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                self._playing = False
            
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False

    def play_async(self, filename: str) -> bool:
        """
        Play an audio file asynchronously in a separate thread.
        
        Args:
            filename: Path to audio file
            
        Returns:
            True if playback thread started successfully, False otherwise
        """
        def _play_thread():
            self.play(filename, blocking=True)
        
        try:
            thread = threading.Thread(target=_play_thread, daemon=True)
            thread.start()
            return True
        except Exception as e:
            logger.error(f"Error starting playback thread: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop current playback.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._pygame:
            return False

        try:
            with self._lock:
                if self._playing:
                    logger.info("Stopping audio playback")
                    self._pygame.mixer.music.stop()
                    self._playing = False
            return True
            
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
            return False

    def pause(self) -> bool:
        """
        Pause current playback.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._pygame:
            return False

        try:
            with self._lock:
                if self._playing:
                    logger.info("Pausing audio playback")
                    self._pygame.mixer.music.pause()
            return True
            
        except Exception as e:
            logger.error(f"Error pausing playback: {e}")
            return False

    def resume(self) -> bool:
        """
        Resume paused playback.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._pygame:
            return False

        try:
            with self._lock:
                logger.info("Resuming audio playback")
                self._pygame.mixer.music.unpause()
            return True
            
        except Exception as e:
            logger.error(f"Error resuming playback: {e}")
            return False

    def set_volume(self, volume: float) -> bool:
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._pygame:
            return False

        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to 0.0-1.0
            with self._lock:
                self._pygame.mixer.music.set_volume(volume)
                self.config.volume = volume
                logger.info(f"Set volume to: {volume}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        if not self._pygame:
            return False

        try:
            return self._pygame.mixer.music.get_busy()
        except Exception as e:
            logger.error(f"Error checking playback status: {e}")
            return False

    def shutdown(self):
        """Shutdown the audio player and cleanup resources."""
        logger.info("Shutting down audio player")
        
        if self._pygame:
            try:
                self.stop()
                self._pygame.mixer.quit()
            except Exception as e:
                logger.error(f"Error shutting down audio player: {e}")
