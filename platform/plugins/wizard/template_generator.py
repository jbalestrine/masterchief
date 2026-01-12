"""
Template generator for plugin configuration files.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any
from .wizard_engine import PluginMetadata

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """Generate configuration templates for different plugin types."""
    
    def __init__(self):
        """Initialize template generator."""
        self.logger = logging.getLogger(__name__)
    
    def generate_templates(
        self,
        plugin_path: Path,
        plugin_type: str,
        metadata: PluginMetadata,
        configuration: Dict[str, Any]
    ):
        """
        Generate all necessary templates for a plugin.
        
        Args:
            plugin_path: Path to plugin directory
            plugin_type: Type of plugin
            metadata: Plugin metadata
            configuration: Plugin-specific configuration
        """
        config_dir = plugin_path / 'config'
        
        # Generate main plugin.yaml
        self._generate_main_config(config_dir, metadata, plugin_type)
        
        # Generate type-specific config
        if plugin_type == 'php':
            self._generate_php_config(config_dir, configuration)
        elif plugin_type == 'python':
            self._generate_python_config(config_dir, configuration)
            self._generate_requirements_txt(plugin_path, configuration)
        elif plugin_type == 'powershell':
            self._generate_powershell_config(config_dir, configuration)
        elif plugin_type == 'nodejs':
            self._generate_nodejs_config(plugin_path, metadata, configuration)
        elif plugin_type == 'shell':
            self._generate_shell_config(config_dir, configuration)
        
        logger.info(f"Templates generated for {plugin_type} plugin at {plugin_path}")
    
    def _generate_main_config(self, config_dir: Path, metadata: PluginMetadata, plugin_type: str):
        """Generate main plugin.yaml configuration."""
        config = {
            'plugin': {
                'name': metadata.name,
                'version': metadata.version,
                'description': metadata.description,
                'author': metadata.author,
                'type': plugin_type,
                'tags': metadata.tags,
                'enabled': True,
                'dependencies': metadata.dependencies
            },
            'logging': {
                'level': 'INFO',
                'file': f'logs/{metadata.name}.log',
                'max_size': '10M',
                'backup_count': 5
            }
        }
        
        config_path = config_dir / 'plugin.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Generated main config: {config_path}")
    
    def _generate_php_config(self, config_dir: Path, config: Dict[str, Any]):
        """Generate PHP-specific configuration."""
        php_config = {
            'php': {
                'version': config.get('php_version', '8.2'),
                'memory_limit': config.get('memory_limit', '256M'),
                'upload_max_filesize': config.get('upload_max_filesize', '64M'),
                'post_max_size': config.get('post_max_size', '64M'),
                'max_execution_time': config.get('max_execution_time', 300),
                'extensions': config.get('extensions', ['curl', 'mbstring', 'xml', 'json']),
                'ini_overrides': {}
            }
        }
        
        config_path = config_dir / 'php_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(php_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Generated PHP config: {config_path}")
    
    def _generate_python_config(self, config_dir: Path, config: Dict[str, Any]):
        """Generate Python-specific configuration."""
        python_config = {
            'python': {
                'version': config.get('python_version', '3.10'),
                'venv_enabled': config.get('venv_enabled', True),
                'venv_path': config.get('venv_path', '.venv'),
                'dependencies': config.get('dependencies', ['flask>=2.0', 'requests', 'pyyaml']),
                'entry_point': config.get('entry_point', 'main.py'),
                'environment': {}
            }
        }
        
        config_path = config_dir / 'python_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(python_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Generated Python config: {config_path}")
    
    def _generate_requirements_txt(self, plugin_path: Path, config: Dict[str, Any]):
        """Generate requirements.txt for Python plugins."""
        dependencies = config.get('dependencies', ['flask>=2.0', 'requests', 'pyyaml'])
        
        requirements_path = plugin_path / 'requirements.txt'
        with open(requirements_path, 'w') as f:
            for dep in dependencies:
                f.write(f"{dep}\n")
        
        logger.info(f"Generated requirements.txt: {requirements_path}")
    
    def _generate_powershell_config(self, config_dir: Path, config: Dict[str, Any]):
        """Generate PowerShell-specific configuration."""
        ps_config = {
            'powershell': {
                'version': config.get('ps_version', '7.0'),
                'execution_policy': config.get('execution_policy', 'RemoteSigned'),
                'modules': config.get('modules', ['Az', 'PSReadLine']),
                'script_signing': config.get('script_signing', False),
                'entry_point': config.get('entry_point', 'main.ps1')
            }
        }
        
        config_path = config_dir / 'powershell_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(ps_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Generated PowerShell config: {config_path}")
    
    def _generate_nodejs_config(
        self,
        plugin_path: Path,
        metadata: PluginMetadata,
        config: Dict[str, Any]
    ):
        """Generate Node.js-specific configuration and package.json."""
        # Generate nodejs_config.yaml
        config_dir = plugin_path / 'config'
        nodejs_config = {
            'nodejs': {
                'version': config.get('node_version', '18'),
                'package_manager': config.get('package_manager', 'npm'),
                'entry_point': config.get('entry_point', 'index.js'),
                'environment': {}
            }
        }
        
        config_path = config_dir / 'nodejs_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(nodejs_config, f, default_flow_style=False, sort_keys=False)
        
        # Generate package.json
        dependencies_list = config.get('dependencies', ['express', 'dotenv'])
        dependencies = {}
        for dep in dependencies_list:
            if '@' in dep:
                name, version = dep.split('@', 1)
                dependencies[name] = version
            else:
                dependencies[dep] = 'latest'
        
        package_json = {
            'name': metadata.name,
            'version': metadata.version,
            'description': metadata.description,
            'main': config.get('entry_point', 'index.js'),
            'scripts': {
                'start': 'node index.js',
                'test': 'echo "Error: no test specified" && exit 1'
            },
            'keywords': metadata.tags,
            'author': metadata.author,
            'license': 'MIT',
            'dependencies': dependencies
        }
        
        package_path = plugin_path / 'package.json'
        with open(package_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        logger.info(f"Generated Node.js config and package.json: {config_path}")
    
    def _generate_shell_config(self, config_dir: Path, config: Dict[str, Any]):
        """Generate Shell-specific configuration."""
        shell_config = {
            'shell': {
                'shell_type': config.get('shell_type', 'bash'),
                'entry_point': config.get('entry_point', 'main.sh'),
                'environment': config.get('environment', {})
            }
        }
        
        config_path = config_dir / 'shell_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(shell_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Generated Shell config: {config_path}")
