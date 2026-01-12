"""
Unit tests for Plugin Wizard.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from platform.plugins.wizard.wizard_engine import (
    WizardEngine, WizardSession, WizardStep, PluginType, PluginMetadata
)
from platform.plugins.wizard.validators import PluginValidator
from platform.plugins.wizard.folder_generator import FolderGenerator
from platform.plugins.wizard.template_generator import TemplateGenerator
from platform.plugins.wizard.step_handlers import StepHandler


class TestWizardEngine:
    """Test wizard engine functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def wizard(self, temp_dir):
        """Create wizard engine instance."""
        return WizardEngine(plugins_base_dir=temp_dir)
    
    def test_start_session(self, wizard):
        """Test starting a new wizard session."""
        session = wizard.start_session()
        
        assert session is not None
        assert session.session_id is not None
        assert session.current_step == WizardStep.TYPE_SELECTION
        assert session.plugin_type is None
        assert not session.completed
    
    def test_get_session(self, wizard):
        """Test retrieving a session."""
        session = wizard.start_session()
        retrieved = wizard.get_session(session.session_id)
        
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
    
    def test_delete_session(self, wizard):
        """Test deleting a session."""
        session = wizard.start_session()
        success = wizard.delete_session(session.session_id)
        
        assert success is True
        assert wizard.get_session(session.session_id) is None
    
    def test_type_selection_step(self, wizard):
        """Test type selection step."""
        session = wizard.start_session()
        
        result = wizard.advance_step(session.session_id, {
            'plugin_type': 'python'
        })
        
        assert result['success'] is True
        assert session.current_step == WizardStep.METADATA
        assert session.plugin_type == PluginType.PYTHON
    
    def test_metadata_step(self, wizard):
        """Test metadata collection step."""
        session = wizard.start_session()
        
        # First, select type
        wizard.advance_step(session.session_id, {'plugin_type': 'python'})
        
        # Then, submit metadata
        result = wizard.advance_step(session.session_id, {
            'name': 'test-plugin',
            'description': 'A test plugin for unit testing',
            'version': '1.0.0',
            'author': 'Test Author'
        })
        
        assert result['success'] is True
        assert session.current_step == WizardStep.CONFIGURATION
        assert session.metadata is not None
        assert session.metadata.name == 'test-plugin'
    
    def test_invalid_type_selection(self, wizard):
        """Test invalid plugin type selection."""
        session = wizard.start_session()
        
        result = wizard.advance_step(session.session_id, {
            'plugin_type': 'invalid_type'
        })
        
        assert result['success'] is False
        assert 'Invalid plugin type' in result['error']


class TestPluginValidator:
    """Test plugin validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return PluginValidator()
    
    def test_valid_plugin_name(self, validator):
        """Test valid plugin name validation."""
        is_valid, error = validator.validate_plugin_name('my-test-plugin')
        
        assert is_valid is True
        assert error == ""
    
    def test_invalid_plugin_name_uppercase(self, validator):
        """Test invalid plugin name with uppercase."""
        is_valid, error = validator.validate_plugin_name('MyPlugin')
        
        assert is_valid is False
        assert 'lowercase' in error.lower()
    
    def test_invalid_plugin_name_short(self, validator):
        """Test invalid plugin name too short."""
        is_valid, error = validator.validate_plugin_name('ab')
        
        assert is_valid is False
        assert 'at least 3' in error
    
    def test_valid_version(self, validator):
        """Test valid version validation."""
        is_valid, error = validator.validate_version('1.0.0')
        
        assert is_valid is True
        assert error == ""
    
    def test_invalid_version(self, validator):
        """Test invalid version validation."""
        is_valid, error = validator.validate_version('1.0')
        
        assert is_valid is False
        assert 'semantic versioning' in error.lower()
    
    def test_valid_description(self, validator):
        """Test valid description validation."""
        is_valid, error = validator.validate_description(
            'This is a valid plugin description'
        )
        
        assert is_valid is True
        assert error == ""
    
    def test_invalid_description_short(self, validator):
        """Test invalid description too short."""
        is_valid, error = validator.validate_description('Too short')
        
        assert is_valid is False
        assert 'at least 10' in error


class TestFolderGenerator:
    """Test folder generator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create folder generator instance."""
        return FolderGenerator(base_dir=temp_dir)
    
    def test_generate_structure(self, generator, temp_dir):
        """Test folder structure generation."""
        plugin_path = generator.generate_structure('test-plugin')
        
        assert plugin_path.exists()
        assert (plugin_path / 'src').exists()
        assert (plugin_path / 'logs').exists()
        assert (plugin_path / 'config').exists()
        assert (plugin_path / 'tests').exists()
        assert (plugin_path / 'README.md').exists()
        assert (plugin_path / '.gitignore').exists()
    
    def test_duplicate_plugin(self, generator):
        """Test creating duplicate plugin."""
        generator.generate_structure('test-plugin')
        
        with pytest.raises(ValueError, match='already exists'):
            generator.generate_structure('test-plugin')


class TestTemplateGenerator:
    """Test template generator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def generator(self):
        """Create template generator instance."""
        return TemplateGenerator()
    
    @pytest.fixture
    def plugin_path(self, temp_dir):
        """Create plugin directory structure."""
        path = Path(temp_dir) / 'test-plugin'
        path.mkdir()
        (path / 'config').mkdir()
        return path
    
    def test_generate_python_templates(self, generator, plugin_path):
        """Test Python template generation."""
        metadata = PluginMetadata(
            name='test-plugin',
            description='Test plugin',
            version='1.0.0',
            plugin_type='python'
        )
        
        config = {
            'python_version': '3.10',
            'venv_enabled': True,
            'dependencies': ['flask', 'requests']
        }
        
        generator.generate_templates(plugin_path, 'python', metadata, config)
        
        assert (plugin_path / 'config' / 'plugin.yaml').exists()
        assert (plugin_path / 'config' / 'python_config.yaml').exists()
        assert (plugin_path / 'requirements.txt').exists()
    
    def test_generate_nodejs_templates(self, generator, plugin_path):
        """Test Node.js template generation."""
        metadata = PluginMetadata(
            name='test-plugin',
            description='Test plugin',
            version='1.0.0',
            plugin_type='nodejs'
        )
        
        config = {
            'node_version': '18',
            'package_manager': 'npm',
            'dependencies': ['express']
        }
        
        generator.generate_templates(plugin_path, 'nodejs', metadata, config)
        
        assert (plugin_path / 'config' / 'plugin.yaml').exists()
        assert (plugin_path / 'config' / 'nodejs_config.yaml').exists()
        assert (plugin_path / 'package.json').exists()


class TestStepHandler:
    """Test step handler."""
    
    @pytest.fixture
    def handler(self):
        """Create step handler instance."""
        return StepHandler()
    
    def test_get_type_selection_data(self, handler):
        """Test getting type selection step data."""
        data = handler.get_step_data('type_selection')
        
        assert 'title' in data
        assert 'options' in data
        assert len(data['options']) == 5  # PHP, Python, PowerShell, Node.js, Shell
    
    def test_get_metadata_data(self, handler):
        """Test getting metadata step data."""
        data = handler.get_step_data('metadata')
        
        assert 'title' in data
        assert 'fields' in data
        assert any(f['name'] == 'name' for f in data['fields'])
        assert any(f['name'] == 'description' for f in data['fields'])
    
    def test_get_python_config_data(self, handler):
        """Test getting Python configuration data."""
        data = handler.get_step_data('configuration', 'python')
        
        assert 'title' in data
        assert 'fields' in data
        assert any(f['name'] == 'python_version' for f in data['fields'])
        assert any(f['name'] == 'venv_enabled' for f in data['fields'])
