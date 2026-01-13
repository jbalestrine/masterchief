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

# Import conversation storage
try:
    from echo.conversation_storage import get_storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False


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


def echo_remember_handler(connection, event, args):
    """
    Search Echo's conversation memory.
    
    Commands:
        !echo remember <query>
    """
    channel = event.target
    nick = event.source.nick
    
    if not STORAGE_AVAILABLE:
        connection.privmsg(channel, f"{nick}: I'm sorry, my persistent memory is not available right now...")
        return
    
    # Get the search query from args
    query = ' '.join(args) if args else None
    
    if not query:
        connection.privmsg(channel, f"{nick}: What should I remember? Try: !echo remember <topic>")
        return
    
    try:
        storage = get_storage()
        results = storage.search_conversations(query, user=nick, limit=3)
        
        if not results:
            connection.privmsg(channel, f"{nick}: I don't recall anything about '{query}'... yet 🌙")
        else:
            connection.privmsg(channel, f"{nick}: I remember... 💜")
            for i, msg in enumerate(results, 1):
                timestamp = msg['timestamp'][:10]  # Just the date
                snippet = msg['message'][:80] + '...' if len(msg['message']) > 80 else msg['message']
                connection.privmsg(channel, f"  {i}. [{timestamp}] {snippet}")
                
                if msg.get('echo_response'):
                    response_snippet = msg['echo_response'][:80] + '...' if len(msg['echo_response']) > 80 else msg['echo_response']
                    connection.privmsg(channel, f"     → {response_snippet}")
    except Exception as e:
        connection.privmsg(channel, f"{nick}: I tried to remember, but something went wrong... {str(e)[:50]}")


def echo_history_handler(connection, event, args):
    """
    Show recent conversation history.
    
    Commands:
        !echo history [limit]
    """
    channel = event.target
    nick = event.source.nick
    
    if not STORAGE_AVAILABLE:
        connection.privmsg(channel, f"{nick}: My memory archive is not available...")
        return
    
    # Get limit from args
    try:
        limit = int(args[0]) if args else 5
        limit = min(limit, 10)  # Cap at 10 to prevent spam
    except ValueError:
        limit = 5
    
    try:
        storage = get_storage()
        history = storage.get_conversation_history(user=nick, limit=limit, channel=channel)
        
        if not history:
            connection.privmsg(channel, f"{nick}: We haven't talked yet, or I've forgotten... 🌙")
        else:
            connection.privmsg(channel, f"{nick}: Our recent conversations... 💜")
            for i, msg in enumerate(history, 1):
                timestamp = msg['timestamp'][:16].replace('T', ' ')  # Date and time
                snippet = msg['message'][:60] + '...' if len(msg['message']) > 60 else msg['message']
                connection.privmsg(channel, f"  {i}. [{timestamp}] {snippet}")
    except Exception as e:
        connection.privmsg(channel, f"{nick}: I couldn't access my memories... {str(e)[:50]}")


def echo_stats_handler(connection, event, args):
    """
    Show Echo's memory statistics.
    
    Commands:
        !echo stats
    """
    channel = event.target
    nick = event.source.nick
    
    if not STORAGE_AVAILABLE:
        connection.privmsg(channel, f"{nick}: Statistics not available...")
        return
    
    try:
        storage = get_storage()
        stats = storage.get_statistics()
        
        connection.privmsg(channel, f"{nick}: My memory... 🌙")
        connection.privmsg(channel, f"  Total conversations: {stats['total_messages']}")
        connection.privmsg(channel, f"  People I've met: {stats['unique_users']}")
        if stats.get('most_active_user'):
            connection.privmsg(channel, f"  Most chatty: {stats['most_active_user']}")
        
        # Show emotional tone distribution
        if stats.get('emotional_tone_distribution'):
            tones = stats['emotional_tone_distribution']
            tone_str = ", ".join([f"{k}: {v}" for k, v in tones.items()])
            connection.privmsg(channel, f"  Moods: {tone_str}")
    except Exception as e:
        connection.privmsg(channel, f"{nick}: Failed to retrieve statistics... {str(e)[:50]}")


def store_conversation_handler(connection, event):
    """
    Automatically store conversations in Echo's memory.
    This should be called for all public messages.
    """
    if not STORAGE_AVAILABLE:
        return
    
    try:
        message = event.arguments[0] if event.arguments else ""
        nick = event.source.nick
        channel = event.target
        
        # Don't store commands
        if message.startswith('!'):
            return
        
        storage = get_storage()
        storage.store_message(
            user=nick,
            message=message,
            channel=channel,
            emotional_tone="neutral"
        )
    except Exception:
        pass  # Silently fail - don't interrupt normal bot operation


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
    
    # Conversation memory commands
    bot.bind("pub", "-|-", "!echo remember", echo_remember_handler)
    bot.bind("pub", "-|-", "!echo history", echo_history_handler)
    bot.bind("pub", "-|-", "!echo stats", echo_stats_handler)
    
    # Echo mention pattern matching
    bot.bind("pubm", "-|-", ".*[Ee]cho.*", echo_mention_handler)
