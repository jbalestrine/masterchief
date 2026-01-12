"""
Voice-to-Script Module
Generate scripts from voice commands using speech recognition
"""

import logging
from typing import Optional
from .ai_generator import AIScriptGenerator, GeneratedScript

logger = logging.getLogger(__name__)


class VoiceToScript:
    """Generate scripts from voice commands."""
    
    def __init__(self, voice_engine, generator: AIScriptGenerator):
        """
        Initialize Voice-to-Script.
        
        Args:
            voice_engine: Voice engine with STT/TTS capabilities
            generator: AI script generator instance
        """
        self.voice = voice_engine
        self.generator = generator
    
    def listen_and_generate(self, timeout: int = 30, language: str = "bash") -> Optional[GeneratedScript]:
        """
        Listen for voice description and generate script.
        
        Args:
            timeout: Maximum time to listen for voice input (seconds)
            language: Target script language
            
        Returns:
            GeneratedScript object or None if failed
        """
        try:
            # Announce that we're listening
            self.voice.speak("I'm listening for your script description. Please describe what you want the script to do.")
            
            # Listen for voice input
            description = self.voice.listen(duration=timeout)
            
            if not description or description.strip() == "":
                self.voice.speak("I didn't hear anything. Please try again.")
                return None
            
            # Confirm what we heard
            self.voice.speak(f"I heard: {description}. Generating script now.")
            
            # Generate script
            script = self.generator.generate(description, language=language)
            
            # Announce completion
            self.voice.speak(f"Script generated successfully. The script is named {script.name}")
            
            return script
            
        except Exception as e:
            logger.error(f"Voice-to-script generation failed: {e}")
            self.voice.speak(f"Sorry, I encountered an error: {str(e)}")
            return None
    
    def confirm_and_save(self, script: GeneratedScript, name: Optional[str] = None) -> bool:
        """
        Voice confirmation to save script.
        
        Args:
            script: Generated script to save
            name: Optional custom name for the script
            
        Returns:
            True if user confirmed and saved, False otherwise
        """
        try:
            # Ask if user wants to hear the script
            self.voice.speak("Would you like me to read back the script? Say yes or no.")
            
            response = self.voice.listen(duration=10)
            
            if response and ("yes" in response.lower() or "yeah" in response.lower()):
                # Read back the script (first 500 chars to avoid very long reads)
                preview = script.content[:500]
                self.voice.speak(f"Here's the script: {preview}")
                
                if len(script.content) > 500:
                    self.voice.speak("The script continues beyond this preview.")
            
            # Ask for confirmation to save
            save_name = name if name else script.name
            self.voice.speak(f"Should I save this script as {save_name}? Say yes to save or no to cancel.")
            
            response = self.voice.listen(duration=10)
            
            if response and ("yes" in response.lower() or "yeah" in response.lower() or "save" in response.lower()):
                self.voice.speak(f"Saving script as {save_name}")
                return True
            else:
                self.voice.speak("Script not saved.")
                return False
                
        except Exception as e:
            logger.error(f"Voice confirmation failed: {e}")
            self.voice.speak("Sorry, I encountered an error during confirmation.")
            return False
    
    def read_script(self, script: GeneratedScript) -> None:
        """
        Read a script back to the user via TTS.
        
        Args:
            script: Script to read back
        """
        try:
            self.voice.speak(f"Reading script {script.name}")
            
            # Read the script content in chunks
            lines = script.content.split("\n")
            
            # Read non-empty, non-comment lines
            content_lines = [
                line for line in lines 
                if line.strip() and not line.strip().startswith("#")
            ]
            
            if len(content_lines) > 10:
                # For long scripts, just read a summary
                self.voice.speak(f"This script has {len(lines)} lines. Here's a summary of the first few lines.")
                for line in content_lines[:5]:
                    self.voice.speak(line)
                self.voice.speak(f"And {len(content_lines) - 5} more lines.")
            else:
                # For short scripts, read the whole thing
                for line in content_lines:
                    self.voice.speak(line)
                    
        except Exception as e:
            logger.error(f"Failed to read script: {e}")
            self.voice.speak("Sorry, I couldn't read the script.")


class MockVoiceEngine:
    """Mock voice engine for testing when voice system is not available."""
    
    def __init__(self):
        self.responses = []
        self.spoken = []
    
    def speak(self, text: str) -> None:
        """Mock speak method."""
        self.spoken.append(text)
        print(f"[TTS] {text}")
    
    def listen(self, duration: int = 10) -> str:
        """Mock listen method."""
        if self.responses:
            response = self.responses.pop(0)
            print(f"[STT] Heard: {response}")
            return response
        return ""
    
    def set_responses(self, responses: list) -> None:
        """Set mock responses for testing."""
        self.responses = responses
