"""XTTS/Coqui TTS voice cloning implementation."""
from typing import List, Optional
import os
import logging
from .base import BaseVoiceCloner

logger = logging.getLogger(__name__)


class XTTSCloner(BaseVoiceCloner):
    """XTTS/Coqui TTS voice cloning implementation.
    
    Best balance of quality and speed.
    Requires only 6-10 seconds of voice samples.
    """
    
    def __init__(self, config):
        """Initialize XTTS cloner.
        
        Args:
            config: VoiceCloningConfig instance
        """
        super().__init__(config)
        self.model_name = config.xtts_model
    
    def load_model(self) -> None:
        """Load the XTTS model."""
        try:
            from TTS.api import TTS
            logger.info(f"Loading XTTS model: {self.model_name}")
            self.model = TTS(self.model_name).to(self.device)
            logger.info("XTTS model loaded successfully")
        except ImportError as e:
            logger.error("TTS library not installed. Install with: pip install TTS")
            raise ImportError("TTS library required for XTTS. Install with: pip install TTS") from e
        except Exception as e:
            logger.error(f"Error loading XTTS model: {e}")
            raise
    
    def train_voice(
        self,
        name: str,
        audio_files: List[str],
        output_dir: str
    ) -> str:
        """Train a voice model from audio samples.
        
        For XTTS, this processes and saves speaker embeddings.
        
        Args:
            name: Name of the voice profile
            audio_files: List of audio file paths for training
            output_dir: Directory to save the trained model
            
        Returns:
            Path to the trained model (speaker wav file)
        """
        if not self.validate_audio_files(audio_files):
            raise ValueError("Invalid audio files provided")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # XTTS uses the first audio file as the speaker reference
        # In practice, you might want to concatenate or use the best quality sample
        speaker_wav = audio_files[0]
        
        # Copy the speaker wav to the output directory
        import shutil
        model_path = os.path.join(output_dir, f"{name}_speaker.wav")
        shutil.copy(speaker_wav, model_path)
        
        logger.info(f"Created XTTS voice model: {model_path}")
        return model_path
    
    def synthesize_speech(
        self,
        text: str,
        model_path: str,
        output_file: Optional[str] = None
    ) -> bytes:
        """Generate speech using XTTS.
        
        Args:
            text: Text to synthesize
            model_path: Path to the speaker wav file
            output_file: Optional path to save audio file
            
        Returns:
            Audio data as bytes
        """
        if self.model is None:
            self.load_model()
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Speaker wav not found: {model_path}")
        
        try:
            # Generate speech using the speaker wav
            wav = self.model.tts(
                text=text,
                speaker_wav=model_path,
                language="en"
            )
            
            # Save to file if requested
            if output_file:
                import scipy.io.wavfile as wavfile
                import numpy as np
                os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
                wavfile.write(output_file, 22050, np.array(wav, dtype=np.float32))
                logger.info(f"Saved audio to: {output_file}")
            
            # Convert to bytes
            import io
            import scipy.io.wavfile as wavfile
            import numpy as np
            buffer = io.BytesIO()
            wavfile.write(buffer, 22050, np.array(wav, dtype=np.float32))
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error synthesizing speech with XTTS: {e}")
            raise
    
    def get_required_sample_duration(self) -> int:
        """Get recommended sample duration for XTTS.
        
        Returns:
            Recommended sample duration (6-10 seconds)
        """
        return 10
