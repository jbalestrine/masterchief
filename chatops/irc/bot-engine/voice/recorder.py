"""Audio recording using sounddevice."""
import logging
import time
import tempfile
from pathlib import Path
from typing import Optional
import threading

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Audio recorder using sounddevice for capturing microphone input."""

    def __init__(self, config):
        """Initialize audio recorder."""
        self.config = config
        self._recording = False
        self._audio_data = []
        
        # Try to import sounddevice and soundfile
        try:
            import sounddevice as sd
            import soundfile as sf
            self._sd = sd
            self._sf = sf
            
            # Initialize VAD if enabled
            if self.config.vad_enabled:
                try:
                    from .vad import VoiceActivityDetector
                    self._vad = VoiceActivityDetector(self.config.vad_aggressiveness)
                except Exception as e:
                    logger.warning(f"Could not initialize VAD: {e}")
                    self._vad = None
            else:
                self._vad = None
            
            logger.info("AudioRecorder initialized successfully")
        except ImportError as e:
            logger.warning(f"Required audio libraries not installed: {e}")
            self._sd = None
            self._sf = None

    def record(self, duration: Optional[int] = None, output_file: Optional[str] = None) -> Optional[str]:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds (None for VAD-based)
            output_file: Optional output filename
            
        Returns:
            Path to recorded file or None if failed
        """
        if not self._sd or not self._sf:
            logger.warning("Audio recording not available")
            return None

        try:
            logger.info(f"Starting audio recording (duration: {duration or 'VAD-based'})")
            
            if duration:
                # Fixed duration recording
                return self._record_fixed_duration(duration, output_file)
            elif self._vad:
                # VAD-based recording
                return self._record_with_vad(output_file)
            else:
                # Default to 5 seconds if no VAD and no duration
                logger.warning("No duration specified and VAD not available, using 5 seconds")
                return self._record_fixed_duration(5, output_file)
                
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None

    def _record_fixed_duration(self, duration: int, output_file: Optional[str] = None) -> Optional[str]:
        """Record audio for a fixed duration."""
        try:
            # Record audio
            logger.info(f"Recording for {duration} seconds...")
            recording = self._sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype='int16'
            )
            self._sd.wait()
            
            # Save to file
            if not output_file:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=f".{self.config.format}",
                    delete=False
                )
                output_file = temp_file.name
                temp_file.close()
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._sf.write(str(output_path), recording, self.config.sample_rate)
            logger.info(f"Audio saved to: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error in fixed duration recording: {e}")
            return None

    def _record_with_vad(self, output_file: Optional[str] = None) -> Optional[str]:
        """Record audio using Voice Activity Detection."""
        if not self._vad:
            logger.warning("VAD not available")
            return None

        try:
            logger.info("Recording with VAD (speak now)...")
            
            self._recording = True
            self._audio_data = []
            silence_start = None
            
            def audio_callback(indata, frames, time_info, status):
                """Callback for audio stream."""
                if status:
                    logger.warning(f"Audio callback status: {status}")
                
                if self._recording:
                    self._audio_data.append(indata.copy())
                    
                    # Check for voice activity
                    if self._vad:
                        is_speech = self._vad.is_speech(
                            indata.tobytes(),
                            self.config.sample_rate
                        )
                        
                        nonlocal silence_start
                        if not is_speech:
                            if silence_start is None:
                                silence_start = time.time()
                            elif time.time() - silence_start >= self.config.silence_duration:
                                self._recording = False
                        else:
                            silence_start = None
            
            # Start recording stream
            with self._sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype='int16',
                callback=audio_callback
            ):
                # Wait for recording to complete or timeout (30 seconds max)
                timeout = 30
                start_time = time.time()
                while self._recording and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
            
            if not self._audio_data:
                logger.warning("No audio data recorded")
                return None
            
            # Concatenate audio data
            import numpy as np
            audio_array = np.concatenate(self._audio_data, axis=0)
            
            # Save to file
            if not output_file:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=f".{self.config.format}",
                    delete=False
                )
                output_file = temp_file.name
                temp_file.close()
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._sf.write(str(output_path), audio_array, self.config.sample_rate)
            logger.info(f"Audio saved to: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error in VAD recording: {e}")
            return None

    def stop_recording(self):
        """Stop current recording."""
        logger.info("Stopping recording")
        self._recording = False

    def get_devices(self):
        """Get list of available audio devices."""
        if not self._sd:
            return []

        try:
            devices = self._sd.query_devices()
            return devices
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
            return []
