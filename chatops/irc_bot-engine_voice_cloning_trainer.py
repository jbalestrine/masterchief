"""Voice training utilities."""
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class VoiceTrainer:
    """Utilities for training voice models."""
    
    @staticmethod
    def record_samples(
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
        os.makedirs(output_dir, exist_ok=True)
        
        default_prompts = [
            "Hello, I am the MasterChief bot, your DevOps assistant.",
            "Deployment to production has completed successfully.",
            "Warning: High CPU usage detected on the main server.",
            "All systems are operational and running smoothly.",
            "An error has occurred. Please check the logs for details.",
            "The build process has started and is now in progress.",
            "Database backup completed without any issues.",
            "Network latency is within acceptable parameters.",
        ]
        
        if prompts is None:
            prompts = default_prompts[:num_samples]
        
        recorded_files = []
        
        try:
            import sounddevice as sd
            import scipy.io.wavfile as wavfile
            import numpy as np
            
            sample_rate = 22050
            
            print("\n" + "="*60)
            print("Voice Sample Recording Session")
            print("="*60)
            print(f"\nYou will record {num_samples} samples.")
            print(f"Each recording will be {duration} seconds long.")
            print("\nPress Enter when ready to start each recording...")
            
            for i, prompt in enumerate(prompts[:num_samples], 1):
                print(f"\n--- Sample {i}/{num_samples} ---")
                print(f"Read the following text:\n")
                print(f'  "{prompt}"\n')
                
                input("Press Enter to start recording...")
                print(f"Recording for {duration} seconds...")
                
                # Record audio
                recording = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype=np.float32
                )
                sd.wait()  # Wait until recording is finished
                
                # Save to file
                filename = f"sample_{i:02d}.wav"
                filepath = os.path.join(output_dir, filename)
                wavfile.write(filepath, sample_rate, recording)
                recorded_files.append(filepath)
                
                print(f"✓ Saved: {filepath}")
            
            print("\n" + "="*60)
            print(f"Recording complete! {len(recorded_files)} samples saved.")
            print(f"Location: {output_dir}")
            print("="*60 + "\n")
            
            return recorded_files
            
        except ImportError as e:
            logger.error("sounddevice library required for recording. Install with: pip install sounddevice")
            raise ImportError("sounddevice required for recording. Install with: pip install sounddevice scipy") from e
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            raise
    
    @staticmethod
    def validate_samples(audio_files: List[str], min_duration: int = 5) -> bool:
        """Validate recorded audio samples.
        
        Args:
            audio_files: List of audio file paths
            min_duration: Minimum required duration in seconds
            
        Returns:
            True if all samples are valid
        """
        try:
            import scipy.io.wavfile as wavfile
            
            for filepath in audio_files:
                if not os.path.exists(filepath):
                    logger.error(f"File not found: {filepath}")
                    return False
                
                # Read audio file
                sample_rate, audio_data = wavfile.read(filepath)
                duration = len(audio_data) / sample_rate
                
                if duration < min_duration:
                    logger.error(f"Sample too short: {filepath} ({duration:.1f}s < {min_duration}s)")
                    return False
                
                logger.info(f"Valid sample: {filepath} ({duration:.1f}s)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating samples: {e}")
            return False
    
    @staticmethod
    def preprocess_audio(
        input_file: str,
        output_file: str,
        target_sample_rate: int = 22050,
        normalize: bool = True
    ) -> str:
        """Preprocess audio file for training.
        
        Args:
            input_file: Input audio file path
            output_file: Output audio file path
            target_sample_rate: Target sample rate
            normalize: Whether to normalize audio
            
        Returns:
            Path to preprocessed audio file
        """
        try:
            import librosa
            import soundfile as sf
            
            # Load audio
            audio, sr = librosa.load(input_file, sr=target_sample_rate)
            
            # Normalize if requested
            if normalize:
                audio = librosa.util.normalize(audio)
            
            # Save preprocessed audio
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            sf.write(output_file, audio, target_sample_rate)
            
            logger.info(f"Preprocessed audio saved: {output_file}")
            return output_file
            
        except ImportError as e:
            logger.error("librosa library required. Install with: pip install librosa soundfile")
            raise ImportError("librosa required for preprocessing. Install with: pip install librosa soundfile") from e
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            raise
