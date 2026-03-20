#!/usr/bin/env python3
"""
Example: Echo Starlite IRC Bot with Persistent Memory

This example shows how to integrate Echo's persistent conversation storage
with an IRC bot so that Echo remembers all conversations.

Features:
- Automatic conversation storage
- Memory search with !echo remember <query>
- History viewing with !echo history
- Statistics with !echo stats
- All existing Echo commands (show, greet, about, etc.)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Note: This is a simplified example showing the integration pattern
# In actual use, you'd connect to a real IRC server


def create_echo_bot_with_memory(server, port, nickname, channels):
    """
    Create an IRC bot with Echo Starlite's persistent memory.
    
    Args:
        server: IRC server address
        port: IRC server port
        nickname: Bot's nickname
        channels: List of channels to join
    
    Returns:
        Configured IRCBot instance
    """
    from chatops.irc.bot_engine.bot import create_bot
    from chatops.irc.bot_engine.echo_commands import (
        register_echo_commands,
        store_conversation_handler
    )
    
    # Create the bot
    bot = create_bot(server, port, nickname, channels)
    
    # Register all Echo commands (includes memory commands)
    register_echo_commands(bot)
    
    # Optionally: Add automatic conversation storage
    # Hook into the bot's message handler to auto-store conversations
    original_on_pubmsg = bot.on_pubmsg
    
    def on_pubmsg_with_storage(connection, event):
        # Store the conversation
        store_conversation_handler(connection, event)
        # Call original handler
        original_on_pubmsg(connection, event)
    
    bot.on_pubmsg = on_pubmsg_with_storage
    
    return bot


def demo_echo_commands():
    """
    Demo of Echo's memory commands.
    
    This shows what commands users can use to interact with Echo's memory.
    """
    print("=" * 60)
    print("Echo Starlite IRC Bot - Memory Commands")
    print("=" * 60)
    print()
    
    print("Available Commands:")
    print()
    
    print("1. Display Commands:")
    print("   !echo show       - Show Echo's full visual form")
    print("   !echo greet      - Get a greeting from Echo")
    print("   !echo about      - Learn about Echo's philosophy")
    print()
    
    print("2. Memory Commands (NEW!):")
    print("   !echo remember <query>  - Search Echo's memory")
    print("                             Example: !echo remember kubernetes")
    print()
    print("   !echo history [limit]   - Show recent conversation history")
    print("                             Example: !echo history 10")
    print()
    print("   !echo stats             - Show Echo's memory statistics")
    print()
    
    print("3. Natural Language:")
    print("   Just mention Echo in your message and she may respond!")
    print("   Examples:")
    print("   - 'Where is Echo?'")
    print("   - 'Thanks Echo!'")
    print("   - 'Hello Echo'")
    print()
    
    print("=" * 60)
    print()


def demo_programmatic_usage():
    """
    Demo of programmatic usage of Echo's memory.
    
    Shows how to use the conversation storage API directly.
    """
    print("=" * 60)
    print("Programmatic Usage Example")
    print("=" * 60)
    print()
    
    # Direct import (avoiding broken __init__.py)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "conversation_storage",
        project_root / "echo" / "conversation_storage.py"
    )
    conversation_storage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conversation_storage)
    
    storage = conversation_storage.get_storage()
    
    print("# Get conversation history for a user")
    print("history = storage.get_conversation_history(")
    print("    user='username',")
    print("    limit=10")
    print(")")
    print()
    
    print("# Search conversations")
    print("results = storage.search_conversations(")
    print("    query='kubernetes',")
    print("    user='username',")
    print("    limit=20")
    print(")")
    print()
    
    print("# Store a conversation")
    print("message_id = storage.store_message(")
    print("    user='username',")
    print("    message='How do I deploy?',")
    print("    echo_response='Use kubectl apply',")
    print("    context_tags=['kubernetes', 'deployment'],")
    print("    emotional_tone='positive',")
    print("    channel='#devops'")
    print(")")
    print()
    
    print("# Get statistics")
    print("stats = storage.get_statistics()")
    print("print(f'Total: {stats[\"total_messages\"]}')")
    print()
    
    # Actually get and show stats
    stats = storage.get_statistics()
    print(f"Current Stats: {stats['total_messages']} conversations with {stats['unique_users']} users")
    print()


def demo_bot_setup():
    """
    Show example bot setup code.
    """
    print("=" * 60)
    print("Bot Setup Example")
    print("=" * 60)
    print()
    
    print("# Simple setup")
    print("```python")
    print("from chatops.irc.bot_engine.bot import create_bot")
    print("from chatops.irc.bot_engine.echo_commands import register_echo_commands")
    print()
    print("# Create bot")
    print("bot = create_bot(")
    print("    server='irc.libera.chat',")
    print("    port=6667,")
    print("    nickname='EchoBot',")
    print("    channels=['#mychannel']")
    print(")")
    print()
    print("# Register Echo commands (includes memory commands!)")
    print("register_echo_commands(bot)")
    print()
    print("# Start bot")
    print("bot.start()")
    print("```")
    print()


def main():
    """Main demo function."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 8 + "Echo Starlite IRC Bot - Integration Example" + " " * 6 + "║")
    print("║" + " " * 14 + "Persistent Memory System" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    demo_echo_commands()
    demo_programmatic_usage()
    demo_bot_setup()
    
    print("=" * 60)
    print("Next Steps")
    print("=" * 60)
    print()
    print("1. Run the demo:")
    print("   python demo_echo_memory.py")
    print()
    print("2. Read the documentation:")
    print("   docs/ECHO_PERSISTENT_MEMORY.md")
    print()
    print("3. Run the tests:")
    print("   python tests/unit/test_conversation_storage.py")
    print()
    print("4. Deploy Echo to your IRC server!")
    print()
    print("🌙 Echo Starlite will remember every conversation. Always.")
    print()


if __name__ == "__main__":
    main()
