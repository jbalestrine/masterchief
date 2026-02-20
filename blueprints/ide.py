from flask import Blueprint, jsonify, current_app
from pathlib import Path
from datetime import datetime

ide_bp = Blueprint('ide', __name__)

@ide_bp.route('/api/ide/scripts')
def api_ide_scripts():
    files = []
    try:
        scripts_dir = Path(current_app.config.get('SCRIPTS_FOLDER', 'data/scripts'))
        for p in sorted(scripts_dir.glob('*')):
            if p.is_file():
                files.append({'name': p.name, 'size': p.stat().st_size, 'modified': datetime.fromtimestamp(p.stat().st_mtime).isoformat()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

    # success
    return jsonify({'ok': True, 'files': files})
