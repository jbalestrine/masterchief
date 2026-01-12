"""
JSON Schema validator for plugin configurations.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validate plugin configurations against schemas."""
    
    def __init__(self):
        """Initialize schema validator."""
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Load configuration schemas for different plugin types.
        
        Returns:
            Dictionary of schemas by plugin type
        """
        return {
            'php': self._get_php_schema(),
            'python': self._get_python_schema(),
            'powershell': self._get_powershell_schema(),
            'nodejs': self._get_nodejs_schema(),
            'shell': self._get_shell_schema(),
        }
    
    def get_schema(self, plugin_type: str) -> Dict[str, Any]:
        """
        Get schema for a plugin type.
        
        Args:
            plugin_type: Type of plugin
            
        Returns:
            JSON schema dictionary
        """
        return self.schemas.get(plugin_type, {})
    
    def validate_config(
        self,
        plugin_type: str,
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate configuration against schema.
        
        Args:
            plugin_type: Type of plugin
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        schema = self.get_schema(plugin_type)
        
        if not schema:
            return True, []  # No schema, allow all
        
        errors = []
        
        # Basic validation (simplified without jsonschema library)
        # In production, use jsonschema library for full validation
        
        # Validate required fields
        required = schema.get('required', [])
        for field in required:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate properties
        properties = schema.get('properties', {})
        for key, value in config.items():
            if key in properties:
                prop_schema = properties[key]
                prop_errors = self._validate_property(key, value, prop_schema)
                errors.extend(prop_errors)
        
        return len(errors) == 0, errors
    
    def _validate_property(
        self,
        key: str,
        value: Any,
        schema: Dict[str, Any]
    ) -> List[str]:
        """
        Validate a single property.
        
        Args:
            key: Property key
            value: Property value
            schema: Property schema
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Type validation
        expected_type = schema.get('type')
        if expected_type:
            if expected_type == 'string' and not isinstance(value, str):
                errors.append(f"{key} must be a string")
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                errors.append(f"{key} must be a number")
            elif expected_type == 'integer' and not isinstance(value, int):
                errors.append(f"{key} must be an integer")
            elif expected_type == 'boolean' and not isinstance(value, bool):
                errors.append(f"{key} must be a boolean")
            elif expected_type == 'array' and not isinstance(value, list):
                errors.append(f"{key} must be an array")
            elif expected_type == 'object' and not isinstance(value, dict):
                errors.append(f"{key} must be an object")
        
        # Enum validation
        enum = schema.get('enum')
        if enum and value not in enum:
            errors.append(f"{key} must be one of: {', '.join(map(str, enum))}")
        
        # Pattern validation
        pattern = schema.get('pattern')
        if pattern and isinstance(value, str):
            import re
            if not re.match(pattern, value):
                errors.append(f"{key} does not match required pattern")
        
        # Min/max validation for numbers
        if isinstance(value, (int, float)):
            minimum = schema.get('minimum')
            maximum = schema.get('maximum')
            
            if minimum is not None and value < minimum:
                errors.append(f"{key} must be >= {minimum}")
            
            if maximum is not None and value > maximum:
                errors.append(f"{key} must be <= {maximum}")
        
        # Min/max length for strings
        if isinstance(value, str):
            min_length = schema.get('minLength')
            max_length = schema.get('maxLength')
            
            if min_length is not None and len(value) < min_length:
                errors.append(f"{key} must be at least {min_length} characters")
            
            if max_length is not None and len(value) > max_length:
                errors.append(f"{key} must be at most {max_length} characters")
        
        return errors
    
    def _get_php_schema(self) -> Dict[str, Any]:
        """Get PHP plugin schema."""
        return {
            'type': 'object',
            'properties': {
                'plugin': {
                    'type': 'object',
                    'required': ['name', 'version', 'description', 'type'],
                    'properties': {
                        'name': {'type': 'string', 'minLength': 3},
                        'version': {'type': 'string', 'pattern': r'^\d+\.\d+\.\d+'},
                        'description': {'type': 'string', 'minLength': 10},
                        'type': {'type': 'string', 'enum': ['php']},
                    }
                }
            },
            'required': ['plugin']
        }
    
    def _get_python_schema(self) -> Dict[str, Any]:
        """Get Python plugin schema."""
        return {
            'type': 'object',
            'properties': {
                'plugin': {
                    'type': 'object',
                    'required': ['name', 'version', 'description', 'type'],
                    'properties': {
                        'name': {'type': 'string', 'minLength': 3},
                        'version': {'type': 'string', 'pattern': r'^\d+\.\d+\.\d+'},
                        'description': {'type': 'string', 'minLength': 10},
                        'type': {'type': 'string', 'enum': ['python']},
                    }
                }
            },
            'required': ['plugin']
        }
    
    def _get_powershell_schema(self) -> Dict[str, Any]:
        """Get PowerShell plugin schema."""
        return {
            'type': 'object',
            'properties': {
                'plugin': {
                    'type': 'object',
                    'required': ['name', 'version', 'description', 'type'],
                    'properties': {
                        'name': {'type': 'string', 'minLength': 3},
                        'version': {'type': 'string', 'pattern': r'^\d+\.\d+\.\d+'},
                        'description': {'type': 'string', 'minLength': 10},
                        'type': {'type': 'string', 'enum': ['powershell']},
                    }
                }
            },
            'required': ['plugin']
        }
    
    def _get_nodejs_schema(self) -> Dict[str, Any]:
        """Get Node.js plugin schema."""
        return {
            'type': 'object',
            'properties': {
                'plugin': {
                    'type': 'object',
                    'required': ['name', 'version', 'description', 'type'],
                    'properties': {
                        'name': {'type': 'string', 'minLength': 3},
                        'version': {'type': 'string', 'pattern': r'^\d+\.\d+\.\d+'},
                        'description': {'type': 'string', 'minLength': 10},
                        'type': {'type': 'string', 'enum': ['nodejs']},
                    }
                }
            },
            'required': ['plugin']
        }
    
    def _get_shell_schema(self) -> Dict[str, Any]:
        """Get Shell plugin schema."""
        return {
            'type': 'object',
            'properties': {
                'plugin': {
                    'type': 'object',
                    'required': ['name', 'version', 'description', 'type'],
                    'properties': {
                        'name': {'type': 'string', 'minLength': 3},
                        'version': {'type': 'string', 'pattern': r'^\d+\.\d+\.\d+'},
                        'description': {'type': 'string', 'minLength': 10},
                        'type': {'type': 'string', 'enum': ['shell']},
                    }
                }
            },
            'required': ['plugin']
        }
