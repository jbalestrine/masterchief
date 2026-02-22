"""Master voice cloning system."""
from typing import List, Optional
from datetime import datetime
import os
import logging

from ..base import VoiceCloningConfig
from .voice_profile import VoiceProfile, VoiceProfileManager
from .xtts_cloner import XTTSCloner
from .tortoise_cloner import TortoiseCloner
from .openvoice_cloner import OpenVoiceCloner
from .trainer import VoiceTrainer

logger = logging.getLogger(__name__)


class VoiceCloner:
    """Master voice cloning system.
    
    Orchestrates multiple voice cloning engines (XTTS, Tortoise, OpenVoice)
    and manages voice profiles.
    """
    
    def __init__(self, config: VoiceCloningConfig):
        """Initialize the voice cloner.
        
        Args:
            config: VoiceCloningConfig instance
        """
        self.config = config
        self.profiles = VoiceProfileManager(config.profiles_dir)
        self.master_voice: Optional[VoiceProfile] = None
        
        # Initialize cloning engines
        self.xtts = XTTSCloner(config)
        self.tortoise = TortoiseCloner(config)
        self.openvoice = OpenVoiceCloner(config)
        
        # Load master voice if configured
        if config.master_voice_name:
            try:
                self.master_voice = self.profiles.get_profile(config.master_voice_name)
                if self.master_voice:
                    logger.info(f"Loaded master voice: {config.master_voice_name}")
            except Exception as e:
                logger.warning(f"Could not load master voice: {e}")
        
        logger.info("Voice cloner initialized")
    
    def _get_cloner(self, engine: str):
        """Get the appropriate cloner for the engine.
        
        Args:
            engine: Engine name (xtts, tortoise, openvoice)
            
        Returns:
            Cloner instance
        """
        if engine == "xtts":
            return self.xtts
        elif engine == "tortoise":
            return self.tortoise
        elif engine == "openvoice":
            return self.openvoice
        else:
            raise ValueError(f"Unknown engine: {engine}")
    
    def create_master_voice(
        self,
        name: str,
        audio_files: List[str],
        engine: str = "xtts"
    ) -> VoiceProfile:
        """Create the master voice profile from audio samples.
        
        This becomes the bot's primary persona voice.
        
        Args:
            name: Name for the master voice profile
            audio_files: List of audio file paths for training
            engine: Engine to use (xtts, tortoise, or openvoice)
            
        Returns:
            Created VoiceProfile
        """
        logger.info(f"Creating master voice '{name}' with {engine}")
        
        # Create the voice profile
        profile = self.clone_voice(name, audio_files, engine)
        
        # Set as master voice
        self.set_master_voice(name)
        
        return profile
    
    def set_master_voice(self, profile_name: str) -> None:
        """Set the active master voice for the bot.
        
        Args:
            profile_name: Name of the profile to set as master
        """
        if self.profiles.set_master_voice(profile_name):
            self.master_voice = self.profiles.get_profile(profile_name)
            logger.info(f"Master voice set to: {profile_name}")
        else:
            raise ValueError(f"Profile not found: {profile_name}")
    
    def speak_as_master(self, text: str, output_file: Optional[str] = None) -> bytes:
        """Speak using the master voice persona.
        
        Args:
            text: Text to synthesize
            output_file: Optional path to save audio
            
        Returns:
            Audio data as bytes
        """
        if self.master_voice is None:
            master = self.profiles.get_master_voice()
            if master is None:
                raise ValueError("No master voice configured")
            self.master_voice = master
        
        return self._synthesize_with_profile(self.master_voice, text, output_file)
    
    def clone_voice(
        self,
        name: str,
        audio_files: List[str],
        engine: str = "xtts"
    ) -> VoiceProfile:
        """Clone a voice and save as a profile.
        
        Args:
            name: Name for the voice profile
            audio_files: List of audio file paths for training
            engine: Engine to use (xtts, tortoise, or openvoice)
            
        Returns:
            Created VoiceProfile
        """
        logger.info(f"Cloning voice '{name}' with {engine} engine")
        
        # Validate audio files
        if not audio_files:
            raise ValueError("No audio files provided")
        
        # Get the appropriate cloner
        cloner = self._get_cloner(engine)
        
        # Create output directory for this profile
        profile_dir = os.path.join(self.config.profiles_dir, name)
        os.makedirs(profile_dir, exist_ok=True)
        
        # Train the voice model
        model_path = cloner.train_voice(name, audio_files, profile_dir)
        
        # Create voice profile
        profile = VoiceProfile(
            name=name,
            engine=engine,
            created_at=datetime.now(),
            sample_files=audio_files.copy(),
            model_path=model_path,
            is_master=False,
            metadata={
                "num_samples": len(audio_files),
                "cloner_class": cloner.__class__.__name__
            }
        )
        
        # Save profile
        profile.save(self.config.profiles_dir)
        
        logger.info(f"Voice profile created: {name}")
        return profile
    
    def list_profiles(self) -> List[VoiceProfile]:
        """List all saved voice profiles.
        
        Returns:
            List of VoiceProfile instances
        """
        return self.profiles.list_profiles()
    
    def record_samples(
        self,
        output_dir: str,
        prompts: Optional[List[str]] = None,
        num_samples: int = 5,
        duration: int = 10
    ) -> List[str]:
        """Interactive recording session for voice samples.
        
        Args:
            output_dir: Directory to save recordings
            prompts: Optional list of text prompts to read
            num_samples: Number of samples to record
            duration: Duration of each recording in seconds
            
        Returns:
            List of recorded audio file paths
        """
        return VoiceTrainer.record_samples(output_dir, prompts, num_samples, duration)
    
    def _synthesize_with_profile(
        self,
        profile: VoiceProfile,
        text: str,
        output_file: Optional[str] = None
    ) -> bytes:
        """Synthesize speech using a voice profile.
        
        Args:
            profile: VoiceProfile to use
            text: Text to synthesize
            output_file: Optional path to save audio
            
        Returns:
            Audio data as bytes
        """
        cloner = self._get_cloner(profile.engine)
        return cloner.synthesize_speech(text, profile.model_path, output_file)
    
    def delete_profile(self, name: str) -> bool:
        """Delete a voice profile.
        
        Args:
            name: Profile name
            
        Returns:
            True if deleted successfully
        """
        return self.profiles.delete_profile(name)
    
    def get_profile(self, name: str) -> Optional[VoiceProfile]:
        """Get a specific voice profile.
        
        Args:
            name: Profile name
            
        Returns:
            VoiceProfile or None
        """
        return self.profiles.get_profile(name)
