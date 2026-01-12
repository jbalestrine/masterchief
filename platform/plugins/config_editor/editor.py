"""
Real-time configuration editor logic.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigEditor:
    """Real-time configuration editor."""
    
    def __init__(self, plugins_base_dir: str = "/opt/masterchief/plugins"):
        """
        Initialize config editor.
        
        Args:
            plugins_base_dir: Base directory for plugins
        """
        self.plugins_base_dir = Path(plugins_base_dir)
        self.pending_changes: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Config editor initialized with base dir: {plugins_base_dir}")
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get plugin configuration.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Configuration dictionary
        """
        plugin_path = self.plugins_base_dir / plugin_id
        
        if not plugin_path.exists():
            raise ValueError(f"Plugin '{plugin_id}' not found")
        
        config_path = plugin_path / 'config' / 'plugin.yaml'
        
        if not config_path.exists():
            raise ValueError(f"Configuration file not found for plugin '{plugin_id}'")
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded config for plugin: {plugin_id}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config for {plugin_id}: {e}")
            raise
    
    def update_plugin_config(
        self,
        plugin_id: str,
        config: Dict[str, Any],
        validate: bool = True
    ) -> bool:
        """
        Update plugin configuration.
        
        Args:
            plugin_id: Plugin identifier
            config: New configuration
            validate: Whether to validate before saving
            
        Returns:
            True if successful
        """
        plugin_path = self.plugins_base_dir / plugin_id
        
        if not plugin_path.exists():
            raise ValueError(f"Plugin '{plugin_id}' not found")
        
        config_path = plugin_path / 'config' / 'plugin.yaml'
        
        if validate:
            from .schema_validator import SchemaValidator
            validator = SchemaValidator()
            
            # Get plugin type from existing config
            try:
                existing_config = self.get_plugin_config(plugin_id)
                plugin_type = existing_config.get('plugin', {}).get('type', 'python')
            except:
                plugin_type = 'python'
            
            is_valid, errors = validator.validate_config(plugin_type, config)
            if not is_valid:
                raise ValueError(f"Configuration validation failed: {errors}")
        
        # Create backup
        backup_path = config_path.with_suffix('.yaml.bak')
        if config_path.exists():
            import shutil
            shutil.copy2(config_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Updated config for plugin: {plugin_id}")
            
            # Clear pending changes
            if plugin_id in self.pending_changes:
                del self.pending_changes[plugin_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating config for {plugin_id}: {e}")
            
            # Restore from backup
            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, config_path)
                logger.info(f"Restored from backup")
            
            raise
    
    def validate_config(
        self,
        plugin_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate configuration without saving.
        
        Args:
            plugin_id: Plugin identifier
            config: Configuration to validate
            
        Returns:
            Validation result dictionary
        """
        try:
            # Get plugin type
            existing_config = self.get_plugin_config(plugin_id)
            plugin_type = existing_config.get('plugin', {}).get('type', 'python')
            
            from .schema_validator import SchemaValidator
            validator = SchemaValidator()
            
            is_valid, errors = validator.validate_config(plugin_type, config)
            
            return {
                'valid': is_valid,
                'errors': errors if not is_valid else []
            }
            
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return {
                'valid': False,
                'errors': [str(e)]
            }
    
    def get_config_diff(
        self,
        plugin_id: str,
        new_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get differences between current and new configuration.
        
        Args:
            plugin_id: Plugin identifier
            new_config: New configuration
            
        Returns:
            List of differences
        """
        try:
            current_config = self.get_plugin_config(plugin_id)
            
            diffs = []
            self._compare_dicts(current_config, new_config, '', diffs)
            
            return diffs
            
        except Exception as e:
            logger.error(f"Error getting config diff: {e}")
            return []
    
    def _compare_dicts(
        self,
        dict1: Dict[str, Any],
        dict2: Dict[str, Any],
        path: str,
        diffs: List[Dict[str, Any]]
    ):
        """
        Recursively compare two dictionaries.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            path: Current path in the dictionary
            diffs: List to accumulate differences
        """
        # Check for added/modified keys
        for key in dict2:
            current_path = f"{path}.{key}" if path else key
            
            if key not in dict1:
                diffs.append({
                    'type': 'added',
                    'path': current_path,
                    'value': dict2[key]
                })
            elif isinstance(dict2[key], dict) and isinstance(dict1[key], dict):
                self._compare_dicts(dict1[key], dict2[key], current_path, diffs)
            elif dict1[key] != dict2[key]:
                diffs.append({
                    'type': 'modified',
                    'path': current_path,
                    'old_value': dict1[key],
                    'new_value': dict2[key]
                })
        
        # Check for removed keys
        for key in dict1:
            if key not in dict2:
                current_path = f"{path}.{key}" if path else key
                diffs.append({
                    'type': 'removed',
                    'path': current_path,
                    'value': dict1[key]
                })
    
    def set_pending_changes(self, plugin_id: str, changes: Dict[str, Any]):
        """
        Set pending changes for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            changes: Pending changes
        """
        self.pending_changes[plugin_id] = {
            'config': changes,
            'timestamp': datetime.now().isoformat()
        }
        logger.info(f"Set pending changes for plugin: {plugin_id}")
    
    def get_pending_changes(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pending changes for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Pending changes or None
        """
        return self.pending_changes.get(plugin_id)
    
    def clear_pending_changes(self, plugin_id: str):
        """
        Clear pending changes for a plugin.
        
        Args:
            plugin_id: Plugin identifier
        """
        if plugin_id in self.pending_changes:
            del self.pending_changes[plugin_id]
            logger.info(f"Cleared pending changes for plugin: {plugin_id}")
