"""
Default value suggestions engine.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DefaultSuggestions:
    """Suggest sensible defaults for plugin configurations."""
    
    def __init__(self):
        """Initialize suggestions engine."""
        self.logger = logging.getLogger(__name__)
    
    def get_defaults(self, plugin_type: str) -> Dict[str, Any]:
        """
        Get default configuration for a plugin type.
        
        Args:
            plugin_type: Type of plugin
            
        Returns:
            Default configuration
        """
        if plugin_type == 'php':
            return self._get_php_defaults()
        elif plugin_type == 'python':
            return self._get_python_defaults()
        elif plugin_type == 'powershell':
            return self._get_powershell_defaults()
        elif plugin_type == 'nodejs':
            return self._get_nodejs_defaults()
        elif plugin_type == 'shell':
            return self._get_shell_defaults()
        else:
            return {}
    
    def _get_php_defaults(self) -> Dict[str, Any]:
        """Get PHP defaults."""
        return {
            'php_version': '8.2',
            'memory_limit': '256M',
            'upload_max_filesize': '64M',
            'post_max_size': '64M',
            'max_execution_time': 300,
            'extensions': ['curl', 'mbstring', 'xml', 'json', 'pdo']
        }
    
    def _get_python_defaults(self) -> Dict[str, Any]:
        """Get Python defaults."""
        return {
            'python_version': '3.10',
            'venv_enabled': True,
            'venv_path': '.venv',
            'entry_point': 'main.py',
            'dependencies': ['flask>=2.0', 'requests', 'pyyaml']
        }
    
    def _get_powershell_defaults(self) -> Dict[str, Any]:
        """Get PowerShell defaults."""
        return {
            'ps_version': '7.0',
            'execution_policy': 'RemoteSigned',
            'modules': ['Az', 'PSReadLine'],
            'script_signing': False,
            'entry_point': 'main.ps1'
        }
    
    def _get_nodejs_defaults(self) -> Dict[str, Any]:
        """Get Node.js defaults."""
        return {
            'node_version': '18',
            'package_manager': 'npm',
            'entry_point': 'index.js',
            'dependencies': ['express', 'dotenv']
        }
    
    def _get_shell_defaults(self) -> Dict[str, Any]:
        """Get Shell defaults."""
        return {
            'shell_type': 'bash',
            'entry_point': 'main.sh',
            'environment': {}
        }
    
    def suggest_conflict_fix(
        self,
        plugin_type: str,
        conflict: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Suggest fix for a conflict.
        
        Args:
            plugin_type: Type of plugin
            conflict: Conflict description
            
        Returns:
            Suggested fix
        """
        field = conflict.get('field', '')
        conflict_type = conflict.get('type', '')
        
        if plugin_type == 'php':
            if 'memory_limit' in field:
                return {
                    'field': 'memory_limit',
                    'suggested_value': '512M',
                    'reason': 'Increase memory limit to accommodate larger uploads'
                }
            elif 'post_max_size' in field:
                return {
                    'field': 'post_max_size',
                    'suggested_value': '128M',
                    'reason': 'Increase post_max_size to be larger than upload_max_filesize'
                }
        
        elif plugin_type == 'powershell':
            if 'execution_policy' in field:
                return {
                    'field': 'execution_policy',
                    'suggested_value': 'RemoteSigned',
                    'reason': 'RemoteSigned provides good balance between security and usability'
                }
        
        return {}
    
    def suggest_config_fix(
        self,
        plugin_type: str,
        misconfig: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Suggest fix for a misconfiguration.
        
        Args:
            plugin_type: Type of plugin
            misconfig: Misconfiguration description
            
        Returns:
            Suggested fix
        """
        field = misconfig.get('field', '')
        
        if plugin_type == 'powershell' and 'execution_policy' in field:
            return {
                'field': 'execution_policy',
                'suggested_value': 'RemoteSigned',
                'reason': 'More secure than Unrestricted while still allowing script execution'
            }
        
        elif plugin_type == 'python' and 'python_version' in field:
            return {
                'field': 'python_version',
                'suggested_value': '3.10',
                'reason': 'Python 3.10 has better performance and security than older versions'
            }
        
        return {}
