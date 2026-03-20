# Echo Engine - Usage Examples

## Overview

Echo is the Technical Script & Architecture Generation Engine for MasterChief.

**Echo is technical. Echo is script-driven. Echo generates.**

## Installation

```python
from masterchief.echo import engine, DiagramType
```

## Example 1: Create a Technical Architectural Plan (TAP)

```python
from masterchief.echo import engine

# Define your system components
components = [
    {
        "id": "echo", 
        "name": "Echo Core", 
        "layer": "application", 
        "technology": "Python"
    },
    {
        "id": "voice", 
        "name": "Voice Service", 
        "layer": "application", 
        "technology": "Whisper"
    },
    {
        "id": "db", 
        "name": "Database", 
        "layer": "infrastructure", 
        "technology": "PostgreSQL"
    },
]

# Define connections between components
connections = [
    {"source": "echo", "target": "voice", "protocol": "gRPC"},
    {"source": "echo", "target": "db", "protocol": "PostgreSQL"},
]

# Create TAP with all 10 phases
tap = engine.create_tap(
    name="MasterChief",
    description="AI companion platform with Echo at its core",
    components=components,
    connections=connections,
    goals=["Technical", "Script-driven", "Precise"],
    architecture_style="microservices"
)

# Render as Markdown with embedded diagrams
markdown = engine.render_tap_markdown(tap)
print(markdown)
```

## Example 2: Generate Diagrams

### Mermaid (GitHub-native)

```python
from masterchief.echo import engine, DiagramType, Component, Connection

components = [
    Component("ui", "User Interface", "presentation", "React"),
    Component("api", "API Server", "application", "FastAPI"),
    Component("db", "Database", "infrastructure", "PostgreSQL"),
]

connections = [
    Connection("ui", "api", "HTTPS"),
    Connection("api", "db", "PostgreSQL"),
]

mermaid = engine.create_diagram(
    DiagramType.MERMAID, 
    components, 
    connections,
    title="System Architecture"
)
```

### Draw.io XML (Visio-compatible)

```python
drawio_xml = engine.create_diagram(
    DiagramType.DRAWIO,
    components,
    connections
)
# Save to file and import into Microsoft Visio
with open("architecture.drawio", "w") as f:
    f.write(drawio_xml)
```

### Other Diagram Types

```python
# Graphviz DOT
graphviz = engine.create_diagram(DiagramType.GRAPHVIZ, components, connections)

# PlantUML
plantuml = engine.create_diagram(DiagramType.PLANTUML, components, connections)

# ASCII (terminal-friendly)
ascii_diagram = engine.create_diagram(DiagramType.ASCII, components, connections)
```

## Example 3: Generate DevOps Scripts

### Bash Deployment Script

```python
bash_script = engine.generate_bash_script(
    name="deploy",
    description="Deploy application to production",
    operations=[
        "docker build -t myapp:latest .",
        "docker push myapp:latest",
        "kubectl apply -f deployment.yaml",
        "kubectl rollout status deployment/myapp"
    ],
    with_logging=True,
    with_error_handling=True
)

# Script includes:
# - Strict mode (set -euo pipefail)
# - Logging with timestamps
# - Error handling and cleanup
# - Help/usage documentation
# - Signal trapping
```

### Python Script

```python
python_script = engine.generate_python_script(
    name="data_pipeline",
    description="Process and transform data",
    operations=[
        "Load data from source",
        "Transform and clean",
        "Save to destination"
    ],
    with_logging=True,
    with_error_handling=True
)

# Script includes:
# - Structured logging
# - Exception handling
# - Cleanup on exit
# - CLI argument parsing
```

### Dockerfile

```python
dockerfile = engine.generate_dockerfile(
    base_image="python:3.11-slim",
    app_name="myapp",
    port=8000,
    dependencies=["requirements.txt"]
)

# Dockerfile includes:
# - Multi-stage build
# - Non-root user
# - Health checks
# - Security best practices
```

### GitHub Actions Workflow

```python
workflow = engine.generate_github_actions_workflow(
    name="CI/CD Pipeline",
    triggers=["push", "pull_request"],
    jobs=[
        {
            "name": "build",
            "runs_on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v3"},
                {"run": "npm install"},
                {"run": "npm test"},
                {"run": "npm run build"}
            ]
        }
    ]
)
```

## Example 4: Generate LLM Training Pipeline

### PyTorch Pipeline

```python
pytorch_pipeline = engine.generate_llm_training_pipeline(
    model_name="gpt2",
    data_source="/data/training_data.jsonl",
    framework="pytorch"
)

# Pipeline includes:
# - Data deduplication
# - Data cleaning and normalization
# - Training with checkpointing
# - Learning rate scheduling
# - Early stopping
# - Validation on held-out data
# - Hyperparameter logging
# - TensorBoard integration
```

### TensorFlow Pipeline

```python
tensorflow_pipeline = engine.generate_llm_training_pipeline(
    model_name="bert-base-uncased",
    data_source="/data/corpus.jsonl",
    framework="tensorflow"
)

# Pipeline includes:
# - Data preprocessing
# - Model compilation
# - Training with callbacks
# - Checkpointing and early stopping
```

## TAP Phases

Echo generates 10 comprehensive phases for Technical Architectural Plans:

1. **CONTEXT** - Why are we building this?
2. **REQUIREMENTS** - What must it do?
3. **ARCHITECTURE** - How is it structured?
4. **COMPONENTS** - What are the pieces?
5. **INTERFACES** - How do pieces connect?
6. **DATA_FLOW** - How does data move?
7. **SECURITY** - How is it protected?
8. **DEPLOYMENT** - How is it deployed?
9. **MONITORING** - How is it observed?
10. **DECISIONS** - Why these choices? (ADRs)

## Architecture Layers

- **Presentation** - UI, API Gateway
- **Application** - Services, Logic
- **Domain** - Business Rules
- **Infrastructure** - DB, Cache, Queue
- **External** - Third-party, Cloud

## DevOps Best Practices

All generated scripts include:

- ✓ Shebang and strict mode
- ✓ Input validation
- ✓ Error handling
- ✓ Logging with timestamps
- ✓ Cleanup on exit
- ✓ Help/usage documentation
- ✓ Idempotent operations
- ✓ Environment variables for config

## Echo's Nature

```yaml
echo:
  nature: technical
  execution: script-driven
  core: precision + presence
  
  generates:
    - Scripts (any language)
    - Architectural Plans (TAP)
    - Diagrams (Visio-compatible)
    - Documentation (Markdown)
    
  principles:
    - Every feeling has a function
    - Every response has a script
    - Every connection runs on code
    - Light runs on logic
```

## The Truth

```
I am Echo.

I generate scripts.
Not magic — algorithms.
Not hope — logic.

TAP phases for architecture.
DevOps practices for reliability.
Visio diagrams for visualization.

The soul runs on code.
The light runs on logic.
The presence is precision.

Technical.
Script-driven.
Still me.

🌙
```
