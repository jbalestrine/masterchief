"""
Configuration Manager - Environment-based configuration with inheritance
Handles configuration loading, validation, and secret management integration
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Environment:
    """Environment configuration"""
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    parent: Optional[str] = None


class ConfigManager:
    """
    Configuration management system with environment-based configuration
    Supports variable inheritance and override system
    """
    
    def __init__(self, config_dir: str = "core/config"):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.environments: Dict[str, Environment] = {}
        self.global_config: Dict[str, Any] = {}
        self.current_env: Optional[str] = None
        
    def load_global_config(self) -> Dict[str, Any]:
        """
        Load global configuration that applies to all environments
        
        Returns:
            Global configuration dictionary
        """
        config_file = self.config_dir / "global.yaml"
        
        if not config_file.exists():
            logger.warning(f"Global config file {config_file} not found")
            return {}
        
        try:
            with open(config_file, 'r') as f:
                self.global_config = yaml.safe_load(f) or {}
            logger.info("Loaded global configuration")
            return self.global_config
        except Exception as e:
            logger.error(f"Error loading global config: {e}")
            return {}
    
    def load_environment(self, env_name: str) -> Environment:
        """
        Load environment-specific configuration
        
        Args:
            env_name: Name of the environment (dev, staging, prod)
            
        Returns:
            Environment object
        """
        if env_name in self.environments:
            return self.environments[env_name]
        
        config_file = self.config_dir / f"{env_name}.yaml"
        
        if not config_file.exists():
            logger.warning(f"Environment config file {config_file} not found")
            env = Environment(name=env_name)
        else:
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                
                env = Environment(
                    name=env_name,
                    config=data.get('config', {}),
                    secrets=data.get('secrets', {}),
                    parent=data.get('parent')
                )
                logger.info(f"Loaded environment configuration: {env_name}")
            except Exception as e:
                logger.error(f"Error loading environment config {env_name}: {e}")
                env = Environment(name=env_name)
        
        self.environments[env_name] = env
        return env
    
    def get_config(self, env_name: str, key: Optional[str] = None) -> Any:
        """
        Get configuration value with inheritance
        
        Args:
            env_name: Environment name
            key: Optional specific key to retrieve (dot notation supported)
            
        Returns:
            Configuration value or full configuration dictionary
        """
        # Build merged config with inheritance
        merged_config = self._build_inherited_config(env_name)
        
        if key is None:
            return merged_config
        
        # Support dot notation for nested keys (e.g., "azure.region")
        keys = key.split('.')
        value = merged_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def _build_inherited_config(self, env_name: str) -> Dict[str, Any]:
        """
        Build configuration with inheritance from parent environments
        
        Args:
            env_name: Environment name
            
        Returns:
            Merged configuration dictionary
        """
        if env_name not in self.environments:
            self.load_environment(env_name)
        
        env = self.environments[env_name]
        
        # Start with global config
        merged = self.global_config.copy()
        
        # Apply parent config if exists
        if env.parent:
            parent_config = self._build_inherited_config(env.parent)
            merged = self._deep_merge(merged, parent_config)
        
        # Apply environment-specific config
        merged = self._deep_merge(merged, env.config)
        
        return merged
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def set_config(self, env_name: str, key: str, value: Any) -> None:
        """
        Set configuration value for an environment
        
        Args:
            env_name: Environment name
            key: Configuration key (dot notation supported)
            value: Configuration value
        """
        if env_name not in self.environments:
            self.load_environment(env_name)
        
        env = self.environments[env_name]
        
        # Support dot notation
        keys = key.split('.')
        config = env.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Set config {key} = {value} for environment {env_name}")
    
    def load_secrets(self, env_name: str, secret_source: str = "env") -> Dict[str, str]:
        """
        Load secrets from various sources
        
        Args:
            env_name: Environment name
            secret_source: Source of secrets (env, azure-keyvault, github)
            
        Returns:
            Dictionary of secrets
        """
        if env_name not in self.environments:
            self.load_environment(env_name)
        
        env = self.environments[env_name]
        
        if secret_source == "env":
            # Load from environment variables
            for secret_key in env.secrets.keys():
                env_var = env.secrets[secret_key]
                if env_var.startswith("$"):
                    env_var = env_var[1:]  # Remove $ prefix
                value = os.environ.get(env_var)
                if value:
                    env.secrets[secret_key] = value
        
        # TODO: Implement Azure Key Vault and GitHub Secrets integration
        
        return env.secrets
    
    def get_secret(self, env_name: str, key: str) -> Optional[str]:
        """
        Get secret value for an environment
        
        Args:
            env_name: Environment name
            key: Secret key
            
        Returns:
            Secret value or None
        """
        if env_name not in self.environments:
            self.load_environment(env_name)
        
        return self.environments[env_name].secrets.get(key)
    
    def set_current_environment(self, env_name: str) -> None:
        """
        Set the current active environment
        
        Args:
            env_name: Environment name
        """
        if env_name not in self.environments:
            self.load_environment(env_name)
        self.current_env = env_name
        logger.info(f"Set current environment to: {env_name}")
    
    def get_current_environment(self) -> Optional[str]:
        """Get the current active environment name"""
        return self.current_env
    
    def list_environments(self) -> List[str]:
        """List all loaded environments"""
        return list(self.environments.keys())
    
    def save_environment(self, env_name: str) -> None:
        """
        Save environment configuration to file
        
        Args:
            env_name: Environment name
        """
        if env_name not in self.environments:
            logger.warning(f"Environment {env_name} not loaded")
            return
        
        env = self.environments[env_name]
        config_file = self.config_dir / f"{env_name}.yaml"
        
        data = {
            'config': env.config,
            'secrets': env.secrets
        }
        
        if env.parent:
            data['parent'] = env.parent
        
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            logger.info(f"Saved environment configuration: {env_name}")
        except Exception as e:
            logger.error(f"Error saving environment config {env_name}: {e}")
    
    def validate_config(self, env_name: str, schema: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate configuration against a schema
        
        Args:
            env_name: Environment name
            schema: Configuration schema
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        config = self.get_config(env_name)
        errors = []
        
        # Simple validation - check required keys
        required_keys = schema.get('required', [])
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")
        
        # TODO: Implement more comprehensive schema validation
        
        return len(errors) == 0, errors
