"""Voice profile management for cloned voices."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class VoiceProfile:
    """A cloned voice profile."""
    name: str
    engine: str  # xtts, tortoise, openvoice
    created_at: datetime
    sample_files: List[str]
    model_path: str  # Path to trained model/embeddings
    is_master: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization.
        
        Returns:
            Dictionary representation of the profile
        """
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceProfile':
        """Create profile from dictionary.
        
        Args:
            data: Dictionary with profile data
            
        Returns:
            VoiceProfile instance
        """
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)
    
    def save(self, profiles_dir: str) -> None:
        """Save profile to disk.
        
        Args:
            profiles_dir: Directory to save profile
        """
        os.makedirs(profiles_dir, exist_ok=True)
        profile_file = os.path.join(profiles_dir, f"{self.name}.json")
        
        with open(profile_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logger.info(f"Saved voice profile: {profile_file}")
    
    @classmethod
    def load(cls, profile_name: str, profiles_dir: str) -> 'VoiceProfile':
        """Load profile from disk.
        
        Args:
            profile_name: Name of the profile
            profiles_dir: Directory containing profiles
            
        Returns:
            VoiceProfile instance
        """
        profile_file = os.path.join(profiles_dir, f"{profile_name}.json")
        
        if not os.path.exists(profile_file):
            raise FileNotFoundError(f"Profile not found: {profile_file}")
        
        with open(profile_file, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded voice profile: {profile_file}")
        return cls.from_dict(data)
    
    def speak(self, text: str, cloner, output_file: Optional[str] = None) -> bytes:
        """Generate speech using this voice profile.
        
        Args:
            text: Text to synthesize
            cloner: VoiceCloner instance
            output_file: Optional path to save audio
            
        Returns:
            Audio data as bytes
        """
        return cloner._synthesize_with_profile(self, text, output_file)


class VoiceProfileManager:
    """Manages voice profiles."""
    
    def __init__(self, profiles_dir: str):
        """Initialize profile manager.
        
        Args:
            profiles_dir: Directory for storing profiles
        """
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
        logger.info(f"Voice profile manager initialized: {profiles_dir}")
    
    def list_profiles(self) -> List[VoiceProfile]:
        """List all saved voice profiles.
        
        Returns:
            List of VoiceProfile instances
        """
        profiles = []
        
        if not os.path.exists(self.profiles_dir):
            return profiles
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                profile_name = filename[:-5]  # Remove .json
                try:
                    profile = VoiceProfile.load(profile_name, self.profiles_dir)
                    profiles.append(profile)
                except Exception as e:
                    logger.error(f"Error loading profile {profile_name}: {e}")
        
        return profiles
    
    def get_profile(self, name: str) -> Optional[VoiceProfile]:
        """Get a specific profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            VoiceProfile or None if not found
        """
        try:
            return VoiceProfile.load(name, self.profiles_dir)
        except FileNotFoundError:
            return None
    
    def delete_profile(self, name: str) -> bool:
        """Delete a voice profile.
        
        Args:
            name: Profile name
            
        Returns:
            True if deleted successfully
        """
        profile_file = os.path.join(self.profiles_dir, f"{name}.json")
        
        if os.path.exists(profile_file):
            os.remove(profile_file)
            logger.info(f"Deleted voice profile: {name}")
            return True
        
        return False
    
    def get_master_voice(self) -> Optional[VoiceProfile]:
        """Get the profile marked as master voice.
        
        Returns:
            Master voice profile or None
        """
        for profile in self.list_profiles():
            if profile.is_master:
                return profile
        return None
    
    def set_master_voice(self, name: str) -> bool:
        """Set a profile as the master voice.
        
        Args:
            name: Profile name
            
        Returns:
            True if set successfully
        """
        # Unset any existing master voice
        for profile in self.list_profiles():
            if profile.is_master:
                profile.is_master = False
                profile.save(self.profiles_dir)
        
        # Set the new master voice
        profile = self.get_profile(name)
        if profile:
            profile.is_master = True
            profile.save(self.profiles_dir)
            logger.info(f"Set master voice: {name}")
            return True
        
        return False
