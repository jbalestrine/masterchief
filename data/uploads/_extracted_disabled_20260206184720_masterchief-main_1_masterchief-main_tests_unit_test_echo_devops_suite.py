"""
Unit tests for Echo DevOps Master Suite
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from echo.devops_suite.master_suite import (
    DevOpsMasterSuite,
    DevOpsPhase,
    DevOpsTask,
    CustomTemplate,
    ScriptType,
    TaskParser,
    TemplateEngine,
)


class TestTaskParser:
    """Test the natural language task parser"""
    
    def test_parse_project_init(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Initialize a new project repository")
        assert phase == "plan"
        assert task_type == "project_init"
    
    def test_parse_docker_build(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Build a Docker image for my application")
        assert phase == "build"
        assert task_type == "docker_build"
    
    def test_parse_unit_tests(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Run unit tests for the project")
        assert phase == "test"
        assert task_type == "unit_tests"
    
    def test_parse_kubernetes_deploy(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Deploy to kubernetes cluster")
        assert phase == "deploy"
        assert task_type == "kubernetes"
    
    def test_parse_health_checks(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Run health checks for the service")
        assert phase == "operate"
        assert task_type == "health_checks"
    
    def test_parse_metrics(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Setup metrics collection with Prometheus")
        assert phase == "monitor"
        assert task_type == "metrics"
    
    def test_parse_vulnerability_scan(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Scan for vulnerabilities in the code")
        assert phase == "secure"
        assert task_type == "vulnerability_scan"
    
    def test_parse_cost_analysis(self):
        parser = TaskParser()
        phase, task_type = parser.parse("Analyze cost and spending")
        assert phase == "optimize"
        assert task_type == "cost_analysis"
    
    def test_parse_unknown_task(self):
        parser = TaskParser()
        phase, task_type = parser.parse("do something random")
        assert phase == "custom"
        assert task_type == "custom"


class TestTemplateEngine:
    """Test the template engine"""
    
    def test_save_and_load_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(template_dir=Path(tmpdir))
            
            template = CustomTemplate(
                id="test_template_1",
                name="Test Template",
                description="A test template",
                phase=DevOpsPhase.BUILD,
                script_type=ScriptType.BASH,
                content="#!/bin/bash\necho 'Hello $NAME'",
                variables=["NAME"]
            )
            
            # Save template
            engine.save_template(template)
            
            # Reload templates
            engine._load_templates()
            
            # Retrieve template
            loaded = engine.get_template("test_template_1")
            assert loaded is not None
            assert loaded.name == "Test Template"
            assert loaded.phase == DevOpsPhase.BUILD
            assert "NAME" in loaded.variables
    
    def test_search_templates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(template_dir=Path(tmpdir))
            
            template1 = CustomTemplate(
                id="docker_build_1",
                name="Docker Build",
                description="Build Docker images",
                phase=DevOpsPhase.BUILD,
                script_type=ScriptType.BASH,
                content="docker build"
            )
            
            template2 = CustomTemplate(
                id="python_build_1",
                name="Python Build",
                description="Build Python packages",
                phase=DevOpsPhase.BUILD,
                script_type=ScriptType.BASH,
                content="python -m build"
            )
            
            engine.save_template(template1)
            engine.save_template(template2)
            
            # Search for "docker"
            results = engine.search_templates("docker")
            assert len(results) == 1
            assert results[0].name == "Docker Build"
            
            # Search for "build"
            results = engine.search_templates("build")
            assert len(results) == 2
    
    def test_list_templates_by_phase(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(template_dir=Path(tmpdir))
            
            template1 = CustomTemplate(
                id="test1",
                name="Build Template",
                description="Build",
                phase=DevOpsPhase.BUILD,
                script_type=ScriptType.BASH,
                content="build"
            )
            
            template2 = CustomTemplate(
                id="test2",
                name="Test Template",
                description="Test",
                phase=DevOpsPhase.TEST,
                script_type=ScriptType.BASH,
                content="test"
            )
            
            engine.save_template(template1)
            engine.save_template(template2)
            
            # List all templates
            all_templates = engine.list_templates()
            assert len(all_templates) == 2
            
            # List BUILD templates only
            build_templates = engine.list_templates(phase=DevOpsPhase.BUILD)
            assert len(build_templates) == 1
            assert build_templates[0].phase == DevOpsPhase.BUILD
    
    def test_template_use_count(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(template_dir=Path(tmpdir))
            
            template = CustomTemplate(
                id="test_template",
                name="Test",
                description="Test",
                phase=DevOpsPhase.BUILD,
                script_type=ScriptType.BASH,
                content="test",
                use_count=0
            )
            
            engine.save_template(template)
            
            # Get template multiple times
            engine.get_template("test_template")
            engine.get_template("test_template")
            
            # Check use count increased
            loaded = engine.templates["test_template"]
            assert loaded.use_count == 2


class TestDevOpsMasterSuite:
    """Test the main DevOps Master Suite"""
    
    def test_create_script_plan_phase(self):
        suite = DevOpsMasterSuite()
        
        task = suite.create_script(
            "Initialize a new project",
            save_as_template=False,
            project_name="test-project"
        )
        
        assert isinstance(task, DevOpsTask)
        assert task.phase == DevOpsPhase.PLAN
        assert "test-project" in task.script_content or "myproject" in task.script_content
        assert task.script_type == ScriptType.BASH
    
    def test_create_script_build_phase(self):
        suite = DevOpsMasterSuite()
        
        task = suite.create_script(
            "Build a Docker image",
            save_as_template=False,
            image_name="myapp",
            tag="v1.0.0"
        )
        
        assert task.phase == DevOpsPhase.BUILD
        assert "myapp" in task.script_content
        assert "docker build" in task.script_content.lower()
    
    def test_create_script_with_template_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = DevOpsMasterSuite()
            suite.template_engine.template_dir = Path(tmpdir)
            
            task = suite.create_script(
                "Build Python project",
                save_as_template=True,
                template_name="my_python_build"
            )
            
            # Check template was saved
            template_file = Path(tmpdir) / f"template_{task.id}.json"
            assert template_file.exists()
            
            # Load and verify template
            with open(template_file) as f:
                template_data = json.load(f)
                assert template_data["name"] == "my_python_build"
    
    def test_run_from_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = DevOpsMasterSuite()
            suite.template_engine.template_dir = Path(tmpdir)
            
            # Create a template
            template = CustomTemplate(
                id="test_template",
                name="Test",
                description="Test template with variables",
                phase=DevOpsPhase.BUILD,
                script_type=ScriptType.BASH,
                content="echo 'Hello ${NAME}, version ${VERSION}'"
            )
            suite.template_engine.save_template(template)
            
            # Run from template
            result = suite.run_from_template(
                "test_template",
                NAME="World",
                VERSION="1.0.0"
            )
            
            assert "Hello World" in result
            assert "version 1.0.0" in result
    
    def test_get_all_capabilities(self):
        suite = DevOpsMasterSuite()
        capabilities = suite.get_all_capabilities()
        
        # Check all phases are present
        expected_phases = [
            "plan", "code", "build", "test", "release",
            "deploy", "operate", "monitor", "secure", "optimize"
        ]
        
        for phase in expected_phases:
            assert phase in capabilities
            assert len(capabilities[phase]) > 0
        
        # Check specific capabilities
        assert "docker_build" in capabilities["build"]
        assert "kubernetes" in capabilities["deploy"]
        assert "vulnerability_scan" in capabilities["secure"]
    
    def test_describe(self):
        suite = DevOpsMasterSuite()
        description = suite.describe()
        
        assert "ECHO DEVOPS MASTER SUITE" in description
        assert "PLAN" in description
        assert "CODE" in description
        assert "BUILD" in description
        assert "TEST" in description
        assert "RELEASE" in description
        assert "DEPLOY" in description
        assert "OPERATE" in description
        assert "MONITOR" in description
        assert "SECURE" in description
        assert "OPTIMIZE" in description
        assert "Echo 🌙💜" in description
    
    def test_task_history(self):
        suite = DevOpsMasterSuite()
        
        # Create multiple tasks
        suite.create_script("Initialize project", save_as_template=False)
        suite.create_script("Build Docker image", save_as_template=False)
        suite.create_script("Run tests", save_as_template=False)
        
        # Check history
        assert len(suite.task_history) == 3
        assert all(isinstance(task, DevOpsTask) for task in suite.task_history)


class TestDevOpsPhaseEnum:
    """Test DevOpsPhase enum"""
    
    def test_all_phases_exist(self):
        expected_phases = [
            "PLAN", "CODE", "BUILD", "TEST", "RELEASE",
            "DEPLOY", "OPERATE", "MONITOR", "SECURE", "OPTIMIZE"
        ]
        
        for phase_name in expected_phases:
            assert hasattr(DevOpsPhase, phase_name)
    
    def test_phase_values(self):
        assert DevOpsPhase.PLAN.value == "plan"
        assert DevOpsPhase.BUILD.value == "build"
        assert DevOpsPhase.DEPLOY.value == "deploy"


class TestScriptTypeEnum:
    """Test ScriptType enum"""
    
    def test_script_types_exist(self):
        expected_types = [
            "BASH", "PYTHON", "YAML", "TERRAFORM",
            "DOCKERFILE", "KUBERNETES", "HELM",
            "ANSIBLE", "GROOVY", "POWERSHELL"
        ]
        
        for script_type in expected_types:
            assert hasattr(ScriptType, script_type)


class TestDataClasses:
    """Test DevOpsTask and CustomTemplate dataclasses"""
    
    def test_devops_task_creation(self):
        task = DevOpsTask(
            id="task_123",
            name="Test Task",
            phase=DevOpsPhase.BUILD,
            description="A test task",
            script_type=ScriptType.BASH,
            script_content="#!/bin/bash\necho 'test'",
            parameters={"key": "value"},
            tags=["test", "build"]
        )
        
        assert task.id == "task_123"
        assert task.phase == DevOpsPhase.BUILD
        assert task.script_type == ScriptType.BASH
        assert task.parameters["key"] == "value"
        assert "test" in task.tags
        assert isinstance(task.created_at, datetime)
    
    def test_custom_template_creation(self):
        template = CustomTemplate(
            id="template_123",
            name="Test Template",
            description="A test template",
            phase=DevOpsPhase.DEPLOY,
            script_type=ScriptType.KUBERNETES,
            content="apiVersion: v1\nkind: Pod",
            variables=["POD_NAME", "IMAGE"]
        )
        
        assert template.id == "template_123"
        assert template.phase == DevOpsPhase.DEPLOY
        assert template.script_type == ScriptType.KUBERNETES
        assert "POD_NAME" in template.variables
        assert template.use_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
