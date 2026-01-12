"""
Voice Cloning Example for MasterChief IRC Bot

This example shows how to clone your voice and use it as the bot's persona.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import using relative path since directory has hyphens
import importlib.util

def load_module_from_path(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
base_path = Path(__file__).parent.parent.parent / "chatops" / "irc" / "bot-engine"
voice_base = load_module_from_path("voice.base", base_path / "voice" / "base.py")
voice_cloning = load_module_from_path("voice.cloning", base_path / "voice" / "cloning" / "__init__.py")
bot_module = load_module_from_path("bot_engine", base_path / "__init__.py")

VoiceCloningConfig = voice_base.VoiceCloningConfig
VoiceCloner = voice_cloning.VoiceCloner
create_bot = bot_module.create_bot


def main():
    """Example usage of voice cloning with IRC bot."""
    
    # Configure voice cloning
    config = VoiceCloningConfig(
        profiles_dir="./voice_profiles/",
        samples_dir="./voice_samples/",
        engine="xtts",
        device="auto"
    )
    
    cloner = VoiceCloner(config)
    
    # Option 1: Record samples interactively
    print("Let's record your voice samples...")
    print("(You can skip this if you already have audio files)")
    
    # Uncomment to record samples interactively:
    # samples = cloner.record_samples(
    #     output_dir="./my_samples/",
    #     num_samples=5,
    #     duration=10
    # )
    
    # Option 2: Use existing audio files
    samples = [
        "voice1.wav",
        "voice2.wav",
        "voice3.wav"
    ]
    
    print("\nNote: Update the 'samples' list above with your actual audio files.")
    print("For this example, we'll assume you have sample audio files.\n")
    
    # Create your master voice
    try:
        profile = cloner.create_master_voice(
            name="my-master-voice",
            audio_files=samples,
            engine="xtts"
        )
        
        print(f"✓ Master voice '{profile.name}' created!")
        
        # Test it out
        print("\nTesting the master voice...")
        cloner.speak_as_master(
            "Hello! I am now speaking in your voice.",
            output_file="test_master_voice.wav"
        )
        print("✓ Test audio saved to: test_master_voice.wav")
        
    except Exception as e:
        print(f"Note: To use this example, you need to have audio samples ready.")
        print(f"Error: {e}")
        print("\nTo get started:")
        print("1. Record voice samples using the CLI:")
        print("   python -m chatops.irc.bot_engine.voice.cloning record-samples")
        print("2. Or provide your own .wav files")
        return
    
    # Use with the IRC bot
    print("\n" + "="*60)
    print("IRC Bot Integration Example")
    print("="*60)
    
    # Create IRC bot
    bot = create_bot(
        server="irc.libera.chat",
        port=6667,
        nickname="masterchief",
        channels=["#devops"]
    )
    
    # Define handler that uses voice cloning
    def announce_handler(connection, event, args):
        """Announce a message with voice."""
        if not args:
            connection.privmsg(event.target, "Usage: !announce <message>")
            return
        
        message = " ".join(args)
        
        # Speak the message using master voice
        try:
            cloner.speak_as_master(message, output_file=f"announcements/{event.source.nick}.wav")
            connection.privmsg(event.target, f"🔊 {message}")
        except Exception as e:
            connection.privmsg(event.target, f"Error: {e}")
    
    def deploy_handler(connection, event, args):
        """Deployment handler with voice feedback."""
        env = args[0] if args else "production"
        msg = f"Deployment to {env} initiated. Standing by."
        
        # Announce deployment with voice
        try:
            cloner.speak_as_master(msg)
            connection.privmsg(event.target, msg)
        except Exception as e:
            connection.privmsg(event.target, f"Deployment started (voice unavailable: {e})")
    
    def status_handler(connection, event, args):
        """Status check with voice response."""
        msg = "All systems operational."
        
        try:
            cloner.speak_as_master(msg)
            connection.privmsg(event.target, f"✓ {msg}")
        except Exception as e:
            connection.privmsg(event.target, f"✓ {msg} (voice unavailable)")
    
    # Bind commands to the bot
    bot.bind("pub", "-|-", "!announce", announce_handler)
    bot.bind("pub", "-|-", "!deploy", deploy_handler)
    bot.bind("pub", "-|-", "!status", status_handler)
    
    print("\nBot configured with voice cloning!")
    print("Commands available:")
    print("  !announce <message> - Announce with your voice")
    print("  !deploy [environment] - Deploy with voice feedback")
    print("  !status - Check status with voice response")
    print("\nTo start the bot, uncomment the line below:")
    print("# bot.start()")
    
    # Uncomment to actually start the bot:
    # bot.start()


def example_voice_management():
    """Example of managing voice profiles."""
    
    config = VoiceCloningConfig(profiles_dir="./voice_profiles/")
    cloner = VoiceCloner(config)
    
    # List all profiles
    print("\n📋 Available Voice Profiles:")
    profiles = cloner.list_profiles()
    for profile in profiles:
        master_badge = " [MASTER]" if profile.is_master else ""
        print(f"  - {profile.name} ({profile.engine}){master_badge}")
    
    # Switch master voice
    if profiles:
        print(f"\nSwitching to profile: {profiles[0].name}")
        cloner.set_master_voice(profiles[0].name)
    
    # Create additional personas
    print("\nYou can create multiple voice personas:")
    print("  - different_persona.py could have its own voice")
    print("  - alert_voice for warnings")
    print("  - casual_voice for friendly messages")


if __name__ == "__main__":
    print("="*60)
    print("MasterChief IRC Bot - Voice Cloning Example")
    print("="*60)
    
    # Run main example
    main()
    
    # Show voice management examples
    # example_voice_management()
