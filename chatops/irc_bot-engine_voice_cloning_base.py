"""Base interface for voice cloning engines."""
from abc import ABC, abstractmethod
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseVoiceCloner(ABC):
    """Abstract base class for voice cloning implementations."""
    
    def __init__(self, config):
        """Initialize the voice cloner.
        
        Args:
            config: VoiceCloningConfig instance
        """
        self.config = config
        self.device = self._get_device()
        self.model = None
        logger.info(f"Initializing {self.__class__.__name__} on device: {self.device}")
    
    def _get_device(self) -> str:
        """Determine the device to use (cuda/cpu).
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if self.config.device == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return self.config.device
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the voice cloning model."""
        pass
    
    @abstractmethod
    def train_voice(
        self,
        name: str,
        audio_files: List[str],
        output_dir: str
    ) -> str:
        """Train a voice model from audio samples.
        
        Args:
            name: Name of the voice profile
            audio_files: List of audio file paths for training
            output_dir: Directory to save the trained model
            
        Returns:
            Path to the trained model
        """
        pass
    
    @abstractmethod
    def synthesize_speech(
        self,
        text: str,
        model_path: str,
        output_file: Optional[str] = None
    ) -> bytes:
        """Generate speech using a trained voice model.
        
        Args:
            text: Text to synthesize
            model_path: Path to the trained voice model
            output_file: Optional path to save audio file
            
        Returns:
            Audio data as bytes
        """
        pass
    
    def validate_audio_files(self, audio_files: List[str]) -> bool:
        """Validate that audio files exist and are readable.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            True if all files are valid
        """
        import os
        for file_path in audio_files:
            if not os.path.exists(file_path):
                logger.error(f"Audio file not found: {file_path}")
                return False
            if not os.path.isfile(file_path):
                logger.error(f"Not a file: {file_path}")
                return False
        return True
    
    def get_required_sample_duration(self) -> int:
        """Get recommended sample duration in seconds.
        
        Returns:
            Recommended sample duration
        """
        # Default implementation, override in subclasses
        return 30
