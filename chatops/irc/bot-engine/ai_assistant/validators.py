"""
Validation rules for AI assistant.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class AssistantValidators:
    """Validation rules and conflict detection."""
    
    def __init__(self):
        """Initialize validators."""
        self.logger = logging.getLogger(__name__)
    
    def detect_conflicts(
        self,
        plugin_type: str,
        config: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Detect conflicting settings in configuration.
        
        Args:
            plugin_type: Type of plugin
            config: Configuration to check
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        if plugin_type == 'php':
            conflicts.extend(self._check_php_conflicts(config))
        elif plugin_type == 'python':
            conflicts.extend(self._check_python_conflicts(config))
        elif plugin_type == 'powershell':
            conflicts.extend(self._check_powershell_conflicts(config))
        elif plugin_type == 'nodejs':
            conflicts.extend(self._check_nodejs_conflicts(config))
        
        return conflicts
    
    def _check_php_conflicts(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check PHP-specific conflicts."""
        conflicts = []
        
        # Check memory limit vs upload size
        memory_limit = config.get('memory_limit', '256M')
        upload_size = config.get('upload_max_filesize', '64M')
        
        memory_mb = self._parse_size(memory_limit)
        upload_mb = self._parse_size(upload_size)
        
        if upload_mb > memory_mb * 0.8:
            conflicts.append({
                'type': 'resource_conflict',
                'field': 'memory_limit',
                'message': f'Upload size ({upload_size}) is too close to memory limit ({memory_limit}). '
                          f'Consider increasing memory_limit or decreasing upload_max_filesize.'
            })
        
        # Check post_max_size vs upload_max_filesize
        post_size = config.get('post_max_size', '64M')
        post_mb = self._parse_size(post_size)
        
        if upload_mb > post_mb:
            conflicts.append({
                'type': 'configuration_conflict',
                'field': 'post_max_size',
                'message': f'post_max_size ({post_size}) must be >= upload_max_filesize ({upload_size})'
            })
        
        return conflicts
    
    def _check_python_conflicts(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check Python-specific conflicts."""
        conflicts = []
        
        # Check venv enabled but no path
        venv_enabled = config.get('venv_enabled', True)
        venv_path = config.get('venv_path', '.venv')
        
        if venv_enabled and not venv_path:
            conflicts.append({
                'type': 'configuration_conflict',
                'field': 'venv_path',
                'message': 'Virtual environment is enabled but no path is specified'
            })
        
        return conflicts
    
    def _check_powershell_conflicts(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check PowerShell-specific conflicts."""
        conflicts = []
        
        # Check execution policy vs script signing
        policy = config.get('execution_policy', 'RemoteSigned')
        signing = config.get('script_signing', False)
        
        if policy in ['AllSigned', 'RemoteSigned'] and not signing:
            conflicts.append({
                'type': 'security_warning',
                'field': 'script_signing',
                'message': f'Execution policy is {policy} but script signing is disabled. '
                          f'You may need to sign scripts or change the policy.'
            })
        
        return conflicts
    
    def _check_nodejs_conflicts(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check Node.js-specific conflicts."""
        conflicts = []
        
        # No major conflicts to check for Node.js
        
        return conflicts
    
    def detect_misconfigurations(
        self,
        plugin_type: str,
        config: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Detect common misconfigurations.
        
        Args:
            plugin_type: Type of plugin
            config: Configuration to check
            
        Returns:
            List of misconfigurations
        """
        issues = []
        
        # Check for overly permissive settings
        if plugin_type == 'powershell':
            policy = config.get('execution_policy')
            if policy == 'Unrestricted':
                issues.append({
                    'type': 'security_risk',
                    'field': 'execution_policy',
                    'message': 'Execution policy "Unrestricted" is a security risk. '
                              'Consider using "RemoteSigned" instead.'
                })
        
        # Check for deprecated versions
        if plugin_type == 'python':
            version = config.get('python_version', '3.10')
            if version in ['3.6', '3.7']:
                issues.append({
                    'type': 'deprecation_warning',
                    'field': 'python_version',
                    'message': f'Python {version} is end-of-life. Consider upgrading to 3.10 or newer.'
                })
        
        return issues
    
    def check_folder_permissions(self, plugin_path: str) -> Dict[str, Any]:
        """
        Check folder permissions for plugin directory.
        
        Args:
            plugin_path: Path to plugin directory
            
        Returns:
            Permission check result
        """
        path = Path(plugin_path)
        
        if not path.exists():
            return {
                'valid': False,
                'error': 'Plugin directory does not exist'
            }
        
        issues = []
        
        # Check directory permissions
        if not os.access(path, os.R_OK):
            issues.append('Directory is not readable')
        
        if not os.access(path, os.W_OK):
            issues.append('Directory is not writable')
        
        if not os.access(path, os.X_OK):
            issues.append('Directory is not executable')
        
        # Check subdirectories
        for subdir in ['src', 'logs', 'config']:
            subpath = path / subdir
            if subpath.exists():
                if not os.access(subpath, os.R_OK | os.W_OK):
                    issues.append(f'{subdir}/ is not readable/writable')
        
        return {
            'valid': len(issues) == 0,
            'path': str(path),
            'issues': issues
        }
    
    def _parse_size(self, size_str: str) -> float:
        """
        Parse size string to MB.
        
        Args:
            size_str: Size string like '256M' or '1G'
            
        Returns:
            Size in MB
        """
        size_str = size_str.upper()
        
        if size_str.endswith('G'):
            return float(size_str[:-1]) * 1024
        elif size_str.endswith('M'):
            return float(size_str[:-1])
        elif size_str.endswith('K'):
            return float(size_str[:-1]) / 1024
        else:
            # Assume bytes
            return float(size_str) / (1024 * 1024)
