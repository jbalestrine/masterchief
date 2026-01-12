#!/usr/bin/env python3
"""MasterChief Flask Web Application - All-in-One File"""
import sys
import os
_original_path=sys.path.copy()
_script_dir=os.path.dirname(os.path.abspath(__file__))
if _script_dir in sys.path:
	sys.path.remove(_script_dir)
import json
import time
import psutil
import zipfile
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from flask import Flask,render_template_string,request,jsonify,redirect,url_for,flash,send_file,get_flashed_messages
from werkzeug.utils import secure_filename
app=Flask(__name__)
app.config['SECRET_KEY']='masterchief-secret-key-change-in-production'
_data_dir=Path(__file__).parent/'data'
app.config['UPLOAD_FOLDER']=_data_dir/'uploads'
app.config['SCRIPTS_FOLDER']=_data_dir/'scripts'
app.config['JAMROOM_DB']=_data_dir/'jamroom.json'
app.config['SHOUTCAST_DB']=_data_dir/'shoutcast.json'
app.config['MAX_CONTENT_LENGTH']=100*1024*1024
for folder in [app.config['UPLOAD_FOLDER'],app.config['SCRIPTS_FOLDER'],_data_dir]:
	folder.mkdir(parents=True,exist_ok=True)
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
	def list_scripts(self):
		scripts=[]
		for ext in ['*.sh','*.ps1','*.py','*.bash']:
			for script_file in self.scripts_folder.glob(ext):
				scripts.append({'name':script_file.name,'path':str(script_file),'size':script_file.stat().st_size,'modified':datetime.fromtimestamp(script_file.stat().st_mtime).isoformat(),'type':script_file.suffix[1:]})
		return sorted(scripts,key=lambda x:x['name'])
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
	disk=psutil.disk_usage('/')
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
<button onclick="openModal('addScriptModal')" class="btn">Add New Script</button>
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
<a href="/scripts/view/{{ script.name }}" class="btn btn-info">View</a>
<a href="/scripts/execute/{{ script.name }}" class="btn">Execute</a>
<a href="/scripts/delete/{{ script.name }}" class="btn btn-danger" onclick="return confirmDelete('{{ script.name }}');">Delete</a>
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
	scripts=script_mgr.list_scripts()
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPTS_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),scripts=scripts,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/scripts/add',methods=['POST'])
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
def scripts_execute(filename):
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=None,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/scripts/run/<filename>',methods=['POST'])
def scripts_run(filename):
	args=request.form.get('args','')
	result=script_mgr.execute_script(filename,args)
	return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}',SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')),filename=filename,result=result,request=request,get_flashed_messages=get_flashed_messages)
@app.route('/scripts/delete/<filename>')
def scripts_delete(filename):
	if script_mgr.delete_script(filename):
		flash('Script deleted successfully!','success')
	else:
		flash('Failed to delete script','error')
	return redirect(url_for('scripts_list'))
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
if __name__=='__main__':
	print('='*70)
	print('MasterChief DevOps Platform')
	print('='*70)
	print('Dashboard: http://localhost:8080')
	print('='*70)
	app.run(host='0.0.0.0',port=8080,debug=True)
