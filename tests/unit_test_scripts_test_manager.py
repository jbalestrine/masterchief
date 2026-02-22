"""Tests for script manager with automation features."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from addons.scripts.manager import ScriptManager


@pytest.fixture
def temp_scripts_dir(tmp_path):
    """Create a temporary scripts directory."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    return scripts_dir


@pytest.fixture
def manager_config(temp_scripts_dir):
    """Create manager configuration."""
    return {
        'ai_generation': {
            'enabled': False,  # Disabled for most tests
            'model': 'codellama',
            'ollama_url': 'http://localhost:11434'
        },
        'voice': {
            'enabled': False
        },
        'templates': {
            'enabled': True,
            'directory': None,  # Will use default
            'custom_directory': str(temp_scripts_dir / "custom_templates")
        },
        'validation': {
            'enabled': True,
            'block_dangerous': True,
            'require_validation': False
        },
        'scheduling': {
            'enabled': False,  # Disabled for basic tests
            'database': str(temp_scripts_dir / "schedules.db")
        }
    }


def test_manager_initialization(manager_config, monkeypatch):
    """Test script manager initialization."""
    monkeypatch.setattr(
        'addons.scripts.manager.Path',
        lambda x: Path(manager_config['scheduling']['database']).parent / "scripts"
    )
    
    manager = ScriptManager(config=manager_config)
    assert manager is not None


def test_manager_list_scripts(tmp_path, monkeypatch):
    """Test listing scripts."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create test script
    test_script = scripts_dir / "test.sh"
    test_script.write_text("#!/bin/bash\necho 'test'")
    
    # Patch scripts_dir
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    scripts = manager.list_scripts()
    assert isinstance(scripts, list)
    assert len(scripts) == 1
    assert scripts[0]['name'] == 'test.sh'


def test_manager_upload_script(tmp_path, monkeypatch):
    """Test uploading a script."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    result = manager.upload_script(
        name="backup.sh",
        content="#!/bin/bash\necho 'Backup'"
    )
    
    assert result is True
    assert (scripts_dir / "backup.sh").exists()


def test_manager_delete_script(tmp_path, monkeypatch):
    """Test deleting a script."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create test script
    test_script = scripts_dir / "delete_me.sh"
    test_script.write_text("#!/bin/bash\necho 'delete'")
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    result = manager.delete_script("delete_me.sh")
    assert result is True
    assert not test_script.exists()


def test_manager_get_script_content(tmp_path, monkeypatch):
    """Test getting script content."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create test script
    test_script = scripts_dir / "read_me.sh"
    content = "#!/bin/bash\necho 'Hello'"
    test_script.write_text(content)
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    read_content = manager.get_script_content("read_me.sh")
    assert read_content == content


def test_manager_execute_script(tmp_path, monkeypatch):
    """Test executing a script."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create executable test script
    test_script = scripts_dir / "execute.sh"
    test_script.write_text("#!/bin/bash\necho 'Executed'")
    test_script.chmod(0o755)
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    result = manager.execute_script("execute.sh")
    
    assert result['success'] is True
    assert result['return_code'] == 0
    assert 'Executed' in result['stdout']


def test_manager_list_templates(tmp_path, monkeypatch):
    """Test listing templates."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    # Mock templates
    from addons.scripts.templates import ScriptTemplates
    manager.templates = ScriptTemplates()
    
    templates = manager.list_templates()
    assert isinstance(templates, list)


def test_manager_validate_script_safe(tmp_path, monkeypatch):
    """Test validating a safe script."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create safe script
    safe_script = scripts_dir / "safe.sh"
    safe_script.write_text("#!/bin/bash\necho 'Safe'")
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    # Initialize validator
    from addons.scripts.validator import ScriptValidator
    manager.validator = ScriptValidator(block_dangerous=True)
    
    result = manager.validate_script("safe.sh")
    
    assert result is not None
    # Safe script should have no critical security issues
    assert all(issue.severity != 'critical' for issue in result.security_issues)


def test_manager_validate_script_dangerous(tmp_path, monkeypatch):
    """Test validating a dangerous script."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create dangerous script
    dangerous_script = scripts_dir / "dangerous.sh"
    dangerous_script.write_text("#!/bin/bash\nrm -rf /")
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    # Initialize validator
    from addons.scripts.validator import ScriptValidator
    manager.validator = ScriptValidator(block_dangerous=True)
    
    result = manager.validate_script("dangerous.sh")
    
    assert result is not None
    assert result.valid is False
    assert len(result.security_issues) > 0


def test_manager_dry_run_script(tmp_path, monkeypatch):
    """Test dry running a script."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    # Create valid script
    valid_script = scripts_dir / "valid.sh"
    valid_script.write_text("#!/bin/bash\necho 'test'")
    
    monkeypatch.setattr(ScriptManager, '__init__', lambda self, config=None: None)
    manager = ScriptManager()
    manager.scripts_dir = scripts_dir
    
    # Initialize validator
    from addons.scripts.validator import ScriptValidator
    manager.validator = ScriptValidator()
    
    result = manager.dry_run_script("valid.sh")
    
    assert result is not None
    assert result['success'] is True


def test_manager_without_optional_features(monkeypatch):
    """Test manager works without optional features."""
    # This tests graceful degradation when features are disabled
    config = {
        'ai_generation': {'enabled': False},
        'voice': {'enabled': False},
        'templates': {'enabled': False},
        'validation': {'enabled': False},
        'scheduling': {'enabled': False}
    }
    
    monkeypatch.setattr(
        'addons.scripts.manager.Path',
        lambda x: Path("/tmp/test_scripts")
    )
    
    manager = ScriptManager(config=config)
    
    # Manager should still work for basic operations
    assert manager is not None
    assert manager.ai_generator is None
    assert manager.voice_scripter is None
