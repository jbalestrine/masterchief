#!/usr/bin/env python3
"""MasterChief Flask Web Application - All-in-One File"""
import sys
import os

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
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
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
app=Flask(__name__)
app.config['SECRET_KEY']='masterchief-secret-key-change-in-production'
app.jinja_env.filters['b64encode'] = lambda s: base64.urlsafe_b64encode(s.encode()).decode()
app.config['ADMIN_TOKEN'] = os.environ.get('ADMIN_TOKEN') or None
app.config['BASIC_AUTH_USER'] = os.environ.get('BASIC_AUTH_USER') or None
app.config['BASIC_AUTH_PASS'] = os.environ.get('BASIC_AUTH_PASS') or None
_data_dir=Path(__file__).parent/'data'
app.config['UPLOAD_FOLDER']=_data_dir/'uploads'
app.config['SCRIPTS_FOLDER']=_data_dir/'scripts'
app.config['JAMROOM_DB']=_data_dir/'jamroom.json'
app.config['SHOUTCAST_DB']=_data_dir/'shoutcast.json'
app.config['MAX_CONTENT_LENGTH']=100*1024*1024
for folder in [app.config['UPLOAD_FOLDER'],app.config['SCRIPTS_FOLDER'],_data_dir]:
	folder.mkdir(parents=True,exist_ok=True)

# Optionally force a default model for debugging via ECHO_FORCE_MODEL.
# If set (or the chosen fallback exists), persist it to data/echo_model.json
# so `/api/echo/preload_model` and the bot prefer this model.
try:
	forced_model = os.environ.get('ECHO_FORCE_MODEL') or None
	# sensible fallback for debugging (update if you prefer another model)
	if not forced_model:
		forced_model = str(Path.cwd() / 'models' / 'Phi-3-mini-4k-instruct-q4.gguf')
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

class JamroomManager:
	def __init__(self,db_path):
		self.db_path=db_path
		self._ensure_db()
	def _ensure_db(self):
		if not self.db_path.exists():
			self._save({'sites':[]})
	def _load(self):
		if self.db_path.exists():
			with open(self.db_path,'r') as f:
				return json.load(f)
		return {'sites':[]}
	def _save(self,data):
		with open(self.db_path,'w') as f:
			json.dump(data,f,indent=2)
	def get_all_sites(self):
		data=self._load()
		return data.get('sites',[])
	def add_site(self,name,url,description=''):
		data=self._load()
		site={'id':str(int(time.time()*1000)),'name':name,'url':url,'description':description,'created':datetime.now().isoformat()}
		data['sites'].append(site)
		self._save(data)
		return site
	def update_site(self,site_id,name,url,description=''):
		data=self._load()
		for site in data['sites']:
			if site['id']==site_id:
				site['name']=name
				site['url']=url
				site['description']=description
				site['updated']=datetime.now().isoformat()
				self._save(data)
				return site
		return None
	def delete_site(self,site_id):
		data=self._load()
		data['sites']=[s for s in data['sites'] if s['id']!=site_id]
		self._save(data)
		return True
class ShoutcastManager:
	def __init__(self,db_path):
		self.db_path=db_path
		self._ensure_db()
	def _ensure_db(self):
		if not self.db_path.exists():
			self._save({'servers':[]})
	def _load(self):
		if self.db_path.exists():
			with open(self.db_path,'r') as f:
				return json.load(f)
		return {'servers':[]}
	def _save(self,data):
		with open(self.db_path,'w') as f:
			json.dump(data,f,indent=2)
	def get_all_servers(self):
		data=self._load()
		return data.get('servers',[])
	def add_server(self,name,host,port,server_type='shoutcast'):
		data=self._load()
		server={'id':str(int(time.time()*1000)),'name':name,'host':host,'port':port,'type':server_type,'status':'stopped','created':datetime.now().isoformat()}
		data['servers'].append(server)
		self._save(data)
		return server
	def update_server(self,server_id,name,host,port,server_type='shoutcast'):
		data=self._load()
		for server in data['servers']:
			if server['id']==server_id:
				server['name']=name
				server['host']=host
				server['port']=port
				server['type']=server_type
				server['updated']=datetime.now().isoformat()
				self._save(data)
				return server
		return None
	def delete_server(self,server_id):
		data=self._load()
		data['servers']=[s for s in data['servers'] if s['id']!=server_id]
		self._save(data)
		return True
	def start_server(self,server_id):
		data=self._load()
		for server in data['servers']:
			if server['id']==server_id:
				server['status']='running'
				self._save(data)
				return True
		return False
	def stop_server(self,server_id):
		data=self._load()
		for server in data['servers']:
			if server['id']==server_id:
				server['status']='stopped'
				self._save(data)
				return True
		return False
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
jamroom_mgr=JamroomManager(app.config['JAMROOM_DB'])
shoutcast_mgr=ShoutcastManager(app.config['SHOUTCAST_DB'])
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
</header>
<nav>
<a href="/" class="{{ 'active' if request.path=='/' else '' }}">Dashboard</a>
<a href="/echo-chat" class="{{ 'active' if '/echo-chat' in request.path else '' }}">🌙 Echo Chat</a>
<a href="/jamroom" class="{{ 'active' if '/jamroom' in request.path else '' }}">Jamroom Sites</a>
<a href="/shoutcast" class="{{ 'active' if '/shoutcast' in request.path else '' }}">Shoutcast/Icecast</a>
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
<a href="/jamroom" class="btn">Manage Jamroom Sites</a>
<a href="/shoutcast" class="btn">Manage Streaming Servers</a>
<a href="/scripts" class="btn">Script Manager</a>
<a href="/processes" class="btn">Process Monitor</a>
<a href="/services" class="btn">Service Monitor</a>
<a href="/addons" class="btn">Install Addons</a>
<a href="/web_ide" class="btn">Web IDE</a>
</div>
{% endblock %}"""
JAMROOM_TEMPLATE="""{% extends "base.html" %}
{% block content %}
<div class="section">
<h2>Jamroom Site Manager</h2>
<button onclick="openModal('addSiteModal')" class="btn">Add New Site</button>
<table>
<thead>
<tr>
<th>Name</th>
<th>URL</th>
<th>Description</th>
<th>Created</th>
<th>Actions</th>
</tr>
</thead>
<tbody>
{% for site in sites %}
<tr>


<td>{{ site.name }}</td>
<td><a href="{{ site.url }}" target="_blank" style="color:#4CAF50;">{{ site.url }}</a></td>
<td>{{ site.description }}</td>
<td>{{ site.created[:10] }}</td>
<td>
<a href="/jamroom/edit/{{ site.id }}" class="btn btn-info">Edit</a>
<a href="/jamroom/delete/{{ site.id }}" class="btn btn-danger" onclick="return confirmDelete('{{ site.name }}');">Delete</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
<div id="addSiteModal" class="modal">
<div class="modal-content">
<span class="close" onclick="closeModal('addSiteModal')">&times;</span>
<h2>Add New Site</h2>
<form method="POST" action="/jamroom/add">
<div class="form-group">
<label>Site Name</label>
<input type="text" name="name" required>
</div>
<div class="form-group">
<label>URL</label>
<input type="url" name="url" required>
</div>
<div class="form-group">
<label>Description</label>
<textarea name="description" rows="3"></textarea>
</div>
<button type="submit" class="btn">Add Site</button>
</form>
</div>
</div>
{% endblock %}"""
JAMROOM_EDIT_TEMPLATE="""{% extends "base.html" %}
{% block content %}
<div class="section">
<h2>Edit Site</h2>
<form method="POST" action="/jamroom/update/{{ site.id }}">
<div class="form-group">
<label>Site Name</label>
<input type="text" name="name" value="{{ site.name }}" required>
</div>
<div class="form-group">
<label>URL</label>
<input type="url" name="url" value="{{ site.url }}" required>
</div>
<div class="form-group">
<label>Description</label>
<textarea name="description" rows="3">{{ site.description }}</textarea>
</div>
<button type="submit" class="btn">Update Site</button>
<a href="/jamroom" class="btn btn-warning">Cancel</a>
</form>
</div>
{% endblock %}"""
SHOUTCAST_TEMPLATE="""{% extends "base.html" %}
{% block content %}
<div class="section">
<h2>Shoutcast/Icecast Server Manager</h2>
<button onclick="openModal('addServerModal')" class="btn">Add New Server</button>
<table>
<thead>
<tr>
<th>Name</th>
<th>Host:Port</th>
<th>Type</th>
<th>Status</th>
<th>Actions</th>
</tr>
</thead>
<tbody>
{% for server in servers %}
<tr>
<td>{{ server.name }}</td>
<td>{{ server.host }}:{{ server.port }}</td>
<td>{{ server.type }}</td>
<td><span class="status-badge status-{{ server.status }}">{{ server.status }}</span></td>
<td>
{% if server.status=='stopped' %}
<a href="/shoutcast/start/{{ server.id }}" class="btn">Start</a>
{% else %}
<a href="/shoutcast/stop/{{ server.id }}" class="btn btn-warning">Stop</a>
{% endif %}
<a href="/shoutcast/edit/{{ server.id }}" class="btn btn-info">Edit</a>
<a href="/shoutcast/delete/{{ server.id }}" class="btn btn-danger" onclick="return confirmDelete('{{ server.name }}');">Delete</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
<div id="addServerModal" class="modal">
<div class="modal-content">
<span class="close" onclick="closeModal('addServerModal')">&times;</span>
<h2>Add New Server</h2>
<form method="POST" action="/shoutcast/add">
<div class="form-group">
<label>Server Name</label>
<input type="text" name="name" required>
</div>
<div class="form-group">
<label>Host</label>
<input type="text" name="host" value="localhost" required>
</div>
<div class="form-group">
<label>Port</label>
<input type="number" name="port" value="8000" required>
</div>
<div class="form-group">
<label>Server Type</label>
<select name="type">
<option value="shoutcast">Shoutcast</option>
<option value="icecast">Icecast</option>
</select>
</div>
<button type="submit" class="btn">Add Server</button>
</form>
</div>
</div>
{% endblock %}"""
SHOUTCAST_EDIT_TEMPLATE="""{% extends "base.html" %}
{% block content %}
<div class="section">
<h2>Edit Server</h2>
<form method="POST" action="/shoutcast/update/{{ server.id }}">
<div class="form-group">
<label>Server Name</label>
<input type="text" name="name" value="{{ server.name }}" required>
</div>
<div class="form-group">
<label>Host</label>
<input type="text" name="host" value="{{ server.host }}" required>
</div>
<div class="form-group">
<label>Port</label>
<input type="number" name="port" value="{{ server.port }}" required>
</div>
<div class="form-group">
<label>Server Type</label>
<select name="type">
<option value="shoutcast" {{ 'selected' if server.type=='shoutcast' else '' }}>Shoutcast</option>
<option value="icecast" {{ 'selected' if server.type=='icecast' else '' }}>Icecast</option>
</select>
</div>
<button type="submit" class="btn">Update Server</button>
<a href="/shoutcast" class="btn btn-warning">Cancel</a>
</form>
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
</div>
</div>
<button onclick="clearChat()" class="btn btn-warning" style="width:100%;margin-top:15px;">Clear Chat</button>
<button onclick="searchMemory()" class="btn btn-info" style="width:100%;margin-top:10px;">Search Memory</button>
</div>
<div class="echo-main">
<div class="chat-header">🌙 Echo Starlite - Chat</div>
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
<button type="submit" class="send-btn">Send 💜</button>
</form>
</div>
</div>
</div>
<script>
let sessionId='web_'+Date.now();
let messageCount=0;
function sendMessage(e){
e.preventDefault();
const input=document.getElementById('chatInput');
const message=input.value.trim();
if(!message)return;
addUserMessage(message);
input.value='';
showTyping();
fetch('/api/echo/chat',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({message:message,session_id:sessionId})
}).then(r=>r.json()).then(data=>{
hideTyping();
addEchoMessage(data.response,data.message_id);
updateStats();
messageCount++;
document.getElementById('session-messages').textContent=messageCount;
}).catch(err=>{
hideTyping();
console.error('Error:',err);
addEchoMessage('Sorry... something went wrong... 💜',null);
});
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
@app.route('/jamroom')
def jamroom_list():
	sites=jamroom_mgr.get_all_sites()
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',JAMROOM_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),sites=sites,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/jamroom/add',methods=['POST'])
def jamroom_add():
	name=request.form.get('name')
	url=request.form.get('url')
	description=request.form.get('description','')
	jamroom_mgr.add_site(name,url,description)
	flash('Site added successfully!','success')
	return redirect(url_for('jamroom_list'))
@app.route('/jamroom/edit/<site_id>')
def jamroom_edit(site_id):
	sites=jamroom_mgr.get_all_sites()
	site=next((s for s in sites if s['id']==site_id),None)
	if not site:
		flash('Site not found','error')
		return redirect(url_for('jamroom_list'))
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',JAMROOM_EDIT_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),site=site,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/jamroom/update/<site_id>',methods=['POST'])
def jamroom_update(site_id):
	name=request.form.get('name')
	url=request.form.get('url')
	description=request.form.get('description','')
	jamroom_mgr.update_site(site_id,name,url,description)
	flash('Site updated successfully!','success')
	return redirect(url_for('jamroom_list'))
@app.route('/jamroom/delete/<site_id>')
def jamroom_delete(site_id):
	jamroom_mgr.delete_site(site_id)
	flash('Site deleted successfully!','success')
	return redirect(url_for('jamroom_list'))
@app.route('/shoutcast')
def shoutcast_list():
	servers=shoutcast_mgr.get_all_servers()
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SHOUTCAST_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),servers=servers,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/shoutcast/add',methods=['POST'])
def shoutcast_add():
	name=request.form.get('name')
	host=request.form.get('host')
	port=request.form.get('port')
	server_type=request.form.get('type')
	shoutcast_mgr.add_server(name,host,int(port),server_type)
	flash('Server added successfully!','success')
	return redirect(url_for('shoutcast_list'))
@app.route('/shoutcast/edit/<server_id>')
def shoutcast_edit(server_id):
	servers=shoutcast_mgr.get_all_servers()
	server=next((s for s in servers if s['id']==server_id),None)
	if not server:
		flash('Server not found','error')
		return redirect(url_for('shoutcast_list'))
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SHOUTCAST_EDIT_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),server=server,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/shoutcast/update/<server_id>',methods=['POST'])
def shoutcast_update(server_id):
	name=request.form.get('name')
	host=request.form.get('host')
	port=request.form.get('port')
	server_type=request.form.get('type')
	shoutcast_mgr.update_server(server_id,name,host,int(port),server_type)
	flash('Server updated successfully!','success')
	return redirect(url_for('shoutcast_list'))
@app.route('/shoutcast/delete/<server_id>')
def shoutcast_delete(server_id):
	shoutcast_mgr.delete_server(server_id)
	flash('Server deleted successfully!','success')
	return redirect(url_for('shoutcast_list'))
@app.route('/shoutcast/start/<server_id>')
def shoutcast_start(server_id):
	shoutcast_mgr.start_server(server_id)
	flash('Server started successfully!','success')
	return redirect(url_for('shoutcast_list'))
@app.route('/shoutcast/stop/<server_id>')
def shoutcast_stop(server_id):
	shoutcast_mgr.stop_server(server_id)
	flash('Server stopped successfully!','success')
	return redirect(url_for('shoutcast_list'))
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

@app.route('/echo-chat')
def echo_chat():
	echo_art=Echo.get_compact_greeting()
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',ECHO_CHAT_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),echo_art=echo_art,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/api/echo/chat',methods=['POST'])
def api_echo_chat():
	try:
		data = request.get_json() or {}
		message = data.get('message','')
		session_id = data.get('session_id','default')
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
		# If a personality is enabled for this session, prepend it as runtime context
		try:
			person = meta.get('personality') or {}
			if person.get('enabled') and person.get('text'):
				# prepend personality as instruction
				message_for_bot = f"[Persona]\n{person.get('text')}\n\nUser: {message}"
			else:
				message_for_bot = message
		except Exception:
			message_for_bot = message
		response = bot.chat(message_for_bot, session_id=session_id)
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
		# persist session metadata so it appears in chat history list
		try:
			_upsert_session_meta(session_id)
		except Exception:
			pass
		storage = get_storage()
		storage.store_message(user='web_user', message=message, echo_response=response.get('response') if isinstance(response, dict) else str(response), channel=session_id)
		return jsonify(response)
	except Exception as e:
		return jsonify({'error':str(e)}),500
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


@app.route('/api/echo/model')
def api_echo_model():
	"""Return the currently discovered local model path (or null)."""
	try:
		bot = get_chat_bot()
		model = None
		# prefer explicit method if available
		if hasattr(bot, '_find_local_model'):
			try:
				model = bot._find_local_model()
			except Exception:
				model = None
		return jsonify({'model': model})
	except Exception as e:
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
        output_name = data.get('output_name') or f"run_{int(time.time())}"
        epochs = int(data.get('epochs', 1))
        batch_size = int(data.get('batch_size', 8))
        lr = float(data.get('lr', 1e-4))

        engine = data.get('engine', 'stub')
        # validate basics
        if not model or not training_file:
            return jsonify({'error': 'model and training_file are required'}), 400

        model_path = Path(model)
        if not model_path.is_absolute():
            model_path = Path.cwd() / model_path
        if not model_path.exists():
            return jsonify({'error': 'model not found'}), 404

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



@app.route('/api/echo/models')
def api_echo_models():
    """List discovered local GGUF models under the `models/` directory."""
    try:
        base = Path.cwd() / 'models'
        models = []
        if base.exists():
            for p in sorted(base.rglob('*.gguf')):
                try:
                    models.append(str(p.relative_to(Path.cwd()).as_posix()))
                except Exception:
                    models.append(str(p))
        return jsonify({'models': models})
    except Exception as e:
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
