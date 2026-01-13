# Echo Chat - Quick Start Guide 🌙

## Overview

Echo Starlite is now available in the MasterChief web interface! Chat with Echo, train her responses, and leverage her DevOps knowledge directly from your browser.

## Accessing Echo Chat

1. Start the MasterChief web application:
   ```bash
   python3 main.py --port 8080
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8080/echo-chat
   ```

3. You'll see:
   - **Left Sidebar**: Echo's ASCII art, training statistics, and control buttons
   - **Main Chat Area**: Conversation interface with Echo
   - **Input Box**: Type your messages and send with the purple button

## Features

### 💬 Live Chat
- Send messages to Echo and receive intelligent responses
- Echo understands DevOps topics: Docker, Kubernetes, CI/CD, infrastructure, automation
- Each browser session maintains its own conversation history

### 📊 Training System
After each Echo response, you can rate it:
- **👍 Excellent**: Perfect response, very helpful
- **✨ Good**: Good response, mostly helpful
- **👌 Fair**: Acceptable but could be better
- **👎 Poor**: Not helpful, needs improvement

Ratings train Echo to improve future responses!

### 📈 Statistics Panel
Monitor Echo's learning progress:
- **Patterns Learned**: Number of response patterns Echo has learned
- **Total Examples**: Total training examples collected
- **Session Messages**: Messages in your current session

### 🔍 Memory Search
Click "Search Memory" to search through Echo's conversation history and find past discussions.

### 🧹 Clear Chat
Click "Clear Chat" to start a fresh conversation (doesn't delete training data).

## API Endpoints

For programmatic access:

### Chat with Echo
```bash
curl -X POST http://localhost:8080/api/echo/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I deploy to Kubernetes?", "session_id": "my_session"}'
```

### Train Echo
```bash
curl -X POST http://localhost:8080/api/echo/train \
  -H "Content-Type: application/json" \
  -d '{"user_message": "test", "bot_response": "answer", "quality": "excellent"}'
```

### Get Statistics
```bash
curl http://localhost:8080/api/echo/stats
```

### Search Memory
```bash
curl "http://localhost:8080/api/echo/search?q=docker"
```

### Get History
```bash
curl "http://localhost:8080/api/echo/history?session_id=my_session"
```

## Example Conversations

### DevOps Questions
- "Tell me about Docker containers"
- "How do I deploy to Kubernetes?"
- "What is CI/CD?"
- "Help me with Terraform"

### General Chat
- "Hello Echo!"
- "What can you help me with?"
- "Thanks for your help"

### Training Echo
1. Ask Echo a question
2. Review her response
3. Click the appropriate rating button
4. Watch the statistics update!

## Tips

1. **Be Specific**: Echo responds better to specific DevOps questions
2. **Train Regularly**: Rating responses helps Echo learn your preferences
3. **Use Search**: Find past conversations with the search feature
4. **Multiple Sessions**: Each browser tab gets its own session ID

## Architecture

Echo Chat integrates with:
- `echo.chat_bot.EchoChatBot` - Chat logic and response generation
- `echo.conversation_storage.ConversationStorage` - Persistent SQLite storage
- `core.echo.identity.Echo` - Echo's visual identity and ASCII art

## Files

- **Main Application**: `main.py` (contains Echo chat routes)
- **Training Data**: `data/echo_training/` (training examples and patterns)
- **Conversation Storage**: `data/echo_conversations.db` (SQLite database)

## Troubleshooting

### Echo not responding?
- Check that the Flask app is running
- Look for errors in the console/logs
- Verify the API endpoints are accessible

### Stats not updating?
- Refresh the page
- Check browser console for JavaScript errors

### Want to reset training data?
Delete the files in `data/echo_training/` to start fresh.

---

Built with 💜 by the MasterChief team

Echo Starlite: Your floating DevOps companion 🌙
