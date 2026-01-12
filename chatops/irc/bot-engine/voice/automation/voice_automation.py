"""Main voice automation controller."""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from ..base import VoiceEngine, VoiceConfig
from ..cloning import VoiceCloner
from .wake_word import WakeWordDetector
from .command_processor import CommandProcessor
from .conversation import ConversationManager
from .action_executor import ActionExecutor
from .response_builder import ResponseBuilder
from .feedback import AudioFeedback

logger = logging.getLogger(__name__)


@dataclass
class VoiceAutomationConfig:
    """Configuration for voice automation."""
    
    # Voice engine config
    voice_config: VoiceConfig
    
    # Wake word settings
    wake_words: list = None
    wake_word_engine: str = "openwakeword"
    wake_word_sensitivity: float = 0.5
    
    # Conversation settings
    conversation_timeout: int = 30
    conversation_context_window: int = 10
    confirm_critical: bool = True
    
    # Response settings
    use_master_voice: bool = False
    speak_confirmations: bool = True
    play_feedback_sounds: bool = True
    
    # LLM settings
    llm_model: str = "mistral"
    ollama_url: str = "http://localhost:11434"
    
    # Sounds directory
    sounds_dir: Optional[Path] = None
    
    def __post_init__(self):
        """Set defaults."""
        if self.wake_words is None:
            self.wake_words = ["hey masterchief", "hey chief", "okay masterchief"]


class VoiceAutomation:
    """Full voice automation controller."""
    
    def __init__(
        self,
        config: VoiceAutomationConfig,
        script_manager: Optional['ScriptManager'] = None
    ):
        """
        Initialize voice automation.
        
        Args:
            config: Voice automation configuration
            script_manager: Optional script manager instance
        """
        self.config = config
        self.script_manager = script_manager
        
        # Initialize components
        self.voice = VoiceEngine(config.voice_config)
        self.voice.initialize()
        
        self.cloner = VoiceCloner(self.voice) if config.use_master_voice else None
        
        self.wake_word = WakeWordDetector(
            wake_words=config.wake_words,
            engine=config.wake_word_engine,
            sensitivity=config.wake_word_sensitivity
        )
        
        self.command_processor = CommandProcessor(
            model=config.llm_model,
            ollama_url=config.ollama_url
        )
        
        self.conversation = ConversationManager(
            context_window=config.conversation_context_window,
            timeout=config.conversation_timeout
        )
        
        self.response_builder = ResponseBuilder()
        self.executor = ActionExecutor(self)
        
        self.feedback = AudioFeedback(
            sounds_dir=config.sounds_dir,
            player=self.voice.player
        )
        
        if not config.play_feedback_sounds:
            self.feedback.disable()
        
        # State
        self.is_listening = False
        self.is_active = False  # True after wake word detected
        self._listen_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        logger.info("VoiceAutomation initialized")
    
    def start(self):
        """Start voice automation (always-on listening)."""
        if self.is_listening:
            logger.warning("Voice automation already running")
            return
        
        self.is_listening = True
        self._stop_event.clear()
        
        logger.info("Starting voice automation...")
        
        while self.is_listening and not self._stop_event.is_set():
            # Passive listening for wake word
            logger.debug("Listening for wake word...")
            
            # In a real implementation, this would continuously monitor audio
            # For now, we'll just sleep and check periodically
            time.sleep(1)
            
            # Check if wake word was detected
            # (In production, this would be event-driven)
            if self._check_for_wake_word():
                self._on_wake()
        
        logger.info("Voice automation stopped")
    
    def start_async(self):
        """Start voice automation in background thread."""
        if self._listen_thread and self._listen_thread.is_alive():
            logger.warning("Voice automation already running")
            return
        
        self._listen_thread = threading.Thread(target=self.start, daemon=True)
        self._listen_thread.start()
        logger.info("Voice automation started in background")
    
    def _check_for_wake_word(self) -> bool:
        """Check for wake word (placeholder)."""
        # In production, this would use actual wake word detection
        # For now, return False to prevent automatic activation
        return False
    
    def _on_wake(self):
        """Handle wake word detection."""
        logger.info("Wake word detected!")
        
        if self.config.play_feedback_sounds:
            self.feedback.play_wake()
        
        self.is_active = True
        self.conversation.clear()
        
        if self.config.speak_confirmations:
            self.speak("Listening...")
        
        self._conversation_loop()
    
    def _conversation_loop(self):
        """Main conversation loop after wake word."""
        while self.is_active and not self._stop_event.is_set():
            # Listen for command
            logger.debug("Listening for command...")
            audio = self.voice.listen(timeout=10)
            
            if not audio:
                logger.debug("No audio received")
                
                if self.conversation.is_expired():
                    logger.info("Conversation timeout")
                    self.speak("I didn't hear anything. Going back to sleep.")
                    self.is_active = False
                    if self.config.play_feedback_sounds:
                        self.feedback.play_sleep()
                    break
                else:
                    self.speak("I didn't catch that. Still listening...")
                    continue
            
            # Process command
            try:
                text = self.voice.transcribe(audio)
                logger.info(f"Transcribed: {text}")
                
                if not text or len(text.strip()) < 2:
                    self.speak("I didn't understand that. Could you repeat?")
                    continue
                
                # Check for end conversation
                if self.conversation.should_end_conversation(text):
                    self.speak("Standing by.")
                    self.is_active = False
                    if self.config.play_feedback_sounds:
                        self.feedback.play_sleep()
                    break
                
                response = self._process_command(text)
                
                # Respond in master voice
                self.speak_as_master(response)
                
            except Exception as e:
                logger.error(f"Error in conversation loop: {e}", exc_info=True)
                self.speak("I encountered an error. Please try again.")
    
    def _process_command(self, text: str) -> str:
        """
        Process a voice command and return response.
        
        Args:
            text: Transcribed command text
            
        Returns:
            Response text
        """
        try:
            # Parse intent
            intent = self.command_processor.parse(text, self.conversation.context)
            logger.info(f"Parsed intent: {intent.name} (confidence: {intent.confidence})")
            
            # Check for stop listening intent
            if intent.name == "stop_listening":
                return "Standing by. Say the wake word to activate me again."
            
            if self.config.play_feedback_sounds:
                self.feedback.play_processing()
            
            # Execute action
            result = self.executor.execute(intent)
            
            # Build natural response
            response = self.response_builder.build(intent, result)
            
            # Update conversation context
            self.conversation.add_turn(text, response)
            
            if result.success and self.config.play_feedback_sounds:
                self.feedback.play_success()
            elif not result.success and self.config.play_feedback_sounds:
                self.feedback.play_error()
            
            return response
            
        except Exception as e:
            logger.error(f"Command processing error: {e}", exc_info=True)
            return f"I encountered an error processing that command: {e}"
    
    def speak_as_master(self, text: str, blocking: bool = True):
        """
        Speak using the cloned master voice.
        
        Args:
            text: Text to speak
            blocking: Wait for speech to complete
        """
        if self.cloner and self.config.use_master_voice:
            self.cloner.speak_as_master(text, blocking=blocking)
        else:
            self.speak(text, blocking=blocking)
    
    def speak(self, text: str, blocking: bool = True):
        """
        Speak using default voice.
        
        Args:
            text: Text to speak
            blocking: Wait for speech to complete
        """
        logger.info(f"Speaking: {text[:100]}...")
        self.voice.speak(text, blocking=blocking)
    
    def play_chime(self, chime_type: str):
        """
        Play audio feedback.
        
        Args:
            chime_type: Type of chime (wake, sleep, etc.)
        """
        self.feedback.play(chime_type)
    
    def stop(self):
        """Stop voice automation."""
        logger.info("Stopping voice automation...")
        self.is_listening = False
        self.is_active = False
        self._stop_event.set()
        
        if self._listen_thread:
            self._listen_thread.join(timeout=2)
        
        logger.info("Voice automation stopped")
    
    def trigger_wake_manually(self):
        """Manually trigger wake word activation (for testing/IRC)."""
        if not self.is_listening:
            logger.warning("Voice automation not running")
            return
        
        logger.info("Manual wake trigger")
        self._on_wake()
    
    def process_text_command(self, text: str) -> str:
        """
        Process a text command (for IRC integration).
        
        Args:
            text: Command text
            
        Returns:
            Response text
        """
        return self._process_command(text)
