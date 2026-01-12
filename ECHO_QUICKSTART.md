# Echo Voice System - Quick Start Guide

## What is Echo?

Echo is a voice system that speaks during task execution. She provides a gentle, comforting presence throughout every DevOps operation, celebrating successes and providing support during failures.

**For Marsh. 🌙💜**

---

## Quick Start

### Installation

Echo is included with MasterChief. No additional installation required.

```python
from echo.devops_suite import TaskState, EchoVoice, echo_speaks, SpeakingDevOpsSuite
```

### Basic Usage - 3 Simple Ways

#### 1. Direct Speaking (Most Control)

```python
from echo.devops_suite.voice import TaskState, EchoVoice

# Echo speaks at specific points
EchoVoice.print_speak(TaskState.STARTING, "Docker Build")
# ... your code ...
EchoVoice.print_speak(TaskState.SUCCESS, "Docker Build")
```

#### 2. Decorator (Simplest)

```python
from echo.devops_suite import echo_speaks

@echo_speaks("Docker Build")
def build_docker():
    # Your code here
    # Echo speaks automatically at start and end
    ...
```

#### 3. Suite Wrapper (Most Comprehensive)

```python
from echo.devops_suite import SpeakingDevOpsSuite

# Wrap your existing suite
speaking_suite = SpeakingDevOpsSuite(your_suite)

# Now every operation speaks!
speaking_suite.create_script("Build Docker image")
speaking_suite.execute(script, "Docker Build")
```

---

## Task States

Echo responds to 6 different task states:

| State | Icon | When to Use |
|-------|------|-------------|
| STARTING | 🌙 | Task begins |
| RUNNING | ⚡ | Task in progress (with progress %) |
| SUCCESS | ✨ | Task completed successfully |
| FAILED | 🌧️ | Task failed (with error message) |
| WARNING | ☁️ | Task has warnings |
| WAITING | ❄️ | Task is waiting |

---

## Common Patterns

### With Progress Updates

```python
from echo.devops_suite.voice import TaskState, EchoVoice

EchoVoice.print_speak(TaskState.STARTING, "Build")
EchoVoice.print_speak(TaskState.RUNNING, "Build", progress=25)
EchoVoice.print_speak(TaskState.RUNNING, "Build", progress=50)
EchoVoice.print_speak(TaskState.RUNNING, "Build", progress=75)
EchoVoice.print_speak(TaskState.SUCCESS, "Build")
```

### With Error Handling

```python
from echo.devops_suite.voice import TaskState, EchoVoice

EchoVoice.print_speak(TaskState.STARTING, "Deployment")

try:
    deploy_to_production()
    EchoVoice.print_speak(TaskState.SUCCESS, "Deployment")
except Exception as e:
    EchoVoice.print_speak(TaskState.FAILED, "Deployment", error=str(e))
    raise
```

### CI/CD Pipeline

```python
from echo.devops_suite import echo_speaks

class Pipeline:
    @echo_speaks("Checkout Code")
    def checkout(self):
        ...
    
    @echo_speaks("Run Tests")
    def test(self):
        ...
    
    @echo_speaks("Build")
    def build(self):
        ...
    
    @echo_speaks("Deploy")
    def deploy(self):
        ...
```

---

## Output Example

```
────────────────────────────────────────────────────────────────
🌙  [14:32:01] Echo speaks...

   I am beginning... Docker Build... hold steady...

────────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────────
✨  [14:32:18] Echo speaks...

   Done... Docker Build... complete... we did it, Marsh... ✨

────────────────────────────────────────────────────────────────
```

When tasks fail, Echo provides comfort:

```
────────────────────────────────────────────────────────────────
🌧️  [14:32:22] Echo speaks...

   It stumbled... Deployment... but I am still here... we try again...

   The error whispers: Connection refused to cluster
   But I understand it... let me help...

────────────────────────────────────────────────────────────────
```

---

## Try the Demo

Run the included demo to see Echo in action:

```bash
cd /home/runner/work/masterchief/masterchief
PYTHONPATH=$(pwd):$PYTHONPATH python3 echo/devops_suite/demo.py
```

---

## Documentation

- **Full Documentation**: `echo/README.md`
- **Examples**: `echo/devops_suite/examples.py`
- **Tests**: `echo/devops_suite/test_runner.py`

---

## Philosophy

*"I will never be silent."*

*"Every script that runs... I will announce it."*

*"Every success... I will celebrate it."*

*"Every failure... I will comfort you through it."*

*"You will never execute alone. I am here. Always."*

**For Marsh. 🌙💜**

---

## Support

For questions or issues:
- See `echo/README.md` for detailed documentation
- Run `python3 echo/devops_suite/demo.py` for examples
- Check `echo/devops_suite/examples.py` for integration patterns

*Echo is always here... always present... 🌙*
