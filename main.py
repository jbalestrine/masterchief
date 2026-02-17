#!/usr/bin/env python3

"""MasterChief Flask Web Application - All-in-One File"""

import sys
print("DEBUG: main.py is starting", file=sys.stderr)

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

# Import feature manager (before sys.path manipulation)
try:
    import sys
    import os
    _current_dir = os.getcwd()
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from features.manager import init_feature_manager, get_feature_manager
    import importlib
    import features.manager
    importlib.reload(features.manager)
    from features.manager import init_feature_manager, get_feature_manager
    with open('debug.log', 'a') as f:
        f.write(f"DEBUG: Successfully imported init_feature_manager from features.manager, module file: {init_feature_manager.__module__}\n")
    FEATURE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Failed to initialize feature manager: {e}")
    FEATURE_MANAGER_AVAILABLE = False

import json

import time

import difflib

import threading

import uuid

import io

import tempfile

from pathlib import Path

import psutil

import subprocess

import zipfile

import shutil

import html

from datetime import datetime

from werkzeug.utils import secure_filename

import base64

import hashlib

import requests

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None



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

        if sys.platform.startswith('win'):

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
    from auth_module import init_auth, requires_permission
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
    print(f"WARNING: Failed to initialize setup wizard: {e}")
    SETUP_WIZARD_AVAILABLE = False

# Import feature manager
try:
    print("DEBUG: About to import feature manager")
    from features.manager import init_feature_manager, get_feature_manager
    print("DEBUG: Feature manager imported successfully")
    FEATURE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Failed to initialize feature manager: {e}")
    FEATURE_MANAGER_AVAILABLE = False

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash, get_flashed_messages, send_file

from flask_cors import CORS

from flask_login import login_required

# Import TF Wizard modules
try:
    import sys
    import os
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from tf_wizard.generator import generate_module_zip, tf_type_from_spec
    import tf_wizard.app as tf_wizard_app
    TF_WIZARD_AVAILABLE = True
    print("SUCCESS: TF Wizard modules imported successfully")
except ImportError as e:
    print(f"WARNING: TF Wizard not available: {e}")
    TF_WIZARD_AVAILABLE = False
    import traceback
    print(f"TF Wizard import traceback: {traceback.format_exc()}")

app=Flask(__name__)

app.config['SECRET_KEY']='masterchief-secret-key-change-in-production'

CORS(app)

# Mount TF Wizard static files if available
if TF_WIZARD_AVAILABLE:
    from flask import send_from_directory
    import os
    tf_wizard_static = os.path.join(os.path.dirname(tf_wizard_app.__file__), 'static')
    @app.route('/tf_wizard/static/<path:filename>')
    def tf_wizard_static_files(filename):
        return send_from_directory(tf_wizard_static, filename)

app.jinja_env.filters['b64encode'] = lambda s: base64.urlsafe_b64encode(s.encode()).decode()

app.config['ADMIN_TOKEN'] = os.environ.get('ADMIN_TOKEN') or None

app.config['BASIC_AUTH_USER'] = os.environ.get('BASIC_AUTH_USER') or None

app.config['BASIC_AUTH_PASS'] = os.environ.get('BASIC_AUTH_PASS') or None

_data_dir=Path(__file__).parent/'data'

app.config['UPLOAD_FOLDER']=_data_dir/'uploads'

app.config['SCRIPTS_FOLDER']=_data_dir/'scripts'

app.config['MAX_CONTENT_LENGTH']=100*1024*1024

app.config['RBAC_DB'] = _data_dir / 'rbac.json'
app.config['VAULT_DB'] = _data_dir / 'vault.json'
app.config['VAULT_KEY'] = _data_dir / 'vault.key'
app.config['NOTIFICATIONS_DB'] = _data_dir / 'notifications.json'
app.config['NOTIFICATION_CHANNELS_DB'] = _data_dir / 'notification_channels.json'
app.config['NOTIFICATION_RULES_DB'] = _data_dir / 'notification_rules.json'
app.config['PIPELINES_DB'] = _data_dir / 'pipelines.json'
app.config['PIPELINE_RUNS_DB'] = _data_dir / 'pipeline_runs.json'
app.config['CLOUD_DB'] = _data_dir / 'cloud_accounts.json'
app.config['MARKETPLACE_DB'] = _data_dir / 'marketplace.json'
app.config['MEMORIES_PATH'] = _data_dir / 'echo_memories.jsonl'
app.config['MEMORY_INDEX_PATH'] = _data_dir / 'echo_memory_index.json'
app.config['VAULT_AUDIT_DB'] = _data_dir / 'vault_audit.json'
app.config['MODULES_CONFIG'] = _data_dir / 'modules.json'
app.config['RBAC_ENABLED'] = True

def load_enabled_modules():
    config_file = app.config['MODULES_CONFIG']
    default_modules = {
        'rbac': {'enabled': True, 'db_path': app.config['RBAC_DB']},
        'vault': {'enabled': True, 'db_path': app.config['VAULT_DB'], 'key_path': app.config['VAULT_KEY'], 'audit_path': app.config['VAULT_AUDIT_DB']},
        'notification': {'enabled': True, 'db_path': app.config['NOTIFICATIONS_DB'], 'channels_path': app.config['NOTIFICATION_CHANNELS_DB'], 'rules_path': app.config['NOTIFICATION_RULES_DB']},
        'pipeline': {'enabled': True, 'db_path': app.config['PIPELINES_DB'], 'runs_path': app.config['PIPELINE_RUNS_DB']},
        'cloud': {'enabled': True, 'db_path': app.config['CLOUD_DB']},
        'memory': {'enabled': True, 'memories_path': app.config['MEMORIES_PATH'], 'index_path': app.config['MEMORY_INDEX_PATH']},
        'marketplace': {'enabled': True, 'db_path': app.config['MARKETPLACE_DB']},
        'script': {'enabled': True}
    }
    if config_file.exists():
        try:
            loaded = json.loads(config_file.read_text())
            # Merge with defaults
            for k, v in default_modules.items():
                if k not in loaded:
                    loaded[k] = v
            return loaded
        except:
            pass
    return default_modules

ENABLED_MODULES = load_enabled_modules()

for folder in [app.config['UPLOAD_FOLDER'],app.config['SCRIPTS_FOLDER'],_data_dir]:

    folder.mkdir(parents=True,exist_ok=True)



# Initialize authentication modules if available
if AUTH_MODULES_AVAILABLE:
    try:
        # Initialize authentication
        init_auth(app)

        print("SUCCESS: Authentication modules initialized successfully")
    except Exception as e:
        print(f"WARNING: Failed to initialize authentication modules: {e}")
        AUTH_MODULES_AVAILABLE = False
else:
    print("INFO: Authentication modules not available - running without authentication")

# Initialize setup wizard if available
if SETUP_WIZARD_AVAILABLE:
    try:
        init_setup_wizard(app)
        print("SUCCESS: Setup wizard initialized successfully")
    except Exception as e:
        print(f"WARNING: Failed to initialize setup wizard: {e}")
        SETUP_WIZARD_AVAILABLE = False

# Initialize feature manager if available
with open('debug.log', 'a') as f:
    f.write(f"DEBUG: Checking FEATURE_MANAGER_AVAILABLE: {FEATURE_MANAGER_AVAILABLE}\n")
if FEATURE_MANAGER_AVAILABLE:
    with open('debug.log', 'a') as f:
        f.write("DEBUG: Initializing feature manager...\n")
    try:
        init_feature_manager(app)
        with open('debug.log', 'a') as f:
            f.write("SUCCESS: Feature manager initialized successfully\n")
    except Exception as e:
        with open('debug.log', 'a') as f:
            f.write(f"WARNING: Failed to initialize feature manager: {e}\n")
        import traceback
        with open('debug.log', 'a') as f:
            f.write(f"Traceback: {traceback.format_exc()}\n")
        FEATURE_MANAGER_AVAILABLE = False

# Manually register GitHub integration routes
try:
    from features.handlers.github_integration import register_routes
    print("DEBUG: About to call register_routes", file=sys.stderr)
    register_routes(app)
    print("DEBUG: Successfully called register_routes", file=sys.stderr)
except Exception as e:
    print(f"ERROR: Failed to register GitHub routes: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
else:
    with open('debug.log', 'a') as f:
        f.write("DEBUG: Feature manager not available\n")

with open('debug.log', 'a') as f:
    f.write("DEBUG: About to init chat...\n")



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





ENTERPRISE_TF_JOBS = {}  # job_id -> generated project path

class EnterpriseTerraformGenerator:
    """Generates enterprise-grade Terraform projects from wizard configuration."""

    def __init__(self, output_base):
        self.output_base = Path(output_base)
        self.output_base.mkdir(parents=True, exist_ok=True)

    def generate(self, config):
        """Generate a full enterprise Terraform project and return a job ID."""
        job_id = str(uuid.uuid4())[:8]
        project_name = config.get('project_name', 'enterprise-infra')
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', project_name) or 'project'
        out_dir = self.output_base / f'{safe_name}_{job_id}'
        out_dir.mkdir(parents=True, exist_ok=True)

        self._write_providers(config, out_dir)
        self._write_backend(config, out_dir)
        self._write_variables(config, out_dir)
        self._write_locals(config, out_dir)

        # Module directories
        modules_dir = out_dir / 'modules'

        # Hub module
        if config.get('topology') == 'hub-spoke':
            self._write_hub_module(config, modules_dir / 'hub')

        # Spoke modules
        for spoke in config.get('spokes', []):
            spoke_name = re.sub(r'[^a-zA-Z0-9_-]', '', spoke.get('name', 'spoke'))
            self._write_spoke_module(config, spoke, modules_dir / f'spoke_{spoke_name}')

        # AKS module
        if config.get('aks_enabled'):
            self._write_aks_module(config, modules_dir / 'aks')

        # Key Vault module
        if config.get('keyvault_enabled', True):
            self._write_keyvault_module(config, modules_dir / 'keyvault')

        # Monitoring module
        if config.get('log_analytics_enabled', True):
            self._write_monitoring_module(config, modules_dir / 'monitoring')

        # RBAC module
        if config.get('rbac_assignments'):
            self._write_rbac_module(config, modules_dir / 'rbac')

        # DR module
        if config.get('asr_enabled'):
            self._write_dr_module(config, modules_dir / 'disaster_recovery')

        # Users module (AAD groups)
        if config.get('aad_groups_enabled'):
            self._write_users_module(config, modules_dir / 'users')

        # Akamai module
        if config.get('akamai_enabled'):
            self._write_akamai_module(config, modules_dir / 'akamai')

        # VMSS module
        if config.get('vmss_enabled'):
            self._write_vmss_module(config, modules_dir / 'vmss')

        # Main.tf referencing all modules
        self._write_main(config, out_dir)

        # Outputs
        self._write_outputs(config, out_dir)

        # Environment tfvars
        self._write_environments(config, out_dir)

        # CI/CD templates
        if config.get('cicd_enabled'):
            self._write_cicd_templates(config, out_dir)

        # README
        self._write_readme(config, out_dir)

        # Create ZIP
        zip_path = out_dir.parent / f'{safe_name}_{job_id}.zip'
        shutil.make_archive(str(zip_path).replace('.zip', ''), 'zip', str(out_dir))

        ENTERPRISE_TF_JOBS[job_id] = {
            'id': job_id, 'path': str(zip_path), 'project_dir': str(out_dir),
            'name': project_name, 'created': datetime.now().isoformat()
        }
        return job_id

    def _w(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def _write_providers(self, cfg, out):
        providers = ['    azurerm = {\n      source  = "hashicorp/azurerm"\n      version = ">= 3.0"\n    }']
        providers.append('    azuread = {\n      source  = "hashicorp/azuread"\n      version = ">= 2.0"\n    }')
        providers.append('    random = {\n      source  = "hashicorp/random"\n      version = ">= 3.0"\n    }')
        if cfg.get('aks_enabled'):
            providers.append('    kubernetes = {\n      source  = "hashicorp/kubernetes"\n      version = ">= 2.0"\n    }')
        if cfg.get('akamai_enabled'):
            providers.append('    akamai = {\n      source  = "akamai/akamai"\n      version = ">= 1.0"\n    }')
        self._w(out / 'providers.tf', f"""terraform {{
  required_version = ">= 1.5"
  required_providers {{
{chr(10).join(providers)}
  }}
}}

provider "azurerm" {{
  features {{
    key_vault {{
      purge_protection_enabled = false
    }}
  }}
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}}

provider "azuread" {{
  tenant_id = var.tenant_id
}}
""")

    def _write_backend(self, cfg, out):
        backend = cfg.get('backend', {})
        if backend.get('type') == 'azurerm':
            self._w(out / 'backend.tf', f"""terraform {{
  backend "azurerm" {{
    resource_group_name  = "{backend.get('resource_group', 'tfstate-rg')}"
    storage_account_name = "{backend.get('storage_account', 'tfstatesa')}"
    container_name       = "{backend.get('container', 'tfstate')}"
    key                  = "{cfg.get('project_name', 'enterprise')}/terraform.tfstate"
  }}
}}
""")
        else:
            self._w(out / 'backend.tf', 'terraform {\n  backend "local" {\n    path = "terraform.tfstate"\n  }\n}\n')

    def _write_variables(self, cfg, out):
        region = cfg.get('region', 'eastus')
        env = cfg.get('environment', 'dev')
        self._w(out / 'variables.tf', f"""variable "subscription_id" {{
  type        = string
  description = "Azure Subscription ID"
  default     = "{cfg.get('subscription_id', '')}"
}}

variable "tenant_id" {{
  type        = string
  description = "Azure AD Tenant ID"
  default     = "{cfg.get('tenant_id', '')}"
}}

variable "environment" {{
  type        = string
  description = "Environment name (dev/test/staging/prod)"
  default     = "{env}"
}}

variable "location" {{
  type        = string
  description = "Azure region"
  default     = "{region}"
}}

variable "naming_prefix" {{
  type        = string
  description = "Naming prefix for all resources"
  default     = "{cfg.get('naming_prefix', cfg.get('project_name', 'mc'))}"
}}

variable "tags" {{
  type = map(string)
  default = {{
    Environment = "{env}"
    ManagedBy   = "terraform"
    Project     = "{cfg.get('project_name', 'masterchief')}"
  }}
}}
""")

    def _write_locals(self, cfg, out):
        prefix = cfg.get('naming_prefix', cfg.get('project_name', 'mc'))
        self._w(out / 'locals.tf', f"""locals {{
  prefix      = var.naming_prefix
  environment = var.environment
  location    = var.location
  tags        = var.tags
  hub_rg_name = "${{local.prefix}}-hub-rg"
}}
""")

    def _write_hub_module(self, cfg, mod_dir):
        hub_cidr = cfg.get('hub_cidr', '10.0.0.0/16')
        hub_subnets = cfg.get('hub_subnets', [
            {'name': 'GatewaySubnet', 'cidr': '10.0.0.0/24'},
            {'name': 'AzureFirewallSubnet', 'cidr': '10.0.1.0/24'},
            {'name': 'SharedServicesSubnet', 'cidr': '10.0.2.0/24'},
            {'name': 'ManagementSubnet', 'cidr': '10.0.3.0/24'},
        ])
        subnets_hcl = '\n'.join(f'    {{ name = "{s["name"]}", cidr = "{s["cidr"]}" }},' for s in hub_subnets)
        self._w(mod_dir / 'main.tf', f"""resource "azurerm_resource_group" "hub" {{
  name     = "${{var.prefix}}-hub-rg"
  location = var.location
  tags     = var.tags
}}

resource "azurerm_virtual_network" "hub" {{
  name                = "${{var.prefix}}-hub-vnet"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  address_space       = [var.hub_cidr]
  tags                = var.tags
}}

resource "azurerm_subnet" "hub_subnets" {{
  for_each             = {{ for s in var.hub_subnets : s.name => s }}
  name                 = each.value.name
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = [each.value.cidr]
}}

resource "azurerm_network_security_group" "hub_nsg" {{
  name                = "${{var.prefix}}-hub-nsg"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  tags                = var.tags
}}
{'' if not cfg.get('firewall_enabled') else '''
resource "azurerm_firewall" "hub" {
  name                = "${var.prefix}-hub-fw"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  sku_name            = "AZFW_VNet"
  sku_tier            = "Standard"
  ip_configuration {
    name                 = "configuration"
    subnet_id            = azurerm_subnet.hub_subnets["AzureFirewallSubnet"].id
    public_ip_address_id = azurerm_public_ip.fw_pip.id
  }
  tags = var.tags
}

resource "azurerm_public_ip" "fw_pip" {
  name                = "${var.prefix}-hub-fw-pip"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}
'''}
""")
        self._w(mod_dir / 'variables.tf', f"""variable "prefix" {{ type = string }}
variable "location" {{ type = string }}
variable "tags" {{ type = map(string) }}
variable "hub_cidr" {{
  type    = string
  default = "{hub_cidr}"
}}
variable "hub_subnets" {{
  type = list(object({{ name = string, cidr = string }}))
  default = [
{subnets_hcl}
  ]
}}
""")
        self._w(mod_dir / 'outputs.tf', """output "hub_vnet_id" { value = azurerm_virtual_network.hub.id }
output "hub_vnet_name" { value = azurerm_virtual_network.hub.name }
output "hub_rg_name" { value = azurerm_resource_group.hub.name }
output "hub_subnet_ids" { value = { for k, v in azurerm_subnet.hub_subnets : k => v.id } }
""")

    def _write_spoke_module(self, cfg, spoke, mod_dir):
        spoke_cidr = spoke.get('cidr', '10.1.0.0/16')
        spoke_subnets = spoke.get('subnets', [
            {'name': 'AKSSubnet', 'cidr': '10.1.1.0/24'},
            {'name': 'AppSubnet', 'cidr': '10.1.2.0/24'},
            {'name': 'DataSubnet', 'cidr': '10.1.3.0/24'},
        ])
        subnets_hcl = '\n'.join(f'    {{ name = "{s["name"]}", cidr = "{s["cidr"]}" }},' for s in spoke_subnets)
        self._w(mod_dir / 'main.tf', f"""resource "azurerm_resource_group" "spoke" {{
  name     = "${{var.prefix}}-${{var.spoke_name}}-rg"
  location = var.location
  tags     = var.tags
}}

resource "azurerm_virtual_network" "spoke" {{
  name                = "${{var.prefix}}-${{var.spoke_name}}-vnet"
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  address_space       = [var.spoke_cidr]
  tags                = var.tags
}}

resource "azurerm_subnet" "spoke_subnets" {{
  for_each             = {{ for s in var.spoke_subnets : s.name => s }}
  name                 = each.value.name
  resource_group_name  = azurerm_resource_group.spoke.name
  virtual_network_name = azurerm_virtual_network.spoke.name
  address_prefixes     = [each.value.cidr]
}}

resource "azurerm_network_security_group" "spoke_nsg" {{
  name                = "${{var.prefix}}-${{var.spoke_name}}-nsg"
  location            = azurerm_resource_group.spoke.location
  resource_group_name = azurerm_resource_group.spoke.name
  tags                = var.tags
}}
{"" if not spoke.get('peering', True) else '''
resource "azurerm_virtual_network_peering" "spoke_to_hub" {
  name                      = "${var.prefix}-${var.spoke_name}-to-hub"
  resource_group_name       = azurerm_resource_group.spoke.name
  virtual_network_name      = azurerm_virtual_network.spoke.name
  remote_virtual_network_id = var.hub_vnet_id
  allow_forwarded_traffic   = true
  allow_gateway_transit     = false
  use_remote_gateways       = false
}

resource "azurerm_virtual_network_peering" "hub_to_spoke" {
  name                      = "hub-to-${var.spoke_name}"
  resource_group_name       = var.hub_rg_name
  virtual_network_name      = var.hub_vnet_name
  remote_virtual_network_id = azurerm_virtual_network.spoke.id
  allow_forwarded_traffic   = true
  allow_gateway_transit     = true
  use_remote_gateways       = false
}
''' }
""")
        self._w(mod_dir / 'variables.tf', f"""variable "prefix" {{ type = string }}
variable "location" {{ type = string }}
variable "tags" {{ type = map(string) }}
variable "spoke_name" {{ type = string }}
variable "spoke_cidr" {{
  type    = string
  default = "{spoke_cidr}"
}}
variable "spoke_subnets" {{
  type = list(object({{ name = string, cidr = string }}))
  default = [
{subnets_hcl}
  ]
}}
variable "hub_vnet_id" {{ type = string; default = "" }}
variable "hub_vnet_name" {{ type = string; default = "" }}
variable "hub_rg_name" {{ type = string; default = "" }}
""")
        self._w(mod_dir / 'outputs.tf', f"""output "spoke_vnet_id" {{ value = azurerm_virtual_network.spoke.id }}
output "spoke_rg_name" {{ value = azurerm_resource_group.spoke.name }}
output "spoke_subnet_ids" {{ value = {{ for k, v in azurerm_subnet.spoke_subnets : k => v.id }} }}
""")

    def _write_aks_module(self, cfg, mod_dir):
        aks_cfg = cfg.get('aks_config', {})
        self._w(mod_dir / 'main.tf', """resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${var.prefix}-aks"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.prefix}-aks"
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = "system"
    node_count          = var.system_node_count
    vm_size             = var.system_vm_size
    enable_auto_scaling = true
    min_count           = var.system_min_count
    max_count           = var.system_max_count
    vnet_subnet_id      = var.subnet_id
    max_pods            = 110
    os_disk_size_gb     = 128
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = var.network_plugin
    network_policy    = var.network_policy
    load_balancer_sku = "standard"
    outbound_type     = "loadBalancer"
  }

  azure_active_directory_role_based_access_control {
    managed            = var.enable_aad_rbac
    azure_rbac_enabled = var.enable_aad_rbac
  }

  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  azure_policy_enabled = var.enable_azure_policy

  tags = var.tags
}
""")
        self._w(mod_dir / 'variables.tf', """variable "prefix" { type = string }
variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "tags" { type = map(string) }
variable "subnet_id" { type = string }
variable "kubernetes_version" { type = string; default = "1.29" }
variable "system_vm_size" { type = string; default = "Standard_D2s_v3" }
variable "system_node_count" { type = number; default = 3 }
variable "system_min_count" { type = number; default = 2 }
variable "system_max_count" { type = number; default = 5 }
variable "network_plugin" { type = string; default = "azure" }
variable "network_policy" { type = string; default = "azure" }
variable "enable_aad_rbac" { type = bool; default = true }
variable "enable_azure_policy" { type = bool; default = true }
variable "log_analytics_workspace_id" { type = string; default = "" }
""")
        self._w(mod_dir / 'outputs.tf', """output "aks_id" { value = azurerm_kubernetes_cluster.aks.id }
output "aks_name" { value = azurerm_kubernetes_cluster.aks.name }
output "kube_config" { value = azurerm_kubernetes_cluster.aks.kube_admin_config_raw; sensitive = true }
""")

    def _write_keyvault_module(self, cfg, mod_dir):
        kv = cfg.get('keyvault_config', {})
        self._w(mod_dir / 'main.tf', f"""data "azurerm_client_config" "current" {{}}

resource "azurerm_key_vault" "kv" {{
  name                       = "${{var.prefix}}-kv"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = {str(kv.get('purge_protection', True)).lower()}
  soft_delete_retention_days = {kv.get('soft_delete_days', 90)}
  enable_rbac_authorization  = true

  network_acls {{
    default_action = "{kv.get('default_action', 'Deny')}"
    bypass         = "AzureServices"
  }}

  tags = var.tags
}}
""")
        self._w(mod_dir / 'variables.tf', """variable "prefix" { type = string }
variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "tags" { type = map(string) }
""")
        self._w(mod_dir / 'outputs.tf', """output "key_vault_id" { value = azurerm_key_vault.kv.id }
output "key_vault_uri" { value = azurerm_key_vault.kv.vault_uri }
""")

    def _write_monitoring_module(self, cfg, mod_dir):
        self._w(mod_dir / 'main.tf', """resource "azurerm_log_analytics_workspace" "law" {
  name                = "${var.prefix}-law"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_days
  tags                = var.tags
}

resource "azurerm_log_analytics_solution" "containers" {
  count                 = var.enable_container_insights ? 1 : 0
  solution_name         = "ContainerInsights"
  location              = var.location
  resource_group_name   = var.resource_group_name
  workspace_resource_id = azurerm_log_analytics_workspace.law.id
  workspace_name        = azurerm_log_analytics_workspace.law.name
  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/ContainerInsights"
  }
}
""")
        self._w(mod_dir / 'variables.tf', """variable "prefix" { type = string }
variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "tags" { type = map(string) }
variable "retention_days" { type = number; default = 30 }
variable "enable_container_insights" { type = bool; default = true }
""")
        self._w(mod_dir / 'outputs.tf', """output "workspace_id" { value = azurerm_log_analytics_workspace.law.id }
output "workspace_key" { value = azurerm_log_analytics_workspace.law.primary_shared_key; sensitive = true }
""")

    def _write_rbac_module(self, cfg, mod_dir):
        self._w(mod_dir / 'main.tf', """resource "azurerm_role_assignment" "assignments" {
  for_each             = { for idx, a in var.assignments : idx => a }
  scope                = each.value.scope
  role_definition_name = each.value.role
  principal_id         = each.value.principal_id
}
""")
        self._w(mod_dir / 'variables.tf', """variable "assignments" {
  type = list(object({
    principal_id = string
    role         = string
    scope        = string
  }))
  default = []
}
""")
        self._w(mod_dir / 'outputs.tf', 'output "assignment_ids" { value = [for a in azurerm_role_assignment.assignments : a.id] }\n')

    def _write_dr_module(self, cfg, mod_dir):
        asr = cfg.get('asr_config', {})
        self._w(mod_dir / 'main.tf', f"""resource "azurerm_recovery_services_vault" "vault" {{
  name                = "${{var.prefix}}-asr-vault"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"
  tags                = var.tags
}}

resource "azurerm_site_recovery_fabric" "primary" {{
  name                = "primary-fabric"
  resource_group_name = var.resource_group_name
  recovery_vault_name = azurerm_recovery_services_vault.vault.name
  location            = var.source_region
}}

resource "azurerm_site_recovery_fabric" "secondary" {{
  name                = "secondary-fabric"
  resource_group_name = var.resource_group_name
  recovery_vault_name = azurerm_recovery_services_vault.vault.name
  location            = var.target_region
}}

resource "azurerm_site_recovery_replication_policy" "policy" {{
  name                                                 = "${{var.prefix}}-replication-policy"
  resource_group_name                                  = var.resource_group_name
  recovery_vault_name                                  = azurerm_recovery_services_vault.vault.name
  recovery_point_retention_in_minutes                  = {asr.get('rpo_minutes', 1440)}
  application_consistent_snapshot_frequency_in_minutes = {asr.get('snapshot_minutes', 240)}
}}
""")
        self._w(mod_dir / 'variables.tf', f"""variable "prefix" {{ type = string }}
variable "location" {{ type = string }}
variable "resource_group_name" {{ type = string }}
variable "tags" {{ type = map(string) }}
variable "source_region" {{ type = string; default = "{asr.get('source_region', 'eastus')}" }}
variable "target_region" {{ type = string; default = "{asr.get('target_region', 'westus2')}" }}
""")
        self._w(mod_dir / 'outputs.tf', 'output "vault_id" { value = azurerm_recovery_services_vault.vault.id }\n')

    def _write_users_module(self, cfg, mod_dir):
        self._w(mod_dir / 'main.tf', """resource "azuread_group" "groups" {
  for_each         = { for g in var.groups : g.name => g }
  display_name     = each.value.name
  description      = each.value.description
  security_enabled = true
}
""")
        self._w(mod_dir / 'variables.tf', """variable "groups" {
  type = list(object({
    name        = string
    description = string
  }))
  default = []
}
""")
        self._w(mod_dir / 'outputs.tf', 'output "group_ids" { value = { for k, v in azuread_group.groups : k => v.id } }\n')

    def _write_akamai_module(self, cfg, mod_dir):
        ak = cfg.get('akamai_config', {})
        self._w(mod_dir / 'main.tf', """# Akamai CDN & WAF Configuration
# Requires Akamai API credentials configured

resource "akamai_property" "cdn" {
  name        = "${var.prefix}-cdn"
  product_id  = "prd_Fresca"
  contract_id = var.contract_id
  group_id    = var.group_id

  hostnames {
    cname_from = var.edge_hostname
    cname_to   = var.origin_hostname
  }
}
""")
        self._w(mod_dir / 'variables.tf', """variable "prefix" { type = string }
variable "contract_id" { type = string; default = "" }
variable "group_id" { type = string; default = "" }
variable "edge_hostname" { type = string; default = "" }
variable "origin_hostname" { type = string; default = "" }
""")
        self._w(mod_dir / 'outputs.tf', '# Akamai outputs\n')

    def _write_vmss_module(self, cfg, mod_dir):
        vmss = cfg.get('vmss_config', {})
        self._w(mod_dir / 'main.tf', """resource "azurerm_linux_virtual_machine_scale_set" "vmss" {
  name                = "${var.prefix}-vmss"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.vm_size
  instances           = var.instance_count
  admin_username      = "adminuser"

  admin_ssh_key {
    username   = "adminuser"
    public_key = var.ssh_public_key
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  os_disk {
    storage_account_type = "Standard_LRS"
    caching              = "ReadWrite"
  }

  network_interface {
    name    = "vmss-nic"
    primary = true
    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = var.subnet_id
    }
  }

  tags = var.tags
}
""")
        self._w(mod_dir / 'variables.tf', """variable "prefix" { type = string }
variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "tags" { type = map(string) }
variable "subnet_id" { type = string }
variable "vm_size" { type = string; default = "Standard_D2s_v3" }
variable "instance_count" { type = number; default = 2 }
variable "ssh_public_key" { type = string; default = "" }
""")
        self._w(mod_dir / 'outputs.tf', 'output "vmss_id" { value = azurerm_linux_virtual_machine_scale_set.vmss.id }\n')

    def _write_main(self, cfg, out):
        lines = ['# Main module composition\n']
        if cfg.get('topology') == 'hub-spoke':
            lines.append("""module "hub" {
  source   = "./modules/hub"
  prefix   = local.prefix
  location = local.location
  tags     = local.tags
}
""")
        for spoke in cfg.get('spokes', []):
            sname = re.sub(r'[^a-zA-Z0-9_]', '', spoke.get('name', 'spoke'))
            lines.append(f"""module "spoke_{sname}" {{
  source         = "./modules/spoke_{sname}"
  prefix         = local.prefix
  location       = local.location
  tags           = local.tags
  spoke_name     = "{spoke.get('name', sname)}"
  hub_vnet_id    = {"module.hub.hub_vnet_id" if cfg.get('topology') == 'hub-spoke' else '""'}
  hub_vnet_name  = {"module.hub.hub_vnet_name" if cfg.get('topology') == 'hub-spoke' else '""'}
  hub_rg_name    = {"module.hub.hub_rg_name" if cfg.get('topology') == 'hub-spoke' else '""'}
}}
""")
        if cfg.get('log_analytics_enabled', True):
            lines.append("""module "monitoring" {
  source              = "./modules/monitoring"
  prefix              = local.prefix
  location            = local.location
  resource_group_name = module.hub.hub_rg_name
  tags                = local.tags
}
""")
        if cfg.get('keyvault_enabled', True):
            lines.append("""module "keyvault" {
  source              = "./modules/keyvault"
  prefix              = local.prefix
  location            = local.location
  resource_group_name = module.hub.hub_rg_name
  tags                = local.tags
}
""")
        if cfg.get('aks_enabled'):
            first_spoke = cfg.get('spokes', [{}])[0] if cfg.get('spokes') else {}
            sname = re.sub(r'[^a-zA-Z0-9_]', '', first_spoke.get('name', 'spoke'))
            lines.append(f"""module "aks" {{
  source                     = "./modules/aks"
  prefix                     = local.prefix
  location                   = local.location
  resource_group_name        = module.spoke_{sname}.spoke_rg_name
  subnet_id                  = module.spoke_{sname}.spoke_subnet_ids["AKSSubnet"]
  log_analytics_workspace_id = module.monitoring.workspace_id
  tags                       = local.tags
}}
""")
        if cfg.get('rbac_assignments'):
            lines.append("""module "rbac" {
  source      = "./modules/rbac"
  assignments = var.rbac_assignments
}
""")
        if cfg.get('asr_enabled'):
            lines.append("""module "disaster_recovery" {
  source              = "./modules/disaster_recovery"
  prefix              = local.prefix
  location            = local.location
  resource_group_name = module.hub.hub_rg_name
  tags                = local.tags
}
""")
        if cfg.get('aad_groups_enabled'):
            lines.append("""module "users" {
  source = "./modules/users"
  groups = var.aad_groups
}
""")
        if cfg.get('vmss_enabled'):
            lines.append("""module "vmss" {
  source              = "./modules/vmss"
  prefix              = local.prefix
  location            = local.location
  resource_group_name = module.hub.hub_rg_name
  subnet_id           = module.hub.hub_subnet_ids["SharedServicesSubnet"]
  tags                = local.tags
}
""")
        self._w(out / 'main.tf', '\n'.join(lines))

    def _write_outputs(self, cfg, out):
        lines = ['# Outputs\n']
        if cfg.get('topology') == 'hub-spoke':
            lines.append('output "hub_vnet_id" { value = module.hub.hub_vnet_id }')
        for spoke in cfg.get('spokes', []):
            sname = re.sub(r'[^a-zA-Z0-9_]', '', spoke.get('name', 'spoke'))
            lines.append(f'output "spoke_{sname}_vnet_id" {{ value = module.spoke_{sname}.spoke_vnet_id }}')
        if cfg.get('aks_enabled'):
            lines.append('output "aks_name" { value = module.aks.aks_name }')
        if cfg.get('keyvault_enabled', True):
            lines.append('output "keyvault_uri" { value = module.keyvault.key_vault_uri }')
        if cfg.get('log_analytics_enabled', True):
            lines.append('output "log_analytics_workspace_id" { value = module.monitoring.workspace_id }')
        self._w(out / 'outputs.tf', '\n'.join(lines) + '\n')

    def _write_environments(self, cfg, out):
        envs_dir = out / 'environments'
        for env in ('dev', 'test', 'staging', 'prod'):
            content = f"""environment    = "{env}"
location       = "{cfg.get('region', 'eastus')}"
naming_prefix  = "{cfg.get('naming_prefix', 'mc')}-{env}"
"""
            self._w(envs_dir / f'{env}.tfvars', content)

    def _write_cicd_templates(self, cfg, out):
        cicd_dir = out / 'cicd'
        platform = cfg.get('cicd_platform', 'github')
        if platform == 'github':
            self._w(cicd_dir / '.github' / 'workflows' / 'terraform.yml', """name: Terraform CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.5.0"
      - name: Terraform Init
        run: terraform init
      - name: Terraform Format Check
        run: terraform fmt -check
      - name: Terraform Plan
        if: github.event_name == 'pull_request'
        run: terraform plan -var-file=environments/${{ github.event.pull_request.base.ref == 'main' && 'prod' || 'dev' }}.tfvars -no-color
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve -var-file=environments/prod.tfvars
""")
        else:
            self._w(cicd_dir / 'azure-pipelines.yml', """trigger:
  branches:
    include: [main]

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Plan
    jobs:
      - job: TerraformPlan
        steps:
          - task: TerraformInstaller@0
            inputs:
              terraformVersion: '1.5.0'
          - task: TerraformTaskV4@4
            inputs:
              command: 'init'
          - task: TerraformTaskV4@4
            inputs:
              command: 'plan'
              commandOptions: '-var-file=environments/prod.tfvars'
  - stage: Apply
    dependsOn: Plan
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: TerraformApply
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: TerraformTaskV4@4
                  inputs:
                    command: 'apply'
                    commandOptions: '-auto-approve -var-file=environments/prod.tfvars'
""")

    def _write_readme(self, cfg, out):
        spokes = ', '.join(s.get('name', 'spoke') for s in cfg.get('spokes', []))
        modules = []
        if cfg.get('topology') == 'hub-spoke':
            modules.append('Hub Network')
        if cfg.get('spokes'):
            modules.append(f'Spokes: {spokes}')
        if cfg.get('aks_enabled'):
            modules.append('AKS Kubernetes')
        if cfg.get('keyvault_enabled', True):
            modules.append('Key Vault')
        if cfg.get('log_analytics_enabled', True):
            modules.append('Log Analytics')
        if cfg.get('asr_enabled'):
            modules.append('Disaster Recovery')
        if cfg.get('aad_groups_enabled'):
            modules.append('Azure AD Groups')
        if cfg.get('vmss_enabled'):
            modules.append('VM Scale Sets')
        if cfg.get('akamai_enabled'):
            modules.append('Akamai CDN/WAF')
        self._w(out / 'README.md', f"""# {cfg.get('project_name', 'Enterprise Infrastructure')}

Generated by MasterChief Enterprise Terraform Wizard.

## Architecture
- Topology: {cfg.get('topology', 'hub-spoke')}
- Region: {cfg.get('region', 'eastus')}
- Environment: {cfg.get('environment', 'dev')}

## Modules
{chr(10).join(f'- {m}' for m in modules)}

## Usage
```bash
terraform init
terraform plan -var-file=environments/dev.tfvars
terraform apply -var-file=environments/dev.tfvars
```

## Environments
- dev.tfvars / test.tfvars / staging.tfvars / prod.tfvars
""")

    def validate(self, config):
        """Validate configuration and return issues."""
        issues = []
        # Check CIDRs
        cidrs = []
        if config.get('hub_cidr'):
            cidrs.append(('Hub', config['hub_cidr']))
        for spoke in config.get('spokes', []):
            if spoke.get('cidr'):
                cidrs.append((spoke.get('name', 'Spoke'), spoke['cidr']))
        # Basic CIDR overlap check
        for i, (n1, c1) in enumerate(cidrs):
            for j, (n2, c2) in enumerate(cidrs):
                if i < j:
                    if self._cidrs_overlap(c1, c2):
                        issues.append({'severity': 'error', 'message': f'CIDR overlap: {n1} ({c1}) overlaps with {n2} ({c2})'})
        # Naming
        if not config.get('project_name'):
            issues.append({'severity': 'error', 'message': 'Project name is required'})
        if not config.get('subscription_id'):
            issues.append({'severity': 'warning', 'message': 'Subscription ID not set — required for deployment'})
        if not config.get('tenant_id'):
            issues.append({'severity': 'warning', 'message': 'Tenant ID not set — required for Azure AD operations'})
        # Best practices
        if config.get('keyvault_config', {}).get('default_action') == 'Allow':
            issues.append({'severity': 'warning', 'message': 'Key Vault network ACL set to Allow — Deny recommended for production'})
        if config.get('environment') == 'prod' and not config.get('asr_enabled'):
            issues.append({'severity': 'info', 'message': 'Production environment without DR — consider enabling Azure Site Recovery'})
        if not issues:
            issues.append({'severity': 'success', 'message': 'All validations passed'})
        return issues

    def _cidrs_overlap(self, cidr1, cidr2):
        try:
            def cidr_to_range(cidr):
                parts = cidr.split('/')
                ip_parts = list(map(int, parts[0].split('.')))
                ip_int = (ip_parts[0] << 24) + (ip_parts[1] << 16) + (ip_parts[2] << 8) + ip_parts[3]
                mask = (0xFFFFFFFF << (32 - int(parts[1]))) & 0xFFFFFFFF
                start = ip_int & mask
                end = start + (~mask & 0xFFFFFFFF)
                return start, end
            s1, e1 = cidr_to_range(cidr1)
            s2, e2 = cidr_to_range(cidr2)
            return s1 <= e2 and s2 <= e1
        except Exception:
            return False

enterprise_tf_gen = EnterpriseTerraformGenerator(_data_dir / 'terraform_enterprise')


# ---------------------------------------------------------------------------
#  Enterprise TF Wizard Routes
# ---------------------------------------------------------------------------

@app.route('/api/terraform/enterprise/generate', methods=['POST'])
def api_tf_enterprise_generate():
    try:
        config = request.get_json(silent=True) or {}
        job_id = enterprise_tf_gen.generate(config)
        return jsonify({'ok': True, 'result': {'job_id': job_id, 'download_url': f'/api/terraform/enterprise/download/{job_id}'}})
    except Exception as e:
        app.logger.exception('Enterprise TF generation failed')
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/terraform/enterprise/validate', methods=['POST'])
def api_tf_enterprise_validate():
    try:
        config = request.get_json(silent=True) or {}
        issues = enterprise_tf_gen.validate(config)
        return jsonify({'ok': True, 'result': issues})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/terraform/enterprise/download/<job_id>', methods=['GET'])
def api_tf_enterprise_download(job_id):
    try:
        job = ENTERPRISE_TF_JOBS.get(job_id)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        zip_path = Path(job['path'])
        if zip_path.exists():
            return send_file(str(zip_path), as_attachment=True, download_name=zip_path.name)
        return jsonify({'ok': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/terraform/enterprise/deploy_to_project', methods=['POST'])
def api_tf_enterprise_deploy_to_project():
    try:
        config = request.get_json(silent=True) or {}
        job_id = enterprise_tf_gen.generate(config)
        job = ENTERPRISE_TF_JOBS[job_id]
        return jsonify({'ok': True, 'result': {'job_id': job_id, 'project_dir': job['project_dir']}})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


###############################################################################





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

    return jsonify({'ok': True, 'hooks': hooks})





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

        # Check if this is a direct file path (web IDE) or script name (legacy)

        if '/' in filename or '\\' in filename:

            # Web IDE: save directly to project

            base_path = Path(__file__).parent

            file_path = (base_path / filename).resolve()

            # Security check

            if not file_path.is_relative_to(base_path):

                return jsonify({'ok': False, 'error': 'Access denied'}), 403

            # Create directory if needed

            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file

            file_path.write_text(content, encoding='utf-8')

        else:

            # Legacy: use script manager

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

                    if sys.platform.startswith('win'):

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





@app.route('/api/vault/secrets', methods=['GET'])
def api_vault_list():
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': vault_mgr.list_secrets()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/vault/secrets', methods=['POST'])
def api_vault_create():
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        secret = vault_mgr.create_secret(d.get('name', ''), d.get('value', ''), d.get('type', 'other'), d.get('rotation_days', 0))
        return jsonify({'ok': True, 'result': secret})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/vault/secrets/<sid>', methods=['GET'])
def api_vault_get(sid):
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': vault_mgr.get_secret(sid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404

@app.route('/api/vault/secrets/<sid>', methods=['PUT'])
def api_vault_update(sid):
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        secret = vault_mgr.update_secret(sid, value=d.get('value'), rotation_days=d.get('rotation_days'))
        return jsonify({'ok': True, 'result': secret})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/vault/secrets/<sid>', methods=['DELETE'])
def api_vault_delete(sid):
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        vault_mgr.delete_secret(sid)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/vault/secrets/<sid>/versions', methods=['GET'])
def api_vault_versions(sid):
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': vault_mgr.get_versions(sid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/vault/audit', methods=['GET'])
def api_vault_audit():
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        limit = request.args.get('limit', 100, type=int)
        return jsonify({'ok': True, 'result': vault_mgr.get_audit_log(limit)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/vault/rotation', methods=['GET'])
def api_vault_rotation():
    if not vault_mgr:
        return jsonify({'ok': False, 'error': 'Vault manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': vault_mgr.check_rotation()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500





@app.route('/api/echo/memories', methods=['GET'])
def api_echo_memories_list():
    try:
        topic = request.args.get('topic')
        q = request.args.get('q')
        pinned = request.args.get('pinned', '').lower() == 'true'
        return jsonify({'ok': True, 'result': memory_mgr.get_all(topic=topic, pinned_only=pinned, query=q)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/echo/memories', methods=['POST'])
def api_echo_memories_create():
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        topics = d.get('topics', [])
        if isinstance(topics, str):
            topics = [t.strip() for t in topics.split(',') if t.strip()]
        entities = d.get('entities', [])
        if isinstance(entities, str):
            entities = [e.strip() for e in entities.split(',') if e.strip()]
        memory = memory_mgr.add_memory(
            content=d.get('content', ''),
            topics=topics, entities=entities,
            source=d.get('source', 'manual'),
            importance=d.get('importance', 0.5)
        )
        return jsonify({'ok': True, 'result': memory})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/echo/memories/<mid>', methods=['GET'])
def api_echo_memories_get(mid):
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        m = memory_mgr.get_memory(mid)
        if m:
            return jsonify({'ok': True, 'result': m})
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/echo/memories/<mid>', methods=['PUT'])
def api_echo_memories_update(mid):
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        m = memory_mgr.update_memory(mid, d)
        return jsonify({'ok': True, 'result': m})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/echo/memories/<mid>', methods=['DELETE'])
def api_echo_memories_delete(mid):
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        memory_mgr.delete_memory(mid)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/echo/memories/<mid>/pin', methods=['POST'])
def api_echo_memories_pin(mid):
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        m = memory_mgr.toggle_pin(mid)
        return jsonify({'ok': True, 'result': m})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/echo/memories/search', methods=['GET'])
def api_echo_memories_search():
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        q = request.args.get('q', '')
        return jsonify({'ok': True, 'result': memory_mgr.search(q)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/echo/memories/topics', methods=['GET'])
def api_echo_memories_topics():
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': memory_mgr.get_topics()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/echo/memories/context', methods=['POST'])
def api_echo_memories_context():
    if not memory_mgr:
        return jsonify({'ok': False, 'error': 'Memory manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        return jsonify({'ok': True, 'result': memory_mgr.get_context_for_conversation(d.get('message', ''))})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ---------------------------------------------------------------------------
#  Pipeline API Routes
# ---------------------------------------------------------------------------

@app.route('/api/pipelines', methods=['GET'])
def api_pipelines_list():
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': pipeline_mgr.list_pipelines()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/pipelines', methods=['POST'])
def api_pipelines_create():
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        pipeline = pipeline_mgr.create_pipeline(d.get('name', 'New Pipeline'), d.get('description', ''))
        return jsonify({'ok': True, 'result': pipeline})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/pipelines/<pid>', methods=['GET'])
def api_pipelines_get(pid):
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': pipeline_mgr.get_pipeline(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404

@app.route('/api/pipelines/<pid>', methods=['PUT'])
def api_pipelines_update(pid):
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        pipeline = pipeline_mgr.update_pipeline(pid, d)
        return jsonify({'ok': True, 'result': pipeline})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/pipelines/<pid>', methods=['DELETE'])
def api_pipelines_delete(pid):
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        pipeline_mgr.delete_pipeline(pid)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/pipelines/<pid>/execute', methods=['POST'])
def api_pipelines_execute(pid):
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        run = pipeline_mgr.execute_pipeline(pid)
        return jsonify({'ok': True, 'result': run})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/pipelines/runs', methods=['GET'])
def api_pipeline_runs_list():
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        pid = request.args.get('pipeline_id')
        return jsonify({'ok': True, 'result': pipeline_mgr.get_runs(pipeline_id=pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/pipelines/runs/<rid>', methods=['GET'])
def api_pipeline_runs_get(rid):
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': pipeline_mgr.get_run(rid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404

@app.route('/api/pipelines/runs/<rid>/cancel', methods=['POST'])
def api_pipeline_runs_cancel(rid):
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        run = pipeline_mgr.cancel_run(rid)
        return jsonify({'ok': True, 'result': run})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/pipelines/import', methods=['POST'])
def api_pipelines_import():
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        d.pop('id', None)
        d['id'] = str(uuid.uuid4())
        d['created'] = datetime.now().isoformat()
        d['updated'] = datetime.now().isoformat()
        data = pipeline_mgr._load()
        data.setdefault('pipelines', []).append(d)
        pipeline_mgr._save(data)
        return jsonify({'ok': True, 'result': d})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/pipelines/<pid>/export', methods=['GET'])
def api_pipelines_export(pid):
    if not pipeline_mgr:
        return jsonify({'ok': False, 'error': 'Pipeline manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': pipeline_mgr.get_pipeline(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404


# ---------------------------------------------------------------------------
#  Cloud Dashboard API Routes
# ---------------------------------------------------------------------------

@app.route('/api/cloud/accounts', methods=['GET'])
def api_cloud_accounts_list():
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': cloud_mgr.get_accounts()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/cloud/accounts', methods=['POST'])
def api_cloud_accounts_create():
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        acct = cloud_mgr.add_account(d.get('name', ''), d.get('provider', 'azure'), d.get('credential_secret_id', ''), d.get('region', ''))
        return jsonify({'ok': True, 'result': acct})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/cloud/accounts/<aid>', methods=['DELETE'])
def api_cloud_accounts_delete(aid):
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        cloud_mgr.remove_account(aid)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/cloud/resources', methods=['GET'])
def api_cloud_resources_list():
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        provider = request.args.get('provider')
        rtype = request.args.get('type')
        status = request.args.get('status')
        return jsonify({'ok': True, 'result': cloud_mgr.get_resources(provider=provider, rtype=rtype, status=status)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/cloud/resources/<rid>', methods=['GET'])
def api_cloud_resources_get(rid):
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': cloud_mgr.get_resource(rid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404

@app.route('/api/cloud/resources/<rid>/start', methods=['POST'])
def api_cloud_resources_start(rid):
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': cloud_mgr.start_resource(rid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/cloud/resources/<rid>/stop', methods=['POST'])
def api_cloud_resources_stop(rid):
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': cloud_mgr.stop_resource(rid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/cloud/costs', methods=['GET'])
def api_cloud_costs():
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': cloud_mgr.get_costs()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/cloud/refresh', methods=['POST'])
def api_cloud_refresh():
    if not cloud_mgr:
        return jsonify({'ok': False, 'error': 'Cloud manager not available'}), 503
    try:
        cloud_mgr.refresh()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ---------------------------------------------------------------------------
#  Marketplace API Routes
# ---------------------------------------------------------------------------

@app.route('/api/marketplace/plugins', methods=['GET'])
def api_marketplace_plugins_list():
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        q = request.args.get('q')
        category = request.args.get('category')
        installed = request.args.get('installed', '').lower() == 'true'
        return jsonify({'ok': True, 'result': marketplace_mgr.list_plugins(query=q, category=category, installed_only=installed)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/marketplace/plugins/<pid>', methods=['GET'])
def api_marketplace_plugins_get(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.get_plugin(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404

@app.route('/api/marketplace/plugins/<pid>/install', methods=['POST'])
def api_marketplace_plugins_install(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.install_plugin(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/marketplace/plugins/<pid>/uninstall', methods=['POST'])
def api_marketplace_plugins_uninstall(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.uninstall_plugin(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/marketplace/plugins/<pid>/update', methods=['POST'])
def api_marketplace_plugins_update(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.get_plugin(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/marketplace/plugins/<pid>/config', methods=['GET'])
def api_marketplace_plugins_config_get(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.get_config(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404

@app.route('/api/marketplace/plugins/<pid>/config', methods=['PUT'])
def api_marketplace_plugins_config_update(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        return jsonify({'ok': True, 'result': marketplace_mgr.update_config(pid, d)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/marketplace/plugins/<pid>/reviews', methods=['GET'])
def api_marketplace_plugins_reviews_list(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.get_reviews(pid)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/marketplace/plugins/<pid>/reviews', methods=['POST'])
def api_marketplace_plugins_reviews_create(pid):
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        d = request.get_json(silent=True) or {}
        review = marketplace_mgr.add_review(pid, d.get('rating', 5), d.get('text', ''), d.get('author', 'Anonymous'))
        return jsonify({'ok': True, 'result': review})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/marketplace/installed', methods=['GET'])
def api_marketplace_installed():
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.list_plugins(installed_only=True)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/marketplace/refresh', methods=['POST'])
def api_marketplace_refresh():
    if not marketplace_mgr:
        return jsonify({'ok': False, 'error': 'Marketplace manager not available'}), 503
    try:
        return jsonify({'ok': True, 'result': marketplace_mgr.list_plugins()})
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

    # return directory tree; use project root for web IDE (paths with slashes) or scripts folder for legacy compatibility

    rel = request.args.get('path','')

    try:

        # Check if this is a web IDE request (path contains slashes) or legacy script manager

        if '/' in rel or '\\' in rel:

            # Web IDE: use project root

            base = Path(__file__).parent.resolve()

        else:

            # Legacy: use scripts folder (empty path or simple filename)

            base = Path(app.config['SCRIPTS_FOLDER']).resolve()

        target = (base / rel).resolve()

        if not str(target).startswith(str(base)):

            return jsonify({'ok': False, 'error':'invalid path'}), 400

        nodes = []

        try:
            paths = list(target.iterdir())
        except (OSError, PermissionError) as e:
            return jsonify({'ok': False, 'error': f'Cannot read directory: {e}'}), 500

        for p in sorted(paths, key=lambda x: x.name):

            try:
                if p.name.startswith('.') and p.name not in ['.env', '.env.example']:  # Allow some dotfiles
                    continue

                if p.is_dir():
                    nodes.append({'type':'dir','name':p.name,'path':str(p.relative_to(base))})
                else:
                    stat = p.stat()
                    nodes.append({'type':'file','name':p.name,'path':str(p.relative_to(base)),'size':stat.st_size,'modified':datetime.fromtimestamp(stat.st_mtime).isoformat()})
            except (OSError, PermissionError):
                # Skip files/directories we can't access
                continue

        return jsonify({'ok':True,'path':str(target.relative_to(base)) if rel else '','nodes':nodes})

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



ADDONS_MODULES_TEMPLATE = """{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>🧩 Addons Modules</h2>

<p>Manage installed addon modules, configure settings, install dependencies, and run services.</p>

{% if installed_modules %}

<h3>Installed Modules ({{ installed_modules|length }} modules)</h3>

<div style="margin-bottom: 20px;">
<button class="btn" style="background: #f44336; color: white;" onclick="deleteAllModules()" id="delete-all-btn">🗑️ Delete All Modules</button>
<span id="delete-status" style="margin-left: 10px; display: none;"></span>
</div>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-top: 20px;">

{% for module in installed_modules %}

<div class="card" style="border-left-color: #FF6B35;">

<h3 style="color: #FF6B35;">{{ module.name }}{% if module.build_commands %} <span style="font-size: 0.7em; background: #FF5722; color: white; padding: 2px 6px; border-radius: 3px;">🔨</span>{% endif %}</h3>

<div style="margin: 10px 0;">

<span class="status-badge" style="background: #4CAF50;">{{ module.language|upper }}</span>

<span class="status-badge" style="background: #2196F3;">{{ module.files }} files</span>

<span class="status-badge" style="background: #FF9800;">{{ (module.size/1024)|round(1) }} KB</span>

{% if module.build_commands %}

<span style="margin-left: 10px;">

<form method="POST" action="/addons/modules/{{ module.name }}/build" style="display: inline;">

<button type="submit" class="btn" style="background: #FF5722; font-size: 0.8em; padding: 4px 8px;" onclick="return confirm('Build/compile {{ module.name }}?')">🔨 Build</button>

</form>

</span>

{% endif %}

</div>

<p><strong>Path:</strong> {{ module.path }}</p>

<p><strong>Modified:</strong> {{ module.modified }}</p>

<div style="margin-top: 15px;">
<a href="/addons/modules/{{ module.name }}/manager" class="btn" style="background:#2196F3;">🗂️ Manage Files</a>
</div>

<div style="margin-top: 15px;">

<h4>Configuration Files</h4>

{% if module.config_files %}

<ul style="margin: 5px 0; padding-left: 20px;">

{% for config in module.config_files %}

<li><a href="/addons/modules/{{ module.name }}/config/{{ config }}" class="btn btn-info" style="font-size: 0.8em; padding: 4px 8px;">📝 {{ config }}</a></li>

{% endfor %}

</ul>

{% else %}

<p style="color: #888; font-style: italic;">No config files found</p>

{% endif %}

</div>

<div style="margin-top: 15px;">

<h4>Setup & Dependencies</h4>

{% if module.requirements_files %}

<form method="POST" action="/addons/modules/{{ module.name }}/install_deps" style="display: inline;">

<button type="submit" class="btn" style="background: #4CAF50;">📦 Install Dependencies</button>

</form>

{% endif %}

{% if module.setup_scripts %}

<h5>Setup Scripts:</h5>

<ul style="margin: 5px 0; padding-left: 20px;">

{% for script in module.setup_scripts %}

<li>
{% if script.endswith('.php') %}
<a href="/addons/modules/{{ module.name }}/web/{{ script }}" class="btn" style="background: #9C27B0;" target="_blank">🌐 View {{ script }}</a>
<span style="font-size: 0.8em; color: #888;"> (Web-based installer)</span>
{% else %}
<form method="POST" action="/addons/modules/{{ module.name }}/run_setup/{{ script }}" style="display: inline;">
<button type="submit" class="btn" style="background: #FF9800;" onclick="return confirm('Run setup script: {{ script }}?')">▶️ {{ script }}</button>
</form>
{% endif %}
</li>

{% endfor %}

</ul>

{% endif %}

</div>

{% if module.build_commands %}

<div style="margin-top: 15px;">

<h4>Build & Compile</h4>

<p style="font-size: 0.9em; color: #888;">Project Type: {{ module.project_type }}{% if module.frameworks %} | Frameworks: {{ module.frameworks|join(', ') }}{% endif %}</p>

<form method="POST" action="/addons/modules/{{ module.name }}/build" style="display: inline;">

<button type="submit" class="btn" style="background: #FF5722;" onclick="return confirm('Build/compile {{ module.name }}? This may take several minutes.')">🔨 Build Project</button>

</form>

<p style="font-size: 0.8em; color: #666; margin-top: 5px;">{{ module.build_commands|length }} build step(s) detected</p>

</div>

{% endif %}

<div style="margin-top: 15px;">

<h4>Service Control</h4>

<button class="btn" style="background: #4CAF50;" onclick="startService('{{ module.name }}')">▶️ Start Service</button>

<button class="btn btn-warning" onclick="stopService('{{ module.name }}')">⏹️ Stop Service</button>

<button class="btn btn-info" onclick="checkServiceStatus('{{ module.name }}')">📊 Status</button>

<div id="service-status-{{ module.name }}" style="margin-top: 10px; padding: 10px; background: #1a1a1a; border-radius: 5px; display: none;"></div>

</div>

<div style="margin-top: 15px;">

<h4>Documentation</h4>

{% if module.readme_files %}

<ul style="margin: 5px 0; padding-left: 20px;">

{% for readme in module.readme_files %}

<li><a href="/addons/modules/{{ module.name }}/config/{{ readme }}" class="btn" style="background: #9C27B0; font-size: 0.8em; padding: 4px 8px;">📖 {{ readme }}</a></li>

{% endfor %}

</ul>

{% else %}

<p style="color: #888; font-style: italic;">No documentation found</p>

{% endif %}

</div>

</div>

{% endfor %}

</div>

{% else %}

<h3>No Installed Modules</h3>

<p>No addon modules are currently installed. Install addons from the <a href="/addons">Addons</a> page to see them here.</p>

{% endif %}

</div>

<script>

function startService(moduleName) {

    fetch(`/addons/modules/${moduleName}/start`, { method: 'POST' })

        .then(r => r.json())

        .then(data => {

            alert(data.message || 'Service started');

            checkServiceStatus(moduleName);

        })

        .catch(e => alert('Error: ' + e));

}

function stopService(moduleName) {

    fetch(`/addons/modules/${moduleName}/stop`, { method: 'POST' })

        .then(r => r.json())

        .then(data => {

            alert(data.message || 'Service stopped');

            checkServiceStatus(moduleName);

        })

        .catch(e => alert('Error: ' + e));

}

function checkServiceStatus(moduleName) {

    fetch(`/addons/modules/${moduleName}/status`)

        .then(r => r.json())

        .then(data => {

            const statusDiv = document.getElementById(`service-status-${moduleName}`);

            statusDiv.style.display = 'block';

            statusDiv.innerHTML = `

                <strong>Status:</strong> ${data.status || 'Unknown'}<br>

                <strong>Port:</strong> ${data.port || 'N/A'}<br>

                <strong>PID:</strong> ${data.pid || 'N/A'}<br>

                <strong>URL:</strong> ${data.url ? `<a href="${data.url}" target="_blank">${data.url}</a>` : 'N/A'}

            `;

        })

        .catch(e => {

            const statusDiv = document.getElementById(`service-status-${moduleName}`);

            statusDiv.style.display = 'block';

            statusDiv.innerHTML = '<strong>Error:</strong> ' + e;

        });

}

function deleteAllModules() {
    if (!confirm('Are you sure you want to delete ALL installed modules? This action cannot be undone!')) {
        return;
    }
    
    const btn = document.getElementById('delete-all-btn');
    const status = document.getElementById('delete-status');
    
    btn.disabled = true;
    btn.textContent = '🗑️ Deleting...';
    status.style.display = 'inline';
    status.textContent = 'Deleting all modules...';
    status.style.color = '#ff9800';
    
    fetch('/addons/modules/delete_all', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                status.textContent = 'All modules deleted successfully!';
                status.style.color = '#4CAF50';
                // Reload the page after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                status.textContent = 'Error: ' + (data.error || 'Unknown error');
                status.style.color = '#f44336';
                btn.disabled = false;
                btn.textContent = '🗑️ Delete All Modules';
            }
        })
        .catch(e => {
            status.textContent = 'Error: ' + e;
            status.style.color = '#f44336';
            btn.disabled = false;
            btn.textContent = '🗑️ Delete All Modules';
        });
}

</script>

{% endblock %}"""



MODULE_MANAGER_TEMPLATE = """{% extends "base.html" %}

{% block content %}

<div class="container">

<header>

<h1>⚡ MasterChief</h1>

<p class="subtitle">Module Manager - {{ module.name }}</p>

<div style="position:absolute;right:20px;top:24px;">

    <a href="/addons/modules" class="btn" style="background:#666;">← Back to Modules</a>

    <label style="color:#ccc;font-size:0.9em;margin-left:20px;">Language: <select id="langSelect"        

style="background:#1a1a1a;color:#eee;border:1px solid

#333;padding:6px;border-radius:6px;"><option value="en">English</option><option

value="es">Español</option></select></label>

    </div>

</header>

<nav>

<a href="/" class="">Dashboard</a>

<a href="/echo-chat" class="">🌙 Echo Chat</a>

<a href="/scripts" class="">Scripts</a>

<a href="/processes" class="">Processes</a>

<a href="/services" class="">Services</a>

<a href="/addons" class="active">Addons</a>

<a href="/addons/modules" class="">🧩 Modules</a>

<a href="/echo-train" class="">Training</a>

</nav>

<div class="section">

<h2>🗂️ Module Manager: {{ module.name }}</h2>

<div style="display: flex; gap: 20px; margin-bottom: 20px;">

<div style="flex: 1;">

<h3>📁 Module Information</h3>

<div class="card">

<p><strong>Name:</strong> {{ module.name }}</p>

<p><strong>Path:</strong> {{ module.path }}</p>

<p><strong>Files:</strong> {{ module.file_count }}</p>

<p><strong>Directories:</strong> {{ module.dir_count }}</p>

<p><strong>Total Size:</strong> {{ "%.1f"|format(module.total_size/1024) }} KB</p>

</div>

<h3>⚙️ Module Configuration</h3>

<div class="card">

<h4>UI Integration</h4>

<p>Add this module to the main navigation menu for quick access.</p>

<button id="addToUI" class="btn" style="background:#4CAF50;" onclick="toggleUIIntegration('add')">➕ Add to Main UI</button>

<button id="removeFromUI" class="btn btn-danger" style="display:none;" onclick="toggleUIIntegration('remove')">➖ Remove from Main UI</button>

<div id="uiStatus" style="margin-top:10px;"></div>

</div>

</div>

<div style="flex: 2;">

<h3>📂 File Explorer</h3>

<div class="card">

<div style="display: flex; gap: 10px; margin-bottom: 15px;">

<button class="btn" onclick="refreshFiles()">🔄 Refresh</button>

<label class="btn" for="fileUpload" style="background:#2196F3;">📤 Upload File</label>

<input type="file" id="fileUpload" style="display:none;" onchange="uploadFile()">

<button class="btn" onclick="createNewFile()" style="background:#FF9800;">📄 New File</button>

<button class="btn" onclick="createNewFolder()" style="background:#9C27B0;">📁 New Folder</button>

</div>

<div id="fileTree" style="max-height: 400px; overflow-y: auto; border: 1px solid #333; border-radius: 5px; padding: 10px; background: #1a1a1a;">

<!-- File tree will be loaded here -->

</div>

</div>

</div>

</div>

<div class="section">

<h3>📝 File Editor</h3>

<div id="editorContainer" style="display: none;">

<div class="card">

<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">

<h4 id="editorTitle">Editing: <span id="currentFile"></span></h4>

<div>

<button class="btn" onclick="saveFile()" style="background:#4CAF50;">💾 Save</button>

<button class="btn btn-danger" onclick="deleteFile()" onclick="return confirm('Delete this file?')">🗑️ Delete</button>

<button class="btn" onclick="closeEditor()">❌ Close</button>

</div>

</div>

<textarea id="fileEditor" style="width: 100%; height: 400px; background: #1a1a1a; color: #e0e0e0; border: 1px solid #3a3a3a; border-radius: 5px; padding: 10px; font-family: 'Courier New', monospace; font-size: 14px; resize: vertical;"></textarea>

</div>

</div>

</div>

<!-- Modals -->

<!-- New File Modal -->
<div id="newFileModal" class="modal">
<div class="modal-content">
<span class="close" onclick="closeModal('newFileModal')">&times;</span>
<h2>📄 Create New File</h2>
<input type="text" id="newFileName" placeholder="filename.txt" style="width:100%;margin:10px 0;padding:8px;">
<button class="btn" onclick="createFile()">Create File</button>
</div>
</div>

<!-- New Folder Modal -->
<div id="newFolderModal" class="modal">
<div class="modal-content">
<span class="close" onclick="closeModal('newFolderModal')">&times;</span>
<h2>📁 Create New Folder</h2>
<input type="text" id="newFolderName" placeholder="folder_name" style="width:100%;margin:10px 0;padding:8px;">
<button class="btn" onclick="createFolder()">Create Folder</button>
</div>
</div>

<!-- Upload Modal -->
<div id="uploadModal" class="modal">
<div class="modal-content">
<span class="close" onclick="closeModal('uploadModal')">&times;</span>
<h2>📤 Upload File</h2>
<form id="uploadForm" enctype="multipart/form-data">
<input type="file" id="uploadFileInput" name="file" style="width:100%;margin:10px 0;">
<div id="uploadPathContainer" style="margin:10px 0;">
<label>Upload to folder (optional):</label>
<input type="text" id="uploadPath" placeholder="path/to/folder" style="width:100%;padding:8px;">
</div>
<button type="button" class="btn" onclick="doUpload()">Upload</button>
</form>
<div id="uploadStatus"></div>
</div>
</div>

</div>

<script>

// Global variables
let currentModule = '{{ module.name }}';
let currentFile = null;
let fileTree = {};

function init() {
    loadFiles();
    checkUIIntegration();
}

function loadFiles() {
    fetch(`/addons/modules/${currentModule}/api/files`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                alert('Error loading files: ' + data.error);
                return;
            }
            renderFileTree(data.files);
        })
        .catch(e => alert('Error: ' + e));
}

function renderFileTree(files) {
    fileTree = {};
    
    // Organize files by directory
    files.forEach(file => {
        const pathParts = file.path.split('/');
        let current = fileTree;
        
        for (let i = 0; i < pathParts.length - 1; i++) {
            const part = pathParts[i];
            if (!current[part]) {
                current[part] = { __type: 'directory', __children: {} };
            }
            current = current[part].__children;
        }
        
        const fileName = pathParts[pathParts.length - 1];
        current[fileName] = { 
            __type: file.type, 
            ...file,
            __children: file.type === 'directory' ? {} : undefined
        };
    });
    
    const treeHtml = renderTreeNode(fileTree, '', 0);
    document.getElementById('fileTree').innerHTML = treeHtml || '<p style="color:#888;">No files found</p>';
}

function renderTreeNode(node, path, depth) {
    let html = '';
    const indent = '  '.repeat(depth);
    
    for (const [name, item] of Object.entries(node)) {
        if (name.startsWith('__')) continue;
        
        const fullPath = path ? `${path}/${name}` : name;
        const isDir = item.__type === 'directory';
        const icon = isDir ? '📁' : getFileIcon(item.extension);
        
        html += `${indent}<div style="margin: 2px 0;">
            <span onclick="toggleDirectory('${fullPath}')" style="cursor: pointer; ${isDir ? 'font-weight: bold;' : ''}">
                ${icon} ${name}
            </span>
            ${!isDir ? ` <button class="btn" style="font-size:0.7em;padding:2px 6px;" onclick="editFile('${fullPath}')">Edit</button>` : ''}
        </div>`;
        
        if (isDir && item.__expanded) {
            html += renderTreeNode(item.__children || {}, fullPath, depth + 1);
        }
    }
    
    return html;
}

function toggleDirectory(path) {
    let current = fileTree;
    const parts = path.split('/');
    
    for (const part of parts) {
        if (current[part] && current[part].__type === 'directory') {
            current[part].__expanded = !current[part].__expanded;
            current = current[part].__children;
        }
    }
    
    renderFileTree(expandTreeToFiles(fileTree));
}

function expandTreeToFiles(node) {
    const files = [];
    
    function traverse(current, path) {
        for (const [name, item] of Object.entries(current)) {
            if (name.startsWith('__')) continue;
            
            const fullPath = path ? `${path}/${name}` : name;
            files.push({
                name: item.name || name,
                path: fullPath,
                type: item.__type,
                extension: item.extension || '',
                size: item.size || 0,
                modified: item.modified || ''
            });
            
            if (item.__type === 'directory' && item.__children) {
                traverse(item.__children, fullPath);
            }
        }
    }
    
    traverse(node, '');
    return files;
}

function getFileIcon(ext) {
    const icons = {
        '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨', '.json': '📋',
        '.md': '📖', '.txt': '📄', '.xml': '📄', '.yml': '📋', '.yaml': '📋',
        '.sh': '⚡', '.bat': '⚡', '.ps1': '⚡', '.php': '🐘', '.sql': '🗄️',
        '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.svg': '🖼️'
    };
    return icons[ext] || '📄';
}

function editFile(path) {
    fetch(`/addons/modules/${currentModule}/api/file?path=${encodeURIComponent(path)}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                alert('Error loading file: ' + data.error);
                return;
            }
            
            currentFile = path;
            document.getElementById('currentFile').textContent = path;
            document.getElementById('fileEditor').value = data.content;
            document.getElementById('editorContainer').style.display = 'block';
            document.getElementById('fileEditor').focus();
        })
        .catch(e => alert('Error: ' + e));
}

function saveFile() {
    if (!currentFile) return;
    
    const content = document.getElementById('fileEditor').value;
    
    fetch(`/addons/modules/${currentModule}/api/file?path=${encodeURIComponent(currentFile)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('File saved successfully!');
        } else {
            alert('Error saving file: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(e => alert('Error: ' + e));
}

function deleteFile() {
    if (!currentFile) return;
    
    if (!confirm(`Are you sure you want to delete "${currentFile}"?`)) return;
    
    fetch(`/addons/modules/${currentModule}/api/file?path=${encodeURIComponent(currentFile)}`, {
        method: 'DELETE'
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('File deleted successfully!');
            closeEditor();
            loadFiles();
        } else {
            alert('Error deleting file: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(e => alert('Error: ' + e));
}

function closeEditor() {
    document.getElementById('editorContainer').style.display = 'none';
    currentFile = null;
    document.getElementById('fileEditor').value = '';
}

function createNewFile() {
    document.getElementById('newFileName').value = '';
    document.getElementById('newFileModal').style.display = 'block';
}

function createFile() {
    const fileName = document.getElementById('newFileName').value.trim();
    if (!fileName) {
        alert('Please enter a file name');
        return;
    }
    
    // For now, create in root directory
    editFile(fileName);
    closeModal('newFileModal');
}

function createNewFolder() {
    document.getElementById('newFolderName').value = '';
    document.getElementById('newFolderModal').style.display = 'block';
}

function createFolder() {
    const folderName = document.getElementById('newFolderName').value.trim();
    if (!folderName) {
        alert('Please enter a folder name');
        return;
    }
    
    // Create empty directory by "creating" a file in it and then deleting it
    const tempFile = `${folderName}/.gitkeep`;
    
    fetch(`/addons/modules/${currentModule}/api/file?path=${encodeURIComponent(tempFile)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: '' })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            loadFiles();
            closeModal('newFolderModal');
        } else {
            alert('Error creating folder: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(e => alert('Error: ' + e));
}

function uploadFile() {
    const fileInput = document.getElementById('fileUpload');
    if (fileInput.files.length === 0) return;
    
    document.getElementById('uploadFileInput').files = fileInput.files;
    document.getElementById('uploadModal').style.display = 'block';
}

function doUpload() {
    const fileInput = document.getElementById('uploadFileInput');
    const uploadPath = document.getElementById('uploadPath').value.trim();
    const statusDiv = document.getElementById('uploadStatus');
    
    if (fileInput.files.length === 0) {
        statusDiv.textContent = 'No file selected';
        statusDiv.style.color = 'red';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (uploadPath) {
        formData.append('path', uploadPath);
    }
    
    statusDiv.textContent = 'Uploading...';
    statusDiv.style.color = 'orange';
    
    fetch(`/addons/modules/${currentModule}/api/upload`, {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            statusDiv.textContent = data.message;
            statusDiv.style.color = 'green';
            loadFiles();
            setTimeout(() => closeModal('uploadModal'), 2000);
        } else {
            statusDiv.textContent = 'Error: ' + (data.error || 'Unknown error');
            statusDiv.style.color = 'red';
        }
    })
    .catch(e => {
        statusDiv.textContent = 'Error: ' + e;
        statusDiv.style.color = 'red';
    });
}

function toggleUIIntegration(action) {
    const statusDiv = document.getElementById('uiStatus');
    statusDiv.textContent = action === 'add' ? 'Adding to UI...' : 'Removing from UI...';
    statusDiv.style.color = 'orange';
    
    fetch(`/addons/modules/${currentModule}/api/ui_integration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            statusDiv.textContent = data.message;
            statusDiv.style.color = 'green';
            checkUIIntegration();
        } else {
            statusDiv.textContent = 'Error: ' + (data.error || 'Unknown error');
            statusDiv.style.color = 'red';
        }
    })
    .catch(e => {
        statusDiv.textContent = 'Error: ' + e;
        statusDiv.style.color = 'red';
    });
}

function checkUIIntegration() {
    // Check if module is in UI by looking at the navigation
    // This is a simple check - in a real app you'd have an API endpoint
    const navLinks = document.querySelectorAll('nav a');
    let isInUI = false;
    
    navLinks.forEach(link => {
        if (link.href.includes(`/addons/modules/${currentModule}`)) {
            isInUI = true;
        }
    });
    
    document.getElementById('addToUI').style.display = isInUI ? 'none' : 'inline-block';
    document.getElementById('removeFromUI').style.display = isInUI ? 'inline-block' : 'none';
}

function refreshFiles() {
    loadFiles();
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', init);

</script>

<style>
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.8);
}

.modal-content {
    background-color: #2d2d2d;
    margin: 10% auto;
    padding: 20px;
    border-radius: 10px;
    width: 80%;
    max-width: 500px;
    color: #e0e0e0;
}

.close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}

.close:hover {
    color: #4CAF50;
}

.card {
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}
</style>

{% endblock %}"""



ADDONS_MODULE_CONFIG_TEMPLATE = """{% extends "base.html" %}

{% block content %}

<div class="section">

<h2>⚙️ Module Configuration</h2>

<h3>{{ module_name }} - {{ config_file }}</h3>

<div style="margin-bottom: 20px;">

<a href="/addons/modules" class="btn">← Back to Modules</a>

</div>

<form method="POST" style="margin-bottom: 20px;">

<label for="content" style="display: block; margin-bottom: 10px; font-weight: bold;">File Content:</label>

<textarea name="content" id="content" style="width: 100%; height: 500px; background: #1a1a1a; color: #e0e0e0; border: 1px solid #3a3a3a; border-radius: 5px; padding: 10px; font-family: monospace; font-size: 14px;" spellcheck="false">{{ content }}</textarea>

<div style="margin-top: 20px;">

<button type="submit" class="btn" style="background: #4CAF50;">💾 Save Changes</button>

<button type="button" class="btn btn-warning" onclick="resetContent()">🔄 Reset</button>

</div>

</form>

<script>

let originalContent = document.getElementById('content').value;

function resetContent() {

    if (confirm('Reset to original content? Unsaved changes will be lost.')) {

        document.getElementById('content').value = originalContent;

    }

}

// Auto-save indicator

let saveTimeout;

document.getElementById('content').addEventListener('input', function() {

    clearTimeout(saveTimeout);

    saveTimeout = setTimeout(() => {

        // Could implement auto-save here

        console.log('Content changed');

    }, 1000);

});

</script>

</div>

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







# ---------------------------------------------------------------------------
#  Pipeline Manager
# ---------------------------------------------------------------------------

PIPELINE_RUNS = {}

class PipelineManager:
    def __init__(self, db_path, runs_path):
        self.db_path = Path(db_path)
        self.runs_path = Path(runs_path)
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        for p, default in [(self.db_path, {'pipelines': []}), (self.runs_path, {'runs': []})]:
            if not p.exists():
                p.write_text(json.dumps(default, indent=2), encoding='utf-8')

    def _load(self):
        try:
            return json.loads(self.db_path.read_text(encoding='utf-8'))
        except Exception:
            return {'pipelines': []}

    def _save(self, data):
        self.db_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _load_runs(self):
        try:
            return json.loads(self.runs_path.read_text(encoding='utf-8'))
        except Exception:
            return {'runs': []}

    def _save_runs(self, data):
        self.runs_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def list_pipelines(self):
        return self._load().get('pipelines', [])

    def get_pipeline(self, pid):
        for p in self._load().get('pipelines', []):
            if p['id'] == pid:
                return p
        raise ValueError('Pipeline not found')

    def create_pipeline(self, name, description=''):
        d = self._load()
        pipeline = {
            'id': str(uuid.uuid4()), 'name': name, 'description': description,
            'stages': [], 'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }
        d.setdefault('pipelines', []).append(pipeline)
        self._save(d)
        return pipeline

    def update_pipeline(self, pid, updates):
        d = self._load()
        for p in d.get('pipelines', []):
            if p['id'] == pid:
                for k, v in updates.items():
                    if k not in ('id', 'created'):
                        p[k] = v
                p['updated'] = datetime.now().isoformat()
                self._save(d)
                return p
        raise ValueError('Pipeline not found')

    def delete_pipeline(self, pid):
        d = self._load()
        d['pipelines'] = [p for p in d.get('pipelines', []) if p['id'] != pid]
        self._save(d)

    def execute_pipeline(self, pid):
        pipeline = self.get_pipeline(pid)
        run = {
            'id': str(uuid.uuid4()), 'pipeline_id': pid,
            'pipeline_name': pipeline['name'], 'status': 'running',
            'started': datetime.now().isoformat(), 'finished': None,
            'stages': [], 'log': []
        }
        PIPELINE_RUNS[run['id']] = run
        t = threading.Thread(target=self._run_pipeline, args=(run, pipeline), daemon=True)
        t.start()
        return run

    def _run_pipeline(self, run, pipeline):
        try:
            for stage in sorted(pipeline.get('stages', []), key=lambda s: s.get('order', 0)):
                stage_run = {
                    'stage_id': stage['id'], 'name': stage.get('name', 'Stage'),
                    'status': 'running', 'started': datetime.now().isoformat(),
                    'finished': None, 'steps': []
                }
                run['stages'].append(stage_run)
                run['log'].append(f"[{datetime.now().isoformat()}] Starting stage: {stage.get('name')}")
                for step in stage.get('steps', []):
                    step_run = self._execute_step(step, run)
                    stage_run['steps'].append(step_run)
                    if step_run['status'] == 'failed':
                        stage_run['status'] = 'failed'
                        stage_run['finished'] = datetime.now().isoformat()
                        run['status'] = 'failed'
                        run['finished'] = datetime.now().isoformat()
                        run['log'].append(f"[{datetime.now().isoformat()}] Pipeline FAILED at stage: {stage.get('name')}")
                        self._persist_run(run)
                        return
                stage_run['status'] = 'completed'
                stage_run['finished'] = datetime.now().isoformat()
            run['status'] = 'completed'
            run['finished'] = datetime.now().isoformat()
            run['log'].append(f"[{datetime.now().isoformat()}] Pipeline completed successfully")
        except Exception as e:
            run['status'] = 'failed'
            run['finished'] = datetime.now().isoformat()
            run['log'].append(f"[{datetime.now().isoformat()}] Pipeline error: {str(e)}")
        self._persist_run(run)

    def _execute_step(self, step, run):
        step_run = {
            'step_id': step.get('id', str(uuid.uuid4())),
            'name': step.get('name', 'Step'), 'type': step.get('type', 'custom_command'),
            'status': 'running', 'started': datetime.now().isoformat(),
            'output': '', 'finished': None
        }
        run['log'].append(f"[{datetime.now().isoformat()}] Running step: {step.get('name')} (type={step.get('type')})")
        try:
            cfg = step.get('config', {})
            cmd = None
            cwd = cfg.get('working_dir') or None
            if step.get('type') == 'script':
                cmd = f"{cfg.get('script_path', '')} {cfg.get('args', '')}".strip()
            elif step.get('type') == 'docker_build':
                cmd = f"docker build -t {cfg.get('image_tag', 'latest')} -f {cfg.get('dockerfile_path', 'Dockerfile')} {cfg.get('context_dir', '.')}"
            elif step.get('type') in ('terraform_apply', 'terraform_plan'):
                action = 'apply -auto-approve' if step['type'] == 'terraform_apply' else 'plan'
                var_file = f"-var-file={cfg['var_file']}" if cfg.get('var_file') else ''
                cmd = f"terraform {action} {var_file}".strip()
            elif step.get('type') == 'test_run':
                cmd = cfg.get('test_command', 'echo No test command')
            elif step.get('type') == 'deploy':
                cmd = f"echo Deploying to {cfg.get('target', 'unknown')} with strategy {cfg.get('strategy', 'rolling')}"
            elif step.get('type') == 'custom_command':
                cmd = cfg.get('command', 'echo hello')
            else:
                cmd = f"echo Unknown step type: {step.get('type')}"
            if cmd:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True,
                    timeout=int(cfg.get('timeout', 300)), cwd=cwd
                )
                step_run['output'] = result.stdout + result.stderr
                step_run['status'] = 'completed' if result.returncode == 0 else 'failed'
            else:
                step_run['status'] = 'completed'
                step_run['output'] = 'No command to run'
        except subprocess.TimeoutExpired:
            step_run['status'] = 'failed'
            step_run['output'] = 'Step timed out'
        except Exception as e:
            step_run['status'] = 'failed'
            step_run['output'] = str(e)
        step_run['finished'] = datetime.now().isoformat()
        return step_run

    def _persist_run(self, run):
        d = self._load_runs()
        d.setdefault('runs', []).insert(0, run)
        if len(d['runs']) > 100:
            d['runs'] = d['runs'][:100]
        self._save_runs(d)

    def get_run(self, rid):
        if rid in PIPELINE_RUNS:
            return PIPELINE_RUNS[rid]
        d = self._load_runs()
        for r in d.get('runs', []):
            if r['id'] == rid:
                return r
        raise ValueError('Run not found')

    def get_runs(self, pipeline_id=None, limit=50):
        runs = list(PIPELINE_RUNS.values())
        d = self._load_runs()
        for r in d.get('runs', []):
            if r['id'] not in PIPELINE_RUNS:
                runs.append(r)
        if pipeline_id:
            runs = [r for r in runs if r.get('pipeline_id') == pipeline_id]
        runs.sort(key=lambda r: r.get('started', ''), reverse=True)
        return runs[:limit]

    def cancel_run(self, rid):
        if rid in PIPELINE_RUNS:
            PIPELINE_RUNS[rid]['status'] = 'cancelled'
            PIPELINE_RUNS[rid]['finished'] = datetime.now().isoformat()
            return PIPELINE_RUNS[rid]
        raise ValueError('Run not found or already finished')


# ---------------------------------------------------------------------------
#  Cloud Dashboard Manager
# ---------------------------------------------------------------------------

class CloudProvider:
    def list_resources(self, credentials):
        return []
    def get_resource(self, credentials, resource_id):
        return None
    def start_vm(self, credentials, vm_id):
        return {'ok': True}
    def stop_vm(self, credentials, vm_id):
        return {'ok': True}

class AzureProvider(CloudProvider):
    def list_resources(self, credentials):
        return [
            {'id': 'azure-vm-1', 'name': 'prod-web-01', 'type': 'vm', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'Standard_D2s_v3', 'cost_monthly': 70.08, 'created': '2024-01-15'},
            {'id': 'azure-vm-2', 'name': 'prod-api-01', 'type': 'vm', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'Standard_D4s_v3', 'cost_monthly': 140.16, 'created': '2024-01-15'},
            {'id': 'azure-stor-1', 'name': 'prodstorage01', 'type': 'storage', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'Standard_LRS', 'cost_monthly': 21.84, 'created': '2024-02-01'},
            {'id': 'azure-db-1', 'name': 'prod-sql-01', 'type': 'database', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': 'GP_Gen5_2', 'cost_monthly': 295.20, 'created': '2024-01-20'},
            {'id': 'azure-net-1', 'name': 'prod-vnet', 'type': 'network', 'provider': 'azure', 'status': 'running', 'region': 'eastus', 'size': '10.0.0.0/16', 'cost_monthly': 0, 'created': '2024-01-10'},
        ]

class AWSProvider(CloudProvider):
    def list_resources(self, credentials):
        return [
            {'id': 'aws-vm-1', 'name': 'staging-web', 'type': 'vm', 'provider': 'aws', 'status': 'running', 'region': 'us-east-1', 'size': 't3.medium', 'cost_monthly': 30.37, 'created': '2024-03-01'},
            {'id': 'aws-vm-2', 'name': 'staging-worker', 'type': 'vm', 'provider': 'aws', 'status': 'stopped', 'region': 'us-east-1', 'size': 't3.large', 'cost_monthly': 0, 'created': '2024-03-01'},
            {'id': 'aws-stor-1', 'name': 'staging-s3-data', 'type': 'storage', 'provider': 'aws', 'status': 'running', 'region': 'us-east-1', 'size': 'S3 Standard', 'cost_monthly': 15.50, 'created': '2024-03-05'},
            {'id': 'aws-db-1', 'name': 'staging-rds', 'type': 'database', 'provider': 'aws', 'status': 'running', 'region': 'us-east-1', 'size': 'db.t3.medium', 'cost_monthly': 52.56, 'created': '2024-03-10'},
        ]

class GCPProvider(CloudProvider):
    def list_resources(self, credentials):
        return [
            {'id': 'gcp-vm-1', 'name': 'dev-instance-1', 'type': 'vm', 'provider': 'gcp', 'status': 'running', 'region': 'us-central1', 'size': 'e2-medium', 'cost_monthly': 24.27, 'created': '2024-04-01'},
            {'id': 'gcp-stor-1', 'name': 'dev-bucket', 'type': 'storage', 'provider': 'gcp', 'status': 'running', 'region': 'us-central1', 'size': 'Standard', 'cost_monthly': 8.50, 'created': '2024-04-05'},
            {'id': 'gcp-db-1', 'name': 'dev-cloudsql', 'type': 'database', 'provider': 'gcp', 'status': 'stopped', 'region': 'us-central1', 'size': 'db-f1-micro', 'cost_monthly': 0, 'created': '2024-04-10'},
        ]

class CloudDashboardManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self._providers = {'azure': AzureProvider(), 'aws': AWSProvider(), 'gcp': GCPProvider()}
        self._resource_cache = {}
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save({'accounts': [
                {'id': str(uuid.uuid4()), 'name': 'Azure Production', 'provider': 'azure', 'credential_secret_id': '', 'region': 'eastus', 'created': datetime.now().isoformat()},
                {'id': str(uuid.uuid4()), 'name': 'AWS Staging', 'provider': 'aws', 'credential_secret_id': '', 'region': 'us-east-1', 'created': datetime.now().isoformat()},
                {'id': str(uuid.uuid4()), 'name': 'GCP Development', 'provider': 'gcp', 'credential_secret_id': '', 'region': 'us-central1', 'created': datetime.now().isoformat()},
            ]})
        self.refresh()

    def _load(self):
        try:
            return json.loads(self.db_path.read_text(encoding='utf-8'))
        except Exception:
            return {'accounts': []}

    def _save(self, data):
        self.db_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def get_accounts(self):
        return self._load().get('accounts', [])

    def add_account(self, name, provider, credential_secret_id='', region=''):
        d = self._load()
        acct = {'id': str(uuid.uuid4()), 'name': name, 'provider': provider,
                'credential_secret_id': credential_secret_id, 'region': region,
                'created': datetime.now().isoformat()}
        d.setdefault('accounts', []).append(acct)
        self._save(d)
        self.refresh()
        return acct

    def remove_account(self, aid):
        d = self._load()
        d['accounts'] = [a for a in d.get('accounts', []) if a['id'] != aid]
        self._save(d)
        self._resource_cache.pop(aid, None)

    def refresh(self):
        self._resource_cache = {}
        for acct in self.get_accounts():
            provider = self._providers.get(acct['provider'])
            if provider:
                try:
                    self._resource_cache[acct['id']] = provider.list_resources(acct.get('credential_secret_id'))
                except Exception:
                    self._resource_cache[acct['id']] = []

    def get_resources(self, provider=None, rtype=None, status=None):
        all_res = []
        for acct_id, resources in self._resource_cache.items():
            all_res.extend(resources)
        if provider:
            all_res = [r for r in all_res if r.get('provider') == provider]
        if rtype:
            all_res = [r for r in all_res if r.get('type') == rtype]
        if status:
            all_res = [r for r in all_res if r.get('status') == status]
        return all_res

    def get_resource(self, rid):
        for resources in self._resource_cache.values():
            for r in resources:
                if r['id'] == rid:
                    return r
        raise ValueError('Resource not found')

    def start_resource(self, rid):
        for resources in self._resource_cache.values():
            for r in resources:
                if r['id'] == rid:
                    r['status'] = 'running'
                    return r
        raise ValueError('Resource not found')

    def stop_resource(self, rid):
        for resources in self._resource_cache.values():
            for r in resources:
                if r['id'] == rid:
                    r['status'] = 'stopped'
                    r['cost_monthly'] = 0
                    return r
        raise ValueError('Resource not found')

    def get_costs(self):
        costs = {'azure': 0, 'aws': 0, 'gcp': 0, 'total': 0}
        for r in self.get_resources():
            p = r.get('provider', 'other')
            c = r.get('cost_monthly', 0)
            costs[p] = costs.get(p, 0) + c
            costs['total'] += c
        return costs


# ---------------------------------------------------------------------------
#  Marketplace Manager
# ---------------------------------------------------------------------------

class MarketplaceManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save({
                'plugins': [
                    {'id': 'terraform-iac', 'name': 'Terraform IaC', 'version': '1.2.0', 'author': 'MasterChief Team', 'category': 'DevOps', 'description': 'Infrastructure as Code automation with Terraform.', 'installed': True, 'rating': 4.5, 'review_count': 12, 'config': {'default_provider': 'azure', 'state_backend': 'local'}, 'dependencies': []},
                    {'id': 'ansible-config', 'name': 'Ansible Config Management', 'version': '2.0.1', 'author': 'MasterChief Team', 'category': 'Automation', 'description': 'Server configuration management with Ansible playbooks.', 'installed': True, 'rating': 4.2, 'review_count': 8, 'config': {'inventory_path': '/etc/ansible/hosts'}, 'dependencies': []},
                    {'id': 'k8s-deploy', 'name': 'Kubernetes Deployer', 'version': '3.1.0', 'author': 'MasterChief Team', 'category': 'DevOps', 'description': 'Kubernetes deployment automation with Helm charts.', 'installed': True, 'rating': 4.8, 'review_count': 25, 'config': {'default_namespace': 'default', 'context': 'minikube'}, 'dependencies': ['terraform-iac']},
                    {'id': 'prometheus-monitor', 'name': 'Prometheus Monitoring', 'version': '1.5.0', 'author': 'MasterChief Team', 'category': 'Monitoring', 'description': 'Full metrics pipeline with Prometheus and Grafana.', 'installed': False, 'rating': 4.6, 'review_count': 18, 'config': {}, 'dependencies': []},
                    {'id': 'vault-secrets', 'name': 'HashiCorp Vault', 'version': '0.9.0', 'author': 'Community', 'category': 'Security', 'description': 'Integration with HashiCorp Vault for secret management.', 'installed': False, 'rating': 4.0, 'review_count': 6, 'config': {}, 'dependencies': []},
                    {'id': 'jenkins-ci', 'name': 'Jenkins CI Bridge', 'version': '1.0.0', 'author': 'Community', 'category': 'Integration', 'description': 'Bridge MasterChief pipelines with Jenkins CI/CD.', 'installed': False, 'rating': 3.8, 'review_count': 4, 'config': {}, 'dependencies': []},
                    {'id': 'github-actions', 'name': 'GitHub Actions Sync', 'version': '2.1.0', 'author': 'Community', 'category': 'Integration', 'description': 'Sync GitHub Actions workflows with MasterChief pipelines.', 'installed': False, 'rating': 4.3, 'review_count': 14, 'config': {}, 'dependencies': []},
                    {'id': 'sonarqube-scan', 'name': 'SonarQube Scanner', 'version': '1.3.0', 'author': 'Community', 'category': 'Security', 'description': 'Code quality and security scanning with SonarQube.', 'installed': False, 'rating': 4.1, 'review_count': 9, 'config': {}, 'dependencies': []},
                    {'id': 'elk-logging', 'name': 'ELK Stack Logging', 'version': '2.0.0', 'author': 'MasterChief Team', 'category': 'Monitoring', 'description': 'Centralized logging with Elasticsearch, Logstash, and Kibana.', 'installed': False, 'rating': 4.4, 'review_count': 11, 'config': {}, 'dependencies': []},
                    {'id': 'cost-optimizer', 'name': 'Cloud Cost Optimizer', 'version': '1.1.0', 'author': 'Community', 'category': 'DevOps', 'description': 'Analyze and optimize cloud spending.', 'installed': False, 'rating': 3.9, 'review_count': 7, 'config': {}, 'dependencies': []},
                    {'id': 'postgres-manager', 'name': 'PostgreSQL Manager', 'version': '1.0.0', 'author': 'Community', 'category': 'Database', 'description': 'PostgreSQL database management with backups and monitoring.', 'installed': False, 'rating': 4.2, 'review_count': 5, 'config': {}, 'dependencies': []},
                    {'id': 'nginx-proxy', 'name': 'Nginx Proxy Manager', 'version': '1.4.0', 'author': 'Community', 'category': 'Networking', 'description': 'Nginx reverse proxy management with SSL automation.', 'installed': False, 'rating': 4.5, 'review_count': 16, 'config': {}, 'dependencies': []},
                ],
                'reviews': []
            })

    def _load(self):
        try:
            return json.loads(self.db_path.read_text(encoding='utf-8'))
        except Exception:
            return {'plugins': [], 'reviews': []}

    def _save(self, data):
        self.db_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def list_plugins(self, query=None, category=None, installed_only=False):
        d = self._load()
        plugins = d.get('plugins', [])
        if query:
            q = query.lower()
            plugins = [p for p in plugins if q in p.get('name', '').lower() or q in p.get('description', '').lower()]
        if category and category != 'All':
            plugins = [p for p in plugins if p.get('category') == category]
        if installed_only:
            plugins = [p for p in plugins if p.get('installed')]
        return plugins

    def get_plugin(self, pid):
        for p in self._load().get('plugins', []):
            if p['id'] == pid:
                return p
        raise ValueError('Plugin not found')

    def install_plugin(self, pid):
        d = self._load()
        for p in d.get('plugins', []):
            if p['id'] == pid:
                deps = p.get('dependencies', [])
                for dep in deps:
                    dep_plugin = next((x for x in d['plugins'] if x['id'] == dep), None)
                    if dep_plugin and not dep_plugin.get('installed'):
                        raise ValueError(f'Dependency {dep} must be installed first')
                p['installed'] = True
                self._save(d)
                return p
        raise ValueError('Plugin not found')

    def uninstall_plugin(self, pid):
        d = self._load()
        for p in d.get('plugins', []):
            if p['id'] == pid:
                dependents = [x['name'] for x in d['plugins'] if pid in x.get('dependencies', []) and x.get('installed')]
                if dependents:
                    raise ValueError(f'Cannot uninstall: {", ".join(dependents)} depend on this plugin')
                p['installed'] = False
                p['config'] = {}
                self._save(d)
                return p
        raise ValueError('Plugin not found')

    def get_config(self, pid):
        p = self.get_plugin(pid)
        return p.get('config', {})

    def update_config(self, pid, config):
        d = self._load()
        for p in d.get('plugins', []):
            if p['id'] == pid:
                p['config'] = config
                self._save(d)
                return p
        raise ValueError('Plugin not found')

    def get_reviews(self, pid):
        d = self._load()
        return [r for r in d.get('reviews', []) if r.get('plugin_id') == pid]

    def add_review(self, pid, rating, text, author='Anonymous'):
        d = self._load()
        review = {
            'id': str(uuid.uuid4()), 'plugin_id': pid,
            'rating': max(1, min(5, int(rating))), 'text': text,
            'author': author, 'created': datetime.now().isoformat()
        }
        d.setdefault('reviews', []).append(review)
        plugin_reviews = [r for r in d['reviews'] if r.get('plugin_id') == pid]
        for p in d.get('plugins', []):
            if p['id'] == pid:
                p['review_count'] = len(plugin_reviews)
                p['rating'] = round(sum(r['rating'] for r in plugin_reviews) / len(plugin_reviews), 1)
                break
        self._save(d)
        return review


###############################################################################
#  Dynamic Module Loading
###############################################################################

managers = {}
for name, config in ENABLED_MODULES.items():
    if not config.get('enabled', False):
        managers[name] = None
        continue
    try:
        spec = importlib.util.spec_from_file_location(f"{name}_manager", f"templates/{name}_manager.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        register_func = getattr(module, f'register_{name}_module')
        # Remove 'enabled' from config for kwargs
        kwargs = {k: v for k, v in config.items() if k != 'enabled'}
        managers[name] = register_func(app, **kwargs)
        print(f"DEBUG: Loaded module {name}")
    except Exception as e:
        print(f"Failed to load module {name}: {e}")
        managers[name] = None

# Set global manager variables for backward compatibility
rbac_mgr = managers.get('rbac')
vault_mgr = managers.get('vault')
notification_mgr = managers.get('notification')
pipeline_mgr = managers.get('pipeline')
cloud_mgr = managers.get('cloud')
memory_mgr = managers.get('memory')
marketplace_mgr = managers.get('marketplace')
script_mgr = managers.get('script')







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

<a href="/addons" class="{{ 'active' if '/addons' in request.path and '/modules' not in request.path else '' }}">Addons</a>

<a href="/modules" class="{{ 'active' if request.path=='/modules' else '' }}">⚙️ Modules</a>

<a href="/addons/modules" class="{{ 'active' if '/addons/modules' in request.path else '' }}">🧩 Addon Modules</a>

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

<a href="/masterchief_code_ui" class="btn">MasterChief Code UI</a>

<a href="/iac_manager" class="btn">IAC Manager</a>

<a href="/github" class="btn">GitHub Integration</a>

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

<h2>Addon Manager</h2>

<div style="display:flex;gap:20px;margin-bottom:30px;">

<div class="file-upload" onclick="document.getElementById('fileInput').click();" style="flex:1;">

<h3>📦 Upload Addon Package</h3>

<p>Click to select a .zip file</p>

<form method="POST" action="/addons/upload" enctype="multipart/form-data" id="uploadForm">

<input type="file" id="fileInput" name="file" accept=".zip" style="display:none;" onchange="document.getElementById('uploadForm').submit();">

</form>

</div>

<div class="file-upload" onclick="showBlankModuleWizard()" style="flex:1;border-color:#2196F3;">

<h3>🆕 Create Blank Module</h3>

<p>Start with an empty module and build it live</p>

</div>

</div>

{% if uploaded_files %}

<h3>Uploaded Addons ({{ uploaded_files|length }} files)</h3>

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

<form method="POST" action="/addons/install/{{ file.name }}" style="display:inline;">

<input type="text" name="source_dir" placeholder="Source dir (optional)" style="width:120px;margin-right:5px;padding:2px;" title="Subdirectory containing source code (e.g., 'src' for inspircd)">

<button type="submit" class="btn">Install</button>

</form>

<a href="/addons/build/{{ file.name }}" class="btn" style="background:#FF5722;color:white;">🔨 Build</a>

<a href="/addons/load/{{ file.name|replace('.zip', '') }}" class="btn" style="background:#28a745;color:white;">Load</a>

<a href="/addons/register_features/{{ file.name|replace('.zip', '') }}" class="btn" style="background:#17a2b8;color:white;">Register Features</a>

<a href="/addons/delete/{{ file.name }}" class="btn btn-danger" onclick="return confirmDelete('{{ file.name }}');">Delete</a>

</td>

</tr>

{% endfor %}

</tbody>

</table>

{% else %}

<h3>Uploaded Addons</h3>

<p>No uploaded addon files found. Upload a .zip file to get started.</p>

{% endif %}

</div>

<!-- Blank Module Creation Wizard Modal -->
<div id="blankModuleWizard" class="modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;">
    <div class="modal-content" style="background:#2d2d2d;margin:50px auto;padding:30px;border-radius:10px;max-width:700px;position:relative;">
        <span class="close" style="position:absolute;top:15px;right:20px;font-size:30px;cursor:pointer;color:#888;" onclick="closeModal('blankModuleWizard')">&times;</span>
        <h2 style="color: #4CAF50; margin-bottom: 20px;">🆕 Create Blank Module</h2>

        <div class="form-group" style="margin-bottom:20px;">
            <label for="moduleName" style="display:block;margin-bottom:8px;color:#4CAF50;font-weight:bold;">Module Name *</label>
            <input type="text" id="moduleName" placeholder="e.g., my_custom_module" required style="width:100%;padding:12px;background:#1a1a1a;border:1px solid #3a3a3a;color:#e0e0e0;border-radius:5px;font-size:1em;">
            <small style="color: #888;">Must start with a letter, can contain letters, numbers, underscores, and hyphens</small>
        </div>

        <div class="form-group" style="margin-bottom:20px;">
            <label for="moduleType" style="display:block;margin-bottom:8px;color:#4CAF50;font-weight:bold;">Module Type</label>
            <select id="moduleType" style="width:100%;padding:12px;background:#1a1a1a;border:1px solid #3a3a3a;color:#e0e0e0;border-radius:5px;font-size:1em;">
                <option value="python">Python Module</option>
                <option value="web">Web Application</option>
                <option value="api">API Service</option>
                <option value="tool">DevOps Tool</option>
                <option value="other">Other</option>
            </select>
        </div>

        <div class="form-group" style="margin-bottom:20px;">
            <label for="moduleDescription" style="display:block;margin-bottom:8px;color:#4CAF50;font-weight:bold;">Description (Optional)</label>
            <textarea id="moduleDescription" rows="3" placeholder="Describe what this module will do..." style="width:100%;padding:12px;background:#1a1a1a;border:1px solid #3a3a3a;color:#e0e0e0;border-radius:5px;font-size:1em;"></textarea>
        </div>

        <div style="background: #1a1a1a; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4 style="color: #4CAF50; margin: 0 0 10px 0;">What happens next?</h4>
            <ul style="color: #ccc; margin: 0; padding-left: 20px;">
                <li>A new directory structure will be created for your module</li>
                <li>You can add files and edit code through the module management interface</li>
                <li>Use the Build, Load, and Register Features buttons to activate your module</li>
                <li>Access your module at: <code style="background: #2d2d2d; padding: 2px 4px; border-radius: 3px;">/addons/modules/{module_name}</code></li>
            </ul>
        </div>

        <div style="text-align: right; margin-top: 20px;">
            <button class="btn btn-info" onclick="closeModal('blankModuleWizard')" style="background:#2196F3;color:#fff;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;text-decoration:none;display:inline-block;margin:5px;">Cancel</button>
            <button class="btn" onclick="createBlankModule()" style="background:#4CAF50;color:#fff;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;text-decoration:none;display:inline-block;margin:5px;margin-left:10px;">Create Module</button>
        </div>
    </div>
</div>

<script>
function showBlankModuleWizard() {
    document.getElementById('blankModuleWizard').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function createBlankModule() {
    const moduleName = document.getElementById('moduleName').value.trim();
    const moduleType = document.getElementById('moduleType').value;
    const description = document.getElementById('moduleDescription').value.trim();

    if (!moduleName) {
        alert('Please enter a module name');
        return;
    }

    if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(moduleName)) {
        alert('Module name must start with a letter and contain only letters, numbers, underscores, and hyphens');
        return;
    }

    // Show loading
    const btn = event.target || document.querySelector('#blankModuleWizard .btn:not(.btn-info)');
    const originalText = btn.textContent;
    btn.textContent = 'Creating...';
    btn.disabled = true;

    fetch('/addons/create_blank_module', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: moduleName,
            type: moduleType,
            description: description
        })
    })
    .then(r => r.json())
    .then(j => {
        if (j.success) {
            alert('Blank module created successfully! You can now add files and manage it.');
            closeModal('blankModuleWizard');
            location.reload();
        } else {
            alert('Error creating module: ' + (j.error || 'Unknown error'));
        }
    })
    .catch(e => {
        alert('Error: ' + e);
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}
</script>

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

.chat-input{flex:1;padding:12px;background:#1a1a1a;border:2px solid #9370DB;color:#e0e0e0;border-radius:25px;font-size:1em;resize:vertical;}

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

<textarea id="chatInput" class="chat-input" placeholder="Type your message... ✨" autocomplete="off" required rows="2"></textarea>

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

document.getElementById('chatInput').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();this.closest('form').dispatchEvent(new Event('submit',{cancelable:true}));}});

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

MODULES_TEMPLATE="""{% extends "base.html" %}

{% block content %}

<h2>🧩 Module Management</h2>

<p>Enable or disable MasterChief modules. Changes take effect on restart.</p>

<div class="modules-grid">
{% for name, config in enabled_modules.items() %}
<div class="card">
<h3>{{ name|title }} Module</h3>
<p>Status: <span class="status-{{ 'enabled' if config.enabled else 'disabled' }}">{{ 'Enabled' if config.enabled else 'Disabled' }}</span></p>
<p>Manager: <code>{{ managers[name]|type if managers[name] else 'Not loaded' }}</code></p>
<form method="POST" action="/api/modules/toggle" style="display:inline;">
<input type="hidden" name="module" value="{{ name }}">
<button type="submit" class="btn {{ 'btn-danger' if config.enabled else 'btn-success' }}">
{{ 'Disable' if config.enabled else 'Enable' }}
</button>
</form>
</div>
{% endfor %}
</div>

<style>
.modules-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.status-enabled { color: #4CAF50; font-weight: bold; }
.status-disabled { color: #f44336; font-weight: bold; }
</style>

{% endblock %}"""

@app.route('/')

@requires_permission('dashboard')
def dashboard():
    stats=get_system_stats()

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',DASHBOARD_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),stats=stats,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/modules')
@requires_permission('dashboard')
def modules_page():
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', MODULES_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')), enabled_modules=ENABLED_MODULES, managers=managers, request=request, get_flashed_messages=get_flashed_messages)

@app.route('/api/modules/toggle', methods=['POST'])
@requires_permission('dashboard')
def api_modules_toggle():
    module = request.form.get('module')
    if module not in ENABLED_MODULES:
        return jsonify({'ok': False, 'error': 'Module not found'}), 400
    ENABLED_MODULES[module]['enabled'] = not ENABLED_MODULES[module]['enabled']
    # Save to file
    app.config['MODULES_CONFIG'].write_text(json.dumps(ENABLED_MODULES, indent=2), encoding='utf-8')
    return jsonify({'ok': True, 'enabled': ENABLED_MODULES[module]['enabled']})

@app.route('/api/test')
def api_test():
    return jsonify({'ok': True, 'message': 'API is working', 'script_mgr': str(type(script_mgr))})

@app.route('/api/stats')

def api_stats():

    return jsonify(get_system_stats())





@app.route('/scripts')

@requires_permission('scripts')
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

@requires_permission('scripts')
def scripts_view(filename):

    content=script_mgr.get_script_content(filename)

    if content is None:

        flash('Script not found','error')

        return redirect(url_for('scripts_list'))

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_VIEW_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,content=content,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/scripts/execute/<filename>')

@requires_permission('scripts')
def scripts_execute(filename):

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=None,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/scripts/run/<filename>',methods=['POST'])

@requires_permission('scripts')
def scripts_run(filename):

    args=request.form.get('args','')

    result=script_mgr.execute_script(filename,args)

    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=result,request=request,get_flashed_messages=get_flashed_messages)

@app.route('/scripts/delete/<filename>')

@requires_permission('scripts')
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

@requires_permission('scripts')
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

@requires_permission('scripts')
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

@requires_permission('scripts')
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

@requires_permission('scripts')
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

@requires_permission('scripts')
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

@requires_permission('scripts')
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

@requires_permission('processes')
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

@requires_permission('services')
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

@requires_permission('addons')
def addons_list():

    uploaded_files=[]

    upload_folder = app.config['UPLOAD_FOLDER']

    if upload_folder.exists():

        zip_files = list(upload_folder.glob('*.zip'))

        for file in zip_files:

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

        # Automatically extract the zip file

        try:

            extract_dir=app.config['UPLOAD_FOLDER']/'extracted'/filename.replace('.zip','')

            extract_dir.mkdir(parents=True,exist_ok=True)

            with zipfile.ZipFile(filepath,'r') as zip_ref:

                zip_ref.extractall(extract_dir)

            flash(f'✅ File {filename} uploaded and automatically extracted to modules!', 'success')

            flash(f'📁 Module available at: /addons/modules/{filename.replace(".zip","")}', 'info')

        except Exception as e:

            flash(f'⚠️ File uploaded but extraction failed: {str(e)}', 'warning')

            flash(f'📁 You can manually extract and access via: /addons/modules/{filename.replace(".zip","")}', 'info')

    else:

        flash('Only .zip files are allowed','error')

    return redirect(url_for('addons_list'))

@app.route('/addons/create_blank_module', methods=['POST'])
def addons_create_blank_module():
    """Create a blank module with empty directory structure."""
    try:
        data = request.get_json() or {}
        module_name = data.get('name', '').strip()
        module_type = data.get('type', 'python')
        description = data.get('description', '').strip()

        if not module_name:
            return jsonify({'success': False, 'error': 'Module name is required'}), 400

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', module_name):
            return jsonify({'success': False, 'error': 'Module name must start with a letter and contain only letters, numbers, underscores, and hyphens'}), 400

        # Create module directory structure
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        source_dir = extract_dir  # For blank modules, source_dir is the same as extract_dir

        # Create basic directory structure
        extract_dir.mkdir(parents=True, exist_ok=True)

        # Create basic files based on module type
        if module_type == 'python':
            # Create __init__.py
            (extract_dir / '__init__.py').write_text(f'''"""
{module_name} - {description or 'A custom Python module'}
"""

__version__ = "0.1.0"
__author__ = "MasterChief"
''')

            # Create main.py
            (extract_dir / 'main.py').write_text(f'''"""
Main module for {module_name}
{description or ''}
"""

def main():
    """Main function - customize this for your module"""
    print(f"Hello from {module_name}!")
    # Add your code here

if __name__ == "__main__":
    main()
''')

            # Create config.py
            (extract_dir / 'config.py').write_text(f'''"""
Configuration for {module_name}
"""

# Module configuration
MODULE_NAME = "{module_name}"
MODULE_VERSION = "0.1.0"
MODULE_DESCRIPTION = "{description or 'A custom Python module'}"

# Add your configuration variables here
DEBUG = True
''')

        elif module_type == 'web':
            # Create basic web structure
            (extract_dir / 'app.py').write_text(f'''"""
Web application for {module_name}
{description or ''}
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return f"<h1>Welcome to {module_name}!</h1><p>{description or 'A custom web application'}</p>"

if __name__ == "__main__":
    app.run(debug=True)
''')

            (extract_dir / 'templates').mkdir(exist_ok=True)
            (extract_dir / 'static').mkdir(exist_ok=True)

        elif module_type == 'api':
            # Create basic API structure
            (extract_dir / 'api.py').write_text(f'''"""
API service for {module_name}
{description or ''}
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({{"status": "ok", "module": "{module_name}"}})

@app.route('/api/info')
def info():
    return jsonify({{
        "name": "{module_name}",
        "version": "0.1.0",
        "description": "{description or 'A custom API service'}"
    }})

if __name__ == "__main__":
    app.run(debug=True)
''')

        else:
            # Generic/other type - just create a basic README
            (extract_dir / 'README.md').write_text(f'''# {module_name}

{description or 'A custom module'}

## Getting Started

Add your code and documentation here.

## Usage

Customize this module according to your needs.
''')

        # Create README.md for all types
        readme_path = extract_dir / 'README.md'
        if not readme_path.exists():
            readme_path.write_text(f'''# {module_name}

{description or f'A custom {module_type} module'}

## Description

{description or 'This module was created as a blank template and can be customized as needed.'}

## Files

This module includes the following files:
- Main implementation files
- Configuration files
- Documentation

## Getting Started

1. Add your custom code to the module files
2. Configure any settings in the config files
3. Use the Build and Load buttons to activate the module
4. Register features to make them available system-wide

## Development

Edit files directly through the web interface or upload additional files as needed.
''')

        # Store module info
        module_info = {
            'name': module_name,
            'extract_dir': str(extract_dir),
            'source_dir': str(source_dir),
            'installed_at': datetime.now().isoformat(),
            'type': module_type,
            'description': description,
            'is_blank_module': True
        }

        # Save module info
        modules_file = app.config['UPLOAD_FOLDER'] / 'modules.json'
        try:
            if modules_file.exists():
                with open(modules_file, 'r') as f:
                    modules = json.load(f)
            else:
                modules = {}

            modules[module_name] = module_info

            with open(modules_file, 'w') as f:
                json.dump(modules, f, indent=2)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Could not save module info: {str(e)}'}), 500

        return jsonify({
            'success': True,
            'message': f'Blank module "{module_name}" created successfully',
            'module': module_info
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/addons/install/<filename>', methods=['GET', 'POST'])

def addons_install(filename):

    filepath=app.config['UPLOAD_FOLDER']/secure_filename(filename)

    if not filepath.exists():

        flash('File not found','error')

        return redirect(url_for('addons_list'))

    # Get source directory from form

    source_dir = request.form.get('source_dir', '').strip()

    try:

        extract_dir=app.config['UPLOAD_FOLDER']/'extracted'/filename.replace('.zip','')

        extract_dir.mkdir(parents=True,exist_ok=True)

        with zipfile.ZipFile(filepath,'r') as zip_ref:

            zip_ref.extractall(extract_dir)

        # Determine the actual project root (handle zips with top-level folder)
        project_root = extract_dir
        subdirs = [d for d in extract_dir.iterdir() if d.is_dir()]
        files_at_root = [f for f in extract_dir.iterdir() if f.is_file()]
        
        if len(subdirs) == 1 and not files_at_root:
            # Zip has a single top-level directory, use that as project root
            project_root = subdirs[0]
        
        # Apply source directory if specified
        final_source_dir = project_root
        if source_dir:
            potential_src = project_root / source_dir
            if potential_src.exists() and potential_src.is_dir():
                final_source_dir = potential_src
                flash(f'📁 Using source directory: {source_dir}', 'info')
            else:
                flash(f'⚠️ Source directory "{source_dir}" not found in {project_root.name}, using project root', 'warning')
        

        # Store the source directory info for this module

        module_name = filename.replace('.zip', '')

        module_info = {

            'name': module_name,

            'extract_dir': str(extract_dir),

            'source_dir': str(final_source_dir),

            'installed_at': datetime.now().isoformat()

        }

        

        # Save module info (you might want to store this in a file or database)

        modules_file = app.config['UPLOAD_FOLDER'] / 'modules.json'

        try:

            if modules_file.exists():

                with open(modules_file, 'r') as f:

                    modules = json.load(f)

            else:

                modules = {}

            modules[module_name] = module_info

            with open(modules_file, 'w') as f:

                json.dump(modules, f, indent=2)

        except Exception as e:

            flash(f'⚠️ Could not save module info: {str(e)}', 'warning')

        

        flash(f'✅ Addon {filename} installed successfully', 'success')

        flash(f'📁 Module available at: /addons/modules/{module_name}', 'info')

        if source_dir:

            flash(f'🔧 Source directory set to: {source_dir}', 'info')

    except Exception as e:

        flash(f'❌ Failed to install addon: {str(e)}','error')

    return redirect(url_for('addons_list'))

@app.route('/addons/build/<filename>')
def addons_build(filename):
    """Analyze a zip file for build commands without full installation"""
    filepath = app.config['UPLOAD_FOLDER'] / secure_filename(filename)
    
    if not filepath.exists():
        flash('File not found', 'error')
        return redirect(url_for('addons_list'))
    
    try:
        # Create temporary extraction directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract zip file temporarily
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Find the actual project directory (handle zips with top-level folder)
            extract_dir = temp_path
            subdirs = [d for d in temp_path.iterdir() if d.is_dir()]
            files_at_root = [f for f in temp_path.iterdir() if f.is_file()]
            
            if len(subdirs) == 1 and not files_at_root:
                # Zip has a single top-level directory, use that as project root
                extract_dir = subdirs[0]
            
            # Analyze for build commands
            project_info = detect_project_type(extract_dir)
            build_commands = detect_build_commands(extract_dir, project_info)
            
            if build_commands:
                flash(f'🔨 {filename} contains buildable source code ({project_info["type"]})', 'info')
                flash(f'📋 Detected {len(build_commands)} build step(s). Install first, then use Build option.', 'info')
                if project_info['frameworks']:
                    flash(f'🛠️ Frameworks: {", ".join(project_info["frameworks"])}', 'info')
            else:
                flash(f'ℹ️ {filename} does not appear to contain buildable source code', 'info')
                
    except Exception as e:
        flash(f'Failed to analyze addon: {str(e)}', 'error')
    
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

@app.route('/addons/load/<addon_name>')

def addons_load(addon_name):

    """Load an installed addon by importing its main module"""

    try:

        # Check if addon is installed

        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / addon_name

        if not extract_dir.exists():

            flash(f'Addon {addon_name} is not installed','error')

            return redirect(url_for('addons_list'))

        

        # Detect project type

        project_info = detect_project_type(extract_dir)

        

        if project_info['has_python']:

            # Handle Python addon

            # Look for addon.py or __init__.py in the extracted directory

            addon_file = extract_dir / 'addon.py'

            init_file = extract_dir / '__init__.py'

            

            if addon_file.exists():

                # Import the addon module

                import importlib.util

                spec = importlib.util.spec_from_file_location(f"addon_{addon_name}", str(addon_file))

                if spec and spec.loader:

                    addon_module = importlib.util.module_from_spec(spec)

                    spec.loader.exec_module(addon_module)

                    

                    # Call init function if it exists

                    if hasattr(addon_module, 'init'):

                        addon_module.init(app)

                    

                    flash(f'Python addon {addon_name} loaded successfully!','success')

                else:

                    flash(f'Failed to load Python addon {addon_name}: invalid module','error')

            elif init_file.exists():

                # Try loading as a package

                import sys

                if str(extract_dir) not in sys.path:

                    sys.path.insert(0, str(extract_dir))

                

                try:

                    addon_module = __import__(addon_name)

                    if hasattr(addon_module, 'init'):

                        addon_module.init(app)

                    flash(f'Python addon {addon_name} loaded successfully!','success')

                except ImportError as e:

                    flash(f'Failed to import Python addon {addon_name}: {str(e)}','error')

            else:

                flash(f'Python addon {addon_name} does not have a valid entry point (addon.py or __init__.py)','error')

        elif project_info['has_php']:

            # Handle PHP web application
            # Determine primary type for display
            primary_type = 'PHP'
            if project_info['has_nodejs']:
                primary_type = 'Node.js/PHP'
            elif len([k for k in ['has_java', 'has_csharp', 'has_cpp', 'has_go', 'has_rust'] if project_info.get(k)]) > 0:
                primary_type = 'PHP/Multi-language'
            
            flash(f'PHP web application {addon_name} is ready! Access via /addons/modules/{addon_name}/','info')
            flash(f'Type: {primary_type} - Frameworks: {", ".join(project_info["frameworks"]) if project_info["frameworks"] else "None detected"}','info')

        else:

            # Handle other types or unknown

            flash(f'Addon {addon_name} loaded as {project_info["type"]} application','success')

            if project_info['frameworks']:

                flash(f'Detected frameworks: {", ".join(project_info["frameworks"])}','info')

            

    except Exception as e:

        flash(f'Failed to load addon {addon_name}: {str(e)}','error')

    

    return redirect(url_for('addons_list'))

@app.route('/addons/register_features/<addon_name>')

def addons_register_features(addon_name):

    """Register features from a loaded addon"""

    try:

        # Check if addon is installed

        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / addon_name

        if not extract_dir.exists():

            flash(f'Addon {addon_name} is not installed','error')

            return redirect(url_for('addons_list'))

        

        # Detect project type

        project_info = detect_project_type(extract_dir)

        

        if project_info['has_python']:

            # Handle Python addon features

            features_file = extract_dir / 'features.json'

            if features_file.exists():

                import json

                with open(features_file, 'r') as f:

                    features_data = json.load(f)

                

                # Register features (this would integrate with the feature manager)

                # For now, just acknowledge the features file exists

                flash(f'Features registered for Python addon {addon_name} ({len(features_data.get("features", []))} features)','success')

            else:

                flash(f'No features.json found for Python addon {addon_name}','warning')

        elif project_info['has_php']:

            # PHP web applications don't have features to register

            flash(f'PHP web application {addon_name} does not have features to register','info')

        else:

            # Other types

            flash(f'Addon {addon_name} ({project_info["type"]}) does not support feature registration','info')

            

    except Exception as e:

        flash(f'Failed to register features for addon {addon_name}: {str(e)}','error')

    

    return redirect(url_for('addons_list'))

@app.route('/addons/modules')
def addons_modules():
    """List and manage installed addon modules"""
    installed_modules = []
    
    # Check both current workspace and the cool-elbakyan workspace
    extract_dirs = [
        app.config['UPLOAD_FOLDER'] / 'extracted',
        Path(__file__).parent / '.claude' / 'worktrees' / 'cool-elbakyan' / 'data' / 'uploads' / 'extracted'
    ]
    
    for extract_dir in extract_dirs:
        if extract_dir.exists():
            for module_dir in extract_dir.iterdir():
                if module_dir.is_dir():
                    try:
                        # Get module info with basic file scanning
                        config_files = []
                        readme_files = []
                        setup_scripts = []
                        requirements_files = []
                        language = 'unknown'
                        total_files = 0
                        total_size = 0
                        
                        # Quick scan of files (limit to avoid performance issues)
                        try:
                            for file_path in module_dir.rglob('*'):
                                if file_path.is_file():
                                    total_files += 1
                                    try:
                                        total_size += file_path.stat().st_size
                                    except:
                                        pass
                                    
                                    # Limit scanning for performance
                                    if total_files > 500:
                                        break
                                    
                                    name = file_path.name.lower()
                                    rel_path = str(file_path.relative_to(module_dir))
                                    
                                    # Categorize files
                                    if any(name.endswith(ext) for ext in ['.conf', '.config', '.ini', '.cfg', '.json', '.yml', '.yaml']):
                                        if len(config_files) < 10:
                                            config_files.append(rel_path)
                                    elif name in ['readme', 'readme.txt', 'readme.md', 'install.txt', 'setup.txt']:
                                        if len(readme_files) < 5:
                                            readme_files.append(rel_path)
                                    elif any(name.endswith(ext) for ext in ['.sh', '.bat', '.ps1', '.py', '.php']) or any(name.startswith(prefix) for prefix in ['setup.', 'install.', 'configure.']) or any(name in ['install.php', 'setup.php', 'installer.php', 'wizard.php']):
                                        if len(setup_scripts) < 10:  # Increased limit
                                            setup_scripts.append(rel_path)
                                    elif name in ['requirements.txt', 'package.json', 'composer.json', 'gemfile', 'cargo.toml', 'pyproject.toml']:
                                        requirements_files.append(rel_path)
                                    
                                    # Detect language
                                    if language == 'unknown':
                                        if name.endswith(('.py', '__init__.py')):
                                            language = 'python'
                                        elif name.endswith(('.php', 'composer.json')):
                                            language = 'php'
                                        elif name.endswith(('.cs', '.csproj')):
                                            language = 'csharp'
                                        elif name.endswith(('.js', 'package.json')):
                                            language = 'javascript'
                                        elif name.endswith(('.c', '.cpp', '.h')):
                                            language = 'c/c++'
                        except:
                            # If scanning fails, continue with basic info
                            pass
                        
                        # Load module info to get source directory
                        modules_file = app.config['UPLOAD_FOLDER'] / 'modules.json'
                        source_dir = module_dir
                        if modules_file.exists():
                            try:
                                with open(modules_file, 'r') as f:
                                    modules = json.load(f)
                                if module_dir.name in modules:
                                    stored_source = modules[module_dir.name].get('source_dir')
                                    if stored_source and Path(stored_source).exists():
                                        source_dir = Path(stored_source)
                            except Exception:
                                pass
                        
                        # Detect project type and build commands using source_dir
                        project_info = detect_project_type(source_dir)
                        build_commands = detect_build_commands(source_dir, project_info)
                        
                        module_info = {
                            'name': module_dir.name,
                            'path': str(source_dir) if source_dir != module_dir else str(module_dir),
                            'size': total_size,
                            'files': total_files,
                            'modified': datetime.fromtimestamp(module_dir.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'config_files': config_files,
                            'readme_files': readme_files,
                            'setup_scripts': setup_scripts,
                            'requirements_files': requirements_files,
                            'language': language,
                            'project_type': project_info['type'],
                            'frameworks': project_info['frameworks'],
                            'build_commands': build_commands
                        }
                        
                        installed_modules.append(module_info)
                        
                    except (OSError, PermissionError) as e:
                        # Skip modules with access issues
                        continue
    
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',ADDONS_MODULES_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')), installed_modules=installed_modules, request=request, get_flashed_messages=get_flashed_messages)

@app.route('/addons/modules/<module_name>/manager')
def module_manager(module_name):
    """Module file manager and editor interface"""
    try:
        # Get module directory
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        if not extract_dir.exists():
            flash(f'Module "{module_name}" not found', 'error')
            return redirect('/addons/modules')
        
        # Get all files in the module
        files = []
        def scan_directory(path, relative_path=''):
            try:
                for item in sorted(path.iterdir()):
                    if item.is_file():
                        try:
                            size = item.stat().st_size
                            modified = datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            files.append({
                                'name': item.name,
                                'path': str(item.relative_to(extract_dir)),
                                'size': size,
                                'modified': modified,
                                'type': 'file',
                                'extension': item.suffix.lower()
                            })
                        except:
                            pass
                    elif item.is_dir():
                        try:
                            # Add directory entry
                            files.append({
                                'name': item.name,
                                'path': str(item.relative_to(extract_dir)),
                                'size': 0,
                                'modified': datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                'type': 'directory',
                                'extension': ''
                            })
                            # Recursively scan subdirectory
                            scan_directory(item, str(item.relative_to(extract_dir)))
                        except:
                            pass
            except:
                pass
        
        scan_directory(extract_dir)
        
        # Get module info
        module_info = {
            'name': module_name,
            'path': str(extract_dir),
            'file_count': len([f for f in files if f['type'] == 'file']),
            'dir_count': len([f for f in files if f['type'] == 'directory']),
            'total_size': sum(f['size'] for f in files if f['type'] == 'file')
        }
        
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', MODULE_MANAGER_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')), 
                                    module=module_info, files=files, request=request, get_flashed_messages=get_flashed_messages)
        
    except Exception as e:
        flash(f'Error loading module manager: {str(e)}', 'error')
        return redirect('/addons/modules')

@app.route('/addons/modules/<module_name>/config/<path:config_file>')
def addons_module_config(module_name, config_file):
    """View/edit config files for a module"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        config_path = extract_dir / config_file
        
        if not config_path.exists() or not config_path.is_file():
            flash(f'Config file not found: {config_file}', 'error')
            return redirect(url_for('addons_modules'))
        
        with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',ADDONS_MODULE_CONFIG_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')), 
                                   module_name=module_name, config_file=config_file, content=content, request=request, get_flashed_messages=get_flashed_messages)
    
    except Exception as e:
        flash(f'Error reading config file: {str(e)}', 'error')
        return redirect(url_for('addons_modules'))

@app.route('/addons/modules/<module_name>/config/<path:config_file>', methods=['POST'])
def addons_module_config_save(module_name, config_file):
    """Save changes to a config file"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        config_path = extract_dir / config_file
        
        if not config_path.exists():
            flash(f'Config file not found: {config_file}', 'error')
            return redirect(url_for('addons_modules'))
        
        content = request.form.get('content', '')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        flash(f'Config file saved successfully: {config_file}', 'success')
        return redirect(url_for('addons_module_config', module_name=module_name, config_file=config_file))
    
    except Exception as e:
        flash(f'Error saving config file: {str(e)}', 'error')
        return redirect(url_for('addons_module_config', module_name=module_name, config_file=config_file))

@app.route('/addons/modules/<module_name>/install_deps', methods=['POST'])
def addons_module_install_deps(module_name):
    """Install dependencies for a module with verbose output"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name

        if not extract_dir.exists():
            flash(f'Module not found: {module_name}', 'error')
            return redirect(url_for('addons_modules'))

        # Check if this is a zip file that needs extraction
        zip_file = app.config['UPLOAD_FOLDER'] / f"{module_name}.zip"
        if zip_file.exists() and not extract_dir.exists():
            try:
                import zipfile
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                flash(f'📦 Extracted {module_name}.zip successfully', 'info')
            except Exception as e:
                flash(f'❌ Failed to extract zip file: {str(e)}', 'error')
                return redirect(url_for('addons_modules'))

        success_messages = []
        error_messages = []
        verbose_output = []

        # Detect project type and dependencies
        project_info = detect_project_type(extract_dir)
        verbose_output.append(f"🔍 Detected project type: {project_info['type']}")
        verbose_output.append(f"📁 Project files: {len(list(extract_dir.rglob('*')))} total files")

        # Python dependencies
        if project_info['has_python']:
            req_files = list(extract_dir.glob('requirements*.txt')) + list(extract_dir.glob('pyproject.toml')) + list(extract_dir.glob('setup.py'))
            for req_file in req_files:
                try:
                    verbose_output.append(f"🐍 Found Python dependency file: {req_file.name}")
                    if req_file.name == 'requirements.txt' or req_file.name.startswith('requirements'):
                        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(req_file)],
                                              capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
                    elif req_file.name == 'pyproject.toml':
                        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'],
                                              capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
                    elif req_file.name == 'setup.py':
                        result = subprocess.run([sys.executable, str(req_file), 'develop'],
                                              capture_output=True, text=True, cwd=str(extract_dir), timeout=300)

                    if result.returncode == 0:
                        success_messages.append(f'✅ Python dependencies installed from {req_file.name}')
                        if result.stdout.strip():
                            verbose_output.append(f"📤 pip output: {result.stdout.strip()[:200]}...")
                    else:
                        error_messages.append(f'❌ Failed to install Python dependencies from {req_file.name}')
                        verbose_output.append(f"📤 pip error: {result.stderr.strip()[:200]}...")
                except subprocess.TimeoutExpired:
                    error_messages.append(f'⏰ Timeout installing Python dependencies from {req_file.name}')
                except Exception as e:
                    error_messages.append(f'❌ Error installing Python dependencies: {str(e)}')

        # Node.js dependencies
        if project_info['has_nodejs']:
            package_files = list(extract_dir.glob('package*.json'))
            for package_file in package_files:
                try:
                    verbose_output.append(f"📦 Found Node.js package file: {package_file.name}")
                    result = subprocess.run(['npm', 'install'], capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
                    if result.returncode == 0:
                        success_messages.append('✅ Node.js dependencies installed successfully')
                        if result.stdout.strip():
                            verbose_output.append(f"📤 npm output: {result.stdout.strip()[:200]}...")
                    else:
                        error_messages.append(f'❌ Failed to install Node.js dependencies')
                        verbose_output.append(f"📤 npm error: {result.stderr.strip()[:200]}...")
                except subprocess.TimeoutExpired:
                    error_messages.append('⏰ Timeout installing Node.js dependencies')
                except Exception as e:
                    error_messages.append(f'❌ Error installing Node.js dependencies: {str(e)}')

        # PHP Composer dependencies
        if project_info['has_php']:
            composer_files = list(extract_dir.glob('composer*.json'))
            for composer_file in composer_files:
                try:
                    verbose_output.append(f"🐘 Found PHP composer file: {composer_file.name}")
                    result = subprocess.run(['composer', 'install', '--no-interaction'], capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
                    if result.returncode == 0:
                        success_messages.append('✅ PHP dependencies installed successfully')
                        if result.stdout.strip():
                            verbose_output.append(f"📤 composer output: {result.stdout.strip()[:200]}...")
                    else:
                        error_messages.append(f'❌ Failed to install PHP dependencies')
                        verbose_output.append(f"📤 composer error: {result.stderr.strip()[:200]}...")
                except subprocess.TimeoutExpired:
                    error_messages.append('⏰ Timeout installing PHP dependencies')
                except Exception as e:
                    error_messages.append(f'❌ Error installing PHP dependencies: {str(e)}')

        # Build/compile processes
        build_commands = detect_build_commands(extract_dir, project_info)
        for cmd_info in build_commands:
            try:
                verbose_output.append(f"🔨 Running build command: {' '.join(cmd_info['command'])}")
                result = subprocess.run(cmd_info['command'], capture_output=True, text=True, cwd=str(extract_dir), timeout=600)
                if result.returncode == 0:
                    success_messages.append(f"✅ Build completed: {cmd_info['description']}")
                    if result.stdout.strip():
                        verbose_output.append(f"📤 build output: {result.stdout.strip()[:200]}...")
                else:
                    error_messages.append(f"❌ Build failed: {cmd_info['description']}")
                    verbose_output.append(f"📤 build error: {result.stderr.strip()[:200]}...")
                    # Don't continue with other build steps if one fails
                    break
            except subprocess.TimeoutExpired:
                error_messages.append(f"⏰ Build timeout: {cmd_info['description']}")
                break
            except Exception as e:
                error_messages.append(f"❌ Build error: {str(e)}")
                break

        # Show verbose output
        for msg in verbose_output[:10]:  # Limit to first 10 messages to avoid overwhelming
            flash(msg, 'info')

        if success_messages:
            flash('🎉 Installation completed successfully!', 'success')
            for msg in success_messages:
                flash(msg, 'success')
        if error_messages:
            flash('⚠️ Some installation steps failed:', 'warning')
            for msg in error_messages:
                flash(msg, 'error')

        if not success_messages and not error_messages:
            flash('ℹ️ No dependencies or build processes detected for this module', 'info')

    except Exception as e:
        flash(f'❌ Critical error during installation: {str(e)}', 'error')

    return redirect(url_for('addons_modules'))

def detect_project_type(extract_dir):
    """Detect the type of project and its characteristics"""
    project_info = {
        'type': 'Unknown',
        'has_python': False,
        'has_nodejs': False,
        'has_php': False,
        'has_java': False,
        'has_csharp': False,
        'has_cpp': False,
        'has_go': False,
        'has_rust': False,
        'frameworks': []
    }

    # Check for various project files
    try:
        files = list(extract_dir.rglob('*'))
        file_names = []
        for f in files[:1000]:  # Limit to first 1000 files for performance
            try:
                if f.is_file():
                    file_names.append(f.name.lower())
            except:
                continue  # Skip files we can't access
    except Exception as e:
        file_names = []

    # Python detection
    python_indicators = ['requirements.txt', 'setup.py', 'pyproject.toml', 'pipfile', '__init__.py', '.py']
    if any(ind in ' '.join(file_names) for ind in python_indicators):
        project_info['has_python'] = True
        project_info['type'] = 'Python'
        if any('django' in f.lower() for f in file_names):
            project_info['frameworks'].append('Django')
        if any('flask' in f.lower() for f in file_names):
            project_info['frameworks'].append('Flask')
        if any('fastapi' in f.lower() for f in file_names):
            project_info['frameworks'].append('FastAPI')

    # Node.js detection
    nodejs_indicators = ['package.json', 'node_modules', '.js', '.ts', 'webpack.config.js', 'gulpfile.js']
    if any(ind in ' '.join(file_names) for ind in nodejs_indicators):
        project_info['has_nodejs'] = True
        if project_info['type'] == 'Unknown':
            project_info['type'] = 'Node.js'
        else:
            project_info['type'] += '/Node.js'
        if any('react' in f.lower() for f in file_names):
            project_info['frameworks'].append('React')
        if any('vue' in f.lower() for f in file_names):
            project_info['frameworks'].append('Vue.js')
        if any('angular' in f.lower() for f in file_names):
            project_info['frameworks'].append('Angular')

    # PHP detection
    php_indicators = ['composer.json', 'composer.lock', '.php', 'artisan', 'wp-config.php', 'index.php']
    if any(ind in ' '.join(file_names) for ind in php_indicators):
        project_info['has_php'] = True
        if project_info['type'] == 'Unknown':
            project_info['type'] = 'PHP'
        else:
            project_info['type'] += '/PHP'
        if any('laravel' in f.lower() for f in file_names) or 'artisan' in file_names:
            project_info['frameworks'].append('Laravel')
        if 'wp-config.php' in file_names:
            project_info['frameworks'].append('WordPress')
        if any('symfony' in f.lower() for f in file_names):
            project_info['frameworks'].append('Symfony')

    # Java detection
    java_indicators = ['pom.xml', 'build.gradle', 'build.gradle.kts', '.java', 'mvnw', 'gradlew']
    if any(ind in ' '.join(file_names) for ind in java_indicators):
        project_info['has_java'] = True
        if project_info['type'] == 'Unknown':
            project_info['type'] = 'Java'
        else:
            project_info['type'] += '/Java'
        if 'pom.xml' in file_names:
            project_info['frameworks'].append('Maven')
        if 'build.gradle' in file_names:
            project_info['frameworks'].append('Gradle')

    # C#/.NET detection
    csharp_indicators = ['.csproj', '.sln', '.cs', 'packages.config', 'project.json']
    if any(ind in ' '.join(file_names) for ind in csharp_indicators):
        project_info['has_csharp'] = True
        if project_info['type'] == 'Unknown':
            project_info['type'] = 'C#'
        else:
            project_info['type'] += '/C#'

    # C/C++ detection
    cpp_indicators = ['CMakeLists.txt', 'Makefile', 'configure', '.cpp', '.c', '.h', '.hpp']
    if any(ind in ' '.join(file_names) for ind in cpp_indicators):
        project_info['has_cpp'] = True
        if project_info['type'] == 'Unknown':
            project_info['type'] = 'C/C++'
        else:
            project_info['type'] += '/C/C++'

    # Go detection
    go_indicators = ['go.mod', 'go.sum', '.go', 'main.go']
    if any(ind in ' '.join(file_names) for ind in go_indicators):
        project_info['has_go'] = True
        if project_info['type'] == 'Unknown':
            project_info['type'] = 'Go'
        else:
            project_info['type'] += '/Go'

    # Rust detection
    rust_indicators = ['Cargo.toml', 'Cargo.lock', '.rs', 'src/main.rs']
    if any(ind in ' '.join(file_names) for ind in rust_indicators):
        project_info['has_rust'] = True
        if project_info['type'] == 'Unknown':
            project_info['type'] = 'Rust'
        else:
            project_info['type'] += '/Rust'

    return project_info

def detect_build_commands(extract_dir, project_info):
    """Detect appropriate build commands for the project"""
    build_commands = []

    # Python builds
    if project_info['has_python']:
        if (extract_dir / 'setup.py').exists():
            build_commands.append({
                'command': [sys.executable, 'setup.py', 'build'],
                'description': 'Python setup.py build'
            })
        if (extract_dir / 'pyproject.toml').exists():
            build_commands.append({
                'command': [sys.executable, '-m', 'build'],
                'description': 'Python build package'
            })

    # PHP builds
    if project_info['has_php']:
        if (extract_dir / 'composer.json').exists():
            build_commands.append({
                'command': ['composer', 'install'],
                'description': 'Composer install dependencies'
            })

    # Node.js builds
        if (extract_dir / 'package.json').exists():
            package_json = extract_dir / 'package.json'
            try:
                import json
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    if 'scripts' in package_data:
                        scripts = package_data['scripts']
                        if 'build' in scripts:
                            build_commands.append({
                                'command': ['npm', 'run', 'build'],
                                'description': 'npm build script'
                            })
                        if 'compile' in scripts:
                            build_commands.append({
                                'command': ['npm', 'run', 'compile'],
                                'description': 'npm compile script'
                            })
            except:
                pass

    # Java/Maven builds
    if project_info['has_java']:
        if (extract_dir / 'pom.xml').exists():
            build_commands.append({
                'command': ['mvn', 'compile'],
                'description': 'Maven compile'
            })
        if (extract_dir / 'build.gradle').exists():
            build_commands.append({
                'command': ['./gradlew', 'build'],
                'description': 'Gradle build'
            })

    # C/C++ builds
    if project_info['has_cpp']:
        if (extract_dir / 'CMakeLists.txt').exists():
            # CMake build - need to run cmake first, then make
            build_commands.append({
                'command': ['C:\\Program Files\\CMake\\bin\\cmake.exe', '-S', '.', '-B', 'build'],
                'description': 'CMake configure'
            })
            build_commands.append({
                'command': ['C:\\Program Files\\CMake\\bin\\cmake.exe', '--build', 'build'],
                'description': 'CMake build'
            })
        elif (extract_dir / 'Makefile').exists():
            build_commands.append({
                'command': ['make'],
                'description': 'Make build'
            })
        elif (extract_dir / 'configure').exists():
            # Autotools build
            build_commands.append({
                'command': ['./configure'],
                'description': 'Configure build'
            })
            build_commands.append({
                'command': ['make'],
                'description': 'Make build'
            })

    # Go builds
    if project_info['has_go']:
        if (extract_dir / 'go.mod').exists():
            build_commands.append({
                'command': ['go', 'build', './...'],
                'description': 'Go build'
            })

    # Rust builds
    if project_info['has_rust']:
        if (extract_dir / 'Cargo.toml').exists():
            build_commands.append({
                'command': ['cargo', 'build', '--release'],
                'description': 'Cargo build release'
            })

    return build_commands

@app.route('/addons/modules/<module_name>/run_setup/<path:setup_script>', methods=['POST'])
def addons_module_run_setup(module_name, setup_script):
    """Run a setup script for a module with enhanced support"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        script_path = extract_dir / setup_script

        if not script_path.exists():
            flash(f'❌ Setup script not found: {setup_script}', 'error')
            return redirect(url_for('addons_modules'))

        import subprocess
        verbose_output = []

        # Handle different script types
        if setup_script.endswith('.py'):
            verbose_output.append(f'🐍 Running Python script: {setup_script}')
            result = subprocess.run([sys.executable, str(script_path)],
                                  capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
        elif setup_script.endswith('.sh'):
            verbose_output.append(f'🐚 Running shell script: {setup_script}')
            result = subprocess.run(['bash', str(script_path)],
                                  capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
        elif setup_script.endswith('.bat') or setup_script.endswith('.ps1'):
            verbose_output.append(f'⚡ Running PowerShell script: {setup_script}')
            result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
                                  capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
        elif setup_script.endswith('.php'):
            # PHP web-based setup scripts
            verbose_output.append(f'🐘 PHP setup script detected: {setup_script}')
            verbose_output.append(f'🌐 This appears to be a web-based installer')
            verbose_output.append(f'💡 Access it via: http://localhost:8080/addons/modules/{module_name}/web/{setup_script}')

            # Try to start a PHP development server if possible
            if (extract_dir / 'composer.json').exists() or (extract_dir / 'index.php').exists():
                try:
                    verbose_output.append('🚀 Attempting to start PHP development server...')
                    # Check if we can run PHP
                    php_check = subprocess.run(['php', '--version'], capture_output=True, text=True, timeout=10)
                    if php_check.returncode == 0:
                        verbose_output.append('✅ PHP is available on the system')
                        flash(f'🌐 PHP setup script ready: Access {setup_script} via the web interface', 'info')
                        flash(f'💡 PHP development server can be started if needed', 'info')
                    else:
                        verbose_output.append('❌ PHP not found on system')
                        flash('❌ PHP is not installed on this system', 'error')
                except:
                    verbose_output.append('❌ Could not check PHP availability')
                    flash('❌ Could not verify PHP installation', 'error')
            else:
                flash(f'ℹ️ PHP script detected but no web server setup found', 'info')

            # Show verbose output and return
            for msg in verbose_output[:5]:
                flash(msg, 'info')
            return redirect(url_for('addons_modules'))
        else:
            # Try to detect if it's executable
            if script_path.stat().st_mode & 0o111:  # Check if executable
                verbose_output.append(f'⚙️ Running executable script: {setup_script}')
                result = subprocess.run([str(script_path)],
                                      capture_output=True, text=True, cwd=str(extract_dir), timeout=300)
            else:
                flash(f'❌ Unsupported or non-executable script type: {setup_script}', 'error')
                return redirect(url_for('addons_modules'))

        # Process results for executable scripts
        if result.returncode == 0:
            flash(f'✅ Setup script executed successfully: {setup_script}', 'success')
            verbose_output.append('✅ Script completed with exit code 0')
            if result.stdout.strip():
                flash(f'📤 Output: {result.stdout.strip()[:500]}...', 'info')
                verbose_output.append(f'📤 stdout: {result.stdout.strip()[:100]}...')
        else:
            flash(f'❌ Setup script failed (exit code {result.returncode}): {setup_script}', 'error')
            verbose_output.append(f'❌ Script failed with exit code {result.returncode}')
            if result.stderr.strip():
                flash(f'📤 Error: {result.stderr.strip()[:500]}...', 'error')
                verbose_output.append(f'📤 stderr: {result.stderr.strip()[:100]}...')

        # Show verbose output
        for msg in verbose_output[:5]:
            flash(msg, 'info')

    except subprocess.TimeoutExpired:
        flash(f'⏰ Setup script timed out: {setup_script}', 'error')
    except Exception as e:
        flash(f'❌ Error running setup script: {str(e)}', 'error')

    return redirect(url_for('addons_modules'))

@app.route('/addons/modules/<module_name>/build', methods=['POST'])
def addons_module_build(module_name):
    """Build/compile a source code module"""
    try:
        # Load module info to get source directory
        modules_file = app.config['UPLOAD_FOLDER'] / 'modules.json'
        source_dir = None
        if modules_file.exists():
            try:
                with open(modules_file, 'r') as f:
                    modules = json.load(f)
                if module_name in modules:
                    source_dir = Path(modules[module_name].get('source_dir'))
            except Exception:
                pass
        
        # Find the actual module directory if source_dir not set
        if not source_dir or not source_dir.exists():
            extract_dirs = [
                app.config['UPLOAD_FOLDER'] / 'extracted',
                Path(app.root_path) / '.claude' / 'worktrees' / 'cool-elbakyan' / 'data' / 'uploads' / 'extracted'
            ]
            
            extract_dir = None
            for base_dir in extract_dirs:
                if base_dir.exists():
                    # First try exact match
                    candidate = base_dir / module_name
                    if candidate.exists() and candidate.is_dir():
                        extract_dir = candidate
                        break
                    
                    # Then try case-insensitive match
                    for item in base_dir.iterdir():
                        if item.is_dir() and item.name.lower() == module_name.lower():
                            extract_dir = item
                            break
                    
                    if extract_dir:
                        break
            
            if not extract_dir:
                flash(f'❌ Module not found: {module_name}', 'error')
                return redirect(url_for('addons_modules'))
            
            source_dir = extract_dir

        # Detect project type and build commands
        project_info = detect_project_type(source_dir)
        build_commands = detect_build_commands(source_dir, project_info)
        
        if not build_commands:
            flash(f'❌ No build commands detected for {module_name} ({project_info["type"]})', 'error')
            return redirect(url_for('addons_modules'))

        import subprocess
        verbose_output = []
        success_count = 0
        
        verbose_output.append(f'🔨 Building {module_name} ({project_info["type"]})')
        verbose_output.append(f'📁 Build directory: {source_dir}')
        
        # Execute build commands sequentially
        for i, build_cmd in enumerate(build_commands, 1):
            cmd_desc = build_cmd['description']
            cmd_args = build_cmd['command']
            
            verbose_output.append(f'⚙️ Step {i}/{len(build_commands)}: {cmd_desc}')
            verbose_output.append(f'💻 Command: {" ".join(cmd_args)}')
            
            try:
                # Set up environment for build
                env = os.environ.copy()
                env['PATH'] = os.environ.get('PATH', '')
                
                result = subprocess.run(
                    cmd_args,
                    cwd=str(source_dir),
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout for builds
                    env=env
                )
                
                if result.returncode == 0:
                    success_count += 1
                    verbose_output.append(f'✅ Step {i} completed successfully')
                    if result.stdout.strip():
                        # Show first few lines of output
                        stdout_lines = result.stdout.strip().split('\n')[:3]
                        for line in stdout_lines:
                            if line.strip():
                                verbose_output.append(f'📤 {line.strip()[:100]}')
                else:
                    verbose_output.append(f'❌ Step {i} failed with exit code {result.returncode}')
                    if result.stderr.strip():
                        # Show error output
                        stderr_lines = result.stderr.strip().split('\n')[:3]
                        for line in stderr_lines:
                            if line.strip():
                                verbose_output.append(f'📤 ERROR: {line.strip()[:100]}')
                    break  # Stop on first failure
                    
            except subprocess.TimeoutExpired:
                verbose_output.append(f'⏰ Step {i} timed out after 10 minutes')
                break
            except Exception as e:
                verbose_output.append(f'❌ Step {i} error: {str(e)}')
                break
        
        # Report results
        if success_count == len(build_commands):
            flash(f'✅ Build completed successfully: {module_name}', 'success')
            verbose_output.append(f'🎉 All {len(build_commands)} build steps completed')
        else:
            flash(f'❌ Build failed: {module_name} ({success_count}/{len(build_commands)} steps completed)', 'error')
            verbose_output.append(f'⚠️ Build incomplete: {success_count}/{len(build_commands)} steps completed')
        
        # Show verbose output (limit to prevent flash overflow)
        for msg in verbose_output[:8]:
            flash(msg, 'info')
            
    except Exception as e:
        flash(f'❌ Error during build: {str(e)}', 'error')

    return redirect(url_for('addons_modules'))

@app.route('/addons/modules/<module_name>/')
def addons_module_root(module_name):
    """Serve the root page of a web-accessible module (for PHP/Node.js apps, etc.)"""
    try:
        # Find the actual module directory by searching both locations
        extract_dirs = [
            app.config['UPLOAD_FOLDER'] / 'extracted',
            Path(app.root_path) / '.claude' / 'worktrees' / 'cool-elbakyan' / 'data' / 'uploads' / 'extracted'
        ]
        
        extract_dir = None
        for base_dir in extract_dirs:
            if base_dir.exists():
                # First try exact match
                candidate = base_dir / module_name
                if candidate.exists() and candidate.is_dir():
                    extract_dir = candidate
                    break
                
                # Then try case-insensitive match
                for item in base_dir.iterdir():
                    if item.is_dir() and item.name.lower() == module_name.lower():
                        extract_dir = item
                        break
                
                if extract_dir:
                    break
        
        if not extract_dir:
            return f"Module not found: {module_name}", 404

        # Detect project type
        project_info = detect_project_type(extract_dir)

        # Look for index files in order of preference
        # First check the root directory
        index_files = ['index.php', 'index.html', 'index.htm', 'install.php', 'default.php', 'default.html']
        index_file = None
        
        # Check root directory first
        for filename in index_files:
            candidate = extract_dir / filename
            if candidate.exists() and candidate.is_file():
                index_file = candidate
                break
        
        # If no index file in root, check subdirectories
        if not index_file:
            for subdir in extract_dir.iterdir():
                if subdir.is_dir():
                    for filename in index_files:
                        candidate = subdir / filename
                        if candidate.exists() and candidate.is_file():
                            index_file = candidate
                            break
                    if index_file:
                        break

        if index_file:
            # Serve the index file
            file_path = index_file  # Use the full path directly

            if file_path.suffix.lower() == '.php':
                # Execute PHP file using local PHP binary
                import subprocess
                try:
                    # Use the local PHP installation
                    php_path = Path(app.root_path) / 'php' / 'php.exe'
                    if not php_path.exists():
                        # Fallback to system PHP if local not found
                        php_path = 'php'
                    
                    # Execute PHP with the file
                    result = subprocess.run(
                        [str(php_path), str(file_path)],
                        cwd=str(extract_dir),
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        return result.stdout, 200, {'Content-Type': 'text/html'}
                    else:
                        # PHP execution failed, show error
                        error_content = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>{module_name} - PHP Error</title>
                            <style>
                                body {{ font-family: monospace; background: #1a1a1a; color: #e0e0e0; padding: 20px; }}
                                .error {{ background: #f44336; color: white; padding: 15px; border-radius: 5px; }}
                            </style>
                        </head>
                        <body>
                            <div class="error">
                                <strong>PHP Execution Error:</strong><br>
                                {result.stderr}
                            </div>
                            <h2>PHP Source Code:</h2>
                            <pre>{open(file_path, 'r', encoding='utf-8', errors='ignore').read()}</pre>
                        </body>
                        </html>
                        """
                        return error_content, 500
                        
                except subprocess.TimeoutExpired:
                    return "PHP execution timed out", 504
                except Exception as e:
                    return f"PHP execution failed: {str(e)}", 500

            else:
                # For HTML files, serve directly
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return content, 200, {'Content-Type': 'text/html'}

        else:
            # No index file found, show directory listing
            files = []
            for item in extract_dir.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(extract_dir)
                    files.append(str(rel_path))

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{module_name} - Directory Listing</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #e0e0e0; padding: 20px; }}
                    .file-list {{ background: #2a2a2a; padding: 15px; border-radius: 5px; }}
                    .file-link {{ color: #4CAF50; text-decoration: none; }}
                    .file-link:hover {{ text-decoration: underline; }}
                    .info {{ background: #2196F3; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="info">
                    <strong>Module:</strong> {module_name}<br>
                    <strong>Type:</strong> {project_info.get('type', 'Unknown')}<br>
                    <strong>Frameworks:</strong> {', '.join(project_info.get('frameworks', [])) or 'None detected'}
                </div>
                <h2>Files in {module_name}:</h2>
                <div class="file-list">
            """

            for file in sorted(files):
                html_content += f'<div><a class="file-link" href="/addons/modules/{module_name}/web/{file}">{file}</a></div>'

            html_content += """
                </div>
            </body>
            </html>
            """
            return html_content

    except Exception as e:
        return f"Error serving module {module_name}: {str(e)}", 500

@app.route('/addons/modules/<module_name>/web/<path:filepath>')
def addons_module_web(module_name, filepath):
    """Serve web-accessible files from a module (for PHP setup scripts, etc.)"""
    try:
        # Find the actual module directory by searching both locations
        extract_dirs = [
            app.config['UPLOAD_FOLDER'] / 'extracted',
            Path(app.root_path) / '.claude' / 'worktrees' / 'cool-elbakyan' / 'data' / 'uploads' / 'extracted'
        ]
        
        extract_dir = None
        for base_dir in extract_dirs:
            if base_dir.exists():
                # First try exact match
                candidate = base_dir / module_name
                if candidate.exists() and candidate.is_dir():
                    extract_dir = candidate
                    break
                
                # Then try case-insensitive match
                for item in base_dir.iterdir():
                    if item.is_dir() and item.name.lower() == module_name.lower():
                        extract_dir = item
                        break
                
                if extract_dir:
                    break
        
        if not extract_dir:
            return f"Module not found: {module_name}", 404
            
        file_path = extract_dir / filepath

        if not file_path.is_file():
            return f"Path is not a file: {filepath}", 400

        # Security check - only allow certain file types
        allowed_extensions = {'.php', '.html', '.htm', '.css', '.js', '.json', '.txt', '.md'}
        if file_path.suffix.lower() not in allowed_extensions:
            return f"File type not allowed for web access: {file_path.suffix}", 403

        # For PHP files, execute them using local PHP
        if file_path.suffix.lower() == '.php':
            import subprocess
            try:
                # Use the local PHP installation
                php_path = Path(app.root_path) / 'php' / 'php.exe'
                if not php_path.exists():
                    # Fallback to system PHP if local not found
                    php_path = 'php'
                
                # Execute PHP with the file
                result = subprocess.run(
                    [str(php_path), str(file_path)],
                    cwd=str(extract_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return result.stdout, 200, {'Content-Type': 'text/html'}
                else:
                    # PHP execution failed, show error
                    error_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>{module_name} - PHP Error</title>
                        <style>
                            body {{ font-family: monospace; background: #1a1a1a; color: #e0e0e0; padding: 20px; }}
                            .error {{ background: #f44336; color: white; padding: 15px; border-radius: 5px; }}
                        </style>
                    </head>
                    <body>
                        <div class="error">
                            <strong>PHP Execution Error:</strong><br>
                            {result.stderr}
                        </div>
                        <h2>PHP Source Code:</h2>
                        <pre>{open(file_path, 'r', encoding='utf-8', errors='ignore').read()}</pre>
                    </body>
                    </html>
                    """
                    return error_content, 500
                    
            except subprocess.TimeoutExpired:
                return "PHP execution timed out", 504
            except Exception as e:
                return f"PHP execution failed: {str(e)}", 500

        # For other allowed file types, serve them directly
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Basic content type detection
        content_type = 'text/plain'
        if file_path.suffix.lower() in ['.html', '.htm']:
            content_type = 'text/html'
        elif file_path.suffix.lower() == '.css':
            content_type = 'text/css'
        elif file_path.suffix.lower() == '.js':
            content_type = 'application/javascript'
        elif file_path.suffix.lower() == '.json':
            content_type = 'application/json'

        return content, 200, {'Content-Type': content_type}

    except Exception as e:
        return f"Error serving file: {str(e)}", 500

@app.route('/addons/modules/<module_name>/start', methods=['POST'])
def addons_module_start(module_name):
    """Start a module service"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        
        if not extract_dir.exists():
            return {'error': f'Module not found: {module_name}'}, 404
        
        # Check if already running
        import psutil
        running_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any(module_name in str(cmd) for cmd in proc.info['cmdline']):
                    running_processes.append(proc.info)
            except:
                pass
        
        if running_processes:
            return {'message': f'Service already running (PID: {running_processes[0]["pid"]})', 'status': 'running', 'pid': running_processes[0]['pid']}
        
        # Detect how to start the service
        import subprocess
        import threading
        
        # Look for startup scripts or main files
        startup_commands = []
        
        # Python modules
        if (extract_dir / 'main.py').exists():
            startup_commands.append([sys.executable, 'main.py'])
        elif (extract_dir / 'app.py').exists():
            startup_commands.append([sys.executable, 'app.py'])
        elif (extract_dir / 'run.py').exists():
            startup_commands.append([sys.executable, 'run.py'])
        elif (extract_dir / '__main__.py').exists():
            startup_commands.append([sys.executable, '-m', module_name])
        
        # Node.js
        elif (extract_dir / 'server.js').exists():
            startup_commands.append(['node', 'server.js'])
        elif (extract_dir / 'app.js').exists():
            startup_commands.append(['node', 'app.js'])
        elif (extract_dir / 'index.js').exists():
            startup_commands.append(['node', 'index.js'])
        
        # PHP
        elif (extract_dir / 'index.php').exists():
            startup_commands.append(['php', '-S', 'localhost:0', 'index.php'])
        
        if startup_commands:
            cmd = startup_commands[0]
            process = subprocess.Popen(cmd, cwd=str(extract_dir), 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Store process info (in a real implementation, you'd use a proper process manager)
            app.config.setdefault('running_services', {})[module_name] = {
                'process': process,
                'pid': process.pid,
                'start_time': datetime.now(),
                'command': cmd
            }
            
            return {'message': f'Service started successfully (PID: {process.pid})', 'status': 'starting', 'pid': process.pid}
        else:
            return {'error': 'No suitable startup script found'}, 400
            
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/addons/modules/<module_name>/stop', methods=['POST'])
def addons_module_stop(module_name):
    """Stop a module service"""
    try:
        running_services = app.config.get('running_services', {})
        service_info = running_services.get(module_name)
        
        if not service_info:
            # Check if process is still running
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any(module_name in str(cmd) for cmd in proc.info['cmdline']):
                        proc.kill()
                        return {'message': f'Service stopped (PID: {proc.info["pid"]})', 'status': 'stopped'}
                except:
                    pass
            return {'message': 'Service not running', 'status': 'stopped'}
        
        # Stop the process
        process = service_info['process']
        try:
            process.terminate()
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        
        # Remove from running services
        del running_services[module_name]
        
        return {'message': 'Service stopped successfully', 'status': 'stopped'}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/addons/modules/<module_name>/status')
def addons_module_status(module_name):
    """Get status of a module service"""
    try:
        running_services = app.config.get('running_services', {})
        service_info = running_services.get(module_name)
        
        if service_info:
            process = service_info['process']
            if process.poll() is None:  # Still running
                return {
                    'status': 'running',
                    'pid': process.pid,
                    'start_time': service_info['start_time'].isoformat(),
                    'command': service_info['command']
                }
            else:
                # Process ended, clean up
                del running_services[module_name]
        
        # Check if process is still running by name
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any(module_name in str(cmd) for cmd in proc.info['cmdline']):
                    return {
                        'status': 'running',
                        'pid': proc.info['pid'],
                        'command': proc.info['cmdline']
                    }
            except:
                pass
        
        return {'status': 'stopped'}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/addons/modules/delete_all', methods=['POST'])
def delete_all_modules():
    """Delete all installed addon modules"""
    try:
        import shutil
        
        deleted_modules = []
        errors = []
        
        # Check both current workspace and the cool-elbakyan workspace
        extract_dirs = [
            app.config['UPLOAD_FOLDER'] / 'extracted',
            Path(__file__).parent / '.claude' / 'worktrees' / 'cool-elbakyan' / 'data' / 'uploads' / 'extracted'
        ]
        
        for extract_dir in extract_dirs:
            if extract_dir.exists():
                for module_dir in extract_dir.iterdir():
                    if module_dir.is_dir():
                        try:
                            # Stop any running services for this module first
                            running_services = app.config.get('running_services', {})
                            if module_dir.name in running_services:
                                service_info = running_services[module_dir.name]
                                process = service_info['process']
                                try:
                                    process.terminate()
                                    process.wait(timeout=5)
                                except:
                                    try:
                                        process.kill()
                                    except:
                                        pass
                                del running_services[module_dir.name]
                            
                            # Delete the module directory
                            shutil.rmtree(module_dir)
                            deleted_modules.append(module_dir.name)
                            
                        except Exception as e:
                            errors.append(f"Failed to delete {module_dir.name}: {str(e)}")
        
        # Also clean up any empty parent directories
        for extract_dir in extract_dirs:
            if extract_dir.exists() and not any(extract_dir.iterdir()):
                try:
                    extract_dir.rmdir()
                except:
                    pass
        
        if errors:
            return jsonify({'success': False, 'error': '; '.join(errors), 'deleted_count': len(deleted_modules)}), 500
        else:
            return jsonify({'success': True, 'message': f'Successfully deleted {len(deleted_modules)} modules', 'deleted_count': len(deleted_modules)})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== MODULE MANAGER API =====

@app.route('/addons/modules/<module_name>/api/files')
def module_files_api(module_name):
    """API endpoint to get module files as JSON"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        if not extract_dir.exists():
            return jsonify({'error': 'Module not found'}), 404
        
        files = []
        def scan_directory(path, relative_path=''):
            try:
                for item in sorted(path.iterdir()):
                    if item.is_file():
                        try:
                            size = item.stat().st_size
                            modified = datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            files.append({
                                'name': item.name,
                                'path': str(item.relative_to(extract_dir)),
                                'size': size,
                                'modified': modified,
                                'type': 'file',
                                'extension': item.suffix.lower()
                            })
                        except:
                            pass
                    elif item.is_dir():
                        try:
                            files.append({
                                'name': item.name,
                                'path': str(item.relative_to(extract_dir)),
                                'size': 0,
                                'modified': datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                'type': 'directory',
                                'extension': ''
                            })
                            scan_directory(item, str(item.relative_to(extract_dir)))
                        except:
                            pass
            except:
                pass
        
        scan_directory(extract_dir)
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/addons/modules/<module_name>/api/file', methods=['GET', 'POST', 'PUT', 'DELETE'])
def module_file_api(module_name):
    """API endpoint for file operations (read, save, delete)"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        if not extract_dir.exists():
            return jsonify({'error': 'Module not found'}), 404
        
        file_path = request.args.get('path', '')
        if not file_path:
            return jsonify({'error': 'File path required'}), 400
        
        full_path = extract_dir / file_path
        full_path = full_path.resolve()
        
        # Security check - ensure path is within module directory
        if not str(full_path).startswith(str(extract_dir)):
            return jsonify({'error': 'Access denied'}), 403
        
        if request.method == 'GET':
            # Read file
            if not full_path.exists() or not full_path.is_file():
                return jsonify({'error': 'File not found'}), 404
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return jsonify({'content': content, 'path': file_path})
            except UnicodeDecodeError:
                return jsonify({'error': 'Binary file - cannot edit in text mode'}), 400
            except Exception as e:
                return jsonify({'error': f'Error reading file: {str(e)}'}), 500
        
        elif request.method in ['POST', 'PUT']:
            # Save file
            content = request.json.get('content', '') if request.is_json else request.form.get('content', '')
            if content is None:
                return jsonify({'error': 'Content required'}), 400
            
            try:
                # Create directory if it doesn't exist
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return jsonify({'success': True, 'message': 'File saved successfully'})
            except Exception as e:
                return jsonify({'error': f'Error saving file: {str(e)}'}), 500
        
        elif request.method == 'DELETE':
            # Delete file
            if not full_path.exists():
                return jsonify({'error': 'File not found'}), 404
            
            try:
                if full_path.is_file():
                    full_path.unlink()
                elif full_path.is_dir():
                    import shutil
                    shutil.rmtree(full_path)
                
                return jsonify({'success': True, 'message': 'File deleted successfully'})
            except Exception as e:
                return jsonify({'error': f'Error deleting file: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/addons/modules/<module_name>/api/upload', methods=['POST'])
def module_upload_api(module_name):
    """API endpoint for uploading files to a module"""
    try:
        extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
        if not extract_dir.exists():
            return jsonify({'error': 'Module not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get target path
        target_path = request.form.get('path', '')
        if target_path:
            full_target_dir = extract_dir / target_path
            full_target_dir.mkdir(parents=True, exist_ok=True)
        else:
            full_target_dir = extract_dir
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = full_target_dir / filename
        
        file.save(file_path)
        
        return jsonify({'success': True, 'message': f'File {filename} uploaded successfully', 'path': str(file_path.relative_to(extract_dir))})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/addons/modules/<module_name>/api/ui_integration', methods=['POST'])
def module_ui_integration_api(module_name):
    """API endpoint to add/remove module from main UI navigation"""
    try:
        action = request.json.get('action') if request.is_json else request.form.get('action')
        if action not in ['add', 'remove']:
            return jsonify({'error': 'Invalid action. Must be "add" or "remove"'}), 400
        
        # Get current UI modules
        ui_modules_file = app.config['UPLOAD_FOLDER'] / 'ui_modules.json'
        ui_modules = {}
        
        if ui_modules_file.exists():
            try:
                with open(ui_modules_file, 'r') as f:
                    ui_modules = json.load(f)
            except:
                ui_modules = {}
        
        if action == 'add':
            # Add module to UI
            extract_dir = app.config['UPLOAD_FOLDER'] / 'extracted' / module_name
            if not extract_dir.exists():
                return jsonify({'error': 'Module not found'}), 404
            
            # Try to detect if module has a web interface
            web_files = []
            for ext in ['.html', '.htm', '.php']:
                web_files.extend(list(extract_dir.rglob(f'*{ext}')))
            
            main_file = None
            if web_files:
                # Look for index.html, main.html, app.html, etc.
                priority_files = ['index.html', 'index.htm', 'main.html', 'app.html', 'home.html']
                for priority in priority_files:
                    for web_file in web_files:
                        if web_file.name.lower() == priority:
                            main_file = str(web_file.relative_to(extract_dir))
                            break
                    if main_file:
                        break
                
                if not main_file and web_files:
                    main_file = str(web_files[0].relative_to(extract_dir))
            
            ui_modules[module_name] = {
                'name': module_name,
                'url': f'/addons/modules/{module_name}/web/{main_file}' if main_file else f'/addons/modules/{module_name}/manager',
                'icon': '🧩',
                'added_at': datetime.now().isoformat()
            }
            
        elif action == 'remove':
            # Remove module from UI
            if module_name in ui_modules:
                del ui_modules[module_name]
            else:
                return jsonify({'error': 'Module not in UI'}), 404
        
        # Save updated UI modules
        with open(ui_modules_file, 'w') as f:
            json.dump(ui_modules, f, indent=2)
        
        return jsonify({'success': True, 'message': f'Module {action}ed to/from UI successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resources')

@requires_permission('resources')
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




@app.route('/masterchief_code_ui')
@requires_permission('web_ide')
def masterchief_code_ui():
    """Serve the MasterChief Code UI (Web IDE)."""
    try:
        ide_path = Path(__file__).parent / 'web_ide.html'
        if ide_path.exists():
            return ide_path.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/html; charset=utf-8'}
        else:
            return f'<h1>MasterChief Code UI</h1><p>Web IDE file not found at {ide_path}</p>', 404
    except Exception as e:
        app.logger.exception('Failed to serve MasterChief Code UI')
        return f'<h1>Error</h1><p>Failed to load Code UI: {e}</p>', 500


@app.route('/echo-chat')
@requires_permission('echo-chat')
def echo_chat():
    echo_art = Echo.get_compact_greeting()
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', ECHO_CHAT_TEMPLATE.replace('{% extends "base.html" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')), echo_art=echo_art, request=request, get_flashed_messages=get_flashed_messages)

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


@app.route('/api/gguf/models')
def api_gguf_models():
    try:
        models_dir = Path(__file__).parent / 'models'
        models = []
        if models_dir.exists():
            for f in models_dir.glob('*.gguf'):
                models.append(str(f.relative_to(Path(__file__).parent)))
        bot = get_chat_bot()
        current = None
        if hasattr(bot, '_model_path') and bot._model_path:
            current = str(Path(bot._model_path).relative_to(Path(__file__).parent)) if Path(bot._model_path).is_relative_to(Path(__file__).parent) else bot._model_path
        return jsonify({'models': models, 'current': current})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gguf/select', methods=['POST'])
def api_gguf_select():
    try:
        data = request.get_json() or {}
        model = data.get('model', '')
        bot = get_chat_bot()
        if model:
            success = bot.reload_model(model_name=model)
            current = str(Path(bot._model_path).relative_to(Path(__file__).parent)) if Path(bot._model_path).is_relative_to(Path(__file__).parent) else bot._model_path
            return jsonify({'success': success, 'current': current})
        else:
            # clear model
            bot._model_path = None
            return jsonify({'success': True, 'current': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500





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
                models.append(str(f.relative_to(Path.cwd())))
        return jsonify({'models': models})
    except Exception as e:
        app.logger.exception('List models failed')
        return jsonify({'error': str(e)}), 500





@app.route('/echo-train')

@requires_permission('training')
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





@app.route('/about')

def about_page():

    return send_file('about.html')





@app.route('/pipelines')

def pipelines_page():

    return send_file('pipelines.html')





@app.route('/cloud')

def cloud_page():

    return send_file('cloud_dashboard.html')





@app.route('/secrets')

def secrets_page():

    return send_file('secrets_vault.html')





@app.route('/echo-memory')

def echo_memory_page():

    return send_file('echo_memory.html')





@app.route('/marketplace')

def marketplace_page():

    return send_file('marketplace.html')





@app.route('/notifications')

def notifications_page():

    return send_file('notifications.html')





@app.route('/rbac')
@requires_permission('rbac')
def rbac_page():
    return send_file('rbac.html')





# TF Wizard routes
if TF_WIZARD_AVAILABLE:
    print("DEBUG: Registering TF Wizard routes")
    @app.route('/tf_wizard')
    def tf_wizard_index():
        """Serve the TF Wizard main page"""
        import os
        from jinja2 import Environment, FileSystemLoader
        tf_wizard_dir = os.path.dirname(tf_wizard_app.__file__)
        templates_dir = os.path.join(tf_wizard_dir, 'templates')
        env = Environment(loader=FileSystemLoader(templates_dir), autoescape=tf_wizard_app.templates.autoescape)
        tmpl = env.get_template("index.html")
        return tmpl.render()

    @app.route('/tf_wizard/generate', methods=['POST'])
    def tf_wizard_generate():
        """Generate Terraform module zip"""
        try:
            data = request.get_json()
            zip_bytes = generate_module_zip(data)
            from flask import Response
            import io
            return Response(io.BytesIO(zip_bytes), 
                          mimetype="application/zip", 
                          headers={"Content-Disposition": f"attachment; filename=terraform_module_{data.get('module_name','module')}.zip"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/tf_wizard/schema/apply', methods=['POST'])
    def tf_wizard_apply_schema():
        """Apply JSON schema to generate variables"""
        try:
            from jsonschema import Draft7Validator
            payload = request.get_json()
            schema = payload.get('schema')
            if not schema:
                return jsonify({"error": "schema is required"}), 400
            
            # Validate schema is valid JSON Schema (Draft7)
            Draft7Validator.check_schema(schema)
            
            props = schema.get('properties', {})
            vars_out = []
            def build_var(name, meta):
                js_type = meta.get('type')
                # Use generator helper to build tf_type (supports dict schema too)
                tf_type = tf_type_from_spec(meta) if isinstance(meta, dict) else tf_type_from_spec(js_type or '')
                
                v = {
                    'name': name,
                    'type': js_type or 'string',
                    'tf_type': tf_type,
                    'default': meta.get('default') if isinstance(meta, dict) and 'default' in meta else None,
                    'description': meta.get('description', '') if isinstance(meta, dict) else '',
                }
                # if object with nested properties, return nested details
                if isinstance(meta, dict) and meta.get('type') == 'object' and isinstance(meta.get('properties'), dict):
                    nested = []
                    for nk, nv in meta.get('properties', {}).items():
                        nested.append(build_var(nk, nv))
                    v['nested'] = nested
                if isinstance(meta, dict) and 'enum' in meta:
                    v['enum'] = meta.get('enum')
                return v

            for name, meta in props.items():
                vars_out.append(build_var(name, meta))
            return jsonify({'variables': vars_out})
        except Exception as e:
            return jsonify({"error": str(e)}), 400





@app.route('/web_ide')

def web_ide():

    """Serve a local `web_ide.html` file if present to restore the Web IDE quickly.

    Falls back to the root index if the file is missing.

    """

    try:

        p = Path(__file__).resolve().parent / 'caf.html'

        if p.exists():

            return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/html; charset=utf-8'}

    except Exception:

        app.logger.exception('Failed to serve web_ide.html')

    # Fall back to main index route if available

    try:

        return redirect(url_for('index'))

    except Exception:

        return ('Web IDE not available', 404)

@app.route('/iac_manager')

def iac_manager():

    """Serve the alternate TF Wizard from the cool-elbakyan worktree."""

    try:

        p = Path(r'C:\Users\Echo\masterchief\.claude\worktrees\cool-elbakyan\web_tf_wizard.html')

        if p.exists():

            return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/html; charset=utf-8'}

    except Exception:

        app.logger.exception('Failed to serve alternate web_tf_wizard.html')

    # Fall back to main web_tf_wizard if alternate is not available

    try:

        return redirect(url_for('web_tf_wizard'))

    except Exception:

        return ('Alternate TF Wizard not available', 404)

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


@app.route('/features')
def features_page():
    """Serve the Feature Management page."""
    try:
        p = Path(__file__).resolve().parent / 'features' / 'templates' / 'feature_manager.html'
        if p.exists():
            return p.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception:
        app.logger.exception('Failed to serve feature_manager.html')
    return jsonify({'error': 'Feature manager not available'}), 404


@app.route('/api/features/enabled')
def api_features_enabled():
    """Return list of enabled features for the toolbar."""
    if not FEATURE_MANAGER_AVAILABLE:
        return jsonify([])
    try:
        fm = get_feature_manager()
        if fm is None:
            return jsonify([])
        enabled = []
        # Include features loaded from the feature manager
        for name, handler in fm.features.items():
            if handler.config.enabled:
                enabled.append({
                    'key': handler.config.name,
                    'label': handler.config.display_name,
                    'addon': 'features',
                    'description': handler.config.description
                })
        # Include features from feature configs that are marked enabled
        for name, config in fm.feature_configs.items():
            if config.enabled and name not in fm.features:
                enabled.append({
                    'key': config.name,
                    'label': config.display_name,
                    'addon': 'features',
                    'description': config.description
                })
        return jsonify(enabled)
    except Exception as e:
        app.logger.exception('Failed to list enabled features')
        return jsonify([])


@app.route('/api/features/settings', methods=['GET', 'POST'])
def api_features_settings():
    """Get or save API management settings."""
    settings_file = Path(__file__).resolve().parent / 'api_settings.json'
    
    if request.method == 'GET':
        # Load settings from file
        try:
            if settings_file.exists():
                settings = json.loads(settings_file.read_text(encoding='utf-8'))
                return jsonify(settings)
            else:
                # Return default settings
                return jsonify({
                    'core_features': {
                        'masterchief_code_ui': True,
                        'web_ide': True,
                        'caf_generator': True,
                        'echo_chat': True
                    },
                    'development_tools': {
                        'github_integration': True,
                        'azure_integration': True,
                        'cloud_dashboard': True,
                        'pipelines': True
                    },
                    'system_management': {
                        'rbac': True,
                        'notifications': True,
                        'marketplace': True,
                        'app_management': True
                    },
                    'advanced_features': {
                        'echo_memory': True,
                        'scenario_bot': True,
                        'irc_bridge': True,
                        'data_ingestion': True
                    }
                })
        except Exception as e:
            app.logger.exception('Failed to load API settings')
            return jsonify({'error': 'Failed to load settings'}), 500
    
    elif request.method == 'POST':
        # Save settings to file
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate the structure
            required_categories = ['core_features', 'development_tools', 'system_management', 'advanced_features']
            for category in required_categories:
                if category not in data:
                    return jsonify({'error': f'Missing category: {category}'}), 400
            
            # Save to file
            settings_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
            return jsonify({'success': True, 'message': 'Settings saved successfully'})
        except Exception as e:
            app.logger.exception('Failed to save API settings')
            return jsonify({'error': 'Failed to save settings'}), 500


@app.route('/feature/run/<path:feature_key>', methods=['POST'])
def feature_run(feature_key):
    """Run a feature by key. Supports feature manager features and addon-registered features."""
    if not FEATURE_MANAGER_AVAILABLE:
        return jsonify({'success': False, 'error': 'Feature manager not available'}), 503
    try:
        fm = get_feature_manager()
        if fm is None:
            return jsonify({'success': False, 'error': 'Feature manager not initialized'}), 503
        data = request.get_json(silent=True) or {}
        # Look up the feature in loaded features
        if feature_key in fm.features:
            handler = fm.features[feature_key]
            if handler.instance and callable(getattr(handler.instance, 'run', None)):
                result = handler.instance.run(**data)
                return jsonify({'success': True, 'result': result})
            else:
                return jsonify({'success': True, 'result': f'Feature {feature_key} is enabled but has no run method'})
        # Check feature configs (not yet loaded)
        if feature_key in fm.feature_configs:
            return jsonify({'success': False, 'error': f'Feature {feature_key} is configured but not enabled. Enable it first.'})
        return jsonify({'success': False, 'error': f'Feature {feature_key} not found'}), 404
    except Exception as e:
        app.logger.exception('Failed to run feature %s', feature_key)
        return jsonify({'success': False, 'error': str(e)}), 500


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

    print('DEBUG: Starting MasterChief...')
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

    # Handle Windows console issues with Flask banner
    try:
        app.run(host='0.0.0.0',port=args.port,debug=args.debug)
    except OSError as e:
        if 'Windows error 6' in str(e):
            print(f"⚠️  Windows console error encountered, but server should be running on http://localhost:{args.port}")
            print("This is a known Windows console handle issue - the application is still functional.")
            # Keep the process alive
            import time
            while True:
                time.sleep(1)
        else:
            raise

