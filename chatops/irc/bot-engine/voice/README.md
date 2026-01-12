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
