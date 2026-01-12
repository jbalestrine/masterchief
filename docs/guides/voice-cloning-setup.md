# Voice Cloning Setup Guide

This guide will help you set up and use the voice cloning system with MasterChief IRC Bot.

## Overview

The voice cloning system allows you to clone your own voice and use it as the bot's "master voice" persona. The bot will speak in YOUR voice when making announcements, responding to commands, or providing feedback.

## Supported Engines

The system supports three voice cloning engines:

### 1. XTTS/Coqui TTS (Recommended)
- **Best for:** Balance of quality and speed
- **Sample duration:** 6-10 seconds
- **Processing speed:** Real-time
- **Quality:** Excellent
- **Languages:** Multilingual support

### 2. Tortoise TTS
- **Best for:** Highest quality output
- **Sample duration:** 1-3 minutes
- **Processing speed:** Slower
- **Quality:** Superior
- **Languages:** English (primary)

### 3. OpenVoice
- **Best for:** Fast setup
- **Sample duration:** 30 seconds
- **Processing speed:** Fastest
- **Quality:** Good
- **Languages:** Multiple languages

## Hardware Requirements

### Minimum Requirements
- **CPU:** Multi-core processor (4+ cores recommended)
- **RAM:** 8 GB
- **Storage:** 5 GB free space
- **OS:** Linux, macOS, or Windows

### Recommended Requirements
- **GPU:** NVIDIA GPU with CUDA support (significantly faster)
- **RAM:** 16 GB or more
- **Storage:** 10 GB free space

## Installation

### 1. Install Dependencies

```bash
# Install the voice cloning dependencies
pip install -r requirements.txt
```

The requirements include:
- `TTS>=0.22.0` - XTTS/Coqui TTS
- `tortoise-tts>=3.0.0` - Tortoise TTS
- `torch>=2.0.0` - Deep learning framework
- `librosa>=0.10.0` - Audio processing
- `soundfile>=0.12.1` - Audio I/O
- `sounddevice` - Audio recording (for interactive recording)

### 2. GPU Setup (Optional but Recommended)

If you have an NVIDIA GPU:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

The system will automatically detect and use GPU if available.

## Quick Start

### Step 1: Record Your Voice Samples

Use the interactive recording tool:

```bash
python -m chatops.irc.bot_engine.voice.cloning record-samples \
    --output ./my_voice_samples/ \
    --num-samples 5 \
    --duration 10
```

This will guide you through recording 5 samples, each 10 seconds long.

**Tips for good recordings:**
- Use a quiet environment
- Speak naturally and clearly
- Read the prompts with consistent volume
- Use a good quality microphone
- Vary your tone across samples

### Step 2: Create Your Master Voice

```bash
python -m chatops.irc.bot_engine.voice.cloning create-master \
    --name "my-persona" \
    --files ./my_voice_samples/*.wav \
    --engine xtts
```

This creates your voice profile and sets it as the master voice.

### Step 3: Test Your Voice

```bash
python -m chatops.irc.bot_engine.voice.cloning test \
    --text "Hello, this is my master voice speaking!"
```

The synthesized audio will be saved to `test_output.wav`.

## Using with IRC Bot

### Basic Integration

```python
from chatops.irc.bot_engine import create_bot
from chatops.irc.bot_engine.voice.cloning import VoiceCloner
from chatops.irc.bot_engine.voice.base import VoiceCloningConfig

# Initialize voice cloner
config = VoiceCloningConfig(
    profiles_dir="./voice_profiles/",
    engine="xtts",
    device="auto"
)
cloner = VoiceCloner(config)

# Create IRC bot
bot = create_bot("irc.libera.chat", 6667, "masterchief", ["#devops"])

# Define command handler with voice
def announce(connection, event, args):
    message = " ".join(args)
    cloner.speak_as_master(message, output_file=f"announcements/{message[:20]}.wav")
    connection.privmsg(event.target, f"🔊 {message}")

# Bind command
bot.bind("pub", "-|-", "!announce", announce)

# Start bot
bot.start()
```

### Advanced Usage

```python
# Create multiple voice personas
cloner.clone_voice(
    name="alert-voice",
    audio_files=["alert_sample1.wav", "alert_sample2.wav"],
    engine="xtts"
)

cloner.clone_voice(
    name="friendly-voice",
    audio_files=["friendly1.wav", "friendly2.wav"],
    engine="xtts"
)

# Use different voices for different contexts
def alert_handler(connection, event, args):
    alert_profile = cloner.get_profile("alert-voice")
    alert_profile.speak("Alert: Something needs attention!", cloner)
    
def welcome_handler(connection, event, args):
    friendly_profile = cloner.get_profile("friendly-voice")
    friendly_profile.speak("Welcome to the channel!", cloner)
```

## Configuration

### YAML Configuration

```yaml
voice:
  cloning:
    enabled: true
    profiles_dir: ./voice_profiles/
    samples_dir: ./voice_samples/
    
    master_voice:
      name: my-persona
      engine: xtts
      
    xtts:
      model: tts_models/multilingual/multi-dataset/xtts_v2
      device: auto  # cuda, cpu, or auto
      
    tortoise:
      model: tortoise-tts
      preset: fast  # ultra_fast, fast, standard, high_quality
      device: auto
      
    openvoice:
      model: openvoice
      device: auto
```

### Python Configuration

```python
from chatops.irc.bot_engine.voice.base import VoiceCloningConfig

config = VoiceCloningConfig(
    enabled=True,
    profiles_dir="./voice_profiles/",
    samples_dir="./voice_samples/",
    device="cuda",  # Force GPU usage
    engine="xtts",
    xtts_model="tts_models/multilingual/multi-dataset/xtts_v2",
    master_voice_name="my-persona"
)
```

## CLI Commands Reference

### Record Voice Samples
```bash
python -m chatops.irc.bot_engine.voice.cloning record-samples \
    [--output ./voice_samples/] \
    [--num-samples 5] \
    [--duration 10]
```

### Create Master Voice
```bash
python -m chatops.irc.bot_engine.voice.cloning create-master \
    --name <profile-name> \
    --files <audio-files> \
    [--engine xtts|tortoise|openvoice]
```

### List Profiles
```bash
python -m chatops.irc.bot_engine.voice.cloning list-profiles
```

### Test Voice
```bash
python -m chatops.irc.bot_engine.voice.cloning test \
    --text "Text to speak" \
    [--output output.wav]
```

### Set Master Voice
```bash
python -m chatops.irc.bot_engine.voice.cloning set-master \
    --name <profile-name>
```

## Troubleshooting

### Common Issues

#### 1. GPU Not Detected

**Problem:** System using CPU even though GPU is available.

**Solution:**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 2. Poor Voice Quality

**Problem:** Generated voice doesn't sound like you.

**Solutions:**
- Record more samples (10+ recommended)
- Use longer recordings (15-20 seconds per sample)
- Ensure consistent audio quality across samples
- Try different engines (Tortoise for highest quality)
- Use a better microphone

#### 3. Out of Memory Errors

**Problem:** "CUDA out of memory" or similar errors.

**Solutions:**
```python
# Use CPU instead
config = VoiceCloningConfig(device="cpu")

# Or reduce model size (engine-specific)
```

#### 4. Slow Generation

**Problem:** Voice synthesis takes too long.

**Solutions:**
- Use GPU if available
- Use faster engine (XTTS or OpenVoice)
- For Tortoise, use faster preset:
```python
config = VoiceCloningConfig(
    engine="tortoise",
    tortoise_preset="ultra_fast"
)
```

#### 5. Audio Recording Issues

**Problem:** Can't record audio samples.

**Solution:**
```bash
# Install audio dependencies
pip install sounddevice scipy soundfile

# Test microphone
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Getting Help

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify all dependencies are installed correctly
3. Test with simple examples before complex integrations
4. Check hardware compatibility (especially for GPU usage)

## Best Practices

### Recording Voice Samples

1. **Environment:** Record in a quiet room with minimal echo
2. **Microphone:** Use a good quality microphone (USB or XLR)
3. **Distance:** Maintain consistent distance from microphone
4. **Volume:** Speak at normal conversational volume
5. **Variety:** Include different emotions and tones
6. **Length:** Provide sufficient sample length for engine requirements

### Voice Profile Management

1. **Naming:** Use descriptive names for profiles
2. **Organization:** Keep profiles organized by purpose
3. **Backup:** Back up voice profiles regularly
4. **Testing:** Test profiles before using in production
5. **Versioning:** Keep different versions for comparison

### Performance Optimization

1. **GPU Usage:** Always use GPU when available
2. **Batch Processing:** Pre-generate common announcements
3. **Caching:** Cache frequently used voice outputs
4. **Engine Selection:** Choose engine based on use case
   - Real-time responses: XTTS or OpenVoice
   - Pre-recorded announcements: Tortoise

## Security Considerations

1. **Privacy:** Voice profiles contain biometric data
2. **Storage:** Secure voice profile storage
3. **Access Control:** Limit who can create/modify profiles
4. **Consent:** Only clone voices with proper consent

## Next Steps

- Explore the [API Reference](../api/voice-cloning.md)
- Check out [Examples](../examples/voice-cloning-example.py)
- Read about [Advanced Features](./voice-cloning-advanced.md)
- Join our community for support

## Additional Resources

- [Coqui TTS Documentation](https://github.com/coqui-ai/TTS)
- [Tortoise TTS Documentation](https://github.com/neonbjb/tortoise-tts)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)
