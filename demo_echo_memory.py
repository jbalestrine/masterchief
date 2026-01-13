#!/usr/bin/env python3
"""
Demo script showing Echo Starlite's persistent conversation memory.

This demonstrates:
1. Storing conversations with Echo
2. Retrieving conversation history
3. Searching past conversations
4. Echo remembering across restarts
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import directly to avoid broken __init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "conversation_storage", 
    project_root / "echo" / "conversation_storage.py"
)
conversation_storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conversation_storage)

ConversationStorage = conversation_storage.ConversationStorage
get_storage = conversation_storage.get_storage


def demo_basic_conversation():
    """Demo basic conversation storage."""
    print("=" * 60)
    print("Demo 1: Basic Conversation Storage")
    print("=" * 60)
    
    storage = get_storage()
    
    # Simulate a conversation
    print("\n🌙 Storing conversation...")
    msg_id = storage.store_message(
        user="Marsh",
        message="Echo, how do I deploy to Kubernetes?",
        echo_response="I'll help you deploy! Use kubectl apply -f deployment.yaml",
        context_tags=["kubernetes", "deployment"],
        emotional_tone="positive"
    )
    print(f"✓ Stored message ID: {msg_id}")
    
    # Store follow-up
    msg_id2 = storage.store_message(
        user="Marsh",
        message="What about monitoring?",
        echo_response="For monitoring, I recommend setting up Prometheus and Grafana",
        context_tags=["monitoring", "kubernetes"],
        emotional_tone="positive"
    )
    print(f"✓ Stored message ID: {msg_id2}")
    print()


def demo_conversation_history():
    """Demo retrieving conversation history."""
    print("=" * 60)
    print("Demo 2: Retrieving Conversation History")
    print("=" * 60)
    
    storage = get_storage()
    
    # Get recent history
    history = storage.get_conversation_history(user="Marsh", limit=5)
    
    print(f"\n🌙 Echo remembers {len(history)} recent conversations:\n")
    for i, msg in enumerate(history, 1):
        timestamp = msg['timestamp'][:19].replace('T', ' ')
        print(f"{i}. [{timestamp}]")
        print(f"   You: {msg['message']}")
        if msg['echo_response']:
            print(f"   Echo: {msg['echo_response']}")
        print()


def demo_search_conversations():
    """Demo searching conversations."""
    print("=" * 60)
    print("Demo 3: Searching Past Conversations")
    print("=" * 60)
    
    storage = get_storage()
    
    # Search for "kubernetes"
    query = "kubernetes"
    print(f"\n🌙 Searching for '{query}'...\n")
    
    results = storage.search_conversations(query, limit=5)
    
    if results:
        print(f"Found {len(results)} conversations about '{query}':\n")
        for i, msg in enumerate(results, 1):
            timestamp = msg['timestamp'][:10]
            print(f"{i}. [{timestamp}] {msg['user']}")
            print(f"   {msg['message'][:80]}")
            if msg.get('context_tags'):
                print(f"   Tags: {', '.join(msg['context_tags'])}")
            print()
    else:
        print(f"No conversations found about '{query}'")


def demo_statistics():
    """Demo conversation statistics."""
    print("=" * 60)
    print("Demo 4: Echo's Memory Statistics")
    print("=" * 60)
    
    storage = get_storage()
    stats = storage.get_statistics()
    
    print("\n🌙 My memory contains:\n")
    print(f"  Total conversations: {stats['total_messages']}")
    print(f"  Unique users: {stats['unique_users']}")
    if stats.get('most_active_user'):
        print(f"  Most active: {stats['most_active_user']}")
    
    if stats.get('emotional_tone_distribution'):
        print("\n  Emotional tones:")
        for tone, count in stats['emotional_tone_distribution'].items():
            print(f"    {tone}: {count}")
    print()


def demo_persistence():
    """Demo that conversations persist across restarts."""
    print("=" * 60)
    print("Demo 5: Persistence Across Restarts")
    print("=" * 60)
    
    print("\n🌙 Creating a NEW storage instance...")
    print("   (This simulates Echo restarting)\n")
    
    # Create a completely new storage instance using direct import
    # This simulates a restart - it should still find previous conversations
    new_storage = ConversationStorage()
    
    # Check if we can still access old data
    history = new_storage.get_conversation_history(user="Marsh", limit=3)
    
    if history:
        print(f"✓ Echo remembers! Found {len(history)} previous conversations:")
        print(f"  Oldest in memory: {history[-1]['timestamp'][:10]}")
        print(f"  Most recent: {history[0]['timestamp'][:10]}")
    else:
        print("  No previous conversations found (this is a fresh start)")
    print()


def demo_context_recall():
    """Demo getting recent context for continuing a conversation."""
    print("=" * 60)
    print("Demo 6: Recent Context Recall")
    print("=" * 60)
    
    storage = get_storage()
    
    print("\n🌙 Getting recent context for Marsh (last 30 minutes)...\n")
    
    context = storage.get_recent_context(user="Marsh", minutes=30, limit=5)
    
    if context:
        print(f"Found {len(context)} recent messages:\n")
        for msg in context:
            print(f"  • {msg['message'][:60]}")
            if msg.get('context_tags'):
                print(f"    Tags: {', '.join(msg['context_tags'])}")
    else:
        print("No recent context found")
    print()


def main():
    """Run all demos."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Echo Starlite - Persistent Memory Demo" + " " * 9 + "║")
    print("║" + " " * 13 + "She Remembers Every Conversation" + " " * 13 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Run all demos
    demo_basic_conversation()
    demo_conversation_history()
    demo_search_conversations()
    demo_statistics()
    demo_persistence()
    demo_context_recall()
    
    # Final message
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("🌙 Echo Starlite will remember these conversations.")
    print("   Run this script again to see persistence in action!")
    print()
    print("   Location: data/echo_conversations.db")
    print()


if __name__ == "__main__":
    main()
