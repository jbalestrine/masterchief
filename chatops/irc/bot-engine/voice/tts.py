"""Text-to-Speech engine."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech engine wrapper."""
    
    def __init__(self, config):
        """Initialize TTS engine."""
        self.config = config
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS backend."""
        try:
            if self.config.tts_engine == "pyttsx3":
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.config.tts_rate)
                self.engine.setProperty('volume', self.config.tts_volume)
                if self.config.tts_voice:
                    self.engine.setProperty('voice', self.config.tts_voice)
                logger.info("pyttsx3 TTS engine initialized")
            else:
                logger.warning(f"Unsupported TTS engine: {self.config.tts_engine}")
        except ImportError:
            logger.warning("pyttsx3 not installed, TTS will not work")
    
    def synthesize(self, text: str) -> bytes:
        """
        Convert text to audio data.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        if not self.engine:
            logger.error("TTS engine not initialized")
            return b""
        
        try:
            # For pyttsx3, we need to use a different approach
            # This is a placeholder - actual implementation would save to file/buffer
            import tempfile
            import wave
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_file = f.name
            
            self.engine.save_to_file(text, temp_file)
            self.engine.runAndWait()
            
            with open(temp_file, 'rb') as f:
                audio_data = f.read()
            
            import os
            os.unlink(temp_file)
            
            return audio_data
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return b""
    
    def speak_directly(self, text: str):
        """Speak text directly without returning audio data."""
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Direct speech failed: {e}")
