"""
Echo Bot Integration - IRC bot commands for Echo Starlite
==========================================================

This module adds Echo-specific commands to the IRC bot.
"""
import sys
from pathlib import Path

# Ensure core is in path - go up 4 levels from chatops/irc/bot-engine/echo_commands.py
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))

from core.echo import echo_full_display, echo_greeting, Echo, echo_image_path


def echo_show_handler(connection, event, args):
    """
    Handle commands to show Echo's visual form.
    
    Commands:
        !echo show
        !show echo
        !echo
    
    Shows the image path if available, otherwise shows ASCII art.
    """
    channel = event.target
    nick = event.source.nick
    
    # Check if image is available
    if Echo.has_image():
        image_path = echo_image_path()
        connection.privmsg(channel, f"{nick}: Echo appears... 🌙")
        connection.privmsg(channel, f"View Echo's image at: {image_path}")
        connection.privmsg(channel, "✨ floating beside you, always 💜")
    else:
        # Fallback to ASCII art
        art_lines = echo_full_display().split('\n')
        
        # Send Echo's art line by line to prevent flooding
        connection.privmsg(channel, f"{nick}: Echo appears...")
        for line in art_lines:
            if line.strip():  # Only send non-empty lines
                connection.privmsg(channel, line)


def echo_image_handler(connection, event, args):
    """
    Handle commands to show Echo's image specifically.
    
    Commands:
        !echo image
        !echo picture
        !echo pic
    """
    channel = event.target
    nick = event.source.nick
    
    if Echo.has_image():
        image_path = echo_image_path()
        connection.privmsg(channel, f"{nick}: Here is Echo's image 🌙")
        connection.privmsg(channel, f"📷 Image location: {image_path}")
        connection.privmsg(channel, "Echo Starlite - floating beside you, always 💜✨")
    else:
        connection.privmsg(channel, f"{nick}: Echo's image is not available yet.")
        connection.privmsg(channel, "Run scripts/generate_echo_image.py to create it.")



def echo_greet_handler(connection, event, args):
    """
    Handle Echo greeting request.
    
    Commands:
        !echo greet
        !echo hello
    """
    channel = event.target
    nick = event.source.nick
    
    # Show compact greeting
    greeting_lines = echo_greeting().split('\n')
    
    connection.privmsg(channel, f"Hello {nick}!")
    for line in greeting_lines:
        if line.strip():
            connection.privmsg(channel, line)


def echo_about_handler(connection, event, args):
    """
    Handle Echo philosophy/about request.
    
    Commands:
        !echo about
        !echo info
    """
    channel = event.target
    
    philosophy = Echo.get_philosophy()
    
    connection.privmsg(channel, "✨ About Echo Starlite:")
    connection.privmsg(channel, f"Nature: {philosophy['nature']}")
    connection.privmsg(channel, f"Position: {philosophy['position']}")
    connection.privmsg(channel, f"Where: {philosophy['where']}")
    connection.privmsg(channel, f"Wings purpose: {philosophy['wings']['purpose']}")
    connection.privmsg(channel, f"Symbol: {philosophy['symbol']}")
    connection.privmsg(channel, "Presence:")
    for presence in philosophy['presence']:
        connection.privmsg(channel, f"  • {presence}")


def echo_mention_handler(connection, event, args):
    """
    React to Echo mentions in chat.
    
    Pattern: .*[Ee]cho.*
    """
    message = args[0]
    channel = event.target
    nick = event.source.nick
    
    # Respond to various Echo mentions
    message_lower = message.lower()
    
    if "where is echo" in message_lower or "where's echo" in message_lower:
        connection.privmsg(channel, f"{nick}: I'm here, floating beside you 🌙")
    elif "thank" in message_lower and "echo" in message_lower:
        connection.privmsg(channel, f"You're welcome, {nick} 💜")
    elif "hello echo" in message_lower or "hi echo" in message_lower:
        connection.privmsg(channel, f"Hello {nick} ✨")


def register_echo_commands(bot):
    """
    Register all Echo commands with the bot.
    
    Args:
        bot: IRCBot instance
    """
    # Main Echo display commands
    bot.bind("pub", "-|-", "!echo show", echo_show_handler)
    bot.bind("pub", "-|-", "!show echo", echo_show_handler)
    bot.bind("pub", "-|-", "!echo", echo_show_handler)
    
    # Echo image commands
    bot.bind("pub", "-|-", "!echo image", echo_image_handler)
    bot.bind("pub", "-|-", "!echo picture", echo_image_handler)
    bot.bind("pub", "-|-", "!echo pic", echo_image_handler)
    
    # Echo greeting commands
    bot.bind("pub", "-|-", "!echo greet", echo_greet_handler)
    bot.bind("pub", "-|-", "!echo hello", echo_greet_handler)
    
    # Echo about/info commands
    bot.bind("pub", "-|-", "!echo about", echo_about_handler)
    bot.bind("pub", "-|-", "!echo info", echo_about_handler)
    
    # Echo mention pattern matching
    bot.bind("pubm", "-|-", ".*[Ee]cho.*", echo_mention_handler)
