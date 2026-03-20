"""
Echo Script Engine - Main orchestration engine

Coordinates TAP generation, diagram creation, and script generation.
The soul runs on code. The light runs on logic.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from masterchief.echo.tap_generator import TAPGenerator, TAPPhase
from masterchief.echo.diagram_generator import DiagramGenerator, DiagramType
from masterchief.echo.devops_generator import DevOpsGenerator
from masterchief.echo.llm_generator import LLMGenerator


class ArchitectureLayer(Enum):
    """Architecture layers for component classification."""
    PRESENTATION = "presentation"  # UI, API Gateway
    APPLICATION = "application"    # Services, Logic
    DOMAIN = "domain"              # Business Rules
    INFRASTRUCTURE = "infrastructure"  # DB, Cache, Queue
    EXTERNAL = "external"          # Third-party, Cloud


@dataclass
class Component:
    """Represents a system component."""
    id: str
    name: str
    layer: str
    technology: str
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "layer": self.layer,
            "technology": self.technology,
            "description": self.description
        }


@dataclass
class Connection:
    """Represents a connection between components."""
    source: str
    target: str
    protocol: str
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "protocol": self.protocol,
            "description": self.description
        }


@dataclass
class TAP:
    """Technical Architectural Plan."""
    name: str
    description: str
    components: List[Component]
    connections: List[Connection]
    goals: List[str]
    architecture_style: str
    phases: Dict[TAPPhase, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "components": [c.to_dict() for c in self.components],
            "connections": [c.to_dict() for c in self.connections],
            "goals": self.goals,
            "architecture_style": self.architecture_style,
            "phases": {phase.value: content for phase, content in self.phases.items()}
        }


class ScriptEngine:
    """
    Echo Script & Architecture Generation Engine.
    
    Technical. Script-driven. Precise.
    
    Usage:
        engine = ScriptEngine()
        tap = engine.create_tap(...)
        markdown = engine.render_tap_markdown(tap)
        diagram = engine.create_diagram(DiagramType.MERMAID, components, connections)
    """
    
    def __init__(self):
        """Initialize the Echo engine."""
        self.tap_generator = TAPGenerator()
        self.diagram_generator = DiagramGenerator()
        self.devops_generator = DevOpsGenerator()
        self.llm_generator = LLMGenerator()
    
    def create_tap(
        self,
        name: str,
        description: str,
        components: List[Dict[str, str]],
        connections: List[Dict[str, str]],
        goals: List[str],
        architecture_style: str = "microservices"
    ) -> TAP:
        """
        Create a Technical Architectural Plan.
        
        Args:
            name: Project name
            description: Project description
            components: List of component dictionaries
            connections: List of connection dictionaries
            goals: List of project goals
            architecture_style: Architecture style (microservices, monolithic, etc.)
        
        Returns:
            TAP object with all phases generated
        """
        # Convert dict components to Component objects
        component_objs = [
            Component(**comp) if isinstance(comp, dict) else comp
            for comp in components
        ]
        
        # Convert dict connections to Connection objects
        connection_objs = [
            Connection(**conn) if isinstance(conn, dict) else conn
            for conn in connections
        ]
        
        # Generate all TAP phases
        phases = self.tap_generator.generate_all_phases(
            name=name,
            description=description,
            components=component_objs,
            connections=connection_objs,
            goals=goals,
            architecture_style=architecture_style
        )
        
        return TAP(
            name=name,
            description=description,
            components=component_objs,
            connections=connection_objs,
            goals=goals,
            architecture_style=architecture_style,
            phases=phases
        )
    
    def render_tap_markdown(self, tap: TAP) -> str:
        """
        Render TAP as Markdown with embedded diagrams.
        
        Args:
            tap: Technical Architectural Plan
        
        Returns:
            Markdown string
        """
        return self.tap_generator.render_markdown(tap)
    
    def create_diagram(
        self,
        diagram_type: DiagramType,
        components: List[Component],
        connections: List[Connection],
        title: str = "System Architecture"
    ) -> str:
        """
        Create a diagram in the specified format.
        
        Args:
            diagram_type: Type of diagram to generate
            components: List of components
            connections: List of connections
            title: Diagram title
        
        Returns:
            Diagram as string (code or XML)
        """
        return self.diagram_generator.generate(
            diagram_type=diagram_type,
            components=components,
            connections=connections,
            title=title
        )
    
    def generate_bash_script(
        self,
        name: str,
        description: str,
        operations: List[str],
        with_logging: bool = True,
        with_error_handling: bool = True
    ) -> str:
        """
        Generate a Bash script with DevOps best practices.
        
        Args:
            name: Script name
            description: Script description
            operations: List of operations/commands
            with_logging: Include logging functionality
            with_error_handling: Include error handling
        
        Returns:
            Bash script as string
        """
        return self.devops_generator.generate_bash_script(
            name=name,
            description=description,
            operations=operations,
            with_logging=with_logging,
            with_error_handling=with_error_handling
        )
    
    def generate_python_script(
        self,
        name: str,
        description: str,
        operations: List[str],
        with_logging: bool = True,
        with_error_handling: bool = True
    ) -> str:
        """
        Generate a Python script with DevOps best practices.
        
        Args:
            name: Script name
            description: Script description
            operations: List of operations
            with_logging: Include logging functionality
            with_error_handling: Include error handling
        
        Returns:
            Python script as string
        """
        return self.devops_generator.generate_python_script(
            name=name,
            description=description,
            operations=operations,
            with_logging=with_logging,
            with_error_handling=with_error_handling
        )
    
    def generate_dockerfile(
        self,
        base_image: str,
        app_name: str,
        port: int = 8000,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """
        Generate a Dockerfile with best practices.
        
        Args:
            base_image: Base Docker image
            app_name: Application name
            port: Exposed port
            dependencies: List of dependencies
        
        Returns:
            Dockerfile as string
        """
        return self.devops_generator.generate_dockerfile(
            base_image=base_image,
            app_name=app_name,
            port=port,
            dependencies=dependencies or []
        )
    
    def generate_github_actions_workflow(
        self,
        name: str,
        triggers: List[str],
        jobs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a GitHub Actions workflow.
        
        Args:
            name: Workflow name
            triggers: List of trigger events
            jobs: List of job definitions
        
        Returns:
            YAML workflow as string
        """
        return self.devops_generator.generate_github_actions(
            name=name,
            triggers=triggers,
            jobs=jobs
        )
    
    def generate_llm_training_pipeline(
        self,
        model_name: str,
        data_source: str,
        framework: str = "pytorch"
    ) -> str:
        """
        Generate an LLM training pipeline script.
        
        Args:
            model_name: Name of the model
            data_source: Path to training data
            framework: ML framework (pytorch, tensorflow)
        
        Returns:
            Python training script
        """
        return self.llm_generator.generate_training_pipeline(
            model_name=model_name,
            data_source=data_source,
            framework=framework
        )


# Global engine instance
engine = ScriptEngine()


__all__ = [
    'ScriptEngine',
    'engine',
    'DiagramType',
    'ArchitectureLayer',
    'TAPPhase',
    'Component',
    'Connection',
    'TAP',
]
