"""Tests for module loader."""
import pytest
from pathlib import Path
from core.module_loader import ModuleLoader, ModuleManifest


def test_module_manifest_creation():
    """Test creating a module manifest from data."""
    data = {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module",
        "author": "Test Author",
        "type": "generic",
        "dependencies": [],
    }
    
    manifest = ModuleManifest(data)
    
    assert manifest.name == "test-module"
    assert manifest.version == "1.0.0"
    assert manifest.description == "Test module"
    assert manifest.author == "Test Author"
    assert manifest.module_type == "generic"


def test_module_loader_initialization():
    """Test module loader initialization."""
    loader = ModuleLoader(module_dirs=[Path("modules")])
    
    assert loader is not None
    assert len(loader.modules) == 0
    assert len(loader.load_order) == 0


def test_module_loader_list_modules():
    """Test listing modules."""
    loader = ModuleLoader()
    
    modules = loader.list_modules()
    
    assert isinstance(modules, list)
