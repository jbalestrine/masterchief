from flask import Blueprint, jsonify, request, current_app
from pathlib import Path
from werkzeug.utils import secure_filename
import subprocess
import sys

mock_bp = Blueprint('mock', __name__)

@mock_bp.route('/api/mock/generate', methods=['POST'])
def api_mock_generate():
    """Generate a docker-compose mock environment for a given terraform project.

    Expects JSON: { name: <project_name>, cloud: 'azure'|'aws'|'gcp' }

    """
    data = request.get_json(silent=True) or {}
    name = data.get('name') or 'tf_project'
    cloud = data.get('cloud') or 'azure'
    mock_type = data.get('mock_type') or 'docker'
    sf = secure_filename(name) or 'tf_project'

    try:
        from tools.terraform_wizard import WizardConfig, generate_mock_docker_compose, generate_mock_hyperv
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Import error: {e}'}), 500

    base = Path(current_app.root_path) / 'data' / 'terraform_projects'
    out_dir = base / sf

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        cfg = WizardConfig(name=sf, cloud=cloud, variables={}, resources=[])

        if mock_type == 'hyperv':
            mock_dir = generate_mock_hyperv(cfg, out_dir)
        else:
            mock_dir = generate_mock_docker_compose(cfg, out_dir)

        return jsonify({'ok': True, 'path': str(mock_dir.relative_to(Path(current_app.root_path)))})
    except Exception as e:
        current_app.logger.exception('Failed to generate mock environment')
        return jsonify({'ok': False, 'error': str(e)}), 500

@mock_bp.route('/api/mock/start', methods=['POST'])
def api_mock_start():
    data = request.get_json(silent=True) or {}
    path = data.get('path')
    mock_type = data.get('mock_type') or 'docker'

    if not path:
        return jsonify({'ok': False, 'error': 'path required'}), 400

    base = Path(current_app.root_path)
    mock_dir = (base / path).resolve()

    if not str(mock_dir).startswith(str(base)):
        return jsonify({'ok': False, 'error': 'invalid path'}), 400

    # choose script based on mock_type
    try:
        if mock_type == 'hyperv':
            start_script = mock_dir / 'start_mock_hyperv.ps1'
            if not start_script.exists():
                return jsonify({'ok': False, 'error': 'start script not found'}), 404

            if not sys.platform.startswith('win'):
                return jsonify({'ok': False, 'error': 'Hyper-V scripts can only be run on Windows'}), 501

            cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(start_script)]
        else:
            start_script = mock_dir / 'start_mock.sh'
            if not start_script.exists():
                return jsonify({'ok': False, 'error': 'start script not found'}), 404

            # attempt to use docker compose
            cmd = [str(start_script)]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if proc.returncode != 0:
            return jsonify({'ok': False, 'error': proc.stderr}), 500

        return jsonify({'ok': True, 'stdout': proc.stdout})
    except Exception as e:
        current_app.logger.exception('Failed to start mock services')
        return jsonify({'ok': False, 'error': str(e)}), 500

@mock_bp.route('/api/mock/stop', methods=['POST'])
def api_mock_stop():
    data = request.get_json(silent=True) or {}
    path = data.get('path')
    mock_type = data.get('mock_type') or 'docker'

    if not path:
        return jsonify({'ok': False, 'error': 'path required'}), 400

    base = Path(current_app.root_path)
    mock_dir = (base / path).resolve()

    if not str(mock_dir).startswith(str(base)):
        return jsonify({'ok': False, 'error': 'invalid path'}), 400

    try:
        if mock_type == 'hyperv':
            stop_script = mock_dir / 'stop_mock_hyperv.ps1'
            if not stop_script.exists():
                return jsonify({'ok': False, 'error': 'stop script not found'}), 404

            if not sys.platform.startswith('win'):
                return jsonify({'ok': False, 'error': 'Hyper-V scripts can only be run on Windows'}), 501

            cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(stop_script)]
        else:
            stop_script = mock_dir / 'stop_mock.sh'
            if not stop_script.exists():
                return jsonify({'ok': False, 'error': 'stop script not found'}), 404

            cmd = [str(stop_script)]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if proc.returncode != 0:
            return jsonify({'ok': False, 'error': proc.stderr}), 500

        return jsonify({'ok': True, 'stdout': proc.stdout})
    except Exception as e:
        current_app.logger.exception('Failed to stop mock services')
        return jsonify({'ok': False, 'error': str(e)}), 500
