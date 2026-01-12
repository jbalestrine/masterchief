"""CLI for voice cloning system."""
import sys
import argparse
import logging
from pathlib import Path
import os

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Import modules directly from file paths due to hyphenated directory names
import importlib.util

def load_module(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load required modules
bot_engine_path = parent_dir / "chatops" / "irc" / "bot-engine"
voice_base = load_module("voice.base", bot_engine_path / "voice" / "base.py")
voice_profile_module = load_module("voice.cloning.voice_profile", bot_engine_path / "voice" / "cloning" / "voice_profile.py")
cloning_base = load_module("voice.cloning.base", bot_engine_path / "voice" / "cloning" / "base.py")
xtts = load_module("voice.cloning.xtts_cloner", bot_engine_path / "voice" / "cloning" / "xtts_cloner.py")
tortoise = load_module("voice.cloning.tortoise_cloner", bot_engine_path / "voice" / "cloning" / "tortoise_cloner.py")
openvoice = load_module("voice.cloning.openvoice_cloner", bot_engine_path / "voice" / "cloning" / "openvoice_cloner.py")
trainer = load_module("voice.cloning.trainer", bot_engine_path / "voice" / "cloning" / "trainer.py")
voice_cloner_module = load_module("voice.cloning.voice_cloner", bot_engine_path / "voice" / "cloning" / "voice_cloner.py")

VoiceCloningConfig = voice_base.VoiceCloningConfig
VoiceCloner = voice_cloner_module.VoiceCloner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_record_samples(args):
    """Record voice samples interactively."""
    config = VoiceCloningConfig(
        profiles_dir=args.profiles_dir,
        samples_dir=args.output,
        device=args.device
    )
    
    cloner = VoiceCloner(config)
    
    print("\n🎤 Voice Sample Recording")
    print("=" * 60)
    
    samples = cloner.record_samples(
        output_dir=args.output,
        num_samples=args.num_samples,
        duration=args.duration
    )
    
    print(f"\n✓ Recorded {len(samples)} samples to: {args.output}")


def cmd_create_master(args):
    """Create master voice from audio files."""
    config = VoiceCloningConfig(
        profiles_dir=args.profiles_dir,
        device=args.device,
        engine=args.engine
    )
    
    cloner = VoiceCloner(config)
    
    # Collect audio files
    audio_files = []
    for pattern in args.files:
        path = Path(pattern)
        if path.is_file():
            audio_files.append(str(path))
        else:
            # Handle glob patterns
            parent = path.parent if path.parent.exists() else Path('.')
            pattern_str = path.name
            audio_files.extend([str(p) for p in parent.glob(pattern_str)])
    
    if not audio_files:
        print(f"❌ No audio files found matching: {args.files}")
        sys.exit(1)
    
    print(f"\n🔊 Creating master voice: {args.name}")
    print(f"   Engine: {args.engine}")
    print(f"   Audio files: {len(audio_files)}")
    
    profile = cloner.create_master_voice(
        name=args.name,
        audio_files=audio_files,
        engine=args.engine
    )
    
    print(f"\n✓ Master voice created: {profile.name}")
    print(f"   Profile directory: {args.profiles_dir}")


def cmd_list_profiles(args):
    """List all voice profiles."""
    config = VoiceCloningConfig(
        profiles_dir=args.profiles_dir
    )
    
    cloner = VoiceCloner(config)
    profiles = cloner.list_profiles()
    
    if not profiles:
        print("\nNo voice profiles found.")
        return
    
    print("\n📋 Voice Profiles")
    print("=" * 60)
    
    for profile in profiles:
        master_badge = " 🎯 [MASTER]" if profile.is_master else ""
        print(f"\n  {profile.name}{master_badge}")
        print(f"    Engine: {profile.engine}")
        print(f"    Created: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Samples: {len(profile.sample_files)}")
        print(f"    Model: {profile.model_path}")


def cmd_test(args):
    """Test master voice synthesis."""
    config = VoiceCloningConfig(
        profiles_dir=args.profiles_dir,
        device=args.device
    )
    
    cloner = VoiceCloner(config)
    
    print(f"\n🔊 Testing master voice")
    print(f"   Text: {args.text}")
    
    output_file = args.output or "test_output.wav"
    
    try:
        cloner.speak_as_master(args.text, output_file=output_file)
        print(f"\n✓ Audio generated: {output_file}")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def cmd_set_master(args):
    """Set a profile as the master voice."""
    config = VoiceCloningConfig(
        profiles_dir=args.profiles_dir
    )
    
    cloner = VoiceCloner(config)
    
    try:
        cloner.set_master_voice(args.name)
        print(f"\n✓ Master voice set to: {args.name}")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MasterChief IRC Bot Voice Cloning CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global arguments
    parser.add_argument(
        '--profiles-dir',
        default='./voice_profiles/',
        help='Directory for voice profiles (default: ./voice_profiles/)'
    )
    parser.add_argument(
        '--device',
        default='auto',
        choices=['auto', 'cuda', 'cpu'],
        help='Device to use for inference (default: auto)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # record-samples command
    record_parser = subparsers.add_parser(
        'record-samples',
        help='Record voice samples interactively'
    )
    record_parser.add_argument(
        '--output',
        default='./voice_samples/',
        help='Output directory for recordings (default: ./voice_samples/)'
    )
    record_parser.add_argument(
        '--num-samples',
        type=int,
        default=5,
        help='Number of samples to record (default: 5)'
    )
    record_parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Duration of each sample in seconds (default: 10)'
    )
    
    # create-master command
    create_parser = subparsers.add_parser(
        'create-master',
        help='Create master voice from audio files'
    )
    create_parser.add_argument(
        '--name',
        required=True,
        help='Name for the master voice profile'
    )
    create_parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help='Audio files or glob patterns (e.g., samples/*.wav)'
    )
    create_parser.add_argument(
        '--engine',
        default='xtts',
        choices=['xtts', 'tortoise', 'openvoice'],
        help='Voice cloning engine (default: xtts)'
    )
    
    # list-profiles command
    list_parser = subparsers.add_parser(
        'list-profiles',
        help='List all voice profiles'
    )
    
    # test command
    test_parser = subparsers.add_parser(
        'test',
        help='Test master voice synthesis'
    )
    test_parser.add_argument(
        '--text',
        required=True,
        help='Text to synthesize'
    )
    test_parser.add_argument(
        '--output',
        help='Output audio file (default: test_output.wav)'
    )
    
    # set-master command
    set_parser = subparsers.add_parser(
        'set-master',
        help='Set a profile as the master voice'
    )
    set_parser.add_argument(
        '--name',
        required=True,
        help='Name of the profile to set as master'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        'record-samples': cmd_record_samples,
        'create-master': cmd_create_master,
        'list-profiles': cmd_list_profiles,
        'test': cmd_test,
        'set-master': cmd_set_master,
    }
    
    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception("Error executing command")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
