"""
REST API endpoints for Configuration Editor.
"""

from flask import Blueprint, request, jsonify
import logging

from .editor import ConfigEditor
from .schema_validator import SchemaValidator

logger = logging.getLogger(__name__)

# Create blueprint
config_editor_bp = Blueprint('config_editor', __name__)

# Initialize components
config_editor = ConfigEditor()
schema_validator = SchemaValidator()


@config_editor_bp.route('/<plugin_id>', methods=['GET'])
def get_config(plugin_id: str):
    """
    Get plugin configuration.
    
    GET /api/config/{plugin_id}
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        JSON response with configuration
    """
    try:
        config = config_editor.get_plugin_config(plugin_id)
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'config': config
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_editor_bp.route('/<plugin_id>', methods=['PUT'])
def update_config(plugin_id: str):
    """
    Update plugin configuration.
    
    PUT /api/config/{plugin_id}
    
    Args:
        plugin_id: Plugin identifier
        
    Request Body:
        JSON configuration
        
    Returns:
        JSON response with update status
    """
    try:
        config = request.get_json()
        
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuration is required'
            }), 400
        
        validate = request.args.get('validate', 'true').lower() == 'true'
        
        config_editor.update_plugin_config(plugin_id, config, validate=validate)
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'plugin_id': plugin_id
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_editor_bp.route('/<plugin_id>/validate', methods=['POST'])
def validate_config(plugin_id: str):
    """
    Validate configuration without saving.
    
    POST /api/config/{plugin_id}/validate
    
    Args:
        plugin_id: Plugin identifier
        
    Request Body:
        JSON configuration to validate
        
    Returns:
        JSON response with validation result
    """
    try:
        config = request.get_json()
        
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuration is required'
            }), 400
        
        result = config_editor.validate_config(plugin_id, config)
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'validation': result
        })
        
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_editor_bp.route('/<plugin_id>/schema', methods=['GET'])
def get_schema(plugin_id: str):
    """
    Get JSON schema for plugin type.
    
    GET /api/config/{plugin_id}/schema
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        JSON response with schema
    """
    try:
        # Get plugin type
        config = config_editor.get_plugin_config(plugin_id)
        plugin_type = config.get('plugin', {}).get('type', 'python')
        
        schema = schema_validator.get_schema(plugin_type)
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'plugin_type': plugin_type,
            'schema': schema
        })
        
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_editor_bp.route('/<plugin_id>/diff', methods=['POST'])
def get_diff(plugin_id: str):
    """
    Get diff of pending changes.
    
    POST /api/config/{plugin_id}/diff
    
    Args:
        plugin_id: Plugin identifier
        
    Request Body:
        JSON with new configuration
        
    Returns:
        JSON response with differences
    """
    try:
        new_config = request.get_json()
        
        if not new_config:
            return jsonify({
                'success': False,
                'error': 'Configuration is required'
            }), 400
        
        diffs = config_editor.get_config_diff(plugin_id, new_config)
        
        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'differences': diffs,
            'count': len(diffs)
        })
        
    except Exception as e:
        logger.error(f"Error getting diff: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
