"""
Example IRC Bot with Voice and Audio Capabilities

This example demonstrates how to use the voice/audio system with the IRC bot
for text-to-speech, speech-to-text, audio recording, and event announcements.
"""
import logging
from chatops.irc.bot_engine import create_bot, IRCBot
from chatops.irc.bot_engine.voice import VoiceEngine, VoiceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create voice engine with custom configuration
voice_config = VoiceConfig(
    enabled=True,
    tts=dict(
        enabled=True,
        rate=150,
        volume=0.9
    ),
    stt=dict(
        enabled=True,
        model="base",  # Use 'tiny' for faster, less accurate transcription
        language="en"
    ),
    recorder=dict(
        enabled=True,
        sample_rate=16000,
        vad_enabled=True
    ),
    player=dict(
        enabled=True,
        volume=0.8
    ),
    announcements=dict(
        enabled=True,
        directory="./sounds",
        events={
            "deploy_success": "success.wav",
            "deploy_failure": "failure.wav",
            "alert_critical": "alert.wav"
        }
    )
)

# Initialize voice engine
voice = VoiceEngine(VoiceConfig.from_dict(voice_config.__dict__))


def deploy_handler(connection, event, args):
    """Handle !deploy command with voice announcement."""
    nick = event.source.nick
    channel = event.target
    
    if not args:
        connection.privmsg(channel, f"{nick}: Usage: !deploy <environment>")
        return
    
    environment = args[0]
    msg = f"Starting deployment to {environment}"
    
    # Send IRC message
    connection.privmsg(channel, f"🚀 {msg}...")
    
    # Bot speaks the message
    voice.speak(msg)
    
    # Simulate deployment success
    success_msg = f"Deployment to {environment} completed successfully"
    connection.privmsg(channel, f"✓ {success_msg}")
    
    # Play success announcement
    voice.announce("deploy_success")


def say_handler(connection, event, args):
    """Handle !say command - bot speaks the text."""
    nick = event.source.nick
    channel = event.target
    
    if not args:
        connection.privmsg(channel, f"{nick}: Usage: !say <text>")
        return
    
    text = " ".join(args)
    connection.privmsg(channel, f"🔊 Speaking: {text}")
    
    # Convert text to speech
    voice.speak(text)


def listen_handler(connection, event, args):
    """Handle !listen command - bot listens and transcribes."""
    nick = event.source.nick
    channel = event.target
    
    duration = 5  # Default 5 seconds
    if args and args[0].isdigit():
        duration = int(args[0])
    
    connection.privmsg(channel, f"🎤 Listening for {duration} seconds...")
    
    # Record and transcribe
    text = voice.listen(duration=duration)
    
    if text:
        connection.privmsg(channel, f"Heard: {text}")
    else:
        connection.privmsg(channel, "Sorry, I didn't catch that.")


def record_handler(connection, event, args):
    """Handle !record command - record audio to file."""
    nick = event.source.nick
    channel = event.target
    
    if not args:
        connection.privmsg(channel, f"{nick}: Usage: !record <filename> [duration]")
        return
    
    filename = args[0]
    duration = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
    
    connection.privmsg(channel, f"🎙️ Recording to {filename} for {duration} seconds...")
    
    # Record audio
    success = voice.record(filename, duration)
    
    if success:
        connection.privmsg(channel, f"✓ Recorded to {filename}")
    else:
        connection.privmsg(channel, "❌ Recording failed")


def play_handler(connection, event, args):
    """Handle !play command - play audio file."""
    nick = event.source.nick
    channel = event.target
    
    if not args:
        connection.privmsg(channel, f"{nick}: Usage: !play <filename>")
        return
    
    filename = args[0]
    connection.privmsg(channel, f"🔊 Playing {filename}...")
    
    # Play audio file
    success = voice.play(filename)
    
    if not success:
        connection.privmsg(channel, "❌ Playback failed")


def voice_command_handler(connection, event, args):
    """Handle !voice command - listen for voice command and process it."""
    nick = event.source.nick
    channel = event.target
    
    connection.privmsg(channel, "🎤 Listening for voice command...")
    
    # Listen for voice input
    text = voice.listen(duration=5)
    
    if text:
        # Process the transcribed text as a command
        connection.privmsg(channel, f"Voice command received: {text}")
        
        # Parse and execute the command
        if text.lower().startswith("deploy"):
            parts = text.split()
            if len(parts) > 1:
                deploy_handler(connection, event, parts[1:])
        else:
            connection.privmsg(channel, f"Unknown voice command: {text}")
    else:
        connection.privmsg(channel, "No voice command detected")


def alert_handler(connection, event, args):
    """Handle !alert command - critical alert with announcement."""
    nick = event.source.nick
    channel = event.target
    
    if not args:
        message = "Critical alert!"
    else:
        message = " ".join(args)
    
    connection.privmsg(channel, f"🚨 ALERT: {message}")
    
    # Speak the alert
    voice.speak(f"Critical alert: {message}")
    
    # Play alert sound
    voice.announce("alert_critical")


def voices_handler(connection, event, args):
    """Handle !voices command - list available TTS voices."""
    channel = event.target
    
    try:
        voice.initialize()
        if voice._tts_engine:
            voices = voice._tts_engine.get_available_voices()
            if voices:
                connection.privmsg(channel, f"Available voices ({len(voices)}):")
                for i, v in enumerate(voices[:5], 1):  # Show first 5
                    connection.privmsg(channel, f"  {i}. {v['name']}")
                if len(voices) > 5:
                    connection.privmsg(channel, f"  ... and {len(voices) - 5} more")
            else:
                connection.privmsg(channel, "No voices available")
        else:
            connection.privmsg(channel, "TTS engine not available")
    except Exception as e:
        connection.privmsg(channel, f"Error listing voices: {e}")


def status_handler(connection, event, args):
    """Handle !status command with voice features."""
    nick = event.source.nick
    channel = event.target
    
    # Get voice system status
    voice_status = "enabled" if voice.config.enabled else "disabled"
    tts_status = "enabled" if voice.config.tts.enabled else "disabled"
    stt_status = "enabled" if voice.config.stt.enabled else "disabled"
    
    status_msg = f"""
📊 MasterChief Bot Status:
  Platform: ✓ Running
  Voice System: {voice_status}
  TTS: {tts_status}
  STT: {stt_status}
    """
    
    connection.privmsg(channel, status_msg.strip())


def main():
    """Run the IRC bot with voice capabilities."""
    # Configuration
    SERVER = "irc.libera.chat"
    PORT = 6667
    NICKNAME = "masterchief-voice"
    CHANNELS = ["#masterchief-dev"]
    
    # Create bot
    bot = create_bot(SERVER, PORT, NICKNAME, CHANNELS)
    
    # Register command bindings
    bot.bind("pub", "-|-", "!deploy", deploy_handler, cooldown=30)
    bot.bind("pub", "-|-", "!say", say_handler)
    bot.bind("pub", "-|-", "!listen", listen_handler)
    bot.bind("pub", "-|-", "!record", record_handler)
    bot.bind("pub", "-|-", "!play", play_handler)
    bot.bind("pub", "-|-", "!voice", voice_command_handler)
    bot.bind("pub", "-|-", "!alert", alert_handler)
    bot.bind("pub", "-|-", "!voices", voices_handler)
    bot.bind("pub", "-|-", "!status", status_handler)
    
    # Set user levels (optional)
    bot.set_user_level("admin", "owner")
    bot.set_user_level("devops", "op")
    
    print("""
MasterChief Voice Bot - Available Commands:
  !deploy <env>     - Deploy with voice announcement
  !say <text>       - Bot speaks the text
  !listen [secs]    - Listen and transcribe (default 5s)
  !record <file> [secs] - Record audio to file
  !play <file>      - Play audio file
  !voice            - Voice command mode
  !alert [msg]      - Critical alert with sound
  !voices           - List available TTS voices
  !status           - Bot status with voice info
    """)
    
    # Start bot
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\nShutting down bot...")
        voice.shutdown()
        print("Bot stopped")


if __name__ == "__main__":
    main()
