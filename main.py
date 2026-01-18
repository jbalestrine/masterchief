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

# Add script dir back for local imports
sys.path.insert(0, _script_dir)
from echo.chat_bot import get_chat_bot, ResponseQuality, TrainingExample
from echo.conversation_storage import get_storage
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
# Sessions index file (persistent metadata for chat sessions)
SESSIONS_INDEX = Path(__file__).resolve().parent / 'data' / 'sessions.json'

def _load_sessions_index():
	try:
		if SESSIONS_INDEX.exists():
			with open(SESSIONS_INDEX,'r',encoding='utf-8') as f:
				return json.load(f)
	except Exception:
		pass
	return {}

def _save_sessions_index(idx: dict):
	try:
		SESSIONS_INDEX.parent.mkdir(parents=True,exist_ok=True)
		with open(SESSIONS_INDEX,'w',encoding='utf-8') as f:
			json.dump(idx,f,indent=2)
		return True
	except Exception:
		return False

def _upsert_session_meta(session_id: str, title: str = None):
	idx = _load_sessions_index()
	now = datetime.now().isoformat()
	entry = idx.get(session_id, {})
	entry['session_id'] = session_id
	entry['title'] = title or entry.get('title') or session_id
	entry['last_updated'] = now
	entry.setdefault('created', now)
	entry.setdefault('favorite', False)
	idx[session_id] = entry
	_save_sessions_index(idx)
	return entry

# --- Resources (Reference / Template / Examples) manager ---------------------------------
RESOURCES_INDEX = Path(__file__).resolve().parent / 'data' / 'resources.json'
RESOURCES_DIR = app.config['UPLOAD_FOLDER'] / 'resources'
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

# Ingestion queue and persistent tasks file
INGEST_TASKS_PATH = Path(__file__).resolve().parent / 'data' / 'ingest_tasks.json'
INGEST_QUEUE = {}

def _load_ingest_tasks():
	try:
		if INGEST_TASKS_PATH.exists():
			data = json.loads(INGEST_TASKS_PATH.read_text(encoding='utf-8'))
			# Normalize older task entries to include a bot_ingested flag
			changed = False
			for tid, t in list(data.items()):
				if 'bot_ingested' not in t:
					t['bot_ingested'] = False
					changed = True
			if changed:
				try:
					_ingest_tasks_backup = INGEST_TASKS_PATH.with_suffix('.bak.json')
					_ingest_tasks_backup.write_text(json.dumps(data, indent=2), encoding='utf-8')
					_ingEST_SAVE = _save_ingest_tasks(data)
				except Exception:
					pass
			return data
	except Exception:
		app.logger.exception('Failed to load ingest tasks')
	return {}

def _save_ingest_tasks(tasks: dict):
	try:
		INGEST_TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
		INGEST_TASKS_PATH.write_text(json.dumps(tasks, indent=2), encoding='utf-8')
		return True
	except Exception:
		app.logger.exception('Failed to save ingest tasks')
		return False

def _start_ingest_worker():
	import threading, time

	def worker():
		app.logger.info('Ingest worker started')
		while True:
			try:
				tasks = _load_ingest_tasks()
				for tid, t in list(tasks.items()):
					if t.get('status') in ('pending', 'running'):
						# mark running
						t['status'] = 'running'
						_save_ingest_tasks(tasks)
						try:
							# perform ingest: read file and store into session meta
							path = Path(t['resource']['path'])
							sess = t.get('session_id','default')
							content = None
							try:
								content = path.read_text(encoding='utf-8')
							except Exception:
								content = None
							storage = get_storage()
							meta = storage.get_session_meta(sess) or {}
							# If the bot supports ingest, call it to wire into knowledge store
							bot_ingested = False
							try:
								bot = get_chat_bot()
								if hasattr(bot, 'ingest_resource'):
									try:
										payload = {'type':'text','text': content} if isinstance(content, str) else {'type':'binary', 'path': str(path), 'size': path.stat().st_size}
										bot_ingested = bool(bot.ingest_resource(sess, t['resource'], payload))
									except Exception:
										app.logger.exception('Bot ingest failed inside worker')
							except Exception:
								app.logger.exception('Failed to obtain bot for ingest')
							ing = meta.get('ingestions', {})
							ing[tid] = {'resource_id': t['resource']['id'], 'status': 'done' if bot_ingested else 'done', 'bot_ingested': bot_ingested, 'ingested_at': datetime.now().isoformat(), 'preview': content[:100] if isinstance(content,str) else None}
							meta['ingestions'] = ing
							storage.set_session_meta(sess, meta)
							# record bot ingestion result on the persistent task
							t['bot_ingested'] = bool(bot_ingested)
							t['status'] = 'done'
							_save_ingest_tasks(tasks)
						except Exception:
							app.logger.exception('Ingest task failed')
							t['status'] = 'error'
							t['bot_ingested'] = False
							_save_ingest_tasks(tasks)
				time.sleep(1)
			except Exception:
				app.logger.exception('Ingest worker loop failed')
				time.sleep(2)

	th = threading.Thread(target=worker, daemon=True)
	th.start()

# start worker at import time
_start_ingest_worker()

def _load_resources_index():
		try:
				if RESOURCES_INDEX.exists():
						with open(RESOURCES_INDEX, 'r', encoding='utf-8') as f:
								return json.load(f)
		except Exception:
				app.logger.exception('Failed to load resources index')
		return {}

def _save_resources_index(idx: dict):
		try:
				RESOURCES_INDEX.parent.mkdir(parents=True, exist_ok=True)
				with open(RESOURCES_INDEX, 'w', encoding='utf-8') as f:
						json.dump(idx, f, indent=2)
				return True
		except Exception:
				app.logger.exception('Failed to save resources index')
				return False

def _resource_id_for(category: str, filename: str) -> str:
		# stable id to reference resources in index
		return f"{category}:{filename}"

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
<div id="resourcesList">(loading...)</div>
</div>
</div>
<script>
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
	 Object.keys(idx).forEach(k=>{
		 const r = idx[k];
		 const div=document.createElement('div');
		 div.style.border='1px solid #333';div.style.padding='8px';div.style.marginBottom='6px';
		 div.innerHTML = '<b>'+r.filename+'</b> <small>['+r.category+']</small><br>'+
			 '<button class="btn btn-sm" onclick="loadIntoSession(\''+encodeURIComponent(k)+'\')">Load into session</button> '
			 +'<button class="btn btn-sm btn-danger" onclick="deleteResource(\''+encodeURIComponent(k)+'\')">Delete</button>';
		 el.appendChild(div);
	 });
 }).catch(e=>{document.getElementById('resourcesList').textContent='Failed to load resources';console.error(e)});
}
function deleteResource(id){ if(!confirm('Delete resource?')) return; fetch('/api/resources/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:decodeURIComponent(id)})}).then(r=>r.json()).then(j=>{ loadResources(); }).catch(e=>console.error(e)); }
function loadIntoSession(id){ const sid = prompt('Load into which session id? (leave blank for current page session)'); fetch('/api/resources/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:decodeURIComponent(id), session_id: sid || ''})}).then(r=>r.json()).then(j=>{ alert(j.message||JSON.stringify(j)); }).catch(e=>console.error(e)); }
loadResources();
</script>
{% endblock %}"""

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
		script_path=self.scripts_folder/secure_filename(filename)
		with open(script_path,'w') as f:
			f.write(content)
		os.chmod(script_path,0o755)
		return True
	def delete_script(self,filename):
		script_path=self.scripts_folder/secure_filename(filename)
		if script_path.exists():
			script_path.unlink()
			return True
		return False
	def execute_script(self,filename,args=''):
		script_path=self.scripts_folder/secure_filename(filename)
		if not script_path.exists():
			return {'success':False,'error':'Script not found'}
		try:
			if script_path.suffix=='.py':
				cmd=[sys.executable,str(script_path)]
			elif script_path.suffix=='.ps1':
				cmd=['powershell','-ExecutionPolicy','Bypass','-File',str(script_path)]
			else:
				cmd=[str(script_path)]
			if args:
				cmd.extend(args.split())
			result=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
			return {'success':result.returncode==0,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
		except subprocess.TimeoutExpired:
			return {'success':False,'error':'Script execution timed out'}
		except Exception as e:
			return {'success':False,'error':str(e)}
	def get_script_content(self,filename):
		script_path=self.scripts_folder/secure_filename(filename)
		if script_path.exists():
			with open(script_path,'r') as f:
				return f.read()
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
	fetch('/scripts/refresh_index',{method:'POST'}).then(async r=>{
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
	# Optional admin token protection: if ADMIN_TOKEN is set, require header 'X-ADMIN-TOKEN' or form/json 'admin_token'
	admin_token = app.config.get('ADMIN_TOKEN')
	if admin_token:
		provided = request.headers.get('X-ADMIN-TOKEN') or request.form.get('admin_token') or (request.get_json(silent=True) or {}).get('admin_token')
		if not provided or provided != admin_token:
			return jsonify({'ok':False,'error':'admin token required'}),401
	cache_file = Path(__file__).resolve().parent / 'data' / 'script_index.json'
	try:
		if cache_file.exists():
			cache_file.unlink()
		return jsonify({'ok':True,'message':'index invalidated'})
	except Exception as e:
		return jsonify({'ok':False,'error':str(e)}),500

def _check_basic_auth():
	"""Return True if no basic auth configured or if request contains valid credentials."""
	user = app.config.get('BASIC_AUTH_USER')
	pw = app.config.get('BASIC_AUTH_PASS')
	if not user or not pw:
		return True
	auth = request.headers.get('Authorization')
	if not auth or not auth.startswith('Basic '):
		return False
	try:
		b64 = auth.split(' ',1)[1].strip()
		creds = base64.b64decode(b64).decode()
		u,p = creds.split(':',1)
		return u == user and p == pw
	except Exception:
		return False

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
		filepath = cat_dir / filename

		# Prevent duplicate filenames in same category
		idx = _load_resources_index()
		rid = _resource_id_for(category, filename)
		if rid in idx:
			return jsonify({'error': 'Resource already exists', 'message': 'Duplicate resource detected'}), 400

		f.save(filepath)
		persona = bool(request.form.get('persona'))

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
		if hasattr(bot, '_find_local_model'):
			try:
				model = bot._find_local_model()
			except Exception:
				model = None

		if model and hasattr(bot, '_generate_with_local_llm'):
			try:
				# short prompt to exercise the worker and any native bindings
				out = bot._generate_with_local_llm('Hello, warmup', max_tokens=8, temperature=0.1)
				warmed = bool(out)
			except Exception as e:
				app.logger.exception('Preload generation failed')
				return jsonify({'model': model, 'warmed': False, 'error': str(e)}), 500

		return jsonify({'model': model, 'warmed': warmed})
	except Exception as e:
		app.logger.exception('Preload endpoint failed')
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
	app.run(host='0.0.0.0',port=args.port,debug=args.debug)
