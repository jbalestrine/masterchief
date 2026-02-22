"""Text-to-Speech engine."""

import logging
"""Text-to-Speech engine using pyttsx3."""
import logging
import queue
import threading
from pathlib import Path
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
            import os
            
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    temp_file = f.name
                
                self.engine.save_to_file(text, temp_file)
                self.engine.runAndWait()
                
                with open(temp_file, 'rb') as f:
                    audio_data = f.read()
                
                return audio_data
            finally:
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
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
    """Text-to-speech engine using pyttsx3 for local TTS."""

    def __init__(self, config):
        """Initialize TTS engine."""
        self.config = config
        self._engine = None
        self._speech_queue = queue.Queue()
        self._worker_thread = None
        self._running = False
        self._lock = threading.Lock()
        
        # Try to import and initialize pyttsx3
        try:
            import pyttsx3
            self._pyttsx3 = pyttsx3
            self._initialize_engine()
            
            # Start worker thread for queue processing
            self._running = True
            self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self._worker_thread.start()
            
            logger.info("TTSEngine initialized successfully")
        except ImportError:
            logger.warning("pyttsx3 not installed, TTS will not be available")
            self._pyttsx3 = None
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            self._pyttsx3 = None

    def _initialize_engine(self):
        """Initialize the pyttsx3 engine with configuration."""
        if not self._pyttsx3:
            return

        try:
            self._engine = self._pyttsx3.init()
            
            # Set voice if specified
            if self.config.voice:
                voices = self._engine.getProperty('voices')
                for voice in voices:
                    if self.config.voice in voice.id or self.config.voice in voice.name:
                        self._engine.setProperty('voice', voice.id)
                        logger.info(f"Set voice to: {voice.name}")
                        break
            
            # Set rate (words per minute)
            self._engine.setProperty('rate', self.config.rate)
            
            # Set volume (0.0 to 1.0)
            self._engine.setProperty('volume', self.config.volume)
            
        except Exception as e:
            logger.error(f"Error configuring TTS engine: {e}")
            self._engine = None

    def _process_queue(self):
        """Worker thread to process speech queue."""
        while self._running:
            try:
                text, save_file = self._speech_queue.get(timeout=1)
                self._speak_internal(text, save_file)
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing speech queue: {e}")

    def _speak_internal(self, text: str, save_file: Optional[str] = None):
        """Internal method to perform actual speech synthesis."""
        if not self._engine:
            logger.warning("TTS engine not available")
            return

        try:
            with self._lock:
                if save_file:
                    # Save to file
                    output_path = Path(self.config.output_dir) / save_file
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    self._engine.save_to_file(text, str(output_path))
                    self._engine.runAndWait()
                    logger.info(f"Saved TTS to file: {output_path}")
                else:
                    # Speak directly
                    self._engine.say(text)
                    self._engine.runAndWait()
                    
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")

    def speak(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """
        Convert text to speech and play it (or save to file).
        
        Args:
            text: Text to convert to speech
            save_to_file: Optional filename to save audio
            
        Returns:
            True if queued successfully, False otherwise
        """
        if not self._engine:
            logger.warning("TTS engine not available, cannot speak")
            return False

        try:
            # Add to queue for processing
            self._speech_queue.put((text, save_to_file))
            logger.info(f"Queued speech: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing speech: {e}")
            return False

    def get_available_voices(self):
        """Get list of available voices."""
        if not self._engine:
            return []

        try:
            voices = self._engine.getProperty('voices')
            return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []

    def set_voice(self, voice_id: str) -> bool:
        """
        Change the voice used for TTS.
        
        Args:
            voice_id: Voice ID or name to use
            
        Returns:
            True if successful, False otherwise
        """
        if not self._engine:
            return False

        try:
            with self._lock:
                voices = self._engine.getProperty('voices')
                for voice in voices:
                    if voice_id in voice.id or voice_id in voice.name:
                        self._engine.setProperty('voice', voice.id)
                        self.config.voice = voice_id
                        logger.info(f"Changed voice to: {voice.name}")
                        return True
                        
                logger.warning(f"Voice not found: {voice_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False

    def set_rate(self, rate: int) -> bool:
        """
        Change speech rate.
        
        Args:
            rate: Words per minute (typically 100-200)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._engine:
            return False

        try:
            with self._lock:
                self._engine.setProperty('rate', rate)
                self.config.rate = rate
                logger.info(f"Changed speech rate to: {rate}")
                return True
                
        except Exception as e:
            logger.error(f"Error setting rate: {e}")
            return False

    def set_volume(self, volume: float) -> bool:
        """
        Change speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._engine:
            return False

        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to 0.0-1.0
            with self._lock:
                self._engine.setProperty('volume', volume)
                self.config.volume = volume
                logger.info(f"Changed volume to: {volume}")
                return True
                
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False

    def shutdown(self):
        """Shutdown the TTS engine and cleanup resources."""
        logger.info("Shutting down TTS engine")
        self._running = False
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2)
        
        if self._engine:
            try:
                self._engine.stop()
            except Exception as e:
                logger.error(f"Error stopping TTS engine: {e}")
