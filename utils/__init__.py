"""
MasterChief Utilities Module

Contains utility functions, helpers, and configuration utilities
used throughout the application.
"""

import os
import sys
import time
import threading
import shutil
import json
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename


def _interpreter_cmd_for_path(p: Path, requested_shell=None):
    """
    Determine an interpreter command for a given script path.
    """
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


def _start_cleanup_thread(retention_days=30):
    """
    Start a background thread to clean up old model output files.
    """
    def runner():
        while True:
            try:
                base = Path(__file__).resolve().parent.parent / 'data' / 'models_output'
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
                            # Import app logger if available
                            try:
                                from flask import current_app
                                current_app.logger.exception('Failed to archive old job %s', d)
                            except ImportError:
                                pass
                # sleep between scans
                time.sleep(60*60*6)
            except Exception:
                # Import app logger if available
                try:
                    from flask import current_app
                    current_app.logger.exception('Cleanup thread error')
                except ImportError:
                    pass
                time.sleep(60*60)
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()


def _env_bool(name, default=False):
    """
    Parse environment variable as boolean.
    """
    v = os.environ.get(name)
    if v is None:
        return default
    return str(v).strip().lower() in ('1', 'true', 'yes', 'on')


def _parse_bool_val(v, default=None):
    """
    Generic value->bool parser.
    """
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


def _start_output_cleanup_thread(retention_days=None, interval_hours=24):
    """
    Start a background thread to clean up old echo output files.
    """
    retention_days = retention_days if retention_days is not None else 30

    def runner():
        outdir = Path(__file__).resolve().parent.parent / 'data' / 'echo_chat_outputs'
        while True:
            try:
                if outdir.exists():
                    for p in outdir.glob('*.txt'):
                        try:
                            age_days = (time.time() - p.stat().st_mtime) / (60*60*24)
                            if age_days > retention_days:
                                p.unlink()
                        except Exception:
                            # Import app logger if available
                            try:
                                from flask import current_app
                                current_app.logger.exception('Failed to prune old echo output %s', p)
                            except ImportError:
                                pass
                time.sleep(interval_hours * 3600)
            except Exception:
                # Import app logger if available
                try:
                    from flask import current_app
                    current_app.logger.exception('Echo output cleanup thread error')
                except ImportError:
                    pass
                time.sleep(3600)
    t = threading.Thread(target=runner, daemon=True)
    t.start()


def get_default_model_path():
    """
    Get the default model path from configuration or fallback.
    """
    cfg = Path(__file__).resolve().parent.parent / 'data' / 'echo_model.json'
    if cfg.exists():
        try:
            return json.loads(cfg.read_text(encoding='utf-8')).get('model')
        except Exception:
            return None
    # sensible fallback (do not force existence here)
    candidate = Path.cwd() / 'models' / 'Phi-3-mini-4k-instruct-q4.gguf'
    return str(candidate) if candidate.exists() else None


def _safe_script_path(filename: str, scripts_folder=None):
    """
    Safely resolve a script path within the scripts folder.
    """
    try:
        fname = secure_filename(filename)
        if not fname:
            return None
        if scripts_folder is None:
            scripts_folder = Path(__file__).resolve().parent.parent / 'data' / 'scripts'
        return Path(scripts_folder) / fname
    except Exception:
        return None


def load_enabled_modules(modules_config=None):
    """
    Load enabled modules configuration.
    """
    if modules_config is None:
        modules_config = Path(__file__).resolve().parent.parent / 'data' / 'modules.json'

    default_modules = {
        'rbac': {'enabled': True, 'db_path': 'data/rbac.json'},
        'vault': {'enabled': True, 'db_path': 'data/vault.json', 'key_path': 'data/vault.key', 'audit_path': 'data/vault_audit.json'},
        'notification': {'enabled': True, 'db_path': 'data/notifications.json', 'channels_path': 'data/notification_channels.json', 'rules_path': 'data/notification_rules.json'},
        'pipeline': {'enabled': True, 'db_path': 'data/pipelines.json', 'runs_path': 'data/pipeline_runs.json'},
        'cloud': {'enabled': True, 'db_path': 'data/cloud_accounts.json'},
        'memory': {'enabled': True, 'memories_path': 'data/echo_memories.jsonl', 'index_path': 'data/echo_memory_index.json'},
        'marketplace': {'enabled': True, 'db_path': 'data/marketplace.json'},
        'script': {'enabled': True}
    }

    if modules_config.exists():
        try:
            loaded = json.loads(modules_config.read_text())
            # Merge with defaults
            for k, v in default_modules.items():
                if k not in loaded:
                    loaded[k] = v
            return loaded
        except:
            pass
    return default_modules