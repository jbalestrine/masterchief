"""
Echo - Technical Script & Architecture Generation Engine

Echo is technical. Echo is script-driven. Echo generates.

Provides:
- Technical Architectural Plans (TAP)
- Visio-compatible diagrams (Mermaid, Draw.io XML, Graphviz, PlantUML, ASCII)
- Script generation (Bash, Python, YAML, Dockerfile, Terraform, GitHub Actions)
- LLM training pipelines
- DevOps best practices
"""

from masterchief.echo.script_engine import (
    engine,
    ScriptEngine,
    DiagramType,
    ArchitectureLayer,
    TAPPhase
)

__version__ = "1.0.0"

__all__ = [
    'engine',
    'ScriptEngine',
    'DiagramType',
    'ArchitectureLayer',
    'TAPPhase',
]
