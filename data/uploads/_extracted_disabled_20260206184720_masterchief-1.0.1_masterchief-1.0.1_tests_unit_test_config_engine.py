"""Tests for configuration engine."""
import pytest
from pathlib import Path
from core.config_engine import ConfigEngine


def test_config_engine_initialization(tmp_path):
    """Test config engine initialization."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "global").mkdir()
    (config_dir / "environments").mkdir()
    
    engine = ConfigEngine(config_dir, environment="dev")
    
    assert engine is not None
    assert engine.environment == "dev"


def test_config_get_with_default(tmp_path):
    """Test getting config value with default."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "global").mkdir()
    (config_dir / "environments").mkdir()
    
    engine = ConfigEngine(config_dir, environment="dev")
    
    value = engine.get("nonexistent_key", default="default_value")
    
    assert value == "default_value"


def test_resolve_env_secrets(tmp_path):
    """Test resolving environment variable secrets."""
    import os
    os.environ["TEST_SECRET"] = "secret_value"
    
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "global").mkdir()
    (config_dir / "environments").mkdir()
    
    engine = ConfigEngine(config_dir, environment="dev")
    
    resolved = engine.resolve_secrets("${env:TEST_SECRET}")
    
    assert resolved == "secret_value"
