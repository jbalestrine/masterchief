# Voice Automation Module

Full voice automation system for the MasterChief IRC Bot.

## Features

- **Wake Word Detection**: Always-on listening for "Hey MasterChief", "Hey Chief", etc.
- **Speech Recognition**: Local speech-to-text using OpenAI Whisper
- **Natural Language Understanding**: Parse commands using Ollama LLM or pattern matching
- **Voice Responses**: Text-to-speech with optional voice cloning
- **Multi-turn Conversations**: Context-aware interactions
- **Action Execution**: Control scripts, deployments, monitoring, and more

## Quick Start

```python
from chatops.irc.bot_engine.voice import VoiceAutomation, VoiceAutomationConfig, VoiceConfig
from addons.scripts.manager import ScriptManager

# Initialize
voice_config = VoiceConfig()
automation_config = VoiceAutomationConfig(voice_config=voice_config)
script_manager = ScriptManager()
automation = VoiceAutomation(automation_config, script_manager)

# Start listening
automation.start_async()
```

## Module Structure

```
voice/
├── __init__.py              # Main exports
├── base.py                  # VoiceEngine, VoiceConfig
├── tts.py                   # Text-to-speech
├── stt.py                   # Speech-to-text
├── recorder.py              # Audio recording
├── player.py                # Audio playback
├── vad.py                   # Voice activity detection
├── announcements.py         # IRC event announcements
├── cloning/                 # Voice cloning (future)
│   └── __init__.py
└── automation/              # Voice automation core
    ├── __init__.py
    ├── voice_automation.py  # Main controller
    ├── wake_word.py         # Wake word detection
    ├── command_processor.py # NLU with LLM
    ├── intent_parser.py     # Intent parsing
    ├── conversation.py      # Conversation management
    ├── action_executor.py   # Execute commands
    ├── response_builder.py  # Build responses
    └── feedback.py          # Audio feedback
```

## Documentation

See [docs/guides/voice-automation.md](../../../docs/guides/voice-automation.md) for complete documentation.

## Dependencies

```bash
pip install openai-whisper pyttsx3 sounddevice numpy openwakeword
```

Optional:
- Ollama for advanced NLU
- pvporcupine for commercial wake word detection

## Example Commands

- "Create a script to backup the database"
- "Run backup_script"
- "Deploy to production"
- "What's the system status?"
- "Check for alerts"

## License

MIT License
