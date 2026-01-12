"""Configuration engine for managing system configuration.

This module provides functionality for loading and managing system configuration.
"""

from typing import Any, Dict, Optional
import yaml


class ConfigEngine:
    """Manages system configuration."""
    
    def __init__(self):
        self.config_path: str = "config.yml"
        self.configs: Dict[str, Dict[str, Any]] = {}
    
    def load_config(self, path: str) -> bool:
        """Load configuration from a file.
        
        Args:
            path: The path to the configuration file
            
        Returns:
            True if the configuration was loaded successfully
        """
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
                self.configs[path] = config
                return True
        except Exception:
            return False
    
    def get_config(self, path: str, key: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration by path and optional key.
        
        Args:
            path: The configuration file path
            key: Optional key to retrieve specific config value
            
        Returns:
            The configuration dict or value
        """
        if path not in self.configs:
            return {}
        
        config_data = self.configs[path]
        
        if key:
            return config_data.get(key, {})
        
        return config_data
    
    def set_config(self, path: str, key: str, value: Any) -> bool:
        """Set a configuration value.
        
        Args:
            path: The configuration file path
            key: The configuration key
            value: The value to set
            
        Returns:
            True if the value was set successfully
        """
        if path not in self.configs:
            self.configs[path] = {}
        
        config = self.configs[path]
        config[key] = value
        
        return True
    
    def save_config(self, path: str) -> bool:
        """Save configuration to a file.
        
        Args:
            path: The path to save the configuration
            
        Returns:
            True if the configuration was saved successfully
        """
        if path not in self.configs:
            return False
        
        try:
            with open(path, 'w') as f:
                yaml.dump(self.configs[path], f)
                return True
        except Exception:
            return False
