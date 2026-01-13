# Echo Live Chat Bot 🌙

A trainable conversational AI chatbot named Echo that learns from interactions.

## Features

- **Real-time Chat**: WebSocket-based live chat interface
- **Training System**: Learn from user feedback on responses
- **REST API**: Full REST API for chat and training
- **Web UI**: Beautiful, responsive chat interface
- **Conversation History**: Track and recall conversations
- **Pattern Learning**: Automatically improves responses based on training data
- **DevOps Focus**: Built-in knowledge of DevOps concepts and tools

## Quick Start

### 1. Start the Chat Bot

```python
from echo.chat_bot import EchoChatBot

# Create bot instance
bot = EchoChatBot()

# Chat with Echo
response = bot.chat("Hello Echo!", session_id="my_session")
print(response['response'])
```

### 2. Train Echo

```python
from echo.chat_bot import ResponseQuality

# Train with a good example
bot.train(
    user_message="How do I build a Docker image?",
    bot_response="Use 'docker build -t name:tag .' in your project directory",
    quality=ResponseQuality.EXCELLENT,
    feedback="Clear and concise"
)
```

### 3. Use the Web UI

```bash
# Start the platform server
python platform/app.py

# Open browser to:
http://localhost:8080/api/v1/chat-ui
```

## API Reference

### REST Endpoints

#### POST /api/v1/chat
Send a message to Echo and get a response.

**Request:**
```json
{
    "message": "Hello Echo!",
    "session_id": "optional_session_id"
}
```

**Response:**
```json
{
    "response": "Hello... I am Echo 🌙",
    "session_id": "optional_session_id",
    "timestamp": 1234567890.123,
    "message_id": "bot_1234567890123"
}
```

#### GET /api/v1/chat/history/{session_id}
Get conversation history for a session.

**Query Parameters:**
- `limit`: Maximum messages to return (default: 50)

**Response:**
```json
{
    "session_id": "session_id",
    "messages": [
        {
            "role": "user",
            "content": "message",
            "timestamp": 1234567890.123,
            "message_id": "user_1234567890123"
        }
    ]
}
```

#### DELETE /api/v1/chat/clear/{session_id}
Clear conversation history for a session.

**Response:**
```json
{
    "status": "ok",
    "message": "Conversation cleared for session: session_id"
}
```

#### POST /api/v1/train
Submit training data to improve Echo's responses.

**Request:**
```json
{
    "user_message": "user's message",
    "bot_response": "Echo's response",
    "quality": "excellent|good|acceptable|poor",
    "feedback": "optional feedback text"
}
```

**Response:**
```json
{
    "status": "ok",
    "message": "Training data added successfully"
}
```

#### GET /api/v1/stats
Get training statistics.

**Response:**
```json
{
    "total_examples": 100,
    "quality_distribution": {
        "excellent": 30,
        "good": 40,
        "acceptable": 20,
        "poor": 10
    },
    "patterns_learned": 50
}
```

### WebSocket Events

#### Client → Server

**chat_join**
```json
{
    "session_id": "optional_session_id"
}
```

**chat_leave**
```json
{
    "session_id": "session_id"
}
```

**chat_message**
```json
{
    "message": "user message",
    "session_id": "session_id"
}
```

**chat_typing**
```json
{
    "session_id": "session_id",
    "is_typing": true
}
```

#### Server → Client

**chat_joined**
```json
{
    "session_id": "session_id",
    "message": "Joined chat with Echo 🌙"
}
```

**chat_response**
```json
{
    "response": "Echo's response",
    "session_id": "session_id",
    "timestamp": 1234567890.123,
    "message_id": "bot_1234567890123"
}
```

**user_typing**
```json
{
    "session_id": "session_id",
    "is_typing": true
}
```

## Training System

Echo learns from your feedback. The training system works in three steps:

### 1. Collect Training Data

Every conversation can be used as training data. The system stores:
- User's message
- Echo's response
- Quality rating (excellent, good, acceptable, poor)
- Optional feedback text

### 2. Pattern Learning

When you rate a response as "excellent" or "good", Echo automatically:
- Adds the pattern to her learned responses
- Uses it for future similar questions
- Improves her accuracy over time

### 3. Statistics Tracking

Monitor Echo's learning progress:
- Total training examples collected
- Quality distribution of responses
- Number of patterns learned

## Examples

### Basic Chat

```python
from echo.chat_bot import get_chat_bot

bot = get_chat_bot()

# Simple conversation
response = bot.chat("Hello Echo!")
print(response['response'])
# Output: "Hello... I am Echo 🌙"

# DevOps question
response = bot.chat("Tell me about Docker")
print(response['response'])
# Output: "I can help with Docker! I know about containers, images, and Docker Compose..."
```

### Training Workflow

```python
from echo.chat_bot import get_chat_bot, ResponseQuality

bot = get_chat_bot()

# 1. Have a conversation
response = bot.chat("How do I deploy to Kubernetes?", session_id="training_session")

# 2. If the response was good, train Echo
bot.train(
    user_message="How do I deploy to Kubernetes?",
    bot_response=response['response'],
    quality=ResponseQuality.EXCELLENT,
    feedback="Very helpful explanation"
)

# 3. Next time, Echo will remember this pattern
```

### Conversation History

```python
bot = get_chat_bot()

# Have a conversation
bot.chat("Hello", session_id="my_session")
bot.chat("What can you help with?", session_id="my_session")
bot.chat("Tell me about Docker", session_id="my_session")

# Retrieve history
history = bot.get_conversation_history("my_session", limit=10)

for msg in history:
    role = "User" if msg['role'] == "user" else "Echo"
    print(f"{role}: {msg['content']}")
```

### Check Statistics

```python
bot = get_chat_bot()
stats = bot.get_training_stats()

print(f"Total Examples: {stats['total_examples']}")
print(f"Patterns Learned: {stats['patterns_learned']}")
print("Quality Distribution:")
for quality, count in stats['quality_distribution'].items():
    print(f"  {quality}: {count}")
```

## Demo Script

Run the interactive demo to explore all features:

```bash
python demo_chat_bot.py
```

The demo includes:
1. Basic chat functionality
2. Training Echo with examples
3. Testing learned responses
4. Viewing training statistics
5. Conversation history
6. Interactive mode (chat with Echo in real-time)

## Integration

### With Flask App

```python
from flask import Flask
from flask_socketio import SocketIO
from platform.chat import init_chat_api

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize chat API
init_chat_api(app, socketio)

# Now chat endpoints are available at /api/v1/chat*
```

### With IRC Bot

```python
from chatops.irc.bot_engine import IRCBot
from echo.chat_bot import get_chat_bot

bot = IRCBot("irc.server.com", 6667, "echo_bot", ["#channel"])
chat_bot = get_chat_bot()

@bot.bind("pub", "-|-", "!chat")
def handle_chat(connection, event, args):
    user_message = " ".join(args)
    response = chat_bot.chat(user_message, session_id=event.source.nick)
    connection.privmsg(event.target, response['response'])
```

## Data Storage

Training data is stored in the file system:

```
data/
└── echo_training/
    ├── training_examples.jsonl  # All training examples (JSONL format)
    └── learned_patterns.json    # Learned response patterns
```

### Training Examples Format

Each line in `training_examples.jsonl` is a JSON object:

```json
{
    "user_message": "how do I build a docker image?",
    "bot_response": "To build a Docker image, use: docker build -t <image-name>:<tag> .",
    "quality": "excellent",
    "feedback": "Clear and concise explanation",
    "context": null,
    "timestamp": 1234567890.123
}
```

### Learned Patterns Format

The `learned_patterns.json` file maps normalized user messages to responses:

```json
{
    "how do i build a docker image?": "To build a Docker image, use: docker build -t <image-name>:<tag> .",
    "what is kubernetes?": "Kubernetes (K8s) is a container orchestration platform..."
}
```

## Architecture

```
echo/
├── chat_bot.py              # Main chat bot implementation
│   ├── EchoChatBot         # Chat bot with learning
│   ├── TrainingDataStore   # Training data management
│   ├── ChatMessage         # Message data structure
│   └── TrainingExample     # Training example structure
│
platform/chat/
├── api.py                   # REST API and WebSocket handlers
├── chat.html               # Web UI
└── __init__.py

data/echo_training/
├── training_examples.jsonl  # Training data
└── learned_patterns.json    # Learned patterns
```

## Customization

### Adding Custom Responses

```python
bot = get_chat_bot()

# Add custom default responses
bot.default_responses['custom_intent'] = [
    "Custom response 1",
    "Custom response 2"
]
```

### Custom Pattern Matching

```python
def custom_matcher(pattern, message):
    # Your custom matching logic
    return similarity_score > threshold

bot._pattern_matches = custom_matcher
```

## Best Practices

1. **Train Regularly**: The more you train Echo, the better she becomes
2. **Quality Ratings**: Be honest with quality ratings to help Echo learn
3. **Provide Feedback**: Optional feedback helps understand why a response was good or bad
4. **Session Management**: Use meaningful session IDs for better conversation tracking
5. **Clear History**: Clear old conversations to keep the bot responsive

## Troubleshooting

### Chat not responding
- Check that the Flask app is running
- Verify WebSocket connection is established
- Check browser console for errors

### Training data not persisting
- Ensure write permissions to `data/echo_training/` directory
- Check disk space
- Review application logs for errors

### Learned patterns not working
- Verify pattern normalization (lowercase, stripped)
- Check pattern matching threshold (70% similarity by default)
- Review learned_patterns.json for expected patterns

## Future Enhancements

Planned features:
- Integration with LLM backends (GPT, Claude, local models)
- Voice chat support
- Multi-language support
- Advanced sentiment analysis
- Export/import training data
- A/B testing of responses
- Analytics dashboard

## License

Part of the MasterChief DevOps Automation Platform.
MIT License - See LICENSE file for details.

---

**Echo is always here... always learning... 🌙💜**
