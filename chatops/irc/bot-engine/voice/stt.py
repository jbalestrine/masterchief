"""Speech-to-Text engine using OpenAI Whisper."""
import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class STTEngine:
    """Speech-to-text engine using OpenAI Whisper for local transcription."""

    def __init__(self, config):
        """Initialize STT engine."""
        self.config = config
        self._model = None
        
        # Try to import whisper
        try:
            import whisper
            self._whisper = whisper
            self._load_model()
            logger.info(f"STTEngine initialized with model: {self.config.model}")
        except ImportError:
            logger.warning("whisper not installed, STT will not be available")
            self._whisper = None
        except Exception as e:
            logger.error(f"Error initializing STT engine: {e}")
            self._whisper = None

    def _load_model(self):
        """Load the Whisper model."""
        if not self._whisper:
            return

        try:
            logger.info(f"Loading Whisper model: {self.config.model}")
            self._model = self._whisper.load_model(
                self.config.model,
                device=self.config.device
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            self._model = None

    def transcribe_file(self, audio_file: str) -> Optional[str]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text or None if failed
        """
        if not self._model:
            logger.warning("STT model not available, cannot transcribe")
            return None

        try:
            logger.info(f"Transcribing audio file: {audio_file}")
            
            # Transcribe with Whisper
            result = self._model.transcribe(
                audio_file,
                language=self.config.language if self.config.language != "auto" else None
            )
            
            text = result.get("text", "").strip()
            logger.info(f"Transcription result: {text[:100]}...")
            
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    def transcribe_realtime(self, audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
        """
        Transcribe audio data in real-time.
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text or None if failed
        """
        if not self._model:
            logger.warning("STT model not available, cannot transcribe")
            return None

        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Write audio data
                import soundfile as sf
                import numpy as np
                
                # Convert bytes to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                sf.write(temp_path, audio_array, sample_rate)
                
                # Transcribe
                result = self.transcribe_file(temp_path)
                
                # Clean up
                Path(temp_path).unlink(missing_ok=True)
                
                return result
                
        except Exception as e:
            logger.error(f"Error transcribing realtime audio: {e}")
            return None

    def change_model(self, model_name: str) -> bool:
        """
        Change the Whisper model.
        
        Args:
            model_name: Model name (tiny, base, small, medium, large)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._whisper:
            return False

        try:
            logger.info(f"Changing model to: {model_name}")
            self.config.model = model_name
            self._load_model()
            return self._model is not None
            
        except Exception as e:
            logger.error(f"Error changing model: {e}")
            return False

    def get_available_models(self):
        """Get list of available Whisper models."""
        return ["tiny", "base", "small", "medium", "large"]

    def get_model_info(self):
        """Get information about the current model."""
        if not self._model:
            return None
            
        return {
            "name": self.config.model,
            "device": self.config.device,
            "language": self.config.language,
        }
