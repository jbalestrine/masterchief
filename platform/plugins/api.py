"""Plugin API endpoints."""
import logging
import os
from pathlib import Path
from werkzeug.utils import secure_filename

from flask import Blueprint, jsonify, request

from .manager import PluginManager

logger = logging.getLogger(__name__)

plugins_bp = Blueprint('plugins', __name__)
plugin_manager = PluginManager()

ALLOWED_EXTENSIONS = {'zip'}
UPLOAD_FOLDER = '/tmp/plugin_uploads'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@plugins_bp.route('/', methods=['GET'])
def list_plugins():
    """List all installed plugins.
    
    Returns:
        JSON response with list of plugins
    """
    try:
        plugins = plugin_manager.list_plugins()
        return jsonify({
            'success': True,
            'plugins': plugins,
            'count': len(plugins)
        })
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@plugins_bp.route('/<plugin_id>', methods=['GET'])
def get_plugin(plugin_id):
    """Get plugin information by ID.
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        JSON response with plugin information
    """
    try:
        plugin = plugin_manager.get_plugin(plugin_id)
        if plugin:
            return jsonify({
                'success': True,
                'plugin': plugin
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Plugin not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting plugin {plugin_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@plugins_bp.route('/upload', methods=['POST'])
def upload_plugin():
    """Upload and install a plugin.
    
    Expects a multipart/form-data request with:
        - file: Plugin zip file
        - name (optional): Plugin name
        
    Returns:
        JSON response with installation result
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only .zip files are allowed'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Get optional plugin name
        plugin_name = request.form.get('name')
        
        # Install plugin
        result = plugin_manager.install_plugin(file_path, plugin_name)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error uploading plugin: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@plugins_bp.route('/<plugin_id>', methods=['DELETE'])
def remove_plugin(plugin_id):
    """Remove a plugin.
    
    Args:
        plugin_id: Plugin identifier
        
    Returns:
        JSON response with removal result
    """
    try:
        result = plugin_manager.remove_plugin(plugin_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error removing plugin {plugin_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@plugins_bp.route('/<plugin_id>/update', methods=['POST'])
def update_plugin(plugin_id):
    """Update a plugin.
    
    Args:
        plugin_id: Plugin identifier
        
    Expects a multipart/form-data request with:
        - file: Plugin zip file
        
    Returns:
        JSON response with update result
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only .zip files are allowed'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Update plugin
        result = plugin_manager.update_plugin(plugin_id, file_path)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error updating plugin {plugin_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
