from flask import Blueprint, jsonify, request, current_app
import subprocess
import json
import shutil
import uuid
from pathlib import Path

azure_bp = Blueprint('azure', __name__)

def _az_cli_available():
    return shutil.which('az') is not None

# Simple CRUD for 3rd-party service hooks (Azure DevOps) stored locally and optionally executed via az devops

HOOKS_FILE = Path(__file__).resolve().parent.parent / 'data' / 'azure_hooks.json'

def _load_hooks():
    try:
        if HOOKS_FILE.exists():
            return json.loads(HOOKS_FILE.read_text(encoding='utf-8'))
    except Exception:
        current_app.logger.exception('Failed to read hooks file')
    return {}

def _save_hooks(h):
    try:
        HOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        HOOKS_FILE.write_text(json.dumps(h, indent=2), encoding='utf-8')
    except Exception:
        current_app.logger.exception('Failed to save hooks file')

@azure_bp.route('/api/ado/hooks', methods=['GET','POST','DELETE'])
def api_ado_hooks():
    if request.method == 'GET':
        return jsonify({'ok': True, 'hooks': _load_hooks()})

    data = request.get_json(silent=True) or {}
    hooks = _load_hooks()

    if request.method == 'POST':
        # add or update hook
        hid = data.get('id') or uuid.uuid4().hex
        hooks[hid] = data
        _save_hooks(hooks)
        return jsonify({'ok': True, 'id': hid})

    if request.method == 'DELETE':
        hid = data.get('id')
        if hid and hid in hooks:
            hooks.pop(hid)
            _save_hooks(hooks)
            return jsonify({'ok': True})
        return jsonify({'ok': False, 'error': 'id not found'}), 404

    return jsonify({'ok': True, 'hooks': hooks})

def _az_cli_available():
    return shutil.which('az') is not None

@azure_bp.route('/api/azure/groups')
def api_azure_groups():
    """List Azure resource groups (uses `az group list` if available)."""
    if not _az_cli_available():
        return jsonify({'ok': False, 'error': 'az CLI not available on server'}), 501

    try:
        proc = subprocess.run(['az', 'group', 'list', '--output', 'json'], capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            return jsonify({'ok': False, 'error': proc.stderr}), 500

        data = json.loads(proc.stdout)
        return jsonify({'ok': True, 'groups': data})
    except Exception as e:
        current_app.logger.exception('az group list failed')
        return jsonify({'ok': False, 'error': str(e)}), 500

@azure_bp.route('/api/azure/resources')
def api_azure_resources():
    """List Azure resources (optionally filter by resource group via ?rg=name)."""
    rg = request.args.get('rg')
    if not _az_cli_available():
        return jsonify({'ok': False, 'error': 'az CLI not available on server'}), 501

    try:
        cmd = ['az', 'resource', 'list', '--output', 'json']
        if rg:
            cmd.extend(['--resource-group', rg])

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        if proc.returncode != 0:
            return jsonify({'ok': False, 'error': proc.stderr}), 500

        data = json.loads(proc.stdout)
        return jsonify({'ok': True, 'resources': data})
    except Exception as e:
        current_app.logger.exception('az resource list failed')
        return jsonify({'ok': False, 'error': str(e)}), 500

@azure_bp.route('/api/azure/storage/accounts')
def api_azure_storage_accounts():
    """List storage accounts."""
    if not _az_cli_available():
        return jsonify({'ok': False, 'error': 'az CLI not available on server'}), 501

    try:
        proc = subprocess.run(['az', 'storage', 'account', 'list', '--output', 'json'], capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            return jsonify({'ok': False, 'error': proc.stderr}), 500

        data = json.loads(proc.stdout)
        return jsonify({'ok': True, 'accounts': data})
    except Exception as e:
        current_app.logger.exception('az storage account list failed')
        return jsonify({'ok': False, 'error': str(e)}), 500

@azure_bp.route('/api/azure/storage/containers', methods=['POST'])
def api_azure_storage_containers():
    """List or create containers. POST JSON: { account: name, action: 'list'|'create', container: name }

    Note: requires appropriate az login and RBAC on server or using SAS/key parameters (not implemented).
    """
    data = request.get_json(silent=True) or {}
    account = data.get('account')
    action = data.get('action') or 'list'
    container = data.get('container')

    if not account:
        return jsonify({'ok': False, 'error': 'account required'}), 400

    if not _az_cli_available():
        return jsonify({'ok': False, 'error': 'az CLI not available on server'}), 501

    try:
        if action == 'list':
            proc = subprocess.run(['az', 'storage', 'container', 'list', '--account-name', account, '--output', 'json'], capture_output=True, text=True, timeout=30)
            if proc.returncode != 0:
                return jsonify({'ok': False, 'error': proc.stderr}), 500

            return jsonify({'ok': True, 'containers': json.loads(proc.stdout)})

        elif action == 'create':
            if not container:
                return jsonify({'ok': False, 'error': 'container required for create'}), 400

            proc = subprocess.run(['az', 'storage', 'container', 'create', '--account-name', account, '--name', container, '--output', 'json'], capture_output=True, text=True, timeout=30)
            if proc.returncode != 0:
                return jsonify({'ok': False, 'error': proc.stderr}), 500

            return jsonify({'ok': True, 'result': json.loads(proc.stdout)})
        else:
            return jsonify({'ok': False, 'error': 'unknown action'}), 400
    except Exception as e:
        current_app.logger.exception('az storage container operation failed')
        return jsonify({'ok': False, 'error': str(e)}), 500

@azure_bp.route('/api/azure/create_rg', methods=['POST'])
def api_azure_create_rg():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    location = data.get('location') or 'eastus'

    if not name:
        return jsonify({'ok': False, 'error': 'name required'}), 400

    if not _az_cli_available():
        return jsonify({'ok': False, 'error': 'az CLI not available on server'}), 501

    try:
        proc = subprocess.run(['az', 'group', 'create', '--name', name, '--location', location, '--output', 'json'], capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            return jsonify({'ok': False, 'error': proc.stderr}), 500

        return jsonify({'ok': True, 'result': json.loads(proc.stdout)})
    except Exception as e:
        current_app.logger.exception('az group create failed')
        return jsonify({'ok': False, 'error': str(e)}), 500
