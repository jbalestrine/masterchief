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
# Voice Cloning Module

Comprehensive voice cloning system for the MasterChief IRC Bot, allowing you to clone your own voice and use it as the bot's "master voice" persona.

## Features

- **Multiple Engines**: Support for XTTS/Coqui TTS, Tortoise TTS, and OpenVoice
- **Master Voice**: Create a primary voice persona for your bot
- **Profile Management**: Save and manage multiple voice profiles
- **Interactive Recording**: Built-in voice sample recording system
- **CLI Tools**: Command-line interface for all operations
- **100% Local**: All processing is done locally, no cloud APIs

## Quick Start

### 1. Install Dependencies
# Voice/Audio System for IRC Bot

A comprehensive local voice and audio system for the MasterChief IRC Bot, enabling text-to-speech, speech-to-text, audio recording, and event-based announcements - all running locally without cloud dependencies.

## Features

### 🎙️ Text-to-Speech (TTS)
- Convert bot responses to spoken audio using `pyttsx3`
- Cross-platform support (Windows, macOS, Linux)
- Configurable voice, rate, and volume
- Queue-based speech synthesis for multiple requests
- Optional audio file output

### 🎧 Speech-to-Text (STT)
- Transcribe voice input using OpenAI Whisper (local)
- Multiple model sizes: tiny, base, small, medium, large
- High-quality transcription with multi-language support
- Real-time transcription from microphone
- Audio file transcription support

### 🔴 Audio Recording
- Record audio from microphone using `sounddevice`
- Voice Activity Detection (VAD) for auto-start/stop
- Configurable sample rate and quality
- Support for WAV, MP3, OGG formats
- Fixed-duration or VAD-based recording

### 🔊 Audio Playback
- Play audio files using `pygame`
- Support for WAV, MP3, OGG formats
- Volume control and playback management
- Async playback support

### 📢 Event Announcements
- Event-triggered audio announcements
- Pre-configured sounds for deployments, alerts, errors
- Simple event registration system
- Integration with IRC bot events

## Installation

### Important Note About Module Path

The bot engine directory is named `bot-engine` (with a hyphen), but Python imports require underscores. If you encounter import errors, you have two options:

**Option 1: Install as package (recommended)**
```bash
cd /path/to/masterchief
pip install -e .
```

**Option 2: Direct import**
```python
import sys
sys.path.insert(0, '/path/to/masterchief')
# Now imports will work
from chatops.irc.bot_engine import create_bot
```

**Option 3: Rename directory**
```bash
mv chatops/irc/bot-engine chatops/irc/bot_engine
```

### Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Record Voice Samples

```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py record-samples \
    --output ./my_samples/ \
    --num-samples 5 \
    --duration 10
```

### 3. Create Master Voice

```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py create-master \
    --name "my-persona" \
    --files ./my_samples/*.wav \
    --engine xtts
```

### 4. Test Your Voice

```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py test \
    --text "Hello, I am speaking in your voice!"
```

## Usage with IRC Bot

```python
import sys
from pathlib import Path
import importlib.util

# Load modules
bot_engine_path = Path("chatops/irc/bot-engine")

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

voice_base = load_module("voice.base", bot_engine_path / "voice" / "base.py")
voice_cloner_module = load_module("voice.cloning.voice_cloner", 
                                  bot_engine_path / "voice" / "cloning" / "voice_cloner.py")

VoiceCloningConfig = voice_base.VoiceCloningConfig
VoiceCloner = voice_cloner_module.VoiceCloner

# Configure and use
config = VoiceCloningConfig(
    profiles_dir="./voice_profiles/",
    engine="xtts",
    device="auto"
)

cloner = VoiceCloner(config)
cloner.speak_as_master("Hello from the bot!")
```

## CLI Commands

### Record Samples
```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py record-samples [options]
```

### Create Master Voice
```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py create-master \
    --name <name> --files <files> [--engine xtts|tortoise|openvoice]
```

### List Profiles
```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py list-profiles
```

### Test Voice
```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py test --text <text>
```

### Set Master Voice
```bash
python chatops/irc/bot-engine/voice/cloning/__main__.py set-master --name <name>
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
- [Voice Cloning Setup Guide](../../docs/guides/voice-cloning-setup.md)
- [Example Usage](../../docs/examples/voice-cloning-example.py)
- [CHANGELOG](../../CHANGELOG.md)

## Testing

```bash
python -m unittest tests.unit.test_voice.test_cloning.test_base
python -m unittest tests.unit.test_voice.test_cloning.test_voice_profile
python -m unittest tests.unit.test_voice.test_cloning.test_voice_cloner
```

All 37 unit tests should pass.
Voice/audio dependencies:
```bash
# Text-to-Speech
pip install pyttsx3>=2.90

# Speech-to-Text (Whisper)
pip install openai-whisper>=20231117

# Audio Recording
pip install sounddevice>=0.4.6 soundfile>=0.12.1

# Audio Playback
pip install pygame>=2.5.0

# Voice Activity Detection
pip install webrtcvad>=2.0.10

# Audio Processing
pip install numpy>=1.24.0 scipy>=1.10.0
```

### System Requirements

**Linux:**
```bash
# Install system audio libraries
sudo apt-get install portaudio19-dev python3-pyaudio espeak ffmpeg
```

**macOS:**
```bash
# Install using Homebrew
brew install portaudio ffmpeg
```

**Windows:**
- No additional system packages required
- Built-in SAPI5 for TTS

## Quick Start

### Basic Usage

```python
from chatops.irc.bot_engine import create_bot
from chatops.irc.bot_engine.voice import VoiceEngine, VoiceConfig

# Create voice engine
voice_config = VoiceConfig()
voice = VoiceEngine(voice_config)

# Create IRC bot
bot = create_bot("irc.libera.chat", 6667, "mybot", ["#mychannel"])

def say_handler(connection, event, args):
    """Bot speaks text."""
    text = " ".join(args)
    voice.speak(text)
    connection.privmsg(event.target, f"🔊 Speaking: {text}")

# Register command
bot.bind("pub", "-|-", "!say", say_handler)

# Start bot
bot.start()
```

### Voice Configuration

```python
from chatops.irc.bot_engine.voice import VoiceConfig

config = VoiceConfig(
    enabled=True,
    tts=dict(
        enabled=True,
        rate=150,        # Words per minute
        volume=0.9,      # 0.0 to 1.0
        voice=None       # Or specific voice ID
    ),
    stt=dict(
        enabled=True,
        model="base",    # tiny, base, small, medium, large
        language="en",
        device="cpu"     # or "cuda" for GPU
    ),
    recorder=dict(
        enabled=True,
        sample_rate=16000,
        channels=1,
        vad_enabled=True,
        vad_aggressiveness=2  # 0-3, higher = more aggressive
    ),
    player=dict(
        enabled=True,
        volume=0.8
    ),
    announcements=dict(
        enabled=True,
        directory="./sounds",
        events={
            "deploy_success": "success.wav",
            "deploy_failure": "failure.wav",
            "alert_critical": "alert.wav"
        }
    )
)

voice = VoiceEngine(VoiceConfig.from_dict(config.__dict__))
```

## IRC Bot Integration

### New Bind Types

The voice system adds three new bind types to the IRC bot:

```python
bot.bind("tts", "-|-", "!say", tts_handler)        # Text-to-speech
bot.bind("voice", "-|-", "!listen", voice_handler)  # Voice commands
bot.bind("audio", "-|-", "event", audio_handler)    # Audio playback
```

### Example Commands

```python
def tts_handler(connection, event, args):
    """Handle !say command - bot speaks text."""
    text = " ".join(args)
    voice.speak(text)

def voice_handler(connection, event, args):
    """Handle !listen command - listen and transcribe."""
    text = voice.listen(duration=5)
    if text:
        connection.privmsg(event.target, f"Heard: {text}")

def deploy_handler(connection, event, args):
    """Deploy with voice announcement."""
    env = args[0] if args else "production"
    voice.speak(f"Starting deployment to {env}")
    # ... perform deployment ...
    voice.announce("deploy_success")

# Register handlers
bot.bind("pub", "-|-", "!say", tts_handler)
bot.bind("pub", "-|-", "!listen", voice_handler)
bot.bind("pub", "-|-", "!deploy", deploy_handler)
```

## Voice System API

### VoiceEngine

Main class that coordinates all voice components.

```python
# Initialization
voice = VoiceEngine(config)
voice.initialize()  # Lazy initialization

# Text-to-Speech
voice.speak("Hello world")
voice.speak("Save this", save_to_file="greeting.wav")

# Speech-to-Text
text = voice.listen(duration=5)  # Fixed duration
text = voice.listen()            # VAD-based (auto-stop on silence)

# Recording
voice.record("recording.wav", duration=10)

# Playback
voice.play("audio.wav")

# Announcements
voice.announce("deploy_success")

# Cleanup
voice.shutdown()
```

### TTSEngine

Text-to-speech functionality.

```python
from chatops.irc.bot_engine.voice.tts import TTSEngine
from chatops.irc.bot_engine.voice.base import TTSConfig

config = TTSConfig(rate=150, volume=1.0)
tts = TTSEngine(config)

# Speak text
tts.speak("Hello world")

# List available voices
voices = tts.get_available_voices()
for voice in voices:
    print(f"{voice['name']}: {voice['id']}")

# Change voice
tts.set_voice("voice_id")

# Adjust settings
tts.set_rate(200)    # Words per minute
tts.set_volume(0.5)  # 0.0 to 1.0
```

### STTEngine

Speech-to-text transcription.

```python
from chatops.irc.bot_engine.voice.stt import STTEngine
from chatops.irc.bot_engine.voice.base import STTConfig

config = STTConfig(model="base", language="en")
stt = STTEngine(config)

# Transcribe audio file
text = stt.transcribe_file("audio.wav")

# Transcribe raw audio data
audio_bytes = b"..."  # Raw audio data
text = stt.transcribe_realtime(audio_bytes, sample_rate=16000)

# Change model
stt.change_model("small")

# Available models
models = stt.get_available_models()
# ['tiny', 'base', 'small', 'medium', 'large']
```

### AudioRecorder

Audio recording with VAD.

```python
from chatops.irc.bot_engine.voice.recorder import AudioRecorder
from chatops.irc.bot_engine.voice.base import RecorderConfig

config = RecorderConfig(sample_rate=16000, vad_enabled=True)
recorder = AudioRecorder(config)

# Fixed duration recording
audio_file = recorder.record(duration=10)

# VAD-based recording (stops on silence)
audio_file = recorder.record()

# Stop recording early
recorder.stop_recording()

# List audio devices
devices = recorder.get_devices()
```

### AudioPlayer

Audio playback.

```python
from chatops.irc.bot_engine.voice.player import AudioPlayer
from chatops.irc.bot_engine.voice.base import PlayerConfig

config = PlayerConfig(volume=0.8)
player = AudioPlayer(config)

# Play audio (blocking)
player.play("audio.wav", blocking=True)

# Play audio (non-blocking)
player.play("audio.wav")

# Play async in separate thread
player.play_async("audio.wav")

# Playback control
player.pause()
player.resume()
player.stop()

# Volume control
player.set_volume(0.5)

# Check status
is_playing = player.is_playing()
```

### AnnouncementManager

Event-based announcements.

```python
from chatops.irc.bot_engine.voice.announcements import AnnouncementManager
from chatops.irc.bot_engine.voice.base import AnnouncementConfig

config = AnnouncementConfig(
    directory="./sounds",
    events={"deploy_success": "success.wav"}
)
manager = AnnouncementManager(config, player)

# Register event
manager.register_event("deploy_failure", "failure.wav")

# Play announcement
manager.announce("deploy_success")

# Check if event registered
has_event = manager.has_event("deploy_success")

# Get all events
events = manager.get_registered_events()

# Unregister event
manager.unregister_event("deploy_failure")
```

## Whisper Models

| Model  | Parameters | Size  | Speed | Accuracy |
|--------|-----------|-------|-------|----------|
| tiny   | 39M       | ~75MB | Fast  | Low      |
| base   | 74M       | ~142MB| Fast  | Medium   |
| small  | 244M      | ~466MB| Medium| Good     |
| medium | 769M      | ~1.5GB| Slow  | High     |
| large  | 1550M     | ~2.9GB| Slow  | Highest  |

**Recommendation:** Start with `base` for good balance of speed and accuracy.

## Troubleshooting

### TTS Not Working

```python
# List available voices
voice.initialize()
voices = voice._tts_engine.get_available_voices()
print(voices)

# Try a different voice
voice._tts_engine.set_voice(voices[0]['id'])
```

### Audio Device Issues

```python
# List audio devices
voice.initialize()
devices = voice._recorder.get_devices()
print(devices)
```

### Whisper Model Download

First time running STT will download the Whisper model:
```
Downloading model...
100%|████████████████████████| 145M/145M [00:30<00:00, 4.83MB/s]
Model loaded successfully
```

Models are cached in `~/.cache/whisper/`

### Permission Errors

**Linux/macOS:**
```bash
# Grant microphone access
# System Settings > Privacy & Security > Microphone
```

**Windows:**
```
Settings > Privacy > Microphone > Allow apps to access microphone
```

## Performance Tips

1. **Use smaller Whisper models** for real-time transcription (`tiny` or `base`)
2. **Enable VAD** for more efficient recording
3. **Use GPU** for faster Whisper transcription (set `device="cuda"`)
4. **Queue TTS** requests instead of blocking

## Architecture

```
voice/
├── __init__.py              # Base module exports
├── base.py                  # Configuration classes
└── cloning/
    ├── __init__.py          # Cloning module exports
    ├── __main__.py          # CLI entry point
    ├── base.py              # Base voice cloner interface
    ├── xtts_cloner.py       # XTTS/Coqui implementation
    ├── tortoise_cloner.py   # Tortoise TTS implementation
    ├── openvoice_cloner.py  # OpenVoice implementation
    ├── voice_profile.py     # Profile management
    ├── trainer.py           # Training utilities
    └── voice_cloner.py      # Main orchestrator
```

## Requirements

- Python 3.8+
- torch >= 2.0.0
- TTS >= 0.22.0 (XTTS/Coqui)
- tortoise-tts >= 3.0.0
- librosa >= 0.10.0
- soundfile >= 0.12.1
- sounddevice >= 0.4.6 (for recording)

## License

See repository LICENSE file.
VoiceEngine
├── TTSEngine (pyttsx3)
│   ├── Voice selection
│   ├── Queue-based synthesis
│   └── Audio output
├── STTEngine (Whisper)
│   ├── Model loading
│   ├── Transcription
│   └── Language detection
├── AudioRecorder (sounddevice)
│   ├── Microphone capture
│   ├── VAD integration
│   └── File output
├── AudioPlayer (pygame)
│   ├── Audio loading
│   ├── Playback control
│   └── Volume management
├── VoiceActivityDetector (webrtcvad)
│   ├── Speech detection
│   └── Silence detection
└── AnnouncementManager
    ├── Event mapping
    └── Audio playback
```

## Examples

See [`docs/examples/voice-bot-example.py`](../examples/voice-bot-example.py) for a complete working example.

## License

Part of the MasterChief Enterprise DevOps Platform.
