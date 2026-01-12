"""Voice Activity Detection using WebRTC VAD."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceActivityDetector:
    """Voice Activity Detector using WebRTC VAD."""

    def __init__(self, aggressiveness: int = 2):
        """
        Initialize VAD.
        
        Args:
            aggressiveness: VAD aggressiveness (0-3), higher = more aggressive
        """
        self.aggressiveness = max(0, min(3, aggressiveness))
        self._vad = None
        
        # Try to import webrtcvad
        try:
            import webrtcvad
            self._vad = webrtcvad.Vad(self.aggressiveness)
            logger.info(f"VAD initialized with aggressiveness: {self.aggressiveness}")
        except ImportError:
            logger.warning("webrtcvad not installed, VAD will not be available")
        except Exception as e:
            logger.error(f"Error initializing VAD: {e}")

    def is_speech(self, audio_frame: bytes, sample_rate: int) -> bool:
        """
        Check if audio frame contains speech.
        
        Args:
            audio_frame: Audio data as bytes
            sample_rate: Sample rate (8000, 16000, 32000, or 48000)
            
        Returns:
            True if speech detected, False otherwise
        """
        if not self._vad:
            logger.warning("VAD not available")
            return True  # Assume speech if VAD not available

        try:
            # WebRTC VAD requires specific sample rates
            supported_rates = [8000, 16000, 32000, 48000]
            if sample_rate not in supported_rates:
                logger.warning(f"Unsupported sample rate: {sample_rate}, using 16000")
                sample_rate = 16000
            
            # Frame length must be 10, 20, or 30 ms
            # Calculate expected frame size
            frame_duration = 20  # ms
            frame_size = int(sample_rate * frame_duration / 1000) * 2  # *2 for 16-bit audio
            
            # Pad or trim frame to correct size
            if len(audio_frame) < frame_size:
                audio_frame = audio_frame + b'\x00' * (frame_size - len(audio_frame))
            elif len(audio_frame) > frame_size:
                audio_frame = audio_frame[:frame_size]
            
            return self._vad.is_speech(audio_frame, sample_rate)
            
        except Exception as e:
            logger.error(f"Error in VAD speech detection: {e}")
            return True  # Assume speech on error

    def set_aggressiveness(self, aggressiveness: int) -> bool:
        """
        Set VAD aggressiveness level.
        
        Args:
            aggressiveness: VAD aggressiveness (0-3)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._vad:
            return False

        try:
            aggressiveness = max(0, min(3, aggressiveness))
            self._vad.set_mode(aggressiveness)
            self.aggressiveness = aggressiveness
            logger.info(f"Set VAD aggressiveness to: {aggressiveness}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting VAD aggressiveness: {e}")
            return False

    def process_audio_stream(self, audio_data: bytes, sample_rate: int, frame_duration_ms: int = 30):
        """
        Process audio stream and return segments with speech detection results.
        
        Args:
            audio_data: Audio data as bytes
            sample_rate: Sample rate
            frame_duration_ms: Frame duration in milliseconds (10, 20, or 30)
            
        Returns:
            List of tuples (audio_frame, is_speech)
        """
        if not self._vad:
            logger.warning("VAD not available")
            return []

        try:
            frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
            results = []
            
            for i in range(0, len(audio_data), frame_size):
                frame = audio_data[i:i + frame_size]
                
                # Skip if frame too small
                if len(frame) < frame_size:
                    break
                
                is_speech = self.is_speech(frame, sample_rate)
                results.append((frame, is_speech))
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing audio stream: {e}")
            return []
