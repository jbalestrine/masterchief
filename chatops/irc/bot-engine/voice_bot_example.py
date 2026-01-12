"""Example IRC bot with voice automation integration."""

import logging
from chatops.irc.bot_engine.bot import IRCBot
from chatops.irc.bot_engine.voice import VoiceAutomation, VoiceAutomationConfig, VoiceConfig
from addons.scripts.manager import ScriptManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_bot_with_voice():
    """Create IRC bot with voice automation."""
    
    # Create IRC bot
    bot = IRCBot(
        server="irc.example.com",
        port=6667,
        nickname="MasterChief",
        channels=["#devops"]
    )
    
    # Initialize voice automation
    voice_config = VoiceConfig()
    automation_config = VoiceAutomationConfig(
        voice_config=voice_config,
        wake_words=["hey masterchief", "hey chief"],
        confirm_critical=True,
        play_feedback_sounds=True
    )
    
    script_manager = ScriptManager()
    automation = VoiceAutomation(automation_config, script_manager)
    
    # Register voice commands
    
    def start_voice_automation(connection, event, args):
        """Start voice automation via IRC."""
        try:
            automation.start_async()
            connection.privmsg(
                event.target,
                "🎤 Voice automation started. Say 'Hey MasterChief' to begin."
            )
            logger.info("Voice automation started via IRC")
        except Exception as e:
            connection.privmsg(event.target, f"❌ Failed to start voice automation: {e}")
            logger.error(f"Failed to start voice automation: {e}")
    
    def stop_voice_automation(connection, event, args):
        """Stop voice automation via IRC."""
        try:
            automation.stop()
            connection.privmsg(event.target, "🔇 Voice automation stopped")
            logger.info("Voice automation stopped via IRC")
        except Exception as e:
            connection.privmsg(event.target, f"❌ Failed to stop voice automation: {e}")
    
    def voice_status_handler(connection, event, args):
        """Get voice automation status."""
        status = "🎤 Active" if automation.is_listening else "🔇 Inactive"
        conversation = "💬 In conversation" if automation.is_active else "😴 Waiting for wake word"
        
        connection.privmsg(
            event.target,
            f"Voice Automation Status: {status} | {conversation}"
        )
    
    def voice_command_handler(connection, event, args):
        """Process a text voice command via IRC."""
        if not args:
            connection.privmsg(event.target, "Usage: !voice command <your command>")
            return
        
        command_text = " ".join(args)
        
        try:
            response = automation.process_text_command(command_text)
            connection.privmsg(event.target, f"🎤 {response}")
        except Exception as e:
            connection.privmsg(event.target, f"❌ Error: {e}")
            logger.error(f"Voice command error: {e}")
    
    def wake_voice_handler(connection, event, args):
        """Manually trigger wake word (for testing)."""
        try:
            automation.trigger_wake_manually()
            connection.privmsg(event.target, "🎤 Voice automation activated manually")
        except Exception as e:
            connection.privmsg(event.target, f"❌ Error: {e}")
    
    # Register IRC bindings
    bot.bind("pub", "-|-", "!voice start", start_voice_automation)
    bot.bind("pub", "-|-", "!voice stop", stop_voice_automation)
    bot.bind("pub", "-|-", "!voice status", voice_status_handler)
    bot.bind("pub", "-|-", "!voice command", voice_command_handler)
    bot.bind("pub", "-|-", "!voice wake", wake_voice_handler)
    
    # Add help command
    def help_handler(connection, event, args):
        """Show voice automation help."""
        help_text = """
🎤 Voice Automation Commands:
• !voice start - Start voice automation
• !voice stop - Stop voice automation
• !voice status - Show current status
• !voice command <cmd> - Execute a voice command via text
• !voice wake - Manually trigger wake word

Voice Commands:
• "Create a script to [description]"
• "Run [script name]"
• "List all scripts"
• "What's the system status?"
• "Deploy to [environment]"
• "Check for alerts"
• Say "that's all" to end conversation
        """.strip()
        
        for line in help_text.split('\n'):
            connection.privmsg(event.target, line)
    
    bot.bind("pub", "-|-", "!voice help", help_handler)
    
    return bot, automation


if __name__ == "__main__":
    bot, automation = create_bot_with_voice()
    
    logger.info("Starting MasterChief IRC Bot with Voice Automation...")
    logger.info("Channels: #devops")
    logger.info("Voice commands enabled via IRC")
    
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        automation.stop()
        logger.info("Bot stopped")
