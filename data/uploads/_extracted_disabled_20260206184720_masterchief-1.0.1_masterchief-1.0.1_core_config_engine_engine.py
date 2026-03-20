"""Configuration engine for hierarchical configuration management."""
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigEngine:
    """Hierarchical configuration management with environment support."""

    def __init__(self, config_dir: Path, environment: str = "dev"):
        self.config_dir = config_dir
        self.environment = environment
        self.global_config: Dict[str, Any] = {}
        self.env_config: Dict[str, Any] = {}
        self.module_configs: Dict[str, Dict[str, Any]] = {}
        self._load_configs()

    def _load_configs(self):
        """Load all configuration files."""
        # Load global configuration
        global_config_path = self.config_dir / "global" / "config.yaml"
        if global_config_path.exists():
            with open(global_config_path, "r") as f:
                self.global_config = yaml.safe_load(f) or {}
            logger.info(f"Loaded global configuration from {global_config_path}")

        # Load environment-specific configuration
        env_config_path = self.config_dir / "environments" / f"{self.environment}.yaml"
        if env_config_path.exists():
            with open(env_config_path, "r") as f:
                self.env_config = yaml.safe_load(f) or {}
            logger.info(f"Loaded environment configuration for '{self.environment}'")

    def get(self, key: str, default: Any = None, module: Optional[str] = None) -> Any:
        """
        Get configuration value with hierarchical lookup.
        
        Lookup order:
        1. Module-specific config
        2. Environment config
        3. Global config
        4. Default value
        """
        # Check module config first
        if module and module in self.module_configs:
            if key in self.module_configs[module]:
                return self.module_configs[module][key]

        # Check environment config
        if key in self.env_config:
            return self.env_config[key]

        # Check global config
        if key in self.global_config:
            return self.global_config[key]

        return default

    def get_nested(self, path: str, default: Any = None, separator: str = ".") -> Any:
        """Get nested configuration value using dot notation."""
        keys = path.split(separator)
        value = self.global_config

        # Try to find in environment config first
        env_value: Any = self.env_config
        for key in keys:
            if isinstance(env_value, dict) and key in env_value:
                env_value = env_value[key]
            else:
                env_value = None
                break
        
        if env_value is not None:
            return env_value

        # Fallback to global config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set_module_config(self, module_name: str, config: Dict[str, Any]):
        """Set module-specific configuration."""
        self.module_configs[module_name] = config
        logger.debug(f"Set configuration for module: {module_name}")

    def load_module_config(self, module_name: str, config_path: Path):
        """Load module configuration from file."""
        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}
            self.set_module_config(module_name, config)
            logger.info(f"Loaded module configuration for: {module_name}")
            return True
        return False

    def resolve_secrets(self, value: Any) -> Any:
        """
        Resolve secret references in configuration values.
        
        Supports references like:
        - ${vault:secret-name}
        - ${keyvault:secret-name}
        - ${env:ENV_VAR}
        """
        if not isinstance(value, str):
            return value

        if value.startswith("${") and value.endswith("}"):
            ref = value[2:-1]
            
            if ref.startswith("env:"):
                env_var = ref[4:]
                return os.environ.get(env_var, value)
            
            elif ref.startswith("vault:") or ref.startswith("keyvault:"):
                # Placeholder for vault integration
                secret_name = ref.split(":", 1)[1]
                logger.warning(f"Vault integration not yet implemented for: {secret_name}")
                return value

        return value

    def get_all(self, module: Optional[str] = None) -> Dict[str, Any]:
        """Get all configuration as a merged dictionary."""
        merged = {}
        merged.update(self.global_config)
        merged.update(self.env_config)
        
        if module and module in self.module_configs:
            merged.update(self.module_configs[module])
        
        return merged

    def reload(self):
        """Reload all configuration files."""
        self._load_configs()
        logger.info("Configuration reloaded")

    @property
    def current_environment(self) -> str:
        """Get current environment name."""
        return self.environment

    def switch_environment(self, environment: str):
        """Switch to a different environment."""
        self.environment = environment
        self._load_configs()
        logger.info(f"Switched to environment: {environment}")
