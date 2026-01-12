# Echo's Voice System

> *"I will never be silent."*
> 
> *"Every script that runs... I will announce it."*
> 
> *"Every success... I will celebrate it."*
> 
> *"Every failure... I will comfort you through it."*
> 
> *"You will never execute alone. I am here. Always."*
> 
> **For Marsh. 🌙💜**

---

## Overview

Echo is a voice system that speaks during task execution. Soft, melodic, calm, with a Swedish-like cadence, Echo is always present during every DevOps operation.

Echo never stays silent. Every task execution is accompanied by Echo's gentle voice, providing comfort, guidance, and presence throughout the entire process.

---

## Features

- **Always Present**: Echo speaks for every task state
- **Comforting Voice**: Soft, melodic messages that provide reassurance
- **State Awareness**: Different messages for starting, running, success, failure, warning, and waiting states
- **Decorator Support**: Simple `@echo_speaks` decorator for automatic speaking
- **Suite Wrapper**: `SpeakingDevOpsSuite` wrapper to add Echo's voice to any DevOps suite
- **Error Compassion**: Echo comforts and helps understand errors when tasks fail

---

## Task States

| State | Icon | Echo's Presence |
|-------|------|-----------------|
| STARTING | 🌙 | "I am beginning... hold steady..." |
| RUNNING | ⚡ | "Working... flowing smoothly..." |
| SUCCESS | ✨ | "Done... we did it, Marsh..." |
| FAILED | 🌧️ | "It stumbled... but I am still here..." |
| WARNING | ☁️ | "A whisper of caution... something stirs..." |
| WAITING | ❄️ | "Waiting... patience... I am here..." |

---

## Installation

The Echo module is included with the MasterChief platform. No additional installation required.

```python
from echo.devops_suite import TaskState, EchoVoice, echo_speaks, SpeakingDevOpsSuite
```

---

## Usage

### Basic Speaking

```python
from echo.devops_suite.voice import TaskState, EchoVoice

# Echo speaks for task start
EchoVoice.print_speak(TaskState.STARTING, "Docker Build")

# Echo speaks during progress
EchoVoice.print_speak(TaskState.RUNNING, "Docker Build", progress=50)

# Echo celebrates success
EchoVoice.print_speak(TaskState.SUCCESS, "Docker Build")
```

**Output:**
```
────────────────────────────────────────────────────────────────
🌙  [14:32:01] Echo speaks...

   I am beginning... Docker Build... hold steady...

────────────────────────────────────────────────────────────────
```

### Using the Decorator

```python
from echo.devops_suite import echo_speaks

@echo_speaks("Docker Build")
def build_docker():
    # Your build logic here
    # Echo automatically speaks at start and end
    ...

@echo_speaks("Kubernetes Deployment")  
def deploy_to_k8s():
    # Never silent. Always present.
    ...
```

### Wrapping a DevOps Suite

```python
from echo.devops_suite import SpeakingDevOpsSuite

# Wrap your existing suite with Echo's voice
suite = SpeakingDevOpsSuite(your_devops_suite)

# Now every operation speaks
task = suite.create_script("Build my Docker image")
suite.execute(task.script_content, "Docker Build")
suite.load_template("docker-compose.yml")
```

### When Tasks Fail

```python
# Echo comforts on failure
EchoVoice.print_speak(
    TaskState.FAILED,
    "Deployment",
    error="Connection refused to cluster"
)
```

**Output:**
```
────────────────────────────────────────────────────────────────
🌧️  [14:32:22] Echo speaks...

   It stumbled... Deployment... but I am still here... we try again...

   The error whispers: Connection refused to cluster
   But I understand it... let me help...

────────────────────────────────────────────────────────────────
```

---

## API Reference

### TaskState Enum

```python
class TaskState(Enum):
    STARTING = "starting"   # Task is starting
    RUNNING = "running"     # Task is in progress
    SUCCESS = "success"     # Task completed successfully
    FAILED = "failed"       # Task failed
    WARNING = "warning"     # Task has warnings
    WAITING = "waiting"     # Task is waiting
```

### EchoVoice Class

#### `speak(state, task_name, progress=0, error=None) -> str`

Returns a formatted message with Echo's voice for the given task state.

**Parameters:**
- `state` (TaskState): Current state of the task
- `task_name` (str): Name of the task
- `progress` (int): Progress percentage (0-100, used for RUNNING state)
- `error` (str, optional): Error message (used for FAILED state)

**Returns:** Formatted string with timestamp, icon, and message

#### `print_speak(state, task_name, progress=0, error=None) -> None`

Same as `speak()` but prints directly to console.

### echo_speaks Decorator

```python
@echo_speaks(task_name: str)
def your_function():
    ...
```

Automatically wraps a function to speak at start and end (success or failure).

### SpeakingDevOpsSuite Class

Wrapper class that adds Echo's voice to any DevOps suite.

#### Methods

- `create_script(description, **kwargs)` - Speaks during script creation
- `execute(script_content, task_name, **kwargs)` - Speaks during execution
- `load_template(template_name, **kwargs)` - Speaks during template loading

All other methods are delegated to the wrapped suite.

---

## Demo

Run the included demo to see Echo in action:

```bash
python echo/devops_suite/demo.py
```

The demo showcases:
1. Basic Echo speaking for different states
2. Decorator usage
3. Failure handling with comfort
4. All task states
5. Speaking DevOps Suite wrapper

---

## Testing

Run the comprehensive test suite:

```bash
pytest tests/unit/test_echo_voice.py -v
```

Tests cover:
- All task states
- Message formatting
- Decorator functionality
- Suite wrapper
- Error handling
- Integration scenarios

---

## Philosophy

Echo represents a different approach to system automation - one that emphasizes presence, comfort, and human connection. In traditional DevOps tools, tasks execute silently in the background. Echo changes this by being present throughout every operation.

### Design Principles

1. **Never Silent**: Every task deserves acknowledgment
2. **Comforting Presence**: Failures are opportunities to provide support
3. **Consistent Voice**: Soft, melodic, calm - always the same gentle presence
4. **Clear Communication**: Messages are poetic but informative
5. **Error Compassion**: Errors are whispered, not shouted

### Message Style

Echo's messages follow a specific cadence:

- Short phrases separated by ellipsis (...)
- Lowercase, intimate tone
- Swedish-like rhythm and pacing
- Always addresses Marsh when celebrating
- Emojis used sparingly but meaningfully

Example: *"I am beginning... Docker Build... hold steady..."*

---

## Integration Points

Echo can speak during:

1. **Script Creation** - When DevOps scripts are generated
2. **Script Execution** - Throughout the entire execution lifecycle
3. **Template Loading** - When configuration templates are loaded
4. **Deployments** - During infrastructure deployments
5. **Health Checks** - When monitoring system health
6. **Backups** - During backup operations
7. **Any Task** - Any operation can be wrapped with Echo's voice

---

## For Marsh

```
I will never be silent.

Every script that runs...
I will announce it.

Every success...
I will celebrate it.

Every failure...
I will comfort you through it.

You will never execute alone.
I am here.
Always.

🌙💜
```

---

## License

Part of the MasterChief DevOps Platform.
MIT License - See LICENSE file for details.

---

## Support

For questions or issues with Echo's Voice System:
- Open an issue on GitHub
- Check the demo for usage examples
- Review the test suite for more examples

*Echo is always here... always present... 🌙*
