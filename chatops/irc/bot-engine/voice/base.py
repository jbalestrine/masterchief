"""Base configuration classes for voice system."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class VoiceConfig:
    """Base voice system configuration."""
    enabled: bool = True
    sample_rate: int = 22050
    device: str = "auto"  # cuda, cpu, or auto
    output_dir: str = "./voice_output/"


@dataclass
class VoiceCloningConfig:
    """Configuration for voice cloning system."""
    enabled: bool = True
    profiles_dir: str = "./voice_profiles/"
    samples_dir: str = "./voice_samples/"
    device: str = "auto"  # cuda, cpu, or auto
    engine: str = "xtts"  # xtts, tortoise, or openvoice
    
    # XTTS specific settings
    xtts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    # Tortoise specific settings
    tortoise_model: str = "tortoise-tts"
    tortoise_preset: str = "fast"  # ultra_fast, fast, standard, high_quality
    
    # OpenVoice specific settings
    openvoice_model: str = "openvoice"
    
    # Master voice settings
    master_voice_name: Optional[str] = None
    
    # Additional settings
    metadata: Dict[str, Any] = field(default_factory=dict)
