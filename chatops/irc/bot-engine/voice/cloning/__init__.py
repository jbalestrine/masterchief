"""Voice cloning system for MasterChief IRC Bot."""
import sys
import os

# Add parent to path for relative imports when loaded as script
if __name__ == '__main__' or not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .voice_cloner import VoiceCloner
    from .voice_profile import VoiceProfile
    from .base import BaseVoiceCloner
except ImportError:
    # Fallback for when module is loaded differently
    VoiceCloner = None
    VoiceProfile = None
    BaseVoiceCloner = None

__all__ = ["VoiceCloner", "VoiceProfile", "BaseVoiceCloner"]
