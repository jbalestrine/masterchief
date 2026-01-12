"""Tests for plugin management."""
import os
import tempfile
import zipfile
from pathlib import Path

import pytest
import yaml

from platform.plugins.manager import PluginManager


@pytest.fixture
def plugin_manager():
    """Create a plugin manager with a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield PluginManager(plugins_dir=temp_dir)


@pytest.fixture
def sample_plugin_zip():
    """Create a sample plugin zip file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create plugin directory
        plugin_dir = Path(temp_dir) / "test-plugin"
        plugin_dir.mkdir()
        
        # Create manifest
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "author": "Test Author",
            "type": "generic",
        }
        
        manifest_path = plugin_dir / "manifest.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest, f)
        
        # Create plugin file
        plugin_file = plugin_dir / "main.py"
        with open(plugin_file, "w") as f:
            f.write("# Test plugin")
        
        # Create zip file
        zip_path = Path(temp_dir) / "test-plugin.zip"
        with zipfile.ZipFile(zip_path, "w") as zip_ref:
            zip_ref.write(manifest_path, "test-plugin/manifest.yaml")
            zip_ref.write(plugin_file, "test-plugin/main.py")
        
        yield str(zip_path)


def test_list_plugins_empty(plugin_manager):
    """Test listing plugins when none are installed."""
    plugins = plugin_manager.list_plugins()
    assert isinstance(plugins, list)
    assert len(plugins) == 0


def test_install_plugin(plugin_manager, sample_plugin_zip):
    """Test installing a plugin."""
    result = plugin_manager.install_plugin(sample_plugin_zip)
    
    assert result["success"] is True
    assert "plugin" in result
    assert result["plugin"]["name"] == "test-plugin"
    assert result["plugin"]["version"] == "1.0.0"


def test_install_plugin_with_custom_name(plugin_manager, sample_plugin_zip):
    """Test installing a plugin with a custom name."""
    result = plugin_manager.install_plugin(sample_plugin_zip, "custom-name")
    
    assert result["success"] is True
    assert result["plugin"]["id"] == "custom-name"


def test_install_duplicate_plugin(plugin_manager, sample_plugin_zip):
    """Test installing a plugin that already exists."""
    # Install first time
    plugin_manager.install_plugin(sample_plugin_zip)
    
    # Try to install again
    result = plugin_manager.install_plugin(sample_plugin_zip)
    
    assert result["success"] is False
    assert "already exists" in result["error"]


def test_list_plugins_after_install(plugin_manager, sample_plugin_zip):
    """Test listing plugins after installation."""
    plugin_manager.install_plugin(sample_plugin_zip)
    
    plugins = plugin_manager.list_plugins()
    assert len(plugins) == 1
    assert plugins[0]["name"] == "test-plugin"


def test_get_plugin(plugin_manager, sample_plugin_zip):
    """Test getting a specific plugin."""
    plugin_manager.install_plugin(sample_plugin_zip)
    
    plugin = plugin_manager.get_plugin("test-plugin")
    assert plugin is not None
    assert plugin["name"] == "test-plugin"
    assert plugin["version"] == "1.0.0"


def test_get_nonexistent_plugin(plugin_manager):
    """Test getting a plugin that doesn't exist."""
    plugin = plugin_manager.get_plugin("nonexistent")
    assert plugin is None


def test_remove_plugin(plugin_manager, sample_plugin_zip):
    """Test removing a plugin."""
    plugin_manager.install_plugin(sample_plugin_zip)
    
    result = plugin_manager.remove_plugin("test-plugin")
    
    assert result["success"] is True
    assert len(plugin_manager.list_plugins()) == 0


def test_remove_nonexistent_plugin(plugin_manager):
    """Test removing a plugin that doesn't exist."""
    result = plugin_manager.remove_plugin("nonexistent")
    
    assert result["success"] is False
    assert "not found" in result["error"]


def test_install_invalid_zip(plugin_manager):
    """Test installing an invalid zip file."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
        f.write(b"not a zip file")
        temp_path = f.name
    
    try:
        result = plugin_manager.install_plugin(temp_path)
        assert result["success"] is False
        assert "Invalid zip file" in result["error"]
    finally:
        os.unlink(temp_path)


def test_install_zip_without_manifest(plugin_manager):
    """Test installing a zip without a manifest."""
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "no-manifest.zip"
        
        # Create zip without manifest
        with zipfile.ZipFile(zip_path, "w") as zip_ref:
            zip_ref.writestr("test.txt", "test content")
        
        result = plugin_manager.install_plugin(str(zip_path))
        assert result["success"] is False
        assert "No valid plugin manifest" in result["error"]
