"""
Web IDE - Monaco Editor based IDE
"""

from flask import Blueprint, jsonify, request, send_from_directory
import os

web_ide_bp = Blueprint('web_ide', __name__)

@web_ide_bp.route('/')
def index():
    """Serve IDE interface"""
    return jsonify({
        'message': 'Web IDE',
        'features': [
            'Monaco Editor',
            'Git Integration',
            'Integrated Terminal',
            'Multi-language support'
        ]
    })

@web_ide_bp.route('/files', methods=['GET'])
def list_files():
    """List files in workspace"""
    path = request.args.get('path', '/opt/masterchief')
    try:
        files = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            files.append({
                'name': entry,
                'type': 'directory' if os.path.isdir(full_path) else 'file',
                'path': full_path
            })
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_ide_bp.route('/files/<path:filepath>', methods=['GET'])
def read_file(filepath):
    """Read file content"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_ide_bp.route('/files/<path:filepath>', methods=['PUT'])
def write_file(filepath):
    """Write file content"""
    try:
        content = request.json.get('content', '')
        with open(filepath, 'w') as f:
            f.write(content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
