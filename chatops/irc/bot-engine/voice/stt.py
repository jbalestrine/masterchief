"""Speech-to-Text engine."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class STTEngine:
    """Speech-to-Text engine wrapper."""
    
    def __init__(self, config):
        """Initialize STT engine."""
        self.config = config
        self.model = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the STT backend."""
        try:
            if self.config.stt_engine == "whisper":
                import whisper
                self.model = whisper.load_model(self.config.stt_model)
                logger.info(f"Whisper STT model '{self.config.stt_model}' loaded")
            else:
                logger.warning(f"Unsupported STT engine: {self.config.stt_engine}")
        except ImportError:
            logger.warning("whisper not installed, STT will not work")
        except Exception as e:
            logger.error(f"Failed to load STT model: {e}")
    
    def transcribe(self, audio_data: bytes) -> str:
        """
        Convert audio to text.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        if not self.model:
            logger.error("STT model not initialized")
            return ""
        
        try:
            import tempfile
            import numpy as np
            
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_file = f.name
                f.write(audio_data)
            
            # Transcribe
            result = self.model.transcribe(
                temp_file,
                language=self.config.stt_language,
                fp16=False
            )
            
            import os
            os.unlink(temp_file)
            
            return result.get("text", "").strip()
        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return ""
