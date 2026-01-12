"""Voice Activity Detection module."""

import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class VAD:
    """Voice Activity Detection."""
    
    def __init__(self, config):
        """Initialize VAD."""
        self.config = config
        self.threshold = config.silence_threshold
        self.silence_duration = config.silence_duration
        logger.info("VAD initialized")
    
    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Determine if audio chunk contains speech.
        
        Args:
            audio_chunk: Audio data bytes
            
        Returns:
            True if speech detected
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Calculate RMS (Root Mean Square) energy
            rms = np.sqrt(np.mean(audio_array**2))
            
            # Normalize to 0-1 range
            normalized_rms = rms / 32768.0
            
            return normalized_rms > self.threshold
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def get_speech_segments(self, audio_data: bytes, sample_rate: int) -> list:
        """
        Find speech segments in audio data.
        
        Args:
            audio_data: Full audio data
            sample_rate: Sample rate of audio
            
        Returns:
            List of (start_time, end_time) tuples in seconds
        """
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Process in chunks
            chunk_samples = int(sample_rate * 0.1)  # 100ms chunks
            segments = []
            in_speech = False
            segment_start = None
            
            for i in range(0, len(audio_array), chunk_samples):
                chunk = audio_array[i:i+chunk_samples]
                if len(chunk) == 0:
                    break
                
                is_speech = self.is_speech(chunk.tobytes())
                
                if is_speech and not in_speech:
                    segment_start = i / sample_rate
                    in_speech = True
                elif not is_speech and in_speech:
                    segment_end = i / sample_rate
                    segments.append((segment_start, segment_end))
                    in_speech = False
            
            # Close last segment if still in speech
            if in_speech:
                segments.append((segment_start, len(audio_array) / sample_rate))
            
            return segments
        except Exception as e:
            logger.error(f"Failed to get speech segments: {e}")
            return []
