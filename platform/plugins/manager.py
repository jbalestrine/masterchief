"""Plugin Manager for MasterChief platform."""
import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugins for the MasterChief platform."""
    
    def __init__(self, plugins_dir: str = "modules"):
        """Initialize the plugin manager.
        
        Args:
            plugins_dir: Directory where plugins are stored
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all installed plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        plugins = []
        
        if not self.plugins_dir.exists():
            return plugins
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir():
                manifest_path = self._find_manifest(item)
                if manifest_path:
                    try:
                        manifest = self._read_manifest(manifest_path)
                        plugins.append({
                            'id': item.name,
                            'name': manifest.get('name', item.name),
                            'version': manifest.get('version', '1.0.0'),
                            'description': manifest.get('description', ''),
                            'author': manifest.get('author', ''),
                            'type': manifest.get('type', 'generic'),
                            'path': str(item),
                        })
                    except Exception as e:
                        logger.error(f"Failed to read manifest for {item.name}: {e}")
        
        return plugins
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get plugin information by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin information or None if not found
        """
        plugin_path = self.plugins_dir / plugin_id
        if not plugin_path.exists():
            return None
        
        manifest_path = self._find_manifest(plugin_path)
        if not manifest_path:
            return None
        
        try:
            manifest = self._read_manifest(manifest_path)
            return {
                'id': plugin_id,
                'name': manifest.get('name', plugin_id),
                'version': manifest.get('version', '1.0.0'),
                'description': manifest.get('description', ''),
                'author': manifest.get('author', ''),
                'type': manifest.get('type', 'generic'),
                'path': str(plugin_path),
            }
        except Exception as e:
            logger.error(f"Failed to get plugin {plugin_id}: {e}")
            return None
    
    def install_plugin(self, file_path: str, plugin_name: Optional[str] = None) -> Dict[str, Any]:
        """Install a plugin from a zip file.
        
        Args:
            file_path: Path to the plugin zip file
            plugin_name: Optional name for the plugin directory
            
        Returns:
            Dictionary with success status and plugin info or error message
        """
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract zip file
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find the plugin directory (should contain manifest)
                plugin_dir = None
                manifest_path = None
                
                # Check if manifest is in root of zip
                manifest_path = self._find_manifest(temp_path)
                if manifest_path:
                    plugin_dir = temp_path
                else:
                    # Check subdirectories
                    for item in temp_path.iterdir():
                        if item.is_dir():
                            manifest_path = self._find_manifest(item)
                            if manifest_path:
                                plugin_dir = item
                                break
                
                if not manifest_path or not plugin_dir:
                    return {
                        'success': False,
                        'error': 'No valid plugin manifest found in zip file'
                    }
                
                # Read manifest to get plugin name
                manifest = self._read_manifest(manifest_path)
                target_name = plugin_name or manifest.get('name', 'unknown-plugin')
                
                # Copy to plugins directory
                target_path = self.plugins_dir / target_name
                if target_path.exists():
                    return {
                        'success': False,
                        'error': f'Plugin {target_name} already exists'
                    }
                
                shutil.copytree(plugin_dir, target_path)
                
                logger.info(f"Successfully installed plugin: {target_name}")
                return {
                    'success': True,
                    'plugin': {
                        'id': target_name,
                        'name': manifest.get('name', target_name),
                        'version': manifest.get('version', '1.0.0'),
                        'description': manifest.get('description', ''),
                    }
                }
                
        except zipfile.BadZipFile:
            return {
                'success': False,
                'error': 'Invalid zip file'
            }
        except Exception as e:
            logger.error(f"Failed to install plugin: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Remove a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Dictionary with success status and message
        """
        try:
            plugin_path = self.plugins_dir / plugin_id
            
            if not plugin_path.exists():
                return {
                    'success': False,
                    'error': f'Plugin {plugin_id} not found'
                }
            
            # Remove the plugin directory
            shutil.rmtree(plugin_path)
            
            logger.info(f"Successfully removed plugin: {plugin_id}")
            return {
                'success': True,
                'message': f'Plugin {plugin_id} removed successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to remove plugin {plugin_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_plugin(self, plugin_id: str, file_path: str) -> Dict[str, Any]:
        """Update an existing plugin.
        
        Args:
            plugin_id: Plugin identifier
            file_path: Path to the new plugin zip file
            
        Returns:
            Dictionary with success status and plugin info or error message
        """
        # Remove old version
        remove_result = self.remove_plugin(plugin_id)
        if not remove_result['success']:
            return remove_result
        
        # Install new version
        return self.install_plugin(file_path, plugin_id)
    
    def _find_manifest(self, directory: Path) -> Optional[Path]:
        """Find a manifest file in a directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            Path to manifest file or None
        """
        manifest_files = ['manifest.yaml', 'manifest.yml', 'manifest.json']
        for filename in manifest_files:
            manifest_path = directory / filename
            if manifest_path.exists():
                return manifest_path
        return None
    
    def _read_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Read and parse a manifest file.
        
        Args:
            manifest_path: Path to manifest file
            
        Returns:
            Parsed manifest data
        """
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
