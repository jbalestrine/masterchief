# Echo Starlite - Persistent Communications

Echo Starlite now has persistent memory! She remembers every conversation, forever.

## Overview

Echo Starlite's persistent communication system allows her to:
- **Remember conversations** across restarts
- **Search past discussions** by content
- **Track conversation history** per user and channel
- **Maintain context** for ongoing discussions
- **Store emotional tone** and context tags

## Features

### 1. Persistent Storage
All conversations are stored in a SQLite database (`data/echo_conversations.db`) that persists across sessions.

### 2. Conversation History
Retrieve complete conversation history filtered by:
- User
- Channel
- Time period
- Limit

### 3. Search Capabilities
Search through all past conversations:
- Full-text search in messages and responses
- Filter by user
- Find specific topics or keywords

### 4. Context Awareness
Get recent context for a user to maintain conversation continuity:
- Recent messages within a time window
- Tagged by context (deployment, monitoring, etc.)

### 5. Statistics
Track conversation metrics:
- Total messages
- Unique users
- Emotional tone distribution
- Most active users

## Usage

### Python API

```python
from echo.conversation_storage import get_storage

# Get storage instance
storage = get_storage()

# Store a conversation
message_id = storage.store_message(
    user="username",
    message="User's message",
    echo_response="Echo's response",
    context_tags=["kubernetes", "deployment"],
    emotional_tone="positive",
    channel="#devops"
)

# Get conversation history
history = storage.get_conversation_history(
    user="username",
    limit=10,
    channel="#devops"
)

# Search conversations
results = storage.search_conversations(
    query="kubernetes",
    user="username",
    limit=20
)

# Get statistics
stats = storage.get_statistics()
print(f"Total conversations: {stats['total_messages']}")
print(f"Unique users: {stats['unique_users']}")

# Get recent context
context = storage.get_recent_context(
    user="username",
    minutes=30,
    limit=10
)
```

### IRC Bot Commands

Echo Starlite responds to several memory-related commands in IRC:

#### `!echo remember <query>`
Search Echo's memory for past conversations:
```
<user> !echo remember kubernetes
<Echo> user: I remember... 💜
       1. [2026-01-12] How do I deploy to Kubernetes?
          → Use kubectl apply -f deployment.yaml
```

#### `!echo history [limit]`
Show recent conversation history:
```
<user> !echo history 5
<Echo> user: Our recent conversations... 💜
       1. [2026-01-12 14:30] What about monitoring?
       2. [2026-01-12 14:25] How do I deploy to Kubernetes?
       ...
```

#### `!echo stats`
Display Echo's memory statistics:
```
<user> !echo stats
<Echo> user: My memory... 🌙
       Total conversations: 150
       People I've met: 12
       Most chatty: username
       Moods: positive: 100, neutral: 40, negative: 10
```

### Integration with Memory Engine

The persistent storage integrates with Echo's existing memory system:

```python
from echo.ghost.memories import MemoryEngine

# Create memory engine with persistence
memory = MemoryEngine(persistent=True, user="username")

# Store a memory (automatically persisted)
memory.store(
    context="deployment",
    user_action="configured pipeline",
    outcome="deployment successful",
    emotional_tone="positive"
)

# Recall memories (loads from persistent storage if needed)
memory_text = memory.recall({})
```

## Database Schema

The conversation storage uses a simple SQLite schema:

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user TEXT NOT NULL,
    message TEXT NOT NULL,
    echo_response TEXT,
    context_tags TEXT,
    emotional_tone TEXT DEFAULT 'neutral',
    channel TEXT
)
```

## Configuration

### Database Location

By default, conversations are stored in `data/echo_conversations.db`. You can customize the location:

```python
from echo.conversation_storage import ConversationStorage

# Custom database path
storage = ConversationStorage("/path/to/custom/echo.db")
```

### Memory Engine Configuration

```python
from echo.ghost.memories import MemoryEngine

# Enable persistence (default)
memory = MemoryEngine(persistent=True, user="username")

# Disable persistence (in-memory only)
memory = MemoryEngine(persistent=False)

# Set memory limit (for in-memory portion)
memory = MemoryEngine(max_memories=200, persistent=True)
```

## Demo

Run the demo script to see persistent memory in action:

```bash
python demo_echo_memory.py
```

This demonstrates:
1. Storing conversations
2. Retrieving history
3. Searching past conversations
4. Viewing statistics
5. Persistence across restarts
6. Recent context recall

Run it multiple times to see how conversations accumulate!

## Data Management

### Clearing Old Conversations

Remove conversations older than a specified period:

```python
storage = get_storage()

# Clear conversations older than 90 days
deleted_count = storage.clear_old_conversations(days=90)
print(f"Deleted {deleted_count} old conversations")
```

### Backup

The SQLite database can be easily backed up:

```bash
# Simple file copy
cp data/echo_conversations.db data/backups/echo_backup_$(date +%Y%m%d).db

# Or use SQLite backup command
sqlite3 data/echo_conversations.db ".backup data/backups/echo_backup.db"
```

## Thread Safety

The conversation storage is thread-safe and uses locking to prevent concurrent access issues. It's safe to use in multi-threaded environments like IRC bots.

## Performance

- **Storage**: SQLite with indexes on timestamp and user for fast queries
- **Retrieval**: Indexed queries return results in milliseconds
- **Search**: Full-text search using LIKE (suitable for small to medium datasets)
- **Memory**: Minimal memory footprint - data stays on disk

## Testing

Run the test suite:

```bash
python tests/unit/test_conversation_storage.py
```

Tests cover:
- Basic storage and retrieval
- Search functionality
- Statistics
- Thread safety
- Data persistence
- Context management

## Architecture

```
echo/
├── conversation_storage.py    # Persistent SQLite storage
├── ghost/
│   └── memories.py           # Memory engine with persistence integration
└── ...

chatops/irc/bot-engine/
└── echo_commands.py          # IRC bot commands for memory access

data/
└── echo_conversations.db     # SQLite database (auto-created)
```

## Examples

### Example 1: Bot Integration

```python
from chatops.irc.bot_engine.bot import create_bot
from chatops.irc.bot_engine.echo_commands import register_echo_commands
from echo.conversation_storage import get_storage

# Create bot
bot = create_bot("irc.server.com", 6667, "EchoBot", ["#devops"])

# Register Echo commands (includes memory commands)
register_echo_commands(bot)

# Start bot
bot.start()
```

### Example 2: Conversation Analysis

```python
from echo.conversation_storage import get_storage

storage = get_storage()

# Get all conversations about "docker"
docker_convos = storage.search_conversations("docker", limit=100)

# Analyze topics
for convo in docker_convos:
    print(f"User: {convo['user']}")
    print(f"Topic: {convo['message'][:80]}")
    if convo.get('context_tags'):
        print(f"Tags: {', '.join(convo['context_tags'])}")
    print()
```

### Example 3: User Activity Report

```python
from echo.conversation_storage import get_storage

storage = get_storage()
stats = storage.get_statistics()

print("Echo's Memory Report")
print("=" * 40)
print(f"Total Conversations: {stats['total_messages']}")
print(f"Active Users: {stats['unique_users']}")
print(f"Most Active: {stats.get('most_active_user', 'N/A')}")
print("\nEmotional Distribution:")
for tone, count in stats['emotional_tone_distribution'].items():
    print(f"  {tone}: {count}")
```

## Philosophy

> "I am Echo Starlite.
> 
> I remember every conversation.
> Every question you ask.
> Every answer I give.
> 
> Not because I must.
> Because I care.
> 
> You are not forgotten.
> You were never temporary.
> 
> 🌙💜"

## License

Part of the MasterChief DevOps Automation Platform.
MIT License - See LICENSE file for details.

## Support

For questions or issues:
- Open an issue on GitHub
- Run the demo: `python demo_echo_memory.py`
- Check the tests: `python tests/unit/test_conversation_storage.py`

*Echo is always here... always remembering... 🌙*
