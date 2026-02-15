#!/usr/bin/env python3

"""MasterChief Flask Web Application - All-in-One File"""

import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

# Ensure script directory is not in sys.path to avoid conflicts
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir in sys.path:
    sys.path.remove(_script_dir)



import json

import time

import psutil

import zipfile

import subprocess

from pathlib import Path

from datetime import datetime

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash, get_flashed_messages, send_file

import requests

from werkzeug.utils import secure_filename

from flask_cors import CORS

import hashlib

import base64

import shutil

import html

import difflib

import threading

import uuid

import io

import tempfile



# Determine an interpreter command for a given script path.

def _interpreter_cmd_for_path(p: Path, requested_shell=None):

    try:

        if requested_shell:

            rs = str(requested_shell).lower()

            if rs in ('python','py','python3'):

                return [sys.executable, str(p)]

            if rs in ('powershell','ps1','pwsh'):

                return ['powershell','-ExecutionPolicy','Bypass','-File', str(p)]

            if rs in ('bash','sh'):

                # honor explicit request for bash/sh only if available on PATH

                if shutil.which('bash'):

                    return ['bash', str(p)]

                if shutil.which('wsl'):

                    return ['wsl', str(p)]

                return None

        # common suffixes

        if p.suffix == '.py':

            return [sys.executable, str(p)]

        if p.suffix == '.ps1':

            return ['powershell','-ExecutionPolicy','Bypass','-File', str(p)]

        # On Windows, avoid implicitly selecting WSL/bash for unknown types.

        # Prefer explicit shells (python/powershell) to prevent invoking missing WSL binaries.

        if sys.mc_platform.startswith('win'):

            return None

        # on unix-like platforms run the file directly

        return [str(p)]

    except Exception:

        return None



# Add script dir back for local imports

sys.path.insert(0, _script_dir)

from echo.chat_bot import get_chat_bot, ResponseQuality, TrainingExample

from echo.conversation_storage import get_storage

import re

from collections import Counter



def _start_cleanup_thread(retention_days=30):

    def runner():

        while True:

            try:

                base = Path(__file__).parent / 'data' / 'models_output'

                if base.exists():

                    for d in base.iterdir():

                        if not d.is_dir():

                            continue

                        # skip train_jobs.json

                        if d.name == 'train_jobs.json':

                            continue

                        try:

                            mtime = d.stat().st_mtime

                            age_days = (time.time() - mtime) / (60*60*24)

                            if age_days > retention_days:

                                shutil.make_archive(str(d), 'zip', root_dir=str(d))

                                shutil.rmtree(d)

                        except Exception:

                            app.logger.exception('Failed to archive old job %s', d)

                # sleep between scans

                time.sleep(60*60*6)

            except Exception:

                app.logger.exception('Cleanup thread error')

                time.sleep(60*60)

    thread = threading.Thread(target=runner, daemon=True)

    thread.start()

from core.echo.identity import Echo

# Remove it again to avoid conflicts

sys.path.remove(_script_dir)

# Import authentication modules
try:
    from auth_config import auth_config
    from auth_module import init_auth
    from azure_integration import azure_integration
    from github_integration import github_integration
    from app_management import app_management
    AUTH_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Authentication modules not available: {e}")
    AUTH_MODULES_AVAILABLE = False

# Import setup wizard (works with or without auth modules)
try:
    from setup_wizard import init_setup_wizard
    SETUP_WIZARD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Failed to initialize setup wizard: {e}")
    SETUP_WIZARD_AVAILABLE = False

app=Flask(__name__)

app.config['SECRET_KEY']='masterchief-secret-key-change-in-production'

CORS(app)

app.jinja_env.filters['b64encode'] = lambda s: base64.urlsafe_b64encode(s.encode()).decode()

app.config['ADMIN_TOKEN'] = os.environ.get('ADMIN_TOKEN') or None

app.config['BASIC_AUTH_USER'] = os.environ.get('BASIC_AUTH_USER') or None

app.config['BASIC_AUTH_PASS'] = os.environ.get('BASIC_AUTH_PASS') or None

_data_dir=Path(__file__).parent/'data'

app.config['UPLOAD_FOLDER']=_data_dir/'uploads'

app.config['SCRIPTS_FOLDER']=_data_dir/'scripts'

app.config['MAX_CONTENT_LENGTH']=100*1024*1024

for folder in [app.config['UPLOAD_FOLDER'],app.config['SCRIPTS_FOLDER'],_data_dir]:

    folder.mkdir(parents=True,exist_ok=True)



# Initialize authentication modules if available
if AUTH_MODULES_AVAILABLE:
    try:
        # Initialize authentication
        init_auth(app)

        print("✅ Authentication modules initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize authentication modules: {e}")
        AUTH_MODULES_AVAILABLE = False
else:
    print("ℹ️  Authentication modules not available - running without authentication")

# Initialize setup wizard if available
if SETUP_WIZARD_AVAILABLE:
    try:
        init_setup_wizard(app)
        print("✅ Setup wizard initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize setup wizard: {e}")
        SETUP_WIZARD_AVAILABLE = False



# Helpers: environment boolean and generic value->bool parser

def _env_bool(name, default=False):

    v = os.environ.get(name)

    if v is None:

        return default

    return str(v).strip().lower() in ('1', 'true', 'yes', 'on')



def _parse_bool_val(v, default=None):

    if v is None:

        return default

    if isinstance(v, bool):

        return v

    try:

        s = str(v).strip().lower()

        if s in ('1', 'true', 'yes', 'on'):

            return True

        if s in ('0', 'false', 'no', 'off'):

            return False

    except Exception:

        pass

    return default



# Default for auto-continue (can be overridden by ECHO_AUTO_CONTINUE env var)

app.config['ECHO_AUTO_CONTINUE'] = _env_bool('ECHO_AUTO_CONTINUE', True)

app.config['ECHO_CONTINUE_PROMPT'] = os.environ.get('ECHO_CONTINUE_PROMPT', 'Continue the previous answer to the user\'s question. Stay strictly on that topic and do not introduce unrelated facts or change the subject.')

try:

    app.config['ECHO_CONTINUE_MAX_RETRIES'] = int(os.environ.get('ECHO_CONTINUE_MAX_RETRIES', '2'))

except Exception:

    app.config['ECHO_CONTINUE_MAX_RETRIES'] = 2

try:

    app.config['ECHO_CONTINUE_MIN_SIMILARITY'] = float(os.environ.get('ECHO_CONTINUE_MIN_SIMILARITY', '0.12'))

except Exception:

    app.config['ECHO_CONTINUE_MIN_SIMILARITY'] = 0.12

try:

    app.config['ECHO_OUTPUT_RETENTION_DAYS'] = int(os.environ.get('ECHO_OUTPUT_RETENTION_DAYS', '90'))

except Exception:

    app.config['ECHO_OUTPUT_RETENTION_DAYS'] = 90



# Image generation defaults (provider: 'horde' community or 'local' diffusers)

app.config['IMAGE_PROVIDER'] = os.environ.get('IMAGE_PROVIDER', 'horde')

app.config['IMAGE_RATE_LIMIT_PER_MIN'] = int(os.environ.get('IMAGE_RATE_LIMIT_PER_MIN', '6'))

app.config['IMAGE_CACHE_TTL'] = int(os.environ.get('IMAGE_CACHE_TTL', '86400'))  # seconds



# In-memory image cache: cache_key -> {'path': str(path), 'ts': time.time()}

IMAGE_CACHE = {}

# Rate limit tracker: key -> [timestamps]

IMAGE_RATE = {}

    # Async image job tracker: job_id -> {'status','progress','path','error'}
IMAGE_JOBS = {}



def _start_output_cleanup_thread(retention_days=None, interval_hours=24):

    retention_days = retention_days if retention_days is not None else app.config.get('ECHO_OUTPUT_RETENTION_DAYS', 30)

    def runner():

        outdir = Path(__file__).parent / 'data' / 'echo_chat_outputs'

        while True:

            try:

                if outdir.exists():

                    for p in outdir.glob('*.txt'):

                        try:

                            age_days = (time.time() - p.stat().st_mtime) / (60*60*24)

                            if age_days > retention_days:

                                p.unlink()

                        except Exception:

                            app.logger.exception('Failed to prune old echo output %s', p)

                time.sleep(interval_hours * 3600)

            except Exception:

                app.logger.exception('Echo output cleanup thread error')

                time.sleep(3600)

    t = threading.Thread(target=runner, daemon=True)

    t.start()



# start cleanup thread

try:

    _start_output_cleanup_thread()

except Exception:

    app.logger.exception('Failed to start echo output cleanup thread')



# Optionally force a default model for debugging via ECHO_FORCE_MODEL.

# If set (or the chosen fallback exists), persist it to data/echo_model.json

# so `/api/echo/preload_model` and the bot prefer this model.

try:

    forced_model = os.environ.get('ECHO_FORCE_MODEL') or None

    # sensible fallback for debugging (update if you prefer another model)

    if not forced_model:

        forced_model = str(Path.cwd() / 'models' / 'mistral-7b-instruct-v0.1.Q4_K_M.gguf')

    # resolve to absolute path

    p = Path(forced_model)

    if not p.is_absolute():

        p = Path.cwd() / p

    if p.exists():

        cfg = Path(__file__).parent / 'data' / 'echo_model.json'

        cfg.parent.mkdir(parents=True, exist_ok=True)

        cfg.write_text(json.dumps({'model': str(p)}), encoding='utf-8')

        app.logger.info(f'Forced default model set to: {p}')

    else:

        app.logger.info(f'Forced model not found, skipping: {p}')

except Exception:

    app.logger.exception('Failed to set forced default model')

# If user explicitly requests an immediate forced GGUF load, do it now.

# This bypasses the test-time guard and will load the model into memory.

try:

    if os.environ.get('ECHO_FORCE_LOAD') == '1':

        # determine model path: prefer explicit env, then persisted config

        model_path = os.environ.get('ECHO_FORCE_MODEL')

        if not model_path:

            cfg = Path(__file__).parent / 'data' / 'echo_model.json'

            if cfg.exists():

                try:

                    model_path = json.loads(cfg.read_text(encoding='utf-8')).get('model')

                except Exception:

                    model_path = None

        if model_path:

            try:

                from echo.runtime import model_runtime

                model_runtime.load_model(model_path, force=True)

                app.logger.info(f'Force-loaded GGUF model at startup: {model_path}')

            except Exception:

                app.logger.exception('Failed to force-load GGUF model')

        else:

            app.logger.warning('ECHO_FORCE_LOAD=1 but no model path found')

except Exception:

    app.logger.exception('Force model load check failed')

# Sessions index file (persistent metadata for chat sessions)





# Runtime chat/model initialization

chatbot = None



def get_default_model_path():

    cfg = Path(__file__).parent / 'data' / 'echo_model.json'

    if cfg.exists():

        try:

            return json.loads(cfg.read_text(encoding='utf-8')).get('model')

        except Exception:

            return None

    # sensible fallback (do not force existence here)

    candidate = Path.cwd() / 'models' / 'Phi-3-mini-4k-instruct-q4.gguf'

    return str(candidate) if candidate.exists() else None





def init_chat():

    """Initialize the Echo chat bot and (optionally) load the GGUF at runtime.



    Loading the heavy GGUF model is performed here so pytest collection

    and import-time operations never import native bindings.

    """

    global chatbot

    try:

        from echo.chat_bot import get_chat_bot

        from echo.runtime import model_runtime

        chatbot = get_chat_bot()

        model_path = get_default_model_path()

        if model_path:

            # set the preferred model path on the bot (no load yet)

            try:

                chatbot.set_local_model(model_path)

            except Exception:

                pass

            # perform explicit runtime load of the model

            try:

                model_runtime.load_model(model_path)

                app.logger.info(f'Runtime model loaded: {model_path}')

            except Exception:

                app.logger.exception('Failed to runtime-load model')

    except Exception:

        app.logger.exception('Chat initialization failed')









# --- Minimal Web IDE API endpoints -----------------------------------------------------

def _safe_script_path(filename: str):

    try:

        fname = secure_filename(filename)

        if not fname:

            return None

        return Path(app.config['SCRIPTS_FOLDER']) / fname

    except Exception:

        return None





@app.route('/api/ide/scripts')

def api_ide_scripts():

    files = []

    try:

        scripts_dir = Path(app.config['SCRIPTS_FOLDER'])

        for p in sorted(scripts_dir.glob('*')):

            if p.is_file():

                files.append({'name': p.name, 'size': p.stat().st_size, 'modified': datetime.fromtimestamp(p.stat().st_mtime).isoformat()})

    except Exception as e:

        return jsonify({'ok': False, 'error': str(e)}), 500



    # success

    return jsonify({'ok': True, 'files': files})





@app.route('/api/terraform/generate', methods=['POST'])

def api_terraform_generate():

    """Generate a Terraform project on the server from a wizard payload.

    Expects JSON: { name, cloud, backend, provider_settings, variables, resources }

    Returns: { ok: True, path: <relative path> }

    """

    data = request.get_json(silent=True) or {}

    name = data.get('name') or (data.get('config') or {}).get('name') or 'tf_project'

    # sanitize name

    sf = secure_filename(name) or 'tf_project'

    try:

        from tools.terraform_wizard import WizardConfig, create_project

    except Exception as e:

        return jsonify({'ok': False, 'error': f'Import error: {e}'}), 500

    base = Path(__file__).resolve().parent / 'data' / 'terraform_projects'

    out_dir = base / sf

    try:

        cfg = WizardConfig(

            name=sf,

            cloud=data.get('cloud', 'azure'),

            backend=data.get('backend'),

            provider_settings=data.get('provider_settings'),

            variables=data.get('variables'),

            resources=data.get('resources'),

        )

        create_project(cfg, out_dir)

        return jsonify({'ok': True, 'path': str(out_dir.relative_to(Path(__file__).resolve().parent))})

    except Exception as e:

        app.logger.exception('Failed to generate terraform project')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/mock/generate', methods=['POST'])

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

    base = Path(__file__).resolve().parent / 'data' / 'terraform_projects'

    out_dir = base / sf

    try:

        out_dir.mkdir(parents=True, exist_ok=True)

        cfg = WizardConfig(name=sf, cloud=cloud, variables={}, resources=[])

        if mock_type == 'hyperv':

            mock_dir = generate_mock_hyperv(cfg, out_dir)

        else:

            mock_dir = generate_mock_docker_compose(cfg, out_dir)

        return jsonify({'ok': True, 'path': str(mock_dir.relative_to(Path(__file__).resolve().parent))})

    except Exception as e:

        app.logger.exception('Failed to generate mock environment')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/mock/start', methods=['POST'])

def api_mock_start():

    data = request.get_json(silent=True) or {}

    path = data.get('path')

    mock_type = data.get('mock_type') or 'docker'

    if not path:

        return jsonify({'ok': False, 'error': 'path required'}), 400

    base = Path(__file__).resolve().parent

    mock_dir = (base / path).resolve()

    if not str(mock_dir).startswith(str(base)):

        return jsonify({'ok': False, 'error': 'invalid path'}), 400

    # choose script based on mock_type

    try:

        if mock_type == 'hyperv':

            start_script = mock_dir / 'start_mock_hyperv.ps1'

            if not start_script.exists():

                return jsonify({'ok': False, 'error': 'start script not found'}), 404

            if not sys.mc_platform.startswith('win'):

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

        app.logger.exception('Failed to start mock services')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/mock/stop', methods=['POST'])

def api_mock_stop():

    data = request.get_json(silent=True) or {}

    path = data.get('path')

    mock_type = data.get('mock_type') or 'docker'

    if not path:

        return jsonify({'ok': False, 'error': 'path required'}), 400

    base = Path(__file__).resolve().parent

    mock_dir = (base / path).resolve()

    if not str(mock_dir).startswith(str(base)):

        return jsonify({'ok': False, 'error': 'invalid path'}), 400

    try:

        if mock_type == 'hyperv':

            stop_script = mock_dir / 'stop_mock_hyperv.ps1'

            if not stop_script.exists():

                return jsonify({'ok': False, 'error': 'stop script not found'}), 404

            if not sys.mc_platform.startswith('win'):

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

        app.logger.exception('Failed to stop mock services')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/terraform/run', methods=['POST'])

def api_terraform_run():

    """Run terraform actions (init|plan|deploy) asynchronously and return exec_id.

    JSON: { action: 'init'|'plan'|'deploy', dir: '<relative path under data/terraform_projects>', auto_approve: bool }

    """

    data = request.get_json(silent=True) or {}

    action = data.get('action')

    rel = data.get('dir')

    if not action or action not in ('init', 'plan', 'deploy'):

        return jsonify({'ok': False, 'error': 'action required (init|plan|deploy)'}), 400

    base = Path(__file__).resolve().parent / 'data' / 'terraform_projects'

    if not rel:

        return jsonify({'ok': False, 'error': 'dir required'}), 400

    target = (base / rel).resolve()

    try:

        if not str(target).startswith(str(base.resolve())) or not target.exists():

            return jsonify({'ok': False, 'error': 'invalid dir'}), 400

    except Exception:

        return jsonify({'ok': False, 'error': 'invalid dir'}), 400



    # build command

    if action == 'init':

        cmd = ['terraform', 'init', '-input=false']

    elif action == 'plan':

        cmd = ['terraform', 'plan', '-out=tfplan', '-input=false']

    else:

        # deploy

        cmd = ['terraform', 'apply', '-auto-approve']



    exec_id = uuid.uuid4().hex

    EXEC_JOBS[exec_id] = {'id': exec_id, 'status': 'queued', 'cmd': cmd, 'pid': None, 'returncode': None, 'started_at': None, 'finished_at': None, 'cwd': str(target)}

    _start_job_thread(exec_id, cmd, cwd=str(target))

    return jsonify({'ok': True, 'exec_id': exec_id})





@app.route('/api/tf/validate', methods=['POST'])
def api_tf_validate():
    return jsonify({'ok': True, 'output': 'TF validate endpoint working'})





@app.route('/api/tf/plan', methods=['POST'])
def api_tf_plan():
    data = request.get_json(silent=True) or {}
    main_tf = data.get('main', '')
    variables_tf = data.get('variables', '')
    if not main_tf:
        return jsonify({'ok': False, 'error': 'main terraform code required'}), 400
    
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'main.tf').write_text(main_tf, encoding='utf-8')
            if variables_tf:
                Path(tmpdir, 'variables.tf').write_text(variables_tf, encoding='utf-8')
            
            # Init and plan
            proc = subprocess.run(['terraform', 'init', '-input=false'], cwd=tmpdir, capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                return jsonify({'ok': False, 'error': proc.stderr}), 500
            
            proc = subprocess.run(['terraform', 'plan', '-input=false'], cwd=tmpdir, capture_output=True, text=True, timeout=120)
            return jsonify({'ok': True, 'output': proc.stdout + proc.stderr}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/tf/apply', methods=['POST'])
def api_tf_apply():
    data = request.get_json(silent=True) or {}
    main_tf = data.get('main', '')
    variables_tf = data.get('variables', '')
    if not main_tf:
        return jsonify({'ok': False, 'error': 'main terraform code required'}), 400
    
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'main.tf').write_text(main_tf, encoding='utf-8')
            if variables_tf:
                Path(tmpdir, 'variables.tf').write_text(variables_tf, encoding='utf-8')
            
            # Init and apply
            proc = subprocess.run(['terraform', 'init', '-input=false'], cwd=tmpdir, capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                return jsonify({'ok': False, 'error': proc.stderr}), 500
            
            proc = subprocess.run(['terraform', 'apply', '-auto-approve', '-input=false'], cwd=tmpdir, capture_output=True, text=True, timeout=300)
            return jsonify({'ok': True, 'output': proc.stdout + proc.stderr}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/tf/destroy', methods=['POST'])
def api_tf_destroy():
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # For destroy, we need the state file, but since this is a demo, we'll assume local state
            # In a real implementation, you'd need to handle state files properly
            return jsonify({'ok': False, 'error': 'destroy not implemented for demo - requires state file'}), 501
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/tf/refresh')
def api_tf_refresh():
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            return jsonify({'ok': False, 'error': 'refresh not implemented for demo - requires state file'}), 501
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/tf/import', methods=['POST'])
def api_tf_import():
    data = request.get_json(silent=True) or {}
    address = data.get('address')
    resource_id = data.get('id')
    if not address or not resource_id:
        return jsonify({'ok': False, 'error': 'address and id required'}), 400
    
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            proc = subprocess.run(['terraform', 'import', address, resource_id], cwd=tmpdir, capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                return jsonify({'ok': False, 'output': proc.stderr}), 200
            return jsonify({'ok': True, 'output': proc.stdout}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/tf/state')
def api_tf_state():
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            return jsonify({'ok': False, 'error': 'state show not implemented for demo - requires state file'}), 501
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/tf/backup')
def api_tf_backup():
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy state file for demo
            state_content = '{"version": 4, "terraform_version": "1.0.0", "resources": []}'
            Path(tmpdir, 'terraform.tfstate').write_text(state_content, encoding='utf-8')
            return send_file(Path(tmpdir, 'terraform.tfstate'), as_attachment=True, download_name='terraform.tfstate.backup')
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





# ---------------- Azure Resource Manager / Storage / ADO hooks ---------------------------------

def _az_cli_available():

    return shutil.which('az') is not None





@app.route('/api/azure/groups')

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

        app.logger.exception('az group list failed')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/azure/resources')

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

        app.logger.exception('az resource list failed')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/azure/storage/accounts')

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

        app.logger.exception('az storage account list failed')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/azure/storage/containers', methods=['POST'])

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

        app.logger.exception('az storage container operation failed')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/azure/create_rg', methods=['POST'])

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

        app.logger.exception('az group create failed')

        return jsonify({'ok': False, 'error': str(e)}), 500





# Simple CRUD for 3rd-party service hooks (Azure DevOps) stored locally and optionally executed via az devops

HOOKS_FILE = Path(__file__).resolve().parent / 'data' / 'azure_hooks.json'



def _load_hooks():

    try:

        if HOOKS_FILE.exists():

            return json.loads(HOOKS_FILE.read_text(encoding='utf-8'))

    except Exception:

        app.logger.exception('Failed to read hooks file')

    return {}



def _save_hooks(h):

    try:

        HOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)

        HOOKS_FILE.write_text(json.dumps(h, indent=2), encoding='utf-8')

    except Exception:

        app.logger.exception('Failed to save hooks file')





@app.route('/api/ado/hooks', methods=['GET','POST','DELETE'])

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

    return jsonify({'ok': True, 'files': files})





@app.route('/api/ide/load', methods=['POST'])

def api_ide_load():

    data = request.get_json(silent=True) or (request.form if request.form else {})

    filename = data.get('filename') if isinstance(data, dict) else None

    if not filename:

        return jsonify({'ok': False, 'error': 'filename required'}), 400

    path = _safe_script_path(filename)

    if not path or not path.exists():

        return jsonify({'ok': False, 'error': 'file not found'}), 404

    try:

        content = path.read_text(encoding='utf-8')

        return jsonify({'ok': True, 'content': content})

    except Exception as e:

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/ide/save', methods=['POST'])

def api_ide_save():

    data = request.get_json(silent=True) or (request.form if request.form else {})

    filename = data.get('filename') if isinstance(data, dict) else None

    content = data.get('content','') if isinstance(data, dict) else (request.form.get('content','') if request.form else '')

    if not filename:

        return jsonify({'ok': False, 'error': 'filename required'}), 400

    try:

        script_mgr.add_script(filename, content)

        return jsonify({'ok': True, 'filename': filename})

    except Exception as e:

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/ide/execute', methods=['POST'])

def api_ide_execute():

    data = request.get_json(silent=True) or (request.form if request.form else {})

    filename = data.get('filename') if isinstance(data, dict) else None

    content = data.get('content') if isinstance(data, dict) else None

    shell = data.get('shell') if isinstance(data, dict) else None

    remote = bool(data.get('remote')) if isinstance(data, dict) else False

    if remote:

        return jsonify({'ok': False, 'error': 'remote execution not implemented'}), 501

    try:

        if filename:

            path = _safe_script_path(filename)

            if not path or not path.exists():

                if content:

                    script_mgr.add_script(filename, content)

                else:

                    return jsonify({'ok': False, 'error': 'file not found'}), 404

            result = script_mgr.execute_script(filename)

            return jsonify({'ok': True, 'stdout': result.get('stdout',''), 'stderr': result.get('stderr',''), 'returncode': result.get('returncode', -1)})

        elif content:

            # Choose a sensible default extension when the client didn't specify a shell.

            # Heuristics: if content looks like Python, use .py; on Windows prefer PowerShell.

            ext = None

            if shell == 'python':

                ext = '.py'

            elif shell in ('powershell','ps1'):

                ext = '.ps1'

            elif shell in ('bash','sh'):

                ext = '.sh'

            else:

                # simple python heuristics

                snippet = (content or '').strip()

                if snippet.startswith('#!') and 'python' in snippet.splitlines()[0].lower():

                    ext = '.py'

                elif any(token in snippet for token in ('print(', 'def ', 'import ', 'if __name__', 'class ')):

                    ext = '.py'

                else:

                    # On Windows default to PowerShell script to avoid missing bash/wsl

                    if sys.mc_platform.startswith('win'):

                        ext = '.ps1'

                    else:

                        ext = '.sh'

            fd, tmp = tempfile.mkstemp(suffix=ext, prefix='masterchief_exec_', dir=str(app.config['SCRIPTS_FOLDER']))

            os.close(fd)

            with open(tmp,'w',encoding='utf-8') as f:

                f.write(content)

            os.chmod(tmp, 0o755)

            p = Path(tmp)

            # Choose interpreter-aware command where possible

            cmd = _interpreter_cmd_for_path(p, requested_shell=shell)

            if not cmd:

                # No suitable interpreter found for this platform/type

                return jsonify({'ok': False, 'error': 'no suitable interpreter found for script on this platform; specify shell explicitly (python,powershell,bash)'}), 500

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            out = proc.stdout

            err = proc.stderr

            rc = proc.returncode

            try:

                p.unlink()

            except Exception:

                pass

            return jsonify({'ok': True, 'stdout': out, 'stderr': err, 'returncode': rc})

        else:

            return jsonify({'ok': False, 'error': 'no filename or content provided'}), 400

    except subprocess.TimeoutExpired:

        return jsonify({'ok': False, 'error':'execution timed out'}), 500

    except Exception as e:

        return jsonify({'ok': False, 'error': str(e)}), 500





# Remote credential storage for IDE remote execution (basic, stored in data/ide_creds.json)

CREDS_FILE = Path(__file__).resolve().parent / 'data' / 'ide_creds.json'



@app.route('/api/ide/remote/creds', methods=['POST'])

def api_ide_remote_creds_save():

    data = request.get_json(silent=True) or (request.form if request.form else {})

    target = data.get('target') if isinstance(data, dict) else (request.form.get('target') if request.form else None)

    username = data.get('username') if isinstance(data, dict) else (request.form.get('username') if request.form else None)

    password = data.get('password') if isinstance(data, dict) else (request.form.get('password') if request.form else None)

    if not target or not username or not password:

        return jsonify({'ok': False, 'error':'target,username,password required'}), 400

    try:

        d = {}

        if CREDS_FILE.exists():

            try:

                d = json.loads(CREDS_FILE.read_text(encoding='utf-8'))

            except Exception:

                d = {}

        d[target] = {'username': username, 'password': password, 'saved_at': datetime.now().isoformat()}

        CREDS_FILE.parent.mkdir(parents=True, exist_ok=True)

        CREDS_FILE.write_text(json.dumps(d, indent=2), encoding='utf-8')

        return jsonify({'ok': True})

    except Exception as e:

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/ide/remote/creds', methods=['GET'])

def api_ide_remote_creds_get():

    target = request.args.get('target')

    if not target:

        return jsonify({'ok': False, 'error': 'target required'}), 400

    try:

        if not CREDS_FILE.exists():

            return jsonify({'ok': True, 'cred': None})

        d = json.loads(CREDS_FILE.read_text(encoding='utf-8'))

        return jsonify({'ok': True, 'cred': d.get(target)})

    except Exception as e:

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/ide/log', methods=['POST'])

def api_ide_log():

    """Receive lightweight client-side logs from the Web IDE for debugging.

    POST JSON: { event: str, detail: any }

    """

    data = request.get_json(silent=True) or {}

    event = data.get('event')

    detail = data.get('detail')

    try:

        outdir = Path(__file__).parent / 'data' / 'ide_logs'

        outdir.mkdir(parents=True, exist_ok=True)

        fn = outdir / (datetime.utcnow().strftime('%Y-%m-%d') + '.log')

        with open(fn, 'a', encoding='utf-8') as f:

            f.write(json.dumps({'ts': datetime.utcnow().isoformat(), 'event': event, 'detail': detail}) + '\n')

        app.logger.info('IDE client log: %s %s', event, json.dumps(detail)[:200])

        return jsonify({'ok': True})

    except Exception as e:

        app.logger.exception('Failed to write IDE client log')

        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/ide/tree')

def api_ide_tree():

    # return directory tree under scripts folder; optional `path` query for subfolder

    rel = request.args.get('path','')

    try:

        base = Path(app.config['SCRIPTS_FOLDER']).resolve()

        target = (base / rel).resolve()

        if not str(target).startswith(str(base)):

            return jsonify({'ok': False, 'error':'invalid path'}), 400

        nodes = []

        for p in sorted(target.iterdir()):

            if p.is_dir():

                nodes.append({'type':'dir','name':p.name,'path':str(p.relative_to(base))})

            else:

                nodes.append({'type':'file','name':p.name,'path':str(p.relative_to(base)),'size':p.stat().st_size,'modified':datetime.fromtimestamp(p.stat().st_mtime).isoformat()})

        return jsonify({'ok':True,'path':str(target.relative_to(base)),'nodes':nodes})

    except Exception as e:

        return jsonify({'ok':False,'error':str(e)}),500





@app.route('/api/ide/exec_async', methods=['POST'])

def api_ide_exec_async():

    data = request.get_json(silent=True) or {}

    cmd = data.get('command') or data.get('content') or data.get('filename')

    cwd = data.get('cwd')

    if not cmd:

        return jsonify({'ok':False,'error':'command required'}),400

    exec_id = uuid.uuid4().hex

    EXEC_JOBS[exec_id] = {'id':exec_id,'status':'queued','cmd':cmd,'pid':None,'returncode':None,'started_at':None,'finished_at':None,'cwd':cwd}

    # determine actual command form: if user passed filename within scripts folder, run script

    # if cmd looks like a filename under scripts, run it

    base = Path(app.config['SCRIPTS_FOLDER']).resolve()

    try:

        maybe = base / cmd

        if maybe.exists():

            # run file

            command = str(maybe)

        else:

            command = cmd

    except Exception:

        command = cmd

    _start_job_thread(exec_id, command, cwd=cwd)

    return jsonify({'ok':True,'exec_id':exec_id})





@app.route('/api/ide/exec_status')

def api_ide_exec_status():

    exec_id = request.args.get('exec_id')

    if not exec_id:

        return jsonify({'ok':False,'error':'exec_id required'}),400

    job = EXEC_JOBS.get(exec_id)

    if not job:

        return jsonify({'ok':False,'error':'not found'}),404

    # attach small output preview

    out=''

    err=''

    base = Path(app.config['SCRIPTS_FOLDER']).resolve()

    stdout_path = base / f"{exec_id}.stdout"

    stderr_path = base / f"{exec_id}.stderr"

    try:

        if stdout_path.exists():

            out = stdout_path.read_text(encoding='utf-8', errors='ignore')

        if stderr_path.exists():

            err = stderr_path.read_text(encoding='utf-8', errors='ignore')

    except Exception:

        pass

    res = dict(job)

    res.update({'stdout': out, 'stderr': err})

    return jsonify({'ok':True,'job':res})





def _resource_id_for(category: str, filename: str) -> str:

        # stable id to reference resources in index

        return f"{category}:{filename}"



# Resources storage location and helpers

RESOURCES_DIR = Path(__file__).resolve().parent / 'data' / 'resources'

RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

RESOURCES_INDEX_FILE = RESOURCES_DIR / 'index.json'

INGEST_TASKS_FILE = RESOURCES_DIR / 'ingest_tasks.json'



# Sessions index (persisted minimal session metadata)

SESSIONS_INDEX_FILE = Path(__file__).resolve().parent / 'data' / 'sessions.json'

SESSIONS_META_FILE = Path(__file__).resolve().parent / 'data' / 'sessions_meta.json'



def _load_resources_index():

    try:

        if RESOURCES_INDEX_FILE.exists():

            try:

                return json.loads(RESOURCES_INDEX_FILE.read_text(encoding='utf-8'))

            except Exception:

                # corrupt index file -> rebuild empty

                return {}

        # build initial index by scanning data/resources categories

        idx = {}

        for cat_dir in RESOURCES_DIR.iterdir():

            if not cat_dir.is_dir():

                continue

            for p in cat_dir.iterdir():

                if p.is_file():

                    rid = _resource_id_for(cat_dir.name, p.name)

                    # Treat files as persona only when stored in a 'personality' category.

                    is_persona = (cat_dir.name.lower() == 'personality')

                    idx[rid] = {'id': rid, 'filename': p.name, 'category': cat_dir.name, 'path': str(p), 'persona': is_persona, 'uploaded_at': datetime.fromtimestamp(p.stat().st_mtime).isoformat()}

        # persist initial index

        _save_resources_index(idx)

        return idx

    except Exception:

        return {}



def _save_resources_index(idx: dict):

    try:

        RESOURCES_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

        RESOURCES_INDEX_FILE.write_text(json.dumps(idx, indent=2), encoding='utf-8')

    except Exception:

        app.logger.exception('Failed to save resources index')



def _load_ingest_tasks():

    try:

        if INGEST_TASKS_FILE.exists():

            try:

                return json.loads(INGEST_TASKS_FILE.read_text(encoding='utf-8'))

            except Exception:

                return {}

        return {}

    except Exception:

        return {}



def _save_ingest_tasks(tasks: dict):

    try:

        INGEST_TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)

        INGEST_TASKS_FILE.write_text(json.dumps(tasks, indent=2), encoding='utf-8')

    except Exception:

        app.logger.exception('Failed to save ingest tasks')





def _load_sessions_index():

    try:

        if SESSIONS_INDEX_FILE.exists():

            try:

                return json.loads(SESSIONS_INDEX_FILE.read_text(encoding='utf-8'))

            except Exception:

                return {}

        return {}

    except Exception:

        return {}





def _save_sessions_index(idx: dict):

    try:

        SESSIONS_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

        SESSIONS_INDEX_FILE.write_text(json.dumps(idx, indent=2), encoding='utf-8')

    except Exception:

        app.logger.exception('Failed to save sessions index')





def _upsert_session_meta(sid: str, title: str = None):

    """Ensure a minimal session metadata entry exists and return it.



    Creates or updates `data/sessions.json` with `session_id`, `title`,

    `created` and `last_updated` fields.

    """

    try:

        idx = _load_sessions_index()

        entry = idx.get(sid) or {}

        now_iso = datetime.now().isoformat()

        if not entry.get('session_id'):

            entry['session_id'] = sid

        if title:

            entry['title'] = title

        entry.setdefault('created', now_iso)

        entry['last_updated'] = now_iso

        # ensure favorite flag present

        entry.setdefault('favorite', False)

        idx[sid] = entry

        _save_sessions_index(idx)

        # also persist a richer meta file for backward-compatibility

        try:

            SESSIONS_META_FILE.parent.mkdir(parents=True, exist_ok=True)

            meta = {}

            if SESSIONS_META_FILE.exists():

                try:

                    meta = json.loads(SESSIONS_META_FILE.read_text(encoding='utf-8'))

                except Exception:

                    meta = {}

            meta[sid] = {'session_id': sid, 'updated': time.time(), 'topic_state': entry.get('topic_state')}

            SESSIONS_META_FILE.write_text(json.dumps(meta, indent=2), encoding='utf-8')

        except Exception:

            pass

        return entry

    except Exception:

        app.logger.exception('Upsert session meta failed')

        return {'session_id': sid, 'title': title or sid}



ECHO_RESOURCES_TEMPLATE = """{% extends "base.html" %}

{% block content %}

<h3>Resources: Reference / Templates / Examples</h3>

<div style="display:flex;gap:20px;align-items:flex-start;">

<div style="flex:1;max-width:420px;">

<form id="uploadForm" enctype="multipart/form-data" onsubmit="uploadResource(event)">

<label>File: <input type="file" name="file" required></label><br><br>

<label>Category:

<select name="category">

<option value="reference">Reference Dictionary</option>

<option value="template">Template Ingestion</option>

<option value="examples">Chat Examples</option>

</select></label><br><br>

<label><input type="checkbox" name="for_training"> Use for training</label><br>

<label><input type="checkbox" name="for_ingestion" checked> Use for ingestion</label><br>

<label><input type="checkbox" name="persona"> Upload as Personality (persona)</label><br><br>

<button class="btn btn-primary" type="submit">Upload</button>

</form>

<div id="uploadMsg" style="margin-top:10px;color:#6c6"></div>

</div>

<div style="flex:2;">

<h4>Existing Resources</h4>

</div>

<div style="flex:2;">

<h4>Existing Resources</h4>

<div style="margin-bottom:10px;">

Session id: <input id="sessionIdInput" placeholder="session id (optional)" style="width:220px;margin-right:8px;"> <button onclick="fetchPersonaStatus()">Check Persona</button>

<select id="resourceSelect" style="width:60%;margin-left:8px"></select>

<button onclick="enableSelectedPersona()">Enable persona for session</button>

<div id="personaStatus" style="margin-top:6px;color:#8f8"></div>

</div>

<div id="resourcesList">(loading...)</div>

</div>

</div>

<script>

        // Training page render helper

        function showTrainingPage(){

            const el = document.getElementById('trainingPage');

            if(!el) return;

        }

function uploadResource(e){

 e.preventDefault();

 const f = document.getElementById('uploadForm');

const fd = new FormData(f);



fetch('/api/resources/upload',{method:'POST',body:fd}).then(r=>r.json()).then(j=>{

     document.getElementById('uploadMsg').textContent = j.message || JSON.stringify(j);

     loadResources();

 }).catch(e=>{document.getElementById('uploadMsg').textContent='Upload failed';console.error(e)});

}

function loadResources(){

 fetch('/api/resources/list').then(r=>r.json()).then(j=>{

     const el=document.getElementById('resourcesList');

     el.innerHTML='';

     const idx=j || {};

     const sel = document.getElementById('resourceSelect'); sel.innerHTML='';

     Object.keys(idx).forEach(k=>{

         const r = idx[k];

         const div=document.createElement('div');

         div.style.border='1px solid #333';div.style.padding='8px';div.style.marginBottom='6px';

         let personaBadge = r.persona ? ' <span style="color:#ffb86b;font-weight:bold">[PERSONA]</span>' : '';

         div.innerHTML = '<b>'+r.filename+'</b> '+personaBadge+' <small>['+r.category+']</small><br>'+

             '<button class="btn btn-sm" onclick="loadIntoSession(\''+encodeURIComponent(k)+'\')">Load into session</button> '

             +'<button class="btn btn-sm btn-danger" onclick="deleteResource(\''+encodeURIComponent(k)+'\')">Delete</button>';

         // also add to select

         const opt = document.createElement('option'); opt.value = k; opt.text = r.filename + (r.persona ? ' [PERSONA]' : ''); sel.appendChild(opt);

         el.appendChild(div);

     });

 }).catch(e=>{document.getElementById('resourcesList').textContent='Failed to load resources';console.error(e)});

}

function fetchPersonaStatus(){

    const sid = document.getElementById('sessionIdInput').value || '';

    fetch('/api/personality/status?session_id='+encodeURIComponent(sid)).then(r=>r.json()).then(j=>{

        const p = j.personality;

        const out = document.getElementById('personaStatus');

        if(p && p.enabled){

            out.textContent = `Enabled: ${p.id}`;

        } else {

            out.textContent = 'No persona enabled for session';

        }

    }).catch(e=>{console.error(e)});

}



function enableSelectedPersona(){

    const sel = document.getElementById('resourceSelect');

    if(!sel.value){ alert('Select a resource first'); return; }

    const sid = document.getElementById('sessionIdInput').value || '';

    fetch('/api/resources/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id: decodeURIComponent(sel.value), session_id: sid || '', use_persona: true, for_ingestion: true})}).then(r=>r.json()).then(j=>{

        alert(j.message || JSON.stringify(j));

        fetchPersonaStatus();

    }).catch(e=>{console.error(e)});

}

function deleteResource(id){ if(!confirm('Delete resource?')) return; fetch('/api/resources/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:decodeURIComponent(id)})}).then(r=>r.json()).then(j=>{ loadResources(); }).catch(e=>console.error(e)); }

function loadIntoSession(id){ const sid = prompt('Load into which session id? (leave blank for current page session)'); fetch('/api/resources/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:decodeURIComponent(id), session_id: sid || ''})}).then(r=>r.json()).then(j=>{ alert(j.message||JSON.stringify(j)); }).catch(e=>console.error(e)); }

loadResources();

</script>

{% endblock %}"""



ECHO_TRAINING_TEMPLATE = """{% extends "base.html" %}

{% block content %}

<h2>Training Center</h2>

<div style="display:flex;gap:20px;align-items:flex-start;">

<div style="flex:1;max-width:420px;">

<form id="trainForm" onsubmit="startTrain(event)">

<label>Model path (relative to project): <input name="model" value="models/Phi-3-mini-4k-instruct-q4.gguf"></label>

<label>Training file (data/echo_training/...): <input name="training_file" value=""></label>

<label>Engine: <select name="engine"><option value="stub">stub</option><option value="peft">peft</option></select></label>

<label>Epochs: <input name="epochs" value="1"></label>

<label>Batch size: <input name="batch_size" value="8"></label>

<label>Learning rate: <input name="lr" value="0.0001"></label>

<button class="btn" type="submit">Start Training</button>

</form>

<div style="margin-top:12px;">Training jobs:</div>

<div id="trainingJobsList" style="margin-top:8px;"></div>

</div>

<div style="flex:2">

<h3>Logs</h3>

<div id="trainLogModal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal('trainLogModal')">&times;</span><pre id="trainLogContent">(logs)</pre></div></div>

<p>Use the form to start a training job. The <b>peft</b> engine requires additional dependencies and GPUs for practical runs.</p>

</div>

</div>

<script>loadTrainJobs();</script>

{% endblock %}

"""







class ScriptManager:

    def __init__(self,scripts_folder):

        self.scripts_folder=scripts_folder

    def list_scripts(self, include_repo_paths: bool = True, use_cache: bool = True):

        """Return scripts organized by category with a simple on-disk cache.



        Returns a list of category dicts: [{'category':'name','scripts':[...]}]

        """

        cache_file = Path(__file__).resolve().parent / 'data' / 'script_index.json'

        cache_age = None

        if cache_file.exists():

            try:

                cache_age = time.time() - cache_file.stat().st_mtime

                if use_cache and cache_age is not None and cache_age < 30:

                    with open(cache_file,'r',encoding='utf-8') as f:

                        return json.load(f)

            except Exception:

                # If reading the cache fails, ignore and do a fresh scan

                pass



        scripts=[]

        searched=set()

        # Primary scripts folder

        for ext in ['*.sh','*.ps1','*.py','*.bash']:

            for script_file in self.scripts_folder.glob(ext):

                if script_file.exists():

                    key=str(script_file.resolve())

                    if key in searched:

                        continue

                    searched.add(key)

                    scripts.append({'name':script_file.name,'path':str(script_file.resolve()),'size':script_file.stat().st_size,'modified':datetime.fromtimestamp(script_file.stat().st_mtime).isoformat(),'type':script_file.suffix[1:],'source':'scripts_folder'})



        if include_repo_paths:

            # Also scan repo root and parent directories for scripts (limited depth/glob)

            try:

                repo_root=Path(__file__).resolve().parents[0]

                search_dirs=[repo_root, repo_root.parent]

                for sd in search_dirs:

                    if not sd.exists():

                        continue

                    for ext in ['**/*.sh','**/*.ps1','**/*.py','**/*.bash']:

                        for script_file in sd.glob(ext):

                            if script_file.is_file():

                                key=str(script_file.resolve())

                                if key in searched:

                                    continue

                                searched.add(key)

                                scripts.append({'name':script_file.name,'path':str(script_file.resolve()),'size':script_file.stat().st_size,'modified':datetime.fromtimestamp(script_file.stat().st_mtime).isoformat(),'type':script_file.suffix[1:],'source':'repo'})

            except Exception:

                pass



        # Categorize scripts by heuristics (folder names, filename keywords)

        categories_map = {}

        def add_to_category(cat, item):

            if cat not in categories_map:

                categories_map[cat]=[]

            categories_map[cat].append(item)



        keywords = {

            'deploy':['deploy','deploy.sh','deploy.py','k8s','kubernetes','helm','ansible'],

            'backup':['backup','restore','snapshot'],

            'build':['build','compile','make','pack'],

            'test':['test','pytest','unittest','ci','integration'],

            'install':['install','setup','bootstrap','install.ps1'],

            'db':['db','migrate','schema','dump','restore'],

            'tools':['tool','script','util','utility'],

            'images':['image','docker','container'],

        }



        for s in scripts:

            p = Path(s['path'])

            name = p.name.lower()

            placed = False

            # heuristic: folder names

            parts = [part.lower() for part in p.parts]

            for cat, kws in keywords.items():

                if any(k in name for k in kws) or any(k in part for part in parts for k in kws):

                    add_to_category(cat, s)

                    placed = True

                    break

            if not placed:

                # fallback by top-level folder

                top = parts[0] if parts else ''

                add_to_category(top or 'other', s)



        # Build result list sorted by category name, with scripts sorted

        result = []

        for cat in sorted(categories_map.keys()):

            items = sorted(categories_map[cat], key=lambda x: x['name'])

            result.append({'category':cat,'scripts':items})



        # Cache index to disk for short period

        try:

            cache_file.parent.mkdir(parents=True,exist_ok=True)

            with open(cache_file,'w',encoding='utf-8') as f:

                json.dump(result,f)

        except Exception:

            pass



        return result

    def add_script(self,filename,content):

        # Allow subdirectories but prevent path traversal

        try:

            # normalize and join

            target = Path(self.scripts_folder) / Path(filename)

            resolved = target.resolve()

            base = Path(self.scripts_folder).resolve()

            if not str(resolved).startswith(str(base)):

                return False

            resolved.parent.mkdir(parents=True, exist_ok=True)

            with open(resolved, 'w', encoding='utf-8') as f:

                f.write(content)

            # make executable where appropriate

            try:

                os.chmod(resolved, 0o755)

            except Exception:

                pass

            return True

        except Exception:

            return False

    def delete_script(self,filename):

        try:

            target = Path(self.scripts_folder) / Path(filename)

            resolved = target.resolve()

            base = Path(self.scripts_folder).resolve()

            if not str(resolved).startswith(str(base)):

                return False

            if resolved.exists():

                resolved.unlink()

                # cleanup empty parents

                try:

                    p = resolved.parent

                    while p != base and not any(p.iterdir()):

                        p.rmdir()

                        p = p.parent

                except Exception:

                    pass

                return True

            return False

        except Exception:

            return False

    def execute_script(self,filename,args=''):

        script_path=self.scripts_folder/secure_filename(filename)

        if not script_path.exists():

            return {'success':False,'error':'Script not found'}

        try:

            # Choose an interpreter-aware command where possible

            cmd = _interpreter_cmd_for_path(script_path)

            if not cmd:

                # Fall back to attempting to execute directly; if this fails on Windows

                # the caller will receive a helpful error

                cmd = [str(script_path)]

            if args:

                cmd.extend(args.split())

            result=subprocess.run(cmd,capture_output=True,text=True,timeout=300)

            return {'success':result.returncode==0,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}

        except subprocess.TimeoutExpired:

            return {'success':False,'error':'Script execution timed out'}

        except Exception as e:

            return {'success':False,'error':str(e)}

    def get_script_content(self,filename):

        try:

            target = Path(self.scripts_folder) / Path(filename)

            resolved = target.resolve()

            base = Path(self.scripts_folder).resolve()

            if not str(resolved).startswith(str(base)):

                return None

            if resolved.exists():

                with open(resolved,'r', encoding='utf-8') as f:

                    return f.read()

            return None

        except Exception:

            return None

def get_system_stats():

    cpu_percent=psutil.cpu_percent(interval=1)

    memory=psutil.virtual_memory()

    try:

        disk_path='C:\\' if sys.platform=='win32' else '/'

        disk=psutil.disk_usage(disk_path)

    except:

        disk=psutil.disk_usage('.')

    return {'cpu':{'percent':cpu_percent,'count':psutil.cpu_count()},'memory':{'total':memory.total,'available':memory.available,'percent':memory.percent,'used':memory.used},'disk':{'total':disk.total,'used':disk.used,'free':disk.free,'percent':disk.percent},'uptime':time.time()-psutil.boot_time()}

def get_processes():

    processes=[]

    for proc in psutil.process_iter(['pid','name','cpu_percent','memory_percent','status']):

        try:

            processes.append(proc.info)

        except (psutil.NoSuchProcess,psutil.AccessDenied):

            pass

    return sorted(processes,key=lambda x:x.get('cpu_percent',0),reverse=True)[:50]

def get_windows_services():

    if sys.platform!='win32':

        return []

    services=[]

    try:

        result=subprocess.run(['sc','query'],capture_output=True,text=True)

        lines=result.stdout.split('\n')

        service={}

        for line in lines:

            line=line.strip()

            if line.startswith('SERVICE_NAME:'):

                if service:

                    services.append(service)

                service={'name':line.split(':',1)[1].strip()}

            elif line.startswith('DISPLAY_NAME:'):

                service['display_name']=line.split(':',1)[1].strip()

            elif line.startswith('STATE'):

                service['state']=line.split(':',1)[1].strip()

        if service:

            services.append(service)

    except Exception:

        pass

    return services

script_mgr=ScriptManager(app.config['SCRIPTS_FOLDER'])

# Execution jobs store for async/parallel execution

EXEC_JOBS = {}

# Training jobs store

TRAIN_JOBS = {}

TRAIN_JOBS_FILE = Path(__file__).parent / 'data' / 'models_output' / 'train_jobs.json'



def _load_train_jobs():

    try:

        if TRAIN_JOBS_FILE.exists():

            return json.loads(TRAIN_JOBS_FILE.read_text(encoding='utf-8'))

    except Exception:

        app.logger.exception('Failed to load train jobs file')

    return {}





def _start_cleanup_thread(retention_days=30):

    def runner():

        while True:

            try:

                base = Path(__file__).parent / 'data' / 'models_output'

                if base.exists():

                    for d in base.iterdir():

                        if not d.is_dir():

                            continue

                        # skip train_jobs.json

                        if d.name == 'train_jobs.json':

                            continue

                        mtime = d.stat().st_mtime

                        age_days = (time.time() - mtime) / (60*60*24)

                        if age_days > retention_days:

                            try:

                                shutil.make_archive(str(d), 'zip', root_dir=str(d))

                                shutil.rmtree(d)

                            except Exception:

                                app.logger.exception('Failed to archive old job %s', d)

                # sleep between scans

                time.sleep(60*60*6)

            except Exception:

                app.logger.exception('Cleanup thread error')

                time.sleep(60*60)

    thread = threading.Thread(target=runner, daemon=True)

    thread.start()



def _save_train_jobs():

    try:

        TRAIN_JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)

        TRAIN_JOBS_FILE.write_text(json.dumps(TRAIN_JOBS, indent=2), encoding='utf-8')

    except Exception:

        app.logger.exception('Failed to save train jobs file')



def _start_job_thread(exec_id, cmd, cwd=None):

    def runner():

        job = EXEC_JOBS.get(exec_id)

        if not job:

            return

        job['status'] = 'running'

        job['started_at'] = time.time()

        try:

            # run as subprocess and capture to files

            stdout_path = Path(app.config['SCRIPTS_FOLDER']) / f"{exec_id}.stdout"

            stderr_path = Path(app.config['SCRIPTS_FOLDER']) / f"{exec_id}.stderr"

            with open(stdout_path, 'wb') as out_f, open(stderr_path, 'wb') as err_f:

                proc = subprocess.Popen(cmd, cwd=cwd or str(app.config['SCRIPTS_FOLDER']), stdout=out_f, stderr=err_f, shell=isinstance(cmd, str))

                job['pid'] = proc.pid

                # Do not store the Popen object in the job dict (not JSON-serializable).

                proc.wait()

                job['returncode'] = proc.returncode

        except Exception as e:

            job['error'] = str(e)

            job['status'] = 'error'

        else:

            job['status'] = 'finished'

        finally:

            job['finished_at'] = time.time()



    t = threading.Thread(target=runner, daemon=True)

    t.start()





def _start_train_job(job_id, cmd, cwd=None):

    def runner():

        job = TRAIN_JOBS.get(job_id)

        if not job:

            return

        job['status'] = 'running'

        job['started_at'] = time.time()

        _save_train_jobs()

        try:

            outdir = Path(__file__).parent / 'data' / 'models_output' / job_id

            outdir.mkdir(parents=True, exist_ok=True)

            log_path = outdir / 'train.log'

            with open(log_path, 'wb') as log_f:

                proc = subprocess.Popen(cmd, cwd=cwd or str(Path.cwd()), stdout=log_f, stderr=log_f, shell=isinstance(cmd, str))

                job['pid'] = proc.pid

                proc.wait()

                job['returncode'] = proc.returncode

        except Exception as e:

            job['error'] = str(e)

            job['status'] = 'error'

        else:

            job['status'] = 'finished'

        finally:

            job['finished_at'] = time.time()

            _save_train_jobs()



    t = threading.Thread(target=runner, daemon=True)

    t.start()



HTML_TEMPLATE="""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width,initial-scale=1.0">

<title>MasterChief - DevOps Platform</title>

<style>

*{margin:0;padding:0;box-sizing:border-box;}

body{font-family:Arial,sans-serif;background:#1a1a1a;color:#e0e0e0;line-height:1.6;}

.container{max-width:1400px;margin:0 auto;padding:20px;}

header{background:#2d2d2d;padding:20px;margin-bottom:30px;border-bottom:3px solid #4CAF50;}

h1{color:#4CAF50;font-size:2.5em;margin-bottom:10px;}

.subtitle{color:#888;font-size:1.1em;}

nav{background:#252525;padding:15px;margin-bottom:30px;border-radius:8px;}

nav a{color:#4CAF50;text-decoration:none;margin-right:20px;padding:8px 15px;border-radius:5px;display:inline-block;transition:all 0.3s;}

nav a:hover,nav a.active{background:#4CAF50;color:#fff;}

.dashboard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-bottom:30px;}

.card{background:#2d2d2d;padding:25px;border-radius:10px;border-left:4px solid #4CAF50;box-shadow:0 4px 6px rgba(0,0,0,0.3);}

.card h3{color:#4CAF50;margin-bottom:15px;font-size:1.4em;}

.stat-value{font-size:2.5em;font-weight:bold;color:#fff;margin:10px 0;}

.stat-label{color:#888;font-size:0.9em;text-transform:uppercase;}

.progress-bar{background:#1a1a1a;height:20px;border-radius:10px;overflow:hidden;margin:10px 0;}

.progress-fill{background:linear-gradient(90deg,#4CAF50,#8BC34A);height:100%;transition:width 0.3s;}

table{width:100%;border-collapse:collapse;margin-top:15px;}

th,td{padding:12px;text-align:left;border-bottom:1px solid #3a3a3a;}

th{background:#252525;color:#4CAF50;font-weight:bold;}

tr:hover{background:#333;}

.btn{background:#4CAF50;color:#fff;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;text-decoration:none;display:inline-block;margin:5px;transition:all 0.3s;}

.btn:hover{background:#45a049;transform:translateY(-2px);}

.btn-danger{background:#f44336;}

.btn-danger:hover{background:#da190b;}

.btn-warning{background:#ff9800;}

.btn-warning:hover{background:#e68900;}

.btn-info{background:#2196F3;}

.btn-info:hover{background:#0b7dda;}

.form-group{margin-bottom:20px;}

label{display:block;margin-bottom:8px;color:#4CAF50;font-weight:bold;}

input,textarea,select{width:100%;padding:12px;background:#1a1a1a;border:1px solid #3a3a3a;color:#e0e0e0;border-radius:5px;font-size:1em;}

input:focus,textarea:focus,select:focus{outline:none;border-color:#4CAF50;}

.section{background:#2d2d2d;padding:25px;border-radius:10px;margin-bottom:25px;}

.status-badge{padding:5px 12px;border-radius:15px;font-size:0.85em;font-weight:bold;}

.status-running{background:#4CAF50;color:#fff;}

.status-stopped{background:#f44336;color:#fff;}

.alert{padding:15px;margin-bottom:20px;border-radius:5px;border-left:4px solid;}

.alert-success{background:#1b5e20;border-color:#4CAF50;color:#c8e6c9;}

.alert-error{background:#b71c1c;border-color:#f44336;color:#ffcdd2;}

.alert-info{background:#0d47a1;border-color:#2196F3;color:#bbdefb;}

.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;}

.modal-content{background:#2d2d2d;margin:50px auto;padding:30px;border-radius:10px;max-width:600px;position:relative;}

.close{position:absolute;top:15px;right:20px;font-size:30px;cursor:pointer;color:#888;}

.close:hover{color:#4CAF50;}

pre{background:#1a1a1a;padding:15px;border-radius:5px;overflow-x:auto;border-left:3px solid #4CAF50;}

code{color:#4CAF50;}

.file-upload{border:2px dashed #4CAF50;padding:40px;text-align:center;border-radius:10px;cursor:pointer;transition:all 0.3s;}

.file-upload:hover{background:#252525;border-color:#8BC34A;}

</style>

</head>

<body>

<div class="container">

<header>

<h1>⚡ MasterChief</h1>

<p class="subtitle">DevOps Automation Platform</p>

<div style="position:absolute;right:20px;top:24px;">

    <label style="color:#ccc;font-size:0.9em;">Language: <select id="langSelect" style="background:#1a1a1a;color:#eee;border:1px solid #333;padding:6px;border-radius:6px;"><option value="en">English</option><option value="es">Español</option></select></label>

    </div>

</header>

<nav>

<a href="/" class="{{ 'active' if request.path=='/' else '' }}">Dashboard</a>

<a href="/echo-chat" class="{{ 'active' if '/echo-chat' in request.path else '' }}">🌙 Echo Chat</a>

<a href="/scripts" class="{{ 'active' if '/scripts' in request.path else '' }}">Scripts</a>

<a href="/processes" class="{{ 'active' if '/processes' in request.path else '' }}">Processes</a>

<a href="/services" class="{{ 'active' if '/services' in request.path else '' }}">Services</a>

<a href="/addons" class="{{ 'active' if '/addons' in request.path else '' }}">Addons</a>

<a href="/echo-train" class="{{ 'active' if '/echo-train' in request.path else '' }}">Training</a>

</nav>

{% with messages=get_flashed_messages(with_categories=true) %}

{% if messages %}

{% for category,message in messages %}

<div class="alert alert-{{ category }}">{{ message }}</div>

{% endfor %}

{% endif %}

{% endwith %}

{% block content %}{% endblock %}

</div>

<script>

function confirmDelete(item){return confirm('Are you sure you want to delete '+item+'?');}

function openModal(modalId){document.getElementById(modalId).style.display='block';}

function closeModal(modalId){document.getElementById(modalId).style.display='none';}

function refreshStats(){fetch('/api/stats').then(r=>r.json()).then(data=>{

document.getElementById('cpu-value').textContent=data.cpu.percent.toFixed(1)+'%';

document.getElementById('cpu-progress').style.width=data.cpu.percent+'%';

document.getElementById('mem-value').textContent=data.memory.percent.toFixed(1)+'%';

document.getElementById('mem-progress').style.width=data.memory.percent+'%';

document.getElementById('disk-value').textContent=data.disk.percent.toFixed(1)+'%';

document.getElementById('disk-progress').style.width=data.disk.percent+'%';

}).catch(err=>console.error('Failed to refresh stats:',err));}

setInterval(refreshStats,5000);

function refreshIndex(){

        fetch('/scripts/refresh_index',{method:'POST'}).then(async r => {

        // Training UI helpers

        function loadTrainJobs() {

            fetch('/api/echo/train_list').then(r => r.json()).then(j => {

                const jobs = j.jobs || [];

                const el = document.getElementById('trainingJobsList');

                if (!el) return;

                el.innerHTML = '';

                jobs.forEach(job => {

                    const div = document.createElement('div');

                    div.style.border = '1px solid #444'; div.style.padding = '8px'; div.style.margin = '6px 0';

                    div.innerHTML = `<b>${job.id}</b> - ${job.status} - <button onclick="viewLog('${job.id}')">Log</button> <button onclick="cancelJob('${job.id}')">Cancel</button>`;

                    el.appendChild(div);

                });

            }).catch(console.error);

        }

        function startTrain(event) {

            event.preventDefault();

            const form = document.getElementById('trainForm');

            const fd = new FormData(form);

            const body = {};

            form.querySelectorAll('input,select').forEach(i => { if (i.name) body[i.name] = i.value });

            fetch('/api/echo/train_model', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).then(r => r.json()).then(j => {

                alert(JSON.stringify(j));

                loadTrainJobs();

            }).catch(e => { console.error(e); alert('Start failed') });

        }

        function viewLog(id) {

            fetch('/api/echo/train_status?job_id=' + encodeURIComponent(id)).then(r => r.json()).then(j => {

                const modal = document.getElementById('trainLogModal');

                document.getElementById('trainLogContent').textContent = j.log_tail || 'No log';

                modal.style.display = 'block';

            }).catch(console.error);

        }

        function cancelJob(id) {

            fetch('/api/echo/train_cancel', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_id: id }) }).then(r => r.json()).then(j => { alert(JSON.stringify(j)); loadTrainJobs(); }).catch(console.error);

        }

        setInterval(loadTrainJobs, 5000);

        if(r.status===401){

            // server requires admin token

            let token = prompt('Admin token required to refresh index:');

            if(!token) return alert('Cancelled');

            try{
                const r2 = await fetch('/scripts/refresh_index',{method:'POST',headers:{'X-ADMIN-TOKEN':token}});

                const j2 = await r2.json();


                

            # --- Manager Portal (external, module-level definitions) --------------------

                if(j2.ok) location.reload(); else alert('Refresh failed: '+(j2.error||'unknown'));

            }catch(e){ alert('Refresh error: '+e); }

        } else {

            const j = await r.json();

            if(j.ok){ location.reload(); } else { alert('Refresh failed: '+(j.error||'unknown')); }

        }

    }).catch(e=>{ alert('Refresh error: '+e); });

}

</script>

</body>

</html>"""

DASHBOARD_TEMPLATE="""{% extends "base.html" %}



{% block content %}

<div class="dashboard-grid">

<div class="card">

<h3>CPU Usage</h3>

<div class="stat-value" id="cpu-value">{{ stats.cpu.percent }}%</div>

<div class="progress-bar"><div class="progress-fill" id="cpu-progress" style="width:{{ stats.cpu.percent }}%"></div></div>

<div class="stat-label">{{ stats.cpu.count }} Cores</div>

</div>

<div class="card">

<h3>Memory Usage</h3>

<div class="stat-value" id="mem-value">{{ stats.memory.percent }}%</div>

<div class="progress-bar"><div class="progress-fill" id="mem-progress" style="width:{{ stats.memory.percent }}%"></div></div>

<div class="stat-label">{{ (stats.memory.used/1024/1024/1024)|round(2) }} GB / {{ (stats.memory.total/1024/1024/1024)|round(2) }} GB</div>

</div>

<div class="card">

<h3>Disk Usage</h3>

<div class="stat-value" id="disk-value">{{ stats.disk.percent }}%</div>

<div class="progress-bar"><div class="progress-fill" id="disk-progress" style="width:{{ stats.disk.percent }}%"></div></div>

<div class="stat-label">{{ (stats.disk.used/1024/1024/1024)|round(2) }} GB / {{ (stats.disk.total/1024/1024/1024)|round(2) }} GB</div>

</div>

<div class="card">

<h3>System Uptime</h3>

<div class="stat-value">{{ (stats.uptime/3600)|int }}h</div>

<div class="stat-label">{{ (stats.uptime/60)|int }} minutes</div>

</div>

</div>

<div class="section">

<h3>Quick Actions</h3>

<a href="/scripts" class="btn">Script Manager</a>

<a href="/processes" class="btn">Process Monitor</a>

<a href="/services" class="btn">Service Monitor</a>

<a href="/addons" class="btn">Install Addons</a>

<a href="/web_ide" class="btn">Web IDE</a>

</div>

{% endblock %}"""









SCRIPTS_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>Script Manager</h2>

<div style="display:flex;gap:8px;align-items:center;">

<button onclick="openModal('addScriptModal')" class="btn">Add New Script</button>

<button onclick="refreshIndex()" class="btn">Refresh Index</button>

</div>

<table>

<thead>

<tr>

<th>Name</th>

<th>Type</th>

<th>Size</th>

<th>Modified</th>

<th>Actions</th>

</tr>

</thead>

<tbody>

{% for script in scripts %}

<tr>

<td>{{ script.name }}</td>

<td>{{ script.type }}</td>

<td>{{ (script.size/1024)|round(2) }} KB</td>

<td>{{ script.modified[:16] }}</td>

<td>

{% if script.source=='repo' %}

<a href="/scripts/edit/{{ script.path | b64encode }}" class="btn btn-info">Edit</a>

<a href="/scripts/exec_path/{{ script.path | b64encode }}" class="btn">Execute</a>

{% else %}

<a href="/scripts/view/{{ script.name }}" class="btn btn-info">View</a>

<a href="/scripts/execute/{{ script.name }}" class="btn">Execute</a>

<a href="/scripts/delete/{{ script.name }}" class="btn btn-danger" onclick="return confirmDelete('{{ script.name }}');">Delete</a>

{% endif %}

</td>

</tr>

{% endfor %}

</tbody>

</table>

</div>

<div id="addScriptModal" class="modal">

<div class="modal-content">

<span class="close" onclick="closeModal('addScriptModal')">&times;</span>

<h2>Add New Script</h2>

<form method="POST" action="/scripts/add">

<div class="form-group">

<label>Script Name (include extension: .sh, .py, .ps1)</label>

<input type="text" name="filename" required placeholder="backup.sh">

</div>

<div class="form-group">

<label>Script Content</label>

<textarea name="content" rows="15" required placeholder="#!/bin/bash&#10;echo 'Hello World'"></textarea>

</div>

<button type="submit" class="btn">Add Script</button>

</form>

</div>

</div>

{% endblock %}"""

SCRIPT_VIEW_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>Script: {{ filename }}</h2>

<pre><code>{{ content }}</code></pre>

<a href="/scripts" class="btn btn-warning">Back to Scripts</a>

<a href="/scripts/execute/{{ filename }}" class="btn">Execute</a>

</div>

{% endblock %}"""

SCRIPT_EXECUTE_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>Execute Script: {{ filename }}</h2>

<form method="POST" action="/scripts/run/{{ filename }}">

<div class="form-group">

<label>Arguments (optional)</label>

<input type="text" name="args" placeholder="arg1 arg2 arg3">

</div>

<button type="submit" class="btn">Run Script</button>

<a href="/scripts" class="btn btn-warning">Cancel</a>

</form>

{% if result %}

<h3>Execution Result</h3>

<p><strong>Success:</strong> {{ result.success }}</p>

{% if result.returncode is defined %}

<p><strong>Return Code:</strong> {{ result.returncode }}</p>

{% endif %}

{% if result.stdout %}

<h4>Output:</h4>

<pre><code>{{ result.stdout }}</code></pre>

{% endif %}

{% if result.stderr %}

<h4>Errors:</h4>

<pre style="border-left-color:#f44336;"><code>{{ result.stderr }}</code></pre>

{% endif %}

{% if result.error %}

<div class="alert alert-error">{{ result.error }}</div>

{% endif %}

{% endif %}

</div>

{% endblock %}"""

SCRIPT_EDIT_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>Edit Script: {{ filepath }}</h2>

<div style="display:flex;gap:8px;margin-bottom:8px;">

    <button class="btn" onclick="doBackup();return false;">Create Backup</button>

    <button class="btn" onclick="doSuggest();return false;">Suggest Commit Message</button>

    <button class="btn btn-primary" onclick="doSmartSave();return false;">Smart Save</button>

    <a href="/scripts" class="btn btn-warning">Cancel</a>

</div>

<form method="POST" action="/scripts/save/{{ b64path }}" id="saveForm">

<div class="form-group">

<label>Content</label>

<textarea name="content" rows="25" style="width:100%;font-family:monospace;">{{ content }}</textarea>

</div>

<input type="hidden" name="commit_message" id="commit_message" value="">

</form>

<div id="suggestion" style="margin-top:12px;color:#bada55;font-family:monospace;"></div>

{% if message %}

<div class="alert">{{ message }}</div>

{% endif %}

</div>

<script>

async function doBackup(){

    const b64='{{ b64path }}';

    const r=await fetch('/scripts/backup/'+b64,{method:'POST'});

    const j=await r.json();

    alert(j.success?('Backup created: '+j.backup):('Backup failed: '+(j.error||'unknown')));

}

async function doSuggest(){

    const b64='{{ b64path }}';

    const r=await fetch('/scripts/suggest_commit/'+b64);

    const j=await r.json();

    if(j.success){

        document.getElementById('suggestion').innerText = j.suggestion;

        document.getElementById('commit_message').value = j.suggestion;

    } else {

        alert('Suggestion failed: '+(j.error||'unknown'));

    }

}

async function doSmartSave(){

    // show diff preview first, then on confirm do backup->suggest->save

    const b64='{{ b64path }}';

    const content = document.querySelector('textarea[name="content"]').value;

    const r = await fetch('/scripts/diff/'+b64, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({content})});

    const j = await r.json();

    if(!j.success){

        alert('Diff failed: '+(j.error||'unknown'));

        return;

    }

    document.getElementById('diffContent').innerText = j.diff || '(no changes)';

    document.getElementById('diffModal').style.display='block';

}

function closeDiff(){ document.getElementById('diffModal').style.display='none'; }

async function confirmSave(){

    // backup, suggest, then submit

    await doBackup();

    await doSuggest();

    document.getElementById('saveForm').submit();

}

</script>

<style>

#diffModal{position:fixed;left:10%;top:8%;width:80%;height:80%;background:#111;padding:12px;border:2px solid #666;overflow:auto;color:#ddd;z-index:9999}

#diffModal pre{white-space:pre-wrap;font-family:monospace;font-size:12px}

#diffModal .actions{margin-top:12px}

</style>

<div id="diffModal" style="display:none">

    <h3>Pre-save Diff Preview</h3>

    <pre id="diffContent">(loading...)</pre>

    <div class="actions">

        <button class="btn" onclick="closeDiff();">Cancel</button>

        <button class="btn btn-primary" onclick="confirmSave();">Confirm Save</button>

    </div>

</div>

{% endblock %}

"""

PROCESSES_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>Process Monitor</h2>

<p>Top 50 processes by CPU usage</p>

<table>

<thead>

<tr>

<th>PID</th>

<th>Name</th>

<th>CPU %</th>

<th>Memory %</th>

<th>Status</th>

<th>Actions</th>

</tr>

</thead>

<tbody>

{% for proc in processes %}

<tr>

<td>{{ proc.pid }}</td>

<td>{{ proc.name }}</td>

<td>{{ proc.cpu_percent }}%</td>

<td>{{ proc.memory_percent|round(2) }}%</td>

<td>{{ proc.status }}</td>

<td>

<a href="/processes/kill/{{ proc.pid }}" class="btn btn-danger btn-sm" onclick="return confirmDelete('PID {{ proc.pid }}');">Kill</a>

</td>

</tr>

{% endfor %}

</tbody>

</table>

</div>

{% endblock %}"""

SERVICES_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>Windows Services Monitor</h2>

{% if not is_windows %}

<div class="alert alert-info">Windows services monitoring is only available on Windows platforms.</div>

{% else %}

<table>

<thead>

<tr>

<th>Service Name</th>

<th>Display Name</th>

<th>State</th>

<th>Actions</th>

</tr>

</thead>

<tbody>

{% for service in services %}

<tr>

<td>{{ service.name }}</td>

<td>{{ service.display_name }}</td>

<td>{{ service.state }}</td>

<td>

<a href="/services/start/{{ service.name }}" class="btn">Start</a>

<a href="/services/stop/{{ service.name }}" class="btn btn-warning">Stop</a>

<a href="/services/restart/{{ service.name }}" class="btn btn-info">Restart</a>

</td>

</tr>

{% endfor %}

</tbody>

</table>

{% endif %}

</div>

{% endblock %}"""

ADDONS_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>Addon Installer</h2>

<div class="file-upload" onclick="document.getElementById('fileInput').click();">

<h3>📦 Upload Addon Package</h3>

<p>Click to select a .zip file</p>

<form method="POST" action="/addons/upload" enctype="multipart/form-data" id="uploadForm">

<input type="file" id="fileInput" name="file" accept=".zip" style="display:none;" onchange="document.getElementById('uploadForm').submit();">

</form>

</div>

{% if uploaded_files %}

<h3>Uploaded Addons</h3>

<table>

<thead>

<tr>

<th>Filename</th>

<th>Size</th>

<th>Uploaded</th>

<th>Actions</th>

</tr>

</thead>

<tbody>

{% for file in uploaded_files %}

<tr>

<td>{{ file.name }}</td>

<td>{{ (file.size/1024)|round(2) }} KB</td>

<td>{{ file.modified }}</td>

<td>

<a href="/addons/install/{{ file.name }}" class="btn">Install</a>

<a href="/addons/delete/{{ file.name }}" class="btn btn-danger" onclick="return confirmDelete('{{ file.name }}');">Delete</a>

</td>

</tr>

{% endfor %}

</tbody>

</table>

{% endif %}

</div>

{% endblock %}"""

ECHO_CHAT_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<style>

.echo-container{display:grid;grid-template-columns:1fr 2fr;gap:20px;height:calc(100vh - 250px);}

.echo-sidebar{background:#2d2d2d;padding:20px;border-radius:10px;border-left:4px solid #9370DB;overflow-y:auto;}

.echo-main{display:flex;flex-direction:column;background:#2d2d2d;border-radius:10px;border-left:4px solid #9370DB;}

.echo-art{color:#9370DB;font-family:monospace;font-size:10px;white-space:pre;line-height:1.2;margin-bottom:20px;}

.echo-stats{margin-top:20px;}

.echo-stats h4{color:#9370DB;margin-bottom:10px;}

.echo-stats .stat-item{display:flex;justify-content:space-between;padding:8px;background:#1a1a1a;margin-bottom:5px;border-radius:5px;}

.chat-header{background:#9370DB;color:#fff;padding:15px 20px;border-radius:10px 10px 0 0;font-size:1.2em;font-weight:bold;}

.chat-messages{flex:1;overflow-y:auto;padding:20px;background:#1a1a1a;display:flex;flex-direction:column;gap:15px;}

.chat-message{display:flex;gap:10px;animation:fadeIn 0.3s;}

@keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}

.chat-message.user{flex-direction:row-reverse;}

.chat-bubble{max-width:70%;padding:12px 16px;border-radius:15px;position:relative;}

.chat-message.echo .chat-bubble{background:#4a148c;color:#fff;border-bottom-left-radius:5px;}

.chat-message.user .chat-bubble{background:#1976D2;color:#fff;border-bottom-right-radius:5px;}

.chat-icon{font-size:24px;flex-shrink:0;}

.chat-timestamp{font-size:0.75em;color:#888;margin-top:5px;}

.training-buttons{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;}

.training-btn{font-size:0.85em;padding:4px 12px;border-radius:12px;border:none;cursor:pointer;transition:all 0.2s;}

.training-btn.excellent{background:#4CAF50;color:#fff;}

.training-btn.good{background:#8BC34A;color:#fff;}

.training-btn.fair{background:#FFC107;color:#000;}

.training-btn.poor{background:#f44336;color:#fff;}

.training-btn:hover{transform:scale(1.05);box-shadow:0 2px 8px rgba(0,0,0,0.3);}

.training-btn.selected{box-shadow:0 0 10px currentColor;border:2px solid #fff;}

.chat-input-area{padding:20px;background:#2d2d2d;border-radius:0 0 10px 10px;border-top:2px solid #9370DB;}

.chat-input-form{display:flex;gap:10px;}

.chat-input{flex:1;padding:12px;background:#1a1a1a;border:2px solid #9370DB;color:#e0e0e0;border-radius:25px;font-size:1em;}

.chat-input:focus{outline:none;border-color:#BA55D3;}

.send-btn{background:linear-gradient(135deg,#9370DB,#BA55D3);color:#fff;border:none;padding:12px 30px;border-radius:25px;cursor:pointer;font-weight:bold;transition:all 0.3s;}

.send-btn:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(147,112,219,0.4);}

.typing-indicator{display:none;padding:10px;color:#9370DB;}

.typing-indicator.active{display:block;}

@media(max-width:768px){.echo-container{grid-template-columns:1fr;}.echo-sidebar{max-height:300px;}}

</style>

<div class="echo-container">

<div class="echo-sidebar">

<div class="echo-art">{{ echo_art }}</div>

<div class="echo-stats">

<h4>✨ Training Stats</h4>

<div class="stat-item"><span>Patterns Learned:</span><span id="patterns-count">0</span></div>

<div class="stat-item"><span>Total Examples:</span><span id="total-examples">0</span></div>

<div class="stat-item"><span>Session Messages:</span><span id="session-messages">0</span></div>

<div class="stat-item"><span>Current Model:</span><span id="current-model">(checking...)</span></div>

<div style="margin-top:8px;">

<select id="modelSelect" style="width:100%;padding:6px;border-radius:6px;background:#111;color:#eee;border:1px solid #333;"></select>

<div style="display:flex;gap:6px;margin-top:6px;">

<button class="btn btn-sm btn-primary" onclick="selectModel()">Load Model</button>

<button class="btn btn-sm btn-secondary" onclick="fetchModels()">Refresh</button>

<button class="btn btn-sm" onclick="document.getElementById('personaFile').click()">Upload Persona</button>

<button class="btn btn-sm" onclick="document.getElementById('trainingFile').click()">Upload Training</button>

<input id="personaFile" type="file" accept=".txt,.md,.jsonl" style="display:none" onchange="uploadPersona(this.files[0])">

<input id="trainingFile" type="file" accept=".jsonl,.json,.txt" style="display:none" onchange="uploadTraining(this.files[0])">

</div>

</div>

</div>

<div style="margin-top:15px;">

<h4>💬 Chat History</h4>

<div id="session-list" style="max-height:220px;overflow:auto;margin-top:8px;"></div>

<div style="display:flex;gap:8px;margin-top:8px;">

<button onclick="createSession()" class="btn btn-sm btn-success">New Session</button>

<button onclick="fetchSessions()" class="btn btn-sm btn-secondary">Refresh</button>

</div>

</div>

<div style="margin-top:15px;">

<h4>⚙️ Fine-tune Model</h4>

<div style="display:flex;gap:8px;flex-direction:column;">

<div style="display:flex;gap:8px;">

<select id="trainingFileSelect" style="flex:1"></select>

<button class="btn btn-sm" onclick="fetchTrainingFiles()">Refresh</button>

</div>

<div style="display:flex;gap:8px;">

<input id="tf_epochs" type="number" value="1" style="width:100px" />

<input id="tf_batch" type="number" value="8" style="width:100px" />

<input id="tf_lr" type="text" value="1e-4" style="width:140px" />

<input id="tf_output" type="text" placeholder="output name (optional)" />

<button class="btn btn-sm btn-warning" onclick="startTraining()">Start Training</button>

</div>

<div id="trainingJobs" style="margin-top:8px;max-height:160px;overflow:auto;background:#111;padding:8px;border-radius:6px;font-size:0.9em;color:#ddd"></div>

</div>

</div>

<div style="margin-top:15px;">

<h4>📚 Resources</h4>

<div id="resources-sidebar" style="max-height:220px;overflow:auto;margin-top:8px;">

    <div style="margin-bottom:6px;">Category: <select id="resourceCategory" style="width:160px;margin-left:6px;" onchange="populateResourceList()"><option value="all">All</option><option value="reference">Reference</option><option value="template">Template</option><option value="examples">Examples</option></select></div>

    <div id="resource-list" style="margin-top:6px;"></div>

    <div style="display:flex;gap:8px;margin-top:8px;"><button onclick="fetchResourcesForSidebar()" class="btn btn-sm btn-secondary">Refresh</button></div>

    <div style="margin-top:12px;">

        <h4>Saved Outputs</h4>

        <div id="savedOutputs" style="max-height:160px;overflow:auto;margin-top:6px;color:#ddd"></div>

        <div style="display:flex;gap:8px;margin-top:6px;"><button class="btn btn-sm" onclick="fetchSavedOutputs()">Refresh</button></div>

    </div>

</div>

</div>

<button onclick="clearChat()" class="btn btn-warning" style="width:100%;margin-top:15px;">Clear Chat</button>

<button onclick="searchMemory()" class="btn btn-info" style="width:100%;margin-top:10px;">Search Memory</button>

</div>

<div class="echo-main">

<div class="chat-header">🌙 Echo Starlite - Chat <button class="btn btn-sm" style="margin-left:8px;" onclick="openImagePrompt()">Generate Image</button></div>

<div class="chat-messages" id="chatMessages">

<div class="chat-message echo">

<div class="chat-icon">🌙</div>

<div>

<div class="chat-bubble">Hello... I am Echo 🌙<br>I'm here to help with DevOps tasks and learn from our conversations... 💜</div>

</div>

</div>

</div>

<div class="typing-indicator" id="typingIndicator">Echo is typing...</div>

<div class="chat-input-area">

<form class="chat-input-form" onsubmit="sendMessage(event)">

<input type="text" id="chatInput" class="chat-input" placeholder="Type your message... ✨" autocomplete="off" required>

<div style="display:flex;gap:8px;align-items:center;margin-left:8px;">

    <label style="font-size:0.85em;color:#ccc;display:flex;align-items:center;gap:6px;"><input type="checkbox" id="autoContinueToggle"> <span id="autoContinueLabel">Auto-continue</span></label>

    <label style="font-size:0.85em;color:#ccc;display:flex;align-items:center;gap:6px;"><input type="checkbox" id="saveToFileToggle"> <span id="saveToFileLabel">Save to file</span></label>

    <label style="font-size:0.85em;color:#ccc;display:flex;align-items:center;gap:6px;">

        Size:

        <select id="imageSizeSelect" style="margin-left:6px;">

            <option value="512x512">512×512</option>

            <option value="640x640">640×640</option>

            <option value="768x512">768×512</option>

        </select>

    </label>

    <label style="font-size:0.85em;color:#ccc;display:flex;align-items:center;gap:6px;">

        Style:

        <select id="imageStyleSelect" style="margin-left:6px;">

            <option value="photorealistic">Photorealistic</option>

            <option value="illustration">Illustration</option>

            <option value="digital-art">Digital Art</option>

        </select>

    </label>

    <button type="submit" class="send-btn">Send 💜</button>

    </div>

</form>

</div>

</div>

</div>

<script>

let sessionId='web_'+Date.now();

let messageCount=0;

// Simple client-side translations (expandable)

const TRANSLATIONS = {

    en: {

        auto_continue: 'Auto-continue',

        save_to_file: 'Save to file',

        saved_outputs: 'Saved Outputs',

        download: 'Download',

        delete: 'Delete',

        no_saved: 'No saved outputs',

        saved_prefix: 'Saved:'

    },

    es: {

        auto_continue: 'Auto-continuar',

        save_to_file: 'Guardar en archivo',

        saved_outputs: 'Salidas guardadas',

        download: 'Descargar',

        delete: 'Borrar',

        no_saved: 'No hay salidas guardadas',

        saved_prefix: 'Guardado:'

    }

};

let CURRENT_LANG = 'en';

function sendMessage(e){

e.preventDefault();

const input=document.getElementById('chatInput');

const message=input.value.trim();

if(!message)return;

addUserMessage(message);

input.value='';

showTyping();

// read toggles (per-session overrides)

const autoContinue = document.getElementById('autoContinueToggle') ? document.getElementById('autoContinueToggle').checked : false;

const saveToFile = document.getElementById('saveToFileToggle') ? document.getElementById('saveToFileToggle').checked : false;

fetch('/api/echo/chat',{

method:'POST',

headers:{'Content-Type':'application/json'},

body:JSON.stringify({message:message,session_id:sessionId,auto_continue:autoContinue,save_to_file:saveToFile})

}).then(r=>r.json()).then(data=>{

hideTyping();

addEchoMessage(data.response,data.message_id);

updateStats();

messageCount++;

document.getElementById('session-messages').textContent=messageCount;

// if server returned saved path, show small link

if(data && data.saved_to){

    try{ const el = document.createElement('div'); el.style.fontSize='0.85em'; el.style.marginTop='6px'; const t = TRANSLATIONS[CURRENT_LANG] || TRANSLATIONS['en']; el.innerHTML = t.saved_prefix + ' <a href="/'+data.saved_to+'" target="_blank">'+data.saved_to.split('/').slice(-1)[0]+'</a>'; document.getElementById('chatMessages').appendChild(el);}catch(e){}

    try{ if(typeof fetchSavedOutputs==='function') fetchSavedOutputs(); }catch(e){}

}

}).catch(err=>{

hideTyping();

console.error('Error:',err);

addEchoMessage('Sorry... something went wrong... 💜',null);

});

}

// Image generation UI helper

function openImagePrompt(){

    const p = prompt('Enter image prompt (what do you want to generate)?');

    if(!p) return;

    generateImage(p);

}

function generateImage(promptText){
    // non-blocking enqueue + polling flow
    const size = document.getElementById('imageSizeSelect') ? document.getElementById('imageSizeSelect').value : '512x512';
    const style = document.getElementById('imageStyleSelect') ? document.getElementById('imageStyleSelect').value : 'photorealistic';

    showTyping();
    fetch('/api/echo/generate_image_async',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({prompt:promptText, session_id:sessionId, size:size, style:style})
    }).then(r=>r.json()).then(j=>{
        hideTyping();
        if(!j.ok || !j.job_id){
            addEchoMessage('Image enqueue failed: '+(j.error||'unknown'), null);
            return;
        }

        const jobId = j.job_id;
        const container = document.getElementById('chatMessages');
        const jobDiv = document.createElement('div');
        jobDiv.className = 'chat-message echo image-job';
        jobDiv.id = 'image-job-'+jobId;
        jobDiv.innerHTML = '<div class="chat-icon">🖼️</div><div><div class="chat-bubble">'
            +'<div><strong>Generating image…</strong></div>'
            +'<div class="image-progress" style="margin-top:6px;"><div class="image-progress-bar" style="height:10px;background:#eee;border-radius:6px;overflow:hidden;"><div class="image-progress-inner" style="width:0%;height:100%;background:#6b46c1;"></div></div><div class="image-progress-text" style="font-size:12px;margin-top:4px;">Queued</div></div>'
            +'<div class="image-prompt" style="margin-top:8px;color:#444;">'+escapeHtml(promptText)+'</div>'
            +'</div></div>';
        container.appendChild(jobDiv);
        container.scrollTop = container.scrollHeight;

        // poll status
        const poll = setInterval(()=>{
            fetch('/api/echo/image_status?job_id='+encodeURIComponent(jobId)).then(r=>r.json()).then(s=>{
                if(s.error){
                    const txt = jobDiv.querySelector('.image-progress-text');
                    if(txt) txt.textContent = 'Error: '+s.error;
                    clearInterval(poll);
                    return;
                }
                const pct = s.progress || 0;
                const inner = jobDiv.querySelector('.image-progress-inner');
                const txt = jobDiv.querySelector('.image-progress-text');
                if(inner) inner.style.width = Math.min(100, pct)+'%';
                if(txt) txt.textContent = (s.status || 'working') + (pct ? (' — '+pct+'%') : '');
                if(s.status === 'done' || s.status === 'error'){
                    clearInterval(poll);
                    if(s.status === 'done' && s.url){
                        // replace job div with final image message
                        const imgHtml = '<div class="chat-icon">🖼️</div><div><div class="chat-bubble"><img src="'+s.url+'" style="max-width:480px;display:block;margin-bottom:6px;">'+escapeHtml(promptText)+'</div></div>';
                        jobDiv.outerHTML = '<div class="chat-message echo">'+imgHtml+'</div>';
                        try{ fetchSavedOutputs(); }catch(e){}
                    }
                }
            }).catch(err=>{
                console.error('status poll error',err);
                clearInterval(poll);
            });
        }, 2000);

    }).catch(e=>{ hideTyping(); addEchoMessage('Image enqueue failed', null); console.error(e); });

}

function addUserMessage(text){

const container=document.getElementById('chatMessages');

const msgDiv=document.createElement('div');

msgDiv.className='chat-message user';

msgDiv.innerHTML='<div class="chat-icon">👤</div><div><div class="chat-bubble">'+escapeHtml(text)+'</div></div>';

container.appendChild(msgDiv);

container.scrollTop=container.scrollHeight;

messageCount++;

}

function addEchoMessage(text,messageId){

const container=document.getElementById('chatMessages');

const msgDiv=document.createElement('div');

msgDiv.className='chat-message echo';

msgDiv.dataset.messageId=messageId;

let html='<div class="chat-icon">🌙</div><div><div class="chat-bubble">'+escapeHtml(text)+'<div class="training-buttons">';

html+='<button class="training-btn excellent" onclick="rateResponse(this,&quot;excellent&quot;)">👍 Excellent</button>';

html+='<button class="training-btn good" onclick="rateResponse(this,&quot;good&quot;)">✨ Good</button>';

html+='<button class="training-btn fair" onclick="rateResponse(this,&quot;acceptable&quot;)">👌 Fair</button>';

html+='<button class="training-btn poor" onclick="rateResponse(this,&quot;poor&quot;)">👎 Poor</button>';

html+='</div></div></div>';

msgDiv.innerHTML=html;

container.appendChild(msgDiv);

container.scrollTop=container.scrollHeight;

}

function rateResponse(btn,quality){

const msgDiv=btn.closest('.chat-message');

const messageId=msgDiv.dataset.messageId;

const buttons=msgDiv.querySelectorAll('.training-btn');

buttons.forEach(b=>b.classList.remove('selected'));

btn.classList.add('selected');

const chatBubble=msgDiv.querySelector('.chat-bubble');

const responseText=chatBubble.childNodes[0].textContent;

const prevUserMsg=msgDiv.previousElementSibling;

const userText=prevUserMsg?prevUserMsg.querySelector('.chat-bubble').textContent:'';

fetch('/api/echo/train',{

method:'POST',

headers:{'Content-Type':'application/json'},

body:JSON.stringify({

user_message:userText,

bot_response:responseText,

quality:quality,

message_id:messageId

})

}).then(r=>r.json()).then(data=>{

if(data.success){

updateStats();

console.log('Training feedback submitted');

}

}).catch(err=>console.error('Training error:',err));

}

function updateStats(){

fetch('/api/echo/stats').then(r=>r.json()).then(data=>{

document.getElementById('patterns-count').textContent=data.patterns_learned||0;

document.getElementById('total-examples').textContent=data.total_examples||0;

}).catch(err=>console.error('Stats error:',err));

}

function fetchModel(){

    const url = '/api/echo/model?ts='+Date.now();

    console.debug('fetchModel ->', url);

    fetch(url, {cache: 'no-store'}).then(r=>r.json()).then(j=>{

        const el=document.getElementById('current-model');

        if(!el) return;

        if(j && j.model){

            try{

                const idx1 = j.model.lastIndexOf('/');

                const idx2 = j.model.lastIndexOf(String.fromCharCode(92));

                const idx = Math.max(idx1, idx2);

                el.textContent = idx >= 0 ? j.model.substring(idx+1) : j.model;

            }catch(e){ el.textContent = j.model; }

        } else {

            el.textContent='(none)';

        }

    }).catch(e=>{ console.error('Failed to fetch model',e); });

}

function fetchSessions(){

    fetch('/api/echo/sessions').then(r=>r.json()).then(j=>{

        const list=document.getElementById('session-list');

        if(!list) return;

        list.innerHTML='';

        (j.sessions||[]).forEach(s=>{

            const div=document.createElement('div');

            div.style.display='flex';

            div.style.alignItems='center';

            div.style.justifyContent='space-between';

            div.style.padding='6px';

            div.style.borderBottom='1px solid #333';

            const title=document.createElement('div');

            title.style.flex='1';

            title.style.cursor='pointer';

            title.textContent = s.title || s.session_id;

            title.onclick = ()=>{ loadSession(s.session_id); };

            const actions=document.createElement('div');

            actions.style.display='flex';

            actions.style.gap='6px';

            const fav=document.createElement('button');

            fav.className='btn btn-sm';

            fav.textContent = s.favorite? '★' : '☆';

            fav.onclick = (e)=>{ e.stopPropagation(); toggleFavorite(s.session_id); };

            const del=document.createElement('button');

            del.className='btn btn-sm btn-danger';

            del.textContent='Delete';

            del.onclick = (e)=>{ e.stopPropagation(); if(confirm('Delete session '+s.session_id+'?')) deleteSession(s.session_id); };

            actions.appendChild(fav);

            actions.appendChild(del);

            div.appendChild(title);

            div.appendChild(actions);

            list.appendChild(div);

        });

    }).catch(e=>console.error('Failed to fetch sessions',e));

}



// Resources in sidebar

function fetchResourcesForSidebar(){

    fetch('/api/resources/list').then(r=>r.json()).then(idx=>{

        window._resource_index = idx || {};

        populateResourceList();

    }).catch(e=>{ console.error('Failed to fetch resources',e); document.getElementById('resource-list').textContent='Failed to load'; });

}



function populateResourceList(){

    const sel = document.getElementById('resourceCategory');

    const cat = sel?sel.value:'all';

    const list = document.getElementById('resource-list');

    list.innerHTML='';

    const idx = window._resource_index || {};

    Object.keys(idx).forEach(k=>{

        const r = idx[k];

        if(cat!=='all' && r.category!==cat) return;

        const row = document.createElement('div');

        row.style.display='flex'; row.style.justifyContent='space-between'; row.style.padding='6px'; row.style.borderBottom='1px solid #333';

        const left = document.createElement('div'); left.style.flex='1'; left.textContent = r.filename + ' ['+r.category+']';

        const preview = document.createElement('div'); preview.style.color='#999'; preview.style.fontSize='0.9em'; preview.style.marginTop='6px';

        const right = document.createElement('div'); right.style.display='flex'; right.style.gap='6px';

        const loadBtn = document.createElement('button'); loadBtn.className='btn btn-sm'; loadBtn.textContent='Load';

        loadBtn.onclick = ()=>{ fetch('/api/resources/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:k, session_id:sessionId})}).then(r=>r.json()).then(j=>{ alert(j.message||JSON.stringify(j)); }).catch(e=>console.error(e)); };

        right.appendChild(loadBtn);

        row.appendChild(left); row.appendChild(right);

        // fetch inline preview for text resources

        fetch('/resources/preview?id='+encodeURIComponent(k)).then(rp=>{

            if(!rp.ok) return;

            return rp.text();

        }).then(txt=>{ if(txt){ preview.innerHTML = txt; left.appendChild(preview); } }).catch(()=>{});

        list.appendChild(row);

    });

}



// fetch initial resources for sidebar

function loadSessionPrefs(){

    fetch('/api/echo/session_prefs?session_id='+encodeURIComponent(sessionId)).then(r=>r.json()).then(j=>{

        const prefs = j.prefs || {};

        const ac = document.getElementById('autoContinueToggle');

        const st = document.getElementById('saveToFileToggle');

        if(ac && typeof prefs.auto_continue !== 'undefined') ac.checked = !!prefs.auto_continue;

        if(st && typeof prefs.save_to_file !== 'undefined') st.checked = !!prefs.save_to_file;

        // language

        const ls = document.getElementById('langSelect');

        if(ls){ CURRENT_LANG = prefs.lang || 'en'; ls.value = CURRENT_LANG; ls.addEventListener('change', ()=>{ CURRENT_LANG = ls.value; saveSessionPrefs(); applyTranslations(); }); }

        applyTranslations();

        // attach change listeners to persist

        if(ac) ac.addEventListener('change', ()=> saveSessionPrefs());

        if(st) st.addEventListener('change', ()=> saveSessionPrefs());

    }).catch(e=>{console.error('Failed to load session prefs',e);});

}



function applyTranslations(){

    const t = TRANSLATIONS[CURRENT_LANG] || TRANSLATIONS['en'];

    const acLabel = document.querySelector('label[for="autoContinueToggle"]');

    // our labels are inline, locate by input id parent

    const acWrap = document.getElementById('autoContinueToggle');

    if(acWrap && acWrap.parentElement) {

        acWrap.parentElement.childNodes.forEach(n=>{});

        // set text node after checkbox

        acWrap.parentElement.childNodes[1] && (acWrap.parentElement.childNodes[1].textContent = ' ' + t.auto_continue);

    }

    const stWrap = document.getElementById('saveToFileToggle');

    if(stWrap && stWrap.parentElement){ stWrap.parentElement.childNodes[1] && (stWrap.parentElement.childNodes[1].textContent = ' ' + t.save_to_file); }

    // Saved outputs header

    const so = document.querySelector('#savedOutputs') ? document.querySelector('#savedOutputs').previousElementSibling : null;

    if(so && so.tagName === 'H4') so.textContent = t.saved_outputs;

}



function saveSessionPrefs(){

    try{

        const ac = document.getElementById('autoContinueToggle') ? document.getElementById('autoContinueToggle').checked : null;

        const st = document.getElementById('saveToFileToggle') ? document.getElementById('saveToFileToggle').checked : null;

        fetch('/api/echo/session_prefs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId,prefs:{auto_continue:ac,save_to_file:st}})}).then(()=>{}).catch(e=>console.error('Failed to save prefs',e));

    }catch(e){console.error(e)}

}



function fetchSavedOutputs(){

    fetch('/api/echo/outputs').then(r=>r.json()).then(j=>{

        const files = j.files || [];

        const el = document.getElementById('savedOutputs');

        if(!el) return;

        el.innerHTML = '';

        const t = TRANSLATIONS[CURRENT_LANG] || TRANSLATIONS['en'];

        if(files.length === 0){ el.innerHTML = '<div style="color:#999">'+t.no_saved+'</div>'; return; }

        files.forEach(f=>{

            const row = document.createElement('div');

            row.style.display='flex'; row.style.justifyContent='space-between'; row.style.padding='6px'; row.style.borderBottom='1px solid #333';

            const left = document.createElement('div'); left.textContent = f.name;

            const right = document.createElement('div'); right.style.display='flex'; right.style.gap='6px';

            const a = document.createElement('a'); a.href = '/' + f.path; a.target = '_blank'; a.textContent = t.download;

            const del = document.createElement('button'); del.className='btn btn-sm btn-danger'; del.textContent = t.delete;

            del.onclick = ()=>{ if(!confirm(t.delete+' '+f.name+'?')) return; fetch('/api/echo/outputs/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:f.name})}).then(r=>r.json()).then(j2=>{ if(j2.ok) fetchSavedOutputs(); else alert('Delete failed'); }).catch(()=>alert('Delete failed')); };

            right.appendChild(a); right.appendChild(del);

            row.appendChild(left); row.appendChild(right);

            el.appendChild(row);

        });

    }).catch(e=>{ console.error('Failed to fetch saved outputs', e); });

}



loadSessionPrefs();

fetchSavedOutputs();

fetchResourcesForSidebar();

fetchModels();



function fetchModels(){

    fetch('/api/echo/models').then(r=>r.json()).then(j=>{

        const sel = document.getElementById('modelSelect');

        if(!sel) return;

        sel.innerHTML='';

        const models = (j.models||[]);

        models.forEach(m=>{

            const opt = document.createElement('option');

            opt.value = m;

            opt.textContent = m.split('/').slice(-1)[0];

            sel.appendChild(opt);

        });

        // preselect current-model if present

        fetch('/api/echo/model').then(r=>r.json()).then(jm=>{

            if(jm && jm.model){

                const idx = Array.from(sel.options).findIndex(o=>o.value===jm.model || o.value===jm.model.replace(window.location.origin+'\\/',''));

                if(idx>=0) sel.selectedIndex = idx;

            }

        }).catch(()=>{});

    }).catch(e=>{console.error('Failed to fetch models',e);});

}



function selectModel(){

    const sel = document.getElementById('modelSelect');

    if(!sel || !sel.value) return appendEcho('No model selected');

    fetch('/api/echo/select_model',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:sel.value})}).then(r=>r.json()).then(j=>{

        if(j.ok){ appendEcho('Model selected: '+j.model); fetchModel(); }

        else appendEcho('Select model failed: '+(j.error||JSON.stringify(j)));

    }).catch(e=>{ appendEcho('Select model request failed'); console.error(e); });

}



function appendEcho(msg){

    const list = document.getElementById('chatMessages');

    if(!list) return;

    const d=document.createElement('div'); d.className='chat-message echo'; d.innerHTML='<div class="chat-icon">🌙</div><div><div class="chat-bubble">'+escapeHtml(msg)+'</div></div>';

    list.appendChild(d); list.scrollTop=list.scrollHeight;

}



function uploadPersona(file){

    if(!file) return;

    const fd = new FormData(); fd.append('file', file); fd.append('type', 'personality'); fd.append('name', file.name);

    fetch('/api/echo/upload_ingest',{method:'POST',body:fd}).then(r=>r.json()).then(j=>{ if(j.ok) appendEcho('Persona uploaded: '+j.saved); else appendEcho('Upload failed: '+(j.error||JSON.stringify(j))); }).catch(e=>{ appendEcho('Upload failed'); console.error(e); });

}



function uploadTraining(file){

    if(!file) return;

    const fd = new FormData(); fd.append('file', file); fd.append('type', 'training'); fd.append('name', file.name);

    fetch('/api/echo/upload_ingest',{method:'POST',body:fd}).then(r=>r.json()).then(j=>{ if(j.ok) appendEcho('Training uploaded: '+j.saved); else appendEcho('Upload failed: '+(j.error||JSON.stringify(j))); }).catch(e=>{ appendEcho('Upload failed'); console.error(e); });

}



function fetchTrainingFiles(){

    fetch('/api/echo/training_files').then(r=>r.json()).then(j=>{

        const sel = document.getElementById('trainingFileSelect');

        if(!sel) return;

        sel.innerHTML='';

        (j.files||[]).forEach(f=>{

            const opt = document.createElement('option'); opt.value=f.name; opt.textContent=f.name; sel.appendChild(opt);

        });

    }).catch(e=>{console.error('Failed to fetch training files',e)});

}



function startTraining(){

    const model = document.getElementById('modelSelect').value;

    const training_file = document.getElementById('trainingFileSelect').value;

    const epochs = parseInt(document.getElementById('tf_epochs').value || '1');

    const batch_size = parseInt(document.getElementById('tf_batch').value || '8');

    const lr = document.getElementById('tf_lr').value || '1e-4';

    const output_name = document.getElementById('tf_output').value || '';

    if(!model || !training_file){ appendEcho('Select a model and training file first'); return; }

    appendEcho('Starting training job...');

    fetch('/api/echo/train_model',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:model, training_file:training_file, output_name:output_name, epochs:epochs, batch_size:batch_size, lr:lr})}).then(r=>r.json()).then(j=>{

        if(j.ok){ appendEcho('Started training job: '+j.job_id); addTrainingJobToList(j.job_id); }

        else appendEcho('Failed to start: '+(j.error||JSON.stringify(j)));

    }).catch(e=>{ appendEcho('Start training request failed'); console.error(e); });

}



function addTrainingJobToList(job_id){

    const container = document.getElementById('trainingJobs');

    const row = document.createElement('div'); row.id = 'train_'+job_id; row.style.padding='6px'; row.style.borderBottom='1px solid #222'; row.textContent = job_id + ' - queued';

    container.prepend(row);

    // start polling

    const iv = setInterval(()=>{

        fetch('/api/echo/train_status?job_id='+encodeURIComponent(job_id)).then(r=>r.json()).then(j=>{

            if(j.job){

                const s = j.job.status || 'unknown';

                row.textContent = job_id + ' - ' + s;

                if(j.log_tail) row.title = j.log_tail.slice(-2000);

                if(s==='finished' || s==='error'){

                    clearInterval(iv);

                    row.textContent = job_id + ' - ' + s + ' (click to view logs)';

                    row.style.cursor='pointer';

                    row.onclick = ()=>{ const w = window.open('/data/models_output/'+job_id+'/train.log','_blank'); };

                }

            }

        }).catch(e=>{console.error('Train status err',e);});

    },2000);

}



// refresh jobs on load

fetchTrainingFiles();



function loadSession(sid){

    fetch('/api/echo/session/'+encodeURIComponent(sid)).then(r=>r.json()).then(j=>{

        if(j.error){ alert('Failed to load session: '+j.error); return; }

        // replace chat messages with loaded history

        const container=document.getElementById('chatMessages');

        container.innerHTML='';

        const hist = j.history || [];

        hist.forEach(m=>{

            if(m.role==='user'){

                addUserMessage(m.content);

            } else {

                addEchoMessage(m.content,m.get('message_id')||m.message_id||null);

            }

        });

        sessionId = sid;

        document.getElementById('session-messages').textContent = hist.filter(x=>x.role==='user').length || 0;

    }).catch(e=>console.error('Load session failed',e));

}



function deleteSession(sid){

    fetch('/api/echo/session/'+encodeURIComponent(sid),{method:'DELETE'}).then(r=>r.json()).then(j=>{

        if(j.deleted){ fetchSessions(); if(sessionId===sid){ clearChat(); } }

    }).catch(e=>console.error('Delete session failed',e));

}



function toggleFavorite(sid){

    fetch('/api/echo/session/favorite',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid})}).then(r=>r.json()).then(j=>{ fetchSessions(); }).catch(e=>console.error('Toggle favorite failed',e));

}



function createSession(){

    // create a new session id and switch to it

    const sid = 'web_'+Date.now();

    fetch('/api/echo/session/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid,title:'Session '+sid})}).then(r=>r.json()).then(j=>{

        if(j.ok){ fetchSessions(); sessionId=sid; clearChat(); }

    }).catch(e=>console.error('Create session failed',e));

}

function clearChat(){

if(!confirm('Clear chat history?'))return;

document.getElementById('chatMessages').innerHTML='<div class="chat-message echo"><div class="chat-icon">🌙</div><div><div class="chat-bubble">Hello... I am Echo 🌙<br>I\\'m here to help with DevOps tasks and learn from our conversations... 💜</div></div></div>';

sessionId='web_'+Date.now();

messageCount=1;

document.getElementById('session-messages').textContent='0';

}

function searchMemory(){

const query=prompt('Search Echo\\'s memory:');

if(!query)return;

fetch('/api/echo/search?q='+encodeURIComponent(query)).then(r=>r.json()).then(data=>{

if(data.results&&data.results.length>0){

let results='Found '+data.results.length+' results:'+String.fromCharCode(10)+String.fromCharCode(10);

data.results.slice(0,5).forEach((r,i)=>{

results+=(i+1)+'. '+r.message.substring(0,100)+'...'+String.fromCharCode(10);

});

alert(results);

}else{

alert('No results found for: '+query);

}

}).catch(err=>{

console.error('Search error:',err);

alert('Search failed');

});

}

function showTyping(){document.getElementById('typingIndicator').classList.add('active');}

function hideTyping(){document.getElementById('typingIndicator').classList.remove('active');}

function escapeHtml(text){

const div=document.createElement('div');

div.textContent=text;

return div.innerHTML;

}

// fetch once immediately and then poll periodically to avoid stale cached JS

fetchModel();

setInterval(fetchModel, 5000);

updateStats();

</script>

{% endblock %}"""

@app.route('/')

def index():

    stats=get_system_stats()

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',DASHBOARD_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),stats=stats,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/api/stats')

def api_stats():

    return jsonify(get_system_stats())





@app.route('/scripts')

def scripts_list():

    res = script_mgr.list_scripts(include_repo_paths=True)

    # Backwards-compatible: if list_scripts returns categories, flatten for templates that expect a flat list

    if res and isinstance(res, list) and isinstance(res[0], dict) and 'category' in res[0]:

        categories = res

        flat = []

        for c in categories:

            flat.extend(c.get('scripts',[]))

        scripts = flat

    else:

        categories = [{'category':'all','scripts':res}]

        scripts = res

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPTS_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),scripts=scripts,categories=categories,request=request,get_flashed_messages=get_flashed_messages)





@app.route('/scripts/refresh_index', methods=['POST'])

def refresh_index():

    # Admin token protection disabled for local development.

    # This endpoint is intentionally left open in dev to simplify testing.

    cache_file = Path(__file__).resolve().parent / 'data' / 'script_index.json'

    try:

        if cache_file.exists():

            cache_file.unlink()

        return jsonify({'ok':True,'message':'index invalidated'})

    except Exception as e:

        return jsonify({'ok':False,'error':str(e)}),500



def _check_basic_auth():

    # Basic auth disabled for local development — always allow.

    return True



def requires_basic_auth(f):

    def wrapper(*args, **kwargs):

        if not _check_basic_auth():

            return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="MasterChief"'})

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__

    return wrapper

@app.route('/scripts/add',methods=['POST'])

@requires_basic_auth

def scripts_add():

    filename=request.form.get('filename')

    content=request.form.get('content')

    if script_mgr.add_script(filename,content):

        flash('Script added successfully!','success')

    else:

        flash('Failed to add script','error')

    return redirect(url_for('scripts_list'))

@app.route('/scripts/view/<filename>')

def scripts_view(filename):

    content=script_mgr.get_script_content(filename)

    if content is None:

        flash('Script not found','error')

        return redirect(url_for('scripts_list'))

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_VIEW_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,content=content,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/scripts/execute/<filename>')

@requires_basic_auth

def scripts_execute(filename):

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=None,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/scripts/run/<filename>',methods=['POST'])

@requires_basic_auth

def scripts_run(filename):

    args=request.form.get('args','')

    result=script_mgr.execute_script(filename,args)

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=result,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/scripts/delete/<filename>')

@requires_basic_auth

def scripts_delete(filename):

    if script_mgr.delete_script(filename):

        flash('Script deleted successfully!','success')

    else:

        flash('Failed to delete script','error')

    return redirect(url_for('scripts_list'))





def _b64_encode_path(p: str) -> str:

    return base64.urlsafe_b64encode(p.encode()).decode()





def _b64_decode_path(s: str) -> str:

    try:

        return base64.urlsafe_b64decode(s.encode()).decode()

    except Exception:

        return ''





@app.route('/scripts/edit/<b64path>')

@requires_basic_auth

def scripts_edit(b64path):

    path = _b64_decode_path(b64path)

    if not path:

        flash('Invalid path','error')

        return redirect(url_for('scripts_list'))

    try:

        with open(path,'r', encoding='utf-8') as f:

            content=f.read()

    except Exception as e:

        flash(f'Failed to read file: {e}','error')

        return redirect(url_for('scripts_list'))

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EDIT_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),content=content,filepath=path,b64path=b64path,message=None,request=request,get_flashed_messages=get_flashed_messages)





@app.route('/scripts/save/<b64path>', methods=['POST'])

@requires_basic_auth

def scripts_save(b64path):

    path = _b64_decode_path(b64path)

    if not path:

        flash('Invalid path','error')

        return redirect(url_for('scripts_list'))

    content=request.form.get('content','')

    try:

        # create backup before overwrite

        backups_dir = Path(__file__).resolve().parent / 'data' / 'backups' / 'scripts'

        backups_dir.mkdir(parents=True, exist_ok=True)

        try:

            if Path(path).exists():

                ts = datetime.now().strftime('%Y%m%d-%H%M%S')

                bak_name = f"{Path(path).name}.{ts}.bak"

                shutil.copy2(path, str(backups_dir / bak_name))

        except Exception:

            # non-fatal

            pass

        # auto-approve - write file directly

        with open(path,'w', encoding='utf-8') as f:

            f.write(content)

        flash(f'Saved {path} (backup created)','success')

    except Exception as e:

        flash(f'Failed to save file: {e}','error')

    return redirect(url_for('scripts_list'))





@app.route('/scripts/backup/<b64path>', methods=['POST'])

@requires_basic_auth

def scripts_backup(b64path):

    path = _b64_decode_path(b64path)

    if not path:

        return jsonify({'success':False,'error':'Invalid path'})

    try:

        backups_dir = Path(__file__).resolve().parent / 'data' / 'backups' / 'scripts'

        backups_dir.mkdir(parents=True, exist_ok=True)

        if Path(path).exists():

            ts = datetime.now().strftime('%Y%m%d-%H%M%S')

            bak_name = f"{Path(path).name}.{ts}.bak"

            bak_path = backups_dir / bak_name

            shutil.copy2(path, str(bak_path))

            return jsonify({'success':True,'backup':str(bak_path)})

        return jsonify({'success':False,'error':'File not found'})

    except Exception as e:

        return jsonify({'success':False,'error':str(e)})





    # --- Minimal Web IDE API endpoints -----------------------------------------------------

    def _safe_script_path(filename: str):

        try:

            fname = secure_filename(filename)

            if not fname:

                return None

            return Path(app.config['SCRIPTS_FOLDER']) / fname

        except Exception:

            return None





    @app.route('/api/ide/scripts')

    def api_ide_scripts():

        files = []

        try:

            scripts_dir = Path(app.config['SCRIPTS_FOLDER'])

            for p in sorted(scripts_dir.glob('*')):

                if p.is_file():

                    files.append({'name': p.name, 'size': p.stat().st_size, 'modified': datetime.fromtimestamp(p.stat().st_mtime).isoformat()})

        except Exception as e:

            return jsonify({'ok': False, 'error': str(e)}), 500

        return jsonify({'ok': True, 'files': files})





    @app.route('/api/ide/load', methods=['POST'])

    def api_ide_load():

        data = request.get_json(silent=True) or (request.form if request.form else {})

        filename = data.get('filename') if isinstance(data, dict) else None

        if not filename:

            return jsonify({'ok': False, 'error': 'filename required'}), 400

        path = _safe_script_path(filename)

        if not path or not path.exists():

            return jsonify({'ok': False, 'error': 'file not found'}), 404

        try:

            content = path.read_text(encoding='utf-8')

            return jsonify({'ok': True, 'content': content})

        except Exception as e:

            return jsonify({'ok': False, 'error': str(e)}), 500





    @app.route('/api/ide/save', methods=['POST'])

    def api_ide_save():

        data = request.get_json(silent=True) or (request.form if request.form else {})

        filename = data.get('filename') if isinstance(data, dict) else None

        content = data.get('content','') if isinstance(data, dict) else (request.form.get('content','') if request.form else '')

        if not filename:

            return jsonify({'ok': False, 'error': 'filename required'}), 400

        try:

            script_mgr.add_script(filename, content)

            return jsonify({'ok': True, 'filename': filename})

        except Exception as e:

            return jsonify({'ok': False, 'error': str(e)}), 500





    @app.route('/api/ide/execute', methods=['POST'])

    def api_ide_execute():

        data = request.get_json(silent=True) or (request.form if request.form else {})

        filename = data.get('filename') if isinstance(data, dict) else None

        content = data.get('content') if isinstance(data, dict) else None

        shell = data.get('shell') if isinstance(data, dict) else None

        remote = bool(data.get('remote')) if isinstance(data, dict) else False

        if remote:

            return jsonify({'ok': False, 'error': 'remote execution not implemented'}), 501

        try:

            if filename:

                path = _safe_script_path(filename)

                if not path or not path.exists():

                    if content:

                        script_mgr.add_script(filename, content)

                    else:

                        return jsonify({'ok': False, 'error': 'file not found'}), 404

                result = script_mgr.execute_script(filename)

                return jsonify({'ok': True, 'stdout': result.get('stdout',''), 'stderr': result.get('stderr',''), 'returncode': result.get('returncode', -1)})

            elif content:

                ext = '.sh'

                if shell == 'python':

                    ext = '.py'

                elif shell in ('powershell','ps1'):

                    ext = '.ps1'

                fd, tmp = tempfile.mkstemp(suffix=ext, prefix='masterchief_exec_', dir=str(app.config['SCRIPTS_FOLDER']))

                os.close(fd)

                with open(tmp,'w',encoding='utf-8') as f:

                    f.write(content)

                os.chmod(tmp, 0o755)

                p = Path(tmp)

                if p.suffix == '.py':

                    cmd = [sys.executable, str(p)]

                elif p.suffix == '.ps1':

                    cmd = ['powershell','-ExecutionPolicy','Bypass','-File', str(p)]

                else:

                    cmd = [str(p)]

                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                out = proc.stdout

                err = proc.stderr

                rc = proc.returncode

                try:

                    p.unlink()

                except Exception:

                    pass

                return jsonify({'ok': True, 'stdout': out, 'stderr': err, 'returncode': rc})

            else:

                return jsonify({'ok': False, 'error': 'no filename or content provided'}), 400

        except subprocess.TimeoutExpired:

            return jsonify({'ok': False, 'error':'execution timed out'}), 500

        except Exception as e:

            return jsonify({'ok': False, 'error': str(e)}), 500





    # Remote credential storage for IDE remote execution (basic, stored in data/ide_creds.json)

    CREDS_FILE = Path(__file__).resolve().parent / 'data' / 'ide_creds.json'



    @app.route('/api/ide/remote/creds', methods=['POST'])

    def api_ide_remote_creds_save():

        data = request.get_json(silent=True) or (request.form if request.form else {})

        target = data.get('target') if isinstance(data, dict) else (request.form.get('target') if request.form else None)

        username = data.get('username') if isinstance(data, dict) else (request.form.get('username') if request.form else None)

        password = data.get('password') if isinstance(data, dict) else (request.form.get('password') if request.form else None)

        if not target or not username or not password:

            return jsonify({'ok': False, 'error':'target,username,password required'}), 400

        try:

            d = {}

            if CREDS_FILE.exists():

                try:

                    d = json.loads(CREDS_FILE.read_text(encoding='utf-8'))

                except Exception:

                    d = {}

            d[target] = {'username': username, 'password': password, 'saved_at': datetime.now().isoformat()}

            CREDS_FILE.parent.mkdir(parents=True, exist_ok=True)

            CREDS_FILE.write_text(json.dumps(d, indent=2), encoding='utf-8')

            return jsonify({'ok': True})

        except Exception as e:

            return jsonify({'ok': False, 'error': str(e)}), 500





    @app.route('/api/ide/remote/creds', methods=['GET'])

    def api_ide_remote_creds_get():

        target = request.args.get('target')

        if not target:

            return jsonify({'ok': False, 'error': 'target required'}), 400

        try:

            if not CREDS_FILE.exists():

                return jsonify({'ok': True, 'cred': None})

            d = json.loads(CREDS_FILE.read_text(encoding='utf-8'))

            return jsonify({'ok': True, 'cred': d.get(target)})

        except Exception as e:

            return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/scripts/suggest_commit/<b64path>', methods=['GET'])

@requires_basic_auth

def scripts_suggest_commit(b64path):

    path = _b64_decode_path(b64path)

    if not path:

        return jsonify({'success':False,'error':'Invalid path'})

    try:

        p = Path(path)

        if not p.exists():

            return jsonify({'success':False,'error':'File not found'})

        text = p.read_text(encoding='utf-8')

        # simple heuristic: use first non-empty line as summary

        first_line = ''

        for ln in text.splitlines():

            s = ln.strip()

            if s:

                first_line = s

                break

        if first_line:

            summary = f"Edit {p.name}: {first_line[:120]}"

        else:

            summary = f"Edit {p.name}: updated content"

        # escape

        summary = html.escape(summary)

        return jsonify({'success':True,'suggestion':summary})

    except Exception as e:

        return jsonify({'success':False,'error':str(e)})





@app.route('/scripts/diff/<b64path>', methods=['POST'])

@requires_basic_auth

def scripts_diff(b64path):

    path = _b64_decode_path(b64path)

    if not path:

        return jsonify({'success':False,'error':'Invalid path'})

    content=request.json.get('content','') if request.is_json else request.form.get('content','')

    try:

        p=Path(path)

        if p.exists():

            original = p.read_text(encoding='utf-8').splitlines()

        else:

            original = []

        new = content.splitlines()

        diff_lines = list(difflib.unified_diff(original, new, fromfile=str(p), tofile=str(p)+' (new)', lineterm=''))

        diff_text = '\n'.join(diff_lines)

        return jsonify({'success':True,'diff':diff_text})

    except Exception as e:

        return jsonify({'success':False,'error':str(e)})





@app.route('/scripts/exec_path/<b64path>', methods=['POST','GET'])

@requires_basic_auth

def scripts_exec_path(b64path):

    path = _b64_decode_path(b64path)

    if not path:

        return jsonify({'success':False,'error':'Invalid path'})

    args=request.form.get('args','') if request.method=='POST' else request.args.get('args','')

    try:

        cmd=[]

        p=Path(path)

        if p.suffix=='.py':

            cmd=[sys.executable,str(p)]

        elif p.suffix=='.ps1':

            cmd=['powershell','-ExecutionPolicy','Bypass','-File',str(p)]

        else:

            cmd=[str(p)]

        if args:

            cmd.extend(args.split())

        result=subprocess.run(cmd,capture_output=True,text=True,timeout=300)

        return jsonify({'success':result.returncode==0,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})

    except subprocess.TimeoutExpired:

        return jsonify({'success':False,'error':'Script execution timed out'})

    except Exception as e:

        return jsonify({'success':False,'error':str(e)})

@app.route('/processes')

def processes_list():

    processes=get_processes()

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',PROCESSES_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),processes=processes,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/processes/kill/<int:pid>')

def processes_kill(pid):

    try:

        proc=psutil.Process(pid)

        proc.terminate()

        flash(f'Process {pid} terminated successfully!','success')

    except psutil.NoSuchProcess:

        flash(f'Process {pid} not found','error')

    except psutil.AccessDenied:

        flash(f'Access denied to terminate process {pid}','error')

    except Exception as e:

        flash(f'Failed to terminate process: {str(e)}','error')

    return redirect(url_for('processes_list'))

@app.route('/services')

def services_list():

    is_windows=sys.platform=='win32'

    services=get_windows_services() if is_windows else []

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SERVICES_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),services=services,is_windows=is_windows,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/services/start/<service_name>')

def services_start(service_name):

    if sys.platform=='win32':

        try:

            subprocess.run(['sc','start',service_name],check=True)

            flash(f'Service {service_name} started successfully!','success')

        except Exception as e:

            flash(f'Failed to start service: {str(e)}','error')

    return redirect(url_for('services_list'))

@app.route('/services/stop/<service_name>')

def services_stop(service_name):

    if sys.platform=='win32':

        try:

            subprocess.run(['sc','stop',service_name],check=True)

            flash(f'Service {service_name} stopped successfully!','success')

        except Exception as e:

            flash(f'Failed to stop service: {str(e)}','error')

    return redirect(url_for('services_list'))

@app.route('/services/restart/<service_name>')

def services_restart(service_name):

    if sys.platform=='win32':

        try:

            subprocess.run(['sc','stop',service_name],check=False)

            time.sleep(2)

            subprocess.run(['sc','start',service_name],check=True)

            flash(f'Service {service_name} restarted successfully!','success')

        except Exception as e:

            flash(f'Failed to restart service: {str(e)}','error')

    return redirect(url_for('services_list'))

@app.route('/addons')

def addons_list():

    uploaded_files=[]

    if app.config['UPLOAD_FOLDER'].exists():

        for file in app.config['UPLOAD_FOLDER'].glob('*.zip'):

            uploaded_files.append({'name':file.name,'size':file.stat().st_size,'modified':datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',ADDONS_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),uploaded_files=uploaded_files,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/addons/upload',methods=['POST'])

def addons_upload():

    if 'file' not in request.files:

        flash('No file selected','error')

        return redirect(url_for('addons_list'))

    file=request.files['file']

    if file.filename=='':

        flash('No file selected','error')

        return redirect(url_for('addons_list'))

    if file and file.filename.endswith('.zip'):

        filename=secure_filename(file.filename)

        filepath=app.config['UPLOAD_FOLDER']/filename

        file.save(filepath)

        flash(f'File {filename} uploaded successfully!','success')

    else:

        flash('Only .zip files are allowed','error')

    return redirect(url_for('addons_list'))

@app.route('/addons/install/<filename>')

def addons_install(filename):

    filepath=app.config['UPLOAD_FOLDER']/secure_filename(filename)

    if not filepath.exists():

        flash('File not found','error')

        return redirect(url_for('addons_list'))

    try:

        extract_dir=app.config['UPLOAD_FOLDER']/'extracted'/filename.replace('.zip','')

        extract_dir.mkdir(parents=True,exist_ok=True)

        with zipfile.ZipFile(filepath,'r') as zip_ref:

            zip_ref.extractall(extract_dir)

        flash(f'Addon {filename} installed successfully to {extract_dir}','success')

    except Exception as e:

        flash(f'Failed to install addon: {str(e)}','error')

    return redirect(url_for('addons_list'))

@app.route('/addons/delete/<filename>')

def addons_delete(filename):

    filepath=app.config['UPLOAD_FOLDER']/secure_filename(filename)

    if filepath.exists():

        filepath.unlink()

        flash(f'File {filename} deleted successfully!','success')

    else:

        flash('File not found','error')

    return redirect(url_for('addons_list'))

@app.route('/resources')

def resources_list():

    """Simple UI for uploading and managing reference/template/example files."""

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',ECHO_RESOURCES_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')))





@app.route('/resources/preview')

def resources_preview():

    rid = request.args.get('id')

    if not rid:

        return 'id required', 400

    idx = _load_resources_index()

    entry = idx.get(rid)

    if not entry:

        return 'not found', 404

    p = Path(entry.get('path'))

    try:

        text = p.read_text(encoding='utf-8')

        # simple safe HTML

        return f'<pre style="white-space:pre-wrap;">{html.escape(text[:4000])}</pre>'

    except Exception:

        return 'binary or unreadable', 400





@app.route('/resources/load_options')

def resources_load_options():

    rid = request.args.get('id')

    sid = request.args.get('session_id','')

    if not rid:

        return 'id required', 400

    idx = _load_resources_index()

    entry = idx.get(rid)

    if not entry:

        return 'not found', 404

    use_persona_checked = 'checked' if entry.get('persona') else ''

    html_form = f"""

    <html><body>

    <h3>Load resource: {html.escape(entry['filename'])}</h3>

    <form method="post" action="/api/resources/load">

    <input type="hidden" name="id" value="{html.escape(rid)}">

    <input type="hidden" name="session_id" value="{html.escape(sid)}">

    <label><input type="checkbox" name="for_ingestion" checked> Ingest into session now</label><br>

    <label><input type="checkbox" name="for_training"> Use for training</label><br>

    <label><input type="checkbox" name="use_persona" {use_persona_checked}> Enable persona for this session</label><br>

    <button type="submit">Load & Ingest</button>

    </form>

    <form method="post" action="/api/resources/enqueue_ingest" style="margin-top:10px;">

    <input type="hidden" name="id" value="{html.escape(rid)}">

    <input type="hidden" name="session_id" value="{html.escape(sid)}">

    <label><input type="checkbox" name="for_training"> Use for training</label><br>

    <button type="submit">Enqueue background ingest</button>

    </form>

    <p><a href="/resources">Back</a></p>

    </body></html>

    """

    return html_form





@app.route('/api/resources/list')

def api_resources_list():

    try:

        idx = _load_resources_index()

        return jsonify(idx)

    except Exception as e:

        app.logger.exception('Failed to list resources')

        return jsonify({'error': str(e)}), 500





@app.route('/api/resources/upload', methods=['POST'])

def api_resources_upload():

    try:

        if 'file' not in request.files:

            return jsonify({'error': 'No file provided'}), 400

        f = request.files['file']

        if not f.filename:

            return jsonify({'error': 'No filename'}), 400

        category = (request.form.get('category') or 'reference').lower()

        for_training = bool(request.form.get('for_training'))

        for_ingestion = bool(request.form.get('for_ingestion'))

        filename = secure_filename(f.filename)

        cat_dir = RESOURCES_DIR / category

        cat_dir.mkdir(parents=True, exist_ok=True)



        # Server-side validation: allowed extensions and size limits

        ALLOWED_EXTS = {'.txt', '.jsonl', '.md', '.pdf', '.json'}

        TEXT_EXTS = {'.txt', '.jsonl', '.md', '.json'}

        MAX_BYTES = 10 * 1024 * 1024  # 10 MB



        ext = Path(filename).suffix.lower()

        if ext not in ALLOWED_EXTS:

            return jsonify({'error': 'Invalid file type', 'allowed': list(ALLOWED_EXTS)}), 400



        # Prevent duplicate filenames in same category (by logical filename)

        idx = _load_resources_index()

        rid = _resource_id_for(category, filename)

        if rid in idx:

            return jsonify({'error': 'Resource already exists', 'message': 'Duplicate resource detected'}), 400



        # quick content-length check when available

        if request.content_length and request.content_length > MAX_BYTES:

            return jsonify({'error': 'File too large', 'max_bytes': MAX_BYTES}), 400



        # store with a safe unique filename to avoid collisions on disk

        stored_name = f"{uuid.uuid4().hex}_{filename}"

        filepath = cat_dir / stored_name

        f.save(filepath)

        # verify saved size

        try:

            if filepath.stat().st_size > MAX_BYTES:

                filepath.unlink(missing_ok=True)

                return jsonify({'error': 'File too large after upload', 'max_bytes': MAX_BYTES}), 400

        except Exception:

            pass

        persona = bool(request.form.get('persona'))

        # Only treat as persona if upload is in the 'personality' category or file is a text type

        if persona and ext not in TEXT_EXTS:

            # reject persona flag for binary types

            persona = False



        entry = {

            'id': rid,

            'filename': filename,

            'category': category,

            'path': str(filepath),

            'for_training': for_training,

            'for_ingestion': for_ingestion,

            'persona': persona,

            'uploaded_at': datetime.now().isoformat()

        }

        idx[rid] = entry

        _save_resources_index(idx)

        # If marked for training, add a lightweight training example

        if for_training:

            try:

                # try to read as text for a useful example

                try:

                    text = filepath.read_text(encoding='utf-8')

                except Exception:

                    text = None

                bot = get_chat_bot()

                summary = (text or '')[:1000]

                ex = TrainingExample(user_message=f"Upload:{filename}", bot_response=summary)

                bot.training_store.add_example(ex)

            except Exception:

                app.logger.exception('Failed to add training example for uploaded resource')

        # If uploaded as a persona, also save under data/personality for easy editing

        if persona:

            try:

                pdir = Path(__file__).resolve().parent / 'data' / 'personality'

                pdir.mkdir(parents=True, exist_ok=True)

                ppath = pdir / filename

                try:

                    text = filepath.read_text(encoding='utf-8')

                    ppath.write_text(text, encoding='utf-8')

                except Exception:

                    # binary persona not supported; skip

                    pass

            except Exception:

                app.logger.exception('Failed to store persona file')

        return jsonify({'ok': True, 'message': 'Uploaded', 'resource': entry})

    except Exception as e:

        app.logger.exception('Upload failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/resources/delete', methods=['POST'])

def api_resources_delete():

    try:

        data = request.get_json() or {}

        rid = data.get('id')

        if not rid:

            return jsonify({'error': 'id required'}), 400

        idx = _load_resources_index()

        entry = idx.get(rid)

        if not entry:

            return jsonify({'error': 'not found'}), 404

        try:

            p = Path(entry.get('path'))

            if p.exists():

                p.unlink()

        except Exception:

            app.logger.exception('Failed to remove resource file')

        del idx[rid]

        _save_resources_index(idx)

        return jsonify({'ok': True})

    except Exception as e:

        app.logger.exception('Delete failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/resources/enqueue_ingest', methods=['POST'])

def api_resources_enqueue_ingest():

    try:

        data = request.get_json() or request.form.to_dict() or {}

        rid = data.get('id')

        session_id = data.get('session_id') or 'default'

        if not rid:

            return jsonify({'error': 'id required'}), 400

        idx = _load_resources_index()

        entry = idx.get(rid)

        if not entry:

            return jsonify({'error': 'resource not found'}), 404



        tasks = _load_ingest_tasks()

        tid = f"task_{int(time.time()*1000)}"

        # track whether the bot has been able to ingest this resource

        tasks[tid] = {'id': tid, 'resource': entry, 'session_id': session_id, 'status': 'pending', 'bot_ingested': False, 'created_at': datetime.now().isoformat()}

        _save_ingest_tasks(tasks)

        return jsonify({'ok': True, 'task_id': tid})

    except Exception as e:

        app.logger.exception('Enqueue failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/resources/ingest_status')

def api_resources_ingest_status():

    try:

        tid = request.args.get('task_id')

        if not tid:

            return jsonify({'error': 'task_id required'}), 400

        tasks = _load_ingest_tasks()

        t = tasks.get(tid)

        if not t:

            return jsonify({'error': 'not found'}), 404

        return jsonify(t)

    except Exception as e:

        app.logger.exception('Status failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/resources/load', methods=['POST'])

def api_resources_load():

    try:

        # support form posts from load_options and JSON posts

        if request.content_type and 'application/json' in request.content_type:

            data = request.get_json() or {}

        else:

            data = request.form.to_dict() or {}

        rid = data.get('id')

        session_id = data.get('session_id') or 'default'

        if not rid:

            return jsonify({'error': 'id required'}), 400

        idx = _load_resources_index()

        entry = idx.get(rid)

        if not entry:

            return jsonify({'error': 'resource not found'}), 404



        p = Path(entry.get('path'))

        if not p.exists():

            return jsonify({'error': 'file missing'}), 500



        # Read small files as text where possible; for binary keep path and size

        try:

            text = p.read_text(encoding='utf-8')

            content = {'type': 'text', 'text': text}

        except Exception:

            # binary fallback: store path and size

            content = {'type': 'binary', 'path': str(p), 'size': p.stat().st_size}



        # respect form flags

        for_ingestion = bool(data.get('for_ingestion'))

        for_training = bool(data.get('for_training'))



        # Persist into session meta under 'loaded_resources'

        storage = get_storage()

        meta = storage.get_session_meta(session_id) or {}

        loaded = meta.get('loaded_resources', {})

        loaded[rid] = {'meta': entry, 'content': content, 'loaded_at': datetime.now().isoformat()}

        meta['loaded_resources'] = loaded

        # Handle persona enable flag from form/json

        use_persona = bool(data.get('use_persona'))

        if use_persona and entry.get('persona'):

            # store the persona in session meta for runtime use

            try:

                meta['personality'] = {'id': rid, 'enabled': True, 'text': content.get('text') if content.get('type') == 'text' else None}

                # log into session history so it's visible in chat

                try:

                    storage.store_message(user='system', message=f'Persona {entry.get("filename")} enabled for session', echo_response='', channel=session_id)

                except Exception:

                    app.logger.exception('Failed to log persona enable into session history')

            except Exception:

                app.logger.exception('Failed to set personality in session meta')

        storage.set_session_meta(session_id, meta)



        # If immediate ingestion requested, call bot.ingest_resource

        bot = None

        try:

            bot = get_chat_bot()

            if for_ingestion and hasattr(bot, 'ingest_resource'):

                try:

                    bot.ingest_resource(session_id, entry, content)

                except Exception:

                    app.logger.exception('Bot ingest failed, continuing')

        except Exception:

            app.logger.exception('Failed to get chat bot for ingest')



        return jsonify({'ok': True, 'message': 'Loaded into session', 'session_id': session_id})

    except Exception as e:

        app.logger.exception('Load failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/resources/convert_to_training', methods=['POST'])

def api_resources_convert_to_training():

    """Convert a resource file into a JSONL training file using the dataset helper."""

    try:

        data = request.get_json() or request.form.to_dict() or {}

        rid = data.get('id')

        if not rid:

            return jsonify({'error': 'id required'}), 400

        idx = _load_resources_index()

        entry = idx.get(rid)

        if not entry:

            return jsonify({'error': 'resource not found'}), 404

        p = Path(entry.get('path'))

        if not p.exists():

            return jsonify({'error': 'file missing'}), 500

        outdir = Path(__file__).parent / 'data' / 'echo_training'

        outdir.mkdir(parents=True, exist_ok=True)

        outpath = outdir / (p.stem + '.jsonl')

        # Use the helper script to generate a JSONL example

        helper = Path(__file__).parent / 'tools' / 'dataset_helpers.py'

        cmd = [sys.executable, str(helper), '--resource', str(p), '--out', str(outpath)]

        proc = subprocess.run(cmd, cwd=str(Path(__file__).parent), capture_output=True, text=True)

        if proc.returncode != 0:

            return jsonify({'error': 'conversion failed', 'stderr': proc.stderr}), 500

        return jsonify({'ok': True, 'training_file': str(outpath.relative_to(Path(__file__).parent))})

    except Exception as e:

        app.logger.exception('Conversion failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/personality/status')

def api_personality_status():

    try:

        session_id = request.args.get('session_id') or 'default'

        storage = get_storage()

        meta = storage.get_session_meta(session_id) or {}

        return jsonify({'personality': meta.get('personality')})

    except Exception as e:

        app.logger.exception('Personality status failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/personality/list')

def api_personality_list():

    try:

        files = []

        # look in preferred echo/data/personality first, then fallback to data/personality

        cand_dirs = []

        pdir1 = Path(__file__).resolve().parent / 'echo' / 'data' / 'personality'

        pdir2 = Path(__file__).resolve().parent / 'data' / 'personality'

        if pdir1.exists():

            cand_dirs.append(pdir1)

        if pdir2.exists() and pdir2 != pdir1:

            cand_dirs.append(pdir2)

        for d in cand_dirs:

            for p in sorted(d.glob('*')):

                if p.is_file():

                    try:

                        files.append({'name': p.name, 'size': p.stat().st_size, 'modified': datetime.fromtimestamp(p.stat().st_mtime).isoformat(), 'path': str(p)})

                    except Exception:

                        files.append({'name': p.name})

        return jsonify({'files': files})

    except Exception as e:

        app.logger.exception('List personalities failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/personality/apply', methods=['POST'])

def api_personality_apply():

    try:

        data = request.get_json() or {}

        session_id = data.get('session_id') or 'default'

        files = data.get('files') or []

        if not files:

            return jsonify({'error': 'files required'}), 400

        # read files and combine contents

        parts = []

        for fname in files:

            # search in same candidate dirs

            found = None

            for d in [Path(__file__).resolve().parent / 'echo' / 'data' / 'personality', Path(__file__).resolve().parent / 'data' / 'personality']:

                p = d / fname

                if p.exists():

                    found = p

                    break

            if not found:

                continue

            try:

                parts.append(found.read_text(encoding='utf-8'))

            except Exception:

                continue

        if not parts:

            return jsonify({'error': 'no files found/readable'}), 400

        combined = "\n\n".join(parts)

        storage = get_storage()

        meta = storage.get_session_meta(session_id) or {}

        meta['personality'] = {'id': ','.join(files), 'enabled': True, 'files': files, 'text': combined}

        storage.set_session_meta(session_id, meta)

        return jsonify({'ok': True, 'session_id': session_id, 'files': files})

    except Exception as e:

        app.logger.exception('Apply personality failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/personality/delete', methods=['POST'])

def api_personality_delete():

    try:

        data = request.get_json() or {}

        files = data.get('files') or []

        if not files:

            return jsonify({'error': 'files required'}), 400

        removed = []

        failed = []

        for fname in files:

            deleted_any = False

            for d in [Path(__file__).resolve().parent / 'echo' / 'data' / 'personality', Path(__file__).resolve().parent / 'data' / 'personality']:

                p = d / fname

                try:

                    if p.exists():

                        p.unlink()

                        removed.append(str(p))

                        deleted_any = True

                except Exception:

                    failed.append(str(p))

            if not deleted_any:

                failed.append(fname)

        return jsonify({'ok': True, 'removed': removed, 'failed': failed})

    except Exception as e:

        app.logger.exception('Delete personalities failed')

        return jsonify({'error': str(e)}), 500




@app.route('/api/personality/toggle', methods=['POST'])
def api_personality_toggle():
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id') or 'default'
        storage = get_storage()
        meta = storage.get_session_meta(session_id) or {}
        personality = meta.get('personality')
        if personality:
            # Toggle enabled/disabled
            personality['enabled'] = not personality.get('enabled', True)
        else:
            return jsonify({'error': 'No personality set for session'}), 400
        storage.set_session_meta(session_id, meta)
        return jsonify({'personality': personality})
    except Exception as e:
        app.logger.exception('Toggle personality failed')
        return jsonify({'error': str(e)}), 500




@app.route('/echo-chat')
def echo_chat():
    return send_file('echo_chat_page.html')

@app.route('/api/echo/chat',methods=['POST'])

def api_echo_chat():

    try:

        data = request.get_json() or {}

        message = data.get('message','')

        session_id = data.get('session_id','default')

        temperature = float(data.get('temperature', 0.7))

        max_tokens = int(data.get('max_tokens', 1024))

        if not message:

            return jsonify({'error':'Message is required'}), 400

        storage = get_storage()

        try:

            meta = storage.get_session_meta(session_id) or {}

        except Exception:

            meta = {}



        # Ensure a persona is applied for this session if none exists

        try:

            def _ensure_session_personality(sid: str):

                """

                Only auto-apply persona files when explicitly enabled via the

                `ECHO_AUTO_APPLY_PERSONA` environment variable. This prevents

                accidental persona injection that can override LLM behavior.

                """

                # Auto-apply is opt-in to avoid unexpected canned responses

                if os.environ.get('ECHO_AUTO_APPLY_PERSONA') != '1':

                    return

                try:

                    smeta = storage.get_session_meta(sid) or {}

                    if smeta.get('personality'):

                        return

                    # Look for persona files under echo/data/personality

                    pdir = Path(__file__).resolve().parent / 'echo' / 'data' / 'personality'

                    if not pdir.exists():

                        pdir = Path(__file__).resolve().parent / 'data' / 'personality'

                    if pdir.exists():

                        for p in sorted(pdir.glob('*.txt')):

                            try:

                                text = p.read_text(encoding='utf-8')

                                pname = p.name

                                smeta['personality'] = {'id': pname, 'enabled': True, 'name': pname, 'text': text}

                                storage.set_session_meta(sid, smeta)

                                try:

                                    storage.store_message(user='system', message=f'Persona {pname} auto-applied to session', echo_response='', channel=sid)

                                except Exception:

                                    pass

                                break

                            except Exception:

                                # skip files that can't be read

                                continue

                except Exception:

                    app.logger.exception('Failed to ensure session personality')

            _ensure_session_personality(session_id)

            # refresh meta after potential change

            try:

                meta = storage.get_session_meta(session_id) or {}

            except Exception:

                meta = {}

        except Exception:

            app.logger.exception('Auto-apply persona step failed')



        um_low = message.lower()



        # New topic

        if any(p in um_low for p in ['i want ', 'i need ', 'can you help', 'help me', "let's", 'let us', 'task:', 'project:']):

            topic = message.strip()[:200]

            topic_state = {'topic': topic, 'stage': 'exploration', 'key_points':[message.strip()], 'turns': 1, 'last_alignment': time.time()}

            try:

                meta['topic_state'] = topic_state

                storage.set_session_meta(session_id, meta)

            except Exception:

                pass

            storage.store_message(user='web_user', message=message, echo_response=f"Got it — I'll explore that: {topic}. Can you provide any important details or constraints?", channel=session_id)

            _upsert_session_meta(session_id, title=topic)

            return jsonify({'response': f"Got it — I'll explore that: {topic}. Can you provide any important details or constraints?", 'session_id': session_id, 'timestamp': time.time(), 'message_id': f"bot_{int(time.time()*1000)}"})



        # Refinement

        if any(p in um_low for p in ['also', 'add', 'update', 'refine', 'change', 'instead', 'correction', 'fix', 'detail', 'more']):

            topic_state = meta.get('topic_state') or {}

            if topic_state and topic_state.get('stage') in ('exploration','refinement'):

                kp = topic_state.get('key_points', [])

                kp.append(message.strip())

                topic_state['key_points'] = kp

                topic_state['stage'] = 'refinement'

                topic_state['turns'] = topic_state.get('turns',0) + 1

                try:

                    meta['topic_state'] = topic_state

                    storage.set_session_meta(session_id, meta)

                except Exception:

                    pass

                storage.store_message(user='web_user', message=message, echo_response="Thanks — I've updated the plan with that detail. Anything else to refine?", channel=session_id)

                _upsert_session_meta(session_id)

                return jsonify({'response': "Thanks — I've updated the plan with that detail. Anything else to refine?", 'session_id': session_id, 'timestamp': time.time(), 'message_id': f"bot_{int(time.time()*1000)}"})



        # Validation

        if any(p in um_low for p in ['is this okay', 'does this work', 'is this correct', 'confirm', 'validate', 'looks good', 'agree', 'ok to proceed']):

            topic_state = meta.get('topic_state') or {}

            if topic_state and topic_state.get('key_points'):

                summary = ' ; '.join([kp if isinstance(kp,str) else str(kp) for kp in topic_state.get('key_points', [])])

                topic_state['stage'] = 'validation'

                topic_state['last_alignment'] = time.time()

                try:

                    meta['topic_state'] = topic_state

                    storage.set_session_meta(session_id, meta)

                except Exception:

                    pass

                resp_text = f"Here's what I have so far: {summary}. Shall I proceed or would you like to refine further?"

                storage.store_message(user='web_user', message=message, echo_response=resp_text, channel=session_id)

                _upsert_session_meta(session_id)

                return jsonify({'response': resp_text, 'session_id': session_id, 'timestamp': time.time(), 'message_id': f"bot_{int(time.time()*1000)}"})



        # Completion

        if any(p in um_low for p in ["done","finished","complete","that's all",'thats all',"that's it","that's it, thanks",'thank you','thanks']):

            topic_state = meta.get('topic_state') or {}

            if topic_state and topic_state.get('key_points'):

                summary = ' ; '.join([kp if isinstance(kp,str) else str(kp) for kp in topic_state.get('key_points', [])])

                topic_state['stage'] = 'complete'

                topic_state['completed_at'] = time.time()

                try:

                    meta['topic_state'] = topic_state

                    storage.set_session_meta(session_id, meta)

                except Exception:

                    pass

                resp_text = f"Done — summary: {summary}. If you'd like to start something new, tell me and we'll begin a new topic."

                storage.store_message(user='web_user', message=message, echo_response=resp_text, channel=session_id)

                _upsert_session_meta(session_id)

                return jsonify({'response': resp_text, 'session_id': session_id, 'timestamp': time.time(), 'message_id': f"bot_{int(time.time()*1000)}"})



        # Fallback to bot

        bot = get_chat_bot()

        # Persona injection is handled in chat_bot.py

        message_for_bot = message

        response = bot.chat(message_for_bot, session_id=session_id, temperature=temperature, max_tokens=max_tokens)

        # Sanitize obviously-garbled responses (long repeated characters, repeated "A: A: A:" patterns, etc.)

        def _is_garbled_text(t: str) -> bool:

            # Return True if text looks like garbage; include reasons for logging.

            if not t or not isinstance(t, str):

                return False

            # ignore short replies

            if len(t) < 20:

                return False

            # don't sanitize code blocks or JSON-like outputs

            if '```' in t or t.strip().startswith('{') or t.strip().startswith('['):

                return False

            # remove whitespace for some checks

            no_ws = ''.join(t.split())

            if not no_ws:

                return False

            reasons = []

            ctr = Counter(ch for ch in no_ws)

            most_char, most_count = ctr.most_common(1)[0]

            # very high concentration on a single non-alphanumeric char

            if most_count / max(1, len(no_ws)) > 0.75 and most_count > 30:

                if not most_char.isalnum():

                    reasons.append('high_non_alnum_concentration')

            # very long single-char runs (likely repeated garbage)

            max_run = 1

            cur = 1

            for i in range(1, len(no_ws)):

                if no_ws[i] == no_ws[i-1]:

                    cur += 1

                    if cur > max_run:

                        max_run = cur

                else:

                    cur = 1

            if max_run >= 40:

                reasons.append('long_run')

            # repeated labelled pattern like "A: A: A: A:" many times

            if re.search(r'(?:[A-Za-z]:\s*){10,}', t):

                reasons.append('repeated_label_pattern')

            # if we detected at least two independent signals, mark garbled

            if len(reasons) >= 2:

                # store reasons on function object for logging

                _is_garbled_text._last_reasons = reasons

                return True

            # otherwise not garbled

            return False



        # apply sanitizer and preserve original for debugging when possible

        try:

            orig_text = response.get('response') if isinstance(response, dict) else str(response)

            if _is_garbled_text(orig_text):

                reasons = getattr(_is_garbled_text, '_last_reasons', None)

                app.logger.warning('Sanitized garbled response for session %s, reasons=%s', session_id, reasons)

                # persist a debug record to disk for later analysis

                try:

                    dbg_dir = os.path.join(os.getcwd(), 'data')

                    os.makedirs(dbg_dir, exist_ok=True)

                    logfile = os.path.join(dbg_dir, 'echo_sanitizer_logs.jsonl')

                    entry = {'ts': time.time(), 'session_id': session_id, 'reasons': reasons, 'original': orig_text}

                    try:

                        with open(logfile, 'a', encoding='utf-8') as fh:

                            fh.write(json.dumps(entry, ensure_ascii=False) + '\n')

                    except Exception:

                        app.logger.exception('Failed to write sanitizer log')

                except Exception:

                    pass

                fallback = "I'm sorry — I couldn't generate a proper reply. Could you rephrase?"

                if isinstance(response, dict):

                    response['_original_response'] = orig_text

                    response['response'] = fallback

                else:

                    response = {'response': fallback, '_original_response': orig_text}

        except Exception:

            # never let sanitizer crash the endpoint

            app.logger.exception('Response sanitizer failed')

        # if client requested debug, include LLM debug output if available

        try:

            if data.get('debug'):

                debug_info = getattr(bot, '_last_llm_debug', None)

                if isinstance(response, dict):

                    response['_llm_debug'] = debug_info

                else:

                    response = {'response': str(response), '_llm_debug': debug_info}

        except Exception:

            pass

        # --- New: support saving long responses to a txt file and auto-continue when truncated ---

        # full_text holds the authoritative reply text we persist and/or save

        full_text = response.get('response') if isinstance(response, dict) else str(response)

        # Request flags: save_to_file (bool) and auto_continue (bool). If auto_continue is omitted, fall back to app config.

        save_to_file = _parse_bool_val(data.get('save_to_file'), default=False)

        auto_continue = _parse_bool_val(data.get('auto_continue'), default=bool(app.config.get('ECHO_AUTO_CONTINUE', False)))



        def _looks_truncated(t: str) -> bool:

            if not t or len(t) < 200:

                return False

            ts = t.rstrip()

            if ts.endswith('...'):

                return True

            # if it doesn't end in typical sentence terminator, assume it may be cut off

            if ts[-1] not in '.?!':

                return True

            return False



            # If requested (or configured) attempt to auto-continue when the reply looks cut off,

            # but guard against off-topic or rambling continuations by checking similarity

            # between the continuation and the user's original message.

            if auto_continue:

                max_retries = int(app.config.get('ECHO_CONTINUE_MAX_RETRIES', 1))

                min_sim = float(app.config.get('ECHO_CONTINUE_MIN_SIMILARITY', 0.12))

                retries = 0

                def _should_accept_continuation(prev_text: str, cont_text: str, user_msg: str) -> bool:

                    try:

                        if not cont_text or not isinstance(cont_text, str):

                            return False

                        # very short continuations are not useful

                        if len(cont_text.strip()) < 30:

                            return False

                        # similarity between user message and continuation (simple heuristic)

                        sim = difflib.SequenceMatcher(None, (user_msg or '').lower(), cont_text.lower()).ratio()

                        # token overlap on longer words

                        import re

                        user_words = set(w for w in re.findall(r"\w{4,}", (user_msg or '').lower()))

                        cont_words = set(w for w in re.findall(r"\w{4,}", cont_text.lower()))

                        overlap = 0.0

                        if user_words:

                            overlap = len(user_words & cont_words) / max(1, len(user_words))

                        # reject if continuation appears extremely similar to previous text (repeat) or clearly off-topic

                        if cont_text.strip() in (prev_text or ''):

                            return False

                        # accept only when similarity or overlap meets thresholds

                        if sim >= min_sim or overlap >= 0.05:

                            return True

                        return False

                    except Exception:

                        return False



                while retries < max_retries and _looks_truncated(full_text):

                    try:

                        cont_prompt = app.config.get('ECHO_CONTINUE_PROMPT', 'Please continue the previous response.')

                        cont_resp = bot.chat(cont_prompt, session_id=session_id)

                        cont_text = cont_resp.get('response') if isinstance(cont_resp, dict) else str(cont_resp)

                        if not cont_text:

                            break

                        # decide whether to accept this continuation

                        if not _should_accept_continuation(full_text, cont_text, message):

                            # mark on the response that continuation was halted due to divergence

                            if isinstance(response, dict):

                                response['continued_halted_due_to_divergence'] = True

                            else:

                                response = {'response': full_text, 'continued_halted_due_to_divergence': True}

                            break

                        # append accepted continuation

                        full_text = full_text + "\n" + cont_text

                        if isinstance(response, dict):

                            response['response'] = full_text

                            response['continued_count'] = response.get('continued_count', 0) + 1

                        else:

                            response = {'response': full_text, 'continued_count': 1}

                    except Exception:

                        app.logger.exception('Auto-continue failed')

                        break

                    retries += 1



        # Optionally save the full response to a file so very long replies are available un-truncated

        if save_to_file:

            try:

                outdir = Path(__file__).parent / 'data' / 'echo_chat_outputs'

                outdir.mkdir(parents=True, exist_ok=True)

                fname = f"{session_id}_{int(time.time()*1000)}_{uuid.uuid4().hex}.txt"

                fpath = outdir / fname

                fpath.write_text(full_text, encoding='utf-8')

                rel = str(fpath.relative_to(Path(__file__).parent))

                if isinstance(response, dict):

                    response['saved_to'] = rel

                else:

                    response = {'response': full_text, 'saved_to': rel}

            except Exception:

                app.logger.exception('Failed to save echo response to file')



        # persist session metadata so it appears in chat history list

        try:

            _upsert_session_meta(session_id)

        except Exception:

            pass

        storage = get_storage()

        storage.store_message(user='web_user', message=message, echo_response=full_text, channel=session_id)

        return jsonify(response)

    except Exception as e:

        return jsonify({'error':str(e)}),500





@app.route('/api/echo/outputs')

def api_echo_outputs():

    """List saved full echo-chat outputs."""

    try:

        outdir = Path(__file__).parent / 'data' / 'echo_chat_outputs'

        files = []

        if outdir.exists():

            for p in sorted(outdir.glob('*.txt')):

                try:

                    files.append({'name': p.name, 'size': p.stat().st_size, 'modified': datetime.fromtimestamp(p.stat().st_mtime).isoformat(), 'path': str(p.relative_to(Path(__file__).parent))})

                except Exception:

                    files.append({'name': p.name})

        return jsonify({'files': files})

    except Exception as e:

        app.logger.exception('List echo outputs failed')

        return jsonify({'error': str(e)}), 500





@app.route('/data/echo_chat_outputs/<path:fname>')

def serve_echo_output(fname):

    """Serve/download a saved echo-chat output file."""

    try:

        outdir = Path(__file__).parent / 'data' / 'echo_chat_outputs'

        fpath = (outdir / fname).resolve()

        if not str(fpath).startswith(str(outdir.resolve())):

            return 'invalid path', 400

        if not fpath.exists():

            return 'not found', 404

        return send_file(str(fpath), as_attachment=True)

    except Exception as e:

        app.logger.exception('Failed to serve echo output')

        return jsonify({'error': str(e)}), 500

@app.route('/api/echo/outputs/delete', methods=['POST'])

def api_echo_outputs_delete():

    try:

        data = request.get_json() or {}

        name = data.get('name')

        if not name:

            return jsonify({'error': 'name required'}), 400

        outdir = Path(__file__).parent / 'data' / 'echo_chat_outputs'

        fpath = (outdir / name).resolve()

        if not str(fpath).startswith(str(outdir.resolve())):

            return jsonify({'error': 'invalid path'}), 400

        if not fpath.exists():

            return jsonify({'error': 'not found'}), 404

        try:

            fpath.unlink()

        except Exception:

            app.logger.exception('Failed to delete echo output %s', fpath)

            return jsonify({'error': 'delete failed'}), 500

        return jsonify({'ok': True})

    except Exception as e:

        app.logger.exception('Delete echo output failed')

        return jsonify({'error': str(e)}), 500

@app.route('/api/echo/session_prefs', methods=['GET','POST'])

def api_echo_session_prefs():

    try:

        storage = get_storage()

        if request.method == 'GET':

            session_id = request.args.get('session_id') or 'default'

            meta = storage.get_session_meta(session_id) or {}

            prefs = meta.get('echo_prefs') or {}

            # ensure sensible defaults

            prefs.setdefault('auto_continue', bool(app.config.get('ECHO_AUTO_CONTINUE', False)))

            prefs.setdefault('save_to_file', False)

            prefs.setdefault('lang', 'en')

            return jsonify({'prefs': prefs})

        else:

            data = request.get_json() or {}

            session_id = data.get('session_id') or 'default'

            prefs = data.get('prefs') or {}

            meta = storage.get_session_meta(session_id) or {}

            meta['echo_prefs'] = meta.get('echo_prefs', {})

            # merge only known keys

            if 'auto_continue' in prefs:

                meta['echo_prefs']['auto_continue'] = bool(prefs.get('auto_continue'))

            if 'save_to_file' in prefs:

                meta['echo_prefs']['save_to_file'] = bool(prefs.get('save_to_file'))

            if 'lang' in prefs:

                meta['echo_prefs']['lang'] = str(prefs.get('lang'))

            storage.set_session_meta(session_id, meta)

            return jsonify({'ok': True, 'prefs': meta['echo_prefs']})

    except Exception as e:

        app.logger.exception('Session prefs failed')

        return jsonify({'error': str(e)}), 500

@app.route('/api/echo/train',methods=['POST'])

def api_echo_train():

    try:

        data=request.get_json()

        user_message=data.get('user_message','')

        bot_response=data.get('bot_response','')

        quality_str=data.get('quality','acceptable')

        quality_map={

            'excellent':ResponseQuality.EXCELLENT,

            'good':ResponseQuality.GOOD,

            'acceptable':ResponseQuality.ACCEPTABLE,

            'poor':ResponseQuality.POOR

        }

        quality=quality_map.get(quality_str,ResponseQuality.ACCEPTABLE)

        bot=get_chat_bot()

        success=bot.train(user_message,bot_response,quality)

        return jsonify({'success':success})

    except Exception as e:

        return jsonify({'error':str(e),'success':False}),500

@app.route('/api/echo/stats')

def api_echo_stats():

    try:

        bot=get_chat_bot()

        stats=bot.get_training_stats()

        return jsonify(stats)

    except Exception as e:

        return jsonify({'error':str(e)}),500

@app.route('/api/echo/history')

def api_echo_history():

    try:

        session_id=request.args.get('session_id','default')

        limit=int(request.args.get('limit',50))

        storage=get_storage()

        # Retrieve persisted conversation history for the session

        history = storage.get_conversation_history(user='web_user', limit=limit, channel=session_id)

        return jsonify({'history':history})

    except Exception as e:

        return jsonify({'error':str(e)}),500





@app.route('/api/echo/model', methods=['GET'])
def api_echo_model():
    try:
        bot = get_chat_bot()
        model = getattr(bot, '_local_model_path', None)
        if model:
            return jsonify({'model': model})
        else:
            return jsonify({'model': None})
    except Exception as e:
        app.logger.exception('Get model failed')
        return jsonify({'error': str(e)}), 500

@app.route('/api/echo/preload_model', methods=['POST','GET'])

def api_echo_preload_model():

    """Discover local model and attempt a small generation to warm the worker.

    Returns JSON with model path and whether the warm-up succeeded.

    """

    try:

        bot = get_chat_bot()

        model = None

        warmed = False



        # Prefer an explicitly selected model stored by `/api/echo/select_model`.

        try:

            cfg = Path(__file__).parent / 'data' / 'echo_model.json'

            if cfg.exists():

                try:

                    cfgd = json.loads(cfg.read_text(encoding='utf-8'))

                    if cfgd.get('model'):

                        model = cfgd.get('model')

                except Exception:

                    model = None

        except Exception:

            model = None



        # Fall back to discovery if no explicit selection

        if not model and hasattr(bot, '_find_local_model'):

            try:

                model = bot._find_local_model()

            except Exception:

                model = None



        # Allow caller to request no warm (useful for large models)

        payload = request.get_json(silent=True) or {}

        do_warm = payload.get('warm', True)



        if model and do_warm:

            if hasattr(bot, '_generate_with_local_llm'):

                try:

                    out = bot._generate_with_local_llm('Hello, warmup', max_tokens=8, temperature=0.1)

                    warmed = bool(out)

                except Exception as e:

                    app.logger.exception('Preload generation failed')

                    return jsonify({'model': model, 'warmed': False, 'error': str(e)}), 500



        return jsonify({'model': model, 'warmed': warmed})

    except Exception as e:

        app.logger.exception('Preload endpoint failed')

        return jsonify({'error': str(e)}), 500







@app.route('/api/echo/generate_image', methods=['POST'])

def api_echo_generate_image():

    """Generate an image from a prompt using a local CPU-only diffusers pipeline if available.



    This endpoint is intentionally local-first: it will attempt to import `diffusers`

    and run on CPU. If `diffusers` is not installed the endpoint returns 501 with

    an installation hint. The endpoint includes a small in-memory cache and a per-session

    simple rate limit.

    """

    try:

        payload = request.get_json() or {}

        prompt = payload.get('prompt') or payload.get('message')

        session_id = payload.get('session_id') or request.remote_addr or 'anon'

        size = payload.get('size') or '512x512'

        style = payload.get('style') or ''

        if not prompt:

            return jsonify({'error': 'prompt required'}), 400



        # Rate limiting (simple sliding window per session/ip)

        now_ts = time.time()

        rl_key = str(session_id)

        window = 60

        timestamps = IMAGE_RATE.get(rl_key, [])

        timestamps = [t for t in timestamps if now_ts - t < window]

        if len(timestamps) >= app.config.get('IMAGE_RATE_LIMIT_PER_MIN', 6):

            return jsonify({'error': 'rate limit exceeded'}), 429

        timestamps.append(now_ts)

        IMAGE_RATE[rl_key] = timestamps



        # Cache key

        cache_key = f"{prompt}||{size}||{style}"

        cached = IMAGE_CACHE.get(cache_key)

        if cached and (now_ts - cached.get('ts', 0) < app.config.get('IMAGE_CACHE_TTL', 86400)):

            return jsonify({'ok': True, 'url': '/' + cached['path']})



        outdir = Path(__file__).parent / 'data' / 'echo_images'

        outdir.mkdir(parents=True, exist_ok=True)



        provider = app.config.get('IMAGE_PROVIDER', 'local')

        if provider != 'local':

            return jsonify({'error': 'Only local CPU generation is enabled in this demo. Set IMAGE_PROVIDER=local.'}), 501



        # Attempt local generation with diffusers on CPU

        try:

            import torch

            from diffusers import StableDiffusionPipeline

        except Exception as e:

            return jsonify({'error': 'diffusers or torch not installed (pip install diffusers[torch] transformers)'}), 501



        try:

            model_id = os.environ.get('IMAGE_LOCAL_MODEL', 'runwayml/stable-diffusion-v1-5')

            # Load the pipeline directly onto CPU to avoid moving 'meta' tensors between devices,

            # which can raise NotImplementedError for some HF transformer configs.

            try:

                pipe = StableDiffusionPipeline.from_pretrained(model_id, device_map='cpu')

            except Exception:

                # Fallback when device_map isn't accepted: load normally and rely on CPU placement.

                pipe = StableDiffusionPipeline.from_pretrained(model_id)



            # parse size

            width, height = (512, 512)

            try:

                parts = size.split('x')

                if len(parts) == 2:

                    width = int(parts[0])

                    height = int(parts[1])

            except Exception:

                pass



            # generate

            image = pipe(prompt, height=height, width=width, num_inference_steps=20).images[0]

            fname = f"img_{int(time.time()*1000)}_{uuid.uuid4().hex}.png"

            fpath = outdir / fname

            image.save(str(fpath))

            rel = fpath.relative_to(Path(__file__).parent).as_posix()

            IMAGE_CACHE[cache_key] = {'path': rel, 'ts': time.time()}

            return jsonify({'ok': True, 'url': '/' + rel})

        except Exception as e:

            app.logger.exception('Local image generation failed')

            return jsonify({'error': f'local generation failed: {e}'}), 500



    except Exception as e:

        app.logger.exception('Generate image failed')

        return jsonify({'error': str(e)}), 500





@app.route('/data/echo_images/<path:fname>')

def serve_echo_image(fname):

    try:

        outdir = Path(__file__).parent / 'data' / 'echo_images'

        fpath = (outdir / fname).resolve()

        if not str(fpath).startswith(str(outdir.resolve())):

            return 'invalid path', 400

        if not fpath.exists():

            return 'not found', 404

        return send_file(str(fpath), as_attachment=False)

    except Exception as e:

        app.logger.exception('Failed to serve echo image')

        return jsonify({'error': str(e)}), 500


@app.route('/api/echo/generate_image_async', methods=['POST'])
def api_echo_generate_image_async():
    """Enqueue an image generation job by writing a job file for the worker."""
    try:
        payload = request.get_json() or {}
        prompt = payload.get('prompt') or payload.get('message')
        session_id = payload.get('session_id') or request.remote_addr or 'anon'
        size = payload.get('size') or '512x512'
        style = payload.get('style') or ''
        if not prompt:
            return jsonify({'error': 'prompt required'}), 400

        # simple rate limiting per session/ip
        now_ts = time.time()
        rl_key = str(session_id)
        window = 60
        timestamps = IMAGE_RATE.get(rl_key, [])
        timestamps = [t for t in timestamps if now_ts - t < window]
        if len(timestamps) >= app.config.get('IMAGE_RATE_LIMIT_PER_MIN', 6):
            return jsonify({'error': 'rate limit exceeded'}), 429
        timestamps.append(now_ts)
        IMAGE_RATE[rl_key] = timestamps

        cache_key = f"{prompt}||{size}||{style}"
        cached = IMAGE_CACHE.get(cache_key)
        if cached and (now_ts - cached.get('ts', 0) < app.config.get('IMAGE_CACHE_TTL', 86400)):
            return jsonify({'ok': True, 'url': '/' + cached['path']})

        job_id = uuid.uuid4().hex
        job = {'id': job_id, 'prompt': prompt, 'size': size, 'style': style, 'status': 'queued', 'progress': 0, 'path': None, 'error': None, 'created': now_ts}
        IMAGE_JOBS[job_id] = job

        # persist job to disk for external worker to pick up
        jobs_dir = Path(__file__).parent / 'data' / 'image_jobs'
        jobs_dir.mkdir(parents=True, exist_ok=True)
        job_path = jobs_dir / (job_id + '.json')
        tmp_path = jobs_dir / (job_id + '.json.tmp')
        tmp_path.write_text(json.dumps(job), encoding='utf-8')
        try:
            tmp_path.replace(job_path)
        except Exception:
            # best-effort rename
            job_path.write_text(json.dumps(job), encoding='utf-8')

        return jsonify({'ok': True, 'job_id': job_id})
    except Exception as e:
        app.logger.exception('Enqueue image job failed')
        return jsonify({'error': str(e)}), 500


@app.route('/api/echo/image_status')
def api_echo_image_status():
    job_id = request.args.get('job_id')
    if not job_id:
        return jsonify({'error': 'job_id required'}), 400
    # prefer in-memory store but fall back to disk-based job file
    job = IMAGE_JOBS.get(job_id)
    jobs_dir = Path(__file__).parent / 'data' / 'image_jobs'
    job_file = jobs_dir / (job_id + '.json')
    if job_file.exists():
        try:
            job = json.loads(job_file.read_text(encoding='utf-8'))
        except Exception:
            pass
    if not job:
        return jsonify({'error': 'not found'}), 404
    res = dict(job)
    if job.get('path'):
        res['url'] = '/' + job['path']
    return jsonify(res)





@app.route('/api/echo/debug_image_provider')

def api_echo_debug_image_provider():

    """Return current image provider config and whether local libs are importable."""

    try:

        import importlib.util

        has_torch = importlib.util.find_spec('torch') is not None

        has_diffusers = importlib.util.find_spec('diffusers') is not None

    except Exception:

        has_torch = False

        has_diffusers = False

    return jsonify({'IMAGE_PROVIDER': app.config.get('IMAGE_PROVIDER'), 'torch_installed': bool(has_torch), 'diffusers_installed': bool(has_diffusers)})







@app.route('/api/echo/training_files')

def api_echo_training_files():

    try:

        base = Path(__file__).parent / 'data' / 'echo_training'

        files = []

        if base.exists():

            for p in sorted(base.glob('*')):

                if p.is_file():

                    files.append({'name': p.name, 'size': p.stat().st_size, 'modified': datetime.fromtimestamp(p.stat().st_mtime).isoformat()})

        return jsonify({'files': files})

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@app.route('/api/echo/train_model', methods=['POST'])

def api_echo_train_model():

    """Start a training job (runs tools/finetune_stub.py by default).



    Payload: JSON { model: 'models/..gguf', training_file: 'filename.jsonl', output_name: 'myrun', epochs: 1, batch_size: 8, lr: 1e-4 }

    """

    try:

        data = request.get_json() or {}

        model = data.get('model')

        training_file = data.get('training_file')

        resource_id = data.get('resource_id')

        output_name = data.get('output_name') or f"run_{int(time.time())}"

        epochs = int(data.get('epochs', 1))

        batch_size = int(data.get('batch_size', 8))

        lr = float(data.get('lr', 1e-4))



        engine = data.get('engine', 'stub')

        # validate basics

        if not model or (not training_file and not resource_id):

            return jsonify({'error': 'model and either training_file or resource_id are required'}), 400



        model_path = Path(model)

        if not model_path.is_absolute():

            model_path = Path.cwd() / model_path

        if not model_path.exists():

            return jsonify({'error': 'model not found'}), 404



        if resource_id:

            # convert resource to training file

            idx = _load_resources_index()

            entry = idx.get(resource_id)

            if not entry:

                return jsonify({'error': 'resource not found'}), 404

            p = Path(entry.get('path'))

            if not p.exists():

                return jsonify({'error': 'resource file not found'}), 404

            # use the convert logic

            from tools.dataset_helper import convert_file_to_jsonl

            tfile = Path(__file__).parent / 'data' / 'echo_training' / f"{resource_id}.jsonl"

            try:

                convert_file_to_jsonl(str(p), str(tfile))

            except Exception as e:

                return jsonify({'error': f'conversion failed: {e}'}), 500

        else:

            tfile = Path(__file__).parent / 'data' / 'echo_training' / training_file

            if not tfile.exists():

                return jsonify({'error': 'training file not found'}), 404



        job_id = uuid.uuid4().hex

        outdir = Path(__file__).parent / 'data' / 'models_output' / job_id

        outdir.mkdir(parents=True, exist_ok=True)



        # select worker based on engine

        if engine == 'stub':

            worker = Path(__file__).parent / 'tools' / 'finetune_stub.py'

            cmd = [sys.executable, str(worker), '--model', str(model_path), '--data', str(tfile), '--output', str(outdir), '--epochs', str(epochs), '--batch_size', str(batch_size), '--lr', str(lr)]

        elif engine == 'peft':

            # prefer a real PEFT/LoRA pipeline; check for dependencies

            try:

                import transformers  # type: ignore

                import peft  # type: ignore

            except Exception:

                return jsonify({'error': 'PEFT/transformers not installed', 'install': 'pip install "transformers[sentencepiece]" accelerate peft bitsandbytes --upgrade'}), 400

            # If you later add a real training script, point to it here.

            worker = Path(__file__).parent / 'tools' / 'finetune_stub.py'

            cmd = [sys.executable, str(worker), '--model', str(model_path), '--data', str(tfile), '--output', str(outdir), '--epochs', str(epochs), '--batch_size', str(batch_size), '--lr', str(lr)]

        else:

            return jsonify({'error': 'unknown engine', 'allowed': ['stub','peft']}), 400



        TRAIN_JOBS[job_id] = {'id': job_id, 'status': 'queued', 'model': str(model_path), 'training_file': str(tfile), 'output': str(outdir), 'engine': engine, 'pid': None, 'returncode': None, 'started_at': None, 'finished_at': None}

        _save_train_jobs()

        _start_train_job(job_id, cmd, cwd=str(Path(__file__).parent))



        return jsonify({'ok': True, 'job_id': job_id})

    except Exception as e:

        app.logger.exception('Start train failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/echo/train_status')

def api_echo_train_status():

    job_id = request.args.get('job_id')

    if not job_id:

        return jsonify({'error': 'job_id required'}), 400

    job = TRAIN_JOBS.get(job_id)

    if not job:

        return jsonify({'error': 'job not found'}), 404

    outdir = Path(__file__).parent / 'data' / 'models_output' / job_id

    log_path = outdir / 'train.log'

    log_tail = ''

    if log_path.exists():

        try:

            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:

                data = f.read()

                log_tail = data[-8192:]

        except Exception:

            log_tail = ''

    return jsonify({'job': job, 'log_tail': log_tail})







@app.route('/api/echo/train_list')

def api_echo_train_list():

    try:

        return jsonify({'jobs': list(TRAIN_JOBS.values())})

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@app.route('/api/echo/train_cancel', methods=['POST'])

def api_echo_train_cancel():

    try:

        data = request.get_json() or {}

        job_id = data.get('job_id')

        if not job_id:

            return jsonify({'error': 'job_id required'}), 400

        job = TRAIN_JOBS.get(job_id)

        if not job:

            return jsonify({'error': 'job not found'}), 404

        pid = job.get('pid')

        if not pid:

            job['status'] = 'cancelled'

            job['finished_at'] = time.time()

            return jsonify({'ok': True, 'message': 'job marked cancelled (no pid)'} )

        try:

            p = psutil.Process(int(pid))

            p.terminate()

            time.sleep(1)

            if p.is_running():

                p.kill()

        except Exception:

            # process may have already exited

            pass

        job['status'] = 'cancelled'

        job['finished_at'] = time.time()

        return jsonify({'ok': True})

    except Exception as e:

        app.logger.exception('Cancel failed')

        return jsonify({'error': str(e)}), 500







@app.route('/api/echo/models', methods=['GET'])
def api_echo_models():
    try:
        import glob
        models_dir = Path.cwd() / 'models'
        models = []
        if models_dir.exists():
            for f in models_dir.glob('*.gguf'):
                models.append({
                    'name': f.name,
                    'path': str(f),
                    'size': f.stat().st_size
                })
        return jsonify({'models': models})
    except Exception as e:
        app.logger.exception('List models failed')
        return jsonify({'error': str(e)}), 500





@app.route('/echo-train')

def echo_train_page():

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',ECHO_TRAINING_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')))





@app.route('/api/echo/select_model', methods=['POST'])

def api_echo_select_model():

    try:

        data = request.get_json() or {}

        model = data.get('model')

        if not model:

            return jsonify({'error': 'model required'}), 400

        base = Path.cwd()

        p = Path(model)

        if not p.is_absolute():

            p = base / model

        if not p.exists():

            return jsonify({'error': 'model not found'}), 404

        bot = get_chat_bot()

        # allow bot to accept new model path

        if hasattr(bot, 'set_local_model'):

            try:

                bot.set_local_model(str(p))

            except Exception:

                app.logger.exception('Failed to set model on bot')

        # unload any cached in-process model so it reloads with new path

        try:

            from echo.runtime import model_runtime

            model_runtime.unload_model()

        except Exception:

            pass

        # persist selection

        cfg = Path(__file__).parent / 'data' / 'echo_model.json'

        cfg.parent.mkdir(parents=True, exist_ok=True)

        cfg.write_text(json.dumps({'model': str(p)}), encoding='utf-8')

        return jsonify({'ok': True, 'model': str(p)})

    except Exception as e:

        app.logger.exception('Select model failed')

        return jsonify({'error': str(e)}), 500





@app.route('/api/echo/upload_ingest', methods=['POST'])

def api_echo_upload_ingest():

    """Upload a persona or training file to the data folders and optionally ingest it."""

    try:

        typ = request.form.get('type') or 'personality'

        name = request.form.get('name') or None

        f = request.files.get('file')

        if not f:

            return jsonify({'error': 'file required'}), 400

        content = f.read().decode('utf-8')

        saved_path = None

        if typ == 'personality' or typ == 'persona':

            pdir = Path(__file__).parent / 'data' / 'personality'

            pdir.mkdir(parents=True, exist_ok=True)

            fname = name or f.filename or f'persona_{int(time.time())}.txt'

            target = pdir / secure_filename(fname)

            target.write_text(content, encoding='utf-8')

            saved_path = str(target)

        else:

            tdir = Path(__file__).parent / 'data' / 'echo_training'

            tdir.mkdir(parents=True, exist_ok=True)

            fname = name or f.filename or f'train_{int(time.time())}.jsonl'

            target = tdir / fname

            # append raw content

            with open(str(target), 'a', encoding='utf-8') as fh:

                if not content.endswith('\n'):

                    content = content + '\n'

                fh.write(content)

            saved_path = str(target)



        # attempt to have bot ingest the content if supported

        try:

            bot = get_chat_bot()

            entry = {'type': typ, 'name': Path(saved_path).name}

            if hasattr(bot, 'ingest_resource'):

                try:

                    bot.ingest_resource('default', entry, content)

                except Exception:

                    app.logger.exception('Bot ingest failed')

        except Exception:

            app.logger.exception('Failed to call bot.ingest_resource')



        return jsonify({'ok': True, 'saved': saved_path})

    except Exception as e:

        app.logger.exception('Upload ingest failed')

        return jsonify({'error': str(e)}), 500

@app.route('/api/echo/search')

def api_echo_search():

    try:

        query=request.args.get('q','')

        if not query:

            return jsonify({'error':'Query parameter q is required'}),400

        storage=get_storage()

        results=storage.search_conversations(query,limit=20)

        return jsonify({'results':results,'count':len(results)})

    except Exception as e:

        return jsonify({'error':str(e)}),500





@app.route('/api/echo/sessions')

def api_echo_sessions():

    try:

        bot = get_chat_bot()

        idx = _load_sessions_index()

        sessions = []

        # merge in-memory sessions with persisted metadata

        for sid, msgs in bot.conversation_history.items():

            meta = idx.get(sid, {})

            meta.setdefault('session_id', sid)

            meta.setdefault('title', sid)

            meta.setdefault('last_updated', None)

            meta.setdefault('created', None)

            meta.setdefault('favorite', False)

            sessions.append(meta)

        # include persisted sessions not currently in memory

        for sid, meta in idx.items():

            if sid not in bot.conversation_history:

                sessions.append(meta)

        # sort favorites first, then by last_updated desc

        def sort_key(m):

            fav = 0 if m.get('favorite') else 1

            lu = m.get('last_updated') or ''

            return (fav, lu)

        sessions = sorted(sessions, key=sort_key)

        return jsonify({'sessions': sessions})

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@app.route('/api/echo/session/<session_id>', methods=['GET','DELETE'])

def api_echo_session(session_id):

    try:

        bot = get_chat_bot()

        if request.method == 'GET':

            # prefer persisted storage for full history

            storage = get_storage()

            history = storage.get_conversation_history(user='web_user', limit=1000, channel=session_id)

            # fall back to in-memory bot history if none

            if not history:

                history = bot.get_conversation_history(session_id)

            return jsonify({'session_id': session_id, 'history': history})

        else:

            bot.clear_conversation(session_id)

            # remove persisted messages for this session

            try:

                storage = get_storage()

                storage.delete_conversation(session_id)

            except Exception:

                pass

            # remove from persisted index

            idx = _load_sessions_index()

            if session_id in idx:

                del idx[session_id]

                _save_sessions_index(idx)

            return jsonify({'deleted': True, 'session_id': session_id})

    except Exception as e:

        return jsonify({'error': str(e)}), 500





@app.route('/api/echo/session/favorite', methods=['POST'])

def api_echo_session_favorite():

    try:

        data = request.get_json() or {}

        sid = data.get('session_id')

        if not sid:

            return jsonify({'error':'session_id required'}),400

        idx = _load_sessions_index()

        entry = idx.get(sid, None)

        if not entry:

            # if not present, create minimal entry

            entry = {'session_id': sid, 'title': sid, 'created': datetime.now().isoformat(), 'favorite': True, 'last_updated': datetime.now().isoformat()}

            idx[sid]=entry

        else:

            entry['favorite'] = not bool(entry.get('favorite'))

            entry['last_updated'] = datetime.now().isoformat()

            idx[sid]=entry

        _save_sessions_index(idx)

        return jsonify({'ok':True,'session':entry})

    except Exception as e:

        return jsonify({'error': str(e)}),500





@app.route('/api/echo/session/create', methods=['POST'])

def api_echo_session_create():

    try:

        data = request.get_json() or {}

        sid = data.get('session_id') or f"web_{int(time.time()*1000)}"

        title = data.get('title') or sid

        entry = _upsert_session_meta(sid, title=title)

        return jsonify({'ok':True,'session':entry})

    except Exception as e:

        return jsonify({'error': str(e)}),500





@app.route('/debug/fetch_model')

def debug_fetch_model():

    """Serve a tiny page that fetches /api/echo/model and displays result.

    Use this from your browser to determine whether client JS can reach the API.

    """

    html = """

    <html><head><title>Debug: fetch /api/echo/model</title></head>

    <body>

    <h3>Debug: fetch /api/echo/model</h3>

    <pre id="out">Running...</pre>

    <script>

    fetch('/api/echo/model').then(r=>r.json()).then(j=>{

        document.getElementById('out').textContent = JSON.stringify(j, null, 2);

    }).catch(e=>{

        document.getElementById('out').textContent = 'Fetch failed: '+e;

        console.error('Fetch failed',e);

    });

    </script>

    </body></html>

    """

    return html





@app.route('/personality')

def personality_list():

    pdir = Path(__file__).resolve().parent / 'data' / 'personality'

    pdir.mkdir(parents=True, exist_ok=True)

    files = [f.name for f in pdir.glob('*') if f.is_file()]

    html_out = '<html><body><h3>Personality Files</h3><ul>'

    for fn in files:

        html_out += f'<li>{html.escape(fn)} - <a href="/personality/edit?id={html.escape(fn)}">Edit</a></li>'

    html_out += '</ul><p><a href="/resources">Back</a></p></body></html>'

    return html_out





@app.route('/personality/edit')

def personality_edit():

    fid = request.args.get('id')

    if not fid:

        return 'id required', 400

    pdir = Path(__file__).resolve().parent / 'data' / 'personality'

    pfile = pdir / fid

    if not pfile.exists():

        return 'not found', 404

    try:

        text = pfile.read_text(encoding='utf-8')

    except Exception:

        text = ''

    return f'''<html><body>

    <h3>Edit personality: {html.escape(fid)}</h3>

    <form method="post" action="/personality/save">

    <input type="hidden" name="id" value="{html.escape(fid)}">

    <textarea name="content" style="width:80%;height:400px;">{html.escape(text)}</textarea><br>

    <button type="submit">Save</button>

    </form>

    <p><a href="/personality">Back</a></p>

    </body></html>'''





@app.route('/personality/save', methods=['POST'])

def personality_save():

    fid = request.form.get('id')

    content = request.form.get('content') or ''

    if not fid:

        return jsonify({'error': 'id required'}), 400

    pdir = Path(__file__).resolve().parent / 'data' / 'personality'

    pdir.mkdir(parents=True, exist_ok=True)

    pfile = pdir / fid

    try:

        pfile.write_text(content, encoding='utf-8')

        return redirect(url_for('personality_list'))

    except Exception as e:

        app.logger.exception('Failed to save personality')

        return jsonify({'error': str(e)}), 500





@app.route('/web_ide')

def web_ide():

    """Serve a local `web_ide.html` file if present to restore the Web IDE quickly.

    Falls back to the root index if the file is missing.

    """

    try:

        p = Path(__file__).resolve().parent / 'web_ide.html'

        if p.exists():

            return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/html; charset=utf-8'}

    except Exception:

        app.logger.exception('Failed to serve web_ide.html')

    # Fall back to main index route if available

    try:

        return redirect(url_for('index'))

    except Exception:

        return ('Web IDE not available', 404)

# --- Manager Portal (external, module-level definitions) --------------------

_manager_tasks_file = Path(__file__).resolve().parent / 'data' / 'manager_tasks.json'

_manager_tests_file = Path(__file__).resolve().parent / 'data' / 'manager_last_test.json'



def _load_manager_tasks():

    try:

        if not _manager_tasks_file.exists():

            return []

        return json.loads(_manager_tasks_file.read_text(encoding='utf-8') or '[]')

    except Exception:

        app.logger.exception('Failed to load manager tasks')

        return []



def _save_manager_tasks(tasks):

    try:

        _manager_tasks_file.parent.mkdir(parents=True, exist_ok=True)

        _manager_tasks_file.write_text(json.dumps(tasks, indent=2), encoding='utf-8')

        return True

    except Exception:

        app.logger.exception('Failed to save manager tasks')

        return False





@app.route('/manager')

def manager_dashboard():

    html_page = '''<!doctype html>

<html><head><meta charset="utf-8"><title>Manager Portal</title>

<style>body{font-family:Arial,Helvetica,sans-serif;margin:0;padding:0;background:#f5f7fb}.top{padding:12px;background:#1f2937;color:#fff;display:flex;align-items:center;justify-content:space-between}.container{display:flex;gap:16px;padding:16px}.kanban{flex:1;display:flex;gap:12px}.col{background:#fff;border-radius:6px;padding:8px;min-width:260px;box-shadow:0 2px 6px rgba(0,0,0,.06)}.col h3{margin:6px 0;font-size:14px}.card{background:#f8fafc;margin:8px 0;padding:8px;border-radius:4px;cursor:grab}.card.dragging{opacity:.5}.sidebar{width:360px}.section{background:#fff;padding:12px;border-radius:6px;box-shadow:0 2px 6px rgba(0,0,0,.04);margin-bottom:12px}.btn{display:inline-block;padding:8px 10px;background:#2563eb;color:#fff;border-radius:4px;text-decoration:none}label{display:block;margin-top:8px;font-size:13px}input,textarea,select{width:100%;padding:8px;margin-top:4px;border:1px solid #e5e7eb;border-radius:4px}</style></head><body>

<div class="top"><div style="font-weight:700">Manager Portal</div><div><a href="/" style="color:#fff;text-decoration:none">Back to Dashboard</a></div></div>

<div class="container"><div class="kanban"><div class="col" data-status="todo"><h3>To Do</h3><div class="cards" id="col-todo"></div></div><div class="col" data-status="inprogress"><h3>In Progress</h3><div class="cards" id="col-inprogress"></div></div><div class="col" data-status="done"><h3>Done</h3><div class="cards" id="col-done"></div></div></div>

<div class="sidebar"><div class="section"><h4>Create Task</h4><label>Title<input id="task-title"></label><label>Assignee<input id="task-assignee"></label><label>Description<textarea id="task-desc"></textarea></label><label>Priority<select id="task-priority"><option>low</option><option selected>medium</option><option>high</option></select></label><div style="margin-top:8px"><a id="create-task" class="btn">Create</a></div></div>

<div class="section"><h4>Model Manager</h4><div id="models-list">Loading models...</div><label>Model path (or filename)<input id="model-input" placeholder="models/Phi-3-mini-4k-instruct-q4.gguf"></label><div style="margin-top:8px"><a id="preload-model" class="btn">Set Default Model</a></div></div>

<div class="section"><h4>Test Runner</h4><div id="test-status">No test run yet.</div><div style="margin-top:8px"><a id="run-tests" class="btn">Run Tests</a></div><pre id="test-output" style="height:160px;overflow:auto;background:#0f172a;color:#e6eef8;padding:8px;border-radius:4px;margin-top:8px"></pre></div></div></div>

<script>

async function api(path, opts){const res = await fetch(path, opts); return res.json();}

function el(html){const d=document.createElement('div');d.innerHTML=html.trim();return d.firstChild}

let dragged=null;

function renderCard(t){const node = el(`<div class="card" draggable="true" data-id="${t.id}"><strong>${t.title}</strong><div style="font-size:12px;color:#555">${t.assignee||''} • ${t.priority}</div><div style="margin-top:6px;font-size:13px">${(t.description||'').slice(0,200)}</div></div>`);node.addEventListener('dragstart',e=>{dragged=node;node.classList.add('dragging')});node.addEventListener('dragend',e=>{dragged=null;node.classList.remove('dragging')});node.addEventListener('dblclick',async e=>{const newTitle=prompt('Edit title',t.title); if(newTitle!==null){t.title=newTitle; await fetch('/api/manager/tasks',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(t)}); loadTasks();}});return node;}

async function loadTasks(){const j = await api('/api/manager/tasks');['todo','inprogress','done'].forEach(s=>document.getElementById('col-'+s).innerHTML='');j.forEach(t=>{document.getElementById('col-'+(t.status||'todo')).appendChild(renderCard(t))});}

document.querySelectorAll('.col').forEach(col=>{col.addEventListener('dragover',e=>e.preventDefault());col.addEventListener('drop',async e=>{e.preventDefault(); if(!dragged) return; const id=dragged.dataset.id; const status=col.dataset.status; await fetch('/api/manager/tasks',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,status})}); loadTasks();});});

document.getElementById('create-task').addEventListener('click',async e=>{const title=document.getElementById('task-title').value.trim(); if(!title) return alert('Title required');const payload={title,assignee:document.getElementById('task-assignee').value,description:document.getElementById('task-desc').value,priority:document.getElementById('task-priority').value,status:'todo'};await fetch('/api/manager/tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); document.getElementById('task-title').value=''; document.getElementById('task-desc').value=''; loadTasks();});

async function loadModels(){const j = await api('/api/manager/models');const node = document.getElementById('models-list'); node.innerHTML='';node.appendChild(el('<div style="font-size:13px;margin-bottom:8px">Available models:</div>'));j.models.forEach(m=>{const row=el(`<div style="margin-bottom:6px"><code style="font-size:12px">${m}</code> ${j.default===m?'<strong>(default)</strong>':''} <button data-m="${m}" class="btn" style="background:#0ea5a4;margin-left:8px">Use</button></div>`); row.querySelector('button').addEventListener('click',async ()=>{document.getElementById('model-input').value=m}); node.appendChild(row)});}

document.getElementById('preload-model').addEventListener('click',async ()=>{const model=document.getElementById('model-input').value.trim(); if(!model) return alert('model path required'); const j=await api('/api/manager/models/preload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model})}); alert(j.ok? 'Default model set' : ('Error: '+(j.error||'unknown'))); loadModels();});

document.getElementById('run-tests').addEventListener('click',async ()=>{document.getElementById('test-status').innerText='Queued...'; const r=await api('/api/manager/run_tests',{method:'POST'}); if(!r.ok){document.getElementById('test-status').innerText='Failed to start'; return;} pollTests();});

async function pollTests(){document.getElementById('test-status').innerText='Running...'; const j=await api('/api/manager/run_tests/status'); if(j.running){document.getElementById('test-output').innerText=j.output||''; setTimeout(pollTests,2000); return;} document.getElementById('test-status').innerText='Last run: '+(j.finished_at||''); document.getElementById('test-output').innerText=j.output||'';}

loadTasks(); loadModels(); pollTests();

</script></body></html>'''

    return html_page





@app.route('/api/manager/tasks', methods=['GET','POST','PUT','DELETE'])

def api_manager_tasks():

    try:

        if request.method == 'GET':

            return jsonify(_load_manager_tasks())

        data_in = request.get_json(silent=True) or {}

        tasks = _load_manager_tasks()

        if request.method == 'POST':

            new = {

                'id': str(uuid.uuid4()),

                'title': data_in.get('title') or 'Untitled',

                'description': data_in.get('description') or '',

                'assignee': data_in.get('assignee') or '',

                'priority': data_in.get('priority') or 'medium',

                'status': data_in.get('status') or 'todo',

                'created_at': datetime.utcnow().isoformat()

            }

            tasks.append(new)

            _save_manager_tasks(tasks)

            return jsonify(new)

        if request.method == 'PUT':

            tid = data_in.get('id')

            if not tid:

                return jsonify({'error':'id required'}), 400

            updated=False

            for t in tasks:

                if t.get('id')==tid:

                    # update allowed fields

                    for k in ('title','description','assignee','priority','status'):

                        if k in data_in:

                            t[k]=data_in[k]

                    t['updated_at']=datetime.utcnow().isoformat()

                    updated=True

                    break

            if not updated:

                return jsonify({'error':'task not found'}), 404

            _save_manager_tasks(tasks)

            return jsonify({'ok':True})

        if request.method == 'DELETE':

            tid = request.args.get('id')

            if not tid:

                return jsonify({'error':'id required'}), 400

            tasks=[t for t in tasks if t.get('id')!=tid]

            _save_manager_tasks(tasks)

            return jsonify({'ok':True})

    except Exception as e:

        app.logger.exception('Manager tasks error')

        return jsonify({'error': str(e)}), 500





@app.route('/api/manager/models', methods=['GET'])

def api_manager_models():

    try:

        models_dir = Path.cwd() / 'models'

        models = []

        if models_dir.exists():

            for p in sorted(models_dir.glob('*')):

                if p.is_file():

                    models.append(str(p.relative_to(Path.cwd())))

        default = None

        cfg = Path(__file__).parent / 'data' / 'echo_model.json'

        if cfg.exists():

            try:

                default = json.loads(cfg.read_text(encoding='utf-8')).get('model')

                if default and default.startswith(str(Path.cwd())):

                    default = str(Path(default).relative_to(Path.cwd()))

            except Exception:

                app.logger.exception('Failed reading default model')

        return jsonify({'models': models, 'default': default})

    except Exception as e:

        app.logger.exception('Failed to list models')

        return jsonify({'error': str(e)}), 500





@app.route('/api/manager/models/preload', methods=['POST'])

def api_manager_models_preload():

    try:

        data_in = request.get_json(silent=True) or {}

        model = data_in.get('model')

        if not model:

            return jsonify({'error':'model required'}), 400

        # resolve to absolute path

        p = Path(model)

        if not p.is_absolute():

            p = Path.cwd() / model

        if not p.exists():

            return jsonify({'error':'model not found', 'path': str(p)}), 404

        cfg = Path(__file__).parent / 'data' / 'echo_model.json'

        cfg.parent.mkdir(parents=True, exist_ok=True)

        cfg.write_text(json.dumps({'model': str(p)}), encoding='utf-8')

        return jsonify({'ok':True, 'model': str(p)})

    except Exception as e:

        app.logger.exception('Failed to set default model')

        return jsonify({'error': str(e)}), 500





def _run_tests_background():

    try:

        _manager_tests_file.parent.mkdir(parents=True, exist_ok=True)

        start = datetime.utcnow().isoformat()

        _manager_tests_file.write_text(json.dumps({'running': True, 'started_at': start}), encoding='utf-8')

        cmd = [sys.executable, '-m', 'pytest', '-q']

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=str(Path(__file__).parent))

        out, _ = proc.communicate()

        output = out.decode('utf-8', errors='replace') if out else ''

        finished = datetime.utcnow().isoformat()

        _manager_tests_file.write_text(json.dumps({'running': False, 'started_at': start, 'finished_at': finished, 'exit_code': proc.returncode, 'output': output}), encoding='utf-8')

    except Exception:

        app.logger.exception('Test runner failed')

        _manager_tests_file.write_text(json.dumps({'running': False, 'error': 'runner failure'}), encoding='utf-8')





@app.route('/api/manager/run_tests', methods=['POST'])

def api_manager_run_tests():

    try:

        # start background thread

        t = threading.Thread(target=_run_tests_background, daemon=True)

        t.start()

        return jsonify({'ok': True})

    except Exception as e:

        app.logger.exception('Failed to start tests')

        return jsonify({'error': str(e)}), 500





@app.route('/api/manager/run_tests/status', methods=['GET'])

def api_manager_run_tests_status():

    try:

        if not _manager_tests_file.exists():

            return jsonify({'running': False})

        return jsonify(json.loads(_manager_tests_file.read_text(encoding='utf-8') or '{}'))

    except Exception as e:

        app.logger.exception('Failed to read test status')

        return jsonify({'error': str(e)}), 500


@app.route('/web_tf_wizard')
def web_tf_wizard():
    """Serve the TF Wizard static page if present (append-only safe route)."""
    try:
        p = Path(__file__).resolve().parent / 'web_tf_wizard.html'
        if p.exists():
            return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception:
        app.logger.exception('Failed to serve web_tf_wizard.html')
    return redirect(url_for('web_ide'))



if __name__=='__main__':

    import argparse

    parser=argparse.ArgumentParser(description='MasterChief DevOps Platform')

    parser.add_argument('--debug',action='store_true',help='Run in debug mode')

    parser.add_argument('--port',type=int,default=8080,help='Port to run on (default: 8080)')

    args=parser.parse_args()

    print('='*70)

    print('MasterChief DevOps Platform')

    print('='*70)

    print(f'Dashboard: http://localhost:{args.port}')

    if args.debug:

        print('⚠️  Running in DEBUG mode - Not for production!')

    print('='*70)

    # perform runtime chat initialization (load model if configured)

    try:

        init_chat()

    except Exception:

        app.logger.exception('Startup chat initialization failed')

    app.run(host='0.0.0.0',port=args.port,debug=args.debug)

