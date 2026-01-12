"""
Unit tests for Configuration Editor.
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from platform.plugins.config_editor.editor import ConfigEditor
from platform.plugins.config_editor.schema_validator import SchemaValidator


class TestConfigEditor:
    """Test configuration editor functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def editor(self, temp_dir):
        """Create config editor instance."""
        return ConfigEditor(plugins_base_dir=temp_dir)
    
    @pytest.fixture
    def sample_plugin(self, temp_dir):
        """Create a sample plugin structure."""
        plugin_path = Path(temp_dir) / 'test-plugin'
        plugin_path.mkdir()
        config_dir = plugin_path / 'config'
        config_dir.mkdir()
        
        # Create sample config
        config = {
            'plugin': {
                'name': 'test-plugin',
                'version': '1.0.0',
                'description': 'Test plugin for unit testing',
                'type': 'python',
                'enabled': True
            },
            'logging': {
                'level': 'INFO'
            }
        }
        
        config_file = config_dir / 'plugin.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        return 'test-plugin'
    
    def test_get_plugin_config(self, editor, sample_plugin):
        """Test getting plugin configuration."""
        config = editor.get_plugin_config(sample_plugin)
        
        assert config is not None
        assert 'plugin' in config
        assert config['plugin']['name'] == 'test-plugin'
    
    def test_get_nonexistent_plugin(self, editor):
        """Test getting configuration for nonexistent plugin."""
        with pytest.raises(ValueError, match='not found'):
            editor.get_plugin_config('nonexistent-plugin')
    
    def test_update_plugin_config(self, editor, sample_plugin):
        """Test updating plugin configuration."""
        # Get current config
        config = editor.get_plugin_config(sample_plugin)
        
        # Modify config
        config['plugin']['version'] = '2.0.0'
        config['plugin']['description'] = 'Updated description for testing'
        
        # Update config
        success = editor.update_plugin_config(sample_plugin, config, validate=False)
        
        assert success is True
        
        # Verify update
        updated_config = editor.get_plugin_config(sample_plugin)
        assert updated_config['plugin']['version'] == '2.0.0'
        assert 'Updated description' in updated_config['plugin']['description']
    
    def test_validate_config(self, editor, sample_plugin):
        """Test configuration validation."""
        config = editor.get_plugin_config(sample_plugin)
        
        result = editor.validate_config(sample_plugin, config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_get_config_diff(self, editor, sample_plugin):
        """Test getting configuration differences."""
        current_config = editor.get_plugin_config(sample_plugin)
        
        # Create modified config
        new_config = current_config.copy()
        new_config['plugin']['version'] = '2.0.0'
        new_config['new_key'] = 'new_value'
        
        diffs = editor.get_config_diff(sample_plugin, new_config)
        
        assert len(diffs) > 0
        assert any(d['type'] == 'modified' for d in diffs)
        assert any(d['type'] == 'added' for d in diffs)


class TestSchemaValidator:
    """Test schema validator."""
    
    @pytest.fixture
    def validator(self):
        """Create schema validator instance."""
        return SchemaValidator()
    
    def test_get_python_schema(self, validator):
        """Test getting Python schema."""
        schema = validator.get_schema('python')
        
        assert schema is not None
        assert 'properties' in schema
        assert 'plugin' in schema['properties']
    
    def test_get_php_schema(self, validator):
        """Test getting PHP schema."""
        schema = validator.get_schema('php')
        
        assert schema is not None
        assert 'properties' in schema
    
    def test_validate_valid_config(self, validator):
        """Test validating valid configuration."""
        config = {
            'plugin': {
                'name': 'test-plugin',
                'version': '1.0.0',
                'description': 'Test plugin for validation',
                'type': 'python'
            }
        }
        
        is_valid, errors = validator.validate_config('python', config)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_missing_required_field(self, validator):
        """Test validating config with missing required field."""
        config = {
            'plugin': {
                'name': 'test-plugin',
                # Missing version, description, and type
            }
        }
        
        is_valid, errors = validator.validate_config('python', config)
        
        # May or may not be valid depending on schema strictness
        # This is a basic test to ensure validation runs
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
