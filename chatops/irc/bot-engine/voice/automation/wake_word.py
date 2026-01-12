"""Wake word detection for voice automation."""

import logging
import time
from typing import List, Optional
import threading

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Detect wake words using local models."""
    
    SUPPORTED_ENGINES = ["openwakeword", "porcupine", "whisper"]
    
    def __init__(self, wake_words: List[str], engine: str = "openwakeword", sensitivity: float = 0.5):
        """
        Initialize wake word detector.
        
        Args:
            wake_words: List of wake words to detect
            engine: Detection engine (openwakeword, porcupine, whisper)
            sensitivity: Detection sensitivity (0.0-1.0)
        """
        self.wake_words = [w.lower() for w in wake_words]
        self.engine_name = engine
        self.sensitivity = sensitivity
        self.engine = None
        self.is_listening = False
        self._stop_event = threading.Event()
        
        logger.info(f"Initializing wake word detector with engine: {engine}")
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize wake word detection engine."""
        try:
            if self.engine_name == "openwakeword":
                self._init_openwakeword()
            elif self.engine_name == "porcupine":
                self._init_porcupine()
            elif self.engine_name == "whisper":
                self._init_whisper()
            else:
                logger.error(f"Unsupported wake word engine: {self.engine_name}")
        except ImportError as e:
            logger.error(f"Failed to import wake word engine {self.engine_name}: {e}")
            logger.info("Falling back to simple text matching")
            self.engine_name = "simple"
    
    def _init_openwakeword(self):
        """Initialize OpenWakeWord engine."""
        try:
            from openwakeword import Model
            self.engine = Model(wakeword_models=self.wake_words)
            logger.info("OpenWakeWord engine initialized")
        except ImportError:
            logger.warning("openwakeword not installed")
            raise
    
    def _init_porcupine(self):
        """Initialize Porcupine engine."""
        try:
            import pvporcupine
            self.engine = pvporcupine.create(keywords=self.wake_words)
            logger.info("Porcupine engine initialized")
        except ImportError:
            logger.warning("pvporcupine not installed")
            raise
    
    def _init_whisper(self):
        """Initialize Whisper-based detection."""
        try:
            import whisper
            self.engine = whisper.load_model("tiny")
            logger.info("Whisper engine initialized for wake word detection")
        except ImportError:
            logger.warning("whisper not installed")
            raise
    
    def detect(self, timeout: Optional[float] = None) -> bool:
        """
        Listen for wake word.
        
        Args:
            timeout: Maximum time to listen (None for indefinite)
            
        Returns:
            True if wake word detected
        """
        if self.engine_name == "simple":
            return self._detect_simple(timeout)
        
        # Placeholder for actual detection
        logger.warning("Wake word detection not fully implemented")
        return False
    
    def _detect_simple(self, timeout: Optional[float] = None) -> bool:
        """Simple text-based wake word detection (for testing)."""
        logger.info("Using simple wake word detection (testing mode)")
        
        start_time = time.time()
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            # In real implementation, this would listen to audio
            # For now, just return False after a short delay
            time.sleep(0.1)
            
            # Check for stop signal
            if self._stop_event.is_set():
                return False
        
        return False
    
    def detect_in_audio(self, audio_data: bytes) -> bool:
        """
        Check if wake word is in audio data.
        
        Args:
            audio_data: Audio bytes to analyze
            
        Returns:
            True if wake word detected
        """
        if not self.engine:
            return False
        
        try:
            if self.engine_name == "whisper":
                # Use Whisper to transcribe and check for wake word
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    f.write(audio_data)
                    temp_file = f.name
                
                result = self.engine.transcribe(temp_file)
                text = result.get("text", "").lower()
                
                import os
                os.unlink(temp_file)
                
                for wake_word in self.wake_words:
                    if wake_word in text:
                        logger.info(f"Wake word detected: {wake_word}")
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Wake word detection error: {e}")
            return False
    
    def detect_in_text(self, text: str) -> bool:
        """
        Check if wake word is in text.
        
        Args:
            text: Text to check
            
        Returns:
            True if wake word found
        """
        text = text.lower()
        for wake_word in self.wake_words:
            if wake_word in text:
                logger.info(f"Wake word detected in text: {wake_word}")
                return True
        return False
    
    def add_wake_word(self, word: str):
        """Add a new wake word."""
        word = word.lower()
        if word not in self.wake_words:
            self.wake_words.append(word)
            logger.info(f"Added wake word: {word}")
    
    def remove_wake_word(self, word: str):
        """Remove a wake word."""
        word = word.lower()
        if word in self.wake_words:
            self.wake_words.remove(word)
            logger.info(f"Removed wake word: {word}")
    
    def stop(self):
        """Stop wake word detection."""
        self._stop_event.set()
        self.is_listening = False
