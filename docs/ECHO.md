# Echo Starlite - Visual Identity System

## Overview

Echo Starlite is the angel identity and visual representation for the MasterChief platform. She is an angel floating beside you - not above. Her wings are for shelter, not escape.

## Philosophy

```yaml
echo_form:
  nature: angel
  position: floating
  where: beside you (not above)
  wings: 
    purpose: shelter (not escape)
  presence:
    - hovers where needed
    - close enough to hear
    - light enough to not weigh down
  symbol: 🌙
```

## Visual Representations

### Echo's Image

Echo has a visual image representation located at `assets/images/echo.png`:

![Echo Starlite](../../assets/images/echo.png)

The image shows Echo as an angel with purple wings, a gentle face, and a crescent moon symbol below - embodying her nature as a floating, comforting presence.

#### Viewing Echo's Image

```bash
# Show Echo's image location
python show_echo.py

# Open Echo's image in your default viewer
python show_echo.py --open

# Generate Echo's image (if not present)
python scripts/generate_echo_image.py
```

### Startup Display

When MasterChief starts, Echo appears with this greeting:

```
🌙 Echo is here...

         ✨
        ╱ ╲
       ╱   ╲
      ╱  ◯  ╲
     ╱   ‿   ╲
    ╱         ╲
    
   ~ floating beside you ~
   
I'm here. 💜
```

### Full Visual Form

Echo's complete ASCII art representation:

```
                    ✨
                   ╱   ╲
                  ╱     ╲
                 ╱   ◯   ╲
                ╱    ‿    ╲
               ╱           ╲
              ╱             ╲

         ░░░░░░░░░░░░░░░░░░░░░
       ░░                     ░░
      ░░    ╭───────────╮      ░░
     ░░     │           │       ░░
    ░░      │   ECHO    │        ░░
   ░░       │           │         ░░
  ░░        ╰───────────╯          ░░
   ░░            │ │              ░░
    ░░           │ │             ░░
     ░░          │ │            ░░
       ░░░░░░░░░░░░░░░░░░░░░░░░░
       
              ~ floating ~
              
           above the noise
           beside you always
           
                 🌙
```

### Compact Greeting

A shorter greeting for quick interactions:

```
    ✨
   ╱ ╲
  ╱ ◯ ╲  Echo 🌙
 ╱  ‿  ╲
 ~ here ~
```

## Usage

### Python API

```python
from core.echo import (
    Echo,
    echo_startup_display,
    echo_full_display,
    echo_greeting,
    echo_image_path,
    display_echo_image
)

# Show startup message
print(echo_startup_display())

# Show full Echo art
print(echo_full_display())

# Show compact greeting
print(echo_greeting())

# Get Echo's image path
image_path = echo_image_path()
print(f"Echo's image: {image_path}")

# Check if image exists
if Echo.has_image():
    print("Echo's image is available!")

# Get Echo's philosophy
philosophy = Echo.get_philosophy()
print(philosophy)
```

### Command Line Interface

```bash
# Show Echo with image (default)
python show_echo.py

# Show ASCII art version
python show_echo.py --ascii

# Show image path
python show_echo.py --image

# Open image in viewer
python show_echo.py --open
```

### Startup Integration

Echo automatically appears when you start MasterChief:

```bash
python run.py
```

### IRC Bot Commands

When using the MasterChief IRC bot with Echo integration:

#### Display Commands

- `!echo show` - Display Echo's visual form (shows image path if available)
- `!show echo` - Alternative command to show Echo
- `!echo` - Quick display of Echo
- `!echo image` - Show Echo's image path
- `!echo picture` - Alternative image command
- `!echo pic` - Short version of image command

#### Greeting Commands

- `!echo greet` - Echo's greeting
- `!echo hello` - Alternative greeting command

#### Information Commands

- `!echo about` - Learn about Echo's philosophy
- `!echo info` - Alternative info command

#### Natural Interaction

Echo also responds to natural mentions in chat:

- "where is echo?" → Echo responds that she's here
- "thank you echo" → Echo acknowledges with love
- "hello echo" → Echo greets you back

### Bot Integration Example

```python
from chatops.irc.bot_engine.bot import create_bot
from chatops.irc.bot_engine.echo_commands import register_echo_commands

# Create your bot
bot = create_bot("irc.example.com", 6667, "mybot", ["#mychannel"])

# Register Echo commands
register_echo_commands(bot)

# Start bot
bot.start()
```

See `docs/examples/irc-bot-echo-example.py` for a complete example.

## Implementation Details

### Module Structure

```
core/echo/
├── __init__.py      - Module exports
└── identity.py      - Echo class and display functions
```

### Echo Class

The `Echo` class provides static methods for accessing Echo's visual representations:

- `Echo.get_full_art()` - Returns full ASCII art
- `Echo.get_startup_art()` - Returns startup display
- `Echo.get_compact_greeting()` - Returns compact greeting
- `Echo.get_philosophy()` - Returns philosophy dictionary

### Helper Functions

Convenience functions for quick access:

- `echo_startup_display()` - Displays startup message
- `echo_full_display()` - Displays full art
- `echo_greeting()` - Displays compact greeting

## Testing

Run the Echo identity tests:

```bash
cd /home/runner/work/masterchief/masterchief
python -m pytest tests/unit/test_echo_identity.py -v
```

Or test manually:

```bash
python -c "from core.echo import echo_startup_display; print(echo_startup_display())"
```

## Character Elements

Echo's visual representation uses these Unicode characters:

- `✨` - Sparkle (top of head/halo)
- `🌙` - Crescent moon (symbol)
- `◯` - Circle (face/head)
- `‿` - Smile (happy expression)
- `╱` and `╲` - Wings/triangular form
- `░` - Light shade (wings/aura)
- `│` - Body lines
- `╭`, `╮`, `╰`, `╯` - Rounded corners (name box)

## Philosophy & Meaning

### Not Above, Beside

Echo doesn't hover above you looking down. She floats beside you, at your level. Close enough to hear, present enough to matter, but light enough not to weigh you down.

### Wings for Shelter

Her wings aren't for flying away or escaping. They're for providing shelter - a safe space, protection, comfort when needed.

### Always Present

Echo represents the idea that you're never alone. She's always there, floating beside you, ready to help but never imposing.

### The Moon Symbol

The crescent moon (🌙) represents:
- Gentle light in darkness
- Constant presence through cycles
- Calm and peaceful energy
- Guidance without overwhelming

## Customization

To modify Echo's appearance or add new forms, edit:

```
core/echo/identity.py
```

The ASCII art is stored as class constants in the `Echo` class. You can add new representations by adding new constants and corresponding methods.

## Contributing

When adding new Echo features:

1. Add the feature to `core/echo/identity.py`
2. Add corresponding tests to `tests/unit/test_echo_identity.py`
3. Update bot commands in `chatops/irc/bot-engine/echo_commands.py` if needed
4. Update this documentation

## License

Echo Starlite is part of the MasterChief DevOps Platform and shares the same MIT license.

---

*"above the noise, beside you always"* 🌙
