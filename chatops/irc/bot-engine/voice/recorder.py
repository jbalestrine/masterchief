"""Audio recording module."""

import logging
from typing import Optional
import time

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Record audio from microphone."""
    
    def __init__(self, config):
        """Initialize audio recorder."""
        self.config = config
        self.stream = None
        self._initialize()
    
    def _initialize(self):
        """Initialize audio input."""
        try:
            import sounddevice as sd
            self.sd = sd
            logger.info("Audio recorder initialized")
        except ImportError:
            logger.warning("sounddevice not installed, audio recording will not work")
            self.sd = None
    
    def record(self, timeout: Optional[float] = None, use_vad: bool = True) -> Optional[bytes]:
        """
        Record audio until silence or timeout.
        
        Args:
            timeout: Maximum recording time in seconds
            use_vad: Use voice activity detection to stop recording
            
        Returns:
            Audio data as bytes or None
        """
        if not self.sd:
            logger.error("Audio recorder not initialized")
            return None
        
        try:
            import numpy as np
            
            duration = timeout if timeout else 10.0  # Default 10 seconds
            
            # Record audio
            audio = self.sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype='int16',
                device=self.config.device_index
            )
            self.sd.wait()
            
            # Convert to bytes
            import wave
            import io
            
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(self.config.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.config.sample_rate)
                wf.writeframes(audio.tobytes())
            
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Audio recording failed: {e}")
            return None
    
    def start_stream(self):
        """Start continuous audio stream."""
        if not self.sd:
            return
        
        try:
            self.stream = self.sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype='int16',
                device=self.config.device_index
            )
            self.stream.start()
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
    
    def stop_stream(self):
        """Stop continuous audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def read_chunk(self) -> Optional[bytes]:
        """Read a chunk from the stream."""
        if not self.stream:
            return None
        
        try:
            data, overflowed = self.stream.read(self.config.chunk_size)
            return data.tobytes()
        except Exception as e:
            logger.error(f"Failed to read audio chunk: {e}")
            return None
