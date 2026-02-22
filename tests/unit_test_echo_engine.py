"""Tests for Echo Script & Architecture Generation Engine."""
import pytest
from masterchief.echo.script_engine import (
    engine,
    ScriptEngine,
    Component,
    Connection,
    TAP,
    DiagramType,
    ArchitectureLayer,
)
from masterchief.echo.tap_generator import TAPPhase


class TestScriptEngine:
    """Test suite for ScriptEngine."""
    
    def test_engine_initialization(self):
        """Test that the engine initializes correctly."""
        test_engine = ScriptEngine()
        assert test_engine is not None
        assert test_engine.tap_generator is not None
        assert test_engine.diagram_generator is not None
        assert test_engine.devops_generator is not None
        assert test_engine.llm_generator is not None
    
    def test_global_engine_instance(self):
        """Test that global engine instance exists."""
        assert engine is not None
        assert isinstance(engine, ScriptEngine)
    
    def test_create_tap_basic(self):
        """Test creating a basic TAP."""
        components = [
            {"id": "api", "name": "API Gateway", "layer": "presentation", "technology": "FastAPI"},
            {"id": "db", "name": "Database", "layer": "infrastructure", "technology": "PostgreSQL"},
        ]
        
        connections = [
            {"source": "api", "target": "db", "protocol": "PostgreSQL"}
        ]
        
        tap = engine.create_tap(
            name="Test System",
            description="A test system",
            components=components,
            connections=connections,
            goals=["Technical", "Scalable"],
            architecture_style="microservices"
        )
        
        assert tap is not None
        assert tap.name == "Test System"
        assert tap.description == "A test system"
        assert len(tap.components) == 2
        assert len(tap.connections) == 1
        assert len(tap.goals) == 2
        assert tap.architecture_style == "microservices"
        assert len(tap.phases) == 10  # All 10 TAP phases
    
    def test_create_tap_with_component_objects(self):
        """Test creating TAP with Component objects."""
        components = [
            Component(
                id="svc1",
                name="Service 1",
                layer="application",
                technology="Python",
                description="Main service"
            )
        ]
        
        connections = [
            Connection(
                source="svc1",
                target="db",
                protocol="HTTP",
                description="API connection"
            )
        ]
        
        tap = engine.create_tap(
            name="Component Test",
            description="Testing with objects",
            components=components,
            connections=connections,
            goals=["Test"],
            architecture_style="monolithic"
        )
        
        assert tap is not None
        assert tap.components[0].name == "Service 1"
        assert tap.connections[0].protocol == "HTTP"
    
    def test_render_tap_markdown(self):
        """Test rendering TAP as markdown."""
        components = [
            {"id": "app", "name": "Application", "layer": "application", "technology": "Node.js"},
        ]
        
        connections = []
        
        tap = engine.create_tap(
            name="Markdown Test",
            description="Test markdown rendering",
            components=components,
            connections=connections,
            goals=["Document"],
            architecture_style="microservices"
        )
        
        markdown = engine.render_tap_markdown(tap)
        
        assert markdown is not None
        assert "# Markdown Test" in markdown
        assert "Test markdown rendering" in markdown
        assert "```mermaid" in markdown
        assert "Application" in markdown
    
    def test_create_mermaid_diagram(self):
        """Test creating a Mermaid diagram."""
        components = [
            Component("ui", "User Interface", "presentation", "React"),
            Component("api", "API Server", "application", "FastAPI"),
            Component("db", "Database", "infrastructure", "PostgreSQL"),
        ]
        
        connections = [
            Connection("ui", "api", "HTTPS"),
            Connection("api", "db", "PostgreSQL"),
        ]
        
        diagram = engine.create_diagram(
            DiagramType.MERMAID,
            components,
            connections,
            title="Test Architecture"
        )
        
        assert diagram is not None
        assert "```mermaid" in diagram
        assert "graph TD" in diagram
        assert "User Interface" in diagram
        assert "API Server" in diagram
        assert "HTTPS" in diagram
        assert "PostgreSQL" in diagram
    
    def test_create_drawio_diagram(self):
        """Test creating a Draw.io XML diagram."""
        components = [
            Component("api", "API", "application", "Python"),
        ]
        
        connections = []
        
        diagram = engine.create_diagram(
            DiagramType.DRAWIO,
            components,
            connections
        )
        
        assert diagram is not None
        assert '<?xml version="1.0"' in diagram
        assert '<mxfile' in diagram
        assert 'API' in diagram
    
    def test_create_graphviz_diagram(self):
        """Test creating a Graphviz DOT diagram."""
        components = [
            Component("svc", "Service", "application", "Go"),
        ]
        
        connections = []
        
        diagram = engine.create_diagram(
            DiagramType.GRAPHVIZ,
            components,
            connections
        )
        
        assert diagram is not None
        assert "digraph" in diagram
        assert "Service" in diagram
        assert "Go" in diagram
    
    def test_create_plantuml_diagram(self):
        """Test creating a PlantUML diagram."""
        components = [
            Component("web", "Web Server", "presentation", "Nginx"),
        ]
        
        connections = []
        
        diagram = engine.create_diagram(
            DiagramType.PLANTUML,
            components,
            connections
        )
        
        assert diagram is not None
        assert "@startuml" in diagram
        assert "@enduml" in diagram
        assert "Web Server" in diagram
    
    def test_create_ascii_diagram(self):
        """Test creating an ASCII diagram."""
        components = [
            Component("cache", "Cache", "infrastructure", "Redis"),
        ]
        
        connections = []
        
        diagram = engine.create_diagram(
            DiagramType.ASCII,
            components,
            connections
        )
        
        assert diagram is not None
        assert "Cache" in diagram
        assert "Redis" in diagram
        assert "=====" in diagram
    
    def test_generate_bash_script(self):
        """Test generating a Bash script."""
        script = engine.generate_bash_script(
            name="Deployment Script",
            description="Deploy application to production",
            operations=[
                "docker build -t app:latest .",
                "docker push app:latest",
                "kubectl apply -f deployment.yaml"
            ]
        )
        
        assert script is not None
        assert "#!/usr/bin/env bash" in script
        assert "set -euo pipefail" in script
        assert "Deployment Script" in script
        assert "docker build" in script
        assert "log_info" in script
        assert "error_exit" in script
    
    def test_generate_python_script(self):
        """Test generating a Python script."""
        script = engine.generate_python_script(
            name="Data Processing",
            description="Process and transform data",
            operations=[
                "Load data from source",
                "Transform data",
                "Save to destination"
            ]
        )
        
        assert script is not None
        assert "#!/usr/bin/env python3" in script
        assert "import logging" in script
        assert "Data Processing" in script
        assert "def main():" in script
        assert "logger.info" in script
    
    def test_generate_dockerfile(self):
        """Test generating a Dockerfile."""
        dockerfile = engine.generate_dockerfile(
            base_image="python:3.11-slim",
            app_name="myapp",
            port=8080,
            dependencies=["requirements.txt"]
        )
        
        assert dockerfile is not None
        assert "FROM python:3.11-slim" in dockerfile
        assert "EXPOSE 8080" in dockerfile
        assert "HEALTHCHECK" in dockerfile
        assert "appuser" in dockerfile
        assert "requirements.txt" in dockerfile
    
    def test_generate_github_actions_workflow(self):
        """Test generating a GitHub Actions workflow."""
        workflow = engine.generate_github_actions_workflow(
            name="CI Pipeline",
            triggers=["push", "pull_request"],
            jobs=[
                {
                    "name": "build",
                    "runs_on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {"run": "npm install"},
                        {"run": "npm test"}
                    ]
                }
            ]
        )
        
        assert workflow is not None
        assert "name: CI Pipeline" in workflow
        assert "push" in workflow
        assert "build:" in workflow
        assert "ubuntu-latest" in workflow
    
    def test_generate_llm_training_pipeline_pytorch(self):
        """Test generating an LLM training pipeline for PyTorch."""
        pipeline = engine.generate_llm_training_pipeline(
            model_name="gpt2",
            data_source="/data/train.jsonl",
            framework="pytorch"
        )
        
        assert pipeline is not None
        assert "#!/usr/bin/env python3" in pipeline
        assert "import torch" in pipeline
        assert "gpt2" in pipeline
        assert "train.jsonl" in pipeline
        assert "LLMDataset" in pipeline
        assert "LLMTrainer" in pipeline
        assert "early_stopping" in pipeline.lower()
        assert "checkpoint" in pipeline.lower()
    
    def test_generate_llm_training_pipeline_tensorflow(self):
        """Test generating an LLM training pipeline for TensorFlow."""
        pipeline = engine.generate_llm_training_pipeline(
            model_name="bert-base",
            data_source="/data/corpus.jsonl",
            framework="tensorflow"
        )
        
        assert pipeline is not None
        assert "#!/usr/bin/env python3" in pipeline
        assert "import tensorflow" in pipeline
        assert "bert-base" in pipeline
        assert "corpus.jsonl" in pipeline


class TestComponent:
    """Test suite for Component class."""
    
    def test_component_creation(self):
        """Test creating a component."""
        comp = Component(
            id="test",
            name="Test Component",
            layer="application",
            technology="Python",
            description="A test component"
        )
        
        assert comp.id == "test"
        assert comp.name == "Test Component"
        assert comp.layer == "application"
        assert comp.technology == "Python"
        assert comp.description == "A test component"
    
    def test_component_to_dict(self):
        """Test converting component to dictionary."""
        comp = Component("c1", "Component 1", "domain", "Java")
        comp_dict = comp.to_dict()
        
        assert comp_dict["id"] == "c1"
        assert comp_dict["name"] == "Component 1"
        assert comp_dict["layer"] == "domain"
        assert comp_dict["technology"] == "Java"


class TestConnection:
    """Test suite for Connection class."""
    
    def test_connection_creation(self):
        """Test creating a connection."""
        conn = Connection(
            source="source",
            target="target",
            protocol="gRPC",
            description="Test connection"
        )
        
        assert conn.source == "source"
        assert conn.target == "target"
        assert conn.protocol == "gRPC"
        assert conn.description == "Test connection"
    
    def test_connection_to_dict(self):
        """Test converting connection to dictionary."""
        conn = Connection("a", "b", "HTTP")
        conn_dict = conn.to_dict()
        
        assert conn_dict["source"] == "a"
        assert conn_dict["target"] == "b"
        assert conn_dict["protocol"] == "HTTP"


class TestTAP:
    """Test suite for TAP class."""
    
    def test_tap_creation(self):
        """Test creating a TAP."""
        components = [Component("c1", "Component", "application", "Python")]
        connections = [Connection("c1", "c2", "HTTP")]
        
        tap = TAP(
            name="Test TAP",
            description="Test",
            components=components,
            connections=connections,
            goals=["Goal 1"],
            architecture_style="microservices"
        )
        
        assert tap.name == "Test TAP"
        assert tap.description == "Test"
        assert len(tap.components) == 1
        assert len(tap.connections) == 1
    
    def test_tap_to_dict(self):
        """Test converting TAP to dictionary."""
        components = [Component("c1", "Component", "application", "Python")]
        connections = [Connection("c1", "c2", "HTTP")]
        
        tap = TAP(
            name="TAP",
            description="Test",
            components=components,
            connections=connections,
            goals=["G1"],
            architecture_style="monolithic",
            phases={TAPPhase.CONTEXT: "Context content"}
        )
        
        tap_dict = tap.to_dict()
        
        assert tap_dict["name"] == "TAP"
        assert len(tap_dict["components"]) == 1
        assert "context" in tap_dict["phases"]


class TestArchitectureLayer:
    """Test suite for ArchitectureLayer enum."""
    
    def test_layer_values(self):
        """Test architecture layer enum values."""
        assert ArchitectureLayer.PRESENTATION.value == "presentation"
        assert ArchitectureLayer.APPLICATION.value == "application"
        assert ArchitectureLayer.DOMAIN.value == "domain"
        assert ArchitectureLayer.INFRASTRUCTURE.value == "infrastructure"
        assert ArchitectureLayer.EXTERNAL.value == "external"


class TestDiagramType:
    """Test suite for DiagramType enum."""
    
    def test_diagram_type_values(self):
        """Test diagram type enum values."""
        assert DiagramType.MERMAID.value == "mermaid"
        assert DiagramType.DRAWIO.value == "drawio"
        assert DiagramType.GRAPHVIZ.value == "graphviz"
        assert DiagramType.PLANTUML.value == "plantuml"
        assert DiagramType.ASCII.value == "ascii"


class TestTAPPhase:
    """Test suite for TAPPhase enum."""
    
    def test_tap_phase_values(self):
        """Test TAP phase enum values."""
        assert TAPPhase.CONTEXT.value == "context"
        assert TAPPhase.REQUIREMENTS.value == "requirements"
        assert TAPPhase.ARCHITECTURE.value == "architecture"
        assert TAPPhase.COMPONENTS.value == "components"
        assert TAPPhase.INTERFACES.value == "interfaces"
        assert TAPPhase.DATA_FLOW.value == "data_flow"
        assert TAPPhase.SECURITY.value == "security"
        assert TAPPhase.DEPLOYMENT.value == "deployment"
        assert TAPPhase.MONITORING.value == "monitoring"
        assert TAPPhase.DECISIONS.value == "decisions"
