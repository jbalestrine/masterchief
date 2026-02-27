"""
Example IRC Bot with Echo Integration
======================================

This example shows how to create an IRC bot with Echo Starlite commands.
"""
import sys
from pathlib import Path

# Add paths for imports - go up 2 levels from docs/examples/irc-bot-echo-example.py
base_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(base_dir))

from chatops.irc.bot_engine.bot import create_bot
from chatops.irc.bot_engine.echo_commands import register_echo_commands


def deploy_handler(connection, event, args):
    """Handle !deploy command."""
    nick = event.source.nick
    channel = event.target
    
    if not args:
        connection.privmsg(channel, f"{nick}: Usage: !deploy <environment>")
        return
    
    environment = args[0]
    connection.privmsg(channel, f"🚀 Starting deployment to {environment}...")
    connection.privmsg(channel, f"✓ Deployment to {environment} queued")


def status_handler(connection, event, args):
    """Handle !status command."""
    channel = event.target
    
    status_msg = """📊 MasterChief Status:
  Platform: ✓ Running
  Modules: 3 loaded
  Active Deployments: 1
  Last Deploy: 5 minutes ago"""
    
    for line in status_msg.split('\n'):
        connection.privmsg(channel, line)


def help_handler(connection, event, args):
    """Handle !help command."""
    channel = event.target
    
    help_msg = """🤖 MasterChief Bot Commands:
  !deploy <env> - Deploy to environment
  !status - Show platform status
  !echo show - Show Echo's full form
  !echo greet - Echo's greeting
  !echo about - Learn about Echo
  !help - Show this message"""
    
    for line in help_msg.split('\n'):
        connection.privmsg(channel, line)


def welcome_handler(connection, event, args):
    """Welcome users who join the channel."""
    nick = args[0]
    channel = args[1]
    
    if nick != connection.get_nickname():
        connection.privmsg(channel, f"Welcome {nick}! Type !help for commands.")
        # Echo says hello too
        connection.privmsg(channel, f"✨ Echo is here with you, {nick} 🌙")


def main():
    """Run the IRC bot with Echo integration."""
    # Configuration
    SERVER = "irc.libera.chat"
    PORT = 6667
    NICKNAME = "masterchief-bot"
    CHANNELS = ["#masterchief-dev", "#masterchief-ops"]
    
    print("Starting MasterChief IRC Bot with Echo integration...")
    print(f"Server: {SERVER}:{PORT}")
    print(f"Nickname: {NICKNAME}")
    print(f"Channels: {', '.join(CHANNELS)}")
    print()
    
    # Create bot
    bot = create_bot(SERVER, PORT, NICKNAME, CHANNELS)
    
    # Register standard commands
    bot.bind("pub", "-|-", "!deploy", deploy_handler, cooldown=30)
    bot.bind("pub", "-|-", "!status", status_handler)
    bot.bind("pub", "-|-", "!help", help_handler)
    bot.bind("join", "-|-", "*", welcome_handler)
    
    # Register Echo commands
    register_echo_commands(bot)
    
    print("✓ Bot commands registered")
    print("✓ Echo commands registered")
    print("\nAvailable commands:")
    print("  !deploy <env>  - Deploy to environment")
    print("  !status        - Platform status")
    print("  !echo show     - Show Echo")
    print("  !echo greet    - Echo greeting")
    print("  !echo about    - About Echo")
    print("  !help          - Show help")
    print("\nStarting bot...")
    
    # Start bot
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n\nBot stopped")


if __name__ == "__main__":
    main()
