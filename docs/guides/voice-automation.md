# Voice Automation Guide

Complete guide to using voice automation with the MasterChief IRC Bot.

## Overview

The Voice Automation system enables hands-free control of all bot features using natural language voice commands. It includes:

- **Wake Word Detection**: Always-on listening for activation phrases
- **Natural Language Understanding**: Parse commands using local LLM or pattern matching
- **Multi-turn Conversations**: Context-aware interactions
- **Voice Responses**: Speak responses using TTS or cloned voice
- **Action Execution**: Control scripts, deployments, monitoring, and more

## Quick Start

### Prerequisites

1. **Python 3.10+** with required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Microphone Access**: Ensure your system has a working microphone

3. **(Optional) Ollama**: For advanced natural language understanding
   ```bash
   # Install Ollama
   curl https://ollama.ai/install.sh | sh
   
   # Pull a model
   ollama pull mistral
   ```

### Basic Setup

1. **Enable Voice Automation** in `config.yml`:
   ```yaml
   voice:
     automation:
       enabled: true
   ```

2. **Configure Wake Words**:
   ```yaml
   voice:
     automation:
       wake_word:
         words:
           - "hey masterchief"
           - "hey chief"
   ```

3. **Start the Bot**:
   ```python
   from chatops.irc.bot_engine.voice import VoiceAutomation, VoiceAutomationConfig, VoiceConfig
   from addons.scripts.manager import ScriptManager
   
   # Create configuration
   voice_config = VoiceConfig()
   automation_config = VoiceAutomationConfig(voice_config=voice_config)
   
   # Initialize voice automation
   script_manager = ScriptManager()
   automation = VoiceAutomation(automation_config, script_manager)
   
   # Start listening
   automation.start_async()
   ```

## Voice Commands

### Script Management

**Create a Script:**
- "Create a script to backup my database"
- "Make a script to deploy the application"
- "Generate a script for cleaning logs"

**Run a Script:**
- "Run backup_script"
- "Execute the deployment script"

**Schedule a Script:**
- "Schedule backup_script to run every night at 2 AM"
- "Run cleanup_script every Monday"

**List Scripts:**
- "List all scripts"
- "Show me the scripts"
- "What scripts are available?"

**Validate a Script:**
- "Validate backup_script"
- "Check the deployment script"

**Delete a Script:**
- "Delete old_script"
- "Remove backup_script"

### Deployments

**Deploy:**
- "Deploy to production"
- "Push to staging"

**Rollback:**
- "Rollback the user service"
- "Undo the last deployment"

**Check Status:**
- "What's the deployment status?"
- "Show me deployment info"

### Monitoring & Status

**System Status:**
- "What's the system status?"
- "How are the servers?"

**Metrics:**
- "Show me CPU usage"
- "What's the memory usage?"

**Alerts:**
- "Are there any alerts?"
- "Check for alerts"

**Logs:**
- "Read me the recent logs"
- "Show the latest logs"

### Bot Control

**Stop Listening:**
- "That's all"
- "Stop listening"
- "Go to sleep"
- "Thanks, goodbye"

**Help:**
- "What can you do?"
- "Help"
- "Show me commands"

## Configuration

### Wake Word Settings

```yaml
voice:
  automation:
    wake_word:
      engine: openwakeword  # openwakeword, porcupine, or whisper
      words:
        - "hey masterchief"
        - "hey chief"
        - "okay masterchief"
      sensitivity: 0.5  # 0.0 (less sensitive) to 1.0 (more sensitive)
```

### Conversation Settings

```yaml
voice:
  automation:
    conversation:
      timeout: 30  # Seconds of silence before returning to passive
      context_window: 10  # Number of conversation turns to remember
      confirm_critical: true  # Require confirmation for critical actions
```

### Response Settings

```yaml
voice:
  automation:
    response:
      use_master_voice: false  # Use cloned voice (requires setup)
      speak_confirmations: true  # Speak "listening" confirmations
      play_feedback_sounds: true  # Play audio chimes
```

### LLM Settings

```yaml
voice:
  automation:
    llm:
      model: mistral  # Ollama model name
      ollama_url: http://localhost:11434
```

## Advanced Usage

### Using with IRC

Voice automation can be triggered via IRC commands:

```python
from chatops.irc.bot_engine.bot import IRCBot

bot = IRCBot("irc.example.com", 6667, "MasterChief", ["#devops"])

# Start voice automation
def start_voice(connection, event, args):
    automation.start_async()
    connection.privmsg(event.target, "🎤 Voice automation started")

bot.bind("pub", "-|-", "!voice start", start_voice)

# Process text commands via IRC
def voice_command(connection, event, args):
    text = " ".join(args)
    response = automation.process_text_command(text)
    connection.privmsg(event.target, response)

bot.bind("pub", "-|-", "!voice", voice_command)
```

### Custom Wake Words

Add custom wake words at runtime:

```python
automation.wake_word.add_wake_word("hey bot")
automation.wake_word.remove_wake_word("okay masterchief")
```

### Voice Cloning (Future)

To use a cloned voice for responses:

1. Record voice samples
2. Train the voice model
3. Enable in configuration:
   ```yaml
   voice:
     automation:
       response:
         use_master_voice: true
   ```

## Troubleshooting

### Microphone Not Working

1. **Check System Permissions**: Ensure the application has microphone access
2. **Test Recording**:
   ```python
   from chatops.irc.bot_engine.voice.base import VoiceEngine, VoiceConfig
   
   engine = VoiceEngine(VoiceConfig())
   engine.initialize()
   audio = engine.listen(timeout=5)
   print(f"Recorded {len(audio)} bytes")
   ```

3. **List Audio Devices**:
   ```python
   import sounddevice as sd
   print(sd.query_devices())
   ```

4. **Specify Device**:
   ```python
   config = VoiceConfig(device_index=1)  # Use device 1
   ```

### Wake Word Not Detected

1. **Test Wake Word Detection**:
   ```python
   text = "hey masterchief what's up"
   detected = automation.wake_word.detect_in_text(text)
   print(f"Detected: {detected}")
   ```

2. **Adjust Sensitivity**:
   ```yaml
   wake_word:
     sensitivity: 0.7  # Increase for more detections
   ```

3. **Use Simpler Wake Words**: Single words are easier to detect

### Speech Recognition Errors

1. **Check Whisper Installation**:
   ```bash
   pip install openai-whisper
   ```

2. **Try Different Model**:
   ```python
   config = VoiceConfig(stt_model="tiny")  # Faster but less accurate
   # or
   config = VoiceConfig(stt_model="base")  # Default
   # or
   config = VoiceConfig(stt_model="small")  # More accurate
   ```

3. **Improve Audio Quality**: Use a better microphone or reduce background noise

### Text-to-Speech Not Working

1. **Check TTS Installation**:
   ```bash
   pip install pyttsx3
   ```

2. **Test TTS**:
   ```python
   engine = VoiceEngine(VoiceConfig())
   engine.initialize()
   engine.speak("Hello world")
   ```

3. **List Available Voices**:
   ```python
   import pyttsx3
   engine = pyttsx3.init()
   voices = engine.getProperty('voices')
   for voice in voices:
       print(f"{voice.id}: {voice.name}")
   ```

### LLM Not Available

If Ollama is not available, the system automatically falls back to pattern matching. This works well for most commands but may be less flexible with natural language variations.

To enable LLM:
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull mistral`
3. Verify it's running: `curl http://localhost:11434/api/tags`

## Architecture

```
Voice Automation System
├── Wake Word Detection
│   ├── OpenWakeWord (local, efficient)
│   ├── Porcupine (commercial, accurate)
│   └── Whisper (flexible, slower)
├── Speech-to-Text
│   └── OpenAI Whisper (local, accurate)
├── Natural Language Understanding
│   ├── Ollama LLM (flexible)
│   └── Pattern Matching (fallback)
├── Action Execution
│   ├── Script Management
│   ├── Deployments
│   ├── Monitoring
│   └── System Control
├── Response Generation
│   ├── Template-based
│   └── Context-aware
└── Text-to-Speech
    ├── pyttsx3 (local)
    └── Voice Cloning (future)
```

## Security Considerations

1. **Local Processing**: All voice processing happens locally - no cloud APIs
2. **Confirmation Required**: Critical actions (delete, deploy, rollback) require confirmation
3. **Microphone Privacy**: Disable when not needed
4. **Access Control**: Integrate with IRC bot permission system

## Performance Tips

1. **Use Smaller Models**: 
   - Whisper "tiny" for faster transcription
   - Consider OpenWakeWord for efficient wake word detection

2. **Adjust Timeouts**:
   ```yaml
   conversation:
     timeout: 15  # Shorter timeout for faster return to passive
   ```

3. **Disable Feedback Sounds** if not needed:
   ```yaml
   response:
     play_feedback_sounds: false
   ```

4. **CPU Usage**: Wake word detection runs continuously but should use minimal CPU (<5%)

## Examples

### Example 1: Complete Workflow

```
[System is in passive listening mode]

User: "Hey MasterChief"
Bot: *chime* "Listening..."

User: "Create a script to backup postgres to S3"
Bot: "Creating a postgres backup script with S3 upload..."
     "Done. I've created backup_postgres_s3.sh. Would you like me to validate it?"

User: "Yes please"
Bot: "Validating script... Script passed all checks. Would you like to schedule it?"

User: "Yes, run it every night at 2 AM"
Bot: "Scheduled backup_postgres_s3.sh to run daily at 2 AM. First run will be tonight."

User: "Thanks, that's all"
Bot: "Standing by."
     *sleep chime*

[Returns to passive listening]
```

### Example 2: System Monitoring

```
User: "Hey Chief"
Bot: "Listening..."

User: "What's the system status?"
Bot: "All systems operational. CPU at 23%, memory at 45%, disk at 67%. No active alerts."

User: "Check for alerts"
Bot: "No active alerts. All systems are operational."

User: "That's all"
Bot: "Standing by."
```

### Example 3: Deployment

```
User: "Hey MasterChief"
Bot: "Listening..."

User: "Deploy to staging"
Bot: "You want me to deploy to staging. Is that correct? Say yes or no."

User: "Yes"
Bot: "Deployment to staging started. Deployment in progress."

User: "What's the deployment status?"
Bot: "Current deployment: completed. Last deployment was 3 hours ago."

User: "Done"
Bot: "Standing by."
```

## Future Enhancements

- Voice cloning for personalized responses
- Multi-language support
- Custom command training
- Integration with more services (Kubernetes, AWS, etc.)
- Web interface for voice control
- Mobile app support

## Support

For issues or questions:
- Check the troubleshooting section above
- Review logs: `tail -f /var/log/masterchief/voice.log`
- Report issues on GitHub: https://github.com/jbalestrine/masterchief/issues

## License

MIT License - See LICENSE file for details
