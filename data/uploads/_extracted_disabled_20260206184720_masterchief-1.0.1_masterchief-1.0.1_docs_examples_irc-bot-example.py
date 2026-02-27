"""
Example IRC Bot with MasterChief Integration

This example shows how to create an IRC bot that integrates with the MasterChief platform
for deployment notifications and command execution.
"""
import asyncio
from chatops.irc.bot_engine import create_bot, IRCBot


def deploy_handler(connection, event, args):
    """Handle !deploy command."""
    nick = event.source.nick
    channel = event.target
    
    if not args:
        connection.privmsg(channel, f"{nick}: Usage: !deploy <environment>")
        return
    
    environment = args[0]
    connection.privmsg(channel, f"🚀 Starting deployment to {environment}...")
    
    # Here you would integrate with MasterChief deployment
    # For now, just simulate
    connection.privmsg(channel, f"✓ Deployment to {environment} queued")


def status_handler(connection, event, args):
    """Handle !status command."""
    nick = event.source.nick
    channel = event.target
    
    # Get status from MasterChief platform
    status_msg = """
📊 MasterChief Status:
  Platform: ✓ Running
  Modules: 3 loaded
  Active Deployments: 1
  Last Deploy: 5 minutes ago
    """
    
    connection.privmsg(channel, status_msg.strip())


def welcome_handler(connection, event, args):
    """Welcome users who join the channel."""
    nick = args[0]
    channel = args[1]
    
    if nick != connection.get_nickname():
        connection.privmsg(channel, f"Welcome {nick}! Type !help for commands.")


def terraform_mention_handler(connection, event, args):
    """React to terraform mentions."""
    channel = event.target
    message = args[0]
    
    if "error" in message.lower() or "fail" in message.lower():
        connection.privmsg(channel, "🔍 I noticed a Terraform issue. Need help? Try !docs terraform")


def main():
    """Run the IRC bot."""
    # Configuration
    SERVER = "irc.libera.chat"
    PORT = 6667
    NICKNAME = "masterchief-bot"
    CHANNELS = ["#masterchief-dev", "#masterchief-ops"]
    
    # Create bot
    bot = create_bot(SERVER, PORT, NICKNAME, CHANNELS)
    
    # Register command bindings
    bot.bind("pub", "-|-", "!deploy", deploy_handler, cooldown=30)
    bot.bind("pub", "-|-", "!status", status_handler)
    bot.bind("join", "-|-", "*", welcome_handler)
    bot.bind("pubm", "-|-", ".*terraform.*", terraform_mention_handler)
    
    # Set user levels (optional)
    bot.set_user_level("admin", "owner")
    bot.set_user_level("devops", "op")
    
    # Start bot
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\nBot stopped")


if __name__ == "__main__":
    main()
