"""Audio playback module."""

import logging
from typing import Optional
import threading

logger = logging.getLogger(__name__)


class AudioPlayer:
    """Play audio through speakers."""
    
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
