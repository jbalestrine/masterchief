"""
Input validation logic for plugin wizard.
"""

import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class PluginValidator:
    """Validator for plugin inputs."""
    
    # Plugin name pattern: lowercase letters, numbers, and hyphens
    NAME_PATTERN = re.compile(r'^[a-z0-9-]+$')
    
    # Version pattern: semantic versioning
    VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$')
    
    def __init__(self):
        """Initialize validator."""
        self.logger = logging.getLogger(__name__)
    
    def validate_plugin_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate plugin name.
        
        Args:
            name: Plugin name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Plugin name is required"
        
        if len(name) < 3:
            return False, "Plugin name must be at least 3 characters"
        
        if len(name) > 50:
            return False, "Plugin name must be less than 50 characters"
        
        if not self.NAME_PATTERN.match(name):
            return False, "Plugin name must contain only lowercase letters, numbers, and hyphens"
        
        if name.startswith('-') or name.endswith('-'):
            return False, "Plugin name cannot start or end with a hyphen"
        
        return True, ""
    
    def validate_version(self, version: str) -> Tuple[bool, str]:
        """
        Validate version string.
        
        Args:
            version: Version string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not version:
            return False, "Version is required"
        
        if not self.VERSION_PATTERN.match(version):
            return False, "Version must follow semantic versioning (e.g., 1.0.0)"
        
        return True, ""
    
    def validate_description(self, description: str) -> Tuple[bool, str]:
        """
        Validate description.
        
        Args:
            description: Description string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not description:
            return False, "Description is required"
        
        if len(description) < 10:
            return False, "Description must be at least 10 characters"
        
        if len(description) > 500:
            return False, "Description must be less than 500 characters"
        
        return True, ""
    
    def validate_dependencies(self, dependencies: List[str]) -> Tuple[bool, str]:
        """
        Validate dependencies list.
        
        Args:
            dependencies: List of dependencies
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(dependencies, list):
            return False, "Dependencies must be a list"
        
        for dep in dependencies:
            if not isinstance(dep, str):
                return False, f"Dependency must be a string: {dep}"
            
            if not dep.strip():
                return False, "Empty dependency found"
        
        return True, ""
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate complete metadata.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate name
        name = metadata.get('name')
        is_valid, error = self.validate_plugin_name(name)
        if not is_valid:
            return False, error
        
        # Validate description
        description = metadata.get('description')
        is_valid, error = self.validate_description(description)
        if not is_valid:
            return False, error
        
        # Validate version
        version = metadata.get('version', '1.0.0')
        is_valid, error = self.validate_version(version)
        if not is_valid:
            return False, error
        
        # Validate dependencies if provided
        dependencies = metadata.get('dependencies', [])
        is_valid, error = self.validate_dependencies(dependencies)
        if not is_valid:
            return False, error
        
        return True, ""
    
    def validate_php_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate PHP configuration.
        
        Args:
            config: PHP configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate memory limit format
        memory_limit = config.get('memory_limit', '256M')
        if not re.match(r'^\d+[MG]$', memory_limit):
            return False, "Memory limit must be in format like '256M' or '1G'"
        
        # Validate max execution time
        max_exec_time = config.get('max_execution_time', 300)
        if not isinstance(max_exec_time, int) or max_exec_time < 0:
            return False, "Max execution time must be a positive integer"
        
        return True, ""
    
    def validate_python_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Python configuration.
        
        Args:
            config: Python configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate Python version
        version = config.get('python_version', '3.10')
        valid_versions = ['3.8', '3.9', '3.10', '3.11', '3.12']
        if version not in valid_versions:
            return False, f"Python version must be one of: {', '.join(valid_versions)}"
        
        # Validate dependencies
        dependencies = config.get('dependencies', [])
        if not isinstance(dependencies, list):
            return False, "Dependencies must be a list"
        
        return True, ""
    
    def validate_powershell_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate PowerShell configuration.
        
        Args:
            config: PowerShell configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate execution policy
        policy = config.get('execution_policy', 'RemoteSigned')
        valid_policies = ['Restricted', 'AllSigned', 'RemoteSigned', 'Unrestricted', 'Bypass']
        if policy not in valid_policies:
            return False, f"Execution policy must be one of: {', '.join(valid_policies)}"
        
        return True, ""
    
    def validate_nodejs_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Node.js configuration.
        
        Args:
            config: Node.js configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate package manager
        pkg_manager = config.get('package_manager', 'npm')
        valid_managers = ['npm', 'yarn', 'pnpm']
        if pkg_manager not in valid_managers:
            return False, f"Package manager must be one of: {', '.join(valid_managers)}"
        
        return True, ""
    
    def validate_shell_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Shell configuration.
        
        Args:
            config: Shell configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate shell type
        shell_type = config.get('shell_type', 'bash')
        valid_shells = ['bash', 'sh', 'zsh', 'fish']
        if shell_type not in valid_shells:
            return False, f"Shell type must be one of: {', '.join(valid_shells)}"
        
        return True, ""
    
    def validate_configuration(self, plugin_type: str, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate plugin-specific configuration.
        
        Args:
            plugin_type: Type of plugin
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if plugin_type == 'php':
            return self.validate_php_config(config)
        elif plugin_type == 'python':
            return self.validate_python_config(config)
        elif plugin_type == 'powershell':
            return self.validate_powershell_config(config)
        elif plugin_type == 'nodejs':
            return self.validate_nodejs_config(config)
        elif plugin_type == 'shell':
            return self.validate_shell_config(config)
        else:
            return False, f"Unknown plugin type: {plugin_type}"
