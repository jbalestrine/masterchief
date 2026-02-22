"""Tortoise TTS voice cloning implementation."""
from typing import List, Optional
import os
import logging
from .base import BaseVoiceCloner

logger = logging.getLogger(__name__)


class TortoiseCloner(BaseVoiceCloner):
    """Tortoise TTS voice cloning implementation.
    
    Highest quality voice cloning.
    Requires 1-3 minutes of voice samples.
    Slower inference but superior output.
    """
    
    def __init__(self, config):
        """Initialize Tortoise cloner.
        
        Args:
            config: VoiceCloningConfig instance
        """
        super().__init__(config)
        self.model_name = config.tortoise_model
        self.preset = config.tortoise_preset
    
    def load_model(self) -> None:
        """Load the Tortoise TTS model."""
        try:
            from tortoise.api import TextToSpeech
            logger.info(f"Loading Tortoise model with preset: {self.preset}")
            self.model = TextToSpeech(device=self.device)
            logger.info("Tortoise model loaded successfully")
        except ImportError as e:
            logger.error("tortoise-tts library not installed. Install with: pip install tortoise-tts")
            raise ImportError("tortoise-tts library required. Install with: pip install tortoise-tts") from e
        except Exception as e:
            logger.error(f"Error loading Tortoise model: {e}")
            raise
    
    def train_voice(
        self,
        name: str,
        audio_files: List[str],
        output_dir: str
    ) -> str:
        """Train a voice model from audio samples.
        
        For Tortoise, this prepares the conditioning samples directory.
        
        Args:
            name: Name of the voice profile
            audio_files: List of audio file paths for training
            output_dir: Directory to save the voice samples
            
        Returns:
            Path to the voice samples directory
        """
        if not self.validate_audio_files(audio_files):
            raise ValueError("Invalid audio files provided")
        
        # Create voice directory
        voice_dir = os.path.join(output_dir, name)
        os.makedirs(voice_dir, exist_ok=True)
        
        # Copy audio files to voice directory
        import shutil
        for i, audio_file in enumerate(audio_files):
            dest = os.path.join(voice_dir, f"sample_{i}.wav")
            shutil.copy(audio_file, dest)
        
        logger.info(f"Created Tortoise voice model: {voice_dir}")
        return voice_dir
    
    def synthesize_speech(
        self,
        text: str,
        model_path: str,
        output_file: Optional[str] = None
    ) -> bytes:
        """Generate speech using Tortoise TTS.
        
        Args:
            text: Text to synthesize
            model_path: Path to the voice samples directory
            output_file: Optional path to save audio file
            
        Returns:
            Audio data as bytes
        """
        if self.model is None:
            self.load_model()
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Voice directory not found: {model_path}")
        
        try:
            # Load conditioning samples
            voice_samples = [
                os.path.join(model_path, f)
                for f in os.listdir(model_path)
                if f.endswith('.wav')
            ]
            
            if not voice_samples:
                raise ValueError(f"No voice samples found in: {model_path}")
            
            # Generate speech
            gen = self.model.tts_with_preset(
                text=text,
                voice_samples=voice_samples,
                preset=self.preset
            )
            
            # Save to file if requested
            if output_file:
                import torchaudio
                os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
                torchaudio.save(output_file, gen.squeeze(0).cpu(), 24000)
                logger.info(f"Saved audio to: {output_file}")
            
            # Convert to bytes
            import io
            import torchaudio
            buffer = io.BytesIO()
            torchaudio.save(buffer, gen.squeeze(0).cpu(), 24000, format='wav')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error synthesizing speech with Tortoise: {e}")
            raise
    
    def get_required_sample_duration(self) -> int:
        """Get recommended sample duration for Tortoise.
        
        Returns:
            Recommended sample duration (60-180 seconds)
        """
        return 120  # 2 minutes
