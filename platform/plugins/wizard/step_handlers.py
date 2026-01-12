"""
Individual step handlers for wizard workflow.
"""

import logging
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class StepType(Enum):
    """Step types."""
    TYPE_SELECTION = "type_selection"
    METADATA = "metadata"
    CONFIGURATION = "configuration"
    REVIEW = "review"


class StepHandler:
    """Base class for wizard step handlers."""
    
    def __init__(self):
        """Initialize step handler."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_step_data(self, step_type: str, plugin_type: str = None) -> Dict[str, Any]:
        """
        Get data structure for a specific step.
        
        Args:
            step_type: Type of step
            plugin_type: Plugin type (for configuration step)
            
        Returns:
            Step data dictionary
        """
        if step_type == StepType.TYPE_SELECTION.value:
            return self._get_type_selection_data()
        elif step_type == StepType.METADATA.value:
            return self._get_metadata_data()
        elif step_type == StepType.CONFIGURATION.value:
            return self._get_configuration_data(plugin_type)
        elif step_type == StepType.REVIEW.value:
            return self._get_review_data()
        else:
            return {'error': 'Invalid step type'}
    
    def _get_type_selection_data(self) -> Dict[str, Any]:
        """Get type selection step data."""
        return {
            'title': 'Select Plugin Type',
            'description': 'Choose the type of plugin you want to create',
            'options': [
                {
                    'value': 'php',
                    'label': 'PHP',
                    'description': 'PHP-based plugin for web applications',
                    'icon': 'php'
                },
                {
                    'value': 'python',
                    'label': 'Python',
                    'description': 'Python-based plugin for scripting and automation',
                    'icon': 'python'
                },
                {
                    'value': 'powershell',
                    'label': 'PowerShell',
                    'description': 'PowerShell plugin for Windows automation',
                    'icon': 'powershell'
                },
                {
                    'value': 'nodejs',
                    'label': 'Node.js',
                    'description': 'Node.js plugin for JavaScript-based services',
                    'icon': 'nodejs'
                },
                {
                    'value': 'shell',
                    'label': 'Shell/Bash',
                    'description': 'Shell script plugin for Unix/Linux automation',
                    'icon': 'terminal'
                }
            ]
        }
    
    def _get_metadata_data(self) -> Dict[str, Any]:
        """Get metadata step data."""
        return {
            'title': 'Plugin Metadata',
            'description': 'Provide basic information about your plugin',
            'fields': [
                {
                    'name': 'name',
                    'label': 'Plugin Name',
                    'type': 'text',
                    'required': True,
                    'placeholder': 'my-awesome-plugin',
                    'validation': {
                        'pattern': '^[a-z0-9-]+$',
                        'message': 'Use lowercase letters, numbers, and hyphens only'
                    }
                },
                {
                    'name': 'description',
                    'label': 'Description',
                    'type': 'textarea',
                    'required': True,
                    'placeholder': 'Brief description of your plugin'
                },
                {
                    'name': 'version',
                    'label': 'Version',
                    'type': 'text',
                    'required': False,
                    'default': '1.0.0',
                    'placeholder': '1.0.0'
                },
                {
                    'name': 'author',
                    'label': 'Author',
                    'type': 'text',
                    'required': False,
                    'placeholder': 'Your Name'
                },
                {
                    'name': 'tags',
                    'label': 'Tags',
                    'type': 'tags',
                    'required': False,
                    'placeholder': 'Add tags (comma-separated)'
                },
                {
                    'name': 'dependencies',
                    'label': 'Dependencies',
                    'type': 'list',
                    'required': False,
                    'placeholder': 'Add dependencies'
                }
            ]
        }
    
    def _get_configuration_data(self, plugin_type: str = None) -> Dict[str, Any]:
        """Get configuration step data."""
        if plugin_type == 'php':
            return self._get_php_config()
        elif plugin_type == 'python':
            return self._get_python_config()
        elif plugin_type == 'powershell':
            return self._get_powershell_config()
        elif plugin_type == 'nodejs':
            return self._get_nodejs_config()
        elif plugin_type == 'shell':
            return self._get_shell_config()
        else:
            return {
                'title': 'Plugin Configuration',
                'description': 'Configure your plugin',
                'fields': []
            }
    
    def _get_php_config(self) -> Dict[str, Any]:
        """Get PHP configuration fields."""
        return {
            'title': 'PHP Configuration',
            'description': 'Configure PHP-specific settings',
            'fields': [
                {
                    'name': 'php_version',
                    'label': 'PHP Version',
                    'type': 'select',
                    'required': True,
                    'default': '8.2',
                    'options': ['7.4', '8.0', '8.1', '8.2', '8.3']
                },
                {
                    'name': 'memory_limit',
                    'label': 'Memory Limit',
                    'type': 'text',
                    'required': False,
                    'default': '256M',
                    'placeholder': '256M'
                },
                {
                    'name': 'upload_max_filesize',
                    'label': 'Upload Max Filesize',
                    'type': 'text',
                    'required': False,
                    'default': '64M',
                    'placeholder': '64M'
                },
                {
                    'name': 'post_max_size',
                    'label': 'Post Max Size',
                    'type': 'text',
                    'required': False,
                    'default': '64M',
                    'placeholder': '64M'
                },
                {
                    'name': 'max_execution_time',
                    'label': 'Max Execution Time (seconds)',
                    'type': 'number',
                    'required': False,
                    'default': 300
                },
                {
                    'name': 'extensions',
                    'label': 'PHP Extensions',
                    'type': 'multiselect',
                    'required': False,
                    'default': ['curl', 'mbstring', 'xml', 'json'],
                    'options': ['curl', 'mbstring', 'xml', 'json', 'pdo', 'mysqli', 'gd', 'zip', 'openssl']
                }
            ]
        }
    
    def _get_python_config(self) -> Dict[str, Any]:
        """Get Python configuration fields."""
        return {
            'title': 'Python Configuration',
            'description': 'Configure Python-specific settings',
            'fields': [
                {
                    'name': 'python_version',
                    'label': 'Python Version',
                    'type': 'select',
                    'required': True,
                    'default': '3.10',
                    'options': ['3.8', '3.9', '3.10', '3.11', '3.12']
                },
                {
                    'name': 'venv_enabled',
                    'label': 'Enable Virtual Environment',
                    'type': 'checkbox',
                    'required': False,
                    'default': True
                },
                {
                    'name': 'venv_path',
                    'label': 'Virtual Environment Path',
                    'type': 'text',
                    'required': False,
                    'default': '.venv',
                    'placeholder': '.venv'
                },
                {
                    'name': 'entry_point',
                    'label': 'Entry Point',
                    'type': 'text',
                    'required': False,
                    'default': 'main.py',
                    'placeholder': 'main.py'
                },
                {
                    'name': 'dependencies',
                    'label': 'Python Dependencies',
                    'type': 'list',
                    'required': False,
                    'default': ['flask>=2.0', 'requests', 'pyyaml'],
                    'placeholder': 'package>=version'
                }
            ]
        }
    
    def _get_powershell_config(self) -> Dict[str, Any]:
        """Get PowerShell configuration fields."""
        return {
            'title': 'PowerShell Configuration',
            'description': 'Configure PowerShell-specific settings',
            'fields': [
                {
                    'name': 'ps_version',
                    'label': 'PowerShell Version',
                    'type': 'select',
                    'required': True,
                    'default': '7.0',
                    'options': ['5.1', '7.0', '7.1', '7.2', '7.3', '7.4']
                },
                {
                    'name': 'execution_policy',
                    'label': 'Execution Policy',
                    'type': 'select',
                    'required': True,
                    'default': 'RemoteSigned',
                    'options': ['Restricted', 'AllSigned', 'RemoteSigned', 'Unrestricted', 'Bypass']
                },
                {
                    'name': 'modules',
                    'label': 'PowerShell Modules',
                    'type': 'list',
                    'required': False,
                    'default': ['Az', 'PSReadLine'],
                    'placeholder': 'Module name'
                },
                {
                    'name': 'script_signing',
                    'label': 'Enable Script Signing',
                    'type': 'checkbox',
                    'required': False,
                    'default': False
                },
                {
                    'name': 'entry_point',
                    'label': 'Entry Point',
                    'type': 'text',
                    'required': False,
                    'default': 'main.ps1',
                    'placeholder': 'main.ps1'
                }
            ]
        }
    
    def _get_nodejs_config(self) -> Dict[str, Any]:
        """Get Node.js configuration fields."""
        return {
            'title': 'Node.js Configuration',
            'description': 'Configure Node.js-specific settings',
            'fields': [
                {
                    'name': 'node_version',
                    'label': 'Node.js Version',
                    'type': 'select',
                    'required': True,
                    'default': '18',
                    'options': ['14', '16', '18', '20', '21']
                },
                {
                    'name': 'package_manager',
                    'label': 'Package Manager',
                    'type': 'select',
                    'required': True,
                    'default': 'npm',
                    'options': ['npm', 'yarn', 'pnpm']
                },
                {
                    'name': 'entry_point',
                    'label': 'Entry Point',
                    'type': 'text',
                    'required': False,
                    'default': 'index.js',
                    'placeholder': 'index.js'
                },
                {
                    'name': 'dependencies',
                    'label': 'NPM Dependencies',
                    'type': 'list',
                    'required': False,
                    'default': ['express', 'dotenv'],
                    'placeholder': 'package@version'
                }
            ]
        }
    
    def _get_shell_config(self) -> Dict[str, Any]:
        """Get Shell configuration fields."""
        return {
            'title': 'Shell Configuration',
            'description': 'Configure Shell-specific settings',
            'fields': [
                {
                    'name': 'shell_type',
                    'label': 'Shell Type',
                    'type': 'select',
                    'required': True,
                    'default': 'bash',
                    'options': ['bash', 'sh', 'zsh', 'fish']
                },
                {
                    'name': 'entry_point',
                    'label': 'Entry Point',
                    'type': 'text',
                    'required': False,
                    'default': 'main.sh',
                    'placeholder': 'main.sh'
                },
                {
                    'name': 'environment',
                    'label': 'Environment Variables',
                    'type': 'keyvalue',
                    'required': False,
                    'placeholder': 'KEY=VALUE'
                }
            ]
        }
    
    def _get_review_data(self) -> Dict[str, Any]:
        """Get review step data."""
        return {
            'title': 'Review & Confirm',
            'description': 'Review your plugin configuration before creation',
            'actions': [
                {
                    'label': 'Go Back',
                    'action': 'back',
                    'style': 'secondary'
                },
                {
                    'label': 'Create Plugin',
                    'action': 'confirm',
                    'style': 'primary'
                }
            ]
        }
