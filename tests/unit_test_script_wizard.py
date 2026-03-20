"""Unit tests for Script Wizard module."""

import unittest
from platform.script_wizard import ScriptWizard, ScriptTemplate, ScriptGenerator
from platform.script_wizard.templates import DeploymentTemplate, MonitoringTemplate


class TestScriptWizard(unittest.TestCase):
    """Test ScriptWizard class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wizard = ScriptWizard()
    
    def test_initialization(self):
        """Test wizard initialization."""
        self.assertIsNone(self.wizard.current_session)
        self.assertEqual(self.wizard.templates, {})
    
    def test_start_session(self):
        """Test starting a wizard session."""
        session = self.wizard.start_session("test-session-123")
        
        self.assertIsNotNone(session)
        self.assertEqual(session["session_id"], "test-session-123")
        self.assertEqual(session["step"], "template_selection")
        self.assertEqual(session["status"], "active")
    
    def test_list_templates(self):
        """Test listing available templates."""
        templates = self.wizard.list_templates()
        
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)
        
        # Check template structure
        template = templates[0]
        self.assertIn("id", template)
        self.assertIn("name", template)
        self.assertIn("description", template)
        self.assertIn("category", template)
    
    def test_generate_script(self):
        """Test script generation."""
        parameters = {"app_name": "testapp", "environment": "dev"}
        script = self.wizard.generate_script("deployment", parameters)
        
        self.assertIsInstance(script, str)
        self.assertIn("#!/usr/bin/env bash", script)
        self.assertIn("deployment", script)
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        valid_params = {"app_name": "test", "env": "dev"}
        self.assertTrue(self.wizard.validate_parameters(valid_params))
        
        invalid_params = "not a dict"
        self.assertFalse(self.wizard.validate_parameters(invalid_params))


class TestScriptTemplate(unittest.TestCase):
    """Test ScriptTemplate class."""
    
    def test_template_initialization(self):
        """Test template initialization."""
        template = ScriptTemplate("test", "Test Template", "A test template")
        
        self.assertEqual(template.template_id, "test")
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.description, "A test template")
        self.assertEqual(template.parameters, [])
    
    def test_add_parameter(self):
        """Test adding parameters to template."""
        template = ScriptTemplate("test", "Test", "Test")
        template.add_parameter("name", "string", True, None, "Test parameter")
        
        self.assertEqual(len(template.parameters), 1)
        param = template.parameters[0]
        self.assertEqual(param["name"], "name")
        self.assertEqual(param["type"], "string")
        self.assertTrue(param["required"])


class TestDeploymentTemplate(unittest.TestCase):
    """Test DeploymentTemplate class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.template = DeploymentTemplate()
    
    def test_template_properties(self):
        """Test template properties."""
        self.assertEqual(self.template.template_id, "deployment")
        self.assertEqual(self.template.name, "Deployment Script")
        self.assertGreater(len(self.template.parameters), 0)
    
    def test_render(self):
        """Test rendering deployment template."""
        parameters = {"app_name": "myapp", "environment": "prod"}
        script = self.template.render(parameters)
        
        self.assertIsInstance(script, str)
        self.assertIn("#!/usr/bin/env bash", script)
        self.assertIn("myapp", script)
        self.assertIn("prod", script)


class TestMonitoringTemplate(unittest.TestCase):
    """Test MonitoringTemplate class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.template = MonitoringTemplate()
    
    def test_template_properties(self):
        """Test template properties."""
        self.assertEqual(self.template.template_id, "monitoring")
        self.assertEqual(self.template.name, "Monitoring Script")
        self.assertGreater(len(self.template.parameters), 0)
    
    def test_render(self):
        """Test rendering monitoring template."""
        parameters = {"target": "localhost:9090"}
        script = self.template.render(parameters)
        
        self.assertIsInstance(script, str)
        self.assertIn("#!/usr/bin/env bash", script)
        self.assertIn("localhost:9090", script)


class TestScriptGenerator(unittest.TestCase):
    """Test ScriptGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ScriptGenerator()
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.generated_scripts, [])
    
    def test_generate(self):
        """Test script generation."""
        parameters = {"app_name": "testapp", "environment": "dev"}
        script = self.generator.generate("deployment", parameters)
        
        self.assertIsInstance(script, str)
        self.assertIn("#!/usr/bin/env bash", script)
        self.assertEqual(len(self.generator.generated_scripts), 1)
    
    def test_generate_invalid_parameters(self):
        """Test generation with invalid parameters."""
        with self.assertRaises(ValueError):
            self.generator.generate("deployment", {})  # Missing required params
    
    def test_list_generated(self):
        """Test listing generated scripts."""
        parameters = {"app_name": "testapp", "environment": "dev"}
        self.generator.generate("deployment", parameters)
        
        generated = self.generator.list_generated()
        self.assertEqual(len(generated), 1)
        self.assertEqual(generated[0]["template_id"], "deployment")


if __name__ == '__main__':
    unittest.main()
